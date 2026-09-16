# Auditoria Pré-Deploy — ibl-site (cPanel)

> Data: 2026-07-29
> Baseline auditado: working tree limpo, último commit `f38b7f9` (2026-06-12), `dist/` gerado em 2026-06-12
> Destino de hospedagem: servidor próprio / cPanel (Apache)
> Referência anterior: `tasks/AUDITORIA_PRODUCAO.md` (2026-06-10) — esta auditoria é o **delta** do que ainda falta

---

## 1. Diagnóstico geral

O site evoluiu muito desde a auditoria de 10/06. Do que era bloqueador lá, **já está resolvido**: páginas institucionais (Sobre, Filiais, Contato, Consórcio, Privacidade) existem e são completas; `sitemap.xml` (45 URLs), `robots.txt` e `404.html` (com `noindex`) estão no build; o title amador foi corrigido; o formulário de lead tem checkbox de consentimento LGPD com link para a política; o WhatsApp foi centralizado em env com número real da matriz; o Phosphor Icons foi pinado na versão 2.1.1; as imagens gigantes de 4–7MB foram reduzidas (hoje a maior tem ~1MB).

A qualidade de SEO on-page está **acima da média do setor**: as 49 páginas do dist têm `lang="pt-BR"`, title, description, canonical e OG únicos; JSON-LD rico (LocalBusiness ×8 nas filiais, Product com specs nos modelos, FAQPage no consórcio, BreadcrumbList em tudo); nenhum link ou asset interno quebrado; todas as imagens têm `alt`; 1 `<h1>` por página; nenhum segredo ou URL local vazou nos bundles.

**O que impede o go-live hoje não é engenharia — é configuração de produção e infra do cPanel.** São 4 bloqueadores, todos resolvíveis em poucas horas.

### Scorecard (delta vs. 10/06)

| Dimensão | Antes | Agora | Observação |
|---|---|---|---|
| Engenharia / build | 9/10 | 9/10 | Pipeline e gates mantidos |
| SEO on-page | 7/10 | 9/10 | sitemap/robots/404/JSON-LD completos |
| Conteúdo institucional | 3/10 | 9/10 | Todas as páginas criadas |
| Conformidade LGPD | 1/10 | 7/10 | Política + consentimento OK; citar GA4/fonts quando ativar |
| Dados reais | 2/10 | 6/10 | WhatsApp real; **GA4 e webhook ainda vazios** |
| Performance | 5/10 | 7/10 | Imagens reduzidas; ainda há 12 arquivos de 600KB–1MB |
| Deploy / infra | 0/10 | 2/10 | Destino escolhido (cPanel), mas sem `.htaccess` nem processo |

---

## 2. Bloqueadores — resolver ANTES de subir (P0)

### P0-1. GA4 não está no build
- O bundle atual de `dist/` **não contém** o carregamento do `googletagmanager` — ou seja, o build foi feito com `VITE_GA4_ID` vazio e todo o código de analytics foi eliminado na compilação.
- O próprio `.env.example` marca GA4 como "obrigatório em produção". Sem ele, você lança o site cego: zero medição de tráfego e de conversão de leads (os eventos `lead_submit_*`, `data-track` etc. já estão instrumentados, só falta o ID).
- **Ação:** criar a propriedade GA4, preencher `VITE_GA4_ID` no `.env` de produção e rebuildar.

### P0-2. Webhook de leads não configurado — nenhum lead chega ao CRM
- O bundle atual não tem URL de webhook: todo envio do formulário cai no estado `skipped` e o lead **só** segue pelo fallback WhatsApp. Nada é registrado no ibl-ai-os.
- O comportamento é seguro (degrada bem), mas é uma **decisão de negócio** que precisa ser explícita:
  - **Opção A:** expor o endpoint de leads do ibl-ai-os publicamente (com token de auth + CORS restrito a `iblmaquinas.com.br`), preencher `VITE_LEAD_WEBHOOK_URL` e validar com `npm run launch:gate:lead` contra o endpoint real.
  - **Opção B:** lançar conscientemente só com WhatsApp e ativar o webhook depois (deixar documentado).
- **Ação:** decidir A ou B antes do rebuild final.

### P0-3. Sem `.htaccess` — em cPanel o 404 e o HTTPS não funcionam sozinhos
- Não existe `.htaccess` em lugar nenhum do projeto. Em Apache/cPanel isso significa: o `404.html` **nunca será servido** (o Apache mostrará o 404 genérico dele), sem redirecionamento forçado para HTTPS, sem unificação www/apex (risco de conteúdo duplicado — o canonical assume `https://iblmaquinas.com.br/` sem www), sem compressão gzip e sem headers de cache.
- **Ação:** criar `public/.htaccess` (assim ele entra automaticamente no `dist/` em todo build). Conteúdo sugerido:

