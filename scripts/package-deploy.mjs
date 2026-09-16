#!/usr/bin/env node

// Empacota o dist/ em um zip pronto para extrair no public_html do cPanel.
// - Injeta dist/api/lead-config.php a partir do .env (token Bitrix fora do git)
// - Remove originais .png/.jpg que possuem derivativo .webp (páginas usam o .webp)
// Uso: node scripts/package-deploy.mjs  (após npm run rebuild:site)

import { execSync } from 'node:child_process'
import { existsSync, readFileSync, statSync, writeFileSync, unlinkSync } from 'node:fs'
import { resolve } from 'node:path'

const root = process.cwd()
const dist = resolve(root, 'dist')

if (!existsSync(resolve(dist, 'index.html'))) {
  console.error('dist/index.html não encontrado — rode `npm run rebuild:site` antes.')
  process.exit(1)
}

if (!existsSync(resolve(dist, '.htaccess'))) {
  console.error('dist/.htaccess não encontrado — confirme que public/.htaccess existe e rebuilde.')
  process.exit(1)
}

// .env → config do endpoint de leads
function readEnvFile() {
  const envPath = resolve(root, '.env')
  const env = {}
  if (existsSync(envPath)) {
    for (const line of readFileSync(envPath, 'utf8').split('\n')) {
      const m = line.match(/^\s*([A-Z0-9_]+)\s*=\s*(.*)\s*$/)
      if (m) env[m[1]] = m[2]
    }
  }
  return { ...env, ...process.env }
}

const env = readEnvFile()
const bitrixUrl = env.BITRIX_WEBHOOK_URL || ''

if (bitrixUrl) {
  const config = `<?php
// Gerado por scripts/package-deploy.mjs a partir do .env — NÃO versionar.
define('BITRIX_WEBHOOK_URL', ${JSON.stringify(bitrixUrl)});
define('BITRIX_ASSIGNED_BY_ID', ${Number(env.BITRIX_ASSIGNED_BY_ID || 0)});
define('LEAD_ALERT_EMAIL', ${JSON.stringify(env.LEAD_ALERT_EMAIL || '')});
`
  writeFileSync(resolve(dist, 'api', 'lead-config.php'), config)
  console.log('✓ dist/api/lead-config.php injetado a partir do .env')
} else {
  console.warn('! BITRIX_WEBHOOK_URL ausente no .env — lead.php responderá 503 e o site degrada para WhatsApp')
}

// Higiene: nada de lixo nem originais superados no pacote
execSync(`find "${dist}" -name '.DS_Store' -delete`, { stdio: 'inherit' })

let pruned = 0
const listCmd = `find "${dist}/case-assets" -type f \\( -name '*.png' -o -name '*.jpg' -o -name '*.jpeg' \\)`
for (const file of execSync(listCmd, { encoding: 'utf8' }).split('\n').filter(Boolean)) {
  const webp = file.replace(/\.(png|jpe?g)$/i, '.webp')
  if (webp !== file && existsSync(webp)) {
    unlinkSync(file)
    pruned += 1
  }
}
console.log(`✓ ${pruned} originais removidos do pacote (substituídos por .webp)`)

const stamp = new Date().toISOString().slice(0, 10).replaceAll('-', '')
const zipName = `ibl-site-deploy-${stamp}.zip`
const zipPath = resolve(root, zipName)

execSync(`rm -f "${zipPath}"`)
// Conteúdo do dist na raiz do zip (extrair direto dentro de public_html)
execSync(`cd "${dist}" && zip -qr9 "${zipPath}" . -x '*.map'`, { stdio: 'inherit' })

const sizeMb = (statSync(zipPath).size / 1024 / 1024).toFixed(1)
console.log(`✓ ${zipName} (${sizeMb} MB) — extrair o CONTEÚDO dentro de public_html/`)
console.log('  Lembrete: dist/api/lead-config.php contém segredo — o zip não deve ser publicado fora do servidor.')
