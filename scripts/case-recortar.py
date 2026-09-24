#!/usr/bin/env python3.11
"""Recorta o fundo branco das fotos de estúdio da linha CASE.

As fichas de produto CASE exibiam a foto original do fabricante, que vem com
fundo branco de estúdio e, na página escura do site, aparece como uma caixa
branca em volta da máquina. Aqui cada foto de estúdio ganha um derivado
`{nome}-nobg.webp` ao lado, com o fundo removido; `generate_pages.py` prefere
esse derivado quando ele existe.

Fotos ambientadas (obra, céu, terra) são deixadas como estão: nelas o fundo é
o conteúdo, não ruído.

Requer Python 3.11 com rembg:
    python3.11 scripts/case-recortar.py [--only slug,slug] [--force]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from recorte_fundo import MODELO, abrir_sessao, fundo_de_estudio, recortar  # noqa: E402

REPO = Path(__file__).resolve().parent.parent
ASSETS = REPO / "public" / "case-assets"
EXTENSOES = {".jpg", ".jpeg", ".png", ".webp"}
SUFIXO = "-nobg"


def e_derivado(p: Path) -> bool:
    """Arquivo gerado por nós ou foto ambientada curada — não é fonte de recorte."""
    return p.stem.endswith(SUFIXO) or p.stem.endswith("-card")


def fontes() -> list[Path]:
    achadas: list[Path] = []
    for pasta in sorted(ASSETS.iterdir()):
        if not pasta.is_dir() or pasta.name == "fotos-processed":
            continue
        for modelo_dir in sorted(pasta.iterdir()):
            if not modelo_dir.is_dir():
                continue
            arquivos = [p for p in sorted(modelo_dir.iterdir())
                        if p.suffix.lower() in EXTENSOES and not e_derivado(p)]
            # o .webp é derivado de otimização do .jpg/.png de mesmo nome
            nomes = {p.stem for p in arquivos if p.suffix.lower() != ".webp"}
            achadas += [p for p in arquivos if p.suffix.lower() != ".webp" or p.stem not in nomes]
    return achadas


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", help="lista de slugs de modelo separados por vírgula")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--modelo", default=MODELO, help=f"modelo do rembg (padrão: {MODELO})")
    args = ap.parse_args()
    filtro = {s.strip() for s in args.only.split(",")} if args.only else None

    try:
        sessao = abrir_sessao(args.modelo)
    except ImportError:
        print("! rembg indisponível. Use python3.11 (veja docs/OPERATIONS.md).", file=sys.stderr)
        return 1

    feitos = pulados = ambientadas = falhas = 0
    for src in fontes():
        modelo_slug = src.parent.name
        if filtro and modelo_slug not in filtro:
            continue
        dst = src.with_name(f"{src.stem}{SUFIXO}.webp")
        if dst.exists() and not args.force and dst.stat().st_mtime_ns >= src.stat().st_mtime_ns:
            pulados += 1
            continue
        try:
            with Image.open(src) as im:
                if not fundo_de_estudio(im):
                    ambientadas += 1
                    continue
                recortada, removidos = recortar(im, sessao)
            recortada.save(dst, "WEBP", quality=82, method=6)
            feitos += 1
            extra = f" · {removidos} fragmento(s) removido(s)" if removidos else ""
            print(f"  ✓ {src.parent.parent.name}/{modelo_slug}/{dst.name}{extra}")
        except Exception as exc:  # noqa: BLE001
            print(f"  ! falhou {src}: {exc}")
            falhas += 1

    print(f"\n{feitos} recortadas · {ambientadas} ambientadas (mantidas) · "
          f"{pulados} já atuais · {falhas} falhas")
    return 0 if not falhas else 1


if __name__ == "__main__":
    raise SystemExit(main())
