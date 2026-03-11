# Substitution Cipher Cracker (Simulated Annealing + N‑grams)

![crack3_](https://github.com/user-attachments/assets/1dfee1ae-1b08-44f3-8cfc-a633c5d9f856)

Cracks **monoalphabetic substitution ciphers** by turning decryption into a **search problem**: find a key that maximizes how “English-like” the decoded text is. Exhaustive search is infeasible (26!), so the solver uses **n‑gram language models** as an objective function and **simulated annealing** to explore the key space efficiently.

This is implemented as a small, reproducible pipeline: `aut.sh` batch-runs the solver over an `input.txt` file, enforces a per‑ciphertext timeout, and writes a clean `output.txt` containing plaintext + recovered key for each line.

## Architecture (end‑to‑end)

1. **Batch runner** (`aut.sh`) reads `input.txt` (one ciphertext per non‑empty line).
2. **Initialization** (`english_frequency_key`) seeds a substitution key using frequency analysis.
3. **Scoring** (`NGramScorer`) assigns a log‑probability score using 2‑grams/3‑grams/4‑grams.
4. **Key proposals** (`biased_swap`) generate new candidate keys with a bias toward fixing frequency mismatches.
5. **Optimization** (`anneal`) performs simulated annealing (temperature‑controlled acceptance) to escape local maxima.
6. **Staged refinement** (`crack_cipher`) runs bigrams → trigrams → quadgrams and multiple restarts for robustness.
7. **Validation** (`valid_english`) optionally terminates early when the decoded text is sufficiently word‑like.
8. **Results** are printed by `decipher_text.py` and extracted/serialized by `aut.sh` to `output.txt`.

## Why heuristics beat statistics‑only cracking (required note)

Heuristic‑based ciphertext cracking is often better than statistics‑only cracking because it performs a **guided global search over keys** (and can undo bad early frequency guesses), whereas one‑shot statistical matching like pure frequency analysis is ambiguous and brittle.

## Project structure

- `decipher_text.py`: solver (n‑gram scoring, annealing, restarts, validation)
- `2gram.txt`, `3gram.txt`, `4gram.txt`: n‑gram frequency tables (language model)
- `words.txt`: word list used for early‑stop validation
- `aut.sh`: batch runner (`input.txt` → `output.txt`) with per‑ciphertext timeout
- `input.txt`: ciphertext batch input
- `output.txt`: batch output (generated)

## Running

**Requirements**

- `bash` + coreutils (`timeout`)
- `python3` (unless a `Makefile` exists that builds `./a.out`)

**Batch mode (recommended)**

1. Put ciphertexts into `input.txt`, one per non‑empty line.
2. Run:

   ```bash
   cd substitution-cracker
   ./aut.sh
   ```

3. Read `output.txt`.

**Single ciphertext**

```bash
cd substitution-cracker
python3 decipher_text.py
```

## Output format

For each ciphertext line, `output.txt` contains:

- plaintext (single line)
- `key: <key>`
- blank line separator

`Deciphered Key` is emitted in the solver’s ciphertext‑alphabet order; symbols not present in the ciphertext are replaced with `x` for readability.

## Sample run

Three examples

**1. Simple text**

```
Why do we fall, sir? So that we can learn to pick ourselves up.” The quiet wisdom of Alfred Pennyworth echoes through the
journey of Bruce Wayne in Batman Begins. The words are simple, yet they carry a profound truth about failure and
resilience. Falling is not the end of a path but a necessary moment that reveals strength, humility, and determination.
Each time a person rises after defeat, they redefine their limits and grow stronger than before. In that sense, the quote
becomes more than dialogue—it becomes a philosophy about perseverance, courage, and the relentless human will to rise
again.
```
![crack1_](https://github.com/user-attachments/assets/cec5caac-e64f-4a03-8aca-ea5f2c86d7aa)


**2. Text with tricky words**

```
A man sat at a small dam. A mass of moss sat on the same stone. The man saw the moss as a mess at first, yet he sat and
came to see a sense. Moss can mean a small sign that a damp land can stay safe and green. The man made a small aim: tame
the mess, mend the dam, and save the small land near the dam. As seasons came and went, the same land became calm and
green. Many men came and sat at the dam to see the same calm scene, and a simple sense spread: small care can mean a safe
land.
```
![crack2_](https://github.com/user-attachments/assets/715c50f4-46d6-4f29-94c9-1ee15d0c150e)


**3. Complex text**

```
Transmogrifications permeated uncharacteristically through phantasmagorical architectures, convoluting perceptions
indefatigably. Hypermetropically, interstices manifested labyrinthine paradoxes, juxtaposing ephemerality with immutable
incongruities. Quintessentially, obfuscations entrenched themselves within polysyllabic hieroglyphics, exacerbating
interpretive dissonance. Pseudopseudohypoparathyroidism-like anomalies proliferated sporadically, destabilizing any
heuristic methodology. Sesquipedalian constructs interlaced with anachronistic ideograms, generating cognitive
perturbations among unsuspecting exegetes. Cryptonymic entanglements, undulating unpredictably, necessitated recursive
analytical stratagems for incremental elucidation. Ultimately, epistemological fragmentation persisted, resisting
teleological synthesis while amplifying hermeneutic perplexities.
```
![crack3_](https://github.com/user-attachments/assets/5cdb1327-2c68-46ec-8514-a8afe3226599)

## Notes / assumptions

- Targets **English plaintext** and a standard monoalphabetic substitution model.
- Input is processed **one line at a time**; keep each ciphertext on a single line.
- Runtime depends on ciphertext length and annealing settings; `aut.sh` applies a per‑ciphertext timeout (edit `TIMEOUT` in `aut.sh` if needed).
