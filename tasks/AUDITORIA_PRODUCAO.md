# Auditoria Técnica + Plano de Produção — ibl-site

> Data: 2026-06-10
> Auditor: Claude (webdesign + dev senior)
> Baseline auditado: `v1.1` (commit `bc99c51`), launch gates documentados em `docs/LAUNCH-GATE.md`
> Objetivo: site profissional em produção, captando leads e apresentando produtos de forma completa

---

## 1. Diagnóstico Geral

O projeto está em um estado **muito melhor do que a média**: milestones v1.0 e v1.1 shipped com gates automatizados (smoke + lead success/failure), `verify:dist` passando hoje, SEO on-page sólido (lang pt-BR, meta description, OG, canonical, JSON-LD Organization/WebSite/Product com specs reais), 32 modelos em 8 categorias com páginas geradas, e lead capture com webhook + fallback WhatsApp + estados observáveis.

**Porém o site NÃO pode ir ao ar hoje.** Os bloqueadores não são de engenharia — são de dados reais, integração e infra de deploy.

### Scorecard

| Dimensão | Nota | Resumo |
|---|---|---|
| Engenharia / build | 9/10 | Pipeline disciplinado, gates, verify-dist OK |
| Lead capture (código) | 8/10 | Robusto, mas aponta para mock localhost |
| SEO on-page | 7/10 | Meta/OG/JSON-LD bons; falta sitemap/robots/404 |
| Conteúdo institucional | 3/10 | Zero páginas: Sobre, Filiais, Contato, Privacidade |
| Dados reais | 2/10 | WhatsApp placeholder, GA4 vazio, webhook mock |
| Performance | 5/10 | SVGs de 4–7MB, 25 PNG vs 1 WebP, fonts/icons via CDN |
| Deploy / infra | 0/10 | Nenhum hosting, CI/CD, DNS configurado no repo |
| Conformidade LGPD | 1/10 | Form coleta dados pessoais sem política/consentimento |

---

## 2. Bloqueadores P0 (impedem go-live)

### P0-1. WhatsApp é número FAKE baked no build
- `wa.me/5567999999999` está em `index.html:713` e compilado em `dist/assets/index-*.js`, `main-*.js`, `mobile-*.js`.
- DDD 67 (MS) nem corresponde à IBL (Cuiabá/MT = 65). Todo lead de fallback iria para número inexistente.
- **Ação:** centralizar o número em env/config (`VITE_WHATSAPP_NUMBER`), substituir em `index.html`, `main.js`, `mobile/main.js`, `generate_pages.py`, rebuildar.

### P0-2. Webhook de leads aponta para mock local
- `.env.example`: `VITE_LEAD_WEBHOOK_URL=http://127.0.0.1:8787/lead`.
- O endpoint real do `ibl-ai-os` precisa estar exposto publicamente (com auth/token + CORS para o domínio do site). O launch gate validou só o contrato com mock — a aceitação do endpoint real está explicitamente pendente (`docs/LAUNCH-READINESS.md`, "Bounded Remainder").
- **Ação:** deployar/expor endpoint de leads do ibl-ai-os, configurar `VITE_LEAD_WEBHOOK_URL` de produção, rodar `launch:gate:lead` contra ele.

### P0-3. Sem analytics
- `VITE_GA4_ID=` vazio. O código de `gtag` existe e trackEvents estão instrumentados (`lead_submit_attempt`, etc.) — só falta o ID.
- **Ação:** criar propriedade GA4, preencher env, validar eventos.

### P0-4. Sem deploy / CI/CD / hosting
- Nenhum `vercel.json`, `netlify.toml`, `.github/workflows`. O `dist/` (63MB) só existe localmente.
- Canonical já assume `https://iblmaquinas.com.br/` — verificar propriedade do domínio, DNS e SSL.
- **Ação:** escolher hosting estático (Cloudflare Pages ou Vercel — ambos servem 63MB sem custo relevante), pipeline GitHub Actions: `generate:pages → build → verify:dist → deploy`.

### P0-5. LGPD
- O formulário coleta nome/telefone (dados pessoais) e envia para webhook + localStorage (`ibl_lead_ops_v1`) sem política de privacidade nem consentimento.
- **Ação:** página `/privacidade/`, checkbox/aviso de consentimento no form, link no footer.

---

## 3. Gaps P1 (profissionalismo e conversão)

