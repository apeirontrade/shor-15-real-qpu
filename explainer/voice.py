"""Generate one narration clip per scene and record the durations make.py times the scenes from.

Usage (from quantum-demo/): .venv/bin/python explainer/voice.py [voice name] [rate]
Default voice is macOS "Samantha"; swap in a Premium voice (e.g. "Zoe (Premium)") once installed.
"""
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(__file__))
from script import SCRIPT  # noqa: E402

HERE = os.path.dirname(__file__)
VOICE = sys.argv[1] if len(sys.argv) > 1 else "Samantha"
RATE = sys.argv[2] if len(sys.argv) > 2 else "178"
os.makedirs(os.path.join(HERE, "voice"), exist_ok=True)
durs = {}
for sid, line, _ in SCRIPT:
    if not line:
        durs[sid] = 0.0
        continue
    aiff = os.path.join(HERE, f"voice/{sid}.aiff")
    wav = os.path.join(HERE, f"voice/{sid}.wav")
    subprocess.run(["say", "-v", VOICE, "-r", RATE, "-o", aiff, line], check=True)
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", aiff, "-ar", "48000", "-ac", "1", wav], check=True)
    os.remove(aiff)
    durs[sid] = round(float(subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", wav])), 2)
json.dump(durs, open(os.path.join(HERE, "voice/durations.json"), "w"), indent=1)
print(f"{VOICE}: {sum(durs.values()):.1f}s of narration")
