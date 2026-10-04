#!/usr/bin/env python3
"""Generate the MatrixConnections icon set (original artwork, procedurally drawn).

Black rounded tile, procedural green "digital rain" (random 3x5 pixel glyphs, no font
or film imagery), and a glowing "M" drawn as a network path with connection nodes.
Small sizes (<=32 px) use a simplified, rain-free variant so they stay legible.

Usage: python3 res/matrix/gen_icons.py   (from the repo root; needs Pillow)
"""
import random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageChops

ROOT = Path(__file__).resolve().parents[2]
GREEN = (0, 255, 65)
S = 1024
SEED = 1999

M_PTS = [(0.24, 0.74), (0.24, 0.28), (0.50, 0.57), (0.76, 0.28), (0.76, 0.74)]


def rain_cells(seed=SEED):
    """Yield (x, y, w, h, alpha, is_head) rectangles in 0..1 units."""
    rnd = random.Random(seed)
    cols, cell_w, cell_h = 16, 1 / 16, 1 / 13
    px_w, px_h = cell_w / 4.2, cell_h / 6.6
    out = []
    for c in range(cols):
        head = rnd.randint(3, 15)
        trail = rnd.randint(5, 11)
        for r in range(head - trail, head + 1):
            if r < 0 or r > 12:
                continue
            t = (r - (head - trail)) / trail  # 0 tail .. 1 head
            alpha = 0.10 + 0.75 * t ** 1.6
            is_head = r == head
            x0 = c * cell_w + cell_w * 0.18
            y0 = r * cell_h + cell_h * 0.12
            for gy in range(5):
                for gx in range(3):
                    if rnd.random() < 0.55 or (is_head and rnd.random() < 0.8):
                        out.append((x0 + gx * px_w * 1.12, y0 + gy * px_h * 1.12,
                                    px_w, px_h, alpha, is_head))
    return out


def tile_mask(size, radius_frac=0.19):
    m = Image.new("L", (size, size), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, size - 1, size - 1),
                                        radius=int(size * radius_frac), fill=255)
    return m


def background(size):
    bg = Image.new("RGBA", (size, size))
    d = ImageDraw.Draw(bg)
    for y in range(size):
        t = y / (size - 1)
        d.line([(0, y), (size, y)], fill=(0, int(18 * (1 - t)) + 2, int(8 * (1 - t)) + 1, 255))
    return bg


def draw_m(size, width_frac, node_r_frac, nodes=True):
    layer = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    pts = [(x * size, y * size) for x, y in M_PTS]
    w = int(size * width_frac)
    d.line(pts, fill=GREEN + (255,), width=w, joint="curve")
    for p in (pts[0], pts[-1]):  # round caps
        d.ellipse((p[0] - w / 2, p[1] - w / 2, p[0] + w / 2, p[1] + w / 2), fill=GREEN + (255,))
    if nodes:
        r, ri = size * node_r_frac, size * node_r_frac * 0.48
        for p in pts:
            d.ellipse((p[0] - r, p[1] - r, p[0] + r, p[1] + r), fill=GREEN + (255,))
            d.ellipse((p[0] - ri, p[1] - ri, p[0] + ri, p[1] + ri), fill=(0, 26, 8, 255))
    return layer


def glow(layer, radius, strength):
    g = layer.filter(ImageFilter.GaussianBlur(radius))
    a = g.getchannel("A").point(lambda v: min(255, int(v * strength)))
    g.putalpha(a)
    return g


def render_full(size=S):
    img = background(size)
    rain = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(rain)
    for x, y, w, h, a, head in rain_cells():
        col = (190, 255, 205) if head else GREEN
        d.rectangle((x * size, y * size, (x + w) * size, (y + h) * size),
                    fill=col + (int(255 * a * 0.62),))
    # darken rain behind the M so the mark reads clearly
    vign = Image.new("L", (size, size), 0)
    ImageDraw.Draw(vign).ellipse((size * 0.12, size * 0.14, size * 0.88, size * 0.88), fill=185)
    vign = vign.filter(ImageFilter.GaussianBlur(size * 0.08))
    ra = ImageChops.subtract(rain.getchannel("A"), vign)
    rain.putalpha(ra)
    img = Image.alpha_composite(img, rain)
    m = draw_m(size, 0.085, 0.058)
    img = Image.alpha_composite(img, glow(m, size * 0.06, 1.1))
    img = Image.alpha_composite(img, glow(m, size * 0.022, 1.6))
    img = Image.alpha_composite(img, m)
    out = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    out.paste(img, (0, 0), tile_mask(size))
    # thin green rim
    rim = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    ImageDraw.Draw(rim).rounded_rectangle((size * 0.006, size * 0.006, size * 0.994, size * 0.994),
                                          radius=int(size * 0.185), outline=GREEN + (90,),
                                          width=max(1, int(size * 0.008)))
    return Image.alpha_composite(out, rim)


