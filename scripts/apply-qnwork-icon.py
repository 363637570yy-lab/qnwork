# -*- coding: utf-8 -*-
"""Build QNwork app + tray icons from assets/qnwork-icon.png."""
from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "assets" / "qnwork-icon.png"
ICONS = ROOT / "src-tauri" / "icons"
PROD_SET = ICONS / "AppIcon.appiconset"
DEV_SET = ICONS / "dev" / "AppIcon.appiconset"

MAC_SLOTS = {
    "16-mac.png": 16,
    "32-mac.png": 32,
    "64-mac.png": 64,
    "128-mac.png": 128,
    "256-mac.png": 256,
    "512-mac.png": 512,
    "1024-mac.png": 1024,
}

TRAY_OUTS = {
    "tray-icon.png": (36, 0.14),
    "tray-icon@2x.png": (36, 0.14),
    "tray-icon-18.png": (18, 0.14),
    "tray-16.png": (16, 0.12),
    "tray-32.png": (32, 0.12),
    "tray-source.png": (128, 0.10),
}


def square_master(src: Path) -> Image.Image:
    im = Image.open(src).convert("RGBA")
    w, h = im.size
    side = max(w, h)
    canvas = Image.new("RGBA", (side, side), (0, 0, 0, 255))
    canvas.paste(im, ((side - w) // 2, (side - h) // 2), im)
    return canvas


def resize_square(im: Image.Image, side: int) -> Image.Image:
    return im.resize((side, side), Image.Resampling.LANCZOS)


def write_appiconset(master: Image.Image, dest: Path) -> None:
    dest.mkdir(parents=True, exist_ok=True)
    for name, side in MAC_SLOTS.items():
        resize_square(master, side).save(dest / name, "PNG")


def crop_mark(im: Image.Image, luma_max: int = 28) -> Image.Image:
    pix = im.load()
    w, h = im.size
    xs, ys = [], []
    for y in range(h):
        for x in range(w):
            r, g, b, a = pix[x, y]
            if a > 8 and (r > luma_max or g > luma_max or b > luma_max):
                xs.append(x)
                ys.append(y)
    if not xs:
        return im
    m = 8
    return im.crop(
        (max(0, min(xs) - m), max(0, min(ys) - m), min(w, max(xs) + 1 + m), min(h, max(ys) + 1 + m))
    )


def pack_tray(src: Image.Image, size: int, pad_ratio: float) -> Image.Image:
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    inner = max(1, int(round(size * (1.0 - 2 * pad_ratio))))
    cw, ch = src.size
    scale = min(inner / cw, inner / ch)
    nw = max(1, int(round(cw * scale)))
    nh = max(1, int(round(ch * scale)))
    resized = src.resize((nw, nh), Image.Resampling.LANCZOS)
    r, g, b, a = resized.split()
    # macOS menu-bar template: black glyph
    a = a.point(lambda v: min(255, int(v * 1.15)) if v > 12 else 0)
    black = Image.new("L", resized.size, 0)
    glyph = Image.merge("RGBA", (black, black, black, a))
    canvas.alpha_composite(glyph, ((size - nw) // 2, (size - nh) // 2))
    return canvas


def main() -> int:
    if not SRC.is_file():
        print(f"missing {SRC}", file=sys.stderr)
        return 1
    master = square_master(SRC)
    write_appiconset(master, PROD_SET)
    write_appiconset(master, DEV_SET)
    master.save(ROOT / "public" / "logo.png", "PNG")

    sys.path.insert(0, str(ROOT / "scripts"))
    from pack_appiconset import pack

    pack(PROD_SET, ICONS, ICONS / "icon.ico")
    pack(DEV_SET, ICONS / "dev", None)

    mark = crop_mark(master)
    for name, (sz, pad) in TRAY_OUTS.items():
        pack_tray(mark, sz, pad).save(ICONS / name, "PNG")

    from tray_win_badge import write_badges

    write_badges(ICONS / "tray-32.png", ICONS)
    print("OK QNwork icons packed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
