#!/usr/bin/env python3.11
"""
Gerador de páginas frontend - IBL Máquinas
Cria páginas estáticas seguindo a hierarquia do Scrape Case
Output: case/{cat}/index.html + case/{cat}/{model}/index.html
"""

import json
import os
import re
import shutil
from html import escape
from pathlib import Path
from typing import Optional
from urllib.parse import quote

BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / "Scrape Case" / "scrape_db.json"
OUT_DIR = BASE_DIR / "case"
SITE_URL = "https://iblmaquinas.com.br"
SITE_NAME = "IBL Máquinas"
SITE_BRAND = "CASE Construction"
DEFAULT_OG_IMAGE = f"{SITE_URL}/og-image.jpg"
# Número WhatsApp comercial (E.164 sem "+"). Mesmo env var usado pelo Vite (main.js).
# Número WhatsApp Business confirmado pela IBL em 2026-07-29.
WHATSAPP_NUMBER = os.environ.get("VITE_WHATSAPP_NUMBER", "5565999808288")
WHATSAPP_BASE_URL = f"https://wa.me/{WHATSAPP_NUMBER}"
HOME_CONTACT_URL = "/#captacao-lead"
ZERO_WIDTH_CHARS = {
    "\u200b",  # zero-width space
    "\u200c",  # zero-width non-joiner
    "\u200d",  # zero-width joiner
    "\ufeff",  # BOM / zero-width no-break space
}
# Modelos fora do portfólio do site (decisão IBL 2026-08-10): escavadeiras acima da CX350C
EXCLUDED_MODEL_SLUGS = {"cx370c-me", "cx490c", "cx500c", "cx800b"}

GENERATED_DERIVATIVE_PATTERN = re.compile(r".+-nobg\.png$|.+\.webp$", re.IGNORECASE)

# Otimização de imagens: acima deste tamanho, um derivativo .webp é gerado e
# preferido nas páginas (o original permanece como fonte do derivativo).
WEBP_THRESHOLD_BYTES = 250 * 1024
WEBP_MAX_DIM = 1400


def ensure_webp_derivative(image_path: "Path") -> "Path | None":
    """Gera (se necessário) um derivativo .webp para imagens pesadas.

    Retorna o caminho do .webp quando ele existe/foi gerado, senão None.
    Degrada silenciosamente se o Pillow não estiver disponível.
    """
    if image_path.suffix.lower() not in {".png", ".jpg", ".jpeg"}:
        return None
    try:
        if image_path.stat().st_size < WEBP_THRESHOLD_BYTES:
            return None
    except OSError:
        return None

    webp_path = image_path.with_suffix(".webp")
    try:
        if webp_path.exists() and webp_path.stat().st_mtime_ns >= image_path.stat().st_mtime_ns:
            return webp_path
    except OSError:
        pass

    try:
        from PIL import Image
    except ImportError:
        print("  ! Pillow indisponível — derivativos .webp não gerados")
        return webp_path if webp_path.exists() else None

    try:
        with Image.open(image_path) as img:
            has_alpha = img.mode in ("RGBA", "LA") or (
                img.mode == "P" and "transparency" in img.info
            )
            img = img.convert("RGBA" if has_alpha else "RGB")
            img.thumbnail((WEBP_MAX_DIM, WEBP_MAX_DIM), Image.LANCZOS)
            img.save(webp_path, "WEBP", quality=80 if has_alpha else 75, method=6)
        return webp_path
    except Exception as exc:  # noqa: BLE001 — otimização nunca deve quebrar o build
        print(f"  ! Falha ao gerar webp de {image_path.name}: {exc}")
        return None


def build_whatsapp_url(message: str) -> str:
    return f"{WHATSAPP_BASE_URL}?text={quote(message)}"


def clean_text(value: str) -> str:
    """Normalize whitespace and strip invisible formatting artifacts."""
    if not value:
        return ""

    cleaned = "".join(ch for ch in value if ch not in ZERO_WIDTH_CHARS)
    cleaned = re.sub(r"\s+", " ", cleaned, flags=re.UNICODE)
    return cleaned.strip()


def iter_sorted_files(path: Path) -> list[Path]:
    return sorted(
        (candidate for candidate in path.iterdir() if candidate.is_file()),
        key=lambda candidate: candidate.name.lower(),
    )


def is_managed_generated_derivative(path: Path) -> bool:
    return GENERATED_DERIVATIVE_PATTERN.fullmatch(path.name) is not None

# Cabeçalho HTML compartilhado (fontes, ícones, CSS)
HEAD_ASSETS_TEMPLATE = """\
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <script>try{var t=localStorage.getItem("ibl_theme");if(t)document.documentElement.dataset.theme=t}catch(e){}</script>
  <meta name="ibl-build" content="v3.6-20260810-2231" />
  <link rel="icon" href="/favicon.ico" />
  <link rel="apple-touch-icon" href="/apple-touch-icon.png" />
  <link rel="stylesheet" href="/vendor/phosphor/bold.css" />
  <link rel="stylesheet" href="/vendor/phosphor/fill.css" />
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Archivo:wght@100..900&family=Inter:wght@300;400;500;600&family=JetBrains+Mono:wght@400;700&display=swap" rel="stylesheet" />
  <script type="module" src="/main.js"></script>
  <style>
    /* Prevent FOUC before JS/CSS loads */
    :root { background-color: #050505; color: #fff; } :root[data-theme="light"] { background-color: #f4f2ed; color: #171717; }
  </style>"""

DEFAULT_DESCRIPTION = (
    "IBL Máquinas, distribuidor oficial CASE Construction com catálogo completo, "
    "suporte técnico especializado e pós-venda regional."
)

