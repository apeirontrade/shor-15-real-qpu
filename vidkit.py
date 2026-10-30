"""Shared look and render loop for the videos: 1080x1080, 30 fps, H.264 + silent AAC, frames piped to ffmpeg."""
import math
import random
import subprocess

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
RED = (248, 113, 113)
WHITE = (241, 245, 249)
DIM = (148, 163, 184)
NOISE = (100, 116, 139)

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


def check(d, cx, cy, s, color, a):
    """Hand-drawn tick (Avenir has no ✓ glyph)."""
    d.line([(cx - s, cy), (cx - s * 0.25, cy + s * 0.8), (cx + s * 1.2, cy - s)], fill=color + (int(255 * a),),
           width=max(4, int(s / 3)))


def cross(d, cx, cy, s, color, a):
    for dx in (-s, s):
        d.line([(cx - dx, cy - s), (cx + dx, cy + s)], fill=color + (int(255 * a),), width=max(4, int(s / 3)))


def bars(d, values, colors, labels, a, g, base=800, top=260, bw=88, gap=26, label_path=MONO):
    """Animated bar chart; g is the 0..1 grow factor."""
    mx = max(values)
    n = len(values)
    left = (W - (n * bw + (n - 1) * gap)) // 2
    for i, (v, col, lab) in enumerate(zip(values, colors, labels)):
        x = left + i * (bw + gap)
        h = (base - top) * v / mx * g
        d.rounded_rectangle([x, base - max(h, 2), x + bw, base], 10, fill=col + (int(255 * a),))
        d.text((x + bw / 2, base - h - 26), str(round(v * g)), font=font(30, DEMI),
               fill=WHITE + (int(255 * a * min(1, g * 3)),), anchor="mm")
        d.text((x + bw / 2, base + 34), lab, font=font(28, 0, label_path), fill=DIM + (int(255 * a),), anchor="mm")


BG = Image.new("RGB", (W, H))
_bgd = ImageDraw.Draw(BG)
for _y in range(H):
    _k = _y / H
    _bgd.line([(0, _y), (W, _y)], fill=(int(8 + 22 * _k), int(12 + 4 * _k), int(38 + 30 * _k)))
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


def render(scenes, out):
    """scenes: list of (draw_fn(d, t, a), seconds). Each scene fades in and out."""
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                           "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                           "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo",
                           "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p",
                           "-c:a", "aac", "-shortest", "-movflags", "+faststart", out], stdin=subprocess.PIPE)
    start = 0.0
    for fn, dur in scenes:
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
    return start
