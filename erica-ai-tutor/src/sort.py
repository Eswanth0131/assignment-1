import os
import shutil

URL_FILE = "data/lecture_urls.txt"
RAW_DIR = "data/raw"
OUT_DIR = "data/clean/website"

PREFIX = "https://pantelis.github.io/aiml-common/lectures/"

def url_to_path(url):
    url = url.strip()
    rest = url[len(PREFIX):].rstrip("/")
    return rest

def main():
    urls = [u.strip() for u in open(URL_FILE) if u.strip()]
    txts = sorted(f for f in os.listdir(RAW_DIR) if f.endswith(".txt"))

    n = min(len(urls), len(txts))

    for i in range(n):
        rel = url_to_path(urls[i])
        dest = os.path.join(OUT_DIR, rel)
        os.makedirs(dest, exist_ok=True)

        src_file = os.path.join(RAW_DIR, txts[i])
        dst_file = os.path.join(dest, "content.txt")

        shutil.copy(src_file, dst_file)

    print("Done.")

if __name__ == "__main__":
    main()