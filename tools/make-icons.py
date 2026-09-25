#!/usr/bin/env python3
"""Generate the TONFTP LLC site images.

Outputs (deterministic, Pillow only):
    assets/icon.png     512x512  brand mark (favicon/apple-touch/JSON-LD logo)
    assets/favicon.png   64x64   favicon
    assets/og.png      1200x630  Open Graph / Twitter card image

Palette matches the :root tokens in style.css.

Usage:
    python3 tools/make-icons.py
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

NAVY = (6, 24, 42)
NAVY_2 = (10, 36, 64)
BRAND = (4, 99, 154)
BRAND_LT = (10, 125, 191)
CYAN = (62, 198, 240)
ICE = (191, 233, 255)
MUTED = (143, 179, 201)

SS = 4  # supersampling factor for antialiasing
ROOT = Path(__file__).resolve().parent.parent

FONT_BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
FONT_REG = "/System/Library/Fonts/Supplemental/Arial.ttf"


def font(path: str, size: int):
    """Load a TrueType font, falling back to Pillow's bundled default."""
    try:
        return ImageFont.truetype(path, size)
    except OSError:  # non-macOS fallback
        return ImageFont.load_default(size)


# --------------------------------------------------------------------------
# brand mark
# --------------------------------------------------------------------------
def gradient(size: int) -> Image.Image:
    """Diagonal navy -> brand gradient."""
    grad = Image.new("RGB", (size, size))
    px = grad.load()
    for y in range(size):
        for x in range(size):
            t = (x / (size - 1) * 0.45) + (y / (size - 1) * 0.55)
            px[x, y] = tuple(
                int(NAVY_2[i] + (BRAND[i] - NAVY_2[i]) * t) for i in range(3)
            )
    return grad


def draw_mark(img: Image.Image, size: int) -> None:
    """Draw the 'T' monogram + accent dot on a `size` canvas."""
    d = ImageDraw.Draw(img)
    u = size / 100  # 100-unit design canvas

    bar_h, bar_w = 11 * u, 52 * u
    bar_x, bar_y = (size - bar_w) / 2, 30 * u
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

    dot_r = 7.5 * u
    cx = size * 0.5 + stem_w / 2 + dot_r * 1.7
    cy = stem_y + stem_h - dot_r * 1.1
    d.ellipse((cx - dot_r, cy - dot_r, cx + dot_r, cy + dot_r), fill=CYAN)


def mark(px: int, radius_ratio: float = 0.22) -> Image.Image:
    """Rounded brand mark at `px` pixels."""
    big = px * SS
    img = gradient(big).convert("RGBA")
    draw_mark(img, big)

    mask = Image.new("L", (big, big), 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        (0, 0, big - 1, big - 1), radius=int(big * radius_ratio), fill=255
    )
    img.putalpha(mask)
    return img.resize((px, px), Image.LANCZOS)


# --------------------------------------------------------------------------
# Open Graph card (1200x630)
# --------------------------------------------------------------------------
def vgradient(w: int, h: int, top: tuple, bottom: tuple) -> Image.Image:
    grad = Image.new("RGB", (1, h))
    px = grad.load()
    for y in range(h):
        t = y / (h - 1)
        px[0, y] = tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3))
    return grad.resize((w, h), Image.BILINEAR)


def glow(size: tuple, center: tuple, radius: int, color: tuple, alpha: int) -> Image.Image:
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    ImageDraw.Draw(layer).ellipse(
        (center[0] - radius, center[1] - radius, center[0] + radius, center[1] + radius),
        fill=color + (alpha,),
    )
    return layer.filter(ImageFilter.GaussianBlur(90))


def build_og() -> Image.Image:
    W, H = 1200, 630
    img = vgradient(W, H, NAVY_2, NAVY).convert("RGBA")

    for center, radius, color, alpha in (
        ((1050, 60), 320, BRAND, 120),
        ((120, 600), 300, CYAN, 40),
        ((640, 700), 340, BRAND_LT, 60),
    ):
        img = Image.alpha_composite(img, glow((W, H), center, radius, color, alpha))

    # blueprint grid, faded toward the edges
    grid = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(grid)
    for x in range(0, W, 56):
        gd.line((x, 0, x, H), fill=ICE + (14,), width=1)
    for y in range(0, H, 56):
        gd.line((0, y, W, y), fill=ICE + (14,), width=1)
    img = Image.alpha_composite(img, grid)

    # brand mark + wordmark
    icon_px = 148
    img.alpha_composite(mark(icon_px), (84, 96))

    d = ImageDraw.Draw(img)
    x_text = 84 + icon_px + 40
    f_word = font(FONT_BOLD, 78)
    f_tag = font(FONT_REG, 34)
    f_dom = font(FONT_REG, 24)

    d.text((x_text, 110), "TON", font=f_word, fill=ICE)
    ton_w = d.textlength("TON", font=f_word)
    d.text((x_text + ton_w, 110), "FTP", font=f_word, fill=CYAN)

    d.text((x_text + 4, 206), "LLC", font=font(FONT_BOLD, 30), fill=MUTED)
    d.text(
        (x_text + 4, 246),
        "Software development for web & native",
        font=f_tag,
        fill=MUTED,
    )

    # accent rule + ownership line
    d.rounded_rectangle((86, 448, 226, 452), radius=2, fill=CYAN)
    d.text(
        (86, 486),
        "tonftp.com — owned and operated by TONFTP LLC",
        font=f_dom,
        fill=ICE,
    )
    d.text((86, 520), "hello@tonftp.com", font=f_dom, fill=CYAN)

    return img.convert("RGB")


# --------------------------------------------------------------------------
def main() -> None:
    out = ROOT / "assets"
    out.mkdir(parents=True, exist_ok=True)

    for name, size in (("icon.png", 512), ("favicon.png", 64)):
        path = out / name
        mark(size).save(path, "PNG", optimize=True)
        print(f"wrote {path.relative_to(ROOT)} ({size}x{size})")

    og_path = out / "og.png"
    build_og().save(og_path, "PNG", optimize=True)
    print(f"wrote {og_path.relative_to(ROOT)} (1200x630)")


if __name__ == "__main__":
    main()
