#!/usr/bin/env python3
"""Generate the TONFTP LLC site icons (assets/icon.png, assets/favicon.png).

Deterministic, dependency-light (Pillow only) replacement for a design-tool
export: a deep-navy→brand rounded square with a cyan "T" monogram and a
signal dot, matching the palette in style.css.

Usage:
    python3 tools/make-icons.py
"""

from pathlib import Path

from PIL import Image, ImageDraw

NAVY = (6, 24, 42)
NAVY_2 = (10, 36, 64)
BRAND = (4, 99, 154)
CYAN = (62, 198, 240)
ICE = (191, 233, 255)

SS = 4  # supersampling factor for antialiasing
ROOT = Path(__file__).resolve().parent.parent


def rounded_mask(size: int, radius_ratio: float = 0.22) -> Image.Image:
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        (0, 0, size - 1, size - 1), radius=int(size * radius_ratio), fill=255
    )
    return mask


def gradient(size: int) -> Image.Image:
    """Diagonal navy → brand gradient."""
    grad = Image.new("RGB", (size, size))
    px = grad.load()
    for y in range(size):
        for x in range(size):
            t = (x / (size - 1) * 0.45) + (y / (size - 1) * 0.55)
            a, b = NAVY_2, BRAND
            px[x, y] = (
                int(a[0] + (b[0] - a[0]) * t),
                int(a[1] + (b[1] - a[1]) * t),
                int(a[2] + (b[2] - a[2]) * t),
            )
    return grad


def draw_mark(img: Image.Image, size: int) -> None:
    """Draw the 'T' monogram + accent dot on top of the gradient."""
    d = ImageDraw.Draw(img)

    # 'T' geometry (relative to a 100-unit canvas)
    u = size / 100
    bar_h = 11 * u
    bar_w = 52 * u
    bar_x = (size - bar_w) / 2
    bar_y = 30 * u
    stem_w = 12 * u
    stem_x = (size - stem_w) / 2
    stem_y = bar_y + bar_h - 1 * u
    stem_h = 40 * u
    radius = 3.2 * u

    d.rounded_rectangle(
        (bar_x, bar_y, bar_x + bar_w, bar_y + bar_h), radius=radius, fill=ICE
    )
    d.rounded_rectangle(
        (stem_x, stem_y, stem_x + stem_w, stem_y + stem_h), radius=radius, fill=ICE
    )

    # cyan signal dot (bottom-right of the stem)
    dot_r = 7.5 * u
    cx, cy = size * 0.5 + stem_w / 2 + dot_r * 1.7, stem_y + stem_h - dot_r * 1.1
    d.ellipse((cx - dot_r, cy - dot_r, cx + dot_r, cy + dot_r), fill=CYAN)


def build(size: int) -> Image.Image:
    big = size * SS
    img = gradient(big)
    draw_mark(img, big)
    img = img.convert("RGBA")
    img.putalpha(rounded_mask(big))
    return img.resize((size, size), Image.LANCZOS)


def main() -> None:
    out = ROOT / "assets"
    out.mkdir(parents=True, exist_ok=True)
    for name, size in (("icon.png", 512), ("favicon.png", 64)):
        path = out / name
        build(size).save(path, "PNG", optimize=True)
        print(f"wrote {path.relative_to(ROOT)} ({size}x{size})")


if __name__ == "__main__":
    main()
