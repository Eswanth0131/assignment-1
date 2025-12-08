import os
import requests
from urllib.parse import urlparse
from bs4 import BeautifulSoup

URL_LIST_FILE = "data/lecture_urls.txt"
OUTPUT_ROOT = "data/clean/website"

def extract_area_and_page(url):
    path = urlparse(url).path
    parts = [p for p in path.split("/") if p]

    if "lectures" not in parts:
        return None, None

    i = parts.index("lectures")
    if len(parts) <= i + 1:
        return None, None

    area = parts[i + 1]

    if len(parts) > i + 2:
        last = parts[-1]
        page = os.path.splitext(last)[0] if last.endswith(".html") else last
    else:
        page = "index"

    return area, page

def extract_text_from_url(url):
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")
    for tag in soup(["script", "style"]):
        tag.extract()

    lines = [line.strip() for line in soup.get_text("\n").splitlines() if line.strip()]
    return "\n".join(lines)

def main():
    if not os.path.exists(URL_LIST_FILE):
        print("missing url list")
        return

    with open(URL_LIST_FILE, "r") as f:
        urls = [line.strip() for line in f if line.strip()]

    for url in urls:
        area, page = extract_area_and_page(url)
        if not area or not page:
            continue

        out_dir = os.path.join(OUTPUT_ROOT, area, page)
        os.makedirs(out_dir, exist_ok=True)
        out_file = os.path.join(out_dir, "content.txt")

        try:
            text = extract_text_from_url(url)
            with open(out_file, "w") as f:
                f.write(text)
        except:
            pass

if __name__ == "__main__":
    main()