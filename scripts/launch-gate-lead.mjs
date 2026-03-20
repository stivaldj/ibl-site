#!/usr/bin/env node

import { mkdir, writeFile } from 'node:fs/promises'
import { dirname, resolve } from 'node:path'
import { createRequire } from 'node:module'

function parseArgs(argv) {
  const options = {
    baseUrl: 'http://127.0.0.1:4174',
    expectedStatus: 'success',
    evidenceFile: '.tmp/launch-gate/latest/lead.json',
  }

  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index]
    const value = argv[index + 1]

    if (arg === '--help') {
      console.log(`Usage: node scripts/launch-gate-lead.mjs [options]

Options:
  --base-url <url>          Base URL for the runtime under test
  --expected-status <name>  success or failure
  --evidence-file <path>    File where lead evidence JSON will be written
`)
      process.exit(0)
    }

    if (arg === '--base-url' && value) {
      options.baseUrl = value.replace(/\/$/, '')
      index += 1
      continue
    }

    if (arg === '--expected-status' && value) {
      options.expectedStatus = value
      index += 1
      continue
    }

    if (arg === '--evidence-file' && value) {
      options.evidenceFile = value
      index += 1
      continue
    }
  }

  if (!['success', 'failure'].includes(options.expectedStatus)) {
    throw new Error(`Unsupported expected status: ${options.expectedStatus}`)
  }

  return options
}

function loadPlaywright() {
  const fallbackRoot = '/Users/joseoliveira/CODING/trading-tool/node_modules'
  const require = createRequire(import.meta.url)

  try {
    return require('playwright')
  } catch {
    return require(resolve(fallbackRoot, 'playwright'))
  }
}

async function submitHomepageLead(page, baseUrl, expectedStatus) {
  await page.goto(`${baseUrl}/?ops=1&utm_source=phase5&utm_medium=launch-gate`, { waitUntil: 'networkidle' })
  await page.fill('#lead-nome', 'Phase Five Home')
  await page.fill('#lead-telefone', '(67) 99999-0001')
  await page.selectOption('#lead-interesse', { index: 1 })

  const popupPromise = page.waitForEvent('popup').catch(() => null)
  await page.click('#lead-form button[type="submit"]')
  const popup = await popupPromise
  if (popup) {
    await popup.close().catch(() => {})
  }

  await page.waitForFunction(
    (status) => document.querySelector('#lead-feedback')?.dataset.submitState === status,
    expectedStatus,
  )

  return page.evaluate(() => {
    const feedback = document.querySelector('#lead-feedback')
    return {
      status: feedback?.dataset.submitState || null,
      message: feedback?.textContent?.trim() || '',
      opsCount: JSON.parse(window.localStorage.getItem('ibl_lead_ops_v1') || '[]').length,
    }
  })
}

async function submitProductLead(page, baseUrl, expectedStatus) {
  await page.goto(`${baseUrl}/produtos/retroescavadeiras/580n/?ops=1&utm_source=phase5&utm_medium=launch-gate`, { waitUntil: 'networkidle' })
  await page.waitForSelector('#product-lead-form')
  await page.fill('#product-lead-nome', 'Phase Five Product')
  await page.fill('#product-lead-whatsapp', '(67) 99999-0002')
  await page.fill('#product-lead-uso', 'Obras urbanas e terraplenagem')

  const popupPromise = page.waitForEvent('popup').catch(() => null)
  await page.click('#product-lead-form button[type="submit"]')
  const popup = await popupPromise
  if (popup) {
    await popup.close().catch(() => {})
  }

  await page.waitForFunction(
    (status) => document.querySelector('#product-lead-feedback')?.dataset.submitState === status,
    expectedStatus,
  )

  return page.evaluate(() => {
    const feedback = document.querySelector('#product-lead-feedback')
    return {
      status: feedback?.dataset.submitState || null,
      message: feedback?.textContent?.trim() || '',
      opsCount: JSON.parse(window.localStorage.getItem('ibl_lead_ops_v1') || '[]').length,
    }
  })
}

async function main() {
  const options = parseArgs(process.argv.slice(2))
  const evidenceFile = resolve(options.evidenceFile)
  await mkdir(dirname(evidenceFile), { recursive: true })

  const { chromium } = loadPlaywright()
  const browser = await chromium.launch({ headless: true })
  const context = await browser.newContext()
  const page = await context.newPage()

  const homepage = await submitHomepageLead(page, options.baseUrl, options.expectedStatus)
  const product = await submitProductLead(page, options.baseUrl, options.expectedStatus)

  const evidence = {
    generatedAt: new Date().toISOString(),
    baseUrl: options.baseUrl,
    expectedStatus: options.expectedStatus,
    homepage,
    product,
    passed:
      homepage.status === options.expectedStatus &&
      product.status === options.expectedStatus,
  }

  await writeFile(evidenceFile, `${JSON.stringify(evidence, null, 2)}\n`, 'utf8')
  await browser.close()

  if (!evidence.passed) {
    console.error('launch-gate-lead: lead flow verification failed')
    process.exit(1)
  }

  console.log(`launch-gate-lead: homepage and product flows reached ${options.expectedStatus}`)
}

main().catch((error) => {
  console.error(`launch-gate-lead: ${error instanceof Error ? error.message : String(error)}`)
  process.exit(1)
})
