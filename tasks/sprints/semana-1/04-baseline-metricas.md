# Semana 1 — Baseline de Métricas

## Objetivo
Estabelecer linha de base para medir evolução de conversão e qualidade de tráfego.

## Instrumentação aplicada no Sprint 1
- Arquivo: `/Users/joseoliveira/CODING/VARIANT/main.js`
- Eventos implementados:
  - `page_view_custom`
  - `cta_click`
  - `scroll_depth` (25/50/75/90)
  - `showcase_model_change`
- Dependência opcional:
  - `VITE_GA4_ID` para envio automático ao GA4 via `gtag`.

## CTAs rastreados
- Home:
  - `header_solicitar_orcamento`
  - `hero_ver_catalogo`
  - `hero_video`
  - `footer_whatsapp`
  - `footer_email`
  - `floating_support_chat`
- Produtos:
  - `produtos_header_solicitar_orcamento`
  - `produtos_footer_whatsapp`
  - `produtos_footer_email`
  - `produtos_floating_support_chat`

## Métricas baseline a coletar (7 dias)
- CTR de CTA principal (home e produtos).
- Scroll depth médio por página.
- Taxa de clique por tipo de contato (WhatsApp x Email x Orçamento).
- Taxa de navegação Home -> Categoria -> Produto.

## Meta inicial (próximo ciclo)
- +15% CTR nos CTAs de topo.
- +20% cliques em CTA contextual de produto.
- Reduzir abandono antes de 50% scroll na home.
