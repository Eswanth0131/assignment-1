import os
import json
import hashlib
from urllib.parse import urlparse, parse_qs
from youtube_transcript_api import YouTubeTranscriptApi

YT_LIST = "data/youtube_ids.txt"
RAW_DIR = "data/raw"
YT_LOG = "data/raw/youtube_ingested.jsonl"

os.makedirs(RAW_DIR, exist_ok=True)

def extract_video_id(x):
    if "http" not in x:
        return x.strip()
    u = urlparse(x)
    if "youtube" in u.netloc:
        q = parse_qs(u.query)
        return q.get("v", [None])[0]
    if "youtu.be" in u.netloc:
        return u.path.lstrip("/")
    return None

def save_text(video_id, text):
    h = hashlib.md5(video_id.encode()).hexdigest()
    path = os.path.join(RAW_DIR, h + ".txt")
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    with open(YT_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps({"video_id": video_id, "file": path}) + "\n")

def fetch_transcript(video_id):
    t = YouTubeTranscriptApi.fetch(video_id, languages=["en", "en-US", "en-GB"])
    return "\n".join([e.text for e in t])

def main():
    if os.path.exists(YT_LOG):
        os.remove(YT_LOG)

    with open(YT_LIST, "r") as f:
        vids = [extract_video_id(x) for x in f.read().splitlines() if x.strip()]

    for vid in vids:
        if vid is None:
            continue
        try:
            text = fetch_transcript(vid)
            save_text(vid, text)
            print(vid)
        except:
            print("fail:", vid)

if __name__ == "__main__":
    main()