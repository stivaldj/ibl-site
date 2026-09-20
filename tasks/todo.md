# Plano de Transformação UX/UI — IBL Máquinas (Meta: padrão projeto US$20k)

## v1.2 — Production Go-Live (2026-06-10)
> Ref: tasks/AUDITORIA_PRODUCAO.md | Branch: feature/v1.2-production-golive
> Decisões: hosting Cloudflare Pages; webhook configurável (endpoint real pendente); dados reais extraídos de www.iblmaquinas.com.br

### Fase 1 — Dados reais e configs
- [x] Dados reais coletados (8 filiais, CNPJ 28.265.622/0001-60, razão social Racine Comércio de Máquinas Ltda, e-mail contato@iblmaquinas.com.br)
- [x] `data/filiais.json` como fonte única (endereços curados do repo + telefones do site WP)
- [x] WhatsApp centralizado (VITE_WHATSAPP_NUMBER; fallback matriz 556733584100 — CONFIRMAR número WhatsApp Business oficial)
- [x] Substituído wa.me/5567999999999 em main.js, mobile/main.js, index.html, mobile/index.html, webapp/main.js, generate_pages.py
- [x] Title/OG profissional (removido "Industrial Edition")

### Fase 2 — SEO técnico e deploy
- [x] sitemap.xml (46 rotas) + robots.txt gerados pelo generate_pages.py
- [x] 404.html com identidade visual
- [x] GitHub Actions → Cloudflare Pages (generate → build → verify → deploy)
- [x] docs/DEPLOY.md com passos de DNS/secrets/cutover

