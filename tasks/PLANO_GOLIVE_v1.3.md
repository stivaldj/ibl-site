# Plano de Desenvolvimento — v1.3 "Production Go-Live" (ibl-site)

> Data: 2026-07-29
> Referências: `tasks/AUDITORIA_PRE_DEPLOY_2026-07-29.md` (auditoria delta), `tasks/AUDITORIA_PRODUCAO.md`, `docs/OPERATIONS.md`, `docs/DEPLOY.md`
> Executor: Claude (com pontos de decisão/insumo marcados como **[VOCÊ]**)
> Meta: site em produção em `https://iblmaquinas.com.br`, medindo tráfego (GA4) e entregando leads ao CRM (ibl-ai-os), servido via cPanel.

---

## Decisões tomadas (registradas)

| Decisão | Escolha | Observação |
|---|---|---|
| Hospedagem | **cPanel (servidor próprio)** | O pipeline Cloudflare Pages existente (`.github/workflows/deploy.yml`) será convertido em CI de verificação (build + verify em PR, sem deploy) |
| Leads | **WhatsApp-only no lançamento** (decisão final 2026-07-29) | O webhook do ibl-ai-os (rota `/lead` ainda inexistente) passa a ser a Fase 4 **pós-go-live** — o site degrada com segurança para o fallback WhatsApp |
| GA4 | Conta `334862278` | Falta o **Measurement ID do fluxo de dados web (`G-XXXXXXXXXX`)** — o número informado é o ID da conta, não serve no `VITE_GA4_ID` |
| `/mobile/` | **Remover do build** (recomendação aceita por ausência de preferência) | Página órfã e duplicada; a home já é responsiva. Reversível via git |
| Escopo | **Go-live completo** | P0 + P1 + otimização de imagens |

---

## Fase 0 — Insumos e acessos **[VOCÊ]** (paralelo às fases 1–3)

Nada aqui bloqueia as fases 1–3; bloqueia apenas as fases 5–6.

- [ ] **GA4:** na conta 334862278, criar uma propriedade GA4 com fluxo de dados web para `iblmaquinas.com.br` e me passar o Measurement ID (`G-XXXXXXXXXX`). Alternativa: se preferir, com o Chrome conectado eu mesmo crio pela sua sessão logada — basta autorizar.
- [ ] **WhatsApp:** confirmar que `67 3358-4100` é o WhatsApp Business oficial de vendas (todo lead do site passa por ele; está marcado `TODO_CONFIRMAR` no código).
- [ ] **cPanel:** informar como o site chega ao servidor — (a) você mesmo faz o upload do `dist/` que eu entregar zipado; (b) me passa acesso FTP/File Manager para eu subir via Chrome; ou (c) outro fluxo.
- [ ] **WordPress atual:** confirmar se o WordPress antigo (`www.iblmaquinas.com.br`) roda **no mesmo cPanel** (aí o deploy substitui o `public_html` e exige backup antes) ou em outro servidor (aí haverá cutover de DNS).
- [ ] **ibl-ai-os em produção:** confirmar se o `dashboard-api` já roda em algum servidor com URL pública. Isso define a opção A ou B da Fase 4.
- [ ] Validar os números de prova social ("+250 operações/ano", "SLA 2h de 1º contato") com o comercial — ou autorizo ajuste/remoção.

---

## Fase 1 — Correções de conteúdo e confiança (P1) — [Claude]

