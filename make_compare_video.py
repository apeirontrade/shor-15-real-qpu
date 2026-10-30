"""Educational video: four kinds of crypto lock vs a real quantum chip, and where Algorand stands.

Usage: .venv/bin/python make_compare_video.py video/locks_x.mp4
Reads the hardware results in results/.
"""
import json
import math
import sys

from ecdlp import build as ecdlp_build, recover
from grover import key_counts
from vidkit import (BOLD, CYAN, DEMI, DIM, GOLD, GREEN, HEAVY, MAGENTA, MED, NOISE, RED, W, WHITE, bars, check,
                    cross, ease, font, render, text)

shor = json.load(open("results/qpu_result_light.json"))
shor_pct = round(100 * sum(shor["marginal"][str(v)] for v in (0, 2, 4, 6)) / shor["shots"])

ec = json.load(open("results/ecdlp_qpu.json"))
votes, _, _ = recover(ec["raw_counts"], ecdlp_build(4, 3)[1], 4)
ec_votes = [votes.get(k, 0) for k in range(4)]

gr = json.load(open("results/grover_qpu.json"))
gr_keys = [key_counts(gr["raw_counts"])[k] for k in range(8)]
gr_pct = round(100 * gr_keys[0b101] / sum(gr_keys))


def card(d, x, y, w, h, title, sub, col, a):
    d.rounded_rectangle([x, y, x + w, y + h], 24, fill=(15, 23, 42, int(220 * a)), outline=col + (int(255 * a),), width=5)
    d.text((x + w / 2, y + h * 0.40), title, font=font(44, BOLD), fill=col + (int(255 * a),), anchor="mm")
    d.text((x + w / 2, y + h * 0.68), sub, font=font(30, MED), fill=WHITE + (int(255 * a),), anchor="mm")


def s_hook(d, t, a):
    text(d, "Could a quantum computer", 400, 66, WHITE, a * ease(t / 0.5))
    text(d, "break today's encryption?", 480, 66, WHITE, a * ease(t / 0.5))
    text(d, "I tested 3 attacks on a real one.", 640, 50, CYAN, a * ease((t - 1.2) / 0.5), face=DEMI)


