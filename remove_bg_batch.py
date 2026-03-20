#!/usr/bin/env python3
"""
Remove backgrounds from 7 machine images using rembg.
The 580N is already done, so it's skipped.
"""
import argparse
import sys
from pathlib import Path
from PIL import Image

BASE_DIR = Path(__file__).parent
SCRAPE_ROOT = BASE_DIR / "Scrape Case/pt-br/southamerica/produtos"
PUBLIC_ROOT = BASE_DIR / "public/case-assets"

# (category, model_slug, source_filename, output_filename)
JOBS = [
    ("escavadeiras-hidraulicas", "cx220c-s2",   "55007306_1457a6f0ed344b968436ff9642c8781e.jpg", "cx220c-nobg.png"),
    ("pas-carregadeiras",        "w20g",          "bd1a0e38_22d95d6ab90e48f1a2c7b8f07b664ac6.jpg", "w20g-nobg.png"),
    ("minicarregadeiras",        "sv300b",        "de414ccc_1cbc519789a14f52b0dd9602dd957d1d.jpg", "sv300b-nobg.png"),
    ("motoniveladoras",          "865b-series-2", "be91b4b3_b2a6b71b0d114374bde1ac8c059fa181.jpg", "865b-nobg.png"),
    ("miniescavadeiras",         "cx22d",         "71a1ea6b_888eeec9a00a43f2876c9761741b0411.png", "cx22d-nobg.png"),
    ("rolo-compactador",         "1107ex",        "97bc363e_286e42a28ca24ba8ba0413807e27e873.jpg", "1107ex-nobg.png"),
    ("tratores-de-esteiras",     "1150l",         "d14deaaf_d840552e56254fd694819a121da920ea.png", "1150l-nobg.png"),
]

MAX_SIZE = 1200  # resize to max this dimension before rembg (saves memory)


def remove_background(img: Image.Image) -> Image.Image:
    from rembg import remove

    return remove(img)

def destination_is_stale(src: Path, dst: Path) -> bool:
    return not dst.exists() or src.stat().st_mtime_ns > dst.stat().st_mtime_ns


def process(cat, model, src_file, dst_file, *, force: bool):
    src = SCRAPE_ROOT / cat / "models" / model / "assets" / src_file
    dst_dir = PUBLIC_ROOT / cat / model
    dst = dst_dir / dst_file

    if not src.exists():
        print(f"  [MISS] Source not found: {src}", file=sys.stderr)
        return False

    if dst.exists() and not force and not destination_is_stale(src, dst):
        print(f"  [SKIP] {dst_file} is up-to-date")
        return False

    if dst.exists():
        if force:
            print(f"  [REFRESH] forcing rebuild of {dst_file}")
        else:
            print(f"  [REFRESH] source image changed for {dst_file}")

    dst_dir.mkdir(parents=True, exist_ok=True)

    print(f"  Loading {src.name} ({src.stat().st_size // 1024} KB)...")
    img = Image.open(src).convert("RGBA")

    # Resize large images to avoid memory issues
    w, h = img.size
    if max(w, h) > MAX_SIZE:
        ratio = MAX_SIZE / max(w, h)
        new_w, new_h = int(w * ratio), int(h * ratio)
        print(f"  Resizing {w}x{h} → {new_w}x{new_h}")
        img = img.resize((new_w, new_h), Image.LANCZOS)

    print(f"  Running rembg...")
    result = remove_background(img)

    result.save(dst)
    print(f"  [OK] Saved → {dst.relative_to(BASE_DIR)}")
    return True


def sync_outputs(expected_outputs: set[Path], *, dry_run: bool):
    for cat, model, _, _ in JOBS:
        target_dir = PUBLIC_ROOT / cat / model
        if not target_dir.exists():
            continue
        for candidate in sorted(target_dir.glob("*-nobg.png")):
            if candidate in expected_outputs:
                continue
            rel = candidate.relative_to(BASE_DIR)
            if dry_run:
                print(f"[SYNC] would remove stale derivative {rel}")
                continue
            candidate.unlink()
            print(f"[SYNC] removed stale derivative {rel}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Gera e sincroniza os PNGs transparentes curados em public/case-assets.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Reprocessa todos os derivativos mesmo se o output estiver atualizado.",
    )
    parser.add_argument(
        "--sync",
        action="store_true",
        help="Remove derivativos *-nobg.png que não fazem mais parte da lista JOBS.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Mostra quais arquivos seriam atualizados/removidos sem escrever no disco.",
    )
    args = parser.parse_args()

    print(f"Processing {len(JOBS)} images...\n")
    expected_outputs = {
        PUBLIC_ROOT / cat / model / dst_file
        for cat, model, _, dst_file in JOBS
    }
    if args.sync:
        sync_outputs(expected_outputs, dry_run=args.dry_run)

    for i, (cat, model, src_file, dst_file) in enumerate(JOBS, 1):
        print(f"[{i}/{len(JOBS)}] {model} — {dst_file}")
        src = SCRAPE_ROOT / cat / "models" / model / "assets" / src_file
        dst = PUBLIC_ROOT / cat / model / dst_file
        if args.dry_run:
            action = "rebuild" if args.force or destination_is_stale(src, dst) else "skip"
            print(f"  [DRY-RUN] would {action} {dst.relative_to(BASE_DIR)}")
            print()
            continue
        try:
            process(cat, model, src_file, dst_file, force=args.force)
        except Exception as e:
            print(f"  [ERROR] {e}", file=sys.stderr)
        print()
    print("Done.")
