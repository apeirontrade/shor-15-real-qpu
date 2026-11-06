import os
from collections import Counter
from PIL import Image, ImageDraw, ImageFont

# Compute exact ECDLP votes from raw JSON
ec_raw = {
  "101100": 45, "000010": 50, "000111": 12, "101101": 39, "111010": 30, "010100": 47,
  "000100": 16, "111000": 31, "010110": 34, "101010": 13, "000000": 41, "010111": 48,
  "101011": 11, "001000": 4, "000110": 25, "110110": 2, "001010": 6, "111001": 49,
  "000001": 36, "111110": 11, "101110": 47, "010101": 45, "000011": 36, "111111": 11,
  "010010": 11, "111011": 42, "010011": 15, "101000": 9, "101111": 28, "011000": 7,
  "110001": 6, "001110": 9, "011010": 4, "110111": 4, "110010": 5, "100101": 3,
  "110000": 13, "111101": 11, "100001": 8, "100100": 7, "110011": 5, "011101": 3,
  "011001": 4, "100111": 6, "010001": 10, "010000": 14, "011111": 2, "100011": 8,
  "011011": 9, "110101": 4, "101001": 11, "001101": 7, "011100": 4, "001001": 3,
  "001111": 5, "000101": 10, "100110": 6, "011110": 2, "001011": 5, "100000": 1,
  "001100": 5, "110100": 1, "100010": 3, "111100": 1
}
votes = Counter()
for bits, c in ec_raw.items():
    u = int(bits[0]) + (int(bits[1]) << 1)
    v = int(bits[2]) + (int(bits[3]) << 1)
    if u % 2 == 1:
        k_val = (v * pow(u, -1, 4)) % 4
        votes[k_val] += c
print("Computed ECDLP votes:", dict(votes))

shor_marginal = [254, 17, 252, 23, 224, 15, 193, 22]
grover_raw = {"101": 691, "011": 29, "110": 42, "100": 54, "010": 38, "001": 54, "111": 47, "000": 45}
# Check bit order: key 101 is index 5 (binary 101)
grover_vals = [grover_raw[f"{i:03b}"] for i in range(8)]
print("Grover vals:", grover_vals)

W, H = 1200, 1500
img = Image.new("RGB", (W, H), "#070B14")
draw = ImageDraw.Draw(img)

def load_font(path, size, variation=None):
    f = ImageFont.truetype(path, size)
    if variation:
        try:
            f.set_variation_by_name(variation)
        except Exception:
            pass
    return f

def find_font(prefer, needles):
    """Prefer the variable fonts this card was drawn with, then any matching file on the system."""
    for path in prefer:
        if os.path.isfile(path):
            return path
    roots = ("/usr/share/fonts", "/usr/local/share/fonts", os.path.expanduser("~/.local/share/fonts"))
    hits = []
    for root in roots:
        for dirpath, _, files in os.walk(root):
            for name in files:
                low = name.lower()
                if low.endswith((".ttf", ".otf")) and any(n in low for n in needles):
                    hits.append(os.path.join(dirpath, name))
    hits.sort(key=lambda p: (0 if "variable" in p.lower() or "[" in p else 1, len(p)))
    if not hits:
        raise SystemExit("missing font matching " + ", ".join(needles))
    return hits[0]

SG_PATH = find_font(
    ["/usr/share/fonts/truetype/sand-box/google/Space Grotesk/SpaceGrotesk-VariableFont_wght.ttf"],
    ("spacegrotesk",),
)
IN_PATH = find_font(
    ["/usr/share/fonts/truetype/sand-box/google/Inter/Inter-VariableFont_opsz,wght.ttf"],
    ("inter-variable", "inter[opsz"),
)
JB_PATH = find_font(
    ["/usr/share/fonts/truetype/sand-box/google/JetBrains Mono/JetBrainsMono-VariableFont_wght.ttf"],
    ("jetbrainsmono-variable", "jetbrainsmono[wght"),
)

f_eyebrow = load_font(JB_PATH, 19, "SemiBold")
f_title = load_font(SG_PATH, 54, "Bold")
f_sub = load_font(IN_PATH, 23, "Medium")
f_sec = load_font(JB_PATH, 20, "Bold")
f_card_title = load_font(SG_PATH, 26, "Bold")
f_card_stat = load_font(SG_PATH, 32, "Bold")
f_card_sub = load_font(IN_PATH, 19, "Regular")
f_mono_sm = load_font(JB_PATH, 16, "Medium")
f_mono_xs = load_font(JB_PATH, 14, "Regular")
f_row_title = load_font(SG_PATH, 26, "Bold")
f_row_desc = load_font(IN_PATH, 20, "Regular")
f_badge = load_font(JB_PATH, 16, "Bold")
f_footer = load_font(JB_PATH, 18, "Medium")

