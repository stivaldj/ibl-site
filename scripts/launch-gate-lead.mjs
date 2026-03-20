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

async function waitForSubmitState(page, feedbackSelector, expectedStatus) {
  for (let attempt = 0; attempt < 20; attempt += 1) {
    const currentStatus = await page.evaluate((selector) => {
      return document.querySelector(selector)?.dataset.submitState || null
    }, feedbackSelector)

    if (currentStatus === expectedStatus) {
      return
    }

    await page.waitForTimeout(500)
  }

  throw new Error(`Timed out waiting for ${feedbackSelector} to reach ${expectedStatus}`)
}

async function submitHomepageLead(page, baseUrl, expectedStatus) {
  await page.goto(`${baseUrl}/?ops=1&utm_source=phase5&utm_medium=launch-gate`, { waitUntil: 'networkidle' })
  await page.evaluate(() => {
    window.__iblOpenedUrls = []
  })
  await page.fill('#lead-nome', 'Phase Five Home')
  await page.fill('#lead-telefone', '(67) 99999-0001')
  await page.selectOption('#lead-interesse', { index: 1 })

  await page.click('#lead-form button[type="submit"]')

  await waitForSubmitState(page, '#lead-feedback', expectedStatus)

  return page.evaluate(() => {
    const feedback = document.querySelector('#lead-feedback')
    return {
      status: feedback?.dataset.submitState || null,
      message: feedback?.textContent?.trim() || '',
      opsCount: JSON.parse(window.localStorage.getItem('ibl_lead_ops_v1') || '[]').length,
      openedUrls: Array.isArray(window.__iblOpenedUrls) ? window.__iblOpenedUrls : [],
    }
  })
}

async function submitProductLead(page, baseUrl, expectedStatus) {
  await page.goto(`${baseUrl}/produtos/retroescavadeiras/580n/?ops=1&utm_source=phase5&utm_medium=launch-gate`, { waitUntil: 'networkidle' })
  await page.waitForSelector('#product-lead-form')
  await page.evaluate(() => {
    window.__iblOpenedUrls = []
  })
  await page.fill('#product-lead-nome', 'Phase Five Product')
  await page.fill('#product-lead-whatsapp', '(67) 99999-0002')
  await page.fill('#product-lead-uso', 'Obras urbanas e terraplenagem')

  await page.click('#product-lead-form button[type="submit"]')

  await waitForSubmitState(page, '#product-lead-feedback', expectedStatus)

  return page.evaluate(() => {
    const feedback = document.querySelector('#product-lead-feedback')
    return {
      status: feedback?.dataset.submitState || null,
      message: feedback?.textContent?.trim() || '',
      opsCount: JSON.parse(window.localStorage.getItem('ibl_lead_ops_v1') || '[]').length,
      openedUrls: Array.isArray(window.__iblOpenedUrls) ? window.__iblOpenedUrls : [],
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
  await context.addInitScript(() => {
    window.__iblOpenedUrls = []
    window.open = (...args) => {
      window.__iblOpenedUrls.push(String(args[0] ?? ''))
      return null
    }
  })
  const homepagePage = await context.newPage()
  const homepage = await submitHomepageLead(homepagePage, options.baseUrl, options.expectedStatus)
  await homepagePage.close()

  const productPage = await context.newPage()
  const product = await submitProductLead(productPage, options.baseUrl, options.expectedStatus)
  await productPage.close()

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