- [ ] Remover `/mobile/` do build: tirar dos inputs do `vite.config.js`, do `verify-dist.mjs`, do `generate_pages.py` (sitemap) e do `robots.txt` (o `Disallow: /mobile/` deixa de ser necessário)
- [ ] Favicon real: gerar `favicon.ico` (32×32 multi-size) + `apple-touch-icon.png` 180×180 a partir do logo, com fundo adequado, e referenciar no `<head>` de todas as páginas (estáticas + `generate_pages.py`)
- [ ] OG image 1200×630 (`public/og-image.jpg`): máquina + logo IBL, aplicada como default em todas as páginas não-produto (produtos continuam com a foto do modelo)
- [ ] Substituir a foto Unsplash da seção Tecnologia por imagem local otimizada (baixar/otimizar ou usar foto real do acervo `fotos/`)
- [ ] Status das unidades: trocar "Aberto" fixo por cálculo via JS pelo horário local da filial (fallback: exibir horário de funcionamento em vez de status)
- [ ] Copy honesto: "TELEMETRIA ONLINE" → indicador neutro; chat "Online agora" → "Resposta rápida via WhatsApp" (mantendo o widget e o fluxo)
- [ ] `sameAs` do JSON-LD Organization: incluir Instagram (`instagram.com/iblmaquinas`)
- [ ] Ajustar texto da página Sobre re: Dynapac (representada desde 2004, mas sem linha no catálogo) para não gerar expectativa — ou nota "linha Dynapac sob consulta"
- **Verificação:** `npm run rebuild:site` + gates smoke; conferência visual das páginas alteradas; grep confirmando zero referências a `/mobile/`, Unsplash e status hardcoded no dist

## Fase 2 — Performance — [Claude]

- [ ] Converter para WebP as ~12 imagens entre 600KB–1MB (`*-nobg.png`, JPGs de produto), meta <300KB cada, atualizando referências no `generate_pages.py`/HTML (com fallback quando necessário)
- [ ] Phosphor Icons: self-host (copiar CSS+fontes para `public/vendor/`) ou, no mínimo, carregar com `defer` — eliminar script síncrono bloqueante no `<head>`
- [ ] Leaflet: self-host os arquivos hoje puxados de unpkg em runtime (mapa das unidades)
- [ ] Google Fonts: avaliar self-host (Archivo, Inter, JetBrains Mono via woff2 locais); se o ganho compensar, aplicar — senão manter com `preconnect` (já existe)
- **Verificação:** rebuild + gates; peso total das imagens antes/depois; nenhuma request a unpkg/unsplash no dist; Lighthouse local (mobile) ≥ 90 em Performance como alvo

## Fase 3 — Infra cPanel — [Claude]

- [ ] Criar `public/.htaccess` (entra no dist em todo build): HTTPS forçado + www→apex, `ErrorDocument 404 /404.html`, gzip, cache (HTML no-cache, assets com hash imutáveis, imagens 1 mês), `Options -Indexes`, headers de segurança
- [ ] Converter `.github/workflows/deploy.yml` em CI de verificação: `generate → build → verify` em push/PR, **sem** etapa de deploy Cloudflare (removendo a dependência dos secrets)
- [ ] Criar `scripts/package-deploy.mjs` (ou make target): gera `dist/` limpo e empacota `ibl-site-deploy-YYYYMMDD.zip` pronto para extrair no `public_html`
- [ ] Documentar em `docs/DEPLOY-CPANEL.md`: passo a passo do upload, backup do WordPress, ativação de SSL (AutoSSL), teste do `.htaccess`
- **Verificação:** dist limpo com ~5 arquivos em `assets/`, `.htaccess` presente, zip íntegro; CI verde

## Fase 4 — Webhook de leads (ibl-ai-os) — [Claude + VOCÊ] — **PÓS-GO-LIVE**

> Decisão final: o site lança com fallback WhatsApp (estado `skipped`, já robusto). Esta fase roda após o go-live, sem bloquear o deploy.
> Bloqueio conhecido: não existe rota de ingestão de leads no ibl-ai-os hoje. Duas opções, decididas pelo resultado da Fase 0:

- [ ] **Opção A — dashboard-api já tem host público:** criar rota `POST /public/site-leads` no `services/dashboard-api` com: token de auth via header (secret), CORS restrito a `https://iblmaquinas.com.br`, rate limit básico, validação do payload do site (contrato do `mock-lead-webhook.mjs`), persistência na tabela de leads/oportunidades existente
- [ ] **Opção B — sem host público para o ibl-ai-os:** criar endpoint leve **no próprio cPanel** (`/api/lead.php` ou app Node no Application Manager) que valida token + CORS, grava na base MySQL do CRM (mesma usada pelo ibl-ai-os) e envia notificação por e-mail — o ibl-ai-os consome da base normalmente
- [ ] Configurar `VITE_LEAD_WEBHOOK_URL` de produção no `.env`
- [ ] Rodar `npm run launch:gate:lead` contra o endpoint real (sucesso E falha simulada)
- **Verificação:** lead de teste ponta a ponta aparecendo no destino (tabela/CRM) com todos os campos; estado `success` no site; fallback WhatsApp intacto quando o endpoint cai

