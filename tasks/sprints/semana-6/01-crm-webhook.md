# Semana 6 — Integração CRM via webhook

## Implementado
- Função central de envio de lead via `POST` JSON para endpoint configurável.
- Variável de ambiente: `VITE_LEAD_WEBHOOK_URL`.
- Payload com contexto:
  - dados do lead
  - página de origem
  - timestamp
  - attribution/UTM

## Eventos instrumentados
- `lead_submit_attempt`
- `lead_submit_success`
- `lead_submit_error`

## Arquivos alterados
- `/Users/joseoliveira/CODING/VARIANT/main.js`
- `/Users/joseoliveira/CODING/VARIANT/.env.example`