### Fase 3 — Institucional + LGPD
- [x] /sobre/, /filiais/, /contato/, /privacidade/ (geradas pelo generate_pages.py, shell compartilhado, JSON-LD)
- [x] Consentimento LGPD obrigatório nos 3 formulários de lead
- [x] Links institucionais nos footers (estático + gerado) + CNPJ no rodapé (home já tinha seção #unidades)

### Fase 4 — Performance
- [x] SVGs do hero: PNG embutido → WebP q82 @2400px (30MB → ~2MB); máscaras alinhadas e verificadas
- [x] JPGs >400KB recomprimidos (rolo 8,4MB → 165KB); dist total 63MB → 23MB
- [x] phosphor-icons pinado @2.1.1

### Verificação
- [x] rebuild:site + verify:dist passando (build Linux em cópia isolada); 9 rotas-chave HTTP 200; sem número fake no dist; consentimento presente
- [ ] Launch gates Playwright (smoke + lead) — rodar na máquina local antes do merge: `npm run launch:gate:smoke` / `launch:gate:lead`
- [ ] Validação visual do hero comprimido no browser (abrir homepage local)

### Pendências de ambiente (fora do repo)
- [ ] Confirmar WhatsApp Business oficial → atualizar VITE_WHATSAPP_NUMBER + regenerar
- [ ] Expor endpoint de leads do ibl-ai-os + secret VITE_LEAD_WEBHOOK_URL
- [ ] Criar GA4 + var VITE_GA4_ID
- [ ] Setup Cloudflare Pages + secrets GitHub + DNS (docs/DEPLOY.md)
- [ ] Push da branch + PR (gh indisponível na sandbox): `git push -u origin feature/v1.2-production-golive`

## Correções rápidas (2026-02-26)
- [x] Corrigir sobreposição do widget de chat no mobile sem quebrar UX do chat.
- [x] Eliminar erro de `favicon.ico` 404.
- [x] Melhorar acessibilidade do chat (rótulo explícito no campo de mensagem).
- [x] Remover placeholders `href="#"` do bloco social/empresa/suporte do footer.
- [x] Reduzir custo de carregamento inicial com `loading="lazy"`/`decoding="async"` em mídia fora da dobra.
- [x] Validar build + smoke test Playwright (home, catálogo, PDP desktop/mobile).

### Revisão das correções rápidas (2026-02-26)
- Chat mobile: botão de trigger permanece ativo e painel fechado não intercepta mais área de interação da hero.
- Favicon: erro de console `404 /favicon.ico` removido nas rotas auditadas (home, catálogo, PDP).
- Acessibilidade: `#chat-widget-input` agora possui `aria-label`, zerando controles sem rótulo.
- Footer: itens de empresa/suporte/social migrados de links fake para botões “em breve”, reduzindo fricção de navegação.
- Mídia: 17 imagens configuradas com `loading="lazy"` e `decoding="async"`, mantendo hero principal como `eager` com `fetchpriority="high"`.

## Objetivo
Elevar o frontend atual de landing visual para uma plataforma comercial premium, com foco em conversão, credibilidade de marca e escalabilidade operacional.

## Checklist de execução
- [x] Mapear stack e arquitetura frontend atual.
- [x] Revisar homepage, catálogo e estrutura de navegação.
- [x] Identificar gaps críticos de UX, UI, conversão e acessibilidade.
- [x] Validar build e footprint técnico inicial.
- [ ] Definir novo posicionamento e proposta de valor por audiência.
- [ ] Reestruturar arquitetura da informação e jornadas por intenção.
- [ ] Construir design system (tokens, componentes, states e padrões responsivos).
- [ ] Redesenhar homepage com narrativa comercial orientada a lead.
- [ ] Redesenhar páginas de categoria com filtros e comparativos.
- [ ] Redesenhar PDPs (produto) com prova técnica, mídia e CTA forte.
- [ ] Implementar captura de demanda (formulários, WhatsApp, CRM e eventos).
- [ ] Implementar SEO técnico, schema e landing pages por região/segmento.
- [ ] Implementar performance, acessibilidade (WCAG AA) e QA cross-device.
- [ ] Instrumentar analytics e funil de conversão com dashboard de negócio.
- [ ] Rodar experimento de otimização contínua (A/B e CRO).

## Fases e entregáveis

### Fase 0 — Diagnóstico técnico-comercial (1 semana)
- Entregáveis:
  - Auditoria heurística UX/UI.
  - Mapa de jornada (descoberta → consideração → contato).
  - Baseline de métricas (LCP, CTR CTA, taxa de lead, scroll depth).

### Fase 1 — Fundamentos de marca e sistema visual (1-2 semanas)
- Entregáveis:
  - Direção de arte premium industrial (tipografia, ritmo, contraste, motion).
  - Design tokens (cor, spacing, radius, sombra, animação).
  - Biblioteca de componentes reutilizáveis com estados e variantes.

### Fase 2 — Arquitetura de informação e navegação (1 semana)
- Entregáveis:
  - Nova IA com rotas por intenção: Comprar, Comparar, Pós-venda, Peças, Falar com especialista.
  - Header mobile-first com mega menu funcional.
  - Breadcrumbs e padrões de navegação contextual.

### Fase 3 — Core de conversão (2 semanas)
- Entregáveis:
  - Homepage orientada a resultado: valor, prova social, diferenciais e CTA duplo.
  - Páginas de categoria com filtros e “comparar modelos”.
  - Template de produto com dados técnicos escaneáveis, mídia real e formulário inteligente.

### Fase 4 — Performance, acessibilidade e SEO (1 semana)
- Entregáveis:
  - Core Web Vitals alvo: LCP < 2.5s, CLS < 0.1, INP < 200ms.
  - Acessibilidade WCAG 2.2 AA (foco, contraste, teclado, ARIA).
  - SEO técnico completo (metas, Open Graph, Schema.org Product/Organization/FAQ).

### Fase 5 — Dados, integração e otimização (1-2 semanas)
- Entregáveis:
  - Integração com CRM e WhatsApp com tracking de origem.
  - Plano de eventos (GA4/Meta/LinkedIn) e funil por etapa.
  - Ciclo de CRO com backlog priorizado por impacto.

## KPIs de sucesso
- +40% taxa de clique em CTAs principais.
- +25% taxa de geração de leads qualificados.
- +30% profundidade média de sessão em páginas de produto.
- -20% taxa de rejeição na homepage.
- 90+ em Performance e Acessibilidade (Lighthouse mobile).

## Revisão (estado atual do projeto)
- Pontos fortes:
  - Identidade visual com direção clara (industrial premium).
  - Catálogo amplo já estruturado em rotas estáticas.
  - Build simples e rápido com Vite + Tailwind.
- Gaps críticos:
  - Muitos links/CTAs sem destino real (`href="#"`) comprometem conversão.
  - Navegação desktop-first e com fricção em mobile para alto volume de conteúdo.
  - Sem trilha de conversão real (captura, qualificação e integração com CRM).
  - Acessibilidade incompleta (faltam labels/ARIA e sem sinal de testes AA).
  - Prova comercial fraca (cases, números auditáveis, depoimentos, garantias detalhadas).
- Risco principal:
  - Alto investimento visual sem mecanismo robusto de geração e qualificação de demanda.

## Backlog Semanal (Execução)

### Semana 1 — Estratégia, baseline e arquitetura (P0)
- [x] P0.1 Definir ICPs (Construtora, locadora, produtor rural) e jobs-to-be-done.
  - Aceite: documento com dores, gatilhos e objeções por perfil.
- [x] P0.2 Mapear jornada completa (Home → Categoria → Produto → Contato).
  - Aceite: fluxograma com pontos de abandono e hipóteses de melhoria.
- [x] P0.3 Definir arquitetura da informação final.
  - Aceite: sitemap aprovado com rotas principais e secundárias.
- [x] P0.4 Instrumentar baseline de métricas atuais (GA4/eventos mínimos).
  - Aceite: dashboard com CTR CTA, taxa de lead e scroll depth.
- [x] P1.1 Inventário de conteúdo e ativos visuais reaproveitáveis.
  - Aceite: planilha com status (usar/ajustar/substituir).

### Semana 2 — Fundamentos de design system (P0)
- [x] P0.1 Criar tokens (cor, tipografia, spacing, radius, sombra, motion).
  - Aceite: tokens versionados em CSS variables + documentação.
- [x] P0.2 Definir grid/layout responsivo mobile-first.
  - Aceite: breakpoints e regras de composição aplicadas.
- [x] P0.3 Criar biblioteca base de componentes críticos.
  - Aceite: Button, Input, Card, Header, Footer, CTA, Badge com estados.
- [x] P1.1 Definir padrões de microinteração com `prefers-reduced-motion`.
  - Aceite: guideline de animação aprovado.

### Semana 3 — Homepage orientada a conversão (P0)
- [x] P0.1 Reescrever hero com valor claro + CTA duplo funcional.
  - Aceite: hero com mensagem por benefício e ações rastreáveis.
- [x] P0.2 Inserir prova comercial real (números auditáveis, cases, depoimentos).
  - Aceite: seção de confiança com evidências verificáveis.
- [x] P0.3 Criar bloco de captação primária (form curto + WhatsApp).
  - Aceite: envio funcional com validação e tracking.
- [x] P1.1 Refino visual premium sem excesso de ruído (menos efeitos cosméticos).
  - Aceite: revisão UX de legibilidade e escaneabilidade.

### Semana 4 — Páginas de categoria (P0)
- [x] P0.1 Redesenhar categorias com filtro por aplicação/potência/peso.
  - Aceite: filtros funcionais e URL compartilhável (query params).
- [x] P0.2 Implementar comparação rápida de modelos.
  - Aceite: comparação lado a lado com 4-6 specs-chave.
- [x] P0.3 Inserir CTA contextual por categoria.
  - Aceite: CTA por intenção (comprar/alugar/consultar).
- [x] P1.1 Melhorar busca interna por linha/modelo.
  - Aceite: busca retorna resultados relevantes em <300ms local.

### Semana 5 — Página de produto (PDP) (P0)
- [x] P0.1 Criar template único de PDP escalável.
  - Aceite: galeria, specs, diferenciais, downloads e CTA.
- [x] P0.2 Bloco de “fit por uso” (para quem este modelo serve).
  - Aceite: seção com cenários e recomendação objetiva.
- [x] P0.3 Formulário qualificado com pré-preenchimento por modelo.
  - Aceite: lead enviado com contexto do produto.
- [x] P1.1 FAQ técnico e comercial por produto.
  - Aceite: seção FAQ indexável e útil para SEO.

### Semana 6 — Integrações de negócio (P0)
- [x] P0.1 Integrar CRM (HubSpot/RD/Salesforce ou webhook).
  - Aceite: lead cria registro com origem/campanha.
- [x] P0.2 Integrar WhatsApp click-to-chat com parâmetros UTM.
  - Aceite: mensagem inicial contextual + origem rastreada.
- [x] P0.3 Definir taxonomia de eventos (view_item, generate_lead etc.).
  - Aceite: eventos disparando corretamente no debug.
- [x] P1.1 Criar alertas operacionais (lead sem resposta > X horas).
  - Aceite: rotina de monitoramento ativa.

### Semana 7 — SEO técnico e conteúdo comercial (P0)
- [x] P0.1 Implementar metadados completos (title, description, OG, canonical).
  - Aceite: páginas críticas com metadata única e validada.
- [x] P0.2 Implementar Schema.org (Organization, Product, FAQ, Breadcrumb).
  - Aceite: rich results test sem erros críticos.
- [ ] P0.3 Criar landing pages por região/segmento de atuação.
  - Aceite: páginas indexáveis com conteúdo útil e CTA local.
- [ ] P1.1 Plano editorial de conteúdo BOFU/MOFU.
  - Aceite: calendário inicial com 8 pautas.

### Semana 8 — Performance, acessibilidade e QA (P0)
- P0.1 Otimizar imagens (WebP/AVIF, lazy loading, tamanhos responsivos).
  - Aceite: redução de peso total de mídia em pelo menos 35%.
- P0.2 Alcançar WCAG 2.2 AA nas páginas principais.
  - Aceite: teclado, foco, contraste e rótulos validados.
- P0.3 Hardening de frontend (erros, estados vazios, fallback).
  - Aceite: fluxo estável sem quebras em devices principais.
- P1.1 Teste cross-browser/cross-device estruturado.
  - Aceite: matriz de QA com evidência de aprovação.

### Semana 9 — CRO e experimentação (P1)
- P1.1 Rodar 2 testes A/B (hero e formulário).
  - Aceite: teste com hipótese, público e métrica definida.
- P1.2 Refinar CTAs por etapa de funil.
  - Aceite: aumento estatístico de CTR.
- P2.1 Personalização leve por origem de tráfego.
  - Aceite: variação de copy por campanha.

### Semana 10 — Fechamento executivo e escala (P1)
- P1.1 Consolidar dashboard executivo de performance comercial.
  - Aceite: visão semanal de aquisição, conversão e qualidade.
- P1.2 Criar playbook de evolução contínua.
  - Aceite: backlog priorizado para próximo ciclo trimestral.
- P2.1 Treinamento do time interno (marketing/comercial).
  - Aceite: handoff com checklist operacional.

## Sequência de implementação recomendada (ordem crítica)
1. Semana 1 a 3 (fundação + home de conversão) — obrigatório.
2. Semana 4 a 6 (categoria + PDP + integrações) — obrigatório.
3. Semana 7 a 8 (SEO + performance + a11y) — obrigatório.
4. Semana 9 a 10 (CRO + escala) — otimização contínua.

## Ajuste Visual Rápido (Carrossel)
- [x] Aplicar efeito de holofote por card (facho cônico do topo até a base).
- [x] Reforçar iluminação na máquina sem distorcer as imagens.
- [x] Validar compilação do ajuste no build.

### Revisão do ajuste
- Implementado em `style.css` com pseudo-elementos em `.catalog-card-shell`:
  - Cone de luz (`::before`) com abertura progressiva até a base.
  - Fonte de luz superior (`::after`) para simular refletor.
- Imagem da máquina com ganho sutil de brilho/contraste para “receber” a luz.
- Mantido padrão anterior de borda/sombra para preservar consistência do carrossel.
- Iteração 2: cone ampliado com base quase total do card e tonalidade laranja translúcida para cobrir melhor toda a máquina.

## Correção de usabilidade do editor de layout (webapp)
- [x] Remover reposicionamento automático na seleção de elemento.
- [x] Materializar elemento apenas ao iniciar arraste/redimensionamento.
- [x] Garantir redimensionamento proporcional por handle de canto com toggle.
- [x] Impedir edição de texto em nós complexos (evitar perda de estilo em ficha/GIF).
- [x] Adicionar undo/redo por teclado e toolbar.
- [x] Priorizar seleção de alvo menor para evitar bloqueio por containers gigantes.
- [x] Criar barra de camadas lateral com seleção por lista.
- [x] Implementar lock/unlock por camada e modo foco em um único elemento.
- [x] Implementar grupo com lock e resize/move proporcional conjunto.
- [x] Permitir minimizar/expandir toolbar, painel de edição e painel de camadas.
- [x] Adicionar ajuste fino por teclado (setas para mover, Alt+setas para redimensionar).
- [x] Adicionar reset do tamanho padrão do elemento selecionado.
- [x] Remover limite de resize preso à viewport (permitir expansão além de `window.innerWidth/innerHeight`).
- [x] Adicionar threshold de arraste para clique simples não materializar/persistir alterações.
- [x] Estabilizar persistência de overlays do hero (`580N` e metadados) para evitar salto ao redimensionar.
- [ ] Validar manualmente no navegador (arraste, resize, persistência e animação do círculo).

### Revisão da correção (2026-02-26)
- Editor atualizado para persistir em coordenadas `fixed` e evitar “saltos” ao clicar.
- Handle de redimensionamento continua visível no canto e ganhou opção de proporção.
- Salvamento anterior migrou para chave nova (`ibl_layout_webapp_v2`) para evitar herança de estado ruim.

### Revisão incremental (2026-02-27)
- Resize do editor não usa mais teto da viewport, removendo travamento de crescimento da máquina.
- Clique simples em elementos editáveis não dispara mais persistência/materialização (evita crescimento indevido no GIF).
- Blocos de título/modelo do hero foram fixados em modo de persistência estável no editor para impedir fuga de posição.

## v1.3 — Production Go-Live (2026-07-29)
> Plano ativo: tasks/PLANO_GOLIVE_v1.3.md | Auditoria: tasks/AUDITORIA_PRE_DEPLOY_2026-07-29.md
> Decisões: cPanel; webhook ibl-ai-os antes do go-live; GA4 conta 334862278 (falta Measurement ID); remover /mobile/; escopo completo

### Execução v1.3 (2026-07-29) — Fases 1–3 + 5 concluídas por Claude
- [x] /mobile/ removido do build (vite, verify-dist, gates, robots)
- [x] Favicon real (.ico multi-size + apple-touch-icon) e OG image 1200×630
- [x] Unsplash → foto local WebP; TELEMETRIA/status "Aberto"/chat com copy honesto (telefones reais por unidade)
- [x] sameAs Instagram; nota Dynapac na página Sobre
- [x] 28 imagens pesadas → WebP (−85%); phosphor + leaflet self-host (zero unpkg/unsplash no dist)
- [x] public/.htaccess (HTTPS, 404, cache, gzip); CI verify-only; package:deploy (injeta lead-config, poda originais)
- [x] WhatsApp Business confirmado: 5565999808288 (env + fallbacks + filiais.json)
- [x] Leads → Bitrix24 via /api/lead.php no cPanel (token via .env, fora do git) + fallback WhatsApp
- [x] GA4 reutilizado: G-P3EYZ24YQZ (fluxo IBL MAQUINAS, histórico preservado) — baked no bundle
- [x] Gates: verify-dist ✓, smoke 4 rotas ✓, lead success E failure ✓ (E2E com PHP + mock Bitrix)
- [x] Pacote: ibl-site-deploy-20260729.zip (8,2 MB, 224 arquivos, .htaccess + api/lead-config.php)
- [ ] VOCÊ: backup do WordPress → extrair zip no public_html → AutoSSL → testes (docs/DEPLOY-CPANEL.md)
- [ ] VOCÊ: automação Bitrix "novo lead → notificação/WhatsApp" + Search Console pós-go-live

## Revisão geral pré-go-live + espelhamento Dynapac nacional (2026-09-16)
> Fonte nacional Dynapac = dynapac.com/br-pt (a aba "Produtos" esconde o que está "Interrompido").
> Fluxo: `npm run dynapac:sync` (documentado em docs/OPERATIONS.md §4).

### Correções gerais — CONCLUÍDO (commit fe53002)
- [x] Remover árvore morta `produtos/` e corrigir `404.html` para `/case/`
- [x] Remover páginas órfãs dos 4 modelos CASE excluídos (CX370C-ME, CX490C, CX500C, CX800B)
- [x] 7 imagens quebradas resolvidas ao regerar as páginas
- [x] Meta description Dynapac: fim da truncagem dupla (`build_meta_description`)
- [x] Títulos por marca: páginas Dynapac não terminam mais em "CASE Construction"
- [x] Copy CASE nas páginas Dynapac corrigida na regeração
- [x] Total do catálogo CASE passa a aplicar a exclusão (32 → 28, bate com a home)
- [x] WhatsApp: fallbacks sincronizados com o número confirmado do `.env`
- [x] `tailwind.config.js` apontando para `case/` e `dynapac/`
- [x] 404 com meta description; "Official Dealer" → "Concessionária Autorizada"; breadcrumb "Home" → "Início"
- [x] SEGURANÇA: `.env` (BITRIX_WEBHOOK_URL) não estava no `.gitignore` — corrigido + `.env.example`

### Dynapac — CONCLUÍDO (commit 9ddd70f)
- [x] Scraper do catálogo nacional (`scripts/dynapac-scrape-nacional.py`)
- [x] 36 → 108 modelos; saem CA250D, CP274, F1200CS e CM2500 (descontinuados no Brasil)
- [x] Mesas/screeds (18) fora do espelho, conforme escopo aprovado
- [x] 108/108 fotos oficiais baixadas (2 CDNs + fallback de URL)
- [x] Specs normalizadas para o padrão brasileiro e rótulos traduzidos
- [x] `prune_dynapac_orfaos`: modelo que sai do catálogo some do build

### Verificação
- [x] `npm run rebuild:site` ✓ · `launch-gate-smoke` ✓ (7 rotas)
- [x] `dist/`: 0 links quebrados, 0 imagens quebradas, sitemap 156/156
- [x] Revisão visual no navegador (home, categoria, ficha de modelo)

### Pendente com a IBL (não dá para resolver no código)
- [x] Telefone de Sinop/MT → (65) 99980-8288, atendimento nacional da rede (IBL, 2026-09-18).
      Todo lead de WhatsApp do site cai neste número; verificado com a variável de CI vazia.
- [x] `fotos-dynapac/` fora do git (decisão do José, 2026-09-18). Originais re-baixáveis;
      o gerador reusa o WebP versionado quando o original falta (CI/clone limpo).

## Fotos oficiais CASE — rodada 1 (2026-09-20)
Fonte: CASE Brand (casebrand.com), acervo oficial CNH. Mapeados 839 arquivos nas
11 linhas; 24 dos 28 modelos têm foto de estúdio disponível.

Aplicado nesta rodada (as 5 máquinas de baixa resolução do site):
| Modelo | Antes | Depois | Origem |
|---|---|---|---|
| 1150L | 460 px | 7360 px (reduzida a 2400) | CCE-IMG-11491 |
| 2050M | 460 px | 7360 px (reduzida a 2400) | CCE-IMG-11499 |
| 845B  | 1114 px | 8697 px (reduzida a 2400) | CCE-IMG-26411 |
| 885B  | 1114 px | 9009 px (reduzida a 2400) | CCE-IMG-26501 |
| SR175B | 1024 px | mantida a atual (ver nota) | — |

- [x] SR175B: NÃO trocada de propósito. A foto de estúdio do portal (CCE-IMG-13186,
      5895 px) é da geração anterior, a SR175 sem "B". A foto atual do site, embora
      de obra e com 1024 px, mostra a SR175B correta. Trocar seria anunciar outro
      modelo. Se a IBL quiser estúdio nessa máquina, é preciso foto da série B.
- [x] 885B: versão em alta (9009 px) aplicada.
- [x] 845B: ângulo de três quartos em alta (8697 px) aplicado.
- [ ] Próximas rodadas: 2ª e 3ª foto por modelo (galeria) e folhetos técnicos em PDF.
