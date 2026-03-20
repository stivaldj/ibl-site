#!/usr/bin/env python3.11
"""
Gerador de páginas frontend - IBL Máquinas
Cria páginas estáticas seguindo a hierarquia do Scrape Case
Output: produtos/{cat}/index.html + produtos/{cat}/{model}/index.html
"""

import json
import os
import re
import shutil
from pathlib import Path
from urllib.parse import quote

BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / "Scrape Case" / "scrape_db.json"
OUT_DIR = BASE_DIR / "produtos"
WHATSAPP_NUMBER = "5567999999999"
WHATSAPP_BASE_URL = f"https://wa.me/{WHATSAPP_NUMBER}"
HOME_CONTACT_URL = "/#captacao-lead"


def build_whatsapp_url(message: str) -> str:
    return f"{WHATSAPP_BASE_URL}?text={quote(message)}"

# Cabeçalho HTML compartilhado (fontes, ícones, CSS)
HEAD_TEMPLATE = """\
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <script src="https://unpkg.com/@phosphor-icons/web"></script>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Archivo:wght@100..900&family=Inter:wght@300;400;500;600&family=JetBrains+Mono:wght@400;700&display=swap" rel="stylesheet" />
  <script type="module" src="/main.js"></script>
  <style>
    /* Prevent FOUC before JS/CSS loads */
    :root { background-color: #050505; color: #fff; }
  </style>"""

# Header de navegação (fixo)
HEADER_HTML = f"""\
    <header class="fixed top-0 w-full z-50 bg-case-dark/90 backdrop-blur-md border-b border-case-border">
      <div class="flex items-center justify-between h-20 px-6 max-w-[1920px] mx-auto">
        <div class="flex items-center gap-4">
          <a href="/"><img src="/ibl-logo.png" alt="IBL Máquinas" class="h-16 w-auto" /></a>
          <span class="font-mono text-[10px] text-case-yellow tracking-widest uppercase">Official Dealer</span>
        </div>
        <div class="hidden lg:flex items-center gap-12" role="navigation" aria-label="Navegação principal">
          <a href="/#catalogo" class="font-mono text-sm uppercase hover:text-case-yellow transition-colors flex items-center gap-2 group">
            <span class="w-1.5 h-1.5 bg-case-yellow rounded-full opacity-0 group-hover:opacity-100 transition-opacity"></span>
            Catálogo
          </a>
          <a href="/#tecnologia" class="font-mono text-sm uppercase hover:text-case-yellow transition-colors flex items-center gap-2 group">
            <span class="w-1.5 h-1.5 bg-case-yellow rounded-full opacity-0 group-hover:opacity-100 transition-opacity"></span>
            Tecnologia
          </a>
          <a href="/#posvenda" class="font-mono text-sm uppercase hover:text-case-yellow transition-colors flex items-center gap-2 group">
            <span class="w-1.5 h-1.5 bg-case-yellow rounded-full opacity-0 group-hover:opacity-100 transition-opacity"></span>
            Pós-Venda
          </a>
          <a href="/#unidades" class="font-mono text-sm uppercase hover:text-case-yellow transition-colors flex items-center gap-2 group">
            <span class="w-1.5 h-1.5 bg-case-yellow rounded-full opacity-0 group-hover:opacity-100 transition-opacity"></span>
            Unidades
          </a>
        </div>
        <div class="flex items-center gap-6">
          <div class="hidden md:flex items-center gap-2 text-xs font-mono text-gray-400">
            <span class="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
            TELEMETRIA ONLINE
          </div>
          <a href="{HOME_CONTACT_URL}" class="bg-white text-black hover:bg-case-yellow hover:text-black transition-colors px-6 py-2.5 font-bold uppercase text-xs tracking-widest border border-white">
            Solicitar Orçamento
          </a>
        </div>
      </div>
    </header>"""

