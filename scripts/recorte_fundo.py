#!/usr/bin/env python3.11
"""Núcleo do recorte de fundo das fotos de produto (usado por Dynapac e CASE).

Substitui o preenchimento por cor a partir dos cantos, que não alcança área
cercada (o vão da alça de uma placa vibratória) nem remove sombra em degradê
(a laje de estúdio sob a máquina).

Requer `rembg` no Python 3.11.
"""
from __future__ import annotations

from collections import deque

import numpy as np
from PIL import Image, ImageFilter

MODELO = "birefnet-general"  # preserva alça fina e alça branca sobre fundo branco
MAX_ENTRADA = 1600   # limite antes do modelo, por memória
MAX_SAIDA = 1200     # limite do arquivo publicado
MASCARA = 320        # resolução da análise de fragmentos
AREA_MINIMA = 0.03   # fragmento menor que isto (vs. maior peça) é candidato a descarte
FOLGA_PECA = 11      # px (na máscara) até o corpo para ainda ser peça da máquina
MARGEM = 12          # folga ao recortar o excesso transparente
QUALIDADE = 82


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
    num canto, longe de tudo. Um fragmento pequeno só é descartado quando também
    está distante do corpo principal.
    """
    alpha = np.asarray(img.getchannel("A"))
    pequena = Image.fromarray(alpha).resize((MASCARA, MASCARA), Image.NEAREST)
    mask = np.asarray(pequena) > 128
    if not mask.any():
        return img, 0
    comps = componentes(mask)
    if len(comps) <= 1:
        return img, 0

    maior_area, maior_comp = comps[0]
    vizinhanca = np.asarray(
        Image.fromarray((maior_comp * 255).astype(np.uint8))
        .filter(ImageFilter.MaxFilter(FOLGA_PECA * 2 + 1))
    ) > 128

    manter = np.zeros_like(mask)
    removidos = 0
    for area, comp in comps:
        if area >= maior_area * AREA_MINIMA or bool((comp & vizinhanca).any()):
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
    return img.crop((max(0, x0 - MARGEM), max(0, y0 - MARGEM),
                     min(img.width, x1 + MARGEM), min(img.height, y1 + MARGEM)))


def fundo_de_estudio(img: Image.Image, limiar: int = 232) -> bool:
    """Foto de estúdio (fundo claro uniforme) x foto ambientada (obra, céu).

    Só a primeira deve ser recortada; recortar uma foto de obra apagaria o
    contexto que a imagem existe para mostrar.
    """
    rgb = img.convert("RGB")
    w, h = rgb.size
    amostras = [rgb.getpixel(p) for p in
                ((2, 2), (w - 3, 2), (2, h - 3), (w - 3, h - 3), (w // 2, 2), (w // 2, h - 3))]
    claros = sum(1 for c in amostras if min(c) > limiar)
    return claros >= 5


def recortar(img: Image.Image, sessao) -> tuple[Image.Image, int]:
    """Aplica o recorte completo: modelo, limpeza de fragmentos e corte de sobra."""
    from rembg import remove

    img = img.convert("RGBA")
    img.thumbnail((MAX_ENTRADA, MAX_ENTRADA), Image.LANCZOS)
    saida = remove(img, session=sessao)
    saida, removidos = limpar_fragmentos(saida)
    saida = cortar_sobra(saida)
    saida.thumbnail((MAX_SAIDA, MAX_SAIDA), Image.LANCZOS)
    return saida, removidos


def abrir_sessao(modelo: str = MODELO):
    from rembg import new_session
    return new_session(modelo)
