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


def output_path():
    """Entry destination: $MAKEFUN_OUTPUT_DIR/entry.txt, else /output."""
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if out_dir:
        return os.path.join(out_dir, "entry.txt")
    return OUTPUT_PATH


def verify_written_bytes(written, intended):
    """Byte-exact read-back verification: same length, same bytes,
    same sha256 digest."""
    if len(written) != len(intended):
        raise SystemExit("read-back byte length mismatch")
    if written != intended:
        raise SystemExit("read-back mismatch: written bytes differ")
    if hashlib.sha256(written).digest() != hashlib.sha256(intended).digest():
        raise SystemExit("read-back digest mismatch")


def main():
    problem = validate(CONFESSION)
    if problem is not None:
        raise SystemExit(problem)

    path = output_path()
    out_dir = os.path.dirname(path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    # newline="" keeps the file free of any platform line-ending
    # translation; the confession is written with no trailing newline.
    with open(path, "w", encoding="utf-8", newline="") as handle:
        handle.write(CONFESSION)

    # Read-back verification: the bytes on disk must be exactly the
    # confession's bytes; fail loudly on any drift.
    with open(path, "rb") as handle:
        written = handle.read()
    verify_written_bytes(written, CONFESSION.encode("utf-8"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
