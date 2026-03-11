import os
import sys
import math
import random
from collections import Counter
import time

ALPHABET = "abcdefghijklmnopqrstuvwxyz"
CIPHABET = "1234567890@#$zyxwvutsrqpon"

# NGRAM
class NGramScorer:
    def __init__(self, filepath):
        self.scores = {}
        self.total = 0
        with open(filepath) as f:
            for line in f:
                k, v = line.strip().split()
                self.scores[k.lower()] = int(v)
                self.total += int(v)
        self.floor = math.log10(0.01/self.total)

    def evaluate(self, text, n):
        score = 0.0
        for i in range(len(text) - n + 1):
            seg = text[i:i+n]
            if seg in self.scores:
                score += math.log10(self.scores[seg] / self.total)
            else:
                score += self.floor
        return score


# UTILITIES
def apply_key(ciphertext, key_map):
    mapping = {CIPHABET[i]: ALPHABET[key_map[i]] for i in range(26)}
    out = []
    for ch in ciphertext:
        if ch in mapping:
            out.append(mapping[ch])
        else:
            out.append(ch)
    return ''.join(out)

def english_frequency_key(ciphertext):
    counts = Counter([c for c in ciphertext if c in CIPHABET])
    cipher_ranked = [x[0] for x in counts.most_common()]
    english_rank = "etaoinshrdlcumwfgypbvkjxqz"

    key = [-1] * 26
    used = set()

    for c, e in zip(cipher_ranked, english_rank):
        idx = CIPHABET.index(c)
        key[idx] = ALPHABET.index(e)
        used.add(ALPHABET.index(e))

    leftovers = [i for i in range(26) if i not in used]
    for i in range(26):
        if key[i] == -1:
            key[i] = leftovers.pop(0)

    return key

def inverse_key(key):
    inv = [0] * 26
    for i, v in enumerate(key):
        inv[v] = i
    return inv

# HEURISTIC 
def biased_swap(key, letter_bias):
    weights = []
    for i in range(26):
        w = abs(letter_bias.get(ALPHABET[key[i]], 0.5))
        weights.append(w)

    i = random.choices(range(26), weights=weights, k=1)[0]
    j = random.choices(range(26), weights=weights, k=1)[0]

    while i == j:
        j = random.choices(range(26), weights=weights, k=1)[0]

    new = key[:]
    new[i], new[j] = new[j], new[i]
    return new

def biased_swap(key, cipher_rank, plain_rank):
    """
    key: list[int] size 26
         key[i] = plaintext index assigned to CIPHABET[i]

    cipher_rank: dict {cipher_symbol -> rank}
    plain_rank: dict {plaintext_letter -> rank}
    """
    # compute mismatch scores
    weights = []
    for i in range(26):
        cipher_symbol = CIPHABET[i]
        plaintext_letter = ALPHABET[key[i]]

        mismatch = abs(
            cipher_rank[cipher_symbol] -
            plain_rank[plaintext_letter]
        )

        weights.append(mismatch + 1)  # avoid zero probability

    # biased selection of first index
    i = random.choices(range(26), weights=weights, k=1)[0]

    # second index: weak bias (prevents determinism)
    j = random.randrange(26)
    while j == i:
        j = random.randrange(26)

    new_key = key[:]
    new_key[i], new_key[j] = new_key[j], new_key[i]

    return new_key

def random_swap(key):
    
    i,j = random.randint(0,25), random.randint(0,25)
    while i == j:
        j = random.randint(0,25)
    new_key = key[:]
    new_key[i], new_key[j] = new_key[j], new_key[i]

    return new_key

def compute_cipher_ranks(ciphertext):
    from collections import Counter

    counts = Counter(c for c in ciphertext if c in CIPHABET)
    for c in CIPHABET:
        counts.setdefault(c, 0)

    ranked = sorted(counts, key=lambda x: counts[x])
    return {c: r for r, c in enumerate(ranked, start=1)}

def compute_plain_ranks(plaintext):
    from collections import Counter

    counts = Counter(c for c in plaintext if c in ALPHABET)
    for c in ALPHABET:
        counts.setdefault(c, 0)

    ranked = sorted(counts, key=lambda x: counts[x])
    return {c: r for r, c in enumerate(ranked, start=1)}

# SIMULATED ANNEALING
def anneal(ciphertext, base_key, scorer, ngram_n, rounds, temp0):
    best_key = base_key[:]
    best_score = scorer.evaluate(apply_key(ciphertext, best_key), ngram_n)
    current = best_key[:]
    current_score = best_score
    cipher_rank = compute_cipher_ranks(ciphertext)
    plain_rank = compute_plain_ranks(apply_key(ciphertext, current))
    for step in range(rounds):
        T = temp0 * (1 - step / rounds)
        proposal = biased_swap(current, cipher_rank, plain_rank)
        trial_text = apply_key(ciphertext, proposal)
        trial_score = scorer.evaluate(trial_text, ngram_n)
        delta = trial_score - current_score
        print(trial_text)
        # time.sleep(0.0)
        if delta > 0 or random.random() < math.exp(delta / max(T, 1e-9)):
            current = proposal
            current_score = trial_score

            if trial_score > best_score:
                best_key = proposal[:]
                best_score = trial_score
                plain_rank = compute_plain_ranks(apply_key(ciphertext, best_key))

    return best_key, best_score