# Header de navegação (fixo)
HEADER_HTML = f"""\
    <header class="fixed top-0 w-full z-50 bg-case-dark/90 backdrop-blur-md border-b border-case-border">
      <div class="flex items-center justify-between h-20 px-6 max-w-[1920px] mx-auto">
        <div class="flex items-center gap-4">
          <a href="/" class="site-brand-link"><img src="/ibl-logo.png" alt="IBL Máquinas" class="h-16 w-auto" /></a>
          <span class="font-mono text-[10px] text-case-yellow tracking-widest uppercase">Concessionária Autorizada</span>
        </div>
        <nav class="hidden lg:flex items-center gap-12" aria-label="Navegação principal">
          <a href="/case/" class="font-mono text-sm uppercase hover:text-case-yellow transition-colors flex items-center gap-2 group">
            <span class="w-1.5 h-1.5 bg-case-yellow rounded-full opacity-0 group-hover:opacity-100 transition-opacity"></span>
            CASE
          </a>
          <a href="/dynapac/" class="font-mono text-sm uppercase hover:text-case-yellow transition-colors flex items-center gap-2 group">
            <span class="w-1.5 h-1.5 bg-case-yellow rounded-full opacity-0 group-hover:opacity-100 transition-opacity"></span>
            Dynapac
          </a>
          <a href="/filiais/" class="font-mono text-sm uppercase hover:text-case-yellow transition-colors flex items-center gap-2 group">
            <span class="w-1.5 h-1.5 bg-case-yellow rounded-full opacity-0 group-hover:opacity-100 transition-opacity"></span>
            Unidades
          </a>
          <a href="/consorcio/" class="font-mono text-sm uppercase hover:text-case-yellow transition-colors flex items-center gap-2 group">
            <span class="w-1.5 h-1.5 bg-case-yellow rounded-full opacity-0 group-hover:opacity-100 transition-opacity"></span>
            Consórcio
          </a>
        </nav>
        <div class="flex items-center gap-6">
          <details class="mobile-nav lg:hidden">
            <summary class="mobile-nav-toggle" aria-label="Abrir navegação principal">
              <span>Menu</span>
              <i class="ph-bold ph-list text-lg"></i>
            </summary>
            <nav class="mobile-nav-panel" aria-label="Navegação principal móvel">
              <a href="/case/" class="mobile-nav-link">CASE</a>
              <a href="/dynapac/" class="mobile-nav-link">Dynapac</a>
              <a href="/filiais/" class="mobile-nav-link">Unidades</a>
              <a href="/consorcio/" class="mobile-nav-link">Consórcio</a>
            </nav>
          </details>
          <div class="hidden md:flex items-center gap-2 text-xs font-mono text-gray-400">
            <span class="w-2 h-2 bg-case-yellow rounded-full"></span>
            8 LOJAS · 6 ESTADOS
          </div>
          <button type="button" data-theme-toggle class="w-10 h-10 flex items-center justify-center border border-case-border text-gray-400 hover:text-case-yellow hover:border-case-yellow transition-colors" aria-label="Alternar tema"><i class="ph-bold ph-sun text-lg"></i></button>
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
            <h2 class="font-display font-black text-5xl md:text-7xl tracking-tighter leading-[0.9]">FALE<br />COM A IBL</h2>
          </div>
          <div class="flex flex-col justify-end items-start lg:items-end">
            <p class="font-bold text-lg mb-6 max-w-sm lg:text-right">Especifique sua próxima máquina com apoio comercial, cobertura regional e resposta rápida da IBL.</p>
            <div class="generated-footer-actions flex gap-4">
              <a href="{build_whatsapp_url('Olá, quero falar com um especialista da IBL Máquinas.')}" target="_blank" rel="noopener noreferrer" class="px-8 py-3 bg-black text-white font-bold uppercase tracking-widest hover:bg-white hover:text-black transition-colors">Whatsapp</a>
              <a href="{HOME_CONTACT_URL}" class="px-8 py-3 border-2 border-black text-black font-bold uppercase tracking-widest hover:bg-black hover:text-white transition-colors">Formulário</a>
            </div>
          </div>
        </div>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-8 mb-12">
          <div>
            <div class="font-bold uppercase tracking-widest border-b border-black pb-2 mb-4 text-sm">CASE Construction</div>
            <ul class="space-y-2 font-medium text-sm">
              <li><a href="/case/escavadeiras-hidraulicas/" class="hover:underline">Escavadeiras</a></li>
              <li><a href="/case/retroescavadeiras/" class="hover:underline">Retroescavadeiras</a></li>
              <li><a href="/case/pas-carregadeiras/" class="hover:underline">Pás Carregadeiras</a></li>
              <li><a href="/case/catalogo/" class="hover:underline">Catálogo completo</a></li>
            </ul>
            <div class="font-bold uppercase tracking-widest border-b border-black pb-2 mb-4 mt-6 text-sm">Dynapac</div>
            <ul class="space-y-2 font-medium text-sm">
              <li><a href="/dynapac/compactacao/" class="hover:underline">Compactação</a></li>
              <li><a href="/dynapac/pavimentacao/" class="hover:underline">Pavimentação</a></li>
              <li><a href="/dynapac/equipamentos-leves/" class="hover:underline">Linha Leve</a></li>
            </ul>
          </div>
          <div>
            <div class="font-bold uppercase tracking-widest border-b border-black pb-2 mb-4 text-sm">Empresa</div>
            <ul class="space-y-2 font-medium text-sm">
              <li><a href="/" class="hover:underline">Página Inicial</a></li>
              <li><a href="/sobre/" class="hover:underline">Sobre nós</a></li>
              <li><a href="/filiais/" class="hover:underline">Nossas Filiais</a></li>
              <li><a href="/contato/" class="hover:underline">Contato</a></li>
              <li><a href="/consorcio/" class="hover:underline">Consórcio CASE</a></li>
              <li><a href="/#tecnologia" class="hover:underline">Tecnologia CASE</a></li>
            </ul>
          </div>
          <div>
            <div class="font-bold uppercase tracking-widest border-b border-black pb-2 mb-4 text-sm">Suporte</div>
            <ul class="space-y-2 font-medium text-sm">
              <li><a href="/#posvenda" class="hover:underline">Pós-venda</a></li>
              <li><a href="{HOME_CONTACT_URL}" class="hover:underline">Solicitar suporte</a></li>
              <li><a href="{build_whatsapp_url('Olá, preciso de suporte comercial da IBL Máquinas.')}" target="_blank" rel="noopener noreferrer" class="hover:underline">Falar com especialista</a></li>
            </ul>
          </div>
          <div>
            <div class="font-bold uppercase tracking-widest border-b border-black pb-2 mb-4 text-sm">Social</div>
            <ul class="space-y-2 font-medium text-sm">
              <li><a href="https://www.instagram.com/iblmaquinas/" target="_blank" rel="noopener noreferrer" class="hover:underline">Instagram</a></li>
              <li><a href="/privacidade/" class="hover:underline">Política de Privacidade</a></li>
            </ul>
            <p class="font-mono text-[11px] uppercase tracking-widest mt-3 opacity-70">Atendimento ativo via WhatsApp e formulário.</p>
          </div>
        </div>
        <div class="flex flex-col md:flex-row justify-between items-center gap-2 pt-8 border-t border-black/10 text-xs font-mono font-bold uppercase tracking-widest opacity-60">
          <p>© 2026 IBL Máquinas — Racine Comércio de Máquinas Ltda · CNPJ 28.265.622/0001-60</p>
          <p>CASE Construction &amp; Dynapac — Concessionária Autorizada</p>
        </div>
      </div>
    </footer>
    <div class="fixed bottom-8 right-8 z-50">
      <a href="{build_whatsapp_url('Olá, vim do site da IBL Máquinas e quero falar com um consultor.')}" target="_blank" rel="noopener noreferrer" aria-label="Falar com um consultor no WhatsApp" class="generated-floating-chat group relative w-16 h-16 bg-case-yellow hover:bg-white transition-all duration-300 flex items-center justify-center border-2 border-black shadow-2xl">
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
    current_item = None

    for line in lines:
        stripped = line.strip()
        cleaned = clean_text(stripped)

        if cleaned.startswith("# "):
            data["title"] = clean_text(cleaned[2:])
        elif cleaned.startswith("**Categoria**: "):
            data["category"] = clean_text(cleaned.replace("**Categoria**: ", "", 1))
        elif cleaned.startswith("## Descrição"):
            section = "descricao"
            current_item = None
        elif cleaned.startswith("## Especificações Rápidas"):
            section = "quick_specs"
            current_item = None
        elif cleaned.startswith("## Especificações Técnicas"):
            section = "tech_specs"
            current_item = None
        elif cleaned.startswith("## Assets Locais"):
            section = "assets"
        elif cleaned.startswith("## "):
            section = None
            current_item = None

        elif section == "descricao" and cleaned and not cleaned.startswith("#"):
            if data["description"]:
                data["description"] += " " + cleaned
            else:
                data["description"] = cleaned

        elif section == "quick_specs" and cleaned.startswith("- **"):
            m = re.match(r"- \*\*(.+?)\*\*: (.+)", cleaned)
            if m:
                current_item = clean_text(m.group(1))
                data["summary_specs"][current_item] = clean_text(m.group(2))
        elif section == "quick_specs" and current_item and cleaned and not cleaned.startswith("#"):
            data["summary_specs"][current_item] = clean_text(f"{data['summary_specs'][current_item]} {cleaned}")

        elif section == "tech_specs":
            if cleaned.startswith("### "):
                if current_group and group_items:
                    data["tech_groups"].append({"group": current_group, "items": group_items})
                current_group = clean_text(cleaned[4:])
                group_items = []
                current_item = None
            elif cleaned.startswith("- **") and current_group is not None:
                m = re.match(r"- \*\*(.+?)\*\*: (.+)", cleaned)
                if m:
                    current_item = {
                        "key": clean_text(m.group(1)),
                        "value": clean_text(m.group(2)),
                    }
                    group_items.append(current_item)
            elif current_item is not None and cleaned and not cleaned.startswith("#"):
                current_item["value"] = clean_text(f"{current_item['value']} {cleaned}")

        elif section == "assets" and cleaned.startswith("- "):
            data["assets_local"].append(clean_text(cleaned[2:]))

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

    source_files = iter_sorted_files(src_assets)
    managed_source_names = {asset_file.name for asset_file in source_files}
    managed_derivative_names = {
        asset_file.name
        for asset_file in iter_sorted_files(dst_dir)
        if is_managed_generated_derivative(asset_file)
    }

    for existing_file in iter_sorted_files(dst_dir):
        if existing_file.name in managed_source_names:
            continue
        if existing_file.name in managed_derivative_names:
            continue
        try:
            existing_file.unlink()
        except OSError as exc:
            print(f"  ! Não foi possível remover {existing_file.name}: {exc}")

    public_paths = []
    for asset_file in source_files:
        dst = dst_dir / asset_file.name
        if not dst.exists() or asset_file.stat().st_mtime_ns > dst.stat().st_mtime_ns:
            shutil.copy2(asset_file, dst)
        webp = ensure_webp_derivative(dst)
        public_name = webp.name if webp is not None else asset_file.name
        public_paths.append(f"/case-assets/{cat_slug}/{model_slug}/{public_name}")

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

def find_card_image(cat_slug: str, model_slug: str):
    """Card de modelo: foto ambientada curada ({slug}-card.webp) tem prioridade;
    senão recorte nobg. Retorna (caminho_publico|None, eh_foto)."""
    base = BASE_DIR / "public" / "case-assets" / cat_slug / model_slug
    card = base / f"{model_slug}-card.webp"
    if card.exists():
        return f"/case-assets/{cat_slug}/{model_slug}/{card.name}", True
    nobg = find_nobg_image(cat_slug, model_slug)
    return nobg, False


def find_nobg_image(cat_slug: str, model_slug: str = None):
    """Prefere o derivativo curado *-nobg.png (máquina recortada) para cards."""
    base = BASE_DIR / "public" / "case-assets" / cat_slug
    if model_slug:
        base = base / model_slug
    if not base.exists():
        return None
    matches = sorted(base.rglob("*-nobg.webp")) or sorted(base.rglob("*-nobg.png"))
    if not matches:
        return None
    rel = matches[0].relative_to(BASE_DIR / "public")
    return "/" + str(rel).replace("\\", "/")


def category_badge(cat: str) -> str:
    badges = {
        "escavadeiras-hidraulicas": "LINHA PESADA",
        "minicarregadeiras": "COMPACTAS",
        "miniescavadeiras": "MINI SÉRIE",
        "motoniveladoras": "NIVELAMENTO",
        "pas-carregadeiras": "CARREGADEIRAS",
        "retroescavadeiras": "VERSATILIDADE",
        "rolo-compactador": "COMPACTAÇÃO",
        "tratores-de-esteiras": "ESTEIRAS",
    }
    return badges.get(cat, cat.upper())


def truncate_text(text: str, max_length: int = 160) -> str:
    normalized = clean_text(text)
    if len(normalized) <= max_length:
        return normalized

    truncated = normalized[: max_length - 1].rsplit(" ", 1)[0].strip()
    return f"{truncated}…"


def build_meta_description(prefix: str, body: str, suffix: str, max_length: int = 160) -> str:
    """Monta uma meta description que já cabe em `max_length`.

    Evita a truncagem dupla (aqui e em `render_head`) que deixava reticências no
    meio da frase. Prefere encerrar o corpo na primeira frase completa.
    """
    budget = max_length - len(prefix) - len(suffix)
    normalized = clean_text(body)
    if budget <= 0:
        return truncate_text(f"{prefix}{normalized}", max_length)

    first_sentence = normalized.split(". ")[0].rstrip(".").strip()
    if first_sentence and len(first_sentence) + 1 <= budget:
        core = f"{first_sentence}."
    else:
        core = truncate_text(normalized, budget)
    return f"{prefix}{core}{suffix}"


def make_absolute_url(path: str) -> str:
    if not path:
        return SITE_URL
    if path.startswith("http://") or path.startswith("https://"):
        return path
    if not path.startswith("/"):
        path = f"/{path}"
    return f"{SITE_URL}{path}"


def build_page_title(page_name: str, brand: str = SITE_BRAND) -> str:
    return f"{page_name} | {SITE_NAME} - {brand}"


def render_json_ld(schema_objects: list[dict]) -> str:
    return "\n".join(
        f'  <script type="application/ld+json">{json.dumps(schema, ensure_ascii=False, separators=(",", ":"))}</script>'
        for schema in schema_objects
    )


def build_breadcrumb_schema(items: list[tuple[str, str]]) -> dict:
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": idx + 1,
                "name": name,
                "item": make_absolute_url(path),
            }
            for idx, (name, path) in enumerate(items)
        ],
    }


def build_item_list(items: list[tuple[str, str]]) -> dict:
    return {
        "@type": "ItemList",
        "numberOfItems": len(items),
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": idx + 1,
                "name": name,
                "url": make_absolute_url(path),
            }
            for idx, (name, path) in enumerate(items)
        ],
    }


def render_head(
    *,
    page_name: str,
    description: str,
    canonical_path: str,
    og_image: Optional[str] = None,
    schema_objects: Optional[list[dict]] = None,
    og_type: str = "website",
    brand: str = SITE_BRAND,
) -> str:
    page_title = build_page_title(page_name, brand)
    meta_description = truncate_text(description or DEFAULT_DESCRIPTION)
    canonical_url = make_absolute_url(canonical_path)
    image_url = make_absolute_url(og_image or DEFAULT_OG_IMAGE)
    schema_html = render_json_ld(schema_objects or [])

    return f"""\
{HEAD_ASSETS_TEMPLATE}
  <meta name="description" content="{escape(meta_description, quote=True)}" />
  <meta property="og:title" content="{escape(page_title, quote=True)}" />
  <meta property="og:description" content="{escape(meta_description, quote=True)}" />
  <meta property="og:type" content="{escape(og_type, quote=True)}" />
  <meta property="og:url" content="{escape(canonical_url, quote=True)}" />
  <meta property="og:image" content="{escape(image_url, quote=True)}" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="{escape(page_title, quote=True)}" />
  <meta name="twitter:description" content="{escape(meta_description, quote=True)}" />
  <meta name="twitter:image" content="{escape(image_url, quote=True)}" />
  <link rel="canonical" href="{escape(canonical_url, quote=True)}" />
  <title>{escape(page_title)}</title>
{schema_html}"""


def render_breadcrumb(cat_name: str, cat_slug: str, model_title: str = None) -> str:
    crumbs = [
        '<li><a href="/" class="hover:text-case-yellow transition-colors">Home</a></li>',
        '<li aria-hidden="true"><i class="ph-bold ph-caret-right text-xs"></i></li>',
        f'<li><a href="/case/" class="hover:text-case-yellow transition-colors">CASE</a></li>',
        '<li aria-hidden="true"><i class="ph-bold ph-caret-right text-xs"></i></li>',
    ]
    if model_title:
        crumbs.append(f'<li><a href="/case/{cat_slug}/" class="hover:text-case-yellow transition-colors">{cat_name}</a></li>')
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
            <h3 class="font-display font-black text-lg uppercase tracking-wider text-case-yellow">{g['group']}</h3>
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


def build_product_cta_heading(title: str) -> str:
    return f"Interessado em {title}?"


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
    hero_img = public_assets[0] if public_assets else DEFAULT_OG_IMAGE

    breadcrumb = render_breadcrumb(category, cat_slug, title)
    summary_pills = render_summary_pills(data["summary_specs"])
    spec_groups = render_spec_groups_html(data["tech_groups"])
    badge = category_badge(cat_slug)
    canonical_path = f"/case/{cat_slug}/{model_slug}/"
    meta_description = data["description"] or (
        f"{title} na linha {SITE_BRAND} da {SITE_NAME} com ficha técnica, "
        "especificações e atendimento comercial especializado."
    )
    breadcrumb_schema = build_breadcrumb_schema(
        [
            ("Início", "/"),
            ("CASE", "/case/"),
            (category, f"/case/{cat_slug}/"),
            (title, canonical_path),
        ]
    )
    product_schema = {
        "@context": "https://schema.org",
        "@type": "Product",
        "name": title,
        "description": clean_text(meta_description),
        "image": [make_absolute_url(hero_img)],
        "brand": {"@type": "Brand", "name": SITE_BRAND},
        "seller": {"@type": "Organization", "name": SITE_NAME, "url": SITE_URL},
        "category": category,
        "model": title,
        "url": make_absolute_url(canonical_path),
    }
    if data["summary_specs"]:
        product_schema["additionalProperty"] = [
            {
                "@type": "PropertyValue",
                "name": clean_text(key),
                "value": clean_text(value),
            }
            for key, value in list(data["summary_specs"].items())[:6]
        ]
    head_html = render_head(
        page_name=title,
        description=meta_description,
        canonical_path=canonical_path,
        og_image=hero_img,
        og_type="product",
        schema_objects=[product_schema, breadcrumb_schema],
    )

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
{head_html}
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
        <div class="absolute top-[20%] left-[5%] w-[70vw] h-[70vw] max-w-[400px] max-h-[400px] bg-case-yellow/5 rounded-full blur-3xl"></div>
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
              <a href="/case/{cat_slug}/" class="border border-case-border text-white px-8 py-4 font-bold uppercase tracking-widest hover:bg-white/10 transition-colors text-sm">
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
        <h2 class="font-display font-black text-4xl md:text-5xl uppercase mb-6">{build_product_cta_heading(title)}</h2>
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

    # Pegar imagem do modelo (foto ambientada curada > recorte > primeiro asset)
    public_assets = copy_assets(model_path, cat_slug, model_slug)
    img_src, is_photo = find_card_image(cat_slug, model_slug)
    if not img_src:
        img_src = public_assets[0] if public_assets else "/og-image.jpg"
        is_photo = True
    if is_photo:
        card_img_html = (
            f'<img src="{img_src}" alt="{model["title"]}" loading="lazy" decoding="async" '
            'class="absolute inset-0 w-full h-full object-cover transition-transform duration-700 '
            'group-hover:scale-105 opacity-80 group-hover:opacity-100" />'
            '<div class="absolute inset-0 bg-gradient-to-t from-case-panel via-case-panel/40 to-transparent"></div>'
        )
    else:
        card_img_html = (
            '<div class="absolute inset-0 flex items-center justify-center">'
            f'<img src="{img_src}" alt="{model["title"]}" loading="lazy" decoding="async" '
            'class="w-[88%] max-w-none transition-transform duration-700 group-hover:scale-105 '
            'opacity-90 group-hover:opacity-100 object-contain" /></div>'
        )

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
            <a href="/case/{cat_slug}/{model_slug}/" class="group block">
              <div class="industrial-border h-[420px] bg-case-panel relative overflow-hidden flex flex-col justify-between p-6 hover-industrial cursor-pointer transition-all duration-300 hover:border-case-yellow/50">
                <div class="absolute top-0 right-0 p-3 z-10">
                  <i class="ph-bold ph-arrow-up-right text-xl opacity-0 group-hover:opacity-100 transition-opacity text-case-yellow"></i>
                </div>
                <div class="relative z-10">
                  <span class="inline-block px-2 py-1 bg-white/10 text-[10px] font-mono tracking-widest mb-3">{short_title}</span>
                </div>
{card_img_html}
                <div class="relative z-10 border-t border-case-border pt-4 mt-4">
                  <h2 class="font-display font-black text-xl uppercase leading-tight mb-3 group-hover:text-case-yellow transition-colors">{title}</h2>
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
    canonical_path = f"/case/{cat_slug}/"
    first_model = models[0] if models else None
    first_slug = get_model_slug(first_model["path"]) if first_model else ""
    category_image = DEFAULT_OG_IMAGE
    if first_model:
        public_assets = copy_assets(first_model["path"], cat_slug, first_slug)
        if public_assets:
            category_image = public_assets[0]
    meta_description = (
        f"Linha CASE de {category} na {SITE_NAME} com {count} modelos disponíveis, "
        "fichas técnicas e atendimento comercial especializado."
    )
    breadcrumb_schema = build_breadcrumb_schema(
        [
            ("Início", "/"),
            ("CASE", "/case/"),
            (category, canonical_path),
        ]
    )
    category_schema = {
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "name": category,
        "description": clean_text(meta_description),
        "url": make_absolute_url(canonical_path),
        "image": make_absolute_url(category_image),
        "mainEntity": build_item_list(
            [(model["title"], f"/case/{cat_slug}/{get_model_slug(model['path'])}/") for model in models]
        ),
    }
    head_html = render_head(
        page_name=category,
        description=meta_description,
        canonical_path=canonical_path,
        og_image=category_image,
        schema_objects=[category_schema, breadcrumb_schema],
    )

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
{head_html}
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
           style="background-image: radial-gradient(var(--color-case-yellow) 1px, transparent 1px); background-size: 30px 30px;"></div>
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
          <h2 class="font-display font-black text-3xl uppercase">Não encontrou o que precisa?</h2>
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
        models = [m for m in cat["models"] if get_model_slug(m["path"]) not in EXCLUDED_MODEL_SLUGS]
        cat_slug = get_cat_slug(models[0]["path"]) if models else ""
        badge = category_badge(cat_slug)
        count = len(models)
        icon = icons.get(cat_slug, "ph-fill ph-wrench")
        num = str(i + 1).zfill(2)

        # Pegar imagem do primeiro modelo
        first_model = models[0]
        first_slug = get_model_slug(first_model["path"])
        public_assets = copy_assets(first_model["path"], cat_slug, first_slug)
        card_img, card_is_photo = find_card_image(cat_slug, first_slug)
        if card_img and card_is_photo:
            img_html = (
                f'<img src="{card_img}" alt="{category}" loading="lazy" decoding="async" '
                'class="w-full h-full object-cover opacity-55 group-hover:opacity-75 transition-opacity duration-500" />'
                '<div class="absolute inset-0 bg-gradient-to-t from-case-panel via-case-panel/45 to-case-panel/25"></div>'
            )
        else:
            img = find_nobg_image(cat_slug) or (public_assets[0] if public_assets else "")
            img_html = f'<img src="{img}" alt="{category}" class="w-full h-full object-contain p-6 opacity-80 group-hover:opacity-100 transition-all duration-500" />' if img else ""

        cat_cards.append(f"""
          <a href="/case/{cat_slug}/" class="group block">
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
                <h3 class="font-display font-black text-xl uppercase leading-tight mb-2 group-hover:text-case-yellow transition-colors">{category}</h3>
                <div class="flex justify-between items-center">
                  <span class="text-gray-500 text-xs font-mono">{count} {"modelo" if count == 1 else "modelos"}</span>
                  <span class="text-case-yellow text-xs font-bold uppercase tracking-wider group-hover:translate-x-1 transition-transform">Ver linha →</span>
                </div>
              </div>
            </div>
          </a>""")

    cards_html = "\n".join(cat_cards)
    total_models = sum(
        len([m for m in c["models"] if get_model_slug(m["path"]) not in EXCLUDED_MODEL_SLUGS])
        for c in db
    )
    canonical_path = "/case/catalogo/"
    meta_description = (
        f"Catálogo CASE da {SITE_NAME} com {len(db)} categorias e {total_models} modelos "
        "de equipamentos, fichas técnicas e suporte comercial especializado."
    )
    category_items = []
    for cat in db:
        models = [m for m in cat["models"] if get_model_slug(m["path"]) not in EXCLUDED_MODEL_SLUGS]
        if not models:
            continue
        category_items.append((cat["category"], f"/case/{get_cat_slug(models[0]['path'])}/"))
    catalog_schema = {
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "name": "Produtos",
        "description": clean_text(meta_description),
        "url": make_absolute_url(canonical_path),
        "image": DEFAULT_OG_IMAGE,
        "mainEntity": build_item_list(category_items),
    }
    breadcrumb_schema = build_breadcrumb_schema([("Início", "/"), ("Produtos", canonical_path)])
    head_html = render_head(
        page_name="Produtos",
        description=meta_description,
        canonical_path=canonical_path,
        og_image=DEFAULT_OG_IMAGE,
        schema_objects=[catalog_schema, breadcrumb_schema],
    )

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
{head_html}
</head>
<body class="antialiased tech-grid bg-case-dark text-white selection:bg-case-yellow selection:text-black">
{HEADER_HTML}

  <main class="pt-20">

    <!-- Hero -->
    <section class="py-20 border-b border-case-border bg-case-dark relative overflow-hidden">
      <div class="absolute inset-0 pointer-events-none">
        <div class="absolute top-[20%] left-[10%] w-[500px] h-[500px] bg-case-yellow/5 rounded-full blur-3xl"></div>
      </div>
      <div class="absolute inset-y-0 right-0 w-1/2 hidden lg:flex items-center justify-end pr-12 pointer-events-none">
        <img src="/case-assets/escavadeiras-hidraulicas/cx220c-s2/cx220c-nobg.webp" alt="" aria-hidden="true" loading="lazy" decoding="async" class="max-h-[320px] w-auto object-contain opacity-80 drop-shadow-[0_30px_30px_rgba(0,0,0,0.8)]" />
      </div>
      <div class="container mx-auto px-6 relative z-10">
        <span class="font-mono text-case-yellow text-sm tracking-widest uppercase block mb-4">/// Catálogo</span>
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


# ─── Páginas institucionais ────────────────────────────────────────────────────

FILIAIS_PATH = BASE_DIR / "data" / "filiais.json"


def load_filiais() -> dict:
    return json.loads(FILIAIS_PATH.read_text(encoding="utf-8"))


def render_institutional_page(
    page_name: str,
    description: str,
    canonical_path: str,
    eyebrow: str,
    title_html: str,
    body_html: str,
    schema_objects: list[dict],
) -> str:
    head_html = render_head(
        page_name=page_name,
        description=description,
        canonical_path=canonical_path,
        og_image=DEFAULT_OG_IMAGE,
        schema_objects=schema_objects,
    )
    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
{head_html}
</head>
<body class="antialiased tech-grid bg-case-dark text-white selection:bg-case-yellow selection:text-black">
{HEADER_HTML}

  <main class="pt-20">
    <section class="py-20 border-b border-case-border bg-case-dark relative overflow-hidden">
      <div class="absolute inset-0 pointer-events-none">
        <div class="absolute top-[20%] left-[10%] w-[500px] h-[500px] bg-case-yellow/5 rounded-full blur-3xl"></div>
      </div>
      <div class="container mx-auto px-6 relative z-10">
        <span class="font-mono text-case-yellow text-sm tracking-widest uppercase block mb-4">/// {eyebrow}</span>
        <h1 class="font-display font-black text-5xl md:text-7xl uppercase leading-none">{title_html}</h1>
      </div>
    </section>
{body_html}
  </main>

{FOOTER_HTML}

</body>
</html>"""


