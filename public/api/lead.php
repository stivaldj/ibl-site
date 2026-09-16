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

$nome      = trim((string)($data['nome'] ?? ''));
$telefone  = trim((string)($data['telefone'] ?? ($data['whatsapp'] ?? '')));
$interesse = trim((string)($data['interesse'] ?? ($data['uso'] ?? '')));
$canal     = trim((string)($data['lead_channel'] ?? 'site'));
$pagina    = trim((string)($data['page_path'] ?? ''));
$modelo    = trim((string)($data['modelo'] ?? ''));
$marca     = trim((string)($data['marca'] ?? ''));
$attr      = is_array($data['attribution'] ?? null) ? $data['attribution'] : [];

if ($nome === '' || $telefone === '' || mb_strlen($nome) > 120 || mb_strlen($telefone) > 40) {
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
