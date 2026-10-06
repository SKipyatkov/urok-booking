#!/usr/bin/env python3
"""Compress logo PNGs and generate WebP variants."""

from pathlib import Path

from PIL import Image

IMG_DIR = Path(__file__).resolve().parent.parent / "backend" / "static" / "img"

FILES = ("urok-logo-horizontal.png", "urok-logo-icon.png")


def optimize() -> None:
    IMG_DIR.mkdir(parents=True, exist_ok=True)
    stacked = IMG_DIR / "urok-logo-stacked.png"
    if stacked.exists():
        stacked.unlink()
        print("Removed unused urok-logo-stacked.png")

    for name in FILES:
        path = IMG_DIR / name
        if not path.exists():
            print(f"Skip missing {name}")
            continue
        img = Image.open(path)
        if img.mode not in ("RGB", "RGBA"):
            img = img.convert("RGBA")
        img.save(path, optimize=True, compress_level=9)
        webp_path = path.with_suffix(".webp")
        img.save(webp_path, "WEBP", quality=82, method=6)
        print(f"{name}: {path.stat().st_size // 1024} KB, webp: {webp_path.stat().st_size // 1024} KB")


if __name__ == "__main__":
    optimize()