# Footer compartilhado
FOOTER_HTML = f"""\
    <footer class="bg-case-yellow pt-16 pb-10 text-black">
      <div class="container mx-auto px-6">
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-12 mb-16 border-b border-black/10 pb-12">
          <div>
            <h2 class="font-display font-black text-5xl md:text-7xl tracking-tighter leading-[0.8]">WORK<br />WITH US</h2>
          </div>
          <div class="flex flex-col justify-end items-start lg:items-end">
            <p class="font-bold text-lg mb-6 max-w-sm lg:text-right">Entre em contato hoje mesmo e descubra como podemos ajudar.</p>
            <div class="generated-footer-actions flex gap-4">
              <a href="{build_whatsapp_url('Olá, quero falar com um especialista da IBL Máquinas sobre os modelos CASE.')}" target="_blank" rel="noopener noreferrer" class="px-8 py-3 bg-black text-white font-bold uppercase tracking-widest hover:bg-white hover:text-black transition-colors">Whatsapp</a>
              <a href="{HOME_CONTACT_URL}" class="px-8 py-3 border-2 border-black text-black font-bold uppercase tracking-widest hover:bg-black hover:text-white transition-colors">Formulário</a>
            </div>
          </div>
        </div>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-8 mb-12">
          <div>
            <div class="font-bold uppercase tracking-widest border-b border-black pb-2 mb-4 text-sm">Máquinas</div>
            <ul class="space-y-2 font-medium text-sm">
              <li><a href="/produtos/escavadeiras-hidraulicas/" class="hover:underline">Escavadeiras</a></li>
              <li><a href="/produtos/retroescavadeiras/" class="hover:underline">Retroescavadeiras</a></li>
              <li><a href="/produtos/pas-carregadeiras/" class="hover:underline">Pás Carregadeiras</a></li>
              <li><a href="/produtos/motoniveladoras/" class="hover:underline">Motoniveladoras</a></li>
              <li><a href="/produtos/tratores-de-esteiras/" class="hover:underline">Tratores</a></li>
            </ul>
          </div>
          <div>
            <div class="font-bold uppercase tracking-widest border-b border-black pb-2 mb-4 text-sm">Empresa</div>
            <ul class="space-y-2 font-medium text-sm">
              <li><a href="/" class="hover:underline">Página Inicial</a></li>
              <li><a href="/#unidades" class="hover:underline">Unidades IBL</a></li>
              <li><a href="/#tecnologia" class="hover:underline">Tecnologia CASE</a></li>
            </ul>
          </div>
          <div>
            <div class="font-bold uppercase tracking-widest border-b border-black pb-2 mb-4 text-sm">Suporte</div>
            <ul class="space-y-2 font-medium text-sm">
              <li><a href="/#posvenda" class="hover:underline">Pós-venda</a></li>
              <li><a href="{HOME_CONTACT_URL}" class="hover:underline">Solicitar suporte</a></li>
              <li><a href="{build_whatsapp_url('Olá, preciso de suporte comercial para equipamentos CASE.')}" target="_blank" rel="noopener noreferrer" class="hover:underline">Falar com especialista</a></li>
            </ul>
          </div>
          <div>
            <div class="font-bold uppercase tracking-widest border-b border-black pb-2 mb-4 text-sm">Social</div>
            <p class="font-medium text-sm leading-relaxed">Canais sociais em atualização para o lançamento.</p>
            <p class="font-mono text-[11px] uppercase tracking-widest mt-3 opacity-70">Atendimento ativo via WhatsApp e formulário.</p>
          </div>
        </div>
        <div class="flex flex-col md:flex-row justify-between items-center pt-8 border-t border-black/10 text-xs font-mono font-bold uppercase tracking-widest opacity-60">
          <p>© 2026 IBL Máquinas. All rights reserved.</p>
          <p>Case Construction Authorized Dealer</p>
        </div>
      </div>
    </footer>
    <div class="fixed bottom-8 right-8 z-50">
      <a href="{build_whatsapp_url('Olá, vim do catálogo CASE e quero falar com um consultor da IBL Máquinas.')}" target="_blank" rel="noopener noreferrer" aria-label="Falar com um consultor no WhatsApp" class="generated-floating-chat group relative w-16 h-16 bg-case-yellow hover:bg-white transition-all duration-300 flex items-center justify-center border-2 border-black shadow-2xl">
        <i class="generated-floating-chat__icon ph-fill ph-chats-circle text-3xl text-black group-hover:scale-110 transition-transform"></i>
        <span class="absolute -top-1 -right-1 w-4 h-4 bg-green-500 border-2 border-black rounded-full animate-pulse"></span>
      </a>
    </div>"""


