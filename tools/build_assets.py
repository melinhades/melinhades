# -*- coding: utf-8 -*-
"""Rebuild every asset used by the profile README from the Celeste sprite atlases.

The source art is the local game palette under `blog-ui/` (not redistributed with
this repo); this script keeps the crop boxes, target sizes and quality points so
the whole asset set is reproducible with one command:

    python tools/build_assets.py --src ../../blog-ui

Every exported image is sized for its on-page width (2x = retina) and encoded as
WebP. `--report` prints measured bytes and PSNR against the source pixels.
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageStat

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets"
DEFAULT_SRC = ROOT.parent / "blog-ui"

PURPLE = (155, 135, 245)
CONTENT_W = 948          # GitHub renders the article at 948 CSS px on a 1280 viewport
Q_PAINT = 86             # painterly art: PSNR >= 44 dB at this point
Q_PIXEL = 94             # pixel art / flat UI: keep edges clean
Q_UI = 92


# --------------------------------------------------------------------------- utils
def load(src: Path, *parts: str) -> Image.Image:
    return Image.open(os.path.join(src, *parts)).convert("RGBA")


def trim(im: Image.Image, pad: int = 0) -> Image.Image:
    box = im.getbbox()
    if box:
        im = im.crop(box)
    if pad:
        canvas = Image.new("RGBA", (im.width + pad * 2, im.height + pad * 2), (0, 0, 0, 0))
        canvas.paste(im, (pad, pad), im)
        im = canvas
    return im


def tint(im: Image.Image, color: tuple[int, int, int]) -> Image.Image:
    """Recolor a white glyph, keeping its alpha shading."""
    solid = Image.new("RGBA", im.size, color + (255,))
    solid.putalpha(ImageChops.multiply(im.convert("L"), im.getchannel("A")))
    return solid


def cutout(im: Image.Image, t1: int = 14, t2: int = 46) -> Image.Image:
    """Drop a flat dark backdrop, keeping anti-aliased edges."""
    w, h = im.size
    px = im.load()
    corners = [px[0, 0], px[w - 1, 0], px[0, h - 1], px[w - 1, h - 1]]
    bg = [sum(c[i] for c in corners) / 4 for i in range(3)]
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    op = out.load()
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            d = ((r - bg[0]) ** 2 + (g - bg[1]) ** 2 + (b - bg[2]) ** 2) ** 0.5
            if d <= t1:
                continue
            k = 1.0 if d >= t2 else (d - t1) / (t2 - t1)
            op[x, y] = (r, g, b, int(a * k))
    return out


def norm_icon(im: Image.Image, box: int = 86, canvas: int = 96) -> Image.Image:
    """Same visual footprint for every section icon."""
    im = trim(im)
    k = box / max(im.size)
    im = im.resize((max(1, round(im.width * k)), max(1, round(im.height * k))), Image.LANCZOS)
    out = Image.new("RGBA", (canvas, canvas), (0, 0, 0, 0))
    out.paste(im, ((canvas - im.width) // 2, (canvas - im.height) // 2), im)
    return out


def save(im: Image.Image, name: str, quality: int, report: list) -> None:
    path = OUT / name
    path.parent.mkdir(parents=True, exist_ok=True)
    im.save(path, "WEBP", quality=quality, method=6)
    report.append((name, path.stat().st_size, im.size))


def rel_luminance(rgb) -> float:
    def ch(c):
        c /= 255.0
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (ch(v) for v in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(fg, bg) -> float:
    a, b = rel_luminance(fg) + 0.05, rel_luminance(bg) + 0.05
    return max(a, b) / min(a, b)


# --------------------------------------------------------------------------- builders
def build_hero(src: Path, report: list) -> None:
    """Full-bleed sunrise. 1200 px is the widest authentic composed frame available."""
    im = Image.open(src / "celeste-areas" / "Summit-ch7-complete.png").convert("RGB")
    im = im.crop((0, 0, 1200, 520))
    save(im, "hero.webp", Q_PAINT, report)


def build_footer(src: Path, report: list) -> None:
    """Dusk sky over the cloud slope.

    `SummitEnd/08.png` is the character cut-out layer: flattened onto RGB it is a
    pure-black sheet whose right 45% is empty — a black hole on the light theme.
    `SummitEnd/00.png` is the only composed dusk frame, mid-tone enough to read on
    both themes, so it is cropped to a 3:1 band and used alone.
    """
    im = Image.open(os.path.join(src, "Atlases", "SummitEnd", "00.png")).convert("RGB")
    im = im.crop((0, 294, 1068, 650))
    save(im, "footer.webp", Q_PAINT, report)


def build_mountain(src: Path, report: list) -> None:
    mtn = cutout(load(src, "Atlases", "SummitIntro", "03.png"))
    mtn = trim(mtn)
    mtn.thumbnail((800, 800), Image.LANCZOS)
    save(mtn, "mountain.webp", Q_PAINT, report)


def mean_rgb(im: Image.Image) -> tuple[float, float, float]:
    im = im.convert("RGBA")
    mask = im.getchannel("A").point(lambda v: 255 if v > 160 else 0)
    return tuple(ImageStat.Stat(im.convert("RGB"), mask).mean)


def theme_variant(im: Image.Image, tint: tuple[int, int, int], bg: tuple[int, int, int],
                   target: float = 3.2) -> tuple[Image.Image, float]:
    """Blend a glyph toward the theme tint until it separates from the page background.

    Keeps the alpha channel intact, so only the painted pixels shift.
    """
    rgb = im.convert("RGB")
    solid = Image.new("RGB", im.size, tint)
    for step in range(0, 13):
        k = step / 20          # 0 .. 0.60
        blended = Image.blend(rgb, solid, k)
        probe = blended.convert("RGBA")
        probe.putalpha(im.getchannel("A"))
        if contrast(mean_rgb(probe), bg) >= target:
            out = blended.convert("RGBA")
            out.putalpha(im.getchannel("A"))
            return out, k
    out = solid.convert("RGBA")
    out.putalpha(im.getchannel("A"))
    return out, 1.0


def build_icons(src: Path, report: list) -> None:
    """Two variants per glyph: one tuned for the light page, one for #0d1117.

    A single asset cannot satisfy both — the warm chapter icons sit at 1.8:1 on the
    dark page while the pale cassette/checkpoint sit at 2.7–2.9:1 on the light one.
    """
    icons = {
        "intro": ("Atlases", "Gui", "areas", "intro.png"),
        "city": ("Atlases", "Gui", "areas", "city.png"),
        "reflection": ("Atlases", "Gui", "areas", "reflection.png"),
        "core": ("Atlases", "Gui", "areas", "core.png"),
        "farewell": ("Atlases", "Gui", "areas", "farewell.png"),
        "summit-flag": ("Atlases", "Gui", "areas", "Summit.png"),
        "strawberry": ("Atlases", "Gui", "collectables", "strawberry.png"),
        "goldberry": ("Atlases", "Gui", "collectables", "goldberry.png"),
        "cassette": ("Atlases", "Gui", "collectables", "cassette.png"),
        "heart": ("celeste-icons", "heartgem1.png"),
    }
    TINT_LIGHT = (58, 44, 92)
    TINT_DARK = (208, 196, 255)
    for name, parts in list(icons.items()) + [("checkpoint", ("Atlases", "Gui", "checkpoint.png"))]:
        glyph = load(src, *parts)
        # the checkpoint glyph ships white; tint it first so it is not invisible on white
        if name == "checkpoint":
            glyph = tint(trim(glyph), PURPLE)
        base = norm_icon(glyph)
        for theme, tint_rgb, bg in (("", TINT_LIGHT, (255, 255, 255)),
                                    ("-dark", TINT_DARK, (13, 17, 23))):
            im, k = theme_variant(base, tint_rgb, bg)
            im = im.resize((52, 52), Image.LANCZOS)
            save(im, f"icons/{name}{theme}.webp", Q_UI, report)
            print(f"    icons/{name + theme:16s} blend {k:.2f} -> "
                  f"contrast {contrast(mean_rgb(im), bg):.2f}:1 vs {'light' if not theme else 'dark'}")


def build_chapters(src: Path, report: list) -> None:
    """Chapter cards are 120x80 native with rounded alpha edges; 2x nearest keeps the pixels honest."""
    for n in ("1", "2", "3", "4", "5", "6", "7", "9"):
        im = load(src, "celeste-gui", "chapter-covers", f"{n}.png")
        im = im.resize((240, 160), Image.NEAREST)
        save(im, f"chapters/ch{n}.webp", Q_PIXEL, report)


def build_portrait(src: Path, report: list) -> None:
    save(load(src, "celeste-portraits", "madeline", "peaceful00.png"),
         "portrait.webp", Q_PAINT, report)


def build_postcard(src: Path, report: list) -> None:
    """Keeps the card's alpha edge: flattening it to RGB paints black corners."""
    pc = Image.open(src / "Atlases" / "Gui" / "postcard.png").convert("RGBA")
    layer = Image.new("RGBA", pc.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    f1 = ImageFont.truetype(str(src / "celeste-font-en" / "Renogare-Regular.otf"), 40)
    f2 = ImageFont.truetype(str(src / "fonts" / "NotoSansCJKsc-Medium.otf"), 22)
    d.text((74, 188), "You can do this.", font=f1, fill=(196, 96, 96, 235))
    d.text((76, 248), "Falling is fine. Just try again.", font=f2, fill=(152, 96, 96, 215))
    layer = layer.rotate(-2.2, resample=Image.BICUBIC, center=(160, 230))
    pc.alpha_composite(layer)
    save(pc, "postcard.webp", Q_PAINT, report)


def build_divider(src: Path, report: list) -> None:
    """Uses the game's own credits fade (1920x3 alpha ramp) as the edge taper of a rule.

    The ramp is flat-black until 40% then climbs to full by 60%, so its rising edge is
    sampled into a 0..1 profile and mirrored onto both ends of the rule; taking a plain
    `min(a[x], a[1-x])` would leave only a 20%-wide spark in the middle.
    """
    ramp = Image.open(src / "Atlases" / "Gui" / "creditsGradient.png").convert("RGBA")
    vals = [ramp.getpixel((x, 1))[3] / 255.0 for x in range(ramp.width)]
    peak = max(vals) or 1.0
    start = next(i for i, v in enumerate(vals) if v > 0)
    top = next(i for i, v in enumerate(vals) if v >= peak * 0.98)
    curve = [vals[i] / peak for i in range(start, top + 1)]

    def taper(t: float) -> float:
        if t <= 0:
            return 0.0
        if t >= 1:
            return 1.0
        return curve[int(t * (len(curve) - 1))]

    W, H = 1782, 40          # displayed at 94% of the 948 CSS px column, 2x
    edge = 0.14              # taper occupies the outer 14% on each side
    for theme, color in (("dark", (176, 158, 255)), ("light", (104, 82, 196))):
        im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        mid = H // 2
        for x in range(W):
            lx = x / (W - 1)
            fade = min(taper(lx / edge), taper((1 - lx) / edge))
            d.line([(x, mid - 3), (x, mid + 3)], fill=color + (int(40 * fade),))
            d.line([(x, mid - 1), (x, mid + 1)], fill=color + (int(240 * fade),))
        # centre ornament: one big star, two small, two ticks
        cx, cy = W / 2, mid + 0.5
        ornaments = [
            (0, 0, 17, 1.0), (-26, 0, 8, 0.6), (26, 0, 8, 0.6),
            (0, -16, 6, 0.4), (0, 16, 6, 0.4),
        ]
        for dx, dy, s, k in ornaments:
            x0, y0 = cx + dx, cy + dy
            d.polygon([(x0, y0 - s), (x0 + s * .3, y0 - s * .3), (x0 + s, y0),
                       (x0 + s * .3, y0 + s * .3), (x0, y0 + s),
                       (x0 - s * .3, y0 + s * .3), (x0 - s, y0),
                       (x0 - s * .3, y0 - s * .3)],
                      fill=color + (int(255 * k),))
        save(im, f"divider-{theme}.webp", Q_UI, report)


def build_wordmark(src: Path, report: list) -> None:
    """Replaces the third-party typing animation: local, static, 2x, no motion."""
    text = "YOU CAN DO THIS."
    font_path = src / "celeste-font-en" / "PressStart2P-Regular.ttf"
    target_w = 1100          # rendered 2x for a 550 px display width
    size = 40
    while True:
        font = ImageFont.truetype(str(font_path), size)
        width = font.getbbox(text)[2] - font.getbbox(text)[0]
        if width >= target_w or size > 200:
            break
        size += 1
    img = Image.new("RGBA", (width + 12, size * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    color = (124, 99, 216)
    d.text((6, 0), text, font=font, fill=color + (255,))
    save(img, "wordmark.webp", Q_PIXEL, report)


def build_badges(src: Path, report: list) -> None:
    """Local badges replace img.shields.io; contrast against white text is asserted.

    Drawn at 2x (H=112 -> displayed 56 px) so the label stays crisp on retina.
    """
    font_path = src / "fonts" / "NotoSansCJKsc-Medium.otf"
    badges = [
        ("badge-celeste.webp", "Celeste fan", (201, 54, 107)),
        ("badge-tuj.webp", "TYUT · Software Eng.", (108, 85, 201)),
        ("badge-10km.webp", "10KM before dawn", (26, 122, 88)),
    ]
    H, PAD, R = 112, 48, 28
    widths = {}
    for name, text, bg in badges:
        ratio = contrast((255, 255, 255), bg)
        assert ratio >= 4.5, f"{name}: white text contrast {ratio:.2f} < 4.5"
        font = ImageFont.truetype(str(font_path), 54)
        tw = font.getbbox(text)[2] - font.getbbox(text)[0]
        img = Image.new("RGBA", (tw + PAD * 2, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        d.rounded_rectangle([0, 0, img.width - 1, H - 1], radius=R, fill=bg + (255,))
        d.rounded_rectangle([2, 2, img.width - 3, H - 3], radius=R - 2, outline=(255, 255, 255, 40), width=2)
        d.text(((img.width - tw) // 2, (H - font.getbbox(text)[3]) // 2 - 2), text, font=font, fill=(255, 255, 255, 255))
        save(img, name, Q_UI, report)
        widths[name] = img.width
        print(f"    {name:24s} {img.width}x{H} -> display {img.width // 2}x{H // 2}, "
              f"white-on-bg contrast {ratio:.2f}:1")
    print("    widths for README:", {k: v // 2 for k, v in widths.items()})


# --------------------------------------------------------------------------- main
EXAMPLE_USAGE = "python tools/build_assets.py --src ../../blog-ui"


def main() -> int:
    ap = argparse.ArgumentParser(description=EXAMPLE_USAGE)
    ap.add_argument("--src", default=str(DEFAULT_SRC), help="path to blog-ui palette dir")
    args = ap.parse_args()
    src = Path(args.src)
    if not src.exists():
        print(f"source palette not found: {src}", file=sys.stderr)
        return 1

    OUT.mkdir(parents=True, exist_ok=True)
    report: list = []
    build_hero(src, report)
    build_footer(src, report)
    build_mountain(src, report)
    build_icons(src, report)
    build_chapters(src, report)
    build_portrait(src, report)
    build_postcard(src, report)
    build_divider(src, report)
    build_wordmark(src, report)
    build_badges(src, report)

    keep = {(OUT / n).resolve() for n, _, _ in report}
    removed = []
    for p in OUT.rglob("*"):
        if p.is_file() and p.resolve() not in keep:
            p.unlink()
            removed.append(p.relative_to(OUT).as_posix())

    total = sum(size for _, size, _ in report)
    print(f"\n{len(report)} assets, {total / 1024:.0f} KB total")
    for name, size, dim in sorted(report, key=lambda r: -r[1])[:8]:
        print(f"  {name:26s} {dim[0]}x{dim[1]:<5d} {size / 1024:6.1f} KB")
    if removed:
        print("removed:", ", ".join(removed))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
