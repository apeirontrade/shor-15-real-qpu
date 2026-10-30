"""Long explainer: narration + synthesized music/SFX + animated scenes + burned-in subtitles.

Usage (from quantum-demo/):
  .venv/bin/python explainer/make.py out.mp4            # full video
  .venv/bin/python explainer/make.py out.mp4 rsa_clock  # render listed scenes only (preview)
Needs explainer/voice/<scene>.wav + durations.json (see voice.py).
"""
import json
import math
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from ecdlp import build as ecdlp_build, recover  # noqa: E402
from grover import key_counts  # noqa: E402
from script import SCRIPT  # noqa: E402
from toycurve import find_toy  # noqa: E402
from vidkit import (BG, BOLD, CYAN, DEMI, DIM, DOTS, FPS, GOLD, GREEN, H, HEAVY, MAGENTA, MED, NOISE, RED,  # noqa: E402
                    W, WHITE, bars, check, cross, ease, font, text)

HERE = os.path.dirname(__file__)
ROOT = os.path.join(HERE, "..")
SR = 48000
PAD = 0.9  # seconds of breathing room after each line
TITLE_LEN = 3.5

# ---------------------------------------------------------------- data from the real runs
shor = json.load(open(os.path.join(ROOT, "results/qpu_result_light.json")))
shor_counts = [shor["marginal"][str(v)] for v in range(8)]
ec = json.load(open(os.path.join(ROOT, "results/ecdlp_qpu.json")))
_votes, _, _ = recover(ec["raw_counts"], ecdlp_build(4, 3)[1], 4)
ec_votes = [_votes.get(k, 0) for k in range(4)]
gr = json.load(open(os.path.join(ROOT, "results/grover_qpu.json")))
gr_keys = [key_counts(gr["raw_counts"])[k] for k in range(8)]
curve, G8, _ = find_toy(8)
curve_pts = curve.points()

DUR = json.load(open(os.path.join(HERE, "voice/durations.json")))


def A(c, a):
    return c + (int(255 * max(0.0, min(1.0, a))),)


# ---------------------------------------------------------------- drawing helpers
def padlock(d, cx, cy, s, col, a, open_=0.0):
    d.arc([cx - s * 0.55, cy - s * 1.25 - open_ * s * 0.5, cx + s * 0.55, cy - s * 0.15 - open_ * s * 0.5], 180, 360,
          fill=A(col, a), width=max(6, int(s * 0.16)))
    d.line([(cx + s * 0.55 - s * 0.08, cy - s * 0.7 - open_ * s * 0.5), (cx + s * 0.55 - s * 0.08, cy - s * 0.2)],
           fill=A(col, a), width=max(6, int(s * 0.16)))
    d.line([(cx - s * 0.55 + s * 0.08, cy - s * 0.7 - open_ * s * 0.5), (cx - s * 0.55 + s * 0.08, cy - s * 0.2 - open_ * s * 0.6)],
           fill=A(col, a), width=max(6, int(s * 0.16)))
    d.rounded_rectangle([cx - s * 0.8, cy - s * 0.25, cx + s * 0.8, cy + s * 0.85], int(s * 0.15), fill=A(col, a))
    d.ellipse([cx - s * 0.12, cy + s * 0.15, cx + s * 0.12, cy + s * 0.39], fill=A((15, 23, 42), a))


def vault(d, cx, cy, r, a, spin=0.0):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=A((51, 65, 85), a), outline=A(DIM, a), width=10)
    d.ellipse([cx - r * 0.8, cy - r * 0.8, cx + r * 0.8, cy + r * 0.8], outline=A(NOISE, a), width=6)
    for i in range(6):
        ang = spin + i * math.pi / 3
        d.line([(cx, cy), (cx + math.cos(ang) * r * 0.6, cy + math.sin(ang) * r * 0.6)], fill=A(DIM, a), width=12)
    d.ellipse([cx - r * 0.18, cy - r * 0.18, cx + r * 0.18, cy + r * 0.18], fill=A(DIM, a))


def toothpick(d, x, y, a):
    d.line([(x, y), (x + 120, y - 40)], fill=A((222, 184, 135), a), width=6)


def card(d, x, y, w, h, title, sub, col, a, tsize=44):
    d.rounded_rectangle([x, y, x + w, y + h], 24, fill=A((15, 23, 42), 0.86 * a), outline=A(col, a), width=5)
    d.text((x + w / 2, y + h * 0.40), title, font=font(tsize, BOLD), fill=A(col, a), anchor="mm")
    if sub:
        d.text((x + w / 2, y + h * 0.70), sub, font=font(28, MED), fill=A(WHITE, a), anchor="mm")


def header(d, s, col, a, y=95, size=58):
    text(d, s, y, size, col, a)