def render_filial_card(filial: dict, index: int) -> str:
    matriz_badge = (
        '<span class="inline-block px-2 py-1 bg-case-yellow text-black text-[10px] font-mono font-bold tracking-widest uppercase">Matriz</span>'
        if filial.get("matriz")
        else ""
    )
    brand_badges = "".join(
        f'<span class="inline-block px-2 py-0.5 border border-case-border text-gray-400 text-[9px] font-mono tracking-widest uppercase">{m}</span>'
        for m in filial.get("marcas", ["CASE Construction"])
    )
    tel_link = filial["telefone_e164"]
    maps_url = f"https://www.google.com/maps/search/?api=1&query={filial['lat']},{filial['lng']}"
    return f"""
          <div class="industrial-border bg-case-panel border border-case-border p-8 flex flex-col gap-4 hover:border-case-yellow transition-colors">
            <div class="flex items-start justify-between">
              <span class="font-mono text-xs text-case-yellow tracking-widest">{str(index + 1).zfill(2)}</span>
              {matriz_badge}
            </div>
            <div class="flex flex-wrap gap-2 -mt-2">{brand_badges}</div>
            <div>
              <h2 class="font-display font-black text-2xl uppercase leading-none">{escape(filial['uf'])} — {escape(filial['cidade'])}</h2>
              <p class="text-xs text-gray-500 uppercase tracking-wide mt-1">{escape(filial['estado'])}</p>
            </div>
            <p class="text-sm text-gray-300 leading-relaxed">{escape(filial['endereco'])}<br />CEP {escape(filial['cep'])}</p>
            <div class="mt-auto flex flex-wrap gap-3 pt-4 border-t border-case-border">
              <a href="tel:{escape(tel_link, quote=True)}" class="text-case-yellow font-bold text-sm uppercase tracking-widest hover:underline">{escape(filial['telefone'])}</a>
              <a href="{escape(maps_url, quote=True)}" target="_blank" rel="noopener noreferrer" class="text-gray-400 text-sm uppercase tracking-widest hover:text-case-yellow transition-colors">Ver no mapa →</a>
            </div>
          </div>"""


