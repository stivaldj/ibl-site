#!/usr/bin/env node

import { mkdir, writeFile } from 'node:fs/promises'
import { dirname, resolve } from 'node:path'
import { chromium } from 'playwright'

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

function hasWhatsAppHandoff(openedUrls) {
  return Array.isArray(openedUrls) && openedUrls.some((url) => typeof url === 'string' && url.startsWith('https://wa.me/'))
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

async function submitLead(page, options) {
  const { baseUrl, route, expectedStatus, feedbackSelector, formLabel, viewport, fill } = options

  if (viewport) {
    await page.setViewportSize(viewport)
  }

  await page.goto(`${baseUrl}${route}`, { waitUntil: 'networkidle' })
  await page.evaluate(() => {
    window.__iblOpenedUrls = []
  })

  await fill(page)
  await waitForSubmitState(page, feedbackSelector, expectedStatus)

  const result = await page.evaluate((selector) => {
    const feedback = document.querySelector(selector)
    return {
      status: feedback?.dataset.submitState || null,
      message: feedback?.textContent?.trim() || '',
      opsCount: JSON.parse(window.localStorage.getItem('ibl_lead_ops_v1') || '[]').length,
      openedUrls: Array.isArray(window.__iblOpenedUrls) ? window.__iblOpenedUrls : [],
    }
  }, feedbackSelector)

  result.route = route
  result.formLabel = formLabel
  result.whatsappPassed = hasWhatsAppHandoff(result.openedUrls)

  if (!result.whatsappPassed) {
    throw new Error(`${formLabel} did not open a WhatsApp handoff URL`)
  }

  return result
}

async function main() {
  const options = parseArgs(process.argv.slice(2))
  const evidenceFile = resolve(options.evidenceFile)
  await mkdir(dirname(evidenceFile), { recursive: true })

  const launchOptions = { headless: true }
  if (process.env.PLAYWRIGHT_CHROMIUM_PATH) {
    launchOptions.executablePath = process.env.PLAYWRIGHT_CHROMIUM_PATH
  }
  const browser = await chromium.launch(launchOptions)
  const context = await browser.newContext()
  // Gate hermético: bloqueia requests externas (tiles de mapa, CDNs) para não
  // depender de rede de terceiros na verificação.
  const baseHost = new URL(options.baseUrl).host
  await context.route('**/*', (route) => {
    const host = new URL(route.request().url()).host
    if (host === baseHost) return route.continue()
    return route.abort()
  })
  await context.addInitScript(() => {
    window.__iblOpenedUrls = []
    window.open = (...args) => {
      window.__iblOpenedUrls.push(String(args[0] ?? ''))
      return null
    }
  })
  const homepagePage = await context.newPage()
  const homepage = await submitLead(homepagePage, {
    baseUrl: options.baseUrl,
    route: '/?ops=1&utm_source=phase6&utm_medium=launch-gate',
    expectedStatus: options.expectedStatus,
    feedbackSelector: '#lead-feedback',
    formLabel: 'homepage',
    viewport: { width: 1440, height: 900 },
    fill: async (page) => {
      await page.fill('#lead-nome', 'Phase Six Home')
      await page.fill('#lead-telefone', '(67) 99999-0001')
      await page.selectOption('#lead-interesse', { index: 1 })
      await page.check('#lead-form input[name="consentimento"]')
      await page.click('#lead-form button[type="submit"]')
    },
  })
  await homepagePage.close()

  const mobilePage = await context.newPage()
  const mobile = await submitLead(mobilePage, {
    baseUrl: options.baseUrl,
    route: '/?ops=1&utm_source=phase6&utm_medium=launch-gate',
    expectedStatus: options.expectedStatus,
    feedbackSelector: '#lead-feedback',
    formLabel: 'homepage-mobile-viewport',
    viewport: { width: 390, height: 844 },
    fill: async (page) => {
      await page.fill('#lead-nome', 'Phase Six Mobile')
      await page.fill('#lead-telefone', '(67) 99999-0003')
      await page.selectOption('#lead-interesse', { index: 1 })
      await page.check('#lead-form input[name="consentimento"]')
      await page.click('#lead-form button[type="submit"]')
    },
  })
  await mobilePage.close()

  const productPage = await context.newPage()
  const product = await submitLead(productPage, {
    baseUrl: options.baseUrl,
    route: '/case/retroescavadeiras/580n/?ops=1&utm_source=phase6&utm_medium=launch-gate',
    expectedStatus: options.expectedStatus,
    feedbackSelector: '#product-lead-feedback',
    formLabel: 'product',
    viewport: { width: 1280, height: 900 },
    fill: async (page) => {
      await page.waitForSelector('#product-lead-form')
      await page.fill('#product-lead-nome', 'Phase Six Product')
      await page.fill('#product-lead-whatsapp', '(67) 99999-0002')
      await page.fill('#product-lead-uso', 'Obras urbanas e terraplenagem')
      await page.check('#product-lead-form input[name="consentimento"]')
      await page.click('#product-lead-form button[type="submit"]')
    },
  })
  await productPage.close()

  const evidence = {
    generatedAt: new Date().toISOString(),
    baseUrl: options.baseUrl,
    expectedStatus: options.expectedStatus,
    homepage,
    mobile,
    product,
    passed:
      homepage.status === options.expectedStatus &&
      mobile.status === options.expectedStatus &&
      product.status === options.expectedStatus &&
      homepage.whatsappPassed &&
      mobile.whatsappPassed &&
      product.whatsappPassed,
  }

  await writeFile(evidenceFile, `${JSON.stringify(evidence, null, 2)}\n`, 'utf8')
  await browser.close()

  if (!evidence.passed) {
    console.error('launch-gate-lead: lead flow verification failed')
    process.exit(1)
  }

  console.log(`launch-gate-lead: homepage, mobile, and product flows reached ${options.expectedStatus} with WhatsApp handoff`)
}

main().catch((error) => {
  console.error(`launch-gate-lead: ${error instanceof Error ? error.message : String(error)}`)
  process.exit(1)
})
