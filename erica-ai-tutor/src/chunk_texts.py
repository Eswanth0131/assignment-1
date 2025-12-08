import os
import json
from pathlib import Path

WEBSITE_DIR = Path("data/clean/website")
PDF_DIR     = Path("data/clean/pdfs")
OUT_PATH    = Path("data/chunks.jsonl")

CHUNK_SIZE = 2000
CHUNK_OVERLAP = 200

def iter_txt_files(base_dir, source):
    for root, _, files in os.walk(base_dir):
        for f in files:
            if not f.endswith(".txt"):
                continue
            path = Path(root) / f
            rel = path.relative_to(base_dir)

            if source == "website":
                logical_id = f"website:{rel.with_suffix('')}"
            else:
                logical_id = f"pdf:{rel.parts[0]}"

            text = open(path, "r", encoding="utf-8", errors="ignore").read()
            yield logical_id, path, text

def chunk_text(text):
    out = []
    i = 0
    L = len(text)
    while i < L:
        out.append(text[i:i+CHUNK_SIZE])
        if i + CHUNK_SIZE >= L:
            break
        i = i + CHUNK_SIZE - CHUNK_OVERLAP
    return out

def main():
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    count = 0

    with open(OUT_PATH, "w", encoding="utf-8") as out:

        for logical_id, path, text in iter_txt_files(WEBSITE_DIR, "website"):
            for i, ch in enumerate(chunk_text(text)):
                out.write(json.dumps({
                    "id": f"{logical_id}::chunk-{i}",
                    "source": "website",
                    "file_path": str(path),
                    "logical_id": logical_id,
                    "chunk_index": i,
                    "text": ch
                }) + "\n")
                count += 1

        for logical_id, path, text in iter_txt_files(PDF_DIR, "pdf"):
            for i, ch in enumerate(chunk_text(text)):
                out.write(json.dumps({
                    "id": f"{logical_id}::chunk-{i}",
                    "source": "pdf",
                    "file_path": str(path),
                    "logical_id": logical_id,
                    "chunk_index": i,
                    "text": ch
                }) + "\n")
                count += 1

    print(f"✓ Wrote {count} chunks → {OUT_PATH}")

if __name__ == "__main__":
    main()