def build_local_business_schema(filial: dict, empresa: dict) -> dict:
    return {
        "@context": "https://schema.org",
        "@type": "LocalBusiness",
        "name": f"IBL Máquinas — {filial['cidade']}/{filial['uf']}",
        "parentOrganization": {"@type": "Organization", "name": empresa["nome_fantasia"]},
        "address": {
            "@type": "PostalAddress",
            "streetAddress": filial["endereco"],
            "addressLocality": filial["cidade"],
            "addressRegion": filial["uf"],
            "postalCode": filial["cep"],
            "addressCountry": "BR",
        },
        "geo": {"@type": "GeoCoordinates", "latitude": filial["lat"], "longitude": filial["lng"]},
        "telephone": filial["telefone_e164"],
        "url": make_absolute_url("/filiais/"),
    }


def generate_institutional_pages() -> int:
    data = load_filiais()
    empresa = data["empresa"]
    filiais = data["filiais"]
    pages = 0

    # ── /filiais/ ──
    cards = "\n".join(render_filial_card(f, i) for i, f in enumerate(filiais))
    filiais_body = f"""
    <section class="py-24 bg-case-dark">
      <div class="container mx-auto px-6">
        <div class="flex items-center gap-8 mb-12 text-sm font-mono text-gray-400">
          <span class="border border-case-border px-4 py-2">{len(filiais)} UNIDADES</span>
          <span class="border border-case-border px-4 py-2">6 ESTADOS</span>
          <span class="border border-case-border px-4 py-2">NORTE E CENTRO-OESTE</span>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
{cards}
        </div>
      </div>
    </section>"""
    schemas = [build_local_business_schema(f, empresa) for f in filiais]
    schemas.append(build_breadcrumb_schema([("Início", "/"), ("Filiais", "/filiais/")]))
    html = render_institutional_page(
        page_name="Filiais",
        description=(
            "8 unidades IBL Máquinas em 6 estados (MS, MT, AC, AM, RO e RR) com vendas, "
            "peças genuínas CASE e assistência técnica. Endereços, telefones e mapas."
        ),
        canonical_path="/filiais/",
        eyebrow="Cobertura Regional",
        title_html='Nossas<br /><span class="text-outline">Filiais</span>',
        body_html=filiais_body,
        schema_objects=schemas,
    )
    out = BASE_DIR / "filiais"
    out.mkdir(exist_ok=True)
    (out / "index.html").write_text(html, encoding="utf-8")
    pages += 1
    print("  ✓ filiais/index.html")

    # ── /sobre/ ──
    sobre_body = f"""
    <section class="py-24 bg-case-dark">
      <div class="container mx-auto px-6 grid grid-cols-1 lg:grid-cols-12 gap-12">
        <div class="lg:col-span-7 space-y-6 text-gray-300 leading-relaxed">
          <p>A <strong class="text-white">IBL Máquinas</strong> iniciou sua trajetória em maio de 1992, assumindo o desafio de representar a marca <strong class="text-white">CASE Construction</strong> em Mato Grosso do Sul. Com determinação, transformamos um sonho em uma empresa sólida, construída a partir do zero.</p>
          <p>Em 2002, expandimos a operação para mais cinco estados: Mato Grosso, Rondônia, Acre, Amazonas e Roraima — consolidando uma das maiores coberturas regionais de equipamentos de construção do Norte e Centro-Oeste do Brasil.</p>
          <p>Em 2004, integramos ao portfólio a <strong class="text-white">Dynapac</strong>, marca mundialmente reconhecida em soluções de compactação e pavimentação asfáltica — linha disponível sob consulta com nossa equipe comercial.</p>
          <p>Hoje, sob a liderança da segunda geração, seguimos investindo em novas tecnologias e mercados, com compromisso diário com a excelência no atendimento, a disponibilidade de peças genuínas e o pós-venda que mantém a operação dos nossos clientes ativa.</p>
        </div>
        <div class="lg:col-span-5">
          <div class="grid grid-cols-2 gap-4">
            <div class="industrial-border bg-case-panel border border-case-border p-6 text-center">
              <div class="font-display font-black text-4xl text-case-yellow">30+</div>
              <div class="text-xs font-mono uppercase tracking-widest text-gray-400 mt-2">Anos de mercado</div>
            </div>
            <div class="industrial-border bg-case-panel border border-case-border p-6 text-center">
              <div class="font-display font-black text-4xl text-case-yellow">8</div>
              <div class="text-xs font-mono uppercase tracking-widest text-gray-400 mt-2">Unidades</div>
            </div>
            <div class="industrial-border bg-case-panel border border-case-border p-6 text-center">
              <div class="font-display font-black text-4xl text-case-yellow">6</div>
              <div class="text-xs font-mono uppercase tracking-widest text-gray-400 mt-2">Estados atendidos</div>
            </div>
            <div class="industrial-border bg-case-panel border border-case-border p-6 text-center">
              <div class="font-display font-black text-4xl text-case-yellow">2</div>
              <div class="text-xs font-mono uppercase tracking-widest text-gray-400 mt-2">Marcas líderes</div>
            </div>
          </div>
          <a href="/filiais/" class="mt-6 block text-center px-8 py-4 bg-case-yellow text-black font-bold uppercase tracking-widest hover:bg-white transition-colors">Conheça nossas filiais</a>
        </div>
      </div>
    </section>"""
    sobre_schema = {
        "@context": "https://schema.org",
        "@type": "AboutPage",
        "name": "Sobre a IBL Máquinas",
        "url": make_absolute_url("/sobre/"),
        "mainEntity": {
            "@type": "Organization",
            "name": empresa["nome_fantasia"],
            "legalName": empresa["razao_social"],
            "foundingDate": empresa["fundacao"],
            "email": empresa["email"],
            "url": SITE_URL,
            "logo": DEFAULT_OG_IMAGE,
            "sameAs": [empresa["instagram"]],
            "brand": [{"@type": "Brand", "name": m} for m in empresa["marcas"]],
        },
    }
    html = render_institutional_page(
        page_name="Sobre nós",
        description=(
            "Desde 1992 representando a CASE Construction e, desde 2004, a Dynapac. "
            "8 unidades em 6 estados do Norte e Centro-Oeste com vendas, peças e pós-venda."
        ),
        canonical_path="/sobre/",
        eyebrow="Desde 1992",
        title_html='Sobre a<br /><span class="text-outline">IBL Máquinas</span>',
        body_html=sobre_body,
        schema_objects=[sobre_schema, build_breadcrumb_schema([("Início", "/"), ("Sobre", "/sobre/")])],
    )
    out = BASE_DIR / "sobre"
    out.mkdir(exist_ok=True)
    (out / "index.html").write_text(html, encoding="utf-8")
    pages += 1
    print("  ✓ sobre/index.html")

    # ── /contato/ ──
    matriz = next(f for f in filiais if f.get("matriz"))
    contato_rows = "\n".join(
        f"""
          <div class="flex flex-col md:flex-row md:items-center justify-between gap-2 p-5 border border-case-border bg-case-panel">
            <div>
              <span class="font-bold text-white uppercase">{escape(f['uf'])} — {escape(f['cidade'])}</span>
              <span class="block text-xs text-gray-500 mt-1">{escape(f['endereco'])} · CEP {escape(f['cep'])}</span>
            </div>
            <a href="tel:{escape(f['telefone_e164'], quote=True)}" class="text-case-yellow font-bold text-sm uppercase tracking-widest hover:underline whitespace-nowrap">{escape(f['telefone'])}</a>
          </div>"""
        for f in filiais
    )
    contato_body = f"""
    <section class="py-24 bg-case-dark">
      <div class="container mx-auto px-6 grid grid-cols-1 lg:grid-cols-12 gap-12">
        <div class="lg:col-span-5 space-y-6">
          <div class="industrial-border bg-case-panel border border-case-border p-8">
            <h2 class="font-display font-black text-2xl uppercase mb-6">Canais diretos</h2>
            <div class="space-y-4 text-sm">
              <a href="{build_whatsapp_url('Olá, quero falar com a equipe IBL Máquinas.')}" target="_blank" rel="noopener noreferrer" class="flex items-center gap-3 text-case-yellow font-bold uppercase tracking-widest hover:underline"><i class="ph-fill ph-whatsapp-logo text-2xl"></i> WhatsApp comercial</a>
              <a href="mailto:{escape(empresa['email'], quote=True)}" class="flex items-center gap-3 text-gray-300 hover:text-case-yellow transition-colors"><i class="ph-bold ph-envelope text-2xl text-case-yellow"></i> {escape(empresa['email'])}</a>
              <a href="tel:{escape(matriz['telefone_e164'], quote=True)}" class="flex items-center gap-3 text-gray-300 hover:text-case-yellow transition-colors"><i class="ph-bold ph-phone text-2xl text-case-yellow"></i> Matriz: {escape(matriz['telefone'])}</a>
            </div>
            <a href="/#captacao-lead" class="mt-8 block text-center px-8 py-4 bg-case-yellow text-black font-bold uppercase tracking-widest hover:bg-white transition-colors">Solicitar orçamento</a>
            <p class="text-xs text-gray-500 mt-4 leading-relaxed">Resposta comercial em até 1 dia útil. Dados tratados conforme nossa <a href="/privacidade/" class="underline hover:text-case-yellow">Política de Privacidade</a>.</p>
          </div>
        </div>
        <div class="lg:col-span-7">
          <h2 class="font-display font-black text-2xl uppercase mb-6">Telefones por unidade</h2>
          <div class="space-y-3">
{contato_rows}
          </div>
        </div>
      </div>
    </section>"""
    contato_schema = {
        "@context": "https://schema.org",
        "@type": "ContactPage",
        "name": "Contato — IBL Máquinas",
        "url": make_absolute_url("/contato/"),
    }
    html = render_institutional_page(
        page_name="Contato",
        description=(
            "Fale com a IBL Máquinas: WhatsApp comercial, e-mail e telefones das 8 unidades "
            "em MS, MT, AC, AM, RO e RR. Resposta em até 1 dia útil."
        ),
        canonical_path="/contato/",
        eyebrow="Fale Conosco",
        title_html='Entre em<br /><span class="text-outline">Contato</span>',
        body_html=contato_body,
        schema_objects=[contato_schema, build_breadcrumb_schema([("Início", "/"), ("Contato", "/contato/")])],
    )
    out = BASE_DIR / "contato"
    out.mkdir(exist_ok=True)
    (out / "index.html").write_text(html, encoding="utf-8")
    pages += 1
    print("  ✓ contato/index.html")

    # ── /privacidade/ ──
    privacidade_body = f"""
    <section class="py-24 bg-case-dark">
      <div class="container mx-auto px-6 max-w-4xl space-y-10 text-gray-300 leading-relaxed text-sm md:text-base">
        <p class="text-xs font-mono uppercase tracking-widest text-gray-500">Última atualização: junho de 2026</p>

        <div>
          <h2 class="font-display font-black text-2xl uppercase text-white mb-4">1. Quem somos</h2>
          <p>Esta Política de Privacidade descreve como a <strong class="text-white">{escape(empresa['razao_social'])}</strong> ("IBL Máquinas"), inscrita no CNPJ {escape(empresa['cnpj'])}, trata os dados pessoais coletados neste site, em conformidade com a Lei Geral de Proteção de Dados Pessoais (Lei nº 13.709/2018 — LGPD).</p>
        </div>

        <div>
          <h2 class="font-display font-black text-2xl uppercase text-white mb-4">2. Dados que coletamos</h2>
          <p>Ao preencher nossos formulários de contato e orçamento, coletamos: <strong class="text-white">nome, telefone/WhatsApp e interesse comercial</strong> (modelo de máquina, tipo de uso e mensagem). Também coletamos dados de navegação (páginas visitadas e eventos de interação) por meio do Google Analytics, de forma pseudonimizada.</p>
        </div>

        <div>
          <h2 class="font-display font-black text-2xl uppercase text-white mb-4">3. Finalidade do tratamento</h2>
          <p>Os dados são utilizados exclusivamente para: atendimento comercial e elaboração de orçamentos; contato via WhatsApp ou telefone solicitado por você; registro do atendimento em nosso sistema interno de gestão de oportunidades; e melhoria da experiência do site.</p>
        </div>

        <div>
          <h2 class="font-display font-black text-2xl uppercase text-white mb-4">4. Compartilhamento</h2>
          <p>Seus dados não são vendidos nem compartilhados com terceiros para fins de marketing. O tratamento ocorre em sistemas da IBL Máquinas e em operadores estritamente necessários à operação (ex.: WhatsApp/Meta para mensagens iniciadas por você e Google Analytics para métricas de uso).</p>
        </div>

        <div>
          <h2 class="font-display font-black text-2xl uppercase text-white mb-4">5. Retenção e segurança</h2>
          <p>Os dados de leads são mantidos pelo período necessário ao atendimento comercial e às obrigações legais. Adotamos medidas técnicas e organizacionais para proteger os dados contra acesso não autorizado.</p>
        </div>

        <div>
          <h2 class="font-display font-black text-2xl uppercase text-white mb-4">6. Seus direitos</h2>
          <p>Nos termos da LGPD, você pode solicitar a qualquer momento: confirmação do tratamento, acesso, correção, anonimização, portabilidade ou eliminação dos seus dados, além de revogar consentimentos. Para exercer seus direitos, contate <a href="mailto:{escape(empresa['email'], quote=True)}" class="text-case-yellow underline hover:no-underline">{escape(empresa['email'])}</a>.</p>
        </div>

        <div>
          <h2 class="font-display font-black text-2xl uppercase text-white mb-4">7. Cookies e analytics</h2>
          <p>Utilizamos o Google Analytics 4 para entender o uso do site (páginas vistas, origem do acesso e eventos de interação). Você pode bloquear cookies nas configurações do seu navegador sem prejuízo à navegação.</p>
        </div>

        <div>
          <h2 class="font-display font-black text-2xl uppercase text-white mb-4">8. Contato do encarregado</h2>
          <p>Dúvidas sobre esta política ou sobre o tratamento de dados podem ser encaminhadas para <a href="mailto:{escape(empresa['email'], quote=True)}" class="text-case-yellow underline hover:no-underline">{escape(empresa['email'])}</a>.</p>
        </div>
      </div>
    </section>"""
    html = render_institutional_page(
        page_name="Política de Privacidade",
        description=(
            "Como a IBL Máquinas coleta, usa e protege seus dados pessoais em conformidade "
            "com a LGPD (Lei nº 13.709/2018)."
        ),
        canonical_path="/privacidade/",
        eyebrow="LGPD",
        title_html='Política de<br /><span class="text-outline">Privacidade</span>',
        body_html=privacidade_body,
        schema_objects=[build_breadcrumb_schema([("Início", "/"), ("Privacidade", "/privacidade/")])],
    )
    out = BASE_DIR / "privacidade"
    out.mkdir(exist_ok=True)
    (out / "index.html").write_text(html, encoding="utf-8")
    pages += 1
    print("  ✓ privacidade/index.html")

    return pages