```apache
# --- HTTPS + domínio canônico (sem www) ---
RewriteEngine On
RewriteCond %{HTTPS} off [OR]
RewriteCond %{HTTP_HOST} ^www\. [NC]
RewriteRule ^(.*)$ https://iblmaquinas.com.br/$1 [L,R=301]

# --- Página de erro ---
ErrorDocument 404 /404.html

# --- Compressão ---
<IfModule mod_deflate.c>
  AddOutputFilterByType DEFLATE text/html text/css text/javascript application/javascript application/json image/svg+xml application/xml
</IfModule>

# --- Cache ---
<IfModule mod_expires.c>
  ExpiresActive On
  ExpiresByType text/html "access plus 0 seconds"
  ExpiresByType text/css "access plus 1 year"
  ExpiresByType application/javascript "access plus 1 year"
  ExpiresByType image/png "access plus 1 month"
  ExpiresByType image/jpeg "access plus 1 month"
  ExpiresByType image/webp "access plus 1 month"
  ExpiresByType image/svg+xml "access plus 1 month"
  ExpiresByType image/x-icon "access plus 1 month"
</IfModule>
# Assets com hash no nome podem ser imutáveis
<FilesMatch "-[A-Za-z0-9_-]{8}\.(js|css)$">
  Header set Cache-Control "public, max-age=31536000, immutable"
</FilesMatch>

# --- Segurança básica ---
Options -Indexes
<IfModule mod_headers.c>
  Header set X-Content-Type-Options "nosniff"
  Header set Referrer-Policy "strict-origin-when-cross-origin"
  Header set X-Frame-Options "SAMEORIGIN"
</IfModule>
```

### P0-4. `dist/` está sujo — não subir como está
- **70 dos 75 arquivos** em `dist/assets/` são bundles de builds antigos (~3,4MB de lixo acumulado; só 5 são referenciados pelas páginas). Há também 1 `.DS_Store` dentro de `dist/produtos/`.
- Subir isso funciona, mas polui o servidor e mascara qual bundle é o vigente.
- **Ação:** `rm -rf dist && npm run rebuild:site` **depois** de configurar o `.env` de produção (P0-1/P0-2) e criar o `.htaccess` (P0-3). Um rebuild limpo garante que tudo entra no bundle correto de uma vez.

---

## 3. Importantes — resolver no go-live ou logo após (P1)

1. **`/mobile/` é uma página órfã.** Duplica a home, nenhuma página linka para ela, e não existe nenhum redirect por viewport/user-agent no código — nenhum usuário jamais chegará lá. O `robots.txt` já a bloqueia (dano de SEO contido), mas ela custa manutenção em dobro (o `mobile/main.js` espelha o `main.js`, débito já reconhecido na v1.1). **Recomendo remover do deploy** (tirar do input do `vite.config.js` e do `verify-dist.mjs`) — a home já é responsiva (menu mobile próprio, grids adaptativos). Alternativa: implementar o redirect de fato, mas isso agrava o débito de duplicação.

2. **`favicon.ico` é o `ibl-logo.png` renomeado** — um PNG de 1080×1350 (não quadrado, 70KB) com extensão `.ico`. Vai aparecer distorcido/cortado nas abas e alguns contextos (Google SERP, leitores antigos) podem ignorá-lo. Gerar um favicon real: `.ico` 32×32 + `apple-touch-icon.png` 180×180 + referências no `<head>`.

3. **OG image é o logo 1080×1350.** WhatsApp/LinkedIn/Facebook cortam para 1200×630 — o logo vai aparecer decapitado ao compartilhar o link. Criar uma imagem social 1200×630 (máquina + logo) e usar em todas as páginas (os produtos já usam foto do modelo, o que é bom).

4. **Imagem do Unsplash hotlinked na seção "Tecnologia".** Dependência externa em página de produção (se o Unsplash mudar/remover, quebra) e a foto é genérica de laboratório — não tem relação com telemetria de frota. Baixar e servir local, ou trocar por foto real de operação/painel SiteWatch.

5. **Conteúdo hardcoded que pode minar confiança:**
   - Status **"Aberto"** fixo nas 8 unidades — às 3h da manhã o site dirá que tudo está aberto. Calcular por horário via JS ou trocar por horário de funcionamento.
   - **"TELEMETRIA ONLINE"** no header e **"Online agora"** no chat — o "chat" na verdade redireciona para WhatsApp. Se ninguém responde 24h, ajustar para algo como "Resposta rápida via WhatsApp" evita frustração.
   - Números de prova social ("+250 operações/ano", "SLA 2h") — confirmar com o comercial antes do ar, já que o rodapé da seção de stats os referencia como "histórico interno IBL (2025)".