# Subtle top glow accent bar
draw.rectangle([0, 0, W, 8], fill="#38BDF8")

PAD = 56

# Eyebrow pill
pill_y = 44
pill_text = "IQM GARNET  •  20-QUBIT QPU VIA AMAZON BRAKET  •  $6.20 HARDWARE RUN"
tw = draw.textlength(pill_text, font=f_eyebrow)
draw.rounded_rectangle([PAD, pill_y, PAD + tw + 36, pill_y + 40], radius=20, fill="#0F2137", outline="#1E3A5F", width=2)
draw.text((PAD + 18, pill_y + 9), pill_text, font=f_eyebrow, fill="#38BDF8")

# Main Title & Subtitle
draw.text((PAD, 104), "Crypto Locks vs. a Real Quantum Chip", font=f_title, fill="#F8FAFC")
draw.text((PAD, 174), "Toy circuits broke all 3 classical schemes on real hardware. Full 256-bit keys stay safe today.", font=f_sub, fill="#94A3B8")

# Section 1 label
draw.text((PAD, 234), "01 // LIVE 20-QUBIT HARDWARE RESULTS (3,450 SHOTS)", font=f_sec, fill="#64748B")

# 3 Side-by-side Chart Cards
c_top = 272
c_h = 430
gap = 24
c_w = (W - 2 * PAD - 2 * gap) // 3

cards = [
    {
        "tag": "RSA  •  SHOR (N = 15)",
        "stat": "92.3% on peaks",
        "sub": "923 / 1,000 shots  →  15 = 3 × 5",
        "vals": shor_marginal,
        "labels": [f"{i:03b}" for i in range(8)],
        "hi": {0, 2, 4, 6},
        "color": "#38BDF8",
        "ymax": 300,
    },
    {
        "tag": "ECC  •  TOY ED25519",
        "stat": "Key k = 3 found",
        "sub": "311 votes vs 78 runner-up",
        "vals": [votes[0], votes[1], votes[2], votes[3]],
        "labels": ["k=0", "k=1", "k=2", "k=3"],
        "hi": {3},
        "color": "#FBBF24",
        "ymax": 350,
    },
    {
        "tag": "AES  •  GROVER (3-BIT)",
        "stat": "69.1% hit rate",
        "sub": "691 / 1,000 shots on key 101",
        "vals": grover_vals,
        "labels": [f"{i:03b}" for i in range(8)],
        "hi": {5},
        "color": "#34D399",
        "ymax": 750,
    },
]

for idx, c in enumerate(cards):
    cx = PAD + idx * (c_w + gap)
    draw.rounded_rectangle([cx, c_top, cx + c_w, c_top + c_h], radius=20, fill="#0E1628", outline="#1E293B", width=2)
    draw.text((cx + 24, c_top + 22), c["tag"], font=f_mono_sm, fill=c["color"])
    draw.text((cx + 24, c_top + 54), c["stat"], font=f_card_stat, fill="#F8FAFC")
    draw.text((cx + 24, c_top + 98), c["sub"], font=f_card_sub, fill="#94A3B8")

    # Bar plot area
    bx0, by0 = cx + 24, c_top + 156
    bw_tot = c_w - 48
    bh_tot = 215
    # Baseline
    draw.line([bx0, by0 + bh_tot, bx0 + bw_tot, by0 + bh_tot], fill="#334155", width=2)

    n = len(c["vals"])
    slot = bw_tot / n
    bar_w = int(slot * 0.62)
    for bi, val in enumerate(c["vals"]):
        bh = max(4, int((val / c["ymax"]) * (bh_tot - 26)))
        x0 = int(bx0 + bi * slot + (slot - bar_w) / 2)
        y0 = by0 + bh_tot - bh
        is_hi = bi in c["hi"]
        fill_col = c["color"] if is_hi else "#26334D"
        draw.rounded_rectangle([x0, y0, x0 + bar_w, by0 + bh_tot - 1], radius=5, fill=fill_col)
        # Value above highlighted bars
        if is_hi and (n <= 4 or bi in {0, 5}):
            vtxt = str(val)
            vw = draw.textlength(vtxt, font=f_mono_xs)
            draw.text((x0 + (bar_w - vw) / 2, y0 - 20), vtxt, font=f_mono_xs, fill=c["color"])
        elif is_hi and n == 8:
            vtxt = str(val)
            vw = draw.textlength(vtxt, font=f_mono_xs)
            draw.text((x0 + (bar_w - vw) / 2, y0 - 20), vtxt, font=f_mono_xs, fill=c["color"])
        # X tick label
        lbl = c["labels"][bi]
        lw = draw.textlength(lbl, font=f_mono_xs)
        draw.text((x0 + (bar_w - lw) / 2, by0 + bh_tot + 10), lbl, font=f_mono_xs, fill="#94A3B8" if is_hi else "#64748B")

