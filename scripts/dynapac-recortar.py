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

import numpy as np
from PIL import Image

REPO = Path(__file__).resolve().parent.parent
DB = REPO / "data" / "dynapac-db.json"
ORIGENS = REPO / "fotos-dynapac"
SAIDA = REPO / "public" / "dynapac-assets"

MODELO = "birefnet-general"  # preserva alça fina e alça branca sobre fundo branco
MAX_ENTRADA = 1600   # limite antes do modelo, por memória
MAX_SAIDA = 1200     # limite do arquivo publicado
MASCARA = 320        # resolução da análise de fragmentos
AREA_MINIMA = 0.03   # fragmento menor que isto (vs. maior peça) é candidato a descarte
FOLGA_PECA = 11      # px (na máscara) de distância até o corpo para ainda ser peça da máquina
MARGEM = 12          # folga ao recortar o excesso transparente


def componentes(mask: np.ndarray) -> list[tuple[int, np.ndarray]]:
    """Componentes conexos (4-vizinhos), do maior para o menor."""
    h, w = mask.shape
    visto = np.zeros_like(mask, dtype=bool)
    achados: list[tuple[int, np.ndarray]] = []
    for y in range(h):
        for x in range(w):
            if not mask[y, x] or visto[y, x]:
                continue
            fila = deque([(y, x)])
            visto[y, x] = True
            pixels = []
            while fila:
                cy, cx = fila.popleft()
                pixels.append((cy, cx))
                for ny, nx in ((cy - 1, cx), (cy + 1, cx), (cy, cx - 1), (cy, cx + 1)):
                    if 0 <= ny < h and 0 <= nx < w and mask[ny, nx] and not visto[ny, nx]:
                        visto[ny, nx] = True
                        fila.append((ny, nx))
            comp = np.zeros_like(mask, dtype=bool)
            ys, xs = zip(*pixels)
            comp[list(ys), list(xs)] = True
            achados.append((len(pixels), comp))
    achados.sort(key=lambda c: -c[0])
    return achados


def limpar_fragmentos(img: Image.Image) -> tuple[Image.Image, int]:
    """Apaga peças soltas longe da máquina (selos de campanha, respingos).

    Só o tamanho não serve como critério: a alça de uma placa vibratória é fina
    e pode sair do modelo como peça separada, enquanto o selo de campanha fica
    num canto, longe de tudo. Por isso um fragmento pequeno só é descartado
    quando também está distante do corpo principal.
    """
    from PIL import ImageFilter

    alpha = np.asarray(img.getchannel("A"))
    pequena = Image.fromarray(alpha).resize((MASCARA, MASCARA), Image.NEAREST)
    mask = np.asarray(pequena) > 128
    if not mask.any():
        return img, 0
    comps = componentes(mask)
    if len(comps) <= 1:
        return img, 0

    maior_area, maior_comp = comps[0]
    # Vizinhança do corpo principal: o que encostar aqui é considerado peça dele.
    vizinhanca = np.asarray(
        Image.fromarray((maior_comp * 255).astype(np.uint8))
        .filter(ImageFilter.MaxFilter(FOLGA_PECA * 2 + 1))
    ) > 128

    manter = np.zeros_like(mask)
    removidos = 0
    for area, comp in comps:
        perto = bool((comp & vizinhanca).any())
        if area >= maior_area * AREA_MINIMA or perto:
            manter |= comp
        else:
            removidos += 1
    if not removidos:
        return img, 0
    manter_full = np.asarray(
        Image.fromarray((manter * 255).astype(np.uint8)).resize(img.size, Image.BILINEAR)
    ) > 64
    novo = np.array(img)
    novo[..., 3] = np.where(manter_full, novo[..., 3], 0)
    return Image.fromarray(novo, "RGBA"), removidos


def cortar_sobra(img: Image.Image) -> Image.Image:
    caixa = img.getchannel("A").point(lambda v: 255 if v > 8 else 0).getbbox()
    if not caixa:
        return img
    x0, y0, x1, y1 = caixa
    x0 = max(0, x0 - MARGEM); y0 = max(0, y0 - MARGEM)
    x1 = min(img.width, x1 + MARGEM); y1 = min(img.height, y1 + MARGEM)
    return img.crop((x0, y0, x1, y1))


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
        from rembg import new_session, remove
    except ImportError:
        print("! rembg indisponível. Use python3.11 (veja docs/OPERATIONS.md).", file=sys.stderr)
        return 1

    db = json.loads(DB.read_text(encoding="utf-8"))
    sessao = new_session(args.modelo)
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
                        im = im.convert("RGBA")
                        im.thumbnail((MAX_ENTRADA, MAX_ENTRADA), Image.LANCZOS)
                        recortada = remove(im, session=sessao)
                    recortada, removidos = limpar_fragmentos(recortada)
                    recortada = cortar_sobra(recortada)
                    recortada.thumbnail((MAX_SAIDA, MAX_SAIDA), Image.LANCZOS)
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