# ---------------------------------------------------------------- scenes: fn(d, t, a, dur)
def sc_cold_open(d, t, a, dur):
    cols = [MAGENTA, GOLD, CYAN, GREEN]
    for i, c in enumerate(cols):
        shake = math.sin(t * 18 + i) * 6 * ease((t - 2.5) / 0.3) * (1 - ease((t - 6) / 0.5))
        padlock(d, 210 + i * 220 + shake, 440, 70, c, a * ease((t - 0.2 - i * 0.25) / 0.4), open_=ease((t - 7 - i * 0.3) / 0.5) if i < 3 else 0)
    text(d, "We rented a real quantum computer", 690, 54, WHITE, a * ease((t - 0.8) / 0.5))
    text(d, "and attacked the locks of the internet.", 760, 46, CYAN, a * ease((t - 1.6) / 0.5), face=DEMI)


def sc_title(d, t, a, dur):
    k = ease(t / 0.6)
    text(d, "CRYPTO LOCKS", 410, int(120 * (0.9 + 0.1 * k)), GOLD, a * k, face=HEAVY)
    text(d, "vs", 520, 60, DIM, a * k, face=DEMI)
    text(d, "A REAL QUANTUM COMPUTER", 620, 60, MAGENTA, a * ease((t - 0.4) / 0.6), face=HEAVY)


def coin(d, cx, cy, r, t, spinning, a, label):
    if spinning:
        w = abs(math.cos(t * 7)) * r + 6
        col = GOLD if math.cos(t * 7) > 0 else CYAN
    else:
        w, col = r, GOLD
    d.ellipse([cx - w, cy - r, cx + w, cy + r], fill=A(col, a), outline=A(WHITE, a), width=5)
    if not spinning:
        d.text((cx, cy), "1", font=font(110, HEAVY), fill=A((15, 23, 42), a), anchor="mm")
    text(d, label, cy + r + 70, 44, WHITE, a, face=DEMI, x=cx)


def sc_bits(d, t, a, dur):
    header(d, "Bits vs qubits", WHITE, a)
    coin(d, 300, 470, 150, t, False, a * ease((t - 0.3) / 0.5), "bit: 0 or 1")
    coin(d, 780, 470, 150, t, True, a * ease((t - 4.0) / 0.5), "qubit: still spinning")


def sc_interference(d, t, a, dur):
    header(d, "Interference", WHITE, a)
    for row, (phase, col, lab) in enumerate(((0.0, GREEN, "in step: they add up"), (math.pi, RED, "out of step: they cancel"))):
        y0 = 290 + row * 360
        k = a * ease((t - 0.5 - row * 2.5) / 0.6)
        if k <= 0:
            continue
        pts1, pts2, pts3 = [], [], []
        for x in range(80, 1000, 6):
            u = (x - 80) / 920 * 4 * math.pi + t * 2.5
            w1, w2 = math.sin(u), math.sin(u + phase)
            pts1.append((x, y0 - 60 + 22 * w1))
            pts2.append((x, y0 - 60 + 22 * w2 + 1))
            pts3.append((x, y0 + 50 + 30 * (w1 + w2)))
        d.line(pts1, fill=A(CYAN, k * 0.7), width=3)
        d.line(pts2, fill=A(MAGENTA, k * 0.7), width=3)
        d.line(pts3, fill=A(col, k), width=6)
        text(d, lab, y0 + 165, 34, col, k, face=DEMI)


def sc_chip(d, t, a, dur):
    header(d, "Our rented chip", WHITE, a)
    cx, cy, s = W // 2, 470, 230
    d.rounded_rectangle([cx - s, cy - s, cx + s, cy + s], 30, fill=A((30, 41, 59), a), outline=A(CYAN, a), width=6)
    for i in range(12):
        for side in (-1, 1):
            off = -s + 30 + i * (2 * s - 60) / 11
            d.line([(cx + off, cy + side * s), (cx + off, cy + side * (s + 30))], fill=A(DIM, a), width=6)
            d.line([(cx + side * s, cy + off), (cx + side * (s + 30), cy + off)], fill=A(DIM, a), width=6)
    for i in range(20):
        r, c = divmod(i, 5)
        x = cx - 160 + c * 80
        y = cy - 120 + r * 80
        glow = 0.5 + 0.5 * math.sin(t * 3 + i * 0.7)
        rad = 14 + 6 * glow
        d.ellipse([x - rad, y - rad, x + rad, y + rad], fill=A(GOLD if i % 3 else MAGENTA, a * (0.6 + 0.4 * glow)))
    text(d, "20 qubits · rented by the shot", 800, 42, CYAN, a * ease((t - 1.0) / 0.5), face=DEMI)
    text(d, "IQM Garnet via Amazon Braket", 860, 34, DIM, a * ease((t - 1.5) / 0.5), face=MED)
    text(d, "< 1¢ per shot", 940, 40, GOLD, a * ease((t - 8.0) / 0.5))