6. **WhatsApp ainda marcado como `TODO_CONFIRMAR`** no `main.js`, `mobile/main.js` e `generate_pages.py`. O fallback usa a matriz Campo Grande (67 3358-4100). Confirmar com a IBL se esse é o WhatsApp Business oficial de vendas antes do go-live — todo lead do site passa por ele.

7. **`sameAs: []` vazio** no JSON-LD Organization da home — incluir ao menos o Instagram (que já está no footer). Ajuda o Google a consolidar a entidade.

8. **Inconsistência Dynapac:** a página Sobre diz que a IBL representa a Dynapac desde 2004, mas o catálogo é 100% CASE (a categoria rolo compactador tem 1 modelo CASE). Decisão da fase 5 do plano anterior — ou incluir a linha, ou ajustar o texto para não gerar expectativa.

---

## 4. Melhorias pós-go-live (P2)

1. **Imagens:** 12 arquivos entre 600KB e 1MB (PNGs sem fundo e JPGs de produto; o maior: `580n-nobg.png` com 1.050KB). Converter para WebP com meta de <300KB por imagem — é o maior ganho de Lighthouse mobile disponível. O dist total (27MB) é tranquilo para cPanel.
2. **Phosphor Icons é script síncrono no `<head>`** (bloqueia a renderização e é ponto único de falha via unpkg). Self-host ou ao menos `defer`. O Leaflet também vem do unpkg em runtime (mapa das unidades) — self-host junto.
3. **Google Fonts externo:** além do custo de performance (CLS), envia IP dos visitantes ao Google — quando ativar o GA4, atualize a Política de Privacidade citando os terceiros (Google Analytics, Google Fonts, Unsplash se mantiver) e considere self-host das fontes.
4. **Search Console + Business Profile:** após o go-live, verificar o domínio no Google Search Console, enviar o sitemap, e criar/vincular os Google Business Profiles das 8 filiais (o JSON-LD LocalBusiness já está pronto para isso — SEO local é o canal nº 1 de um dealer regional).
5. **CI/CD:** hoje o deploy será upload manual do `dist/`. Vale criar um workflow (GitHub Actions com FTP-deploy, ou script `rsync`) para `generate:pages → build → verify:dist → upload`, eliminando risco de subir build velho.

---

## 5. Checklist de deploy no cPanel (ordem de execução)

1. [ ] Confirmar WhatsApp Business oficial com a IBL (P1-6)
2. [ ] Criar propriedade GA4 → preencher `VITE_GA4_ID` no `.env` (P0-1)
3. [ ] Decidir webhook de leads (expor endpoint do ibl-ai-os **ou** lançar WhatsApp-only) → `VITE_LEAD_WEBHOOK_URL` (P0-2)
4. [ ] Criar `public/.htaccess` com o conteúdo da seção P0-3
5. [ ] Remover `/mobile/` do build (ou decidir mantê-la conscientemente) (P1-1)
6. [ ] `rm -rf dist && npm run rebuild:site` (gera dist limpo com env de produção)
7. [ ] Rodar `npm run launch:gate:smoke` (e `launch:gate:lead` se webhook ativo)
8. [ ] Conferir que `dist/assets/` tem só ~5 arquivos e que o `.htaccess` está no dist
9. [ ] Upload do **conteúdo** de `dist/` para `public_html/` (não a pasta dist em si)
10. [ ] Ativar SSL no cPanel (AutoSSL/Let's Encrypt) para `iblmaquinas.com.br` e `www`
11. [ ] Testar em produção: home, 1 página de produto, formulário de lead (ponta a ponta), `/404-inexistente`, `https://` forçado, `www` redirecionando, `sitemap.xml` acessível
12. [ ] Google Search Console: verificar domínio + enviar sitemap
13. [ ] Rodar Lighthouse (mobile) na home e em 1 produto; guardar baseline

**Estimativa:** P0 completo em meio dia (a maior variável é o endpoint de leads); P1 em 1 dia adicional.

---

## 6. O que NÃO precisa de ação (verificado e aprovado)

- Links e assets internos: **zero quebrados** nas 49 páginas do dist
- Acessibilidade básica: todas as `<img>` com `alt`, labels nos inputs, `aria-label` nos controles, `role="status"`/`aria-live` no feedback do form, 1 h1/página
- Canonical, title e description únicos em todas as páginas
- Sitemap cobre 100% das rotas públicas; robots.txt correto e apontando para o sitemap
- Nenhum segredo, token ou URL local (`127.0.0.1`) vazou nos bundles compilados
- Formulário de lead: consentimento LGPD + link para a Política de Privacidade, fallback WhatsApp robusto
- CNPJ e razão social no rodapé
- git limpo, com pipeline de rebuild documentado em `docs/OPERATIONS.md`
