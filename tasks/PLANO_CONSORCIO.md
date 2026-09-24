# Plano de Implementação — Página Consórcio CASE (Primo Rossi)
> Data: 2026-06-11
> Estimativa: ~4h (1 bloco)
> Rota: `/consorcio/`

---

## 1. Pesquisa — o produto

### O que é
O **Consórcio Nacional CASE** é o consórcio oficial das máquinas CASE Construction, administrado desde 2017 pela **Primo Rossi Administradora de Consórcio Ltda** (CNPJ 51.597.300/0001-30) — a administradora de consórcios mais antiga do Brasil, fundada em 1964 (um ano após a criação do sistema de consórcios). As cotas são vendidas **na rede de concessionárias** — é aí que a IBL entra: o lead é local, o relacionamento e a entrega da máquina são da concessionária.

### Mecânica (confirmada nas fontes)
- Sem juros e sem entrada; paga-se taxa de administração (fonte terceirizada cita ~1,68% a.a. — **CONFIRMAR** com material oficial)
- Grupos com **assembleias mensais**; contemplação por **sorteio ou lance**; sem obrigação de lance
- Crédito **corrigido junto com o valor do bem de referência** (mantém poder de compra)
- Cartas de crédito de referência: **~R$ 293 mil a R$ 1,3 mi**; parcelas ~R$ 3,1 mil a R$ 19,9 mil (fonte GT Consórcio — **valores de referência, validar**)
- Sem prazo para retirar o bem após contemplação; crédito fica aplicado
- App do consorciado (assembleias, lances, extratos, boleto)
- Regulamento público no site da Primo Rossi

### Números de prova social
- Primo Rossi: desde 1964, +200 contemplações/mês, +R$ 13 bilhões em créditos pagos
- Consórcio CASE: +328% em vendas de cotas (1º sem/2020), +73% (2021 vs 2020)

### Posicionamento vs financiamento
A CASE também oferece financiamento via **Banco CNH** (disponível na IBL). O consórcio NÃO substitui: é a opção de **compra planejada** (renovação de frota programada, expansão sem pressa, locadores) enquanto o financiamento atende urgência. A página deve apresentar os dois caminhos honestamente — isso aumenta a credibilidade e captura os dois perfis.

### Fontes
- primorossi.com.br/consorcio/maquinas-construcao-case-ce (página oficial do produto)
- primorossi.com.br (institucional, números, regulamento)
- casece.com — Serviços Financeiros / Banco CNH
- operaction.com.br — release crescimento 328% (2020)
- autoindustria.com.br — cotas +73% (2022)
- gtconsorcio.com — tabela de créditos/parcelas (referência de mercado, não oficial)

---

## 2. Estrutura da página `/consorcio/`

Gerada pelo `generate_pages.py` (shell compartilhado — mesmo padrão das institucionais), adicionada ao sitemap, nav e footers.

| # | Seção | Conteúdo |
|---|---|---|
| 1 | Hero | Eyebrow "/// Consórcio Nacional CASE". H1: "Sua próxima CASE sem juros e sem entrada". Sub: compra planejada com a administradora mais antiga do Brasil. CTA primário "Quero simular" (→ form da própria página) + CTA WhatsApp. Máquina recortada + selo Primo Rossi desde 1964 |
| 2 | Barra de prova | 3 stats: Desde 1964 · +200 contemplações/mês · +R$ 13 bi em créditos entregues |
| 3 | Como funciona | 4 passos numerados: ① Escolha o valor do crédito ② Parcelas que cabem no fluxo de caixa ③ Assembleias mensais — sorteio ou lance ④ Contemplado: retira sua CASE na IBL com pós-venda completo |
| 4 | Consórcio × Financiamento | Tabela honesta (juros, entrada, prazo de retirada, perfil ideal). Fecha com: "Pressa? A IBL também opera financiamento Banco CNH" — captura os dois perfis |
| 5 | Para quem é | 3 cards: Renovação programada de frota · Expansão planejada · Locadores e prestadores de serviço |
| 6 | Faixas de crédito | Range de referência (R$ 293 mil – R$ 1,3 mi) com disclaimer visível "valores de referência — consulte condições vigentes" |
| 7 | FAQ | 5-6 perguntas: o que é contemplação, como funciona lance, crédito corrige?, posso usar para qualquer modelo CASE?, quem administra?, onde vejo o regulamento |
| 8 | Form de lead | Mesmo motor do site (webhook + fallback WhatsApp + consentimento LGPD), com `lead_channel: "consorcio"` e campos: nome, WhatsApp, categoria de máquina de interesse, faixa de crédito desejada |
| 9 | Compliance | Administradora oficial: Primo Rossi (CNPJ), autorizada pelo Banco Central; link para o regulamento; disclaimers de valores |

### Integrações no site existente
- Item "Consórcio" no nav do header (desktop + mobile) e nos footers (coluna Empresa/Suporte)
- CTA "Compre via consórcio" nas páginas de produto (abaixo do form de lead)
- Opção "Consórcio CASE" no select "Linha de interesse" do form da home
- SEO: title "Consórcio CASE sem juros | IBL Máquinas e Primo Rossi", JSON-LD (Service + FAQPage), sitemap automático

### Tracking
- Eventos: `consorcio_view`, `consorcio_lead_submit`, `consorcio_whatsapp`, `consorcio_cta_produto`
- Lead ops: canal "consorcio" no monitor de SLA existente

---

## 3. O que NÃO fazer
- Não publicar taxa de administração, prazos ou tabelas como se fossem oficiais — tudo que não vier de material oficial da parceria entra como "referência"
- Não simular cálculo de parcela no site (responsabilidade da administradora; risco regulatório) — o "simular" do CTA = formulário de contato qualificado
- Não usar logo Primo Rossi sem confirmar permissão de uso na parceria

## 4. Pendências de negócio (antes ou logo após o go-live da página)
- [ ] Confirmar com a CASE/Primo Rossi o material oficial de condições vigentes (tabela de grupos, taxa adm, prazos)
- [ ] Confirmar uso da marca Primo Rossi na página
- [ ] Definir destino do lead de consórcio (mesmo funil do ibl-ai-os? vendedor especialista?)
- [ ] Validar se a IBL tem código/link de parceiro no simulador da Primo Rossi (se sim, CTA secundário pode apontar para lá com tracking)

## 5. Critérios de Done
- Página gerada, no sitemap, lighthouse ok, form de lead com consentimento funcionando (gate de lead passa), links no nav/footers, eventos GA4, disclaimers presentes