def generate_consorcio_page() -> str:
    """Página /consorcio/ — Consórcio Nacional CASE (Primo Rossi)."""
    faq_items = [
        ("O que é a contemplação?", "É o momento em que você recebe a carta de crédito para retirar sua máquina. Acontece nas assembleias mensais, por sorteio ou por lance — sem obrigação de ofertar lance."),
        ("Como funciona o lance?", "O lance é uma antecipação de parcelas que aumenta sua chance de contemplação. Quem não quer ou não pode ofertar continua concorrendo normalmente nos sorteios mensais."),
        ("Meu crédito perde valor com o tempo?", "Não. O valor da carta de crédito é corrigido sempre que o valor do bem de referência é ajustado — você mantém o poder de compra até a contemplação."),
        ("Posso usar o crédito em qualquer máquina CASE?", "Sim. A carta de crédito contempla a linha CASE Construction — escavadeiras, retroescavadeiras, pás carregadeiras, motoniveladoras, tratores de esteiras e linha compacta — com retirada e pós-venda na IBL."),
        ("Quem administra o consórcio?", "A Primo Rossi Administradora de Consórcio Ltda (CNPJ 51.597.300/0001-30), administradora oficial do Consórcio Nacional CASE desde 2017 e a mais antiga do Brasil, fundada em 1964. Autorizada e fiscalizada pelo Banco Central."),
        ("Onde consulto o regulamento?", "O regulamento completo está disponível no site oficial da Primo Rossi. Nossa equipe também orienta sobre grupos, prazos e condições vigentes no atendimento."),
    ]
    faq_html = "\n".join(
        f"""
          <details class="border border-case-border bg-case-panel group">
            <summary class="cursor-pointer list-none p-5 flex items-center justify-between gap-4">
              <span class="font-bold text-white uppercase text-sm tracking-wide">{escape(q)}</span>
              <i class="ph-bold ph-plus text-case-yellow group-open:rotate-45 transition-transform"></i>
            </summary>
            <p class="px-5 pb-5 text-sm text-gray-300 leading-relaxed">{escape(a)}</p>
          </details>"""
        for q, a in faq_items
    )
    faq_schema = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
            for q, a in faq_items
        ],
    }
    service_schema = {
        "@context": "https://schema.org",
        "@type": "Service",
        "name": "Consórcio Nacional CASE",
        "serviceType": "Consórcio de máquinas de construção",
        "provider": {"@type": "Organization", "name": "Primo Rossi Administradora de Consórcio Ltda"},
        "broker": {"@type": "Organization", "name": SITE_NAME, "url": SITE_URL},
        "areaServed": "Norte e Centro-Oeste do Brasil",
        "url": make_absolute_url("/consorcio/"),
    }
    head_html = render_head(
        page_name="Consórcio CASE sem juros",
        description=(
            "Compre sua máquina CASE sem juros e sem entrada com o Consórcio Nacional CASE, "
            "administrado pela Primo Rossi desde 2017. Simule com a IBL Máquinas."
        ),
        canonical_path="/consorcio/",
        og_image=DEFAULT_OG_IMAGE,
        schema_objects=[service_schema, faq_schema, build_breadcrumb_schema([("Início", "/"), ("Consórcio", "/consorcio/")])],
    )
    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
{head_html}
</head>
<body class="antialiased tech-grid bg-case-dark text-white selection:bg-case-yellow selection:text-black">
{HEADER_HTML}

  <main class="pt-20">

    <!-- Hero -->
    <section class="py-20 border-b border-case-border bg-case-dark relative">
      <div class="absolute inset-0 pointer-events-none overflow-hidden">
        <div class="absolute top-[20%] left-[10%] w-[500px] h-[500px] bg-case-yellow/5 rounded-full blur-3xl"></div>
      </div>
      <div class="absolute inset-y-0 right-0 w-[60%] hidden lg:flex items-center justify-end pointer-events-none z-30">
        <img src="/case-assets/fotos-processed/580n-series2.svg" alt="" aria-hidden="true" loading="lazy" decoding="async" class="w-full object-contain object-right scale-110 origin-right translate-y-[25px] drop-shadow-[0_40px_40px_rgba(0,0,0,0.85)]" />
      </div>
      <div class="container mx-auto px-6 relative z-10">
        <span class="font-mono text-case-yellow text-sm tracking-widest uppercase block mb-4">/// Consórcio Nacional CASE</span>
        <h1 class="font-display font-black uppercase leading-[0.95] max-w-2xl">
          <span class="block text-5xl md:text-6xl">Sua próxima CASE</span>
          <span class="block text-outline text-3xl md:text-4xl mt-2 tracking-tight">Sem juros. Sem entrada.</span>
        </h1>
        <p class="text-gray-300 mt-6 max-w-xl text-lg leading-relaxed">Compra planejada com a administradora mais antiga do Brasil.<br />Você programa, a IBL entrega.</p>
        <div class="flex flex-wrap gap-4 mt-8">
          <a data-track="consorcio_cta_simular" href="#consorcio-lead" class="px-8 py-4 bg-case-yellow text-black font-bold uppercase tracking-widest hover:bg-white transition-colors">Quero simular</a>
          <a data-track="consorcio_cta_whatsapp" href="{build_whatsapp_url('Olá, quero saber mais sobre o Consórcio CASE com a IBL Máquinas.')}" target="_blank" rel="noopener noreferrer" class="px-8 py-4 border border-case-yellow text-case-yellow font-bold uppercase tracking-widest hover:bg-case-yellow/10 transition-colors">WhatsApp</a>
        </div>
      </div>
    </section>

    <!-- Prova social -->
    <section class="border-b border-case-border bg-case-gray">
      <div class="grid grid-cols-1 md:grid-cols-3 divide-y md:divide-y-0 md:divide-x divide-case-border">
        <div class="p-8 md:p-10 text-center"><div class="font-display font-black text-4xl text-case-yellow">Desde 1964</div><div class="font-mono text-xs text-gray-400 uppercase tracking-widest mt-2">Primo Rossi — a administradora mais antiga do Brasil</div></div>
        <div class="p-8 md:p-10 text-center"><div class="font-display font-black text-4xl text-case-yellow">+200</div><div class="font-mono text-xs text-gray-400 uppercase tracking-widest mt-2">Contemplações por mês</div></div>
        <div class="p-8 md:p-10 text-center"><div class="font-display font-black text-4xl text-case-yellow">+R$ 13 bi</div><div class="font-mono text-xs text-gray-400 uppercase tracking-widest mt-2">Em créditos já entregues</div></div>
      </div>
    </section>

    <!-- Como funciona -->
    <section class="py-24 bg-case-dark">
      <div class="container mx-auto px-6">
        <span class="font-mono text-case-yellow text-sm tracking-widest uppercase block mb-4">/// Como funciona</span>
        <h2 class="font-display font-black text-4xl md:text-5xl uppercase mb-12">4 passos até a sua máquina</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6">
          <div class="industrial-border bg-case-panel p-8"><span class="font-mono text-case-yellow text-xs">01</span><h3 class="font-display font-black text-xl uppercase mt-3 mb-3">Escolha o crédito</h3><p class="text-sm text-gray-300 leading-relaxed">Defina o valor da carta de crédito de acordo com a máquina que sua operação precisa.</p></div>
          <div class="industrial-border bg-case-panel p-8"><span class="font-mono text-case-yellow text-xs">02</span><h3 class="font-display font-black text-xl uppercase mt-3 mb-3">Parcelas no orçamento</h3><p class="text-sm text-gray-300 leading-relaxed">Sem juros e sem entrada: as parcelas cabem no fluxo de caixa, com prazo do grupo escolhido.</p></div>
          <div class="industrial-border bg-case-panel p-8"><span class="font-mono text-case-yellow text-xs">03</span><h3 class="font-display font-black text-xl uppercase mt-3 mb-3">Assembleias mensais</h3><p class="text-sm text-gray-300 leading-relaxed">Concorra todo mês por sorteio ou antecipe a contemplação com lance — sem obrigatoriedade.</p></div>
          <div class="industrial-border bg-case-panel p-8"><span class="font-mono text-case-yellow text-xs">04</span><h3 class="font-display font-black text-xl uppercase mt-3 mb-3">Retire na IBL</h3><p class="text-sm text-gray-300 leading-relaxed">Contemplado, você escolhe o modelo e retira na IBL — com garantia CASE e pós-venda regional.</p></div>
        </div>
      </div>
    </section>

    <!-- Consórcio vs Financiamento -->
    <section class="py-24 bg-[#080808] border-y border-case-border">
      <div class="container mx-auto px-6">
        <span class="font-mono text-case-yellow text-sm tracking-widest uppercase block mb-4">/// Qual caminho?</span>
        <h2 class="font-display font-black text-4xl md:text-5xl uppercase mb-12">Consórcio ou financiamento</h2>
        <div class="overflow-x-auto">
          <table class="w-full text-sm border border-case-border">
            <thead>
              <tr class="bg-case-panel font-mono text-xs uppercase tracking-widest text-gray-400">
                <th class="text-left p-4 border-b border-case-border"></th>
                <th class="text-left p-4 border-b border-l border-case-border text-case-yellow">Consórcio CASE</th>
                <th class="text-left p-4 border-b border-l border-case-border text-white">Financiamento Banco CNH</th>
              </tr>
            </thead>
            <tbody class="text-gray-300">
              <tr><td class="p-4 border-b border-case-border font-bold text-white">Juros</td><td class="p-4 border-b border-l border-case-border">Sem juros (taxa de administração)</td><td class="p-4 border-b border-l border-case-border">Com juros da operação</td></tr>
              <tr><td class="p-4 border-b border-case-border font-bold text-white">Entrada</td><td class="p-4 border-b border-l border-case-border">Sem entrada</td><td class="p-4 border-b border-l border-case-border">Conforme condição vigente</td></tr>
              <tr><td class="p-4 border-b border-case-border font-bold text-white">Quando recebo a máquina</td><td class="p-4 border-b border-l border-case-border">Na contemplação (sorteio ou lance)</td><td class="p-4 border-b border-l border-case-border">Imediato, após aprovação</td></tr>
              <tr><td class="p-4 font-bold text-white">Ideal para</td><td class="p-4 border-l border-case-border">Renovação programada e expansão planejada</td><td class="p-4 border-l border-case-border">Necessidade imediata de equipamento</td></tr>
            </tbody>
          </table>
        </div>
        <p class="text-gray-400 text-sm mt-6">Tem pressa? A IBL também opera o financiamento do <strong class="text-white">Banco CNH</strong>, o banco oficial da CASE. <a href="/contato/" class="text-case-yellow underline hover:no-underline">Fale com a equipe</a> e compare os dois caminhos para o seu caso.</p>
      </div>
    </section>

    <!-- Para quem é + faixas -->
    <section class="py-24 bg-case-dark">
      <div class="container mx-auto px-6 grid grid-cols-1 lg:grid-cols-2 gap-12">
        <div>
          <h2 class="font-display font-black text-3xl uppercase mb-8">Para quem faz sentido</h2>
          <div class="space-y-4">
            <div class="border border-case-border bg-case-panel p-6"><h3 class="font-bold uppercase text-case-yellow text-sm tracking-widest mb-2">Renovação programada de frota</h3><p class="text-sm text-gray-300">Substitua máquinas no momento certo do ciclo, sem comprometer o caixa com juros.</p></div>
            <div class="border border-case-border bg-case-panel p-6"><h3 class="font-bold uppercase text-case-yellow text-sm tracking-widest mb-2">Expansão planejada</h3><p class="text-sm text-gray-300">Novas frentes de obra no radar? Programe a aquisição e chegue com equipamento próprio.</p></div>
            <div class="border border-case-border bg-case-panel p-6"><h3 class="font-bold uppercase text-case-yellow text-sm tracking-widest mb-2">Locadores e prestadores de serviço</h3><p class="text-sm text-gray-300">Aumente a frota de locação com previsibilidade de custo e margem protegida.</p></div>
          </div>
        </div>
        <div>
          <h2 class="font-display font-black text-3xl uppercase mb-8">Faixas de crédito</h2>
          <div class="industrial-border bg-case-panel p-8">
            <div class="flex items-end gap-3"><span class="font-display font-black text-4xl text-case-yellow">R$ 293 mil</span><span class="text-gray-400 mb-1">a</span><span class="font-display font-black text-4xl text-case-yellow">R$ 1,3 mi</span></div>
            <p class="text-sm text-gray-300 mt-4 leading-relaxed">Cartas de crédito para toda a linha CASE Construction — da minicarregadeira à escavadeira de grande porte.</p>
            <p class="text-xs text-gray-500 mt-4 font-mono uppercase tracking-wide">* Valores de referência. Grupos, prazos e condições vigentes são informados pela administradora no atendimento.</p>
          </div>
          <a data-track="consorcio_cta_simular_2" href="#consorcio-lead" class="mt-6 block text-center px-8 py-4 bg-case-yellow text-black font-bold uppercase tracking-widest hover:bg-white transition-colors">Simular meu consórcio</a>
        </div>
      </div>
    </section>

    <!-- FAQ -->
    <section class="py-24 bg-[#080808] border-y border-case-border">
      <div class="container mx-auto px-6 max-w-4xl">
        <h2 class="font-display font-black text-4xl uppercase mb-10">Perguntas frequentes</h2>
        <div class="space-y-3">
{faq_html}
        </div>
      </div>
    </section>

    <!-- Lead -->
    <section id="consorcio-lead" class="py-24 bg-case-dark">
      <div class="container mx-auto px-6 grid grid-cols-1 lg:grid-cols-12 gap-12">
        <div class="lg:col-span-6">
          <span class="font-mono text-case-yellow text-sm tracking-widest uppercase block mb-4">/// Simulação</span>
          <h2 class="font-display font-black text-4xl md:text-5xl uppercase leading-[0.95]">Receba uma simulação do seu consórcio</h2>
          <p class="text-gray-300 mt-5 max-w-xl">Informe a linha de interesse e nossa equipe retorna com grupos, prazos e parcelas vigentes do Consórcio Nacional CASE.</p>
        </div>
        <div class="lg:col-span-6">
          <form id="lead-form" class="industrial-border bg-case-panel p-6 md:p-7 space-y-4">
            <h3 class="font-display font-black text-2xl uppercase">Simular consórcio</h3>
            <div>
              <label for="lead-nome" class="block text-xs font-mono uppercase tracking-widest text-gray-400 mb-2">Nome</label>
              <input id="lead-nome" name="nome" required class="input-field" placeholder="Seu nome completo" />
            </div>
            <div>
              <label for="lead-telefone" class="block text-xs font-mono uppercase tracking-widest text-gray-400 mb-2">WhatsApp</label>
              <input id="lead-telefone" name="telefone" required class="input-field" placeholder="(00) 00000-0000" />
            </div>
            <div>
              <label for="lead-interesse" class="block text-xs font-mono uppercase tracking-widest text-gray-400 mb-2">Linha de interesse</label>
              <select id="lead-interesse" name="interesse" required class="input-field">
                <option value="">Selecione uma categoria</option>
                <option>Consórcio — Escavadeiras Hidráulicas</option>
                <option>Consórcio — Retroescavadeiras</option>
                <option>Consórcio — Pás-Carregadeiras</option>
                <option>Consórcio — Minicarregadeiras</option>
                <option>Consórcio — Motoniveladoras</option>
                <option>Consórcio — Miniescavadeiras</option>
                <option>Consórcio — Rolo Compactador</option>
                <option>Consórcio — Tratores de Esteira</option>
              </select>
            </div>
            <label class="flex items-start gap-3 pt-1 text-xs text-gray-400 leading-relaxed cursor-pointer">
              <input type="checkbox" name="consentimento" required class="mt-0.5 accent-[var(--color-case-yellow)]" />
              <span>Autorizo o uso dos meus dados para contato comercial, conforme a <a href="/privacidade/" class="underline hover:text-case-yellow" target="_blank">Política de Privacidade</a>.</span>
            </label>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2">
              <button data-track="consorcio_lead_submit" type="submit" class="btn btn-primary w-full">Quero simular</button>
              <a data-track="consorcio_lead_whatsapp" href="{build_whatsapp_url('Olá, quero simular o Consórcio CASE.')}" target="_blank" rel="noopener noreferrer" class="btn btn-secondary w-full">WhatsApp direto</a>
            </div>
            <p id="lead-feedback" role="status" aria-live="polite" class="text-xs font-mono text-gray-500 uppercase tracking-widest"></p>
          </form>
        </div>
      </div>
    </section>

    <!-- Compliance -->
    <section class="py-12 bg-[#080808] border-t border-case-border">
      <div class="container mx-auto px-6 text-xs text-gray-500 leading-relaxed space-y-2">
        <p><strong class="text-gray-300">Administradora oficial:</strong> Primo Rossi Administradora de Consórcio Ltda — CNPJ 51.597.300/0001-30 — autorizada e fiscalizada pelo Banco Central do Brasil. Administradora do Consórcio Nacional CASE desde 2017.</p>
        <p>O consórcio não garante contemplação imediata. Valores, grupos, prazos e taxas são os vigentes na contratação, informados pela administradora. Regulamento disponível em <a href="https://primorossi.com.br/" target="_blank" rel="noopener noreferrer" class="underline hover:text-case-yellow">primorossi.com.br</a>.</p>
        <p>A IBL Máquinas atua como ponto de venda autorizado e responsável pela entrega e pós-venda dos equipamentos CASE.</p>
      </div>
    </section>

  </main>

