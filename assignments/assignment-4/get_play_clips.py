import os
import pandas as pd
import subprocess

VIDEO_FILE = "game1.mp4"   # video
CSV_FILE = "plays.csv"     # 50 plays
OUTPUT_DIR = "plays_clips"

os.makedirs(OUTPUT_DIR, exist_ok=True)

def timestamp_to_seconds(ts):
    if "-->" in ts:
        ts = ts.split("-->")[0].strip()

    ts = ts.replace(",", ".")

    parts = ts.split(":")
    if len(parts) != 3:
        raise ValueError(f"Invalid timestamp format: {ts}")

    h = int(parts[0])
    m = int(parts[1])
    s = float(parts[2])

    return h * 3600 + m * 60 + s

def extract_clips():
    print("Reading CSV...")
    df = pd.read_csv(CSV_FILE)

    print("Extracting clips...")

    for i, row in df.iterrows():
        ts = row["timestamp"]
        start_sec = timestamp_to_seconds(ts)

        # Clip settings
        clip_start = max(start_sec - 2, 0)
        clip_duration = 5

        out_path = os.path.join(OUTPUT_DIR, f"play_{i+1:02d}.mp4")

        cmd = [
            "ffmpeg",
            "-ss", str(clip_start),
            "-i", VIDEO_FILE,
            "-t", str(clip_duration),
            "-y",
            out_path
        ]

        print(f"Creating clip {i+1:02d} at {ts} -> {out_path}")
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    print("\nFinished. All clips saved in:", OUTPUT_DIR)


if __name__ == "__main__":
    extract_clips()