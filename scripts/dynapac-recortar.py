#!/usr/bin/env python3.11
"""Recorta o fundo das fotos Dynapac com rembg (mesmo método usado na linha CASE).

O recorte antigo era um preenchimento a partir dos quatro cantos: nunca alcança
área cercada (o vão da alça das placas vibratórias) nem sombra em degradê (a
"laje" de estúdio sob a máquina). Aqui o fundo é separado por modelo de imagem
e o resultado ainda passa por uma limpeza de fragmentos soltos, que remove
selos de campanha (ex.: o emblema SEISMIC) deixados longe da máquina.

O modelo padrão é o `birefnet-general`. Foi escolhido por comparação: o `u2net`
apaga a alça fina das placas vibratórias e o `isnet-general-use` perde a alça
branca da DRP60D, que se confunde com o fundo branco do estúdio.

Requer Python 3.11 com rembg instalado:
    python3.11 scripts/dynapac-recortar.py [--only slug,slug] [--force]

A saída vai direto para public/dynapac-assets/{categoria}/{slug}/{slug}.webp,
que é o arquivo versionado e publicado. `generate_pages.py` reaproveita esse
derivado enquanto ele for mais novo que o original.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import deque
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from recorte_fundo import MODELO, abrir_sessao, recortar  # noqa: E402

REPO = Path(__file__).resolve().parent.parent
DB = REPO / "data" / "dynapac-db.json"
ORIGENS = REPO / "fotos-dynapac"
SAIDA = REPO / "public" / "dynapac-assets"



def origem(cat: str, slug: str) -> Path | None:
    pasta = ORIGENS / cat / slug
    if not pasta.exists():
        return None
    arquivos = [p for p in sorted(pasta.iterdir())
                if p.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"} and not p.name.startswith(".")]
    return arquivos[0] if arquivos else None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", help="lista de slugs separados por vírgula")
    ap.add_argument("--force", action="store_true", help="refaz mesmo se a saída estiver atual")
    ap.add_argument("--modelo", default=MODELO, help=f"modelo do rembg (padrão: {MODELO})")
    args = ap.parse_args()
    filtro = {s.strip() for s in args.only.split(",")} if args.only else None

    try:
        sessao = abrir_sessao(args.modelo)
    except ImportError:
        print("! rembg indisponível. Use python3.11 (veja docs/OPERATIONS.md).", file=sys.stderr)
        return 1

    db = json.loads(DB.read_text(encoding="utf-8"))
    feitos = pulados = falhas = limpos = 0

    for cat in db["categorias"]:
        for sub in cat["subcategorias"]:
            for modelo in sub["modelos"]:
                slug, cat_slug = modelo["slug"], cat["slug"]
                if filtro and slug not in filtro:
                    continue
                src = origem(cat_slug, slug)
                if not src:
                    print(f"  ! sem original: {cat_slug}/{slug}")
                    falhas += 1
                    continue
                dst_dir = SAIDA / cat_slug / slug
                dst = dst_dir / f"{slug}.webp"
                if dst.exists() and not args.force and dst.stat().st_mtime_ns >= src.stat().st_mtime_ns:
                    pulados += 1
                    continue
                try:
                    with Image.open(src) as im:
                        recortada, removidos = recortar(im, sessao)
                    dst_dir.mkdir(parents=True, exist_ok=True)
                    recortada.save(dst, "WEBP", quality=82, method=6)
                    feitos += 1
                    limpos += 1 if removidos else 0
                    extra = f" · {removidos} fragmento(s) removido(s)" if removidos else ""
                    print(f"  ✓ {cat_slug}/{slug}{extra}")
                except Exception as exc:  # noqa: BLE001
                    print(f"  ! falhou {cat_slug}/{slug}: {exc}")
                    falhas += 1

    print(f"\n{feitos} recortadas ({limpos} com fragmento removido) · {pulados} já atuais · {falhas} falhas")
    return 0 if not falhas else 1


if __name__ == "__main__":
    raise SystemExit(main())