{FOOTER_HTML}

</body>
</html>"""


# ─── Main ───────────────────────────────────────────────────────────────────────

# Páginas estáticas mantidas à mão na raiz do repo (fora de /case/).
STATIC_PAGE_PATHS = [
    "/",
    "/sobre/",
    "/filiais/",
    "/contato/",
    "/consorcio/",
    "/privacidade/",
]


def generate_sitemap(page_paths: list[str]) -> None:
    """Gera public/sitemap.xml e public/robots.txt a partir das rotas conhecidas."""
    from datetime import date

    public_dir = BASE_DIR / "public"
    public_dir.mkdir(exist_ok=True)
    today = date.today().isoformat()

    entries = []
    for path in page_paths:
        loc = make_absolute_url(path)
        priority = "1.0" if path == "/" else ("0.8" if path.count("/") <= 2 else "0.6")
        entries.append(
            f"  <url>\n    <loc>{escape(loc)}</loc>\n    <lastmod>{today}</lastmod>\n    <priority>{priority}</priority>\n  </url>"
        )

    sitemap = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(entries)
        + "\n</urlset>\n"
    )
    (public_dir / "sitemap.xml").write_text(sitemap, encoding="utf-8")
    print(f"  ✓ public/sitemap.xml ({len(page_paths)} rotas)")

    robots = (
        "User-agent: *\n"
        "Allow: /\n\n"
        f"Sitemap: {SITE_URL}/sitemap.xml\n"
    )
    (public_dir / "robots.txt").write_text(robots, encoding="utf-8")
    print("  ✓ public/robots.txt")




# ─── Dynapac (marca 2) ─────────────────────────────────────────────────────────

DYNAPAC_DB_PATH = BASE_DIR / "data" / "dynapac-db.json"
DYNAPAC_OUT_DIR = BASE_DIR / "dynapac"
DYNAPAC_STATES = ["AC", "AM", "RO", "RR"]
DYNAPAC_COVERAGE = "Concessionária Dynapac no Acre, Amazonas, Rondônia e Roraima"
DYNAPAC_META_SUFFIX = " Vendas, peças e assistência IBL no AC, AM, RO e RR."
DYNAPAC_BRAND = "Dynapac"

DYNAPAC_CATEGORY_ICONS = {
    "compactacao": "ph-fill ph-circle-dashed",
    "pavimentacao": "ph-fill ph-road-horizon",
    "equipamentos-leves": "ph-fill ph-hand-fist",
}


def dynapac_filiais() -> list[dict]:
    data = load_filiais()
    return [f for f in data["filiais"] if f["uf"] in DYNAPAC_STATES]


def process_dynapac_image(cat_slug: str, model_slug: str) -> str:
    """Converte fotos-dynapac/{cat}/{slug}/original.* em public/dynapac-assets/.../{slug}.webp.

    Fundo branco contíguo vira transparência (flood fill pelas bordas) para
    integrar ao layout dark. Retorna caminho público ou "".
    """
    src_dir = BASE_DIR / "fotos-dynapac" / cat_slug / model_slug
    if not src_dir.exists():
        return ""
    sources = [p for p in iter_sorted_files(src_dir) if p.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"} and not p.name.startswith(".")]
    if not sources:
        return ""
    src = sources[0]

    dst_dir = BASE_DIR / "public" / "dynapac-assets" / cat_slug / model_slug
    dst_dir.mkdir(parents=True, exist_ok=True)
    dst = dst_dir / f"{model_slug}.webp"
    public_path = f"/dynapac-assets/{cat_slug}/{model_slug}/{model_slug}.webp"

    try:
        if dst.exists() and dst.stat().st_mtime_ns >= src.stat().st_mtime_ns:
            return public_path
    except OSError:
        pass

    try:
        from PIL import Image, ImageDraw
    except ImportError:
        print("  ! Pillow indisponível — imagens Dynapac não processadas")
        return ""

    try:
        with Image.open(src) as img:
            img = img.convert("RGBA")
            img.thumbnail((1200, 1200), Image.LANCZOS)
            # Fundo branco -> alpha, apenas se os cantos forem quase brancos
            w, h = img.size
            corners = [img.getpixel(p) for p in [(2, 2), (w - 3, 2), (2, h - 3), (w - 3, h - 3)]]
            whiteish = sum(1 for c in corners if c[0] > 232 and c[1] > 232 and c[2] > 232 and c[3] > 200)
            if whiteish >= 3:
                for p in [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]:
                    try:
                        ImageDraw.floodfill(img, p, (0, 0, 0, 0), thresh=42)
                    except (ValueError, RecursionError):
                        pass
            img.save(dst, "WEBP", quality=82, method=6)
        return public_path
    except Exception as exc:  # noqa: BLE001
        print(f"  ! Falha ao processar imagem Dynapac {model_slug}: {exc}")
        return ""


def render_dynapac_page(*, page_name, description, canonical_path, body_html, schema_objects=None, og_image=None):
    head_html = render_head(
        page_name=page_name,
        description=description,
        canonical_path=canonical_path,
        og_image=og_image or DEFAULT_OG_IMAGE,
        schema_objects=schema_objects or [],
        brand=DYNAPAC_BRAND,
    )
    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
{head_html}
</head>
<body data-brand="dynapac" class="antialiased tech-grid bg-case-dark text-white selection:bg-case-yellow selection:text-black">
{HEADER_HTML}

  <main class="pt-20">
{body_html}
  </main>

{FOOTER_HTML}

</body>
</html>"""