# WORD VALIDATION
def valid_english(text, wordlist, threshold=0.95):
    chars = ",.?!#@*();:&$%^\"'-\n\t0123456789"
    text = text.translate(str.maketrans(chars, ' ' * len(chars)))
    words = [w.lower().strip() for w in text.split()]

    hit = 0
    for w in words:
        if w in wordlist:
            hit += 1

    return hit / max(1, len(words)) > threshold


# MAIN
def crack_cipher(ciphertext, bigram, trigram, quadgram, wordlist,
                 restarts=15, stage_iters_start=[100, 500, 2200]):

    stage_iters = stage_iters_start[:]
    seed_key = english_frequency_key(ciphertext)
    threshold = 1.0
    best_global = seed_key[:]
    best_score = -1e10

    for attempt in range(restarts):            
        e1 = bigram.evaluate(apply_key(ciphertext, seed_key), 2)
        k1, _ = anneal(ciphertext, seed_key, bigram, 2,
                        stage_iters[0], 10.0)
        e2 = trigram.evaluate(apply_key(ciphertext, k1), 3)
        k2, _ = anneal(ciphertext, k1, trigram, 3,
                        stage_iters[1], 15.0)
        e3 = quadgram.evaluate(apply_key(ciphertext, k2), 4)
        k3, s3 = anneal(ciphertext, k2, quadgram, 4,
                         stage_iters[2], 15.0)
        
        if s3 > best_score:
            best_global = k3[:]
            best_score = s3

        decoded = apply_key(ciphertext, best_global)

        if valid_english(decoded, wordlist, threshold):
            # print("found at:",attempt)
            return best_global, apply_key(ciphertext, best_global)
            
        if (attempt>6):
            threshold = threshold*0.98
            stage_iters = [int(x*1.2*(attempt+1)) for x in stage_iters_start]
        random.shuffle(seed_key)
    return best_global, apply_key(ciphertext, best_global)

# ---------- Example Driver ----------
if __name__ == "__main__":
    # cipher = open("ciphertext.txt").read()
    start = time.time()
    cipher = ""
    
    cipher = input()
    # cipher = "64s48u46 8y6 q480ryp nrv 6ryy43 2yu$2tn46, n4 54yu u$ o46. un8u yrpnu n4 6r6 y$u vq441 54qq, n80ryp s4043rvn 6348wv, n80ryp y$ 34vu. n4 58v 2yv234 5n4un43 n4 58v 8vq441 $3 6348wryp. t$yvtr$2v, 2yt$yvtr$2v, 8qq 58v 8 oq23. n4 34w4wo4346 t3#ryp, 5rvnryp, n$1ryp, o4ppryp, 404y q82pnryp. n4 sq$8u46 un3$2pn un4 2yr043v4, v44ryp vu83v, 1q8y4uv, v44ryp 483un, 8qq o2u nrwv4qs. 5n4y n4 q$$z46 6$5y, u3#ryp u$ v44 nrv o$6#, un434 58v y$unryp. ru 58v x2vu un8u n4 58v un434, o2u n4 t$2q6 y$u s44q 8y#unryp s$3 x2vu nrv 134v4yt4."
    
    cwd = os.path.dirname(os.path.abspath(__file__))
    bigram = NGramScorer(cwd + "/2gram.txt")
    trigram = NGramScorer(cwd + "/3gram.txt")
    quadgram = NGramScorer(cwd + "/4gram.txt")
    wordlist = {}
    with open(cwd + "/words.txt") as f:
        for line in f:
            w = line.strip()
            
            wordlist[w.lower()] = 1            
    key, plaintext = crack_cipher(cipher, bigram, trigram, quadgram, wordlist)
    key = "".join(CIPHABET[i] for i in inverse_key(key))

    # print("\nCiphertext:\n",cipher)
    puncs =  ",.?!#@*();:&$%^\"'-"
    plaintext = "".join([i for i in plaintext if i not in puncs])
    print("Deciphered Plaintext:",plaintext)

    key = "".join([i if i in cipher else 'x' for i in key])
    print("Deciphered Key:",key,end='')

    # newfile = open("deciphered_text.txt", "w")
    # newfile.write("Ciphertext:\n")
    # newfile.write(cipher)
    # newfile.write("\n\nDeciphered Plaintext:\n")
    # newfile.write(plaintext)
    # newfile.write("\n\nDeciphered Key:\n")
    # newfile.write(key)
    # newfile.close()
    # end = time.time()
    # print("\nTime taken:", end - start, "seconds")
