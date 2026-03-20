#!/usr/bin/env python3
"""
Process photos from fotos/ → public/case-assets/fotos-processed/

Steps per image:
  1. Resize to max 1400px (avoids OOM on 32MB files)
  2. rembg background removal
  3. Near-white pixel cleanup (fixes residual white patches, e.g. 885B)
"""
import argparse
import sys
from pathlib import Path
import numpy as np
from PIL import Image

BASE_DIR  = Path(__file__).parent
INPUT_DIR = BASE_DIR / "fotos"
OUT_DIR   = BASE_DIR / "public" / "case-assets" / "fotos-processed"
MAX_SIZE  = 1400      # px — keeps quality but avoids memory crash on big files
WHITE_THR = 225       # R,G,B all above this → transparent (near-white cleanup)

# Known mappings (just for display)
LABELS = {
    "20170622111823_14_CLICK_DPBR_CNH_CASE_TRATOR_DE_ESTEIRA_2050M_FRONTAL_CABINE_ESQUERDA_SAIDA": "trator-2050m",
    "20170626105327_CLICK_DPBR_CNH_CASE_ESCAVADEIRA_CX220C_2643_1":                                "cx220c-v1",
    "20170612142618_CNH_CASE_ESCAVADEIRA_CX220C_LATERAL_ESQUERDA_alta":                            "cx220c-lateral",
    "20170613110405_Carregadeira_W20F_Foto_Estudio_Alta_33":                                       "w20f-studio",
    "20240502180734__DS_8336":                                                                      "unknown-ds8336",
    "20240502182755__DS_8800":                                                                      "unknown-ds8800",
    "20240502192248_DJI_0276":                                                                      "unknown-dji",
    "20240503120630_CCE_W20G_1_3_4_front_DIR":                                                     "w20g-front",
    "20240627141950_Case_CX22D_005":                                                                "cx22d",
    "20220803151602_885B_5":                                                                        "885b-motoniveladora",
}


def clean_white(img: Image.Image, threshold: int) -> Image.Image:
    """Force near-white pixels to fully transparent."""
    data = np.array(img, dtype=np.uint16)
    r, g, b, a = data[:, :, 0], data[:, :, 1], data[:, :, 2], data[:, :, 3]
    mask = (r > threshold) & (g > threshold) & (b > threshold)
    data[mask, 3] = 0
    return Image.fromarray(data.astype(np.uint8))


def remove_background(img: Image.Image) -> Image.Image:
    from rembg import remove

    return remove(img)


def destination_is_stale(src: Path, dst: Path) -> bool:
    return not dst.exists() or src.stat().st_mtime_ns > dst.stat().st_mtime_ns


def process(src: Path, dst: Path, *, force: bool):
    if dst.exists() and not force and not destination_is_stale(src, dst):
        print("  [SKIP] up-to-date")
        return False

    if dst.exists():
        if force:
            print("  [REFRESH] forced rebuild")
        else:
            print("  [REFRESH] source image changed")

    mb = src.stat().st_size / 1_048_576
    print(f"  Loading {src.name} ({mb:.1f} MB) …")
    img = Image.open(src).convert("RGBA")

    w, h = img.size
    if max(w, h) > MAX_SIZE:
        ratio = MAX_SIZE / max(w, h)
        nw, nh = int(w * ratio), int(h * ratio)
        print(f"  Resizing {w}×{h} → {nw}×{nh}")
        img = img.resize((nw, nh), Image.LANCZOS)

    print(f"  Running rembg …")
    result = remove_background(img)

    print(f"  Cleaning near-white artifacts (threshold={WHITE_THR}) …")
    result = clean_white(result, WHITE_THR)

    dst.parent.mkdir(parents=True, exist_ok=True)
    result.save(dst, optimize=True)
    print(f"  [OK] → {dst.relative_to(BASE_DIR)}")
    return True


def sync_outputs(expected_outputs: set[Path], *, dry_run: bool):
    for candidate in sorted(OUT_DIR.glob("*.png")):
        if candidate in expected_outputs:
            continue
        rel = candidate.relative_to(BASE_DIR)
        if dry_run:
            print(f"[SYNC] would remove stale output {rel}")
            continue
        candidate.unlink()
        print(f"[SYNC] removed stale output {rel}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Processa fotos locais e atualiza public/case-assets/fotos-processed.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Reprocessa todas as imagens mesmo se o output estiver atualizado.",
    )
    parser.add_argument(
        "--sync",
        action="store_true",
        help="Remove outputs em fotos-processed/ que não correspondem mais às fotos de origem.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Mostra quais mudanças seriam feitas sem gravar arquivos.",
    )
    args = parser.parse_args()

    photos = sorted(INPUT_DIR.glob("*.jpg")) + sorted(INPUT_DIR.glob("*.png"))
    print(f"Found {len(photos)} photos in fotos/\n")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    expected_outputs = {
        OUT_DIR / f"{LABELS.get(src.stem, src.stem)}-nobg.png"
        for src in photos
    }

    if args.sync:
        sync_outputs(expected_outputs, dry_run=args.dry_run)

    for i, src in enumerate(photos, 1):
        label = LABELS.get(src.stem, src.stem)
        dst   = OUT_DIR / f"{label}-nobg.png"
        print(f"[{i}/{len(photos)}] {label}")
        if args.dry_run:
            action = "rebuild" if args.force or destination_is_stale(src, dst) else "skip"
            print(f"  [DRY-RUN] would {action} {dst.relative_to(BASE_DIR)}")
            print()
            continue
        try:
            process(src, dst, force=args.force)
        except Exception as e:
            print(f"  [ERROR] {e}", file=sys.stderr)
        print()

    print(f"Done. Output → {OUT_DIR.relative_to(BASE_DIR)}")
