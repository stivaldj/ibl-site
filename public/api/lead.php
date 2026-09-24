<?php
/**
 * IBL Máquinas — endpoint de leads do site (cPanel/PHP).
 * Recebe POST JSON do formulário e cria um Lead no Bitrix24 via webhook REST.
 * Config: api/lead-config.php (NÃO versionado — ver lead-config.sample.php).
 */

header('Content-Type: application/json; charset=utf-8');
header('X-Content-Type-Options: nosniff');

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['ok' => false, 'error' => 'method_not_allowed']);
    exit;
}

$configPath = __DIR__ . '/lead-config.php';
if (!file_exists($configPath)) {
    http_response_code(503);
    echo json_encode(['ok' => false, 'error' => 'config_missing']);
    exit;
}
require $configPath; // define BITRIX_WEBHOOK_URL e opcionais

$raw = file_get_contents('php://input');
$data = json_decode($raw, true);
if (!is_array($data)) {
    http_response_code(400);
    echo json_encode(['ok' => false, 'error' => 'invalid_json']);
    exit;
}

// ─── Anti-spam ────────────────────────────────────────────────────────────
// Robô recebe um "ok" falso: assim não descobre qual filtro o barrou.
function ibl_resposta_falsa(string $motivo): void {
    error_log('[ibl-lead] descartado: ' . $motivo);
    echo json_encode(['ok' => true, 'lead_id' => null]);
    exit;
}

// 1. Só aceita envio vindo de uma página do próprio site
// HTTP_HOST pode trazer a porta (":443"); a origem é comparada só pelo domínio
$hostSite = strtolower(preg_replace('/^www\./', '', (string)parse_url('http://' . ($_SERVER['HTTP_HOST'] ?? ''), PHP_URL_HOST)));
$origem   = (string)($_SERVER['HTTP_ORIGIN'] ?? ($_SERVER['HTTP_REFERER'] ?? ''));
$hostOrig = strtolower(preg_replace('/^www\./', '', (string)parse_url($origem, PHP_URL_HOST)));
if ($hostSite === '' || $hostOrig !== $hostSite) {
    http_response_code(403);
    echo json_encode(['ok' => false, 'error' => 'forbidden_origin']);
    exit;
}

// 2. Campo-isca: invisível para pessoas, robôs de formulário preenchem
if (trim((string)($data['website'] ?? '')) !== '') {
    ibl_resposta_falsa('campo-isca preenchido');
}

// 3. Ninguém preenche nome, WhatsApp e interesse em menos de 2 segundos
if ((int)($data['form_elapsed_ms'] ?? 0) < 2000) {
    ibl_resposta_falsa('envio rápido demais');
}

// 4. No máximo 5 envios por IP a cada 10 minutos
$dirLimite = sys_get_temp_dir() . '/ibl-lead-limite';
if (!is_dir($dirLimite)) @mkdir($dirLimite, 0700, true);
$arqLimite = $dirLimite . '/' . sha1((string)($_SERVER['REMOTE_ADDR'] ?? '')) . '.json';
$agora = time();
$envios = array_values(array_filter(
    (array)json_decode((string)@file_get_contents($arqLimite), true),
    fn($t) => is_int($t) && $t > $agora - 600
));
if (count($envios) >= 5) {
    http_response_code(429);
    echo json_encode(['ok' => false, 'error' => 'rate_limited']);
    exit;
}
$envios[] = $agora;
@file_put_contents($arqLimite, json_encode($envios), LOCK_EX);

$nome      = trim((string)($data['nome'] ?? ''));
$telefone  = trim((string)($data['telefone'] ?? ($data['whatsapp'] ?? '')));
$interesse = trim((string)($data['interesse'] ?? ($data['uso'] ?? '')));
$canal     = trim((string)($data['lead_channel'] ?? 'site'));
$pagina    = trim((string)($data['page_path'] ?? ''));
$modelo    = trim((string)($data['modelo'] ?? ''));
$marca     = trim((string)($data['marca'] ?? ''));
$attr      = is_array($data['attribution'] ?? null) ? $data['attribution'] : [];

$digitos = preg_replace('/\D/', '', $telefone);
if ($nome === '' || mb_strlen($nome) > 120 || strlen($digitos) < 10 || strlen($digitos) > 13) {
    http_response_code(422);
    echo json_encode(['ok' => false, 'error' => 'invalid_fields']);
    exit;
}

$comments = [];
if ($marca !== '')     $comments[] = "Marca: {$marca}";
if ($interesse !== '') $comments[] = "Interesse: {$interesse}";
if ($modelo !== '')    $comments[] = "Modelo: {$modelo}";
if ($pagina !== '')    $comments[] = "Página: {$pagina}";
if ($canal !== '')     $comments[] = "Canal: {$canal}";
foreach (['utm_source','utm_medium','utm_campaign','utm_term','utm_content'] as $k) {
    if (!empty($attr[$k])) $comments[] = "{$k}: {$attr[$k]}";
}
$comments[] = 'Origem: formulário do site iblmaquinas.com.br';

$fields = [
    'TITLE'     => 'Lead Site — ' . $nome . ($interesse !== '' ? " ({$interesse})" : ''),
    'NAME'      => $nome,
    'SOURCE_ID' => 'WEB',
    'SOURCE_DESCRIPTION' => 'Site iblmaquinas.com.br',
    'COMMENTS'  => implode("\n", $comments),
    'PHONE'     => [['VALUE' => $telefone, 'VALUE_TYPE' => 'MOBILE']],
];
if (defined('BITRIX_ASSIGNED_BY_ID') && BITRIX_ASSIGNED_BY_ID) {
    $fields['ASSIGNED_BY_ID'] = BITRIX_ASSIGNED_BY_ID;
}

$payload = json_encode(['fields' => $fields, 'params' => ['REGISTER_SONET_EVENT' => 'Y']]);

$ch = curl_init(rtrim(BITRIX_WEBHOOK_URL, '/') . '/crm.lead.add.json');
curl_setopt_array($ch, [
    CURLOPT_POST => true,
    CURLOPT_POSTFIELDS => $payload,
    CURLOPT_HTTPHEADER => ['Content-Type: application/json'],
    CURLOPT_RETURNTRANSFER => true,
    CURLOPT_TIMEOUT => 12,
]);
$response = curl_exec($ch);
$httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
curl_close($ch);

$decoded = json_decode((string)$response, true);
$leadId = $decoded['result'] ?? null;

if ($httpCode < 200 || $httpCode >= 300 || !$leadId) {
    error_log('[ibl-lead] Falha Bitrix HTTP ' . $httpCode . ' resp=' . substr((string)$response, 0, 300));
    http_response_code(502);
    echo json_encode(['ok' => false, 'error' => 'bitrix_failed']);
    exit;
}

// Alerta opcional por e-mail (backup do alerta nativo do Bitrix)
if (defined('LEAD_ALERT_EMAIL') && LEAD_ALERT_EMAIL) {
    $subject = 'Novo lead do site: ' . $nome;
    $body = "Novo lead recebido pelo site.\n\nNome: {$nome}\nTelefone: {$telefone}\nInteresse: {$interesse}\nPágina: {$pagina}\nLead Bitrix: #{$leadId}";
    @mail(LEAD_ALERT_EMAIL, $subject, $body, 'From: site@iblmaquinas.com.br');
}

echo json_encode(['ok' => true, 'lead_id' => $leadId]);
