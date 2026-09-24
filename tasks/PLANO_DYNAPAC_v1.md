# Plano Dynapac + Home Multi-marca — IBL Máquinas (v1.0)

> Data: 2026-08-06 · Autor: Claude + xbr
> Pré-requisito: site CASE v1.3 aprovado em teste.iblmaquinas.com.br (feito)
> Objetivo: transformar o site em portal de concessionária **multi-marca** — CASE Construction (8 lojas, 6 estados) e Dynapac (**somente AC, AM, RO e RR**) — mantendo o estilo industrial dark aprovado.

## Decisões (2026-08-06)

| Tema | Decisão |
|---|---|
| Estrutura de URLs | **`/case/...` e `/dynapac/...`** — catálogo CASE migra de `/produtos/` para `/case/`; institucionais (sobre, filiais, contato, consórcio, privacidade) continuam compartilhadas na raiz. Migração é "grátis" agora: o domínio principal ainda não foi ao ar, nada indexado. |
| Home | **Seletor + conteúdo IBL**: hero dividido CASE \| Dynapac no topo, seguido de seções institucionais (quem somos, 8 lojas, pós-venda, formulário de contato). Raiz continua forte para SEO. |
| Linha Dynapac | **Catálogo BR completo** (compactação, pavimentação e equipamentos leves) — Claude levanta tudo do site oficial; IBL depois poda o que não vende na região. |
| Identidade Dynapac | Mesmo layout industrial; accent muda de amarelo CASE (#E58E1A) para **vermelho Dynapac** (≈#E2001A) via variável CSS por marca. Máquinas Dynapac são amarelas — contraste continua bom no fundo dark. |
| Cobertura Dynapac | Só 4 unidades exibidas nas páginas Dynapac: **Rio Branco/AC, Manaus/AM, Ariquemes/RO, Boa Vista/RR** — com aviso claro de cobertura regional. |

## Arquitetura alvo

```
/                       → Home IBL: seletor de marca + institucional
/case/                  → Home da marca CASE (atual home vira esta página)
/case/{categoria}/{modelo}/     → catálogo CASE (migrado de /produtos/...)
/dynapac/               → Home da marca Dynapac (cobertura AC/AM/RO/RR)
/dynapac/{categoria}/{modelo}/  → catálogo Dynapac
/sobre/ /filiais/ /contato/ /consorcio/ /privacidade/  → compartilhadas (2 marcas)
/api/lead.php           → mesmo endpoint; payload ganha campo "marca"
```

---

## Fase 0 — Coleta de dados Dynapac — [Claude]

- [ ] Levantar catálogo Dynapac Brasil no site oficial (dynapac.com/br-pt): categorias **Compactação** (rolos de solo CA, tandem CC, pneumáticos CP), **Pavimentação** (vibroacabadoras SD/F, fresadoras) e **Equipamentos Leves** (placas LG/LP, compactadores de percussão, cortadoras)
- [ ] Extrair por modelo: nome, specs técnicas principais (peso, largura de trabalho, motor, etc.), descrição, aplicações
- [ ] Baixar fotos oficiais de cada modelo (material OEM — concessionária autorizada pode usar); processar: recorte nobg via pipeline existente (`remove_bg`) + derivativos WebP
- [ ] Obter logo Dynapac oficial (SVG/PNG alta) e definir tokens de cor da marca
- [ ] Montar `data/dynapac-db.json` no mesmo padrão do codedb CASE (categorias → modelos → specs/assets)
- **Saída:** banco de dados Dynapac pronto para o gerador + assets processados

## Fase 1 — Arquitetura multi-marca — [Claude]

- [ ] Refatorar `generate_pages.py` para ser **brand-aware**: config por marca (slug de rota, nome, logo, cor accent, categorias, unidades atendidas, mensagem de WhatsApp, JSON-LD Brand)
- [ ] Tema CSS por marca: `body[data-brand]` + variável `--brand-accent` (CASE amarelo / Dynapac vermelho); componentes já usam a variável — mudança pontual
- [ ] Migrar catálogo CASE `/produtos/...` → `/case/...`: gerador, vite entries, links internos, breadcrumbs, sitemap, robots, launch gates, verify-dist
- [ ] Redirect 301 `/produtos/*` → `/case/*` no `.htaccess` (higiene para quem tiver salvo links do staging)
- [ ] `data/filiais.json`: adicionar campo `marcas` por filial (todas têm CASE; AC/AM/RO/RR têm Dynapac também)
- **Saída:** build atual (só CASE) funcionando 100% na nova estrutura, gates verdes

## Fase 2 — Home seletora + institucionais multi-marca — [Claude]

- [ ] Nova home `/`: hero seletor dividido (CASE amarelo \| Dynapac vermelho, foto de máquina de cada lado) + seções IBL: história/números, mapa das 8 lojas, pós-venda, formulário de lead geral
- [ ] `/case/` vira a home da marca (conteúdo da home atual, com breadcrumb para raiz)
- [ ] `/dynapac/` home da marca: hero Dynapac, destaque de cobertura **"Concessionária Dynapac no AC, AM, RO e RR"**, categorias, unidades da região, formulário
- [ ] Institucionais atualizadas: sobre (história das 2 marcas), filiais (badge CASE/Dynapac por unidade), contato
- [ ] JSON-LD: Organization com `brand: [CASE Construction, Dynapac]`; AutoDealer por unidade com marcas corretas
- **Saída:** navegação completa entre marcas, sem beco sem saída

## Fase 3 — Catálogo Dynapac — [Claude]

- [ ] Gerar `/dynapac/{categoria}/` e `/dynapac/{categoria}/{modelo}/` com os mesmos templates (ficha técnica, galeria, formulário de lead, FAQ, related)
- [ ] Formulário de lead: campo `marca` no payload → Bitrix recebe "Marca: Dynapac" nos comentários (facilita roteamento comercial)
- [ ] GA4: dimensão `brand` nos eventos de lead e navegação
- [ ] OG image específica Dynapac (1200×630, máquina + logo, barra vermelha)
- [ ] Sitemap unificado com as duas árvores
- **Saída:** catálogo Dynapac navegável de ponta a ponta

## Fase 4 — QA, build e staging — [Claude]

- [ ] Gates atualizados: smoke nas rotas das 2 marcas + home seletora; lead gate nos formulários das 2 marcas (success e failure)
- [ ] Verificação de referências de imagem (todas resolvem), zero dependências externas novas
- [ ] Screenshots desktop/mobile das páginas-chave das duas marcas
- [ ] Build + pacote + **deploy no teste.iblmaquinas.com.br via FTP** para sua aprovação
- **Saída:** staging atualizado com o portal multi-marca completo

## Fase 5 — Validação e poda — [VOCÊ]

- [ ] Navegar o staging e aprovar visual/estrutura
- [ ] **Podar o catálogo Dynapac**: me dizer quais modelos vocês NÃO vendem (eu removo em minutos)
- [ ] Validar o texto de cobertura regional (AC/AM/RO/RR) e telefones das 4 unidades Dynapac
- [ ] Confirmar com a Dynapac/gerente comercial se há material oficial de fotos preferido
- [ ] Aprovar → cutover produção (backup WordPress + pacote de produção + AutoSSL, plano já documentado)

---

## Riscos & pontos de atenção

1. **Fotos Dynapac**: qualidade/resolução do site oficial varia por modelo; alguns podem ficar sem foto de recorte — fallback: foto ambientada + placeholder padronizado.
2. **Lineup BR ≠ lineup regional**: o catálogo completo pode listar máquinas que a IBL não vende no Norte — mitigado pela Fase 5 (poda é remoção de entradas no JSON + rebuild, minutos).
3. **Especificações**: specs extraídas do site oficial — qualquer divergência com a tabela comercial da IBL deve ser apontada na Fase 5.
4. **SEO da migração /produtos/→/case/**: risco zero em produção (nada indexado); 301 cobre o staging.
5. **Marca registrada**: uso de logos CASE/Dynapac como concessionária autorizada — mesmo enquadramento já usado na parte CASE.

## Estimativas

| Fase | Dependência | Estimativa |
|---|---|---|
| 0 — Coleta Dynapac | — | ~1 dia |
| 1 — Arquitetura multi-marca | — (paralela à F0) | ~1 dia |
| 2 — Home + institucionais | F1 | ~meio dia |
| 3 — Catálogo Dynapac | F0 + F1 | ~1 dia |
| 4 — QA + staging | F2 + F3 | ~meio dia |
| 5 — Validação/poda | F4 | seu tempo |

## Critérios de aceite

1. Home `/` permite escolher marca e apresenta a IBL institucionalmente
2. `/case/` preserva 100% do conteúdo e funcionalidades aprovadas na v1.3
3. `/dynapac/` cobre o catálogo BR com fotos, specs e lead form funcionando (lead no Bitrix com marca identificada)
4. Páginas Dynapac exibem somente as 4 unidades AC/AM/RO/RR com aviso de cobertura
5. Gates (smoke + lead success/failure) verdes nas duas marcas; staging atualizado para aprovação
