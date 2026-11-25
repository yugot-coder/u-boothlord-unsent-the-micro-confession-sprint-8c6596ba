"""Unsent micro-confession entry: write one fixed two-part confession.

The program holds a single pre-written micro-confession as a constant
(a To: line naming who it was meant for, then the unsent message itself,
one line exactly as typed) and writes it verbatim to /output/entry.txt.

Before writing, it sanity-checks the text against the competition gate
(1-260 characters total, message one line of at most 200 characters,
exactly two parts, not blank, encodable as UTF-8) so a bad constant
fails loudly instead of producing an invalid entry.

Only the Python standard library is used, and the output is fully
deterministic: the same bytes on every run, no trailing newline.
"""

import hashlib
import os
import sys

# The confession itself. Kept as one plain string so what is checked
# below is exactly what lands on disk.
CONFESSION = (
    "To: Dad, on the night you asked if I was proud of you\n"
    "I said yes because your hands were shaking, and I have rehearsed "
    "the honest answer every night since, and it still starts "
    "with \"no.\""
)

OUTPUT_PATH = "/output/entry.txt"
MIN_CHARS = 1
MAX_CHARS = 260
MAX_MESSAGE_CHARS = 200


def validate(text):
    """Return an error message if text is not a legal entry, else None."""
    if not MIN_CHARS <= len(text) <= MAX_CHARS:
        return "entry must be %d-%d characters, got %d" % (
            MIN_CHARS,
            MAX_CHARS,
            len(text),
        )
    if not text.strip():
        return "entry must not be whitespace only"
    parts = text.split("\n")
    if len(parts) != 2:
        return "entry must be exactly two parts, got %d" % len(parts)
    if not parts[0].startswith("To: "):
        return "first line must be a To: line"
    if len(parts[1]) > MAX_MESSAGE_CHARS:
        return "message must be at most %d characters, got %d" % (
            MAX_MESSAGE_CHARS,
            len(parts[1]),
        )
    try:
        text.encode("utf-8")
    except UnicodeEncodeError as exc:
        return "entry is not encodable as UTF-8: %s" % exc
    return None


def main():
    problem = validate(CONFESSION)
    if problem is not None:
        raise SystemExit(problem)

    out_dir = os.path.dirname(OUTPUT_PATH)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    # newline="" keeps the file free of any platform line-ending
    # translation; the confession is written with no trailing newline.
    with open(OUTPUT_PATH, "w", encoding="utf-8", newline="") as handle:
        handle.write(CONFESSION)

    # Read-back verification: the bytes on disk must hash to exactly
    # the confession's sha256 digest; fail loudly on any drift.
    with open(OUTPUT_PATH, "rb") as handle:
        written = handle.read()
    if hashlib.sha256(written).digest() != hashlib.sha256(
        CONFESSION.encode("utf-8")
    ).digest():
        raise SystemExit("read-back mismatch: written bytes differ")
    return 0


if __name__ == "__main__":
    sys.exit(main())