# ─── Helpers de parsing do content.md ─────────────────────────────────────────

def parse_content_md(content: str) -> dict:
    """Extrai dados estruturados do content.md."""
    data = {
        "title": "",
        "category": "",
        "description": "",
        "summary_specs": {},
        "tech_groups": [],
        "assets_local": [],
    }

    lines = content.split("\n")
    section = None
    current_group = None
    group_items = []

    for line in lines:
        stripped = line.strip()

        if stripped.startswith("# "):
            data["title"] = stripped[2:].strip()
        elif stripped.startswith("**Categoria**: "):
            data["category"] = stripped.replace("**Categoria**: ", "").strip()
        elif stripped.startswith("## Descrição"):
            section = "descricao"
        elif stripped.startswith("## Especificações Rápidas"):
            section = "quick_specs"
        elif stripped.startswith("## Especificações Técnicas"):
            section = "tech_specs"
        elif stripped.startswith("## Assets Locais"):
            section = "assets"
        elif stripped.startswith("## "):
            section = None

        elif section == "descricao" and stripped and not stripped.startswith("#"):
            if data["description"]:
                data["description"] += " " + stripped
            else:
                data["description"] = stripped

        elif section == "quick_specs" and stripped.startswith("- **"):
            m = re.match(r"- \*\*(.+?)\*\*: (.+)", stripped)
            if m:
                data["summary_specs"][m.group(1).strip()] = m.group(2).strip()

        elif section == "tech_specs":
            if stripped.startswith("### "):
                if current_group and group_items:
                    data["tech_groups"].append({"group": current_group, "items": group_items})
                current_group = stripped[4:].strip()
                group_items = []
            elif stripped.startswith("- **") and current_group is not None:
                m = re.match(r"- \*\*(.+?)\*\*: (.+)", stripped)
                if m:
                    group_items.append({"key": m.group(1).strip(), "value": m.group(2).strip()})

        elif section == "assets" and stripped.startswith("- "):
            data["assets_local"].append(stripped[2:].strip())

    # Flush último grupo
    if current_group and group_items:
        data["tech_groups"].append({"group": current_group, "items": group_items})

    return data


def copy_assets(model_path_str: str, cat_slug: str, model_slug: str) -> list:
    """
    Copia assets do modelo para public/case-assets/{cat}/{model}/
    Retorna lista de paths públicos (/case-assets/...).
    """
    src_assets = BASE_DIR / model_path_str / "assets"
    if not src_assets.exists():
        return []

    dst_dir = BASE_DIR / "public" / "case-assets" / cat_slug / model_slug
    dst_dir.mkdir(parents=True, exist_ok=True)

    public_paths = []
    for asset_file in src_assets.iterdir():
        if asset_file.is_file():
            dst = dst_dir / asset_file.name
            if not dst.exists():
                shutil.copy2(asset_file, dst)
            public_paths.append(f"/case-assets/{cat_slug}/{model_slug}/{asset_file.name}")

    return public_paths


def get_cat_slug(model_path: str) -> str:
    parts = model_path.split("/")
    try:
        idx = parts.index("produtos")
        return parts[idx + 1]
    except (ValueError, IndexError):
        return ""


def get_model_slug(model_path: str) -> str:
    return model_path.split("/")[-1].lower()


# ─── Templates HTML ─────────────────────────────────────────────────────────────

def category_badge(cat: str) -> str:
    badges = {
        "escavadeiras-hidraulicas": "HEAVY LINE",
        "minicarregadeiras": "COMPACT LOADERS",
        "miniescavadeiras": "MINI SERIES",
        "motoniveladoras": "GRADING",
        "pas-carregadeiras": "LOADERS",
        "retroescavadeiras": "VERSATILITY",
        "rolo-compactador": "COMPACTION",
        "tratores-de-esteiras": "DOZING",
    }
    return badges.get(cat, cat.upper())


