<?php
// Copie para lead-config.php NO SERVIDOR (public_html/api/lead-config.php).
// NUNCA versionar lead-config.php no git — contém o token do Bitrix.

// Webhook de entrada do Bitrix24 com permissão CRM (Recursos p/ desenvolvedor → Webhook de entrada)
define('BITRIX_WEBHOOK_URL', 'https://iblmaquinas.bitrix24.com.br/rest/1/SEU_TOKEN_AQUI');

// Opcional: ID do responsável padrão pelos leads do site
define('BITRIX_ASSIGNED_BY_ID', 0);

// Opcional: e-mail que recebe alerta de novo lead (backup do push do Bitrix)
define('LEAD_ALERT_EMAIL', '');
