# Deploy — Cloudflare Pages

Pipeline: push na `main` → GitHub Actions roda `npm run rebuild:site` (generate → build → verify) → `wrangler pages deploy dist`.

Workflow: `.github/workflows/deploy.yml`. PRs rodam build + verify sem deploy.

## Setup único (uma vez)

### 1. Cloudflare

1. Criar conta/usar conta Cloudflare e criar o projeto Pages:
   ```bash
   npx wrangler pages project create ibl-site --production-branch=main
   ```
2. Criar API Token em https://dash.cloudflare.com/profile/api-tokens com permissão **Cloudflare Pages — Edit**.
3. Anotar o **Account ID** (dashboard → Workers & Pages → visão geral, coluna direita).

### 2. GitHub — Secrets e Variables

Em `Settings → Secrets and variables → Actions` do repo:

**Secrets:**

| Nome | Valor |
|---|---|
| `CLOUDFLARE_API_TOKEN` | token criado acima |
| `CLOUDFLARE_ACCOUNT_ID` | account id |
| `VITE_LEAD_WEBHOOK_URL` | URL pública do endpoint de leads do ibl-ai-os (deixar vazio até existir — site degrada para fallback WhatsApp) |

**Variables:**

| Nome | Valor |
|---|---|
| `VITE_GA4_ID` | ID da propriedade GA4 (ex: `G-XXXXXXXXXX`) |
| `VITE_WHATSAPP_NUMBER` | WhatsApp comercial E.164 sem `+` (ex: `556733584100`) |
| `VITE_LEAD_SLA_HOURS` | `2` |

### 3. Domínio

1. Pages → projeto `ibl-site` → Custom domains → adicionar `iblmaquinas.com.br` (e `www`).
2. Se o DNS não estiver na Cloudflare: criar CNAME `iblmaquinas.com.br → ibl-site.pages.dev` no provedor atual, ou migrar o DNS para a Cloudflare (recomendado — SSL e redirects automáticos).
3. **Atenção:** o domínio hoje serve o site WordPress antigo (`www.iblmaquinas.com.br`). A troca de DNS é o momento do cutover — fazer só depois do go-live aprovado.
4. Configurar redirect `www → apex` (ou o inverso, mas escolher um canônico; o `<link rel="canonical">` do site usa apex sem `www`).

### 4. Pós-deploy (primeira vez)

1. Google Search Console: verificar propriedade do domínio e submeter `https://iblmaquinas.com.br/sitemap.xml`.
2. Testar formulário de lead em produção (estado `success` com webhook, ou `skipped` → WhatsApp).
3. Conferir GA4 recebendo eventos (`lead_submit_attempt`, etc.).

## Pendências de ambiente (fora do repo)

- [ ] Confirmar número WhatsApp Business oficial (hoje: telefone da matriz)
- [ ] Expor endpoint de leads do ibl-ai-os (auth + CORS para `iblmaquinas.com.br`) e preencher `VITE_LEAD_WEBHOOK_URL`
- [ ] Criar propriedade GA4 e preencher `VITE_GA4_ID`
- [ ] Acesso ao DNS de `iblmaquinas.com.br` para o cutover