def render_breadcrumb(cat_name: str, cat_slug: str, model_title: str = None) -> str:
    crumbs = [
        '<li><a href="/" class="hover:text-case-yellow transition-colors">Home</a></li>',
        '<li aria-hidden="true"><i class="ph-bold ph-caret-right text-xs"></i></li>',
        f'<li><a href="/produtos/" class="hover:text-case-yellow transition-colors">Produtos</a></li>',
        '<li aria-hidden="true"><i class="ph-bold ph-caret-right text-xs"></i></li>',
    ]
    if model_title:
        crumbs.append(f'<li><a href="/produtos/{cat_slug}/" class="hover:text-case-yellow transition-colors">{cat_name}</a></li>')
        crumbs.append('<li aria-hidden="true"><i class="ph-bold ph-caret-right text-xs"></i></li>')
        crumbs.append(f'<li><span aria-current="page" class="text-white">{model_title}</span></li>')
    else:
        crumbs.append(f'<li><span aria-current="page" class="text-white">{cat_name}</span></li>')
    return f'<nav aria-label="Breadcrumb" data-breadcrumb-nav class="generated-breadcrumb flex items-center gap-2 text-xs font-mono text-gray-400"><ol class="flex flex-wrap items-center gap-2">{"".join(crumbs)}</ol></nav>'


def render_spec_groups_html(tech_groups: list) -> str:
    if not tech_groups:
        return ""

    groups_html = []
    for g in tech_groups:
        items_html = "".join(
            f"""<div class="flex items-start justify-between py-3 border-b border-case-border last:border-0 gap-4">
                  <span class="text-gray-400 text-sm font-mono flex-shrink-0 w-48">{item['key']}</span>
                  <span class="text-white text-sm text-right">{item['value']}</span>
                </div>"""
            for item in g["items"]
        )
        groups_html.append(f"""
        <div class="mb-8">
          <div class="flex items-center gap-3 mb-4">
            <div class="w-1 h-6 bg-case-yellow"></div>
            <h4 class="font-display font-black text-lg uppercase tracking-wider text-case-yellow">{g['group']}</h4>
          </div>
          <div class="bg-case-panel border border-case-border p-6">
            {items_html}
          </div>
        </div>""")

    return "\n".join(groups_html)


def render_summary_pills(specs: dict) -> str:
    if not specs:
        return ""
    pills = []
    for key, val in list(specs.items())[:4]:
        pills.append(f"""
        <div class="border border-case-border bg-case-panel px-6 py-4 flex flex-col gap-1">
          <span class="font-mono text-xs text-gray-500 uppercase tracking-widest">{key}</span>
          <span class="font-display font-black text-2xl text-case-yellow">{val}</span>
        </div>""")
    return "\n".join(pills)


# ─── Página de produto (ficha técnica) ─────────────────────────────────────────

def generate_product_page(model: dict, category: str, cat_slug: str) -> str:
    model_path = model["path"]
    model_slug = get_model_slug(model_path)
    content_path = BASE_DIR / model_path / "content.md"

    # Ler e parsear content.md
    if content_path.exists():
        content = content_path.read_text(encoding="utf-8")
        data = parse_content_md(content)
    else:
        data = {
            "title": model["title"],
            "category": category,
            "description": "",
            "summary_specs": {},
            "tech_groups": [],
            "assets_local": [],
        }

    title = data["title"] or model["title"]

    # Copiar assets para public/
    public_assets = copy_assets(model_path, cat_slug, model_slug)
    hero_img = public_assets[0] if public_assets else "https://images.unsplash.com/photo-1626296765727-4a4115f5732c?q=80&w=2670&auto=format&fit=crop"

    breadcrumb = render_breadcrumb(category, cat_slug, title)
    summary_pills = render_summary_pills(data["summary_specs"])
    spec_groups = render_spec_groups_html(data["tech_groups"])
    badge = category_badge(cat_slug)

    description_html = f'<p class="text-gray-300 text-lg leading-relaxed max-w-2xl">{data["description"]}</p>' if data["description"] else ""

    has_specs = bool(data["tech_groups"])
    specs_section = f"""
      <section class="py-24 bg-case-dark">
        <div class="container mx-auto px-6">
          <div class="mb-12">
            <span class="font-mono text-case-yellow text-sm tracking-widest uppercase block mb-2">/// Technical Data</span>
            <h2 class="font-display font-black text-4xl md:text-5xl uppercase">Especificações <span class="text-outline-yellow">Técnicas</span></h2>
          </div>
          <div class="grid grid-cols-1 lg:grid-cols-2 gap-12">
            {spec_groups}
          </div>
        </div>
      </section>""" if has_specs else ""

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
{HEAD_TEMPLATE}
  <title>{title} | IBL Máquinas - Case Construction</title>