def s_locks(d, t, a):
    text(d, "4 kinds of lock", 150, 58, WHITE, a)
    cards = [("RSA", "banks, websites", MAGENTA), ("Elliptic curves", "Bitcoin · Ethereum · Algorand", GOLD),
             ("AES-256 / SHA-256", "stored data, hashing", CYAN), ("Falcon", "post-quantum signatures", GREEN)]
    for i, (ti, sub, col) in enumerate(cards):
        x = 60 + (i % 2) * 495
        y = 250 + (i // 2) * 360
        card(d, x, y, 465, 320, ti, sub, col, a * ease((t - 0.3 - i * 0.4) / 0.4))


def s_rsa(d, t, a):
    text(d, "Lock 1 · RSA", 140, 62, MAGENTA, a)
    text(d, "Attack: Shor's algorithm", 220, 40, DIM, a, face=DEMI)
    text(d, "Real chip factored", 400, 50, WHITE, a * ease((t - 0.5) / 0.5), face=DEMI)
    text(d, "15 = 3 × 5", 510, 120, GOLD, a * ease((t - 0.9) / 0.5), face=HEAVY)
    text(d, f"{shor_pct}% of {shor['shots']} shots correct", 630, 42, CYAN, a * ease((t - 1.5) / 0.5), face=DEMI)
    k = a * ease((t - 2.6) / 0.5)
    text(d, "Real RSA-2048 needs < 1,000,000 qubits", 830, 40, WHITE, k, face=DEMI)
    text(d, "This chip has 20.  (Gidney, Google, 2025)", 885, 32, DIM, k, face=MED)


def s_ecc(d, t, a):
    text(d, "Lock 2 · Elliptic curves", 110, 58, GOLD, a)
    text(d, "a mini copy of Algorand's curve: same equation,", 180, 34, WHITE, a, face=MED)
    text(d, "16 points instead of a 77-digit number", 225, 34, WHITE, a, face=MED)
    if t > 1.2:
        g = ease((t - 1.6) / 2.0)
        bars(d, ec_votes, [NOISE, NOISE, NOISE, GOLD], ["key 0", "key 1", "key 2", "key 3"], a * ease((t - 1.2) / 0.4),
             g, base=720, top=330, bw=150, gap=50, label_path="/System/Library/Fonts/Avenir Next.ttc")
    k = a * ease((t - 4.0) / 0.5)
    text(d, "Real chip found the secret key from the public key", 830, 38, CYAN, k, face=DEMI)
    text(d, "(only 4 possible keys, so it's a toy)", 880, 32, DIM, k, face=MED)
    k2 = a * ease((t - 7.0) / 0.5)
    text(d, "Real 256-bit curves: < 500,000 physical qubits", 965, 36, WHITE, k2, face=DEMI)
    text(d, "Google Quantum AI, March 2026", 1012, 28, DIM, k2, face=MED)


def s_aes(d, t, a):
    text(d, "Lock 3 · AES-256 & SHA-256", 110, 56, CYAN, a)
    text(d, "Attack: Grover's search, 8 possible keys", 185, 36, DIM, a, face=DEMI)
    if t > 0.8:
        g = ease((t - 1.0) / 2.0)
        bars(d, gr_keys, [GOLD if k == 0b101 else NOISE for k in range(8)], [f"{k:03b}" for k in range(8)],
             a * ease((t - 0.8) / 0.4), g, base=650, top=290)
    k = a * ease((t - 3.4) / 0.5)
    text(d, f"Found the key in 2 checks: {gr_pct}% of 1,000 shots", 760, 38, WHITE, k, face=DEMI)
    text(d, "(guessing takes 4.5 tries on average; the toy lock is hard-wired)", 808, 28, DIM, k, face=MED)
    k2 = a * ease((t - 6.0) / 0.5)
    text(d, "But it's only a square-root speed-up:", 900, 38, WHITE, k2, face=DEMI)
    text(d, "AES-256 still needs a 39-digit number of steps", 955, 38, GREEN, k2)


def s_falcon(d, t, a):
    text(d, "Lock 4 · Falcon", 250, 66, GREEN, a)
    text(d, "lattice math, not curves or primes", 330, 40, DIM, a, face=DEMI)
    k = a * ease((t - 0.8) / 0.6)
    cx, cy = W // 2, 540
    shield = [(cx, cy - 110), (cx + 95, cy - 70), (cx + 85, cy + 40), (cx, cy + 110), (cx - 85, cy + 40), (cx - 95, cy - 70)]
    d.polygon(shield, fill=GREEN + (int(60 * k),), outline=GREEN + (int(255 * k),), width=6)
    check(d, cx, cy, 38, GREEN, k)
    text(d, "No known quantum attack.", 760, 52, WHITE, a * ease((t - 1.4) / 0.5))
    text(d, "Nothing to run. NIST-selected for the post-quantum era.", 840, 34, DIM, a * ease((t - 2.0) / 0.5), face=MED)


def s_score(d, t, a):
    text(d, "Scoreboard", 120, 64, WHITE, a)
    text(d, "toy lock on", 230, 28, DIM, a, face=DEMI, x=640)
    text(d, "real chip", 262, 28, DIM, a, face=DEMI, x=640)
    text(d, "real lock vs", 230, 28, DIM, a, face=DEMI, x=900)
    text(d, "future QC", 262, 28, DIM, a, face=DEMI, x=900)
    rows = [("RSA", MAGENTA, f"{shor_pct}%", False), ("Elliptic curves", GOLD, "key found", False),
            ("AES-256 / SHA-256", CYAN, f"{gr_pct}%", True), ("Falcon", GREEN, "no attack", True)]
    for i, (name, col, chip, safe) in enumerate(rows):
        y = 380 + i * 150
        k = a * ease((t - 0.5 - i * 0.6) / 0.4)
        d.rounded_rectangle([50, y - 60, 1030, y + 60], 20, fill=(15, 23, 42, int(200 * k)), outline=col + (int(200 * k),), width=3)
        text(d, name, y, 40, col, k, x=90, anchor="lm")
        text(d, chip, y, 38, WHITE, k, face=DEMI, x=640)
        if safe:
            check(d, 900, y, 28, GREEN, k)
        else:
            cross(d, 900, y, 26, RED, k)
    text(d, "red = breakable once big quantum computers exist", 1000, 30, DIM, a * ease((t - 3.2) / 0.5), face=MED)


def s_algo(d, t, a):
    text(d, "So where does Algorand stand?", 150, 54, WHITE, a)
    items = [("Standard accounts use Ed25519, an elliptic curve:", WHITE),
             ("open to the same attack as Bitcoin & Ethereum", WHITE),
             ("An Algorand address IS its public key", GOLD),
             ("But mainnet already supports", GREEN),
             ("Falcon-1024 post-quantum accounts", GREEN),
             ("Bitcoin's main quantum proposal (BIP-360): still a draft", DIM)]
    ys = [300, 355, 470, 590, 645, 780]
    groups = [0, 0, 1, 2, 2, 3]
    for (s, col), y, g in zip(items, ys, groups):
        text(d, s, y, 38 if col != DIM else 32, col, a * ease((t - 0.5 - g * 1.4) / 0.5), face=DEMI)
    text(d, "Checked Oct 30 2026: Algorand consensus v42, bitcoin/bips repo", 960, 26, NOISE,
         a * ease((t - 5.0) / 0.5), face=MED)


def s_fine(d, t, a):
    text(d, "Honest fine print", 330, 60, MAGENTA, a)
    items = ["Toy-sized locks, hand-built circuits", "No error correction", "Nobody can break 256-bit crypto today"]
    for i, s in enumerate(items):
        text(d, "•  " + s, 470 + i * 85, 42, WHITE, a * ease((t - 0.4 - i * 0.5) / 0.5), face=MED, x=130, anchor="lm")


def s_end(d, t, a):
    text(d, "Not today.", 430, 100, GOLD, a * ease(t / 0.5), face=HEAVY)
    text(d, "But the math works.", 550, 76, MAGENTA, a * ease((t - 0.7) / 0.5), face=HEAVY)
    text(d, "Upgrade before Q-Day.", 700, 46, WHITE, a * ease((t - 1.5) / 0.5), face=DEMI)


SCENES = [(s_hook, 4.5), (s_locks, 5.5), (s_rsa, 7.0), (s_ecc, 11.0), (s_aes, 10.5), (s_falcon, 5.5),
          (s_score, 8.5), (s_algo, 9.5), (s_fine, 5.0), (s_end, 4.2)]

if __name__ == "__main__":
    total = render(SCENES, sys.argv[1])
    print(f"{sys.argv[1]}: {total:.1f}s  shor {shor_pct}%  ecdlp votes {ec_votes}  grover {gr_pct}%")
