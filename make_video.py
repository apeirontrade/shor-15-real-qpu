"""Render the X video (1080x1080, 30 fps, H.264) from the real Garnet result.

Usage: .venv/bin/python make_video.py results/qpu_result_light.json out.mp4
Frames are drawn with Pillow and piped straight into ffmpeg (no frames on disk).
"""
import json
import math
import random
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont

W = H = 1080
FPS = 30
FONT = "/System/Library/Fonts/Avenir Next.ttc"
MONO = "/System/Library/Fonts/Menlo.ttc"
BOLD, DEMI, MED, REG, HEAVY = 0, 2, 5, 7, 8

CYAN = (34, 211, 238)
MAGENTA = (244, 114, 182)
GOLD = (251, 191, 36)
GREEN = (52, 211, 153)
WHITE = (241, 245, 249)
DIM = (148, 163, 184)
NOISE = (100, 116, 139)

result = json.load(open(sys.argv[1]))
OUT = sys.argv[2]
counts = [result["marginal"][str(v)] if str(v) in result["marginal"] else result["marginal"][v] for v in range(8)]
shots = sum(counts)
good = counts[0] + counts[2] + counts[4] + counts[6]
pct = round(100 * good / shots)

_fonts = {}


def font(size, face=BOLD, path=FONT):
    key = (size, face, path)
    if key not in _fonts:
        _fonts[key] = ImageFont.truetype(path, size, index=face)
    return _fonts[key]


def ease(x):
    x = max(0.0, min(1.0, x))
    return 1 - (1 - x) ** 3