</head>
<body class="antialiased tech-grid bg-case-dark text-white selection:bg-case-yellow selection:text-black">
{HEADER_HTML}

  <main class="pt-20">

    <!-- Breadcrumb -->
    <div class="bg-case-panel border-b border-case-border py-4 px-6">
      <div class="container mx-auto">
        {breadcrumb}
      </div>
    </div>

    <!-- Hero Produto -->
    <section class="relative border-b border-case-border overflow-hidden bg-case-dark">
      <div class="absolute inset-0 pointer-events-none">
        <div class="absolute top-0 left-1/4 h-full w-px bg-case-border"></div>
        <div class="absolute top-0 right-1/4 h-full w-px bg-case-border"></div>
        <div class="absolute top-[20%] left-[5%] w-[400px] h-[400px] bg-case-yellow/5 rounded-full blur-3xl"></div>
      </div>
      <div class="container mx-auto px-6 py-16 lg:py-24 relative z-10">
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
          <div class="lg:col-span-5 space-y-8">
            <div>
              <span class="inline-block px-3 py-1 bg-case-yellow/10 border border-case-yellow/30 font-mono text-xs text-case-yellow tracking-widest uppercase mb-4">{badge}</span>
              <h1 class="generated-product-title font-display font-black text-4xl md:text-5xl xl:text-6xl uppercase leading-tight">{title}</h1>
            </div>
            {description_html}
            <!-- Quick specs pills -->
            <div class="grid grid-cols-2 gap-3">
              {summary_pills}
            </div>
            <div class="generated-hero-actions flex gap-4 pt-4">
              <a href="{HOME_CONTACT_URL}" class="bg-case-yellow text-black px-8 py-4 font-bold uppercase tracking-widest hover:bg-white transition-colors flex items-center gap-3 text-sm">
                Solicitar Orçamento <i class="ph-bold ph-arrow-right"></i>
              </a>
              <a href="/produtos/{cat_slug}/" class="border border-case-border text-white px-8 py-4 font-bold uppercase tracking-widest hover:bg-white/10 transition-colors text-sm">
                ← Ver Categoria
              </a>
            </div>
          </div>
          <div class="lg:col-span-7 relative h-[400px] lg:h-[600px] flex items-center justify-center">
            <div class="absolute inset-0 flex items-center justify-center">
              <div class="w-full h-full relative overflow-hidden industrial-border">
                <img src="{hero_img}" alt="{title}" class="w-full h-full object-contain p-8 filter drop-shadow-2xl hover:scale-105 transition-transform duration-700" />
                <div class="absolute top-4 left-4 bg-black/80 border border-case-border px-3 py-1 font-mono text-xs text-case-yellow">
                  CASE CONSTRUCTION
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    {specs_section}

    <!-- CTA Final -->
    <section class="py-20 bg-case-gray border-t border-case-border">
      <div class="container mx-auto px-6 text-center">
        <span class="font-mono text-case-yellow text-sm tracking-widest uppercase block mb-4">/// IBL Máquinas</span>
        <h2 class="font-display font-black text-4xl md:text-5xl uppercase mb-6">Interessado no {title.split()[0]} {title.split()[1] if len(title.split()) > 1 else ''}?</h2>
        <p class="text-gray-400 mb-10 max-w-xl mx-auto">Nossa equipe especializada está pronta para apresentar uma proposta personalizada para sua operação.</p>
        <div class="flex flex-col sm:flex-row gap-4 justify-center">
          <a href="{HOME_CONTACT_URL}" class="bg-case-yellow text-black px-10 py-4 font-bold uppercase tracking-widest hover:bg-white transition-colors">
            Solicitar Orçamento
          </a>
          <a href="{build_whatsapp_url(f'Olá, tenho interesse no modelo {title}.')}" target="_blank" rel="noopener noreferrer" class="border border-case-border text-white px-10 py-4 font-bold uppercase tracking-widest hover:border-case-yellow transition-colors">
            Falar com Consultor
          </a>
        </div>
      </div>
    </section>

  </main>