1. **Páginas institucionais inexistentes:** Sobre a IBL, Contato, **Filiais (8 filiais — zero menções a "filial" na homepage!)**, Pós-venda/Peças como páginas dedicadas (hoje só âncoras `#captacao-lead`). Para um dealer regional, a página de filiais com endereços/telefones/mapa é fator de confiança nº 1 e SEO local.
2. **SEO local zero:** sem `LocalBusiness` JSON-LD por filial, sem Google Business Profile linkado, `sameAs: []` vazio no Organization.
3. **Sem `sitemap.xml` e `robots.txt`** — gerar no `generate_pages.py` (todas as ~45 rotas).
4. **Sem `404.html`.**
5. **Title amador:** "IBL Máquinas | Case Construction 2026 - Industrial Edition" — "Industrial Edition" é codename de design, não título de produção. Sugestão: "IBL Máquinas | Concessionária CASE Construction — Vendas, Peças e Serviços".
6. **OG image = logo PNG** — criar imagem social 1200×630 real.
7. **Catálogo desbalanceado:** rolo-compactador (1 modelo), miniescavadeiras (2), retroescavadeiras (2). Linha Dynapac ausente (o negócio é dealer Case **e Dynapac**).

---

## 4. Débitos P2 (performance e manutenção)

1. **Imagens pesadas:** `fotos-processed/*.svg` com 4–7MB cada (bitmaps embutidos em SVG — converter para WebP/AVIF), jpg de 8,4MB em rolo-compactador. 25 PNG vs 1 WebP.
2. **Duplicação desktop/mobile:** `mobile/main.js` (1.790 linhas) espelha `main.js` — débito já reconhecido no audit v1.1. Médio prazo: unificar com CSS responsivo.
3. **Dependências CDN sem pin:** `unpkg.com/@phosphor-icons/web` (sem versão fixa — risco de quebra silenciosa) e Google Fonts (CLS). Self-host ambos.
4. **Hero depende de metadata por modelo** (debt aceito v1.1) — documentar processo ao adicionar modelo novo.

---

## 5. Plano de Execução (proposto como milestone v1.2 — "Production Go-Live")

### Fase 1 — Dados reais e integração (P0) — ~1 dia
- [ ] Coletar do Valternei/IBL: número WhatsApp comercial oficial, telefones e endereços das 8 filiais, CNPJ/razão social para footer e privacidade
- [ ] Centralizar WhatsApp em `VITE_WHATSAPP_NUMBER` e substituir placeholder em todos os pontos
- [ ] Expor endpoint de leads do ibl-ai-os (auth token + CORS) e configurar `VITE_LEAD_WEBHOOK_URL` de produção
- [ ] Criar GA4 e preencher `VITE_GA4_ID`
- [ ] Corrigir `<title>` e OG titles
- [ ] Rodar `launch:gate:lead` contra endpoint real

### Fase 2 — Deploy e SEO técnico — ~1 dia
- [ ] Hosting estático (Cloudflare Pages ou Vercel) + DNS `iblmaquinas.com.br` + SSL
- [ ] GitHub Actions: `generate:pages → build:site → verify:dist → deploy` em push na main
- [ ] Gerar `sitemap.xml` + `robots.txt` no `generate_pages.py`
- [ ] `404.html`
- [ ] OG image 1200×630
- [ ] Google Search Console + submissão do sitemap

### Fase 3 — Conteúdo institucional e LGPD — ~2 dias
- [ ] Página `/filiais/` com as 8 filiais (endereço, telefone, mapa, JSON-LD LocalBusiness cada)
- [ ] Página `/sobre/` (história, marcas representadas, território)
- [ ] Página `/contato/` (form + filiais resumidas)
- [ ] Página `/privacidade/` + consentimento no formulário de lead
- [ ] Seção "Nossas Filiais" na homepage + links no footer

### Fase 4 — Performance — ~1 dia
- [ ] Converter SVGs gigantes e PNGs para WebP (target: nenhuma imagem >300KB)
- [ ] Comprimir jpg de 8,4MB do rolo-compactador
- [ ] Self-host fonts e phosphor-icons (ou pin de versão)
- [ ] `loading="lazy"` em imagens fora da dobra; Lighthouse ≥90 mobile

### Fase 5 — Catálogo e crescimento (pós go-live)
- [ ] Linha Dynapac (compactação) — hoje ausente
- [ ] Completar categorias magras (miniescavadeiras, rolos)
- [ ] Unificar desktop/mobile (eliminar débito v1.1)
- [ ] Meta Pixel / remarketing se houver mídia paga

**Go-live possível ao fim da Fase 2** (com aviso LGPD mínimo no form antecipado da Fase 3, se necessário).

---

## 6. Informações que dependem do negócio (bloqueiam Fase 1)

1. Número de WhatsApp comercial oficial (com DDD correto)
2. Endereços/telefones/horários das 8 filiais
3. Confirmação do domínio `iblmaquinas.com.br` (registro e acesso ao DNS)
4. Acesso à conta Google (GA4 / Search Console / Business Profile)
5. Decisão: incluir Dynapac no go-live ou depois?
6. CNPJ/razão social para rodapé e política de privacidade
