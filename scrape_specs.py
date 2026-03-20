#!/usr/bin/env python3.11
"""
Scraping completo de fichas técnicas - CASE Construction
Extrai specs do __JSS_STATE__ (Sitecore CMS) e salva em content.md enriquecido
"""

import argparse
import json
import re
import sys
import time
from pathlib import Path
from bs4 import BeautifulSoup

BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / "Scrape Case" / "scrape_db.json"
BASE_URL = "https://www.casece.com"


def get_model_url(model_path: str) -> str:
    """Extrai URL canônica do modelo a partir do path no banco de dados."""
    parts = model_path.split("/")
    try:
        prod_idx = parts.index("produtos")
        cat_slug = parts[prod_idx + 1]
        model_slug = parts[-1].lower()
        return f"{BASE_URL}/pt-br/southamerica/produtos/{cat_slug}/{model_slug}"
    except (ValueError, IndexError):
        return None


def get_category_slug(model_path: str) -> str:
    parts = model_path.split("/")
    try:
        prod_idx = parts.index("produtos")
        return parts[prod_idx + 1]
    except (ValueError, IndexError):
        return ""


def strip_html(html_str: str) -> str:
    """Remove tags HTML e limpa o texto."""
    if not html_str:
        return ""
    soup = BeautifulSoup(html_str, "html.parser")
    return soup.get_text(separator=" ").strip()


def html_list_to_markdown(html_str: str) -> str:
    """Converte lista HTML em markdown."""
    if not html_str:
        return ""
    soup = BeautifulSoup(html_str, "html.parser")
    lines = []
    for li in soup.find_all("li"):
        indent = "  " if "ql-indent-1" in li.get("class", []) else ""
        text = li.get_text(strip=True)
        if text:
            lines.append(f"{indent}- {text}")
    return "\n".join(lines)


def fetch_page(url: str):
    """Faz scraping de uma URL usando StealthyFetcher."""
    from scrapling.fetchers import StealthyFetcher
    page = StealthyFetcher.fetch(
        url,
        headless=True,
        network_idle=True,
        disable_resources=False,
        timeout=60000,
        wait=2000,
    )
    return page


def extract_jss_state(html_content: str) -> dict:
    """Extrai o __JSS_STATE__ do HTML da página."""
    match = re.search(
        r'<script type="application/json" id="__JSS_STATE__">(.*?)</script>',
        html_content,
        re.DOTALL,
    )
    if not match:
        return {}
    return json.loads(match.group(1))


def parse_model_data(jss_data: dict) -> dict:
    """Extrai dados estruturados do produto a partir do JSS_STATE."""
    result = {
        "title": "",
        "description": "",
        "summary_specs": [],
        "tech_specs": [],
        "standard_equipment": [],
        "gallery_assets": [],
        "brochures": [],
    }

    try:
        route = jss_data["sitecore"]["route"]
        main = route["placeholders"]["jss-main"]
    except (KeyError, TypeError):
        return result

    for item in main:
        comp = item.get("componentName", "")
        api = item.get("fields", {}).get("apiData", {})
        if not api:
            continue

        # Título, descrição e quick specs
        if comp in ("ProductSeoTags", "ProductModelDetailHeroSection"):
            if not result["title"] and api.get("title"):
                result["title"] = strip_html(api["title"])
            if not result["description"] and api.get("description"):
                result["description"] = strip_html(api["description"])
            if not result["summary_specs"] and api.get("summarySpecs"):
                for s in api["summarySpecs"]:
                    key = strip_html(s.get("key", "")).strip()
                    val = s.get("value", "").strip()
                    if key and val:
                        result["summary_specs"].append({"key": key, "value": val})

        # Tabela de especificações técnicas numéricas
        elif comp == "ProductModelSpecifications":
            models_list = api.get("models", [])
            if models_list:
                # Pega o primeiro modelo (versão principal)
                model = models_list[0]
                for spec_group in model.get("specs", []):
                    group_name = spec_group.get("group", "")
                    items = []
                    for spec_item in spec_group.get("items", []):
                        key = strip_html(spec_item.get("key", "")).strip()
                        val = strip_html(spec_item.get("value", "")).strip()
                        if key and val and val != "-":
                            items.append({"key": key, "value": val})
                    if items:
                        result["tech_specs"].append({"group": group_name, "items": items})

        # Equipamento padrão / features
        elif comp == "ProductModelDetailsSpecificationTable":
            groups = api.get("groups", [])
            for group in groups:
                group_title = strip_html(group.get("title", ""))
                items = []
                for feat in group.get("items", []):
                    feat_title = strip_html(feat.get("title", ""))
                    for col in feat.get("columns", []):
                        short_desc = col.get("shortDescription", "")
                        md = html_list_to_markdown(short_desc)
                        if md:
                            items.append({"title": feat_title, "content": md})
                if items:
                    result["standard_equipment"].append({
                        "group_title": group_title,
                        "items": items
                    })

        # Galeria de imagens
        elif comp == "ProductModelDetailMediaGallery":
            for asset in api.get("assets", []):
                url = asset.get("url", "")
                if url:
                    result["gallery_assets"].append(url)

        # Brochures / PDFs
        elif comp == "ProductFloatingMenu":
            for brochure in api.get("brochures", []):
                title = strip_html(brochure.get("title", ""))
                url = brochure.get("url", "")
                if url:
                    result["brochures"].append({"title": title, "url": url})

    return result


