
import random

def encrypt(plaintext: str) -> str:
    """
    Encrypts plaintext using the substitution cipher.
    """
    ciphertext = ""
    for char in plaintext.lower():
        if char in encrypt_map:
            ciphertext += encrypt_map[char]
        else:
            ciphertext += char  # keep non-mapped characters unchanged
    return ciphertext


def decrypt(ciphertext: str) -> str:
    """
    Decrypts ciphertext using the substitution cipher.
    """
    plaintext = ""
    for char in ciphertext:
        if char in decrypt_map:
            plaintext += decrypt_map[char]
        else:
            plaintext += char  # keep non-mapped characters unchanged
    return plaintext


# Define the keys
PLAINTEXT_CHARS = "abcdefghijklmnopqrstuvwxyz"
# key
KEY = "y@zot6p148#qw2r$nvx59s73u0"

char_list = list(KEY)
random.shuffle(char_list)
KEY = "".join(char_list)


# Create lookup dictionaries
encrypt_map = dict(zip(PLAINTEXT_CHARS, KEY))
decrypt_map = dict(zip(KEY, PLAINTEXT_CHARS))

# Example usage
if __name__ == "__main__":
    # print("Plaintext :", text)
    text = "Within the labyrinthine architecture of human cognition lies an extraordinary capacity for introspective contemplation and philosophical reconstruction. Civilization progresses not merely through technological sophistication but through the intellectual magnanimity that encourages interdisciplinary collaboration and epistemological curiosity. When individuals embrace intellectual perseverance and cultivate humanitarian responsibility, society experiences a metamorphosis that transcends superficial advancement. Thus, the synthesis of intellectual rigor, ethical conscientiousness, and imaginative innovation becomes the quintessential catalyst for sustainable progress and the harmonious evolution of humanity."
    
    text = "A man sat at a small dam. A mass of moss sat on the same stone. The man saw the moss as a mess at first, yet he sat and came to see a sense. Moss can mean a small sign that a damp land can stay safe and green. The man made a small aim: tame the mess, mend the dam, and save the small land near the dam. As seasons came and went, the same land became calm and green. Many men came and sat at the dam to see the same calm scene, and a simple sense spread: small care can mean a safe land."
    text = "“Why do we fall, sir? So that we can learn to pick ourselves up.” The quiet wisdom of Alfred Pennyworth echoes through the journey of Bruce Wayne in Batman Begins. The words are simple, yet they carry a profound truth about failure and resilience. Falling is not the end of a path but a necessary moment that reveals strength, humility, and determination. Each time a person rises after defeat, they redefine their limits and grow stronger than before. In that sense, the quote becomes more than dialogue—it becomes a philosophy about perseverance, courage, and the relentless human will to rise again."
    encrypted = encrypt(text)
    print("Encrypted :", encrypted)
    
    # encrypted = "64s48u46 8y6 q480ryp nrv 6ryy43 2yu$2tn46, n4 54yu u$ o46. un8u yrpnu n4 6r6 y$u vq441 54qq, n80ryp s4043rvn 6348wv, n80ryp y$ 34vu. n4 58v 2yv234 5n4un43 n4 58v 8vq441 $3 6348wryp. t$yvtr$2v, 2yt$yvtr$2v, 8qq 58v 8 oq23. n4 34w4wo4346 t3#ryp, 5rvnryp, n$1ryp, o4ppryp, 404y q82pnryp. n4 sq$8u46 un3$2pn un4 2yr043v4, v44ryp vu83v, 1q8y4uv, v44ryp 483un, 8qq o2u nrwv4qs. 5n4y n4 q$$z46 6$5y, u3#ryp u$ v44 nrv o$6#, un434 58v y$unryp. ru 58v x2vu un8u n4 58v un434, o2u n4 t$2q6 y$u s44q 8y#unryp s$3 x2vu nrv 134v4yt4."
    # decrypted = decrypt(encrypted)
    # print("Decrypted :", decrypted)