def render_dynapac_breadcrumb(items: list[tuple[str, str]]) -> str:
    crumbs = ['<li><a href="/" class="hover:text-case-yellow transition-colors">Home</a></li>']
    for label, href in items[:-1]:
        crumbs.append('<li aria-hidden="true"><i class="ph-bold ph-caret-right text-xs"></i></li>')
        crumbs.append(f'<li><a href="{href}" class="hover:text-case-yellow transition-colors">{escape(label)}</a></li>')
    crumbs.append('<li aria-hidden="true"><i class="ph-bold ph-caret-right text-xs"></i></li>')
    crumbs.append(f'<li><span aria-current="page" class="text-white">{escape(items[-1][0])}</span></li>')
    return (
        '<nav aria-label="Breadcrumb" data-breadcrumb-nav class="generated-breadcrumb flex items-center gap-2 '
        'text-xs font-mono text-gray-400"><ol class="flex flex-wrap items-center gap-2">' + "".join(crumbs) + "</ol></nav>"
    )


def render_dynapac_coverage_strip() -> str:
    return f"""
    <div class="bg-case-yellow text-black py-3">
      <div class="container mx-auto px-6 flex flex-wrap items-center gap-x-6 gap-y-1">
        <span class="font-mono text-xs font-bold uppercase tracking-widest">/// Cobertura Dynapac</span>
        <span class="text-sm font-bold uppercase">Acre · Amazonas · Rondônia · Roraima</span>
      </div>
    </div>"""


def render_dynapac_unidades_section() -> str:
    cards = "".join(render_filial_card(f, i) for i, f in enumerate(dynapac_filiais()))
    return f"""
    <section class="py-20 border-t border-case-border" id="unidades-dynapac">
      <div class="container mx-auto px-6">
        <span class="font-mono text-case-yellow text-sm tracking-widest uppercase block mb-4">/// Onde atendemos Dynapac</span>
        <h2 class="font-display font-black text-3xl md:text-5xl uppercase leading-none mb-4">4 unidades no Norte</h2>
        <p class="text-gray-400 max-w-2xl mb-10">A linha Dynapac é atendida pela IBL nas unidades do Acre, Amazonas, Rondônia e Roraima — com vendas, peças e assistência técnica. Nos demais estados, atendemos a linha CASE Construction.</p>
        <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6">{cards}</div>
      </div>
    </section>"""


def render_dynapac_cta_section(model_name: str) -> str:
    wa = build_whatsapp_url(f"Olá, tenho interesse no equipamento Dynapac {model_name}. Atendo pela região Norte.")
    return f"""
    <section class="py-20 bg-case-panel border-t border-case-border">
      <div class="container mx-auto px-6 text-center">
        <h2 class="font-display font-black text-3xl md:text-5xl uppercase mb-6">Solicitar Orçamento</h2>
        <p class="text-gray-400 max-w-xl mx-auto mb-8">Fale com a equipe IBL da sua região para condições comerciais, disponibilidade e prazo de entrega do {escape(model_name)}.</p>
        <a href="{wa}" target="_blank" rel="noopener noreferrer" class="inline-block px-10 py-4 bg-case-yellow text-black font-bold uppercase tracking-widest hover:bg-white transition-colors">Falar com Consultor</a>
      </div>
    </section>"""


def _spec_label(key: str) -> str:
    return key.replace("_", " ").capitalize().replace("Forca", "Força").replace("Potencia", "Potência").replace("pavimentacao", "pavimentação").replace("percussao", "percussão")


def render_dynapac_model_card(cat_slug: str, model: dict) -> str:
    img = model.get("_img") or ""
    img_html = (
        f'<img src="{img}" alt="{escape(model["nome_completo"], quote=True)}" loading="lazy" decoding="async" '
        'class="w-full h-full object-contain p-4 opacity-90 group-hover:scale-105 transition-transform duration-500" />'
        if img else '<i class="ph-fill ph-wrench text-6xl text-gray-700"></i>'
    )
    pills = "".join(
        f'<span class="font-mono text-[10px] uppercase tracking-wide text-gray-400 border border-case-border px-2 py-1">{escape(_spec_label(k))}: {escape(str(v))}</span>'
        for k, v in list(model.get("specs", {}).items())[:2] if v
    )
    return f"""
          <a href="/dynapac/{cat_slug}/{model['slug']}/" class="group block industrial-border bg-case-panel border border-case-border hover:border-case-yellow transition-colors">
            <div class="h-48 flex items-center justify-center bg-gradient-to-b from-case-gray/40 to-transparent overflow-hidden">{img_html}</div>
            <div class="p-6 border-t border-case-border">
              <h3 class="font-display font-black text-xl uppercase group-hover:text-case-yellow transition-colors">{escape(model['modelo'])}</h3>
              <p class="text-xs text-gray-500 mt-1 mb-3 line-clamp-2">{escape(truncate_text(model.get('descricao', ''), 110))}</p>
              <div class="flex flex-wrap gap-2">{pills}</div>
            </div>
          </a>"""


def generate_dynapac_category_page(cat: dict) -> str:
    cat_slug = cat["slug"]
    sections = []
    total = 0
    for sub in cat["subcategorias"]:
        cards = "".join(render_dynapac_model_card(cat_slug, m) for m in sub["modelos"])
        total += len(sub["modelos"])
        sections.append(f"""
        <div class="mb-16">
          <div class="flex items-center gap-3 mb-6">
            <div class="w-1 h-6 bg-case-yellow"></div>
            <h2 class="font-display font-black text-2xl uppercase tracking-wide">{escape(sub['nome'])}</h2>
            <span class="font-mono text-xs text-gray-500">{len(sub['modelos'])} {"modelo" if len(sub['modelos']) == 1 else "modelos"}</span>
          </div>
          <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">{cards}</div>
        </div>""")

    breadcrumb = render_dynapac_breadcrumb([("Dynapac", "/dynapac/"), (cat["nome"], f"/dynapac/{cat_slug}/")])
    body = f"""
    {render_dynapac_coverage_strip()}
    <section class="py-16 border-b border-case-border relative overflow-hidden">
      <div class="absolute top-[10%] right-[5%] w-[420px] h-[420px] bg-case-yellow/5 rounded-full blur-3xl pointer-events-none"></div>
      <div class="container mx-auto px-6 relative z-10">
        {breadcrumb}
        <span class="font-mono text-case-yellow text-sm tracking-widest uppercase block mt-8 mb-4">/// Dynapac · {escape(cat['nome'])}</span>
        <h1 class="font-display font-black text-5xl md:text-7xl uppercase leading-none">{escape(cat['nome'])}</h1>
        <p class="text-gray-400 max-w-2xl mt-6">{total} {"equipamento" if total == 1 else "equipamentos"} Dynapac com vendas, peças e assistência técnica da IBL Máquinas no Norte do Brasil.</p>
      </div>
    </section>
    <section class="py-16"><div class="container mx-auto px-6">{''.join(sections)}</div></section>
    {render_dynapac_unidades_section()}"""

    schema = [
        build_breadcrumb_schema([("Início", "/"), ("Dynapac", "/dynapac/"), (cat["nome"], f"/dynapac/{cat_slug}/")]),
        build_item_list([(m["nome_completo"], f"/dynapac/{cat_slug}/{m['slug']}/") for s in cat["subcategorias"] for m in s["modelos"]]),
    ]
    return render_dynapac_page(
        page_name=cat["nome"],
        description=f"Linha Dynapac de {cat['nome'].lower()} na IBL Máquinas — {DYNAPAC_COVERAGE.lower()}. {total} modelos com peças e assistência técnica.",
        canonical_path=f"/dynapac/{cat_slug}/",
        body_html=body,
        schema_objects=schema,
    )


def generate_dynapac_model_page(cat: dict, sub: dict, model: dict) -> str:
    cat_slug = cat["slug"]
    slug = model["slug"]
    img = model.get("_img") or ""
    nome = model["nome_completo"]

    specs_items = "".join(
        f"""<div class="flex items-start justify-between py-3 border-b border-case-border last:border-0 gap-4">
              <span class="text-gray-400 text-sm font-mono flex-shrink-0 w-48">{escape(_spec_label(k))}</span>
              <span class="text-white text-sm text-right">{escape(str(v))}</span>
            </div>"""
        for k, v in model.get("specs", {}).items() if v
    )
    pills = render_summary_pills({_spec_label(k): v for k, v in list(model.get("specs", {}).items())[:4] if v})
    img_html = (
        f'<img src="{img}" alt="{escape(nome, quote=True)}" class="max-h-[420px] w-auto object-contain drop-shadow-[0_30px_40px_rgba(0,0,0,0.8)]" />'
        if img else ""
    )
    breadcrumb = render_dynapac_breadcrumb([
        ("Dynapac", "/dynapac/"), (cat["nome"], f"/dynapac/{cat_slug}/"), (model["modelo"], f"/dynapac/{cat_slug}/{slug}/"),
    ])

    body = f"""
    {render_dynapac_coverage_strip()}
    <section class="py-16 border-b border-case-border relative overflow-hidden">
      <div class="absolute top-[10%] left-[40%] w-[500px] h-[500px] bg-case-yellow/5 rounded-full blur-3xl pointer-events-none"></div>
      <div class="container mx-auto px-6 relative z-10">
        {breadcrumb}
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center mt-10">
          <div>
            <span class="font-mono text-case-yellow text-sm tracking-widest uppercase block mb-4">/// {escape(sub['nome'])}</span>
            <h1 class="font-display font-black text-5xl md:text-6xl uppercase leading-none">{escape(nome)}</h1>
            <p class="text-gray-400 mt-6 leading-relaxed">{escape(model.get('descricao', ''))}</p>
            <div class="grid grid-cols-2 gap-4 mt-8">{pills}</div>
          </div>
          <div class="flex items-center justify-center">{img_html}</div>
        </div>
      </div>
    </section>
    <section class="py-16">
      <div class="container mx-auto px-6 max-w-4xl">
        <div class="flex items-center gap-3 mb-6">
          <div class="w-1 h-6 bg-case-yellow"></div>
          <h2 class="font-display font-black text-2xl uppercase tracking-wide">Ficha Técnica</h2>
        </div>
        <div class="bg-case-panel border border-case-border p-6">{specs_items}</div>
        <p class="text-xs text-gray-600 font-mono mt-4 uppercase tracking-wide">Especificações de referência do fabricante. Confirme a configuração exata com a equipe comercial IBL.</p>
      </div>
    </section>
    <section class="py-20 bg-case-panel border-t border-case-border">
      <div class="container mx-auto px-6 text-center">
        <h2 class="font-display font-black text-3xl md:text-5xl uppercase mb-6">Solicitar Orçamento</h2>
        <p class="text-gray-400 max-w-xl mx-auto mb-8">Fale com a equipe IBL da sua região para condições, disponibilidade e prazo de entrega.</p>
        <a href="{build_whatsapp_url(f'Olá, tenho interesse no equipamento Dynapac {nome}.')}" target="_blank" rel="noopener noreferrer" class="inline-block px-10 py-4 bg-case-yellow text-black font-bold uppercase tracking-widest hover:bg-white transition-colors">Falar com Consultor</a>
      </div>
    </section>
    {render_dynapac_unidades_section()}"""

    schema = [
        build_breadcrumb_schema([
            ("Início", "/"), ("Dynapac", "/dynapac/"), (cat["nome"], f"/dynapac/{cat_slug}/"), (nome, f"/dynapac/{cat_slug}/{slug}/"),
        ]),
        {
            "@context": "https://schema.org",
            "@type": "Product",
            "name": nome,
            "brand": {"@type": "Brand", "name": "Dynapac"},
            "description": model.get("descricao", ""),
            "image": make_absolute_url(img) if img else make_absolute_url(DEFAULT_OG_IMAGE),
            "url": make_absolute_url(f"/dynapac/{cat_slug}/{slug}/"),
        },
    ]
    return render_dynapac_page(
        page_name=nome,
        description=build_meta_description(f"{nome}: ", model.get("descricao", ""), DYNAPAC_META_SUFFIX),
        canonical_path=f"/dynapac/{cat_slug}/{slug}/",
        body_html=body,
        og_image=img or None,
        schema_objects=schema,
    )