def build_content_md(data: dict, model_path: str, category: str, url: str, existing_assets: list) -> str:
    """Monta o arquivo content.md enriquecido."""
    lines = []

    title = data["title"] or Path(model_path).name.upper()
    lines.append(f"# {title}")
    lines.append(f"**URL**: {url}")
    lines.append(f"**Categoria**: {category}")
    lines.append("")

    # Descrição
    if data["description"]:
        lines.append("## Descrição")
        lines.append(data["description"])
        lines.append("")

    # Quick specs
    if data["summary_specs"]:
        lines.append("## Especificações Rápidas")
        for s in data["summary_specs"]:
            lines.append(f"- **{s['key']}**: {s['value']}")
        lines.append("")

    # Especificações técnicas completas
    if data["tech_specs"]:
        lines.append("## Especificações Técnicas")
        for group in data["tech_specs"]:
            lines.append(f"### {group['group']}")
            for item in group["items"]:
                lines.append(f"- **{item['key']}**: {item['value']}")
            lines.append("")

    # Equipamento padrão
    if data["standard_equipment"]:
        lines.append("## Equipamento Padrão")
        for eq_group in data["standard_equipment"]:
            if eq_group["group_title"]:
                lines.append(f"### {eq_group['group_title']}")
            for item in eq_group["items"]:
                if item["title"]:
                    lines.append(f"#### {item['title']}")
                lines.append(item["content"])
                lines.append("")

    # Assets
    all_assets = list(existing_assets)
    if data["gallery_assets"]:
        lines.append("## Galeria")
        for img_url in data["gallery_assets"]:
            lines.append(f"- {img_url}")
        lines.append("")

    if all_assets:
        lines.append("## Assets Locais")
        for asset in all_assets:
            # Relativizar o path
            rel = asset.replace(f"{model_path}/", "")
            lines.append(f"- {rel}")
        lines.append("")

    # Brochures
    if data["brochures"]:
        lines.append("## Brochures / Documentos")
        for b in data["brochures"]:
            lines.append(f"- [{b['title']}]({b['url']})")
        lines.append("")

    return "\n".join(lines)


def scrape_model(model: dict, category: str) -> bool:
    """Scraping completo de um modelo. Retorna True se sucesso."""
    model_path = model["path"]
    content_path = BASE_DIR / model_path / "content.md"
    existing_assets = model.get("assets", [])

    url = get_model_url(model_path)
    if not url:
        print(f"  [ERRO] Não foi possível derivar URL de: {model_path}")
        return False

    print(f"  Scraping: {url}")

    try:
        page = fetch_page(url)
        if page.status != 200:
            print(f"  [ERRO] HTTP {page.status} para {url}")
            return False

        jss_data = extract_jss_state(page.html_content)
        if not jss_data:
            print(f"  [AVISO] JSS_STATE não encontrado em {url}")
            return False

        data = parse_model_data(jss_data)

        # Verificar se specs foram extraídas
        specs_count = len(data["tech_specs"])
        equip_count = len(data["standard_equipment"])
        print(f"    → {specs_count} grupos de specs, {equip_count} grupos de equipamento padrão")

        content_md = build_content_md(
            data, model_path, category, url, existing_assets
        )

        # Salvar content.md
        content_path.write_text(content_md, encoding="utf-8")
        print(f"    ✓ Salvo: {content_path}")
        return True

    except Exception as e:
        print(f"  [ERRO] {type(e).__name__}: {e}")
        return False


def update_db_with_specs(db: list):
    """Adiciona flag 'specs_scraped' no scrape_db.json."""
    # Lê content.md de cada modelo e extrai summary specs para o JSON
    for cat in db:
        for model in cat["models"]:
            content_path = BASE_DIR / model["path"] / "content.md"
            if content_path.exists():
                content = content_path.read_text(encoding="utf-8")
                # Extrai quick specs do markdown
                specs = {}
                for line in content.split("\n"):
                    if line.startswith("- **") and "**: " in line:
                        parts = line[4:].split("**: ", 1)
                        if len(parts) == 2:
                            key = parts[0].strip()
                            val = parts[1].strip()
                            specs[key] = val
                if specs:
                    model["specs"] = specs
                model["specs_scraped"] = True
    return db


def main():
    parser = argparse.ArgumentParser(
        description="Atualiza content.md e scrape_db.json a partir do __JSS_STATE__ do site CASE.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Retorna código de saída 1 se algum modelo falhar, em vez de esconder o refresh parcial.",
    )
    parser.add_argument(
        "--pause-ms",
        type=int,
        default=1500,
        help="Pausa entre requisições, em milissegundos. Padrão: 1500.",
    )
    args = parser.parse_args()

    print("=== SCRAPING FICHAS TÉCNICAS CASE ===\n")

    db = json.loads(DB_PATH.read_text(encoding="utf-8"))

    total = sum(len(cat["models"]) for cat in db)
    done = 0
    failed = []

    for cat_entry in db:
        category = cat_entry["category"]
        models = cat_entry["models"]
        print(f"\n[{category}] ({len(models)} modelos)")

        for model in models:
            done += 1
            print(f"  [{done}/{total}] {model['title']}")
            success = scrape_model(model, category)
            if not success:
                failed.append(model["title"])
            # Pequena pausa para não sobrecarregar o servidor
            time.sleep(max(args.pause_ms, 0) / 1000)

    # Atualizar scrape_db.json com specs básicas
    print("\n\nAtualizando scrape_db.json...")
    updated_db = update_db_with_specs(db)
    DB_PATH.write_text(
        json.dumps(updated_db, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    print("✓ scrape_db.json atualizado")

    print(f"\n=== RESUMO ===")
    print(f"✓ Sucesso: {done - len(failed)}/{total}")
    if failed:
        print(f"✗ Falhas ({len(failed)}):")
        for f in failed:
            print(f"  - {f}")
        if args.strict:
            print("\n[STRICT] Refresh incompleto: pelo menos um modelo falhou.", file=sys.stderr)
            raise SystemExit(1)


if __name__ == "__main__":
    main()