# Section 2: Full-Scale Blockchain Post-Quantum Scorecard
draw.text((PAD, 742), "02 // WHERE FULL-SCALE CRYPTO & L1 CHAINS STAND TODAY", font=f_sec, fill="#64748B")

rows = [
    {
        "name": "Bitcoin  (secp256k1)",
        "desc": "Breakable by Shor once fault-tolerant (<500k qubits); BIP-360 quantum proposal is still a draft.",
        "badge": "BIP-360 IN DRAFT",
        "b_fg": "#FBBF24",
        "b_bg": "#2B2111",
        "b_bd": "#78350F",
        "hi": False,
    },
    {
        "name": "Ethereum  (secp256k1)",
        "desc": "Same elliptic-curve Shor exposure; upgrading live wallets, contracts & consensus takes years.",
        "badge": "MULTI-YEAR MIGRATION",
        "b_fg": "#FBBF24",
        "b_bg": "#2B2111",
        "b_bd": "#78350F",
        "hi": False,
    },
    {
        "name": "AES-256 & SHA-256",
        "desc": "Grover only gives a square-root speedup (~2^128 operations at scale). Hashes & symmetric keys hold.",
        "badge": "STAYS QUANTUM-SAFE",
        "b_fg": "#34D399",
        "b_bg": "#0B2922",
        "b_bd": "#065F46",
        "hi": False,
    },
    {
        "name": "Algorand  (Falcon-1024 + State Proofs)",
        "desc": "NIST post-quantum Falcon State Proofs + native Falcon-1024 mainnet accounts (v42) already live.",
        "badge": "PQ LIVE ON MAINNET",
        "b_fg": "#38BDF8",
        "b_bg": "#0C263B",
        "b_bd": "#0284C7",
        "hi": True,
    },
]

ry = 782
rh = 132
rgap = 18

for r in rows:
    bg = "#102038" if r["hi"] else "#0E1628"
    bd = "#0284C7" if r["hi"] else "#1E293B"
    draw.rounded_rectangle([PAD, ry, W - PAD, ry + rh], radius=18, fill=bg, outline=bd, width=2)
    if r["hi"]:
        draw.rounded_rectangle([PAD, ry, PAD + 8, ry + rh], radius=4, fill="#38BDF8")

    tx = PAD + (28 if r["hi"] else 24)
    draw.text((tx, ry + 24), r["name"], font=f_row_title, fill="#F8FAFC")
    draw.text((tx, ry + 70), r["desc"], font=f_row_desc, fill="#CBD5E1" if r["hi"] else "#94A3B8")

    # Right-aligned status badge on top line
    bw = draw.textlength(r["badge"], font=f_badge) + 32
    bx = W - PAD - 24 - bw
    by = ry + 22
    draw.rounded_rectangle([bx, by, bx + bw, by + 36], radius=18, fill=r["b_bg"], outline=r["b_bd"], width=2)
    draw.text((bx + 16, by + 8), r["badge"], font=f_badge, fill=r["b_fg"])

    ry += rh + rgap

# Footer
fy = 1418
draw.line([PAD, fy - 18, W - PAD, fy - 18], fill="#1E293B", width=2)
draw.text((PAD, fy), "@JS4vef", font=f_footer, fill="#F8FAFC")
r_foot = "Code & raw Braket counts: github.com/apeirontrade/shor-15-real-qpu"
rfw = draw.textlength(r_foot, font=f_footer)
draw.text((W - PAD - rfw, fy), r_foot, font=f_footer, fill="#64748B")

out = "results/quantum_crypto_card.png"
img.save(out, "PNG")
print("Saved", out)
