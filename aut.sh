#!/usr/bin/env bash

TIMEOUT=120

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
INPUT_FILE="$SCRIPT_DIR/input.txt"
OUTPUT_FILE="$SCRIPT_DIR/output.txt"

rm -f "$OUTPUT_FILE" a.out

if [ -f "Makefile" ]; then
    make clean >/dev/null 2>&1
    make >/dev/null 2>&1 || exit 1
    executable="./a.out"

elif ls *.py >/dev/null 2>&1; then
    executable="python3 $(ls *.py | head -n 1)"

else
    exit 1
fi

: >"$OUTPUT_FILE"

if [ ! -f "$INPUT_FILE" ]; then
    echo "input.txt not found"
    exit 1
fi

: >"$OUTPUT_FILE"

if ! grep -q '[^[:space:]]' "$INPUT_FILE"; then
    echo "input.txt is empty"
    exit 1
fi

while IFS= read -r cipher || [ -n "$cipher" ]; do
    if [[ "$cipher" =~ ^[[:space:]]*$ ]]; then
        continue
    fi

    run_out="$(timeout "$TIMEOUT" $executable <<<"$cipher" 2>/dev/null)" || exit 1

    plaintext="$(printf '%s\n' "$run_out" | sed -n 's/^Deciphered Plaintext:[[:space:]]*//p' | head -n 1)"
    key="$(printf '%s\n' "$run_out" | sed -n 's/^Deciphered Key:[[:space:]]*//p' | head -n 1)"

    printf '%s\nkey: %s\n\n' "$plaintext" "$key" >>"$OUTPUT_FILE"
done <"$INPUT_FILE"
