#!/usr/bin/env python3
"""Generate the in-app wordmark (flutter/assets/logo_dark.png / logo_light.png, shown max 300x60).
Rendered with IBM Plex Mono Bold (SIL OFL) into a PNG; the font itself is not bundled."""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(__file__).resolve().parents[2]
FONT = sys.argv[1] if len(sys.argv) > 1 else "/usr/share/fonts/truetype/sand-box/google/IBM Plex Mono/IBMPlexMono-Bold.ttf"
W, H = 600, 120


def make(color, glow_alpha, out):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    icon = Image.open(ROOT / "flutter/assets/icon.png").convert("RGBA").resize((96, 96), Image.LANCZOS)
    img.paste(icon, (6, 12), icon)
    font = ImageFont.truetype(FONT, 46)
    text = "MatrixConnections"
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    # shrink to fit
    size = 46
    while d.textlength(text, font=font) > W - 124 and size > 20:
        size -= 1
        font = ImageFont.truetype(FONT, size)
    bbox = d.textbbox((0, 0), text, font=font)
    y = (H - (bbox[3] - bbox[1])) // 2 - bbox[1]
    d.text((116, y), text, font=font, fill=color + (255,))
    if glow_alpha:
        g = layer.filter(ImageFilter.GaussianBlur(7))
        g.putalpha(g.getchannel("A").point(lambda v: int(v * glow_alpha)))
        img = Image.alpha_composite(img, g)
    img = Image.alpha_composite(img, layer)
    img.save(out)


make((0, 255, 65), 0.9, ROOT / "flutter/assets/logo_dark.png")
make((0, 120, 30), 0.0, ROOT / "flutter/assets/logo_light.png")