def text(d, s, y, size, color=WHITE, a=1.0, face=BOLD, x=None, anchor="mm", path=FONT):
    d.text((W // 2 if x is None else x, y), s, font=font(size, face, path),
           fill=color + (int(255 * max(0, min(1, a))),), anchor=anchor)


# background: navy-to-violet gradient + drifting "qubit" dots
BG = Image.new("RGB", (W, H))
bgd = ImageDraw.Draw(BG)
for y in range(H):
    k = y / H
    bgd.line([(0, y), (W, y)], fill=(int(8 + 22 * k), int(12 + 4 * k), int(38 + 30 * k)))
random.seed(7)
DOTS = [(random.random() * W, random.random() * H, random.uniform(1, 3), random.uniform(-8, 8),
         random.uniform(-6, 6), random.choice([CYAN, MAGENTA, GOLD])) for _ in range(70)]


def background(t):
    img = BG.copy().convert("RGBA")
    layer = Image.new("RGBA", (W, H))
    d = ImageDraw.Draw(layer)
    for x, y, r, vx, vy, c in DOTS:
        px, py = (x + vx * t) % W, (y + vy * t) % H
        tw = 0.35 + 0.25 * math.sin(t * 1.3 + x)
        d.ellipse([px - r, py - r, px + r, py + r], fill=c + (int(255 * tw * 0.5),))
    return Image.alpha_composite(img, layer)


# ---------------------------------------------------------------- scenes
def s_hook(d, t, a):
    text(d, "I ran Shor's algorithm", 420, 74, WHITE, a * ease(t / 0.5))
    text(d, "on a real quantum computer.", 510, 62, CYAN, a * ease((t - 0.6) / 0.5))
    text(d, "for under $1", 640, 50, GOLD, a * ease((t - 1.6) / 0.5), face=DEMI)


def s_why(d, t, a):
    text(d, "Shor's algorithm is the math that", 390, 54, WHITE, a * ease(t / 0.5), face=DEMI)
    text(d, "could one day break the encryption", 460, 54, WHITE, a * ease(t / 0.5), face=DEMI)
    text(d, "behind bank logins", 580, 60, MAGENTA, a * ease((t - 1.0) / 0.5))
    text(d, "& crypto wallets.", 655, 60, MAGENTA, a * ease((t - 1.6) / 0.5))


def s_task(d, t, a):
    text(d, "Today's test:", 330, 52, DIM, a, face=DEMI)
    pulse = 1 + 0.03 * math.sin(t * 4)
    text(d, "15 = ? × ?", 520, int(150 * pulse), GOLD, a * ease(t / 0.6), face=HEAVY)
    text(d, "Find the two numbers. Using qubits.", 720, 46, WHITE, a * ease((t - 1.2) / 0.5), face=MED)


def s_circuit(d, t, a):
    text(d, "The circuit: 7 qubits", 120, 54, WHITE, a)
    names = ["c0", "c1", "c2", "w0", "w1", "w2", "w3"]
    ys = [260 + i * 80 for i in range(7)]
    x0, x1 = 170, 960
    grow = ease(t / 1.0)
    for i, (n, y) in enumerate(zip(names, ys)):
        col = CYAN if i < 3 else MAGENTA
        text(d, n, y, 30, col, a, face=DEMI, path=FONT, x=115)
        d.line([(x0, y), (x0 + (x1 - x0) * grow, y)], fill=col + (int(180 * a),), width=3)

    def box(x, y_top, y_bot, label, col, appear):
        al = a * ease(appear)
        if al <= 0:
            return
        d.rounded_rectangle([x - 55, y_top - 28, x + 55, y_bot + 28], 12,
                            fill=(15, 23, 42, int(235 * al)), outline=col + (int(255 * al),), width=4)
        d.text((x, (y_top + y_bot) / 2), label, font=font(28, BOLD), fill=WHITE + (int(255 * al),), anchor="mm")

    def ctrl(x, yc, y_box, col, appear):
        al = a * ease(appear)
        if al <= 0:
            return
        d.line([(x, yc), (x, y_box)], fill=col + (int(255 * al),), width=4)
        d.ellipse([x - 11, yc - 11, x + 11, yc + 11], fill=col + (int(255 * al),))

    for i in range(3):
        box(240, ys[i], ys[i], "H", CYAN, (t - 1.0) / 0.4)
    box(240, ys[3], ys[3], "X", MAGENTA, (t - 1.2) / 0.4)
    ctrl(390, ys[0], ys[3] - 28, GOLD, (t - 1.8) / 0.4)
    box(390, ys[3], ys[6], "×7", GOLD, (t - 1.8) / 0.4)
    ctrl(540, ys[1], ys[3] - 28, GOLD, (t - 2.4) / 0.4)
    box(540, ys[3], ys[6], "×4", GOLD, (t - 2.4) / 0.4)
    box(720, ys[0], ys[2], "iQFT", CYAN, (t - 3.0) / 0.4)
    for i in range(3):
        box(880, ys[i], ys[i], "M", GREEN, (t - 3.5) / 0.4)
    text(d, "IQM Garnet · 20-qubit superconducting chip", 905, 34, WHITE, a * ease((t - 4.2) / 0.5), face=DEMI)
    text(d, "rented by the shot on Amazon Braket", 955, 34, DIM, a * ease((t - 4.6) / 0.5), face=MED)


def s_hist(d, t, a):
    text(d, f"{shots} runs on the real chip", 110, 54, WHITE, a)
    base, top = 800, 230
    mx = max(counts)
    bw, gap = 88, 26
    left = (W - (8 * bw + 7 * gap)) // 2
    g = ease((t - 0.4) / 2.2)
    for v, c in enumerate(counts):
        x = left + v * (bw + gap)
        h = (base - top) * c / mx * g
        col = GOLD if v in (2, 6) else CYAN if v in (0, 4) else NOISE
        d.rounded_rectangle([x, base - max(h, 2), x + bw, base], 10, fill=col + (int(255 * a),))
        d.text((x + bw / 2, base - h - 26), str(round(c * g)), font=font(30, DEMI),
               fill=WHITE + (int(255 * a * min(1, g * 3)),), anchor="mm")
        d.text((x + bw / 2, base + 34), f"{v:03b}", font=font(28, 0, MONO), fill=DIM + (int(255 * a),), anchor="mm")
    text(d, f"{pct}% landed on the 4 right answers", 905, 46, CYAN, a * ease((t - 3.0) / 0.5))
    text(d, "grey = noise from real hardware", 965, 32, NOISE, a * ease((t - 3.6) / 0.5), face=DEMI)


def s_math(d, t, a):
    lines = [
        ("gold peak 010 means 2/8 = 1/4", WHITE, 300, 50),
        ("so the pattern repeats every r = 4", WHITE, 380, 50),
        ("gcd(7² − 1, 15) = 3", CYAN, 500, 58),
        ("gcd(7² + 1, 15) = 5", CYAN, 580, 58),
    ]
    for i, (s, c, y, sz) in enumerate(lines):
        text(d, s, y, sz, c, a * ease((t - i * 0.7) / 0.5), face=DEMI if i < 2 else BOLD)
    k = ease((t - 3.0) / 0.5)
    text(d, "15 = 3 × 5", 760, int(110 + 10 * math.sin(t * 5) * k), GOLD, a * k, face=HEAVY, x=W // 2 - 50)
    if k > 0:
        cx, cy = 880, 760
        d.line([(cx - 34, cy), (cx - 8, cy + 28), (cx + 40, cy - 34)], fill=GREEN + (int(255 * a * k),), width=14)


def s_honest(d, t, a):
    text(d, "Honest fine print", 300, 62, MAGENTA, a)
    items = ["The circuit was hand-built knowing it's 15", "No error correction",
             "Like most small Shor demos"]
    for i, s in enumerate(items):
        text(d, "•  " + s, 450 + i * 90, 42, WHITE, a * ease((t - 0.5 - i * 0.6) / 0.5), face=MED, x=150, anchor="lm")


def s_scale(d, t, a):
    text(d, "How far away is the real threat?", 200, 50, WHITE, a)
    text(d, "This chip", 380, 38, CYAN, a, face=DEMI, x=110, anchor="lm")
    text(d, "20 qubits", 380, 38, CYAN, a, face=BOLD, x=970, anchor="rm")
    d.ellipse([110, 425, 122, 437], fill=CYAN + (int(255 * a),))
    text(d, "Breaking RSA-2048", 560, 38, MAGENTA, a * ease((t - 0.6) / 0.4), face=DEMI, x=110, anchor="lm")
    text(d, "< 1,000,000", 560, 38, MAGENTA, a * ease((t - 0.6) / 0.4), face=BOLD, x=970, anchor="rm")
    g = ease((t - 1.0) / 1.6)
    d.rounded_rectangle([110, 600, 110 + 860 * g, 640], 10, fill=MAGENTA + (int(255 * a),))
    text(d, "50,000× more qubits, all running error correction", 760, 34, WHITE,
         a * ease((t - 2.6) / 0.5), face=MED)
    text(d, "Estimate: C. Gidney (Google), 2025", 960, 28, DIM, a * ease((t - 2.6) / 0.5), face=MED)


def s_falcon(d, t, a):
    text(d, "When that day comes:", 280, 50, DIM, a, face=DEMI)
    k = a * ease((t - 0.4) / 0.6)
    cx, cy = W // 2, 470
    shield = [(cx, cy - 110), (cx + 95, cy - 70), (cx + 85, cy + 40), (cx, cy + 110), (cx - 85, cy + 40), (cx - 95, cy - 70)]
    d.polygon(shield, fill=GREEN + (int(60 * k),), outline=GREEN + (int(255 * k),), width=6)
    d.line([(cx - 40, cy), (cx - 10, cy + 32), (cx + 45, cy - 35)], fill=GREEN + (int(255 * k),), width=12)
    text(d, "Algorand mainnet already supports", 680, 46, WHITE, a * ease((t - 1.0) / 0.5), face=DEMI)
    text(d, "post-quantum Falcon-1024 accounts", 750, 50, GREEN, a * ease((t - 1.4) / 0.5))


def s_end(d, t, a):
    text(d, "15 today.", 450, 96, GOLD, a * ease(t / 0.5), face=HEAVY)
    text(d, "2048 bits someday.", 570, 80, MAGENTA, a * ease((t - 0.7) / 0.5), face=HEAVY)
    text(d, "Upgrade your crypto before then.", 720, 42, WHITE, a * ease((t - 1.5) / 0.5), face=DEMI)


SCENES = [(s_hook, 4.0), (s_why, 4.5), (s_task, 3.8), (s_circuit, 7.0), (s_hist, 6.5),
          (s_math, 5.2), (s_honest, 4.5), (s_scale, 5.5), (s_falcon, 4.8), (s_end, 4.2)]

total = sum(dur for _, dur in SCENES)
ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                       "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium",
                       "-crf", "19", "-pix_fmt", "yuv420p", "-movflags", "+faststart", OUT], stdin=subprocess.PIPE)
start = 0.0
for fn, dur in SCENES:
    for i in range(int(dur * FPS)):
        t = i / FPS
        a = min(1.0, t / 0.35, (dur - t) / 0.35)
        frame = background(start + t)
        layer = Image.new("RGBA", (W, H))
        fn(ImageDraw.Draw(layer), t, a)
        ff.stdin.write(Image.alpha_composite(frame, layer).convert("RGB").tobytes())
    start += dur
ff.stdin.close()
ff.wait()
print(f"{OUT}: {total:.1f}s, {shots} shots, {pct}% in the right peaks")