def render_small(px):
    size = px * 16
    img = Image.new("RGBA", (size, size), (0, 8, 3, 255))
    m = draw_m(size, 0.15 if px <= 16 else 0.13, 0.0, nodes=False)
    img = Image.alpha_composite(img, glow(m, size * 0.03, 1.3))
    img = Image.alpha_composite(img, m)
    out = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    out.paste(img, (0, 0), tile_mask(size, 0.16))
    return out.resize((px, px), Image.LANCZOS)


def sized(full, px):
    return render_small(px) if px <= 32 else full.resize((px, px), Image.LANCZOS)


def save_ico(full, path, sizes):
    imgs = [sized(full, s) for s in sizes]
    big = imgs[-1]
    big.save(path, format="ICO", sizes=[(s, s) for s in sizes], append_images=imgs[:-1])


def svg(path):
    """Vector version (no blur filter dependency; glow is optional for renderers that support it)."""
    def u(v):
        return f"{v * 1024:.1f}"
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 1024">',
             '<defs><linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">'
             '<stop offset="0" stop-color="#031408"/><stop offset="1" stop-color="#000000"/>'
             '</linearGradient></defs>',
             '<rect width="1024" height="1024" rx="195" fill="url(#bg)"/>']
    for x, y, w, h, a, head in rain_cells():
        cx, cy = x + w / 2 - 0.5, y + h / 2 - 0.51
        if (cx / 0.38) ** 2 + (cy / 0.37) ** 2 < 1:
            a *= 0.25
        col = "#BEFFCD" if head else "#00FF41"
        parts.append(f'<rect x="{u(x)}" y="{u(y)}" width="{u(w)}" height="{u(h)}" '
                     f'fill="{col}" fill-opacity="{a * 0.62:.2f}"/>')
    pts = " ".join(f"{u(x)},{u(y)}" for x, y in M_PTS)
    parts.append(f'<polyline points="{pts}" fill="none" stroke="#00FF41" stroke-opacity="0.25" '
                 f'stroke-width="150" stroke-linejoin="round" stroke-linecap="round"/>')
    parts.append(f'<polyline points="{pts}" fill="none" stroke="#00FF41" stroke-width="87" '
                 f'stroke-linejoin="round" stroke-linecap="round"/>')
    for x, y in M_PTS:
        parts.append(f'<circle cx="{u(x)}" cy="{u(y)}" r="59" fill="#00FF41"/>')
        parts.append(f'<circle cx="{u(x)}" cy="{u(y)}" r="28.5" fill="#001A08"/>')
    parts.append('<rect x="6" y="6" width="1012" height="1012" rx="190" fill="none" '
                 'stroke="#00FF41" stroke-opacity="0.35" stroke-width="8"/>')
    parts.append("</svg>")
    Path(path).write_text("\n".join(parts) + "\n")


def main():
    full = render_full()
    ico_sizes = [16, 24, 32, 48, 64, 128, 256]
    full.save(ROOT / "res/icon.png")                               # 1024 master
    full.resize((512, 512), Image.LANCZOS).save(ROOT / "res/matrix/icon-512.png")
    full.save(ROOT / "res/mac-icon.png")
    sized(full, 32).save(ROOT / "res/32x32.png")
    sized(full, 64).save(ROOT / "res/64x64.png")
    sized(full, 128).save(ROOT / "res/128x128.png")
    sized(full, 256).save(ROOT / "res/128x128@2x.png")
    save_ico(full, ROOT / "res/icon.ico", ico_sizes)
    save_ico(full, ROOT / "flutter/windows/runner/resources/app_icon.ico", ico_sizes)
    save_ico(full, ROOT / "res/tray-icon.ico", [16, 24, 32, 48, 64])
    # In-app icon (loadIcon prefers assets/icon.png, falls back to icon.svg); also used for the tray.
    sized(full, 256).save(ROOT / "flutter/assets/icon.png")
    svg(ROOT / "flutter/assets/icon.svg")
    svg(ROOT / "res/scalable.svg")


if __name__ == "__main__":
    main()