## Fase 5 — Configuração final e build de produção — [Claude]

- [ ] `.env` de produção completo: `VITE_GA4_ID` (G-XXXX da Fase 0), `VITE_LEAD_WEBHOOK_URL` (Fase 4), `VITE_WHATSAPP_NUMBER` confirmado, `VITE_LEAD_SLA_HOURS=2`
- [ ] Remover `TODO_CONFIRMAR` do código após confirmação do WhatsApp
- [ ] `rm -rf dist && npm run rebuild:site` (build limpo definitivo)
- [ ] Gates completos: `verify:dist`, `launch:gate:smoke`, `launch:gate:lead`
- [ ] Auditoria do artefato: gtag do GA4 presente no bundle, URL do webhook presente, zero `localhost`, zero assets órfãos, zero `.DS_Store`, `.htaccess` incluído
- [ ] Gerar o pacote de deploy (zip)
- **Verificação:** checklist de artefato 100%; commit + tag `v1.3`

## Fase 6 — Deploy e cutover — [VOCÊ com apoio Claude]

- [ ] **Backup do WordPress atual** (arquivos + banco) antes de qualquer substituição
- [ ] Upload/extração do pacote no `public_html` (ou cutover de DNS, conforme Fase 0)
- [ ] SSL ativo (AutoSSL/Let's Encrypt) para apex e `www`
- [ ] Smoke em produção: home, 2 páginas de produto, formulário de lead ponta a ponta (webhook + fallback), `/rota-inexistente` → 404 customizado, `https://` e `www→apex` redirecionando, `sitemap.xml` e `robots.txt` acessíveis
- [ ] GA4 DebugView recebendo eventos reais (`page_view`, `lead_submit_attempt`)
- **Rollback:** restaurar backup do WordPress / reverter DNS — documentado no `docs/DEPLOY-CPANEL.md`

## Fase 7 — Pós-go-live (primeira semana) — [Claude + VOCÊ]

- [ ] Google Search Console: verificar propriedade e submeter o sitemap **[VOCÊ ou Chrome assistido]**
- [ ] Atualizar Política de Privacidade citando GA4/cookies (e Google Fonts, se mantido externo)
- [ ] Lighthouse produção (mobile + desktop) na home e em 1 PDP — guardar baseline no repo
- [ ] Google Business Profile das 8 filiais vinculado ao site (o JSON-LD LocalBusiness já está pronto) **[VOCÊ]**
- [ ] Monitorar leads nos primeiros dias (SLA de contato + estado `success` vs `skipped`)

---

## Critérios de aceite do "produto final"

1. Site no ar em `https://iblmaquinas.com.br` com SSL, 404 customizado e redirects corretos
2. Formulário de lead com fallback WhatsApp funcional ponta a ponta (integração CRM na Fase 4 pós-go-live)
3. GA4 registrando page views e eventos de conversão
4. Zero dependências de runtime em unpkg/unsplash; imagens ≤300KB; Lighthouse mobile ≥90 (meta)
5. Sitemap submetido no Search Console; dist limpo e reproduzível via `npm run rebuild:site`
6. Rollback documentado e backup do site antigo guardado

## Ordem de execução e estimativa

| Fase | Dependência | Esforço |
|---|---|---|
| 1 — Conteúdo/confiança | nenhuma | ~meio dia |
| 2 — Performance | nenhuma | ~meio dia |
| 3 — Infra cPanel | nenhuma | ~2h |
| 4 — Webhook (pós-go-live) | Fase 0 (decisão A/B) | ~meio dia a 1 dia |
| 5 — Build final | Fases 0–3 | ~2h |
| 6 — Deploy | Fase 5 + acessos | ~2h |
| 7 — Pós-go-live | Fase 6 | contínuo (1ª semana) |

Fases 1, 2 e 3 começam imediatamente e não dependem de nenhum insumo externo.