{FOOTER_HTML}

</body>
</html>"""


# ─── Página de categoria ────────────────────────────────────────────────────────

def render_model_card(model: dict, cat_slug: str) -> str:
    model_path = model["path"]
    model_slug = get_model_slug(model_path)

    # Pegar imagem do modelo
    public_assets = copy_assets(model_path, cat_slug, model_slug)
    img_src = public_assets[0] if public_assets else "https://images.unsplash.com/photo-1626296765727-4a4115f5732c?q=80&w=800&auto=format&fit=crop"

    # Ler specs básicas do content.md
    content_path = BASE_DIR / model_path / "content.md"
    specs_html = ""
    if content_path.exists():
        content = content_path.read_text(encoding="utf-8")
        data = parse_content_md(content)
        if data["summary_specs"]:
            items = list(data["summary_specs"].items())[:2]
            specs_html = "".join(
                f'<div><span class="text-gray-500 text-xs font-mono block">{k}</span><span class="text-white text-sm font-bold">{v}</span></div>'
                for k, v in items
            )

    title = model["title"]
    short_title = title.split()[-1] if title else model_slug.upper()

    return f"""
            <a href="/produtos/{cat_slug}/{model_slug}/" class="group block">
              <div class="industrial-border h-[420px] bg-case-panel relative overflow-hidden flex flex-col justify-between p-6 hover-industrial cursor-pointer transition-all duration-300 hover:border-case-yellow/50">
                <div class="absolute top-0 right-0 p-3 z-10">
                  <i class="ph-bold ph-arrow-up-right text-xl opacity-0 group-hover:opacity-100 transition-opacity text-case-yellow"></i>
                </div>
                <div class="relative z-10">
                  <span class="inline-block px-2 py-1 bg-white/10 text-[10px] font-mono tracking-widest mb-3">{short_title}</span>
                </div>
                <div class="absolute inset-0 flex items-center justify-center">
                  <img src="{img_src}" alt="{title}"
                    class="w-[80%] max-w-none transition-transform duration-700 group-hover:scale-110 filter grayscale group-hover:grayscale-0 opacity-50 group-hover:opacity-90 object-contain" />
                </div>
                <div class="relative z-10 border-t border-case-border pt-4 mt-4">
                  <h3 class="font-display font-black text-xl uppercase leading-tight mb-3 group-hover:text-case-yellow transition-colors">{title}</h3>
                  <div class="flex justify-between items-end">
                    <div class="flex gap-6">
                      {specs_html}
                    </div>
                    <span class="text-case-yellow text-xs font-bold uppercase tracking-wider group-hover:translate-x-1 transition-transform">Ver Ficha →</span>
                  </div>
                </div>
              </div>
            </a>"""


def generate_category_page(cat_entry: dict) -> str:
    category = cat_entry["category"]
    models = cat_entry["models"]
    cat_slug = get_cat_slug(models[0]["path"]) if models else ""
    badge = category_badge(cat_slug)

    breadcrumb = render_breadcrumb(category, cat_slug)
    cards_html = "\n".join(render_model_card(m, cat_slug) for m in models)
    count = len(models)

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
{HEAD_TEMPLATE}
  <title>{category} | IBL Máquinas - Case Construction</title>
</head>
<body class="antialiased tech-grid bg-case-dark text-white selection:bg-case-yellow selection:text-black">
{HEADER_HTML}

  <main class="pt-20">

    <!-- Breadcrumb -->
    <div class="bg-case-panel border-b border-case-border py-4 px-6">
      <div class="container mx-auto">
        {breadcrumb}
      </div>
    </div>

    <!-- Hero categoria -->
    <section class="py-16 border-b border-case-border bg-case-dark relative overflow-hidden">
      <div class="absolute inset-0 pointer-events-none opacity-5"
           style="background-image: radial-gradient(#E58E1A 1px, transparent 1px); background-size: 30px 30px;"></div>
      <div class="container mx-auto px-6 relative z-10">
        <span class="font-mono text-case-yellow text-sm tracking-widest uppercase block mb-3">/// {badge}</span>
        <div class="flex flex-col md:flex-row justify-between items-start md:items-end gap-6">
          <h1 class="generated-category-title font-display font-black text-4xl sm:text-5xl md:text-7xl uppercase leading-none">
            {category.split()[0]}<br /><span class="text-outline">{" ".join(category.split()[1:]) or "&nbsp;"}</span>
          </h1>
          <div class="flex items-center gap-4 text-sm font-mono text-gray-400">
            <span class="border border-case-border px-4 py-2">{count} MODELOS DISPONÍVEIS</span>
          </div>
        </div>
      </div>
    </section>

    <!-- Grid de modelos -->
    <section class="py-20 bg-case-dark">
      <div class="container mx-auto px-6">
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {cards_html}
        </div>
      </div>
    </section>

    <!-- CTA -->
    <section class="py-16 bg-case-gray border-t border-case-border">
      <div class="container mx-auto px-6 flex flex-col md:flex-row justify-between items-center gap-8">
        <div>
          <h3 class="font-display font-black text-3xl uppercase">Não encontrou o que precisa?</h3>
          <p class="text-gray-400 mt-2">Nossa equipe pode te ajudar a encontrar o equipamento ideal.</p>
        </div>
        <a href="{build_whatsapp_url(f'Olá, preciso de ajuda para escolher um equipamento da linha {category}.')}" target="_blank" rel="noopener noreferrer" class="bg-case-yellow text-black px-10 py-4 font-bold uppercase tracking-widest hover:bg-white transition-colors flex-shrink-0">
          Falar com Consultor
        </a>
      </div>
    </section>

  </main>

{FOOTER_HTML}

</body>
</html>"""


