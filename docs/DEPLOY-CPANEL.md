# Deploy — cPanel (servidor próprio)

> Decisão v1.3: hospedagem em servidor próprio via cPanel. O antigo pipeline
> Cloudflare Pages virou CI de verificação (`.github/workflows/deploy.yml`) —
> ele valida o build a cada push, mas o deploy é manual.

## Pré-requisitos

- `.env` de produção na raiz do repo com:
  - `VITE_GA4_ID=G-XXXXXXXXXX` (Measurement ID do fluxo de dados web — **não** é o ID da conta)
  - `VITE_WHATSAPP_NUMBER=5565999808288` (WhatsApp Business confirmado pela IBL)
  - `VITE_LEAD_WEBHOOK_URL=/api/lead.php` (endpoint PHP no próprio cPanel → Bitrix24)
  - `VITE_LEAD_SLA_HOURS=2`
  - `BITRIX_WEBHOOK_URL=https://iblmaquinas.bitrix24.com.br/rest/1/SEU_TOKEN` (webhook de entrada com permissão CRM; usado pelo `package:deploy` para gerar `dist/api/lead-config.php` — nunca vai para o git)
  - `LEAD_ALERT_EMAIL=` (opcional: e-mail que recebe aviso de novo lead)
- Python 3 com Pillow (`pip install pillow`) — usado para gerar derivativos `.webp`
- Node 20+ com dependências instaladas (`npm install`)

## Gerar o pacote

```bash
rm -rf dist
npm run rebuild:site       # generate:pages → vite build → verify:dist
npm run launch:gate:smoke  # com `vite preview` servindo o dist (ver docs/LAUNCH-GATE.md)
npm run package:deploy     # gera ibl-site-deploy-YYYYMMDD.zip
```

Checklist do artefato antes de subir:

- `dist/assets/` contém só os bundles do build atual (±5 arquivos)
- `dist/.htaccess` presente
- `grep -r "unpkg\|unsplash" dist --include='*.html'` → vazio
- Se GA4 configurado: `grep -rl googletagmanager dist/assets` → 1 bundle

## Subir no cPanel

1. **Backup primeiro:** se o WordPress antigo estiver neste mesmo cPanel, baixar
   backup completo (File Manager → compactar `public_html` + export do banco no
   phpMyAdmin) antes de qualquer alteração.
2. File Manager → `public_html` → Upload do zip → **Extract** (o conteúdo do zip
   já está na raiz — index.html deve ficar em `public_html/index.html`).
3. Remover os arquivos do site antigo que sobraram (wp-*, etc.), preservando o
   backup do passo 1.
4. **SSL:** cPanel → SSL/TLS Status → Run AutoSSL para `iblmaquinas.com.br` e
   `www.iblmaquinas.com.br`.
5. Se o domínio apontar para outro servidor hoje, ajustar o DNS (A record) para
   o IP deste cPanel — este é o momento do cutover.

## Leads → Bitrix24 (+ alerta de novo lead)

O formulário do site envia POST JSON para `/api/lead.php` (mesmo domínio, sem
CORS). O endpoint cria um Lead no Bitrix24 (`crm.lead.add`) com nome, telefone,
interesse, página de origem e UTMs nos comentários. Se o endpoint falhar ou a
config faltar, o site degrada com segurança para o fluxo WhatsApp.

Setup no servidor:

1. O `npm run package:deploy` já injeta `api/lead-config.php` no zip a partir do
   `.env`. Confirme após extrair que `public_html/api/lead-config.php` existe.
2. Teste: `curl -X POST https://iblmaquinas.com.br/api/lead.php -H 'Content-Type: application/json' -d '{"nome":"Teste Deploy","telefone":"(65) 99999-0000","interesse":"Retroescavadeiras"}'`
   → deve responder `{"ok":true,"lead_id":N}` e o lead aparecer no CRM.

Alerta de novo lead no WhatsApp (65 99980-8288):

- **Recomendado:** automação nativa do Bitrix24 — CRM → Leads → Regras de
  automação → em "Novo lead", adicionar notificação para o responsável (push do
  app Bitrix24) e/ou mensagem via canal WhatsApp conectado ao Bitrix.
  Isso evita colocar credenciais de API do WhatsApp no servidor.
- Backup opcional: definir `LEAD_ALERT_EMAIL` no `.env` — o `lead.php` envia um
  e-mail a cada lead criado.

## Testes pós-deploy

- `https://iblmaquinas.com.br/` carrega com cadeado (SSL)
- `http://` e `https://www.` redirecionam 301 para `https://` sem www
- `/case/retroescavadeiras/580n/` carrega com imagens
- Endereços do site antigo redirecionam: `/produtos/580n/` → `/case/retroescavadeiras/580n/`,
  `/sobre-nos/` → `/sobre/`, `/tipo/escavadeiras/` → `/case/escavadeiras-hidraulicas/`
  (mapa completo no `public/.htaccess`; os 43 endereços do sitemap antigo foram testados)
- Formulário de lead: enviar teste → abre WhatsApp com mensagem preenchida
- `/qualquer-coisa-inexistente` → página 404 customizada
- `/sitemap.xml` e `/robots.txt` acessíveis
- GA4 → Relatórios → Tempo real: registra a visita (se configurado)

## Rollback

Restaurar o backup do passo 1 (extrair o zip do site antigo de volta em
`public_html` e, se necessário, reimportar o banco). DNS só reverte se tiver
sido alterado.

## Pós-go-live (primeira semana)

1. Google Search Console: verificar propriedade + enviar `sitemap.xml`
2. Atualizar Política de Privacidade citando o GA4 (cookies/analytics)
3. Lighthouse (mobile) na home e em uma PDP — guardar baseline
4. Fase 4 do plano: expor endpoint de leads do ibl-ai-os e preencher
   `VITE_LEAD_WEBHOOK_URL` + rebuild + redeploy
