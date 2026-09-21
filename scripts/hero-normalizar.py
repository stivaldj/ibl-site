#!/usr/bin/env python3.11
"""Normaliza as máquinas do hero da home CASE num palco comum.

Antes, cada máquina vinha de um SVG do Canva com enquadramento próprio, e o
main.js compensava com 12 números de ajuste manual por máquina (96 ao todo),
calibrados a olho para uma única largura de tela.

Aqui todas saem no mesmo canvas, apoiadas na mesma linha de chão e centradas.
O único número por máquina é `largura`: a fração do palco que ela ocupa, que
preserva a noção de porte (a minicarregadeira não pode parecer maior que a
escavadeira de 22 t). Com isso o front-end não precisa de ajuste nenhum.

    python3.11 scripts/hero-normalizar.py [--only slug,slug]

Fontes em .jpg (foto de estúdio com fundo branco) são recortadas com o mesmo
motor das fichas; fontes já recortadas (-nobg.webp) são usadas como estão.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))

REPO = Path(__file__).resolve().parent.parent
SAIDA = REPO / "public" / "case-assets" / "hero"
ASSETS = REPO / "public" / "case-assets"

PALCO = (1600, 1000)   # canvas comum a todas as máquinas
CHAO = 930             # linha de chão (y) onde toda máquina apoia
ALTURA_MAX = 860       # teto: lança de escavadeira não pode estourar o palco

# slug -> (fonte, largura). `largura` é o único ajuste por máquina.
MAQUINAS = {
    "580n":   (REPO / "fotos/hero-src/580n.jpg", 0.88),
    "cx220c": (ASSETS / "escavadeiras-hidraulicas/cx220c-s2/55007306_1457a6f0ed344b968436ff9642c8781e-nobg.webp", 0.98),
    "w20g":   (REPO / "fotos/hero-src/w20g.jpg", 0.84),
    "sv300b": (ASSETS / "minicarregadeiras/sv300b/sv300b-nobg.webp", 0.64),
    "885b":   (ASSETS / "motoniveladoras/885b-series-2/b75b722d_a957dd987b4d409c9a5dc6fc81bee9b1-nobg.webp", 0.98),
    "cx22d":  (ASSETS / "miniescavadeiras/cx22d/71a1ea6b_888eeec9a00a43f2876c9761741b0411-nobg.webp", 0.52),
    "1107ex": (ASSETS / "rolo-compactador/1107ex/1107ex-nobg.webp", 0.74),
    "2050m":  (ASSETS / "tratores-de-esteiras/2050m/9a075b7b_208c9d0c083a401e8454168a273134d5-nobg.webp", 0.82),
}


def carregar(fonte: Path, sessao_ref: list) -> Image.Image:
    img = Image.open(fonte)
    if fonte.suffix.lower() in {".jpg", ".jpeg"}:
        from recorte_fundo import abrir_sessao, recortar
        if not sessao_ref:
            sessao_ref.append(abrir_sessao())
        img, _ = recortar(img, sessao_ref[0])
    return img.convert("RGBA")


def normalizar(img: Image.Image, largura: float) -> Image.Image:
    caixa = img.getchannel("A").point(lambda v: 255 if v > 8 else 0).getbbox()
    img = img.crop(caixa)
    escala = min(PALCO[0] * largura / img.width, ALTURA_MAX / img.height)
    novo = (max(1, round(img.width * escala)), max(1, round(img.height * escala)))
    img = img.resize(novo, Image.LANCZOS)
    palco = Image.new("RGBA", PALCO, (0, 0, 0, 0))
    palco.alpha_composite(img, ((PALCO[0] - img.width) // 2, CHAO - img.height))
    return palco


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only")
    args = ap.parse_args()
    filtro = set(args.only.split(",")) if args.only else None
    SAIDA.mkdir(parents=True, exist_ok=True)
    sessao: list = []
    for slug, (fonte, largura) in MAQUINAS.items():
        if filtro and slug not in filtro:
            continue
        if not fonte.exists():
            print(f"  ! fonte ausente: {slug} ({fonte})")
            return 1
        palco = normalizar(carregar(fonte, sessao), largura)
        destino = SAIDA / f"{slug}.webp"
        palco.save(destino, "WEBP", quality=86, method=6)
        print(f"  ✓ hero/{slug}.webp  largura={largura}  {destino.stat().st_size // 1024} KB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
