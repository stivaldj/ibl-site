#!/usr/bin/env python3
"""Espelha o catálogo Dynapac do site NACIONAL (dynapac.com/br-pt).

Fonte da verdade: as três listagens de produtos do site brasileiro. A aba
"Produtos" do próprio site esconde tudo que está marcado como `data-discontinued="true"`
("Interrompido"), então só os modelos ativos entram aqui.

Saída: data/dynapac-db.json (mesmo schema consumido por generate_pages.py) e
data/dynapac-downloads.json (fila de fotos para scripts/dynapac-download-fotos.py).

Uso:
    python3 scripts/dynapac-scrape-nacional.py [--cache-dir DIR] [--offline]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
import unicodedata
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from html import unescape
from pathlib import Path

BASE = "https://dynapac.com"
LOCALE = "/br-pt"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 IBL-site-build"
REPO = Path(__file__).resolve().parent.parent

LISTAGENS = {
    "compactacao": f"{BASE}{LOCALE}/products/compaction",
    "pavimentacao": f"{BASE}{LOCALE}/products/paving",
    "equipamentos-leves": f"{BASE}{LOCALE}/products/light-equipment",
}

CATEGORIA_NOMES = {
    "compactacao": "Compactação",
    "pavimentacao": "Pavimentação",
    "equipamentos-leves": "Equipamentos Leves",
}

# Subcategorias ignoradas no espelho: mesas/screeds são acessório de pavimentadora,
# não máquina de catálogo.
SUBCATEGORIAS_IGNORADAS = {"mesas", "fixed screeds", "screeds"}

# O site nacional repete a mesma subcategoria com grafias/idiomas diferentes.
# Normalizamos para um rótulo único em português.
SUBCATEGORIA_CANONICA = {
    "rolos de um cilindro para solos": ("Rolos de Um Cilindro para Solos", "rolos-de-um-cilindro-para-solos"),
    "rolos tandem para asfalto/solos": ("Rolos Tandem para Asfalto e Solos", "rolos-tandem"),
    "rolos combinados": ("Rolos Combinados", "rolos-combinados"),
    "compactadores de pneus": ("Compactadores de Pneus", "compactadores-de-pneus"),
    "compactador tamping": ("Compactadores Tamping", "compactadores-tamping"),
    "rolo com cilindro de aço": ("Rolos Estáticos", "rolos-estaticos"),
    "pavimentadoras rodoviárias": ("Pavimentadoras Rodoviárias", "pavimentadoras-rodoviarias"),
    "pavimentadoras urbanas": ("Pavimentadoras Urbanas", "pavimentadoras-urbanas"),
    "pavimentadoras compactas": ("Pavimentadoras Compactas", "pavimentadoras-compactas"),
    "compact pavers": ("Pavimentadoras Compactas", "pavimentadoras-compactas"),
    "commercial pavers": ("Pavimentadoras Comerciais", "pavimentadoras-comerciais"),
    "pavimentadoras americanas": ("Pavimentadoras Comerciais", "pavimentadoras-comerciais"),
    "mini pavimentadoras": ("Mini Pavimentadoras", "mini-pavimentadoras"),
    "equipamentos leves": ("Placas Vibratórias", "placas-vibratorias"),
    "reversible plates": ("Placas Reversíveis", "placas-reversiveis"),
    "soquetes": ("Soquetes Compactadores", "soquetes"),
    "compactadores de valeta": ("Compactadores de Valeta", "compactadores-de-valeta"),
    "rolos duplex": ("Rolos Duplex", "rolos-duplex"),
    "mix spreader": ("Espalhadoras", "espalhadoras"),
}

# Ordem de exibição das subcategorias dentro de cada categoria.
ORDEM_SUBCATEGORIAS = [
    "rolos-de-um-cilindro-para-solos", "rolos-tandem", "rolos-combinados",
    "compactadores-de-pneus", "compactadores-tamping", "rolos-estaticos",
    "pavimentadoras-rodoviarias", "pavimentadoras-urbanas", "pavimentadoras-compactas",
    "pavimentadoras-comerciais", "mini-pavimentadoras",
    "placas-vibratorias", "placas-reversiveis", "soquetes",
    "compactadores-de-valeta", "rolos-duplex", "espalhadoras",
]

# Rótulo no singular usado para abrir a descrição de cada modelo.
SUBCATEGORIA_SINGULAR = {
    "rolos-de-um-cilindro-para-solos": "Rolo compactador de um cilindro para solos",
    "rolos-tandem": "Rolo compactador tandem para asfalto e solos",
    "rolos-combinados": "Rolo compactador combinado",
    "compactadores-de-pneus": "Compactador de pneus",
    "compactadores-tamping": "Compactador tamping",
    "rolos-estaticos": "Rolo compactador estático",
    "pavimentadoras-rodoviarias": "Pavimentadora rodoviária",
    "pavimentadoras-urbanas": "Pavimentadora urbana",
    "pavimentadoras-compactas": "Pavimentadora compacta",
    "pavimentadoras-comerciais": "Pavimentadora comercial",
    "mini-pavimentadoras": "Mini pavimentadora",
    "placas-vibratorias": "Placa vibratória compactadora",
    "placas-reversiveis": "Placa vibratória reversível",
    "soquetes": "Soquete compactador",
    "compactadores-de-valeta": "Compactador de valeta",
    "rolos-duplex": "Rolo compactador duplex",
    "espalhadoras": "Espalhadora de agregados",
}

# Specs priorizadas na ficha (rótulo de saída -> padrões aceitos no site).
SPEC_PRIORIDADE = [
    ("peso_operacional", [r"^peso operacional$", r"^peso operacional incl\. rops$", r"^peso operacional \(incl", r"^peso operacional \(m[áa]x"]),
    ("largura_tambor", [r"^w\. largura do cilindro$", r"^largura de trabalho", r"^largura do cilindro", r"^largura de compacta"]),
    ("diametro_tambor", [r"^d\. di[âa]metro do cilindro$", r"^di[âa]metro do cilindro"]),
    ("motor", [r"^modelo do motor$", r"^motor$", r"^fabricante do motor"]),
    ("potencia", [r"^pot[êe]ncia", r"^sa[íi]da de pot"]),
    ("carga_linear", [r"^carga est[áa]tica linear"]),
    ("forca_centrifuga", [r"^for[çc]a centr[íi]fuga"]),
    ("frequencia", [r"^frequ[êe]ncia"]),
    ("largura_pavimentacao", [r"^largura de pavimenta", r"^largura b[áa]sica"]),
    ("capacidade_funil", [r"^capacidade do funil", r"^capacidade da tremonha"]),
]

# Rótulos que o site nacional ainda serve em inglês nos cards.
CARD_LABEL_PT = {
    "operating weight": "Peso operacional",
    "compaction force": "Força de compactação",
    "working width": "Largura de trabalho",
    "centrifugal force": "Força centrífuga",
    "drum width": "Largura de trabalho",
    "engine power": "Potência",
}

SPEC_LABELS = {
    "peso_operacional": "Peso operacional",
    "largura_tambor": "Largura de trabalho",
    "diametro_tambor": "Diâmetro do cilindro",
    "motor": "Motor",
    "potencia": "Potência",
    "carga_linear": "Carga estática linear",
    "forca_centrifuga": "Força centrífuga",
    "frequencia": "Frequência de vibração",
    "largura_pavimentacao": "Largura de pavimentação",
    "capacidade_funil": "Capacidade do funil",
}


def normalizar_valor(valor: str) -> str:
    """Padroniza a grafia numérica das specs vindas do site.

    A fonte mistura convenções — o mesmo 2130 aparece como "2,130 mm" e
    "2.130 mm" na mesma ficha. Como o site é brasileiro, milhar vira ponto.
    Vírgula seguida de 1 ou 2 dígitos é decimal e não é tocada.
    """
    valor = re.sub(r"(?<=\d),(?=\d{3}(?!\d))", ".", valor)
    valor = re.sub(r"\bKg\b", "kg", valor)
    valor = re.sub(r"(\d)(rpm|kg|mm|hp|kW|kN|t/h)\b", r"\1 \2", valor)
    valor = re.sub(r"\s+([,.)])", r"\1", valor)
    valor = re.sub(r"\(\s+", "(", valor)
    valor = re.sub(r"\bkw\b", "kW", valor)
    valor = re.sub(r"@(?=\d)", "@ ", valor)
    return re.sub(r"\s{2,}", " ", valor).strip()


def slugify(value: str) -> str:
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
    value = value.lower().replace("+", "-plus")
    value = re.sub(r"[^a-z0-9]+", "-", value).strip("-")
    return value or "modelo"


def strip_tags(html: str) -> str:
    return re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", " ", html))).strip()


def fetch(url: str, cache_dir: Path, offline: bool = False) -> str:
    cache_dir.mkdir(parents=True, exist_ok=True)
    cached = cache_dir / (slugify(url.replace(BASE, "")) + ".html")
    if cached.exists():
        return cached.read_text(encoding="utf-8", errors="replace")
    if offline:
        raise RuntimeError(f"sem cache para {url} (modo --offline)")
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    for tentativa in range(3):
        try:
            with urllib.request.urlopen(req, timeout=45) as resp:
                html = resp.read().decode("utf-8", errors="replace")
            cached.write_text(html, encoding="utf-8")
            return html
        except Exception as exc:  # noqa: BLE001
            if tentativa == 2:
                raise
            print(f"    ! retry {tentativa + 1}/2 em {url}: {exc}", file=sys.stderr)
            time.sleep(2 + tentativa * 3)
    raise RuntimeError("inalcançável")


def parse_listagem(html: str) -> list[dict]:
    """Extrai os cards ativos (data-discontinued="false") de uma listagem."""
    itens: list[dict] = []
    padrao = re.compile(
        r'<div class="large-4 medium-6 columns product-grid-box no-padding"([^>]*)>(.*?)'
        r'<div class="large-6 medium-6 small-6 columns grid-btn add-to-compare',
        re.S,
    )
    for match in padrao.finditer(html):
        attrs, corpo = match.group(1), match.group(2)

        def attr(nome: str) -> str:
            found = re.search(nome + r'="([^"]*)"', attrs)
            return found.group(1) if found else ""

        if attr("data-discontinued") != "false":
            continue
        href = re.search(r'href="(/br-pt/products/[^"]+)"', corpo)
        if not href:
            continue
        card_specs: dict[str, str] = {}
        for spec in re.finditer(
            r'<span class="spec-title">([^<]+)</span>\s*<span class="metric">'
            r'<span class="value">([^<]*)</span>(?:\s*<span class="unit">([^<]*)</span>)?',
            corpo,
        ):
            titulo = unescape(spec.group(1)).strip().rstrip(":")
            valor = unescape(spec.group(2)).strip()
            unidade = unescape(spec.group(3) or "").strip()
            if valor:
                card_specs[titulo] = f"{valor} {unidade}".strip()
        itens.append(
            {
                "modelo": unescape(attr("data-label")).replace("Dynapac ", "").strip(),
                "subcategoria_bruta": unescape(attr("data-category")).strip(),
                "url": BASE + href.group(1),
                "card_specs": card_specs,
                "thumb": (re.search(r'data-src="([^"]+)"', corpo) or [None, ""])[1],
            }
        )
    return itens


PROXY_PREFIX = "/assets/images/made/images/remote/https_"
CDN_HOSTS = ("pdf.dynapac.com", "pim.dynapac.com")


def origem_do_proxy(url: str) -> str:
    """Converte a URL do redimensionador do site na foto original do CDN.

    O site serve `/assets/images/made/images/remote/https_<host>/<path>_L_A_Q.jpg`;
    o arquivo de origem é `https://<host>/<path>.jpg`.
    """
    if PROXY_PREFIX not in url:
        return ""
    caminho = url.split(PROXY_PREFIX, 1)[1]
    host, _, resto = caminho.partition("/")
    if host not in CDN_HOSTS or not resto:
        return ""
    resto = re.sub(r"_\d+_\d+(?:_\d+)?(?:_c\d+)?(\.\w+)$", r"\1", resto)
    return f"https://{host}/{resto}"


def imagens_candidatas(html: str, thumb: str) -> list[str]:
    """Candidatas de foto oficial, em ordem de preferência.

    O link `/Full/` da galeria às vezes aponta para um arquivo removido, e os
    modelos mais novos vivem em outro CDN (`pim.dynapac.com`). Por isso
    devolvemos uma lista e deixamos o downloader tentar em ordem.
    """
    candidatas: list[str] = []

    def add(url: str) -> None:
        if url and url not in candidatas and "/Measurements/" not in url:
            candidatas.append(url)

    add(origem_do_proxy(thumb))

    diretos = re.findall(r'href="(https://(?:pdf|pim)\.dynapac\.com/[^"]+\.(?:jpg|jpeg|png))"', html)
    for url in diretos:
        if "/Full/" in url:
            add(url)

    # Fotos servidas via redimensionador (inclui o CDN novo).
    for atributo in re.findall(r'(?:src|data-src)="([^"]+)"', html):
        origem = origem_do_proxy(atributo)
        if origem and "/Full/" in origem:
            add(origem)

    for url in diretos:
        add(url)
    for atributo in re.findall(r'(?:src|data-src)="([^"]+)"', html):
        add(origem_do_proxy(atributo))

    # Os dois CDNs espelham o mesmo acervo; quando um responde 404, o outro
    # costuma ter o arquivo. Fecha a lista com o espelho de cada candidata.
    for url in list(candidatas):
        add(url.replace("pdf.dynapac.com", "pim.dynapac.com")
            if "pdf.dynapac.com" in url
            else url.replace("pim.dynapac.com", "pdf.dynapac.com"))
    return candidatas[:6]


def parse_specs(html: str) -> dict[str, str]:
    """Lê as tabelas de características técnicas em pares rótulo -> valor."""
    brutas: dict[str, str] = {}
    for tabela in re.findall(r"<table.*?</table>", html, re.S):
        for linha in re.findall(r"<tr.*?</tr>", tabela, re.S):
            celulas = [strip_tags(c) for c in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", linha, re.S)]
            celulas = [c for c in celulas if c]
            if len(celulas) >= 2:
                rotulo, valor = celulas[0], " ".join(celulas[1:]).strip()
                if rotulo and valor and rotulo.lower() not in brutas:
                    brutas[rotulo.lower()] = valor
    return brutas


def selecionar_specs(brutas: dict[str, str], card_specs: dict[str, str]) -> dict[str, str]:
    """Monta a ficha final já com rótulos em português e sem repetições."""
    escolhidas: dict[str, str] = {}
    for chave, padroes in SPEC_PRIORIDADE:
        for padrao in padroes:
            achou = next((v for r, v in brutas.items() if re.search(padrao, r)), None)
            if achou:
                escolhidas[SPEC_LABELS[chave]] = normalizar_valor(achou)
                break

    for titulo, valor in card_specs.items():
        if len(escolhidas) >= 8:
            break
        rotulo = CARD_LABEL_PT.get(titulo.strip().lower(), titulo.strip())
        normalizado = normalizar_valor(valor)
        if rotulo in escolhidas:
            continue
        # "Largura de compactação" repetindo "Largura de trabalho", etc.
        if normalizado in escolhidas.values():
            continue
        escolhidas[rotulo] = normalizado

    # Descarta specs sem valor real (ex.: "Hz" ou "N/A" sozinhos).
    return {
        k: v for k, v in escolhidas.items()
        if re.search(r"\d", v) and v.strip().upper() not in {"N/A", "-"}
    }


def parse_destaques(html: str) -> list[str]:
    """Títulos do bloco 'Características e Benefícios' (texto real da Dynapac)."""
    inicio = html.find("Características e Benefícios")
    if inicio == -1:
        return []
    trecho = html[inicio : inicio + 30000]
    fim = trecho.find("Características técnicas")
    if fim > 0:
        trecho = trecho[:fim]
    destaques: list[str] = []
    for titulo in re.findall(r'<h5[^>]*class="features-title"[^>]*>(.*?)</h5>', trecho, re.S):
        texto = strip_tags(titulo)
        if texto and texto not in destaques:
            destaques.append(texto)
    return destaques[:4]


def buscar_spec(specs: dict[str, str], *padroes: str) -> str | None:
    for padrao in padroes:
        for rotulo, valor in specs.items():
            if re.search(padrao, rotulo, re.I):
                return valor
    return None


def montar_descricao(modelo: str, sub_slug: str, destaques: list[str], specs: dict[str, str]) -> str:
    base = SUBCATEGORIA_SINGULAR.get(sub_slug, "Equipamento")
    partes = [f"{base} Dynapac {modelo}"]

    peso = buscar_spec(specs, r"^peso operacional")
    e_pavimentadora = "pavimentadora" in base.lower()
    if e_pavimentadora:
        largura = buscar_spec(specs, r"largura b[áa]sica", r"largura m[áa]x", r"largura")
        rotulo_largura = "largura de pavimentação"
    else:
        largura = buscar_spec(specs, r"largura de trabalho", r"largura de compacta", r"largura")
        rotulo_largura = "largura de trabalho"

    medidas = []
    if peso:
        medidas.append(f"peso operacional de {peso}")
    if largura:
        medidas.append(f"{rotulo_largura} de {largura}")
    if not medidas:
        potencia = buscar_spec(specs, r"^pot[êe]ncia")
        if potencia:
            medidas.append(f"motor de {potencia}")
    if medidas:
        partes.append("com " + " e ".join(medidas))

    frase = " ".join(partes) + "."
    if destaques:
        frase += " Destaques: " + ", ".join(destaques[:3]) + "."
    return frase


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache-dir", default=str(REPO / ".tmp" / "dynapac-br"))
    ap.add_argument("--offline", action="store_true", help="usa apenas o cache local")
    ap.add_argument("--workers", type=int, default=4)
    args = ap.parse_args()
    cache = Path(args.cache_dir)

    print("[1/3] Baixando listagens do site nacional (dynapac.com/br-pt) ...")
    cards: list[dict] = []
    for cat_slug, url in LISTAGENS.items():
        html = fetch(url, cache, args.offline)
        itens = parse_listagem(html)
        for item in itens:
            item["categoria"] = cat_slug
        cards.extend(itens)
        print(f"  ✓ {CATEGORIA_NOMES[cat_slug]}: {len(itens)} cards ativos")

    # Normaliza subcategoria e descarta ignoradas / duplicados entre listagens.
    selecionados: dict[str, dict] = {}
    ignorados = 0
    for card in cards:
        bruta = card["subcategoria_bruta"].strip().lower()
        if bruta in SUBCATEGORIAS_IGNORADAS:
            ignorados += 1
            continue
        nome, slug = SUBCATEGORIA_CANONICA.get(bruta, (card["subcategoria_bruta"].strip(), slugify(bruta)))
        card["sub_nome"], card["sub_slug"] = nome, slug
        card["slug"] = slugify(card["modelo"])
        # O site nacional repete alguns modelos em duas listagens (ex.: F80W em
        # Pavimentação e Linha Leve). Mantemos apenas a primeira ocorrência para
        # não gerar duas páginas do mesmo equipamento.
        if card["slug"] not in selecionados:
            selecionados[card["slug"]] = card
    print(f"  ✓ {len(selecionados)} modelos únicos ({ignorados} cards de mesas/screeds ignorados)\n")

    print(f"[2/3] Baixando {len(selecionados)} fichas de produto ...")
    lista = list(selecionados.values())

    def enriquecer(card: dict) -> dict:
        html = fetch(card["url"], cache, args.offline)
        brutas = parse_specs(html)
        card["specs"] = selecionar_specs(brutas, card["card_specs"])
        card["destaques"] = parse_destaques(html)
        card["imagens"] = imagens_candidatas(html, card.get("thumb", ""))
        card["imagem_url"] = card["imagens"][0] if card["imagens"] else ""
        return card

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        for n, card in enumerate(pool.map(enriquecer, lista), 1):
            if n % 20 == 0 or n == len(lista):
                print(f"  ... {n}/{len(lista)}")

    print("\n[3/3] Montando data/dynapac-db.json ...")
    db = {
        "marca": "Dynapac",
        "fonte": "dynapac.com/br-pt (catálogo nacional; apenas modelos ativos)",
        "coletado_em": time.strftime("%Y-%m-%d"),
        "categorias": [],
    }
    downloads: list[dict] = []
    sem_imagem: list[str] = []

    for cat_slug, cat_nome in CATEGORIA_NOMES.items():
        da_categoria = [c for c in lista if c["categoria"] == cat_slug]
        subs: dict[str, dict] = {}
        for card in da_categoria:
            sub = subs.setdefault(
                card["sub_slug"], {"nome": card["sub_nome"], "slug": card["sub_slug"], "modelos": []}
            )
            sub["modelos"].append(
                {
                    "modelo": card["modelo"],
                    "nome_completo": f"Dynapac {card['modelo']}",
                    "descricao": montar_descricao(card["modelo"], card["sub_slug"], card["destaques"], card["specs"]),
                    "specs": card["specs"],
                    "imagem_url": card["imagem_url"],
                    "pagina_url": card["url"],
                    "slug": card["slug"],
                }
            )
            if card["imagens"]:
                downloads.append(
                    {
                        "url": card["imagens"][0],
                        "alternativas": card["imagens"][1:4],
                        "dest": f"{cat_slug}/{card['slug']}",
                    }
                )
            else:
                sem_imagem.append(f"{cat_slug}/{card['slug']}")

        ordenadas = sorted(
            subs.values(),
            key=lambda s: (ORDEM_SUBCATEGORIAS.index(s["slug"]) if s["slug"] in ORDEM_SUBCATEGORIAS else 99, s["nome"]),
        )
        for sub in ordenadas:
            sub["modelos"].sort(key=lambda m: m["slug"])
        db["categorias"].append({"nome": cat_nome, "slug": cat_slug, "subcategorias": ordenadas})
        total = sum(len(s["modelos"]) for s in ordenadas)
        print(f"  ✓ {cat_nome}: {total} modelos em {len(ordenadas)} subcategorias")

    (REPO / "data" / "dynapac-db.json").write_text(
        json.dumps(db, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (REPO / "data" / "dynapac-downloads.json").write_text(
        json.dumps(downloads, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    total = sum(len(s["modelos"]) for c in db["categorias"] for s in c["subcategorias"])
    print(f"\n✓ {total} modelos gravados · {len(downloads)} fotos na fila")
    if sem_imagem:
        print(f"  ! {len(sem_imagem)} sem imagem: {', '.join(sem_imagem[:8])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