def sc_locks(d, t, a, dur):
    header(d, "4 kinds of lock", WHITE, a, y=110)
    cards = [("RSA", "websites, banks", MAGENTA, 1.5), ("Elliptic curves", "Bitcoin · Ethereum · Algorand", GOLD, 4.0),
             ("AES / SHA-256", "stored data, hashing", CYAN, 8.5), ("Falcon", "built for the quantum age", GREEN, 12.5)]
    for i, (ti, sub, col, at) in enumerate(cards):
        x = 60 + (i % 2) * 495
        y = 220 + (i // 2) * 360
        card(d, x, y, 465, 320, ti, sub, col, a * ease((t - at) / 0.5))
        padlock(d, x + 232, y + 50, 26, col, a * ease((t - at) / 0.5))


def sc_rsa_idea(d, t, a, dur):
    header(d, "Lock 1 · RSA", MAGENTA, a)
    text(d, "3 × 5 = 15", 330, 96, GREEN, a * ease((t - 1.0) / 0.5), face=HEAVY)
    text(d, "easy", 420, 40, GREEN, a * ease((t - 1.0) / 0.5), face=DEMI)
    text(d, "15 = ? × ?", 590, 96, RED, a * ease((t - 3.0) / 0.5), face=HEAVY)
    text(d, "hard (for big numbers)", 680, 40, RED, a * ease((t - 3.0) / 0.5), face=DEMI)
    text(d, "Real RSA numbers: 617 digits", 850, 44, WHITE, a * ease((t - 5.5) / 0.5), face=DEMI)


def sc_rsa_clock(d, t, a, dur):
    header(d, "Shor's trick: find the rhythm", MAGENTA, a)
    cx, cy, R = W // 2, 520, 300
    d.ellipse([cx - R, cy - R, cx + R, cy + R], outline=A(DIM, a), width=5)
    pos = lambda n: (cx + R * math.sin(2 * math.pi * n / 15), cy - R * math.cos(2 * math.pi * n / 15))  # noqa: E731
    for n in range(15):
        x, y = pos(n)
        d.ellipse([x - 26, y - 26, x + 26, y + 26], fill=A((15, 23, 42), a), outline=A(NOISE, a), width=3)
        d.text((x, y), str(n), font=font(28, DEMI), fill=A(DIM, a), anchor="mm")
    seq = [pow(7, x, 15) for x in range(5)]  # 1, 7, 4, 13, 1
    step = (t - 2.5) / 1.4
    for i in range(min(4, max(0, int(step)) + 1)):
        if step < i:
            break
        p0, p1 = pos(seq[i]), pos(seq[i + 1])
        f = ease(step - i)
        d.line([p0, (p0[0] + (p1[0] - p0[0]) * f, p0[1] + (p1[1] - p0[1]) * f)], fill=A(GOLD, a), width=8)
    for i, n in enumerate(seq[:4]):
        if step >= i - 0.2:
            x, y = pos(n)
            d.ellipse([x - 30, y - 30, x + 30, y + 30], fill=A(GOLD, a), outline=A(WHITE, a), width=3)
            d.text((x, y), str(n), font=font(30, BOLD), fill=A((15, 23, 42), a), anchor="mm")
    text(d, "×7 each step, on a 15-hour clock", 880, 40, WHITE, a * ease((t - 2.5) / 0.5), face=DEMI)
    text(d, "1 · 7 · 4 · 13 · 1: repeats every 4", 945, 44, GOLD, a * ease((t - 8.5) / 0.5))


def sc_rsa_result(d, t, a, dur):
    header(d, f"Real chip: {sum(shor_counts)} shots", WHITE, a)
    g = ease((t - 0.3) / 2.0)
    bars(d, shor_counts, [GOLD if v in (2, 6) else CYAN if v in (0, 4) else NOISE for v in range(8)],
         [f"{v:03b}" for v in range(8)], a, g, base=640, top=220)
    pct = round(100 * sum(shor_counts[v] for v in (0, 2, 4, 6)) / sum(shor_counts))
    text(d, f"{pct}% on the right answers · grey = noise", 730, 38, CYAN, a * ease((t - 2.5) / 0.5), face=DEMI)
    k = ease((t - 6.5) / 0.5)
    text(d, "15 = 3 × 5", 870, int(110 + 8 * math.sin(t * 5) * k), GOLD, a * k, face=HEAVY, x=W // 2 - 40)
    if k > 0:
        check(d, 840, 870, 34, GREEN, a * k)


def sc_vault(d, t, a, dur):
    header(d, "Toothpick, meet vault", WHITE, a)
    vault(d, 680, 470, 260, a * ease((t - 0.3) / 0.5), spin=t * 0.15)
    toothpick(d, 150, 560, a * ease((t - 8.5) / 0.5))
    text(d, "us", 590, 34, GOLD, a * ease((t - 8.5) / 0.5), x=210)
    text(d, "RSA-2048 needs < 1,000,000 qubits", 830, 42, WHITE, a * ease((t - 4.5) / 0.5), face=DEMI)
    text(d, "We had 20.   (estimate: Gidney, Google, 2025)", 890, 32, DIM, a * ease((t - 6.5) / 0.5), face=MED)


def edwards_y(x, dd=-12.0):
    return math.sqrt((1 + x * x) / (1 - dd * x * x))


def sc_ecc_idea(d, t, a, dur):
    header(d, "Lock 2 · Elliptic curves", GOLD, a)
    sx, sy, ox, oy = 340, 330, W // 2, 620
    pts = [(ox + x * sx, oy - edwards_y(x) * sy) for x in np.linspace(-1.35, 1.35, 120)]
    d.line(pts, fill=A(GOLD, a), width=6)
    hops = [-1.1, 0.3, -0.45, 0.9, 0.05, 1.2]
    n = min(len(hops) - 1, int(max(0, t - 2.0) / 0.9))
    for i in range(n + 1):
        x = hops[i]
        px, py = ox + x * sx, oy - edwards_y(x) * sy
        if i:
            xp = hops[i - 1]
            qx, qy = ox + xp * sx, oy - edwards_y(xp) * sy
            d.arc([min(px, qx), min(py, qy) - 120, max(px, qx) + 1, max(py, qy) + 40], 180, 360, fill=A(CYAN, a * 0.8), width=4)
        col = MAGENTA if i == len(hops) - 1 else CYAN
        d.ellipse([px - 16, py - 16, px + 16, py + 16], fill=A(col, a))
    text(d, "secret = number of hops", 760, 42, CYAN, a * ease((t - 3.0) / 0.5), face=DEMI)
    text(d, "public = where you land", 820, 42, MAGENTA, a * ease((t - 5.0) / 0.5), face=DEMI)
    text(d, "forward: easy · backward: hard", 920, 40, WHITE, a * ease((t - 7.5) / 0.5))


def sc_ecc_mini(d, t, a, dur):
    header(d, "A mini copy of Algorand's curve", GOLD, a, size=50)
    text(d, "−x² + y² = 1 + d·x²y²  (same equation as Ed25519)", 165, 32, DIM, a, face=MED)
    gx, gy, cell = 230, 230, 48
    G4 = curve.mul(2, G8)
    Q = curve.mul(3, G4)
    sub = [curve.mul(m, G4) for m in range(4)]
    for x in range(13):
        for y in range(13):
            px, py = gx + x * cell, gy + (12 - y) * cell
            d.ellipse([px - 3, py - 3, px + 3, py + 3], fill=A(NOISE, a * 0.6))
    for i, P in enumerate(curve_pts):
        px, py = gx + P[0] * cell, gy + (12 - P[1]) * cell
        k = a * ease((t - 0.8 - i * 0.08) / 0.3)
        col = GOLD if P in sub else CYAN
        d.ellipse([px - 13, py - 13, px + 13, py + 13], fill=A(col, k))
    qx, qy = gx + Q[0] * cell, gy + (12 - Q[1]) * cell
    k = a * ease((t - 4.5) / 0.5)
    d.ellipse([qx - 26, qy - 26, qx + 26, qy + 26], outline=A(MAGENTA, k), width=6)
    text(d, f"public key {Q}", qy - 50, 32, MAGENTA, k, x=qx)
    text(d, "16 points (the real curve: a 77-digit number of them)", 900, 34, WHITE, a * ease((t - 2.0) / 0.5), face=DEMI)
    text(d, "the chip only gets the public key", 960, 34, MAGENTA, a * ease((t - 6.0) / 0.5), face=DEMI)


def sc_ecc_result(d, t, a, dur):
    header(d, "Real chip: which key?", WHITE, a)
    g = ease((t - 0.3) / 2.0)
    bars(d, ec_votes, [NOISE, NOISE, NOISE, GOLD], ["key 0", "key 1", "key 2", "key 3"], a, g, base=650, top=230,
         bw=150, gap=50, label_path="/System/Library/Fonts/Avenir Next.ttc")
    k = ease((t - 2.0) / 0.5)
    text(d, "Secret key found: 3", 800, 64, GOLD, a * k, face=HEAVY)
    text(d, "(only 4 possible keys, a true toy)", 880, 36, DIM, a * ease((t - 6.0) / 0.5), face=MED)


def sc_ecc_real(d, t, a, dur):
    header(d, "The real curve", WHITE, a)
    vault(d, 680, 470, 260, a, spin=t * 0.15)
    toothpick(d, 150, 560, a * ease((t - 4.0) / 0.4))
    text(d, "256-bit curves: < 500,000 physical qubits", 830, 40, WHITE, a * ease((t - 1.0) / 0.5), face=DEMI)
    text(d, "Google Quantum AI, March 2026", 890, 30, DIM, a * ease((t - 1.0) / 0.5), face=MED)


def sc_aes(d, t, a, dur):
    header(d, "Lock 3 · AES: Grover's search", CYAN, a, size=52)
    if t < 8.5:
        # ideal amplitude amplification, 0 -> 1 -> 2 iterations
        it = min(2.0, max(0.0, (t - 3.0) / 2.0))
        theta = math.asin(1 / math.sqrt(8))
        pm = math.sin((2 * it + 1) * theta) ** 2
        vals = [(1 - pm) / 7 * 1000 if k != 5 else pm * 1000 for k in range(8)]
        bars(d, [max(v, 1) for v in vals], [GOLD if k == 5 else NOISE for k in range(8)], [f"{k:03b}" for k in range(8)],
             a, 1.0, base=650, top=250)
        text(d, f"ideal machine · check {int(it + 0.0001)}", 760, 38, WHITE, a, face=DEMI)
    else:
        k = ease((t - 8.5) / 0.4)
        bars(d, gr_keys, [GOLD if j == 5 else NOISE for j in range(8)], [f"{j:03b}" for j in range(8)], a * k,
             ease((t - 8.5) / 1.8), base=650, top=250)
        text(d, f"real chip: key found in 2 checks, {round(gr_keys[5] / 10)}% of shots", 760, 38, CYAN, a * k, face=DEMI)
    text(d, "(our toy lock was hard-wired to the key)", 820, 30, DIM, a, face=MED)


def sc_aes_real(d, t, a, dur):
    header(d, "Square root of giant = still giant", CYAN, a, size=50)
    big = "115792089237316195423570985008687907853269984665640564039457584007913129639936"  # 2^256
    half = "340282366920938463463374607431768211456"  # 2^128
    text(d, "AES-256 keys:", 280, 36, DIM, a, face=DEMI)
    text(d, big[:39], 340, 34, WHITE, a * ease((t - 0.5) / 0.5), path="/System/Library/Fonts/Menlo.ttc", face=0)
    text(d, big[39:], 385, 34, WHITE, a * ease((t - 0.5) / 0.5), path="/System/Library/Fonts/Menlo.ttc", face=0)
    text(d, "Grover still needs about:", 520, 36, DIM, a * ease((t - 2.5) / 0.5), face=DEMI)
    text(d, half, 590, 34, GREEN, a * ease((t - 2.5) / 0.5), path="/System/Library/Fonts/Menlo.ttc", face=0)
    text(d, "This lock holds.", 800, 80, GREEN, a * ease((t - 5.5) / 0.5), face=HEAVY)


def sc_falcon(d, t, a, dur):
    header(d, "Lock 4 · Falcon", GREEN, a)
    ox, oy = W // 2, 500
    b1, b2 = (70, 18), (28, 64)
    for i in range(-7, 8):
        for j in range(-6, 7):
            x = ox + i * b1[0] + j * b2[0] + math.sin(t * 0.6) * 10
            y = oy + i * b1[1] + j * b2[1]
            if 120 < x < 960 and 190 < y < 800:
                k = a * ease((t - 1.0 - (abs(i) + abs(j)) * 0.05) / 0.4)
                d.ellipse([x - 6, y - 6, x + 6, y + 6], fill=A(GREEN, k * 0.8))
    k = a * ease((t - 5.0) / 0.5)
    d.rounded_rectangle([200, 430, 880, 570], 24, fill=A((15, 23, 42), 0.9 * k), outline=A(GREEN, k), width=4)
    text(d, "a maze in hundreds of dimensions", 470, 36, WHITE, k, face=DEMI)
    text(d, "no rhythm for Shor's trick to find", 530, 36, WHITE, k, face=DEMI)
    text(d, "No known quantum attack", 880, 60, GREEN, a * ease((t - 10.0) / 0.5), face=HEAVY)


def sc_limits(d, t, a, dur):
    header(d, "Our limitations", MAGENTA, a)
    items = [("Toy locks", "15 · a 4-key curve · an 8-key search", 3.0),
             ("Hand-built circuits", "custom-made for each toy", 4.6),
             ("Noise", "8–35% of shots were wrong", 6.5),
             ("Proves nothing at real size", "in either direction", 9.5)]
    for i, (ti, sub, at) in enumerate(items):
        y = 230 + i * 180
        k = a * ease((t - at) / 0.5)
        d.rounded_rectangle([90, y, 990, y + 150], 22, fill=A((15, 23, 42), 0.86 * k), outline=A(MAGENTA, k), width=4)
        text(d, ti, y + 52, 44, WHITE, k, x=130, anchor="lm")
        text(d, sub, y + 108, 32, DIM, k, face=MED, x=130, anchor="lm")


def sc_bigger(d, t, a, dur):
    header(d, "Rent a bigger chip?", WHITE, a)
    text(d, "Amazon: a 107-qubit chip, online today", 220, 40, CYAN, a * ease((t - 2.0) / 0.5), face=DEMI)
    k = a * ease((t - 6.0) / 0.5)
    for i in range(5):
        for j in range(5):
            x, y = 220 + i * 26, 360 + j * 26
            d.ellipse([x - 8, y - 8, x + 8, y + 8], fill=A(NOISE, k))
    d.line([(370, 420), (460, 420)], fill=A(WHITE, k), width=6)
    d.polygon([(460, 405), (485, 420), (460, 435)], fill=A(WHITE, k))
    d.ellipse([520, 380, 600, 460], fill=A(GOLD, k))
    text(d, "many noisy qubits = 1 reliable qubit", 560, 36, WHITE, k, face=DEMI)
    k2 = a * ease((t - 12.0) / 0.5)
    text(d, "Record so far", 690, 34, DIM, k2, face=DEMI, x=110, anchor="lm")
    text(d, "70", 690, 40, GOLD, k2, x=970, anchor="rm")
    d.rounded_rectangle([110, 720, 110 + 860 * 70 / 1200, 750], 8, fill=A(GOLD, k2))
    text(d, "Needed to break a real curve", 820, 34, DIM, k2, face=DEMI, x=110, anchor="lm")
    text(d, "~1,200", 820, 40, MAGENTA, k2, x=970, anchor="rm")
    d.rounded_rectangle([110, 850, 110 + 860 * ease((t - 13.0) / 1.5), 880], 8, fill=A(MAGENTA, k2))
    text(d, "IBM + UChicago, July 2026 · Google Quantum AI, March 2026", 960, 26, NOISE, k2, face=MED)


def sc_score(d, t, a, dur):
    header(d, "Scoreboard", WHITE, a)
    rows = [("RSA", MAGENTA, False, 2.0), ("Elliptic curves", GOLD, False, 2.6),
            ("AES-256 / SHA-256", CYAN, True, 6.0), ("Falcon", GREEN, True, 6.6)]
    for i, (name, col, safe, at) in enumerate(rows):
        y = 290 + i * 160
        k = a * ease((t - at) / 0.4)
        d.rounded_rectangle([70, y - 60, 1010, y + 60], 20, fill=A((15, 23, 42), 0.8 * k), outline=A(col, 0.8 * k), width=3)
        text(d, name, y, 44, col, k, x=110, anchor="lm")
        if safe:
            check(d, 880, y, 30, GREEN, k)
            text(d, "holds", y, 32, GREEN, k, face=DEMI, x=740)
        else:
            cross(d, 880, y, 28, RED, k)
            text(d, "breakable*", y, 32, RED, k, face=DEMI, x=740)
    text(d, "*once big error-corrected quantum computers exist", 960, 30, DIM, a * ease((t - 3.5) / 0.5), face=MED)


CHAINS = [("Bitcoin", "secp256k1"), ("Ethereum", "secp256k1"), ("Solana", "Ed25519"), ("Cardano", "Ed25519"),
          ("XRP Ledger", "secp256k1 / Ed25519"), ("BNB Chain", "secp256k1"), ("Avalanche", "secp256k1"),
          ("Tron", "secp256k1"), ("Dogecoin", "secp256k1"), ("Litecoin", "secp256k1"), ("Polkadot", "sr25519"),
          ("Stellar", "Ed25519"), ("Algorand", "Ed25519 · Falcon accounts available")]


def sc_chains(d, t, a, dur):
    header(d, "Major chains that sign with curves", GOLD, a, y=85, size=48)
    voice_len = DUR["chains"]
    for i, (name, crv) in enumerate(CHAINS):
        col_i, row = i % 2, i // 2
        x = 60 + col_i * 495
        y = 150 + row * 112
        if i == 12:
            x = 60 + 247
        at = 2.0 + i * (voice_len - 7.0) / 13
        k = a * ease((t - at) / 0.4)
        algo = name == "Algorand"
        d.rounded_rectangle([x, y, x + 465, y + 100], 18, fill=A((15, 23, 42), 0.88 * k),
                            outline=A(GOLD if algo else RED, 0.9 * k), width=3)
        text(d, name, y + 36, 36, WHITE, k, x=x + 24, anchor="lm")
        text(d, crv, y + 76, 26, GREEN if algo else DIM, k, face=MED, x=x + 24, anchor="lm")
        cross(d, x + 425, y + 50, 14, RED, k)
    k = a * ease((t - (voice_len - 4.5)) / 0.5)
    text(d, "Signatures: at risk someday.  Mining & hashing (SHA-256): hold.", 950, 28, WHITE, k, face=DEMI)
    text(d, "based on each chain's standard account signatures", 985, 24, NOISE, k, face=MED)


def sc_algorand(d, t, a, dur):
    header(d, "Where Algorand stands", WHITE, a)
    items = [("Standard accounts: Ed25519 (an elliptic curve)", WHITE, 1.0),
             ("Same kind of risk as Bitcoin & Ethereum", WHITE, 3.5),
             ("An address IS its public key: always visible", GOLD, 6.0),
             ("Mainnet already supports Falcon-1024 accounts", GREEN, 10.0),
             ("Bitcoin's main quantum proposal (BIP-360): a draft", DIM, 13.5)]
    for i, (s, col, at) in enumerate(items):
        text(d, s, 260 + i * 120, 36, col, a * ease((t - at) / 0.5), face=DEMI)
    text(d, "checked Oct 30 2026: Algorand consensus v42 · bitcoin/bips repo", 960, 26, NOISE, a * ease((t - 13.5) / 0.5), face=MED)


def sc_when(d, t, a, dur):
    header(d, "So when?", WHITE, a)
    k = a * ease((t - 1.0) / 0.5)
    card(d, 90, 230, 900, 260, "28–49%", "", GOLD, k, tsize=96)
    text(d, "chance within 10 years (26 experts, GRI survey 2025)", 430, 32, WHITE, k, face=MED)
    k2 = a * ease((t - 7.0) / 0.5)
    card(d, 90, 560, 900, 260, "2031", "", MAGENTA, k2, tsize=96)
    text(d, "US deadline: key systems switch signatures (EO 14412)", 760, 32, WHITE, k2, face=MED)


def sc_outro(d, t, a, dur):
    text(d, "Not today.", 380, 110, GOLD, a * ease(t / 0.5), face=HEAVY)
    text(d, "But the math works.", 510, 80, MAGENTA, a * ease((t - 0.8) / 0.5), face=HEAVY)
    text(d, "Upgrade before Q-Day.", 650, 50, WHITE, a * ease((t - 1.8) / 0.5), face=DEMI)
    text(d, "github.com/apeirontrade/shor-15-real-qpu", 830, 34, CYAN, a * ease((t - 3.5) / 0.5), face=DEMI)


SCENE_FN = {k[3:]: v for k, v in globals().items() if k.startswith("sc_")}


# ---------------------------------------------------------------- timeline
def timeline(only=None):
    out, start = [], 0.0
    for sid, line, cap in SCRIPT:
        if only is not None and sid not in only:
            continue
        dur = TITLE_LEN if sid == "title" else DUR[sid] + PAD
        out.append((sid, line, cap, start, dur))
        start += dur
    return out


def subtitle_chunks(line, voice_len):
    """Split narration into ~1-sentence chunks timed by character count."""
    parts, cur = [], ""
    for word in line.split():
        cur = (cur + " " + word).strip()
        if word.endswith((".", "?", "!")) or len(cur) > 46:
            parts.append(cur)
            cur = ""
    if cur:
        parts.append(cur)
    total = sum(len(p) for p in parts)
    t, out = 0.0, []
    for p in parts:
        dt = voice_len * len(p) / total
        out.append((t, t + dt, p))
        t += dt
    return out


def draw_subtitle(d, s):
    f = font(32, DEMI)
    w = d.textlength(s, font=f)
    d.rounded_rectangle([W / 2 - w / 2 - 18, 1010, W / 2 + w / 2 + 18, 1060], 12, fill=(0, 0, 0, 150))
    d.text((W / 2, 1035), s, font=f, fill=WHITE + (255,), anchor="mm")


# ---------------------------------------------------------------- audio
def tone_env(n, attack, release):
    env = np.ones(n)
    a, r = min(int(attack * SR), n // 2), min(int(release * SR), n // 2)
    env[:a] = np.linspace(0, 1, a)
    env[-r:] *= np.linspace(1, 0, r)
    return env


def music(seconds):
    """Gentle synth bed: Am - F - C - G pads, a soft arpeggio and a quiet pulse at 96 bpm."""
    n = int(seconds * SR)
    t = np.arange(n) / SR
    out = np.zeros(n)
    chords = [[57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62]]
    bar = 4 * 60 / 96
    hz = lambda m: 440 * 2 ** ((m - 69) / 12)  # noqa: E731
    for b in range(int(seconds / bar) + 1):
        s0 = int(b * bar * SR)
        seg = min(n - s0, int(bar * SR))
        if seg <= 0:
            break
        tt = np.arange(seg) / SR
        ch = chords[b % 4]
        pad = sum(np.sin(2 * np.pi * hz(m) * tt) + 0.5 * np.sin(2 * np.pi * hz(m) * 1.003 * tt) for m in ch)
        out[s0:s0 + seg] += 0.05 * pad * tone_env(seg, 0.6, 0.6)
        for i in range(8):
            a0 = s0 + int(i * bar / 8 * SR)
            ln = int(0.35 * SR)
            if a0 + ln > n:
                break
            m = ch[i % 3] + 12 * (1 + (i // 3) % 2)
            ta = np.arange(ln) / SR
            out[a0:a0 + ln] += 0.035 * np.sin(2 * np.pi * hz(m) * ta) * np.exp(-ta * 9)
        for i in range(4):
            k0 = s0 + int(i * bar / 4 * SR)
            ln = int(0.18 * SR)
            if k0 + ln > n:
                break
            tk = np.arange(ln) / SR
            out[k0:k0 + ln] += 0.09 * np.sin(2 * np.pi * (50 + 60 * np.exp(-tk * 30)) * tk) * np.exp(-tk * 22)
    return out


def sfx_whoosh():
    ln = int(0.5 * SR)
    rng = np.random.default_rng(1)
    noise = rng.standard_normal(ln)
    k = np.linspace(0.02, 0.4, ln)
    y = np.zeros(ln)
    for i in range(1, ln):  # one-pole low-pass with a rising cutoff
        y[i] = y[i - 1] + k[i] * (noise[i] - y[i - 1])
    return 0.12 * y * np.sin(np.linspace(0, np.pi, ln))


def sfx_chime():
    ln = int(1.2 * SR)
    t = np.arange(ln) / SR
    return 0.12 * (np.sin(2 * np.pi * 880 * t) + 0.6 * np.sin(2 * np.pi * 1320 * t)) * np.exp(-t * 3.5)


def sfx_glitch():
    ln = int(0.4 * SR)
    rng = np.random.default_rng(2)
    sq = np.sign(np.sin(2 * np.pi * 180 * np.arange(ln) / SR)) * (rng.random(ln) > 0.5)
    return 0.05 * sq * np.exp(-np.arange(ln) / SR * 6)


CHIME_AT = {"rsa_result": 6.5, "ecc_result": 2.0, "aes": 9.5}


def build_audio(tl, total, path):
    n = int(total * SR) + SR
    voice = np.zeros(n)
    sfx = np.zeros(n)
    w, c, g = sfx_whoosh(), sfx_chime(), sfx_glitch()
    for sid, line, _, start, dur in tl:
        s = int(start * SR)
        if line:
            raw = subprocess.check_output(["ffmpeg", "-loglevel", "error", "-i", os.path.join(HERE, f"voice/{sid}.wav"),
                                           "-f", "s16le", "-ac", "1", "-ar", str(SR), "-"])
            v = np.frombuffer(raw, dtype=np.int16).astype(float) / 32768
            vs = s + int(0.35 * SR)
            voice[vs:vs + len(v)] += v[: n - vs]
        sfx[s:s + len(w)] += w[: n - s]
        if sid in CHIME_AT:
            cs = s + int(CHIME_AT[sid] * SR)
            sfx[cs:cs + len(c)] += c[: n - cs]
        if sid == "limits":
            for off in (6.5, 6.9):
                gs = s + int(off * SR)
                sfx[gs:gs + len(g)] += g
    bed = music(n / SR)
    # duck the music under the voice
    env = np.convolve(np.abs(voice), np.ones(SR // 10) / (SR // 10), mode="same")
    duck = 1 - 0.65 * np.clip(env * 25, 0, 1)
    mix = 0.95 * voice + bed * duck + sfx
    mix[-SR:] *= np.linspace(1, 0, SR)
    pcm = (np.clip(mix, -1, 1) * 32767).astype(np.int16)
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "s16le", "-ar", str(SR), "-ac", "1", "-i", "-",
                    "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-ar", str(SR), "-ac", "2", path],
                   input=pcm.tobytes(), check=True)


# ---------------------------------------------------------------- render
def bg_frame(t):
    img = BG.convert("RGBA")
    layer = Image.new("RGBA", (W, H))
    d = ImageDraw.Draw(layer)
    for x, y, r, vx, vy, c in DOTS:
        px, py = (x + vx * t) % W, (y + vy * t) % H
        tw = 0.35 + 0.25 * math.sin(t * 1.3 + x)
        d.ellipse([px - r, py - r, px + r, py + r], fill=c + (int(255 * tw * 0.5),))
    return Image.alpha_composite(img, layer)


def main():
    out = sys.argv[1]
    only = set(sys.argv[2:]) or None
    tl = timeline(only)
    total = sum(x[4] for x in tl)
    wav = out + ".wav"
    build_audio(tl, total, wav)
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                           "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", wav,
                           "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
                           "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", out], stdin=subprocess.PIPE)
    clock = 0.0
    for sid, line, cap, start, dur in tl:
        subs = subtitle_chunks(line, DUR.get(sid, 0)) if line else []
        fn = SCENE_FN[sid]
        for i in range(int(dur * FPS)):
            t = i / FPS
            a = min(1.0, t / 0.35, (dur - t) / 0.35)
            frame = bg_frame(clock + t)
            layer = Image.new("RGBA", (W, H))
            d = ImageDraw.Draw(layer)
            fn(d, t, a, dur)
            tv = t - 0.35
            for s0, s1, s in subs:
                if s0 <= tv < s1:
                    draw_subtitle(d, s)
            ff.stdin.write(Image.alpha_composite(frame, layer).convert("RGB").tobytes())
        clock += dur
    ff.stdin.close()
    ff.wait()
    os.remove(wav)
    print(f"{out}: {total:.1f}s, scenes: {[x[0] for x in tl]}")


if __name__ == "__main__":
    main()