# ─── Página índice de todos os produtos ─────────────────────────────────────────

def generate_products_index(db: list) -> str:
    cat_cards = []
    icons = {
        "escavadeiras-hidraulicas": "ph-fill ph-tractor",
        "minicarregadeiras": "ph-fill ph-truck",
        "miniescavadeiras": "ph-fill ph-tractor",
        "motoniveladoras": "ph-fill ph-road-horizon",
        "pas-carregadeiras": "ph-fill ph-truck",
        "retroescavadeiras": "ph-fill ph-tractor",
        "rolo-compactador": "ph-fill ph-circle-dashed",
        "tratores-de-esteiras": "ph-fill ph-tractor",
    }

    for i, cat in enumerate(db):
        category = cat["category"]
        models = cat["models"]
        cat_slug = get_cat_slug(models[0]["path"]) if models else ""
        badge = category_badge(cat_slug)
        count = len(models)
        icon = icons.get(cat_slug, "ph-fill ph-wrench")
        num = str(i + 1).zfill(2)

        # Pegar imagem do primeiro modelo
        first_model = models[0]
        first_slug = get_model_slug(first_model["path"])
        public_assets = copy_assets(first_model["path"], cat_slug, first_slug)
        img = public_assets[0] if public_assets else ""
        img_html = f'<img src="{img}" alt="{category}" class="w-full h-full object-contain p-6 filter grayscale group-hover:grayscale-0 opacity-40 group-hover:opacity-90 transition-all duration-500" />' if img else ""

        cat_cards.append(f"""
          <a href="/produtos/{cat_slug}/" class="group block">
            <div class="industrial-border h-[360px] bg-case-panel relative overflow-hidden flex flex-col justify-between p-8 hover-industrial cursor-pointer">
              <div class="absolute top-0 right-0 p-4 z-10">
                <i class="ph-bold ph-arrow-up-right text-2xl opacity-0 group-hover:opacity-100 transition-opacity text-case-yellow"></i>
              </div>
              <div class="relative z-10 flex items-start justify-between">
                <div>
                  <span class="font-mono text-xs text-case-yellow tracking-widest">{num}</span>
                  <div class="mt-2">
                    <i class="{icon} text-3xl text-white/20 group-hover:text-case-yellow transition-colors"></i>
                  </div>
                </div>
                <span class="inline-block px-2 py-1 bg-white/10 text-[10px] font-mono tracking-widest">{badge}</span>
              </div>
              <div class="absolute inset-0 flex items-center justify-center">
                {img_html}
              </div>
              <div class="relative z-10 border-t border-case-border pt-4">
                <h3 class="font-display font-black text-2xl uppercase leading-none mb-2 group-hover:text-case-yellow transition-colors">{category}</h3>
                <div class="flex justify-between items-center">
                  <span class="text-gray-500 text-xs font-mono">{count} modelos</span>
                  <span class="text-case-yellow text-xs font-bold uppercase tracking-wider group-hover:translate-x-1 transition-transform">Ver linha →</span>
                </div>
              </div>
            </div>
          </a>""")

    cards_html = "\n".join(cat_cards)
    total_models = sum(len(c["models"]) for c in db)

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
{HEAD_TEMPLATE}
  <title>Produtos | IBL Máquinas - Case Construction</title>