def generate_dynapac_home(db: dict) -> str:
    cats_cards = []
    total_models = 0
    for i, cat in enumerate(db["categorias"]):
        count = sum(len(s["modelos"]) for s in cat["subcategorias"])
        total_models += count
        icon = DYNAPAC_CATEGORY_ICONS.get(cat["slug"], "ph-fill ph-wrench")
        first_img = ""
        for s in cat["subcategorias"]:
            for m in s["modelos"]:
                if m.get("_img"):
                    first_img = m["_img"]
                    break
            if first_img:
                break
        img_html = (
            f'<img src="{first_img}" alt="{escape(cat["nome"], quote=True)}" loading="lazy" decoding="async" class="w-full h-full object-contain p-6 opacity-50 group-hover:opacity-90 transition-all duration-500" />'
            if first_img else ""
        )
        cats_cards.append(f"""
          <a href="/dynapac/{cat['slug']}/" class="group block industrial-border bg-case-panel border border-case-border hover:border-case-yellow transition-colors relative overflow-hidden">
            <div class="absolute top-4 left-4 font-mono text-xs text-gray-600">{str(i + 1).zfill(2)}</div>
            <div class="h-56">{img_html}</div>
            <div class="p-8 border-t border-case-border">
              <div class="flex items-center justify-between mb-2">
                <h2 class="font-display font-black text-2xl uppercase group-hover:text-case-yellow transition-colors">{escape(cat['nome'])}</h2>
                <i class="{icon} text-2xl text-case-yellow"></i>
              </div>
              <p class="font-mono text-xs text-gray-500 uppercase tracking-widest">{count} equipamentos →</p>
            </div>
          </a>""")

    body = f"""
    {render_dynapac_coverage_strip()}
    <section class="py-24 border-b border-case-border relative overflow-hidden">
      <div class="absolute top-[15%] right-[8%] w-[560px] h-[560px] bg-case-yellow/5 rounded-full blur-3xl pointer-events-none"></div>
      <div class="container mx-auto px-6 relative z-10">
        <span class="font-mono text-case-yellow text-sm tracking-widest uppercase block mb-6">/// IBL Máquinas · Concessionária Autorizada</span>
        <h1 class="font-display font-black text-6xl md:text-8xl uppercase leading-[0.9]">DYNAPAC<br /><span class="text-case-yellow">COMPACTAÇÃO &amp;<br />PAVIMENTAÇÃO</span></h1>
        <p class="text-gray-400 max-w-2xl mt-8 text-lg">Equipamentos Dynapac para compactação de solos e asfalto, pavimentação e obras urbanas — com vendas, peças originais e assistência técnica da IBL no Acre, Amazonas, Rondônia e Roraima.</p>
        <div class="flex flex-wrap gap-4 mt-10">
          <a href="#linhas" class="px-8 py-4 bg-case-yellow text-black font-bold uppercase tracking-widest hover:bg-white transition-colors">Ver Linhas</a>
          <a href="{build_whatsapp_url('Olá, quero falar sobre equipamentos Dynapac com a IBL Máquinas.')}" target="_blank" rel="noopener noreferrer" class="px-8 py-4 border border-white/30 font-bold uppercase tracking-widest hover:border-case-yellow hover:text-case-yellow transition-colors">Falar com Consultor</a>
        </div>
      </div>
    </section>
    <section class="py-20" id="linhas">
      <div class="container mx-auto px-6">
        <span class="font-mono text-case-yellow text-sm tracking-widest uppercase block mb-4">/// Linhas de produto</span>
        <h2 class="font-display font-black text-3xl md:text-5xl uppercase leading-none mb-12">{total_models} equipamentos em 3 linhas</h2>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">{''.join(cats_cards)}</div>
      </div>
    </section>
    {render_dynapac_unidades_section()}"""

    schema = [
        build_breadcrumb_schema([("Início", "/"), ("Dynapac", "/dynapac/")]),
        {
            "@context": "https://schema.org",
            "@type": "Organization",
            "name": "IBL Máquinas — Dynapac",
            "url": make_absolute_url("/dynapac/"),
            "brand": {"@type": "Brand", "name": "Dynapac"},
            "areaServed": ["Acre", "Amazonas", "Rondônia", "Roraima"],
        },
    ]
    return render_dynapac_page(
        page_name="Compactação e Pavimentação",
        description=f"{DYNAPAC_COVERAGE}: rolos compactadores, pavimentadoras e linha leve Dynapac com vendas, peças e assistência técnica IBL Máquinas.",
        canonical_path="/dynapac/",
        body_html=body,
        schema_objects=schema,
    )


def generate_dynapac(sitemap_paths: list[str]) -> int:
    if not DYNAPAC_DB_PATH.exists():
        print("  ! data/dynapac-db.json ausente — páginas Dynapac não geradas")
        return 0
    db = json.loads(DYNAPAC_DB_PATH.read_text(encoding="utf-8"))
    pages = 0

    # Processar imagens e anexar caminho público a cada modelo
    for cat in db["categorias"]:
        for sub in cat["subcategorias"]:
            for m in sub["modelos"]:
                m["_img"] = process_dynapac_image(cat["slug"], m["slug"])

    DYNAPAC_OUT_DIR.mkdir(exist_ok=True)
    (DYNAPAC_OUT_DIR / "index.html").write_text(generate_dynapac_home(db), encoding="utf-8")
    pages += 1
    print("  ✓ dynapac/index.html")

    for cat in db["categorias"]:
        cat_dir = DYNAPAC_OUT_DIR / cat["slug"]
        cat_dir.mkdir(exist_ok=True)
        (cat_dir / "index.html").write_text(generate_dynapac_category_page(cat), encoding="utf-8")
        pages += 1
        sitemap_paths.append(f"/dynapac/{cat['slug']}/")
        print(f"  ✓ dynapac/{cat['slug']}/index.html")
        for sub in cat["subcategorias"]:
            for m in sub["modelos"]:
                model_dir = cat_dir / m["slug"]
                model_dir.mkdir(exist_ok=True)
                (model_dir / "index.html").write_text(generate_dynapac_model_page(cat, sub, m), encoding="utf-8")
                pages += 1
                sitemap_paths.append(f"/dynapac/{cat['slug']}/{m['slug']}/")

    removidos = prune_dynapac_orfaos(db)
    print(f"  ✓ {pages} páginas Dynapac" + (f" ({removidos} rotas órfãs removidas)" if removidos else ""))
    return pages


def prune_dynapac_orfaos(db: dict) -> int:
    """Apaga páginas e imagens de modelos que saíram do catálogo nacional.

    Sem isso, um modelo descontinuado na Dynapac continuaria publicado (o Vite
    empacota qualquer index.html encontrado em `dynapac/`).
    """
    validos = {
        (cat["slug"], m["slug"])
        for cat in db["categorias"]
        for sub in cat["subcategorias"]
        for m in sub["modelos"]
    }
    categorias = {cat["slug"] for cat in db["categorias"]}
    removidos = 0

    for base, rotulo in ((DYNAPAC_OUT_DIR, "página"), (BASE_DIR / "public" / "dynapac-assets", "imagem")):
        if not base.exists():
            continue
        for cat_dir in base.iterdir():
            if not cat_dir.is_dir():
                continue
            if cat_dir.name not in categorias:
                shutil.rmtree(cat_dir)
                removidos += 1
                print(f"  - {rotulo}s removidas: dynapac/{cat_dir.name}/ (categoria fora do catálogo)")
                continue
            for model_dir in cat_dir.iterdir():
                if model_dir.is_dir() and (cat_dir.name, model_dir.name) not in validos:
                    shutil.rmtree(model_dir)
                    removidos += 1
                    print(f"  - {rotulo} removida: {cat_dir.name}/{model_dir.name}")
    return removidos


def main():
    print("=== GERANDO PÁGINAS FRONTEND ===\n")

    db = json.loads(DB_PATH.read_text(encoding="utf-8"))

    # Garantir que o diretório de saída existe
    OUT_DIR.mkdir(exist_ok=True)
    (BASE_DIR / "public" / "case-assets").mkdir(parents=True, exist_ok=True)

    # Derivativos .webp para imagens pesadas já presentes em public/case-assets
    # (curadas ou de execuções anteriores) — as páginas preferem o .webp.
    print("[ASSETS] Gerando derivativos .webp para imagens pesadas ...")
    webp_count = 0
    for candidate in sorted((BASE_DIR / "public" / "case-assets").rglob("*")):
        if candidate.is_file() and ensure_webp_derivative(candidate) is not None:
            webp_count += 1
    print(f"  ✓ {webp_count} derivativos .webp disponíveis\n")

    total_pages = 0
    sitemap_paths = list(STATIC_PAGE_PATHS) + ["/case/", "/case/catalogo/", "/dynapac/"]

    # 1. Página índice do catálogo CASE em /case/catalogo/
    # (/case/index.html é a home da marca, arquivo estático versionado — não gerar por cima)
    print("[1/N] Gerando /case/catalogo/index.html ...")
    idx_html = generate_products_index(db)
    catalogo_dir = OUT_DIR / "catalogo"
    catalogo_dir.mkdir(parents=True, exist_ok=True)
    (catalogo_dir / "index.html").write_text(idx_html, encoding="utf-8")
    total_pages += 1
    print("  ✓ case/catalogo/index.html")

    # 2. Páginas de categoria e produto
    for cat_entry in db:
        category = cat_entry["category"]
        models = [m for m in cat_entry["models"] if get_model_slug(m["path"]) not in EXCLUDED_MODEL_SLUGS]
        cat_entry = {**cat_entry, "models": models}
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
        sitemap_paths.append(f"/case/{cat_slug}/")
        print(f"  ✓ case/{cat_slug}/index.html")

        # Páginas de produto
        for model in models:
            model_slug = get_model_slug(model["path"])
            model_dir = cat_dir / model_slug
            model_dir.mkdir(exist_ok=True)

            print(f"  Gerando {model['title']} ...")
            prod_html = generate_product_page(model, category, cat_slug)
            (model_dir / "index.html").write_text(prod_html, encoding="utf-8")
            total_pages += 1
            sitemap_paths.append(f"/case/{cat_slug}/{model_slug}/")
            print(f"  ✓ case/{cat_slug}/{model_slug}/index.html")

    # 3. Páginas institucionais
    print("\n[Institucional] Gerando páginas institucionais ...")
    total_pages += generate_institutional_pages()

    # 3a-bis. Páginas Dynapac
    print("\n[Dynapac] Gerando páginas da marca ...")
    total_pages += generate_dynapac(sitemap_paths)

    # 3b. Página de consórcio
    consorcio_dir = BASE_DIR / "consorcio"
    consorcio_dir.mkdir(exist_ok=True)
    (consorcio_dir / "index.html").write_text(generate_consorcio_page(), encoding="utf-8")
    total_pages += 1
    print("  ✓ consorcio/index.html")

    # 4. Sitemap e robots.txt
    print("\n[SEO] Gerando sitemap.xml e robots.txt ...")
    generate_sitemap(sitemap_paths)

    print(f"\n=== {total_pages} páginas geradas em /case/ ===")


if __name__ == "__main__":
    main()
