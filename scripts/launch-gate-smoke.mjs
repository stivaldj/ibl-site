#!/usr/bin/env node

import { mkdir, writeFile } from 'node:fs/promises'
import { resolve } from 'node:path'

function parseArgs(argv) {
  const options = {
    baseUrl: 'http://127.0.0.1:4173',
    evidenceDir: '.tmp/launch-gate/latest',
  }

  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index]
    const value = argv[index + 1]

    if (arg === '--help') {
      console.log(`Usage: node scripts/launch-gate-smoke.mjs [options]

Options:
  --base-url <url>         Base URL for the served packaged artifact
  --evidence-dir <path>    Directory where smoke evidence JSON will be written
`)
      process.exit(0)
    }

    if (arg === '--base-url' && value) {
      options.baseUrl = value.replace(/\/$/, '')
      index += 1
      continue
    }

    if (arg === '--evidence-dir' && value) {
      options.evidenceDir = value
      index += 1
      continue
    }
  }

  return options
}

const ROUTES = [
  { path: '/', label: 'home', required: ['captacao-lead', '/assets/', 'DYNAPAC'] },
  { path: '/case/', label: 'case-home', required: ['captacao-lead', '/assets/'] },
  { path: '/case/catalogo/', label: 'case-catalog', required: ['/assets/', 'CASE'] },
  { path: '/case/retroescavadeiras/580n/', label: 'case-product', required: ['/assets/', 'Retroescavadeira 580N S2'] },
  { path: '/dynapac/', label: 'dynapac-home', required: ['/assets/', 'DYNAPAC'] },
  { path: '/dynapac/compactacao/', label: 'dynapac-category', required: ['/assets/', 'Compactação'] },
  { path: '/dynapac/compactacao/ca250d/', label: 'dynapac-product', required: ['/assets/', 'CA250D'] },
]

async function main() {
  const options = parseArgs(process.argv.slice(2))
  const evidenceDir = resolve(options.evidenceDir)
  await mkdir(evidenceDir, { recursive: true })

  const results = []

  for (const route of ROUTES) {
    const response = await fetch(`${options.baseUrl}${route.path}`)
    const html = await response.text()
    const hasRawSourceRefs =
      html.includes('/main.js') ||
      html.includes('/mobile/main.js') ||
      html.includes('/style.css') ||
      html.includes('/mobile/style.css')

    const missingRequired = route.required.filter((token) => !html.includes(token))

    const entry = {
      ...route,
      status: response.status,
      ok: response.ok && !hasRawSourceRefs && missingRequired.length === 0,
      hasRawSourceRefs,
      missingRequired,
    }

    results.push(entry)
  }

  const summary = {
    generatedAt: new Date().toISOString(),
    baseUrl: options.baseUrl,
    routes: results,
    passed: results.every((entry) => entry.ok),
  }

  await writeFile(
    resolve(evidenceDir, 'smoke.json'),
    `${JSON.stringify(summary, null, 2)}\n`,
    'utf8',
  )

  if (!summary.passed) {
    console.error('launch-gate-smoke: representative packaged route checks failed')
    process.exit(1)
  }

  console.log(`launch-gate-smoke: ${results.length} representative routes passed`)
}

main().catch((error) => {
  console.error(`launch-gate-smoke: ${error instanceof Error ? error.message : String(error)}`)
  process.exit(1)
})
