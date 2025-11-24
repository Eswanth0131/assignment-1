import re
import pandas as pd

# Load transcript
TRANSCRIPT_FILE = "transcript.srt"
with open(TRANSCRIPT_FILE, "r") as f:
    srt_text = f.read()

# Parse
pattern = re.compile(
    r"(\d+)\s+([\d:,]+ --> [\d:,]+)\s+(.*?)(?=\n\d+\s+[\d:,]+ -->|\Z)",
    re.DOTALL
)

segments = pattern.findall(srt_text)

def clean(text):
    return text.replace("\n", " ").strip()

parsed = []
for idx, timestamp, text in segments:
    parsed.append({
        "timestamp": timestamp,
        "text": clean(text)
    })

# Classification rules
OFFENSE_KEYWORDS = [
    "drives", "shoots", "three", "rolls", "cut", "screen",
    "pass", "iso", "isolation", "pick", "handoff", "transition"
]

DEFENSE_KEYWORDS = [
    "blocks", "steal", "deflects", "contest",
    "pressure", "double", "close out", "forces"
]

PLAY_TYPES = {
    "Pick and Roll": ["screen", "pick", "roll"],
    "Isolation": ["iso", "isolation"],
    "Handoff Action": ["handoff"],
    "Drive and Kick": ["drives", "kick"],
    "Catch and Shoot": ["catch", "shoots"],
    "Transition Offense": ["fast break", "in transition"],
    "Zone Defense": ["zone"],
    "Man-to-Man Defense": ["guarding", "close out", "man"],
    "Double Team": ["double"],
    "Steal / Turnover": ["steal", "turnover"]
}

def classify_play(text):
    t = text.lower()
    offense = any(k in t for k in OFFENSE_KEYWORDS)
    defense = any(k in t for k in DEFENSE_KEYWORDS)

    if offense and not defense:
        category = "Offensive Play"
    elif defense and not offense:
        category = "Defensive Play"
    elif offense and defense:
        # If both appear, choose the dominant one:
        # Offense > Defense lexically for basketball play context
        category = "Offensive Play"
    else:
        category = "Unclear"

    play_type = "Unknown"
    for name, keys in PLAY_TYPES.items():
        if any(k in t for k in keys):
            play_type = name
            break

    return category, play_type

# Classification
plays = []
for seg in parsed:
    category, play_type = classify_play(seg["text"])
    plays.append({
        "timestamp": seg["timestamp"],
        "play_type": play_type,
        "category": category,
        "description": seg["text"]
    })

# Generate 50 plays & save
filtered = [p for p in plays if p["play_type"] != "Unknown"]
output = filtered[:50] if len(filtered) >= 50 else filtered

df = pd.DataFrame(output)
df.to_csv("task2_1_output.csv", index=False)

print("Generated plays.csv with", len(output), "plays.")