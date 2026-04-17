# Semana 6 — Alertas operacionais de lead (SLA)

## Implementado
- Registro local de leads enviados para monitor operacional.
- Verificação recorrente de SLA (default 2h) para leads não marcados como contatados.
- Evento de risco operacional: `lead_sla_risk`.
- Painel operacional opcional para acompanhamento:
  - acessar com `?ops=1` na URL.
  - permite marcar lead como contatado.

## Configuração
- `VITE_LEAD_SLA_HOURS` (opcional)

## Arquivo alterado
- `/Users/joseoliveira/CODING/VARIANT/main.js`