</head>
<body class="antialiased tech-grid bg-case-dark text-white selection:bg-case-yellow selection:text-black">
{HEADER_HTML}

  <main class="pt-20">

    <!-- Hero -->
    <section class="py-20 border-b border-case-border bg-case-dark relative overflow-hidden">
      <div class="absolute inset-0 pointer-events-none">
        <div class="absolute top-[20%] left-[10%] w-[500px] h-[500px] bg-case-yellow/5 rounded-full blur-3xl"></div>
      </div>
      <div class="container mx-auto px-6 relative z-10">
        <span class="font-mono text-case-yellow text-sm tracking-widest uppercase block mb-4">/// Inventory</span>
        <h1 class="font-display font-black text-6xl md:text-8xl uppercase leading-none">
          Nossa<br /><span class="text-outline">Frota</span>
        </h1>
        <div class="flex items-center gap-8 mt-8 text-sm font-mono text-gray-400">
          <span class="border border-case-border px-4 py-2">{len(db)} CATEGORIAS</span>
          <span class="border border-case-border px-4 py-2">{total_models} MODELOS</span>
          <span class="border border-case-border px-4 py-2">CASE CONSTRUCTION</span>
        </div>
      </div>
    </section>

    <!-- Grid de categorias -->
    <section class="py-24 bg-case-dark">
      <div class="container mx-auto px-6">
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {cards_html}
        </div>
      </div>
    </section>

  </main>

{FOOTER_HTML}

</body>
</html>"""


# ─── Main ───────────────────────────────────────────────────────────────────────

def main():
    print("=== GERANDO PÁGINAS FRONTEND ===\n")

    db = json.loads(DB_PATH.read_text(encoding="utf-8"))

    # Garantir que o diretório de saída existe
    OUT_DIR.mkdir(exist_ok=True)
    (BASE_DIR / "public" / "case-assets").mkdir(parents=True, exist_ok=True)

    total_pages = 0

    # 1. Página índice /produtos/index.html
    print("[1/N] Gerando /produtos/index.html ...")
    idx_html = generate_products_index(db)
    (OUT_DIR / "index.html").write_text(idx_html, encoding="utf-8")
    total_pages += 1
    print("  ✓ produtos/index.html")

    # 2. Páginas de categoria e produto
    for cat_entry in db:
        category = cat_entry["category"]
        models = cat_entry["models"]
        if not models:
            continue
        cat_slug = get_cat_slug(models[0]["path"])
        cat_dir = OUT_DIR / cat_slug
        cat_dir.mkdir(exist_ok=True)

        # Página de categoria
        print(f"\n[{category}] Gerando página de categoria ...")
        cat_html = generate_category_page(cat_entry)
        (cat_dir / "index.html").write_text(cat_html, encoding="utf-8")
        total_pages += 1
        print(f"  ✓ produtos/{cat_slug}/index.html")

        # Páginas de produto
        for model in models:
            model_slug = get_model_slug(model["path"])
            model_dir = cat_dir / model_slug
            model_dir.mkdir(exist_ok=True)

            print(f"  Gerando {model['title']} ...")
            prod_html = generate_product_page(model, category, cat_slug)
            (model_dir / "index.html").write_text(prod_html, encoding="utf-8")
            total_pages += 1
            print(f"  ✓ produtos/{cat_slug}/{model_slug}/index.html")

    print(f"\n=== {total_pages} páginas geradas em /produtos/ ===")
    print("\nPróximo passo: atualize tailwind.config.js para incluir os novos HTMLs")
    print("  content: ['./index.html', './produtos/**/*.html', './src/**/*.{js,ts,jsx,tsx}']")


if __name__ == "__main__":
    main()
