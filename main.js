import './style.css'
import heroMachines from './data/hero-machines.json'

// Atendimento nacional da rede (E.164 sem "+"): todos os leads caem neste WhatsApp.
const WHATSAPP_NUMBER = import.meta.env.VITE_WHATSAPP_NUMBER || '5565999808288'
const WHATSAPP_BASE_URL = `https://wa.me/${WHATSAPP_NUMBER}`

const ANALYTICS_MILESTONES = [25, 50, 75, 90]
const ATTRIBUTION_STORAGE_KEY = 'ibl_attribution_v1'
const LEAD_OPS_STORAGE_KEY = 'ibl_lead_ops_v1'
const LEAD_OPS_UPDATED_EVENT = 'lead-ops-updated'
const LEAD_SUBMIT_STATUS = {
  success: 'success',
  skipped: 'skipped',
  failure: 'failure'
}
const LEAD_OPS_SUBMISSION_STATUS = {
  pending: 'pending',
  submitted: 'submitted',
  skipped: 'skipped',
  failed: 'failed'
}

function initAnalytics() {
  window.dataLayer = window.dataLayer || []

  const measurementId = import.meta.env.VITE_GA4_ID
  if (measurementId && !window.gtag) {
    const gaScript = document.createElement('script')
    gaScript.async = true
    gaScript.src = `https://www.googletagmanager.com/gtag/js?id=${measurementId}`
    document.head.appendChild(gaScript)

    window.gtag = function gtag() {
      window.dataLayer.push(arguments)
    }

    window.gtag('consent', 'default', {
      analytics_storage: 'granted',
      ad_storage: 'denied',
      ad_user_data: 'denied',
      ad_personalization: 'denied'
    })
    window.gtag('js', new Date())
    window.gtag('config', measurementId)
  }
}

// === Consentimento de cookies (LGPD) ===
// O Google Analytics só carrega depois de "Aceitar". A escolha fica no
// navegador; a política de privacidade tem o botão para rever.
const CONSENT_KEY = 'ibl-consent-analytics'

function readConsent() {
  try {
    return window.localStorage.getItem(CONSENT_KEY)
  } catch {
    return null
  }
}

function saveConsent(value) {
  try {
    window.localStorage.setItem(CONSENT_KEY, value)
  } catch {
    // navegação privada sem storage: vale só para esta página
  }
}

function clearAnalyticsCookies() {
  const domains = ['', `; domain=${window.location.hostname}`, `; domain=.${window.location.hostname.replace(/^www\./, '')}`]
  document.cookie.split(';').map((c) => c.split('=')[0].trim()).filter((name) => name.startsWith('_ga')).forEach((name) => {
    domains.forEach((domain) => {
      document.cookie = `${name}=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/${domain}`
    })
  })
}

function applyConsent(value) {
  if (value === 'granted') {
    initAnalytics()
    return
  }
  if (typeof window.gtag === 'function') {
    window.gtag('consent', 'update', { analytics_storage: 'denied' })
  }
  clearAnalyticsCookies()
}

function showConsentBanner() {
  if (document.getElementById('consent-banner')) return
  const banner = document.createElement('div')
  banner.id = 'consent-banner'
  banner.className = 'consent-banner'
  banner.setAttribute('role', 'dialog')
  banner.setAttribute('aria-live', 'polite')
  banner.setAttribute('aria-label', 'Aviso de cookies')
  banner.innerHTML = `
    <p class="consent-banner__text">
      Usamos cookies do Google Analytics para entender como o site é usado. Nada de publicidade.
      <a href="/privacidade/" class="consent-banner__link">Política de privacidade</a>
    </p>
    <div class="consent-banner__actions">
      <button type="button" class="consent-banner__btn" data-consent="denied">Recusar</button>
      <button type="button" class="consent-banner__btn consent-banner__btn--accept" data-consent="granted">Aceitar</button>
    </div>
  `
  banner.addEventListener('click', (event) => {
    const button = event.target instanceof Element ? event.target.closest('[data-consent]') : null
    if (!button) return
    const value = button.getAttribute('data-consent')
    saveConsent(value)
    applyConsent(value)
    banner.remove()
  })
  document.body.appendChild(banner)
}

function setupConsent() {
  const stored = readConsent()
  if (stored === 'granted' || stored === 'denied') {
    applyConsent(stored)
  } else {
    showConsentBanner()
  }
  document.querySelectorAll('[data-cookie-preferences]').forEach((button) => {
    button.addEventListener('click', () => showConsentBanner())
  })
}

function trackEvent(eventName, params = {}) {
  window.dataLayer = window.dataLayer || []
  window.dataLayer.push({ event: eventName, ...params })
  if (window.gtag) {
    window.gtag('event', eventName, params)
  }
}

function initAttribution() {
  const url = new URL(window.location.href)
  const incoming = {
    utm_source: url.searchParams.get('utm_source') || '',
    utm_medium: url.searchParams.get('utm_medium') || '',
    utm_campaign: url.searchParams.get('utm_campaign') || '',
    utm_content: url.searchParams.get('utm_content') || '',
    utm_term: url.searchParams.get('utm_term') || '',
    referrer: document.referrer || '',
    landing_page: window.location.pathname
  }

  const hasIncomingUtm = Object.entries(incoming).some(([key, value]) => key.startsWith('utm_') && value)
  const storedRaw = window.localStorage.getItem(ATTRIBUTION_STORAGE_KEY)
  if (hasIncomingUtm || !storedRaw) {
    window.localStorage.setItem(ATTRIBUTION_STORAGE_KEY, JSON.stringify(incoming))
  }
}

function getAttribution() {
  try {
    const raw = window.localStorage.getItem(ATTRIBUTION_STORAGE_KEY)
    return raw ? JSON.parse(raw) : {}
  } catch {
    return {}
  }
}

// Anti-spam (conferido em /api/lead.php): campo-isca invisível e o tempo
// desde que a página abriu — pessoa real não envia em menos de 2 s.
function ensureLeadHoneypot(form) {
  if (!(form instanceof HTMLFormElement) || form.querySelector('[name="website"]')) return
  const trap = document.createElement('div')
  trap.className = 'lead-hp'
  trap.setAttribute('aria-hidden', 'true')
  trap.innerHTML = '<label>Site <input type="text" name="website" tabindex="-1" autocomplete="off"></label>'
  form.appendChild(trap)
}

function readLeadHoneypot() {
  return [...document.querySelectorAll('input[name="website"]')].map((input) => input.value).join('').trim()
}

// WhatsApp com DDD: 10 ou 11 dígitos; com 55 na frente, 12 ou 13
function isValidLeadPhone(value) {
  const digits = String(value || '').replace(/\D/g, '')
  return digits.length >= 10 && digits.length <= 13
}

const LEAD_PHONE_MESSAGE = 'Informe um WhatsApp válido com DDD.'

function buildLeadWebhookPayload(leadPayload) {
  return {
    ...leadPayload,
    website: readLeadHoneypot(),
    form_elapsed_ms: Math.round(performance.now()),
    marca: document.body?.dataset?.brand === 'dynapac' ? 'Dynapac' : 'CASE Construction',
    page_path: window.location.pathname,
    captured_at: new Date().toISOString(),
    attribution: getAttribution()
  }
}

function getLeadSubmitTrackingContext(leadPayload) {
  return {
    page_path: window.location.pathname,
    lead_channel: leadPayload.lead_channel || 'unknown'
  }
}

function createLeadSubmitResult(status, extras = {}) {
  return {
    ok: status === LEAD_SUBMIT_STATUS.success,
    skipped: status === LEAD_SUBMIT_STATUS.skipped,
    status,
    ...extras
  }
}

function getLeadSubmitFeedbackMessage(submitResult) {
  if (submitResult.status === LEAD_SUBMIT_STATUS.skipped) {
    return 'Webhook indisponível. Abrindo o WhatsApp para registrar seu atendimento sem perder o contato...'
  }

  if (submitResult.status === LEAD_SUBMIT_STATUS.failure) {
    return 'Não conseguimos enviar ao sistema agora. Abrindo o WhatsApp para continuar o atendimento manualmente...'
  }

  return 'Solicitação enviada para a equipe IBL. Abrindo o WhatsApp para agilizar o atendimento...'
}

function clearLeadSubmitFeedback(target) {
  if (!(target instanceof HTMLElement)) return
  delete target.dataset.submitState
}

function applyLeadSubmitFeedback(target, submitResult) {
  if (!(target instanceof HTMLElement)) return
  target.dataset.submitState = submitResult.status
  target.textContent = getLeadSubmitFeedbackMessage(submitResult)
  playFeedbackPop(target)
}

/** Reinicia a animação de entrada do retorno do formulário.
 *  Sem o reflow, uma segunda mensagem seguida não reanima. */
function playFeedbackPop(target) {
  if (!(target instanceof HTMLElement)) return
  target.classList.remove('feedback-pop')
  void target.offsetWidth
  target.classList.add('feedback-pop')
}

function shouldResetLeadForm(submitResult) {
  return submitResult.status === LEAD_SUBMIT_STATUS.success
}

function getLeadOpsSubmissionStatus(submitResult) {
  if (submitResult.status === LEAD_SUBMIT_STATUS.success) {
    return LEAD_OPS_SUBMISSION_STATUS.submitted
  }

  if (submitResult.status === LEAD_SUBMIT_STATUS.skipped) {
    return LEAD_OPS_SUBMISSION_STATUS.skipped
  }

  return LEAD_OPS_SUBMISSION_STATUS.failed
}

function escapeHtml(value) {
  return String(value ?? '')
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#39;')
}

function getLeadOpsSubmissionMeta(status) {
  if (status === LEAD_OPS_SUBMISSION_STATUS.submitted) {
    return {
      label: 'enviado',
      className: 'border border-emerald-500/30 bg-emerald-500/10 text-emerald-300'
    }
  }

  if (status === LEAD_OPS_SUBMISSION_STATUS.skipped) {
    return {
      label: 'webhook ignorado',
      className: 'border border-amber-500/30 bg-amber-500/10 text-amber-200'
    }
  }

  if (status === LEAD_OPS_SUBMISSION_STATUS.failed) {
    return {
      label: 'falhou',
      className: 'border border-red-500/30 bg-red-500/10 text-red-300'
    }
  }

  return {
    label: 'pendente',
    className: 'border border-sky-500/30 bg-sky-500/10 text-sky-300'
  }
}

function getLeadOpsContextLabel(item) {
  if (item.lead_type === 'product') {
    const model = item.modelo || 'modelo não informado'
    const usage = item.uso || 'uso não informado'
    return `${model} · ${usage}`
  }

  return item.interesse || 'interesse não informado'
}

function getLeadOpsSlaState(item, slaMs, now = Date.now()) {
  if (item.contact_status === 'contacted') {
    return {
      label: 'contatado',
      className: 'text-emerald-300'
    }
  }

  const createdAt = new Date(item.created_at).getTime()
  if (Number.isFinite(createdAt) && (now - createdAt) > slaMs) {
    return {
      label: 'sla em risco',
      className: 'text-red-300'
    }
  }

  return {
    label: 'dentro do sla',
    className: 'text-gray-400'
  }
}

async function submitLeadToWebhook(leadPayload) {
  const webhookUrl = import.meta.env.VITE_LEAD_WEBHOOK_URL
  const payload = buildLeadWebhookPayload(leadPayload)
  const trackingContext = getLeadSubmitTrackingContext(leadPayload)

  trackEvent('lead_submit_attempt', trackingContext)

  if (!webhookUrl) {
    trackEvent('lead_submit_skipped', {
      ...trackingContext,
      skip_reason: 'missing_webhook_url'
    })
    return createLeadSubmitResult(LEAD_SUBMIT_STATUS.skipped, {
      payload,
      reason: 'missing_webhook_url'
    })
  }

  try {
    const response = await fetch(webhookUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(payload)
    })

    if (!response.ok) {
      const errorMessage = `Lead webhook falhou com status ${response.status}`
      trackEvent('lead_submit_error', {
        ...trackingContext,
        error_message: errorMessage,
        http_status: response.status
      })
      return createLeadSubmitResult(LEAD_SUBMIT_STATUS.failure, {
        payload,
        error_message: errorMessage,
        http_status: response.status
      })
    }

    trackEvent('lead_submit_success', trackingContext)
    return createLeadSubmitResult(LEAD_SUBMIT_STATUS.success, {
      payload
    })
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : 'unknown'
    trackEvent('lead_submit_error', {
      ...trackingContext,
      error_message: errorMessage
    })
    return createLeadSubmitResult(LEAD_SUBMIT_STATUS.failure, {
      payload,
      error_message: errorMessage
    })
  }
}

function getLeadOpsItems() {
  try {
    const raw = window.localStorage.getItem(LEAD_OPS_STORAGE_KEY)
    return raw ? JSON.parse(raw) : []
  } catch {
    return []
  }
}

function saveLeadOpsItems(items) {
  window.localStorage.setItem(LEAD_OPS_STORAGE_KEY, JSON.stringify(items))
  window.dispatchEvent(new CustomEvent(LEAD_OPS_UPDATED_EVENT))
}

function recordLeadOpsItem(lead) {
  const items = getLeadOpsItems()
  const entry = {
    id: `lead_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    contact_status: 'new',
    submission_status: LEAD_OPS_SUBMISSION_STATUS.pending,
    page_path: window.location.pathname,
    fallback_channel: 'whatsapp',
    ...lead
  }
  items.unshift(entry)
  saveLeadOpsItems(items.slice(0, 100))
  return entry
}

function updateLeadOpsItem(leadId, updates) {
  let nextEntry = null
  const items = getLeadOpsItems()
  const next = items.map((item) => {
    if (item.id !== leadId) return item
    nextEntry = {
      ...item,
      ...updates,
      updated_at: new Date().toISOString()
    }
    return nextEntry
  })
  saveLeadOpsItems(next)
  return nextEntry
}

function finalizeLeadOpsItem(leadId, submitResult) {
  const nextEntry = updateLeadOpsItem(leadId, {
    submission_status: getLeadOpsSubmissionStatus(submitResult),
    submit_result: submitResult.status,
    submit_ok: submitResult.ok,
    submit_skipped: submitResult.skipped,
    submit_reason: submitResult.reason || '',
    error_message: submitResult.error_message || '',
    http_status: submitResult.http_status || null
  })

  if (!nextEntry) return

  const leadLabel = nextEntry.nome || 'Lead sem nome'
  const routeLabel = nextEntry.page_path || window.location.pathname
  if (nextEntry.submission_status === LEAD_OPS_SUBMISSION_STATUS.submitted) {
    console.info(`[LEAD OPS] Lead enviado com sucesso: ${leadLabel} (${routeLabel})`)
    return
  }

  if (nextEntry.submission_status === LEAD_OPS_SUBMISSION_STATUS.skipped) {
    console.warn(`[LEAD OPS] Lead sem webhook: ${leadLabel} (${routeLabel})`)
    return
  }

  console.error(
    `[LEAD OPS] Lead com falha de envio: ${leadLabel} (${routeLabel})${nextEntry.http_status ? ` status ${nextEntry.http_status}` : ''}${nextEntry.error_message ? ` - ${nextEntry.error_message}` : ''}`
  )
}

function setupLeadOpsMonitor() {
  const url = new URL(window.location.href)
  const opsMode = url.searchParams.get('ops') === '1'
  const slaHours = Number(import.meta.env.VITE_LEAD_SLA_HOURS || '2')
  const slaMs = Math.max(1, slaHours) * 60 * 60 * 1000
  let lastAlertAt = 0

  const panel = document.createElement('aside')
  panel.id = 'lead-ops-panel'
  panel.className = 'card-surface fixed left-4 bottom-4 z-[80] w-[320px] hidden'
  panel.innerHTML = `
    <div class="p-4 border-b border-case-border">
      <h3 class="font-display font-black text-lg uppercase">Lead Ops Monitor</h3>
      <p class="text-[11px] font-mono uppercase tracking-widest text-gray-500">SLA ${slaHours}h</p>
      <div id="lead-ops-summary" class="grid grid-cols-2 gap-2 mt-3 text-[10px] font-mono uppercase tracking-widest text-gray-400"></div>
    </div>
    <div id="lead-ops-list" class="max-h-[280px] overflow-y-auto p-3 space-y-2"></div>
  `

  function renderPanel() {
    const list = panel.querySelector('#lead-ops-list')
    const summary = panel.querySelector('#lead-ops-summary')
    if (!(list instanceof HTMLElement) || !(summary instanceof HTMLElement)) return
    const items = getLeadOpsItems()
    const now = Date.now()
    const totals = items.reduce((acc, item) => {
      acc[item.submission_status] = (acc[item.submission_status] || 0) + 1
      const slaState = getLeadOpsSlaState(item, slaMs, now)
      if (slaState.label === 'sla em risco') {
        acc.risk += 1
      }
      return acc
    }, {
      [LEAD_OPS_SUBMISSION_STATUS.submitted]: 0,
      [LEAD_OPS_SUBMISSION_STATUS.skipped]: 0,
      [LEAD_OPS_SUBMISSION_STATUS.failed]: 0,
      [LEAD_OPS_SUBMISSION_STATUS.pending]: 0,
      risk: 0
    })

    summary.innerHTML = `
      <span>enviados <strong class="text-emerald-300">${totals.submitted}</strong></span>
      <span>pendentes <strong class="text-sky-300">${totals.pending}</strong></span>
      <span>ignorados <strong class="text-amber-200">${totals.skipped}</strong></span>
      <span>falhas <strong class="text-red-300">${totals.failed}</strong></span>
      <span class="col-span-2">sla em risco <strong class="text-red-300">${totals.risk}</strong></span>
    `

    if (items.length === 0) {
      list.innerHTML = '<p class="text-xs font-mono text-gray-500 uppercase tracking-widest">Sem leads registrados</p>'
      return
    }
    list.innerHTML = items.slice(0, 12).map((item) => `
      <article class="compare-item">
        <div class="flex items-center justify-between gap-2 mb-2">
          <p class="text-[11px] font-mono uppercase tracking-widest text-case-yellow">${item.lead_type || 'lead'}</p>
          <span class="rounded-full px-2 py-1 text-[10px] font-mono uppercase tracking-widest ${getLeadOpsSubmissionMeta(item.submission_status).className}">
            ${getLeadOpsSubmissionMeta(item.submission_status).label}
          </span>
        </div>
        <p class="text-xs text-white">${escapeHtml(item.nome || 'Lead sem nome')} · ${escapeHtml(item.telefone || '-')}</p>
        <p class="mt-1 text-[11px] text-gray-300">${escapeHtml(getLeadOpsContextLabel(item))}</p>
        <div class="mt-2 flex items-center justify-between gap-3 text-[10px] font-mono uppercase tracking-widest">
          <span class="text-gray-500">${escapeHtml(item.page_path || '-')}</span>
          <span class="${getLeadOpsSlaState(item, slaMs, now).className}">${getLeadOpsSlaState(item, slaMs, now).label}</span>
        </div>
        ${item.error_message ? `<p class="mt-2 text-[11px] text-red-300">${escapeHtml(item.error_message)}</p>` : ''}
        ${item.submit_reason ? `<p class="mt-2 text-[11px] text-amber-200">${escapeHtml(item.submit_reason)}</p>` : ''}
        <div class="mt-2 flex items-center justify-between gap-3">
          <p class="text-[10px] font-mono uppercase tracking-widest text-gray-500">${new Date(item.created_at).toLocaleString('pt-BR')}</p>
          <button data-lead-id="${item.id}" class="text-[10px] font-mono uppercase tracking-widest text-gray-400 hover:text-case-yellow">
            ${item.contact_status === 'contacted' ? 'contatado' : 'marcar contato'}
          </button>
        </div>
      </article>
    `).join('')
  }

  function runSlaCheck() {
    const now = Date.now()
    const items = getLeadOpsItems()
    const atRisk = items.filter(
      (item) => item.contact_status !== 'contacted' && (now - new Date(item.created_at).getTime()) > slaMs,
    )
    if (atRisk.length > 0 && (now - lastAlertAt) > 15 * 60 * 1000) {
      lastAlertAt = now
      trackEvent('lead_sla_risk', {
        page_path: window.location.pathname,
        pending_leads: atRisk.length,
        sla_hours: slaHours
      })
      console.warn(`[LEAD OPS] ${atRisk.length} lead(s) fora do SLA de ${slaHours}h.`)
    }
  }

  panel.addEventListener('click', (event) => {
    const target = event.target
    if (!(target instanceof HTMLElement)) return
    const leadId = target.getAttribute('data-lead-id')
    if (!leadId) return
    updateLeadOpsItem(leadId, { contact_status: 'contacted' })
    renderPanel()
  })

  window.addEventListener(LEAD_OPS_UPDATED_EVENT, () => {
    if (opsMode) renderPanel()
  })
  window.addEventListener('storage', (event) => {
    if (event.key === LEAD_OPS_STORAGE_KEY && opsMode) {
      renderPanel()
    }
  })

  if (opsMode) {
    panel.classList.remove('hidden')
    document.body.appendChild(panel)
    renderPanel()
  }

  runSlaCheck()
  window.setInterval(() => {
    runSlaCheck()
    if (opsMode) renderPanel()
  }, 60 * 1000)
}

function getScrollPercent() {
  const doc = document.documentElement
  const body = document.body
  const scrollTop = doc.scrollTop || body.scrollTop
  const scrollHeight = doc.scrollHeight || body.scrollHeight
  const clientHeight = doc.clientHeight || window.innerHeight
  const maxScroll = Math.max(scrollHeight - clientHeight, 1)
  return Math.min(100, Math.round((scrollTop / maxScroll) * 100))
}

function setupScrollDepthTracking() {
  const reached = new Set()

  const onScroll = () => {
    const percent = getScrollPercent()
    ANALYTICS_MILESTONES.forEach((milestone) => {
      if (percent >= milestone && !reached.has(milestone)) {
        reached.add(milestone)
        trackEvent('scroll_depth', {
          page_path: window.location.pathname,
          scroll_percent: milestone
        })
      }
    })
  }

  window.addEventListener('scroll', onScroll, { passive: true })
  onScroll()
}

function setupClickTracking() {
  document.addEventListener('click', (event) => {
    const target = event.target
    if (!(target instanceof Element)) return
    const tracked = target.closest('[data-track]')
    if (!(tracked instanceof HTMLElement)) return

    const ctaId = tracked.getAttribute('data-track')
    if (!ctaId) return

    trackEvent('cta_click', {
      page_path: window.location.pathname,
      cta_id: ctaId
    })
  })
}

function setupLeadForm() {
  const form = document.getElementById('lead-form')
  if (!form) return

  ensureLeadHoneypot(form)
  const feedback = document.getElementById('lead-feedback')
  const nome = form.querySelector('[name="nome"]')
  const telefone = form.querySelector('[name="telefone"]')
  const interesse = form.querySelector('[name="interesse"]')

  form.addEventListener('submit', async (event) => {
    event.preventDefault()
    clearLeadSubmitFeedback(feedback)

    const payload = {
      nome: nome?.value?.trim() || '',
      telefone: telefone?.value?.trim() || '',
      interesse: interesse?.value?.trim() || ''
    }

    if (!payload.nome || !payload.telefone || !payload.interesse) {
      if (feedback) {
        feedback.textContent = 'Preencha os campos obrigatórios.'
        playFeedbackPop(feedback)
      }
      return
    }

    if (!isValidLeadPhone(payload.telefone)) {
      if (feedback) {
        feedback.textContent = LEAD_PHONE_MESSAGE
        playFeedbackPop(feedback)
      }
      telefone?.focus()
      return
    }

    trackEvent('generate_lead', {
      page_path: window.location.pathname,
      lead_channel: 'form_whatsapp',
      lead_interest: payload.interesse
    })

    const leadOpsEntry = recordLeadOpsItem({
      lead_type: 'home',
      lead_channel: 'form_whatsapp',
      nome: payload.nome,
      telefone: payload.telefone,
      interesse: payload.interesse
    })

    const submitResult = await submitLeadToWebhook({
      lead_channel: 'form_whatsapp',
      lead_type: 'home',
      nome: payload.nome,
      telefone: payload.telefone,
      interesse: payload.interesse
    })
    finalizeLeadOpsItem(leadOpsEntry.id, submitResult)

    const attribution = getAttribution()
    const sourceSuffix = attribution.utm_source ? ` Origem: ${attribution.utm_source}/${attribution.utm_medium || 'na'}.` : ''
    const message = encodeURIComponent(
      `Olá, sou ${payload.nome}. Meu WhatsApp é ${payload.telefone}. Tenho interesse em ${payload.interesse}.${sourceSuffix}`
    )
    const whatsappUrl = `${WHATSAPP_BASE_URL}?text=${message}`

    applyLeadSubmitFeedback(feedback, submitResult)
    window.open(whatsappUrl, '_blank', 'noopener,noreferrer')
    if (shouldResetLeadForm(submitResult)) {
      form.reset()
    }
  })
}

function setupProductCatalogTools() {
  const section = document.getElementById('catalogo-linhas')
  const grid = document.getElementById('catalog-grid')
  if (!section || !grid) return

  const searchInput = document.getElementById('catalog-search')
  const filterButtons = section.querySelectorAll('.filter-chip')
  const comparePanel = document.getElementById('compare-panel')
  const compareList = document.getElementById('compare-list')
  const compareClear = document.getElementById('compare-clear')
  const compareContact = document.getElementById('compare-contact')

  const lineMeta = {
    '/case/escavadeiras-hidraulicas/': {
      key: 'escavadeiras-hidraulicas',
      name: 'Escavadeiras Hidráulicas',
      models: 5,
      applications: ['construcao', 'locacao'],
      compareModels: [
        { name: 'CX220C', power: '147 hp', weight: '22.149 kg', destaque: 'Caçamba: 1,2 m³' },
        { name: 'CX350C', power: '268 hp', weight: '35.700 kg', destaque: 'Caçamba: 2,1 m³' }
      ]
    },
    '/case/minicarregadeiras/': {
      key: 'minicarregadeiras',
      name: 'Minicarregadeiras',
      models: 6,
      applications: ['locacao', 'urbanismo', 'agro'],
      compareModels: [
        { name: 'SV300B', power: '90 hp', weight: '3.765 kg', destaque: 'Carga operacional: 1.360 kg' },
        { name: 'SR175B', power: '67 hp', weight: '2.930 kg', destaque: 'Carga operacional: 790 kg' }
      ]
    },
    '/case/miniescavadeiras/': {
      key: 'miniescavadeiras',
      name: 'Miniescavadeiras',
      models: 2,
      applications: ['urbanismo', 'agro'],
      compareModels: [
        { name: 'CX22D', power: '20.9 hp', weight: '2.190 kg', destaque: 'Profundidade: 2,4 m' },
        { name: 'CX35D', power: '24.8 hp', weight: '3.500 kg', destaque: 'Profundidade: 3,2 m' }
      ]
    },
    '/case/motoniveladoras/': {
      key: 'motoniveladoras',
      name: 'Motoniveladoras',
      models: 3,
      applications: ['construcao', 'agro'],
      compareModels: [
        { name: '865B', power: '193 hp', weight: '17.216 kg', destaque: 'Lâmina: 3,7 m' },
        { name: '845B', power: '174 hp', weight: '15.600 kg', destaque: 'Lâmina: 3,7 m' }
      ]
    },
    '/case/pas-carregadeiras/': {
      key: 'pas-carregadeiras',
      name: 'Pás-Carregadeiras',
      models: 4,
      applications: ['construcao', 'agro', 'locacao'],
      compareModels: [
        { name: 'W20G', power: '142 hp', weight: '11.800 kg', destaque: 'Caçamba: até 2,3 m³' },
        { name: '821E', power: '204 hp', weight: '17.500 kg', destaque: 'Caçamba: até 3,4 m³' }
      ]
    },
    '/case/retroescavadeiras/': {
      key: 'retroescavadeiras',
      name: 'Retroescavadeiras',
      models: 2,
      applications: ['construcao', 'agro', 'locacao'],
      compareModels: [
        { name: '580N', power: '96 hp', weight: '7.662 kg', destaque: 'Profundidade: 4,3 m' },
        { name: '575SV', power: '85 hp', weight: '7.200 kg', destaque: 'Profundidade: 4,1 m' }
      ]
    },
    '/case/rolo-compactador/': {
      key: 'rolo-compactador',
      name: 'Rolo Compactador',
      models: 1,
      applications: ['construcao', 'urbanismo'],
      compareModels: [
        { name: '1107EX', power: '110 hp', weight: '13.200 kg', destaque: 'Tambor: 2,13 m' }
      ]
    },
    '/case/tratores-de-esteiras/': {
      key: 'tratores-de-esteiras',
      name: 'Tratores de Esteiras',
      models: 5,
      applications: ['construcao', 'agro'],
      compareModels: [
        { name: '2050M', power: '130 hp', weight: '13.138 kg', destaque: 'Lâmina: PAT 3,1 m' },
        { name: '850M', power: '100 hp', weight: '9.500 kg', destaque: 'Lâmina: PAT 2,9 m' }
      ]
    }
  }

  const cards = [...grid.querySelectorAll('a.group.block')]
  const lineByKey = Object.values(lineMeta).reduce((acc, meta) => {
    acc[meta.key] = meta
    return acc
  }, {})
  const comparePathByKey = Object.entries(lineMeta).reduce((acc, [path, meta]) => {
    acc[meta.key] = path
    return acc
  }, {})
  const selected = new Map()

  const params = new URLSearchParams(window.location.search)
  const initialFilter = params.get('f')
  let activeFilter = initialFilter && [...filterButtons].some((btn) => btn.getAttribute('data-filter') === initialFilter)
    ? initialFilter
    : 'all'
  const initialSearch = params.get('q') || ''
  if (searchInput) searchInput.value = initialSearch

  const initialCompare = (params.get('cmp') || '').split(',').map((value) => value.trim()).filter(Boolean)
  const initialModelMap = (params.get('m') || '').split(',').reduce((acc, chunk) => {
    const [key, idxRaw] = chunk.split(':')
    const idx = Number(idxRaw)
    if (key && Number.isInteger(idx)) acc[key] = idx
    return acc
  }, {})

  initialCompare.slice(0, 3).forEach((key) => {
    if (!lineByKey[key]) return
    const idx = initialModelMap[key]
    const safeIdx = Number.isInteger(idx) && idx >= 0 && idx < lineByKey[key].compareModels.length ? idx : 0
    selected.set(key, safeIdx)
  })

  cards.forEach((anchor) => {
    const pathname = new URL(anchor.href).pathname.endsWith('/')
      ? new URL(anchor.href).pathname
      : `${new URL(anchor.href).pathname}/`
    const meta = lineMeta[pathname]
    if (!meta) return

    anchor.dataset.line = meta.name.toLowerCase()
    anchor.dataset.apps = meta.applications.join(' ')
    anchor.dataset.key = meta.key

    const card = anchor.querySelector('.industrial-border')
    if (!card) return

    const compareToggle = document.createElement('button')
    compareToggle.type = 'button'
    compareToggle.className = 'compare-toggle'
    compareToggle.textContent = 'Comparar'
    compareToggle.setAttribute('data-key', meta.key)
    compareToggle.setAttribute('data-track', 'produtos_compare_toggle')

    compareToggle.addEventListener('click', (event) => {
      event.preventDefault()
      event.stopPropagation()

      if (selected.has(meta.key)) {
        selected.delete(meta.key)
      } else {
        if (selected.size >= 3) return
        selected.set(meta.key, 0)
      }
      renderCompare()
      updateCompareButtons()
      syncCatalogStateUrl()
      trackEvent('compare_update', {
        page_path: window.location.pathname,
        selected_count: selected.size
      })
    })

    card.appendChild(compareToggle)
  })

  function updateCompareButtons() {
    grid.querySelectorAll('[data-key]').forEach((btn) => {
      const key = btn.getAttribute('data-key')
      const isSelected = selected.has(key)
      btn.textContent = isSelected ? 'Selecionado' : 'Comparar'
      btn.classList.toggle('is-selected', isSelected)
    })
  }

  function syncCatalogStateUrl() {
    const url = new URL(window.location.href)
    const query = url.searchParams
    query.delete('f')
    query.delete('q')
    query.delete('cmp')
    query.delete('m')

    const term = (searchInput?.value || '').trim().toLowerCase()
    if (activeFilter !== 'all') query.set('f', activeFilter)
    if (term) query.set('q', term)
    if (selected.size > 0) {
      const compareKeys = [...selected.keys()]
      query.set('cmp', compareKeys.join(','))
      const modelState = compareKeys.map((key) => `${key}:${selected.get(key)}`)
      query.set('m', modelState.join(','))
    }
    window.history.replaceState({}, '', `${url.pathname}${query.toString() ? `?${query.toString()}` : ''}`)
  }

  function renderCompare() {
    if (!comparePanel || !compareList) return

    const entries = [...selected.entries()]
    if (entries.length === 0) {
      comparePanel.classList.add('hidden')
      compareList.innerHTML = ''
      if (compareContact) {
        compareContact.href = `${WHATSAPP_BASE_URL}?text=Ol%C3%A1%2C%20quero%20comparar%20linhas%20de%20m%C3%A1quinas%20CASE.`
      }
      return
    }

    comparePanel.classList.remove('hidden')
    compareList.innerHTML = entries.map(([key, modelIndex]) => {
      const path = comparePathByKey[key]
      const meta = lineMeta[path]
      if (!meta) return ''
      const safeIndex = Number.isInteger(modelIndex) && modelIndex >= 0 && modelIndex < meta.compareModels.length ? modelIndex : 0
      const model = meta.compareModels[safeIndex]
      const options = meta.compareModels.map((item, idx) => (
        `<option value="${idx}" ${idx === safeIndex ? 'selected' : ''}>${item.name}</option>`
      )).join('')
      return `
        <article class="compare-item">
          <div class="flex items-start justify-between gap-3 mb-3">
            <h4 class="font-bold uppercase text-sm">${meta.name}</h4>
            <button type="button" class="text-xs text-case-yellow font-mono" data-remove-key="${meta.key}">remover</button>
          </div>
          <div class="mb-3">
            <label class="block text-[10px] font-mono uppercase tracking-widest text-gray-500 mb-1">Modelo de referência</label>
            <select class="input-field compare-model-select" data-model-key="${meta.key}">
              ${options}
            </select>
          </div>
          <div class="space-y-1 text-xs font-mono uppercase tracking-widest text-gray-400">
            <p>Modelos: <span class="text-white">${meta.models}</span></p>
            <p>Modelo: <span class="text-white">${model.name}</span></p>
            <p>Potência: <span class="text-white">${model.power}</span></p>
            <p>Peso op.: <span class="text-white">${model.weight}</span></p>
            <p>Destaque: <span class="text-white">${model.destaque}</span></p>
            <p>Aplicação: <span class="text-white">${meta.applications.join(', ')}</span></p>
          </div>
        </article>
      `
    }).join('')

    if (compareContact) {
      const selectedModels = entries.map(([key, modelIndex]) => {
        const path = comparePathByKey[key]
        const meta = lineMeta[path]
        const model = meta?.compareModels[modelIndex] || meta?.compareModels[0]
        return model?.name
      }).filter(Boolean)
      const whatsappText = encodeURIComponent(`Olá, quero comparar os modelos: ${selectedModels.join(', ')}.`)
      compareContact.href = `${WHATSAPP_BASE_URL}?text=${whatsappText}`
    }
  }

  function applyFilters() {
    const term = (searchInput?.value || '').trim().toLowerCase()
    let visibleCount = 0

    cards.forEach((anchor) => {
      const line = anchor.dataset.line || ''
      const apps = anchor.dataset.apps || ''
      const matchesFilter = activeFilter === 'all' || apps.includes(activeFilter)
      const matchesTerm = term === '' || line.includes(term) || apps.includes(term)
      const visible = matchesFilter && matchesTerm
      anchor.classList.toggle('hidden', !visible)
      if (visible) visibleCount += 1
    })

    trackEvent('catalog_filter', {
      page_path: window.location.pathname,
      filter: activeFilter,
      search_term: term,
      visible_items: visibleCount
    })
    syncCatalogStateUrl()
  }

  filterButtons.forEach((btn) => {
    btn.classList.toggle('is-active', btn.getAttribute('data-filter') === activeFilter)
    btn.addEventListener('click', () => {
      activeFilter = btn.getAttribute('data-filter') || 'all'
      filterButtons.forEach((other) => other.classList.toggle('is-active', other === btn))
      applyFilters()
    })
  })

  searchInput?.addEventListener('input', applyFilters)

  compareList?.addEventListener('click', (event) => {
    const target = event.target
    if (!(target instanceof HTMLElement)) return
    const key = target.getAttribute('data-remove-key')
    if (!key) return
    selected.delete(key)
    renderCompare()
    updateCompareButtons()
    syncCatalogStateUrl()
  })

  compareList?.addEventListener('change', (event) => {
    const target = event.target
    if (!(target instanceof HTMLSelectElement)) return
    const key = target.getAttribute('data-model-key')
    if (!key || !selected.has(key)) return
    const newIndex = Number(target.value)
    selected.set(key, Number.isInteger(newIndex) && newIndex >= 0 ? newIndex : 0)
    renderCompare()
    syncCatalogStateUrl()
    trackEvent('compare_model_change', {
      page_path: window.location.pathname,
      line_key: key
    })
  })

  compareClear?.addEventListener('click', () => {
    selected.clear()
    renderCompare()
    updateCompareButtons()
    syncCatalogStateUrl()
  })

  applyFilters()
  renderCompare()
  updateCompareButtons()
}

function setupProductPageEnhancements() {
  const parts = window.location.pathname.split('/').filter(Boolean)
  const brandRoots = ['case', 'dynapac']
  if (!brandRoots.includes(parts[0]) || parts.length !== 3) return
  if (parts[0] === 'case' && parts[1] === 'catalogo') return

  const [, catSlug] = parts
  const main = document.querySelector('main')
  const titleEl = document.querySelector('h1')
  if (!main || !titleEl) return

  const modelName = titleEl.textContent.trim()
  const fitByCategory = {
    'escavadeiras-hidraulicas': [
      ['Terraplenagem pesada', 'Alta produtividade para escavação contínua e ciclo de carga intenso.'],
      ['Obras de infraestrutura', 'Entrega estabilidade e força para frentes com alto volume de movimentação.'],
      ['Operação de longa jornada', 'Cabine e manutenção pensadas para disponibilidade operacional.']
    ],
    'retroescavadeiras': [
      ['Obras urbanas', 'Versatilidade para escavação, carregamento e apoio em espaços reduzidos.'],
      ['Manutenção de rede', 'Troca rápida de aplicação e mobilidade entre múltiplos pontos.'],
      ['Operação mista', 'Boa relação entre desempenho e custo operacional para frentes variadas.']
    ],
    'pas-carregadeiras': [
      ['Carga e movimentação', 'Alto rendimento por ciclo para materiais diversos.'],
      ['Pátios e mineração leve', 'Robustez para trabalho contínuo com menor tempo de manobra.'],
      ['Operação em agroindústria', 'Capacidade para alimentação de planta e suporte logístico.']
    ],
    'minicarregadeiras': [
      ['Locação e múltiplos clientes', 'Equipamento versátil para diferentes frentes com troca rápida de implemento.'],
      ['Serviços urbanos', 'Agilidade em espaços reduzidos e menor impacto operacional.'],
      ['Apoio em obras', 'Boa produtividade em tarefas de acabamento e movimentação leve.']
    ],
    'motoniveladoras': [
      ['Nivelamento de vias', 'Precisão de lâmina para acabamento e regularização de superfície.'],
      ['Estradas rurais', 'Desempenho consistente em manutenção de trechos extensos.'],
      ['Infraestrutura linear', 'Controle operacional para padrões rigorosos de nivelamento.']
    ],
    'miniescavadeiras': [
      ['Áreas confinadas', 'Dimensões compactas para operação segura em espaços limitados.'],
      ['Obras urbanas leves', 'Produtividade com menor intervenção de canteiro.'],
      ['Paisagismo e utilidades', 'Precisão de escavação para serviços detalhados.']
    ],
    'rolo-compactador': [
      ['Base e sub-base', 'Compactação consistente para aumento da vida útil do pavimento.'],
      ['Infraestrutura urbana', 'Eficiência operacional em projetos de vias e loteamentos.'],
      ['Frentes contínuas', 'Bom desempenho para ritmo constante de compactação.']
    ],
    'tratores-de-esteiras': [
      ['Empuxo em terrenos severos', 'Força e tração para movimentação de material em condição crítica.'],
      ['Abertura de área', 'Produtividade para limpeza e conformação de terreno.'],
      ['Operação em agro', 'Suporte robusto para infraestrutura e manutenção de áreas produtivas.']
    ]
  }

  const fitCases = fitByCategory[catSlug] || [
    ['Aplicação principal', 'Configuração indicada para alta produtividade operacional.'],
    ['Aplicação secundária', 'Boa adaptação para cenários mistos com demanda variável.'],
    ['Aplicação estratégica', 'Redução de risco operacional com suporte técnico regional.']
  ]

  const faqByCategory = {
    'escavadeiras-hidraulicas': [
      ['Esse modelo atende operação contínua?', 'Sim. É indicado para ciclos longos e aplicações de alta demanda, com foco em produtividade e disponibilidade.'],
      ['Como funciona o suporte técnico?', 'A IBL atende com equipe regional e plano de manutenção preventiva para reduzir paradas não planejadas.'],
      ['É possível avaliar custo operacional?', 'Sim. A proposta comercial pode incluir cenário de consumo, manutenção e recomendação por tipo de aplicação.']
    ],
    'retroescavadeiras': [
      ['Esse modelo é indicado para obra urbana?', 'Sim. É uma linha versátil para frentes com espaço limitado e múltiplas tarefas operacionais.'],
      ['A máquina aceita diferentes implementos?', 'Sim. A configuração pode variar por necessidade de operação e disponibilidade técnica.'],
      ['Vocês apoiam na escolha da configuração?', 'Sim. O time comercial-técnico orienta a seleção conforme aplicação e produtividade esperada.']
    ],
    'pas-carregadeiras': [
      ['Qual o diferencial da linha em produtividade?', 'Capacidade de carga por ciclo, robustez estrutural e apoio de pós-venda para manter a operação ativa.'],
      ['Há suporte para operação intensa?', 'Sim. Existe cobertura de peças, serviço técnico e planos de manutenção conforme criticidade da frota.'],
      ['Posso comparar versões antes da proposta?', 'Sim. A equipe monta comparação técnica e comercial orientada ao seu cenário.']
    ],
    'minicarregadeiras': [
      ['A linha atende locação?', 'Sim. É uma das aplicações mais comuns, especialmente pela versatilidade e troca de implementos.'],
      ['É indicada para uso urbano?', 'Sim. O porte compacto favorece mobilidade e produtividade em áreas restritas.'],
      ['Existe recomendação por tipo de serviço?', 'Sim. A recomendação considera aplicação principal, carga de trabalho e disponibilidade.']
    ],
    'motoniveladoras': [
      ['É adequada para nivelamento de vias?', 'Sim. A linha é focada em acabamento e regularização com controle operacional preciso.'],
      ['Como é feito o suporte pós-venda?', 'Com atendimento regional e planejamento de manutenção para manter desempenho em operação contínua.'],
      ['Vocês ajudam na escolha por aplicação?', 'Sim. A recomendação é feita com base no tipo de terreno, frequência e exigência de produtividade.']
    ],
    'miniescavadeiras': [
      ['É indicada para áreas confinadas?', 'Sim. O porte compacto facilita operação segura em espaços reduzidos.'],
      ['Atende obras leves e utilidades?', 'Sim. É bastante usada em serviços urbanos, redes e paisagismo.'],
      ['Há apoio para definir implementos?', 'Sim. A equipe orienta configuração conforme serviço e ganho operacional esperado.']
    ],
    'rolo-compactador': [
      ['A linha atende base e sub-base?', 'Sim. Foi projetada para compactação consistente em obras de infraestrutura.'],
      ['É possível montar plano de manutenção?', 'Sim. O pós-venda define rotinas preventivas para manter desempenho e disponibilidade.'],
      ['Vocês oferecem proposta técnica-comercial?', 'Sim. A proposta considera escopo da obra, ritmo operacional e janela de execução.']
    ],
    'tratores-de-esteiras': [
      ['Esse modelo atende terrenos severos?', 'Sim. A linha é indicada para operações de alto esforço com tração e empuxo consistentes.'],
      ['Serve para abertura e conformação de área?', 'Sim. É uma das aplicações centrais da categoria em obras e agro.'],
      ['Como funciona o atendimento comercial?', 'Após envio dos dados, a equipe retorna com recomendação de configuração e disponibilidade.']
    ]
  }
  const faqItems = faqByCategory[catSlug] || [
    ['Esse modelo é indicado para minha operação?', 'A recomendação depende do tipo de aplicação, carga de trabalho e meta de produtividade.'],
    ['Como funciona o suporte técnico?', 'A IBL oferece atendimento regional e acompanhamento para manter disponibilidade operacional.'],
    ['Como recebo proposta comercial?', 'Envie o formulário com seu cenário e retornamos com recomendação técnica e condições comerciais.']
  ]

  const firstCtaSection = [...main.querySelectorAll('section')].find((section) => (
    section.textContent.includes('Solicitar Orçamento') &&
    section.textContent.includes('Falar com Consultor')
  ))
  if (!firstCtaSection) return

  if (!document.getElementById('product-fit-section')) {
    const fitSection = document.createElement('section')
    fitSection.id = 'product-fit-section'
    fitSection.className = 'py-16 bg-case-dark border-t border-case-border'
    fitSection.innerHTML = `
      <div class="container mx-auto px-6">
        <span class="font-mono text-case-yellow text-sm tracking-widest uppercase block mb-2">/// Fit por uso</span>
        <h2 class="font-display font-black text-3xl md:text-4xl uppercase mb-8">Onde este modelo performa melhor</h2>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          ${fitCases.map(([title, text]) => `
            <article class="product-fit-card">
              <h3 class="product-fit-title">${title}</h3>
              <p class="product-fit-text">${text}</p>
            </article>
          `).join('')}
        </div>
      </div>
    `
    firstCtaSection.parentElement.insertBefore(fitSection, firstCtaSection)
  }

  if (!document.getElementById('product-faq-section')) {
    const faqSection = document.createElement('section')
    faqSection.id = 'product-faq-section'
    faqSection.className = 'py-16 bg-case-dark border-t border-case-border'
    faqSection.innerHTML = `
      <div class="container mx-auto px-6">
        <span class="font-mono text-case-yellow text-sm tracking-widest uppercase block mb-2">/// FAQ Técnico e Comercial</span>
        <h2 class="font-display font-black text-3xl md:text-4xl uppercase mb-8">Perguntas frequentes</h2>
        <div class="space-y-3" id="product-faq-list">
          ${faqItems.map(([question, answer], idx) => `
            <article class="faq-item ${idx === 0 ? 'is-open' : ''}">
              <button class="faq-question" type="button" aria-expanded="${idx === 0 ? 'true' : 'false'}" data-faq-index="${idx}">
                <span>${question}</span>
                <i class="ph-bold ph-plus text-case-yellow"></i>
              </button>
              <div class="faq-answer">
                <p>${answer}</p>
              </div>
            </article>
          `).join('')}
        </div>
      </div>
    `
    firstCtaSection.parentElement.insertBefore(faqSection, firstCtaSection)

    const faqList = faqSection.querySelector('#product-faq-list')
    faqList?.addEventListener('click', (event) => {
      const target = event.target
      if (!(target instanceof HTMLElement)) return
      const trigger = target.closest('.faq-question')
      if (!(trigger instanceof HTMLButtonElement)) return
      const item = trigger.closest('.faq-item')
      if (!item) return
      const isOpen = item.classList.toggle('is-open')
      trigger.setAttribute('aria-expanded', isOpen ? 'true' : 'false')
      trackEvent('faq_toggle', {
        page_path: window.location.pathname,
        faq_index: trigger.getAttribute('data-faq-index'),
        faq_open: isOpen
      })
    })
  }

  firstCtaSection.id = 'produto-contato'
  firstCtaSection.innerHTML = `
    <div class="container mx-auto px-6">
      <div class="product-contact-wrap">
        <span class="font-mono text-case-yellow text-sm tracking-widest uppercase block mb-3">/// Solicitação Rápida</span>
        <h2 class="font-display font-black text-3xl md:text-4xl uppercase mb-3">Quero proposta para ${modelName}</h2>
        <p class="text-gray-400 mb-6">Preencha os dados e nossa equipe retorna com recomendação comercial e disponibilidade para sua região.</p>
        <form id="product-lead-form" class="space-y-4">
          <input type="hidden" name="modelo" value="${modelName}">
          <input type="hidden" name="categoria" value="${catSlug}">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
            <div>
              <label class="block text-xs font-mono uppercase tracking-widest text-gray-400 mb-2" for="product-lead-nome">Nome</label>
              <input class="input-field" id="product-lead-nome" name="nome" required placeholder="Seu nome completo">
            </div>
            <div>
              <label class="block text-xs font-mono uppercase tracking-widest text-gray-400 mb-2" for="product-lead-whatsapp">WhatsApp</label>
              <input class="input-field" id="product-lead-whatsapp" name="telefone" type="tel" inputmode="tel" autocomplete="tel" required placeholder="(00) 00000-0000">
            </div>
          </div>
          <div>
            <label class="block text-xs font-mono uppercase tracking-widest text-gray-400 mb-2" for="product-lead-uso">Aplicação principal</label>
            <input class="input-field" id="product-lead-uso" name="uso" required placeholder="Ex.: terraplenagem pesada, locação, obras urbanas">
          </div>
          <label class="flex items-start gap-3 pt-1 text-xs text-gray-400 leading-relaxed cursor-pointer">
            <input type="checkbox" name="consentimento" required class="mt-0.5 accent-[var(--color-case-yellow)]">
            <span>Autorizo o uso dos meus dados para contato comercial, conforme a <a href="/privacidade/" class="underline hover:text-case-yellow" target="_blank">Política de Privacidade</a>.</span>
          </label>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2">
            <button data-track="product_lead_submit" type="submit" class="btn btn-primary w-full">Solicitar orçamento</button>
            <a data-track="product_lead_whatsapp" href="${WHATSAPP_BASE_URL}?text=${encodeURIComponent(`Olá, tenho interesse no modelo ${modelName}.`) }" target="_blank" rel="noopener noreferrer" class="btn btn-secondary w-full">
              Falar no WhatsApp
            </a>
          </div>
          <p id="product-lead-feedback" role="status" aria-live="polite" class="text-xs font-mono uppercase tracking-widest text-gray-500"></p>
          ${document.body?.dataset?.brand === 'dynapac' ? '' : '<a data-track="product_consorcio_cta" href="/consorcio/" class="block text-center text-xs font-mono uppercase tracking-widest text-case-yellow hover:underline pt-1">Prefere comprar sem juros? Conheça o Consórcio CASE →</a>'}
        </form>
      </div>
    </div>
  `

  const productForm = document.getElementById('product-lead-form')
  ensureLeadHoneypot(productForm)
  const productFeedback = document.getElementById('product-lead-feedback')
  productForm?.addEventListener('submit', async (event) => {
    event.preventDefault()
    clearLeadSubmitFeedback(productFeedback)
    const formData = new FormData(productForm)
    const payload = Object.fromEntries(formData.entries())

    if (!payload.nome || !payload.telefone || !payload.uso) {
      if (productFeedback) {
        productFeedback.textContent = 'Preencha os campos obrigatórios.'
        playFeedbackPop(productFeedback)
      }
      return
    }

    if (!isValidLeadPhone(payload.telefone)) {
      if (productFeedback) {
        productFeedback.textContent = LEAD_PHONE_MESSAGE
        playFeedbackPop(productFeedback)
      }
      productForm.querySelector('[name="telefone"]')?.focus()
      return
    }

    trackEvent('generate_lead', {
      page_path: window.location.pathname,
      lead_channel: 'product_form_whatsapp',
      lead_model: payload.modelo,
      lead_category: payload.categoria
    })

    const leadOpsEntry = recordLeadOpsItem({
      lead_type: 'product',
      lead_channel: 'product_form_whatsapp',
      nome: String(payload.nome || ''),
      telefone: String(payload.telefone || ''),
      uso: String(payload.uso || ''),
      modelo: String(payload.modelo || ''),
      categoria: String(payload.categoria || '')
    })

    const submitResult = await submitLeadToWebhook({
      lead_channel: 'product_form_whatsapp',
      lead_type: 'product',
      nome: String(payload.nome || ''),
      telefone: String(payload.telefone || ''),
      uso: String(payload.uso || ''),
      modelo: String(payload.modelo || ''),
      categoria: String(payload.categoria || '')
    })
    finalizeLeadOpsItem(leadOpsEntry.id, submitResult)

    const attribution = getAttribution()
    const sourceSuffix = attribution.utm_source ? ` Origem: ${attribution.utm_source}/${attribution.utm_medium || 'na'}.` : ''
    const message = encodeURIComponent(
      `Olá, sou ${payload.nome}. Meu WhatsApp é ${payload.telefone}. Tenho interesse no modelo ${payload.modelo} para ${payload.uso}.${sourceSuffix}`
    )
    window.open(`${WHATSAPP_BASE_URL}?text=${message}`, '_blank', 'noopener,noreferrer')
    applyLeadSubmitFeedback(productFeedback, submitResult)
    if (shouldResetLeadForm(submitResult)) {
      productForm.reset()
    }
  })

  if (!document.getElementById('product-sticky-cta')) {
    const sticky = document.createElement('div')
    sticky.id = 'product-sticky-cta'
    sticky.className = 'product-sticky-cta'
    sticky.innerHTML = `
      <div class="product-sticky-inner">
        <span class="product-sticky-label">Interessado em ${modelName}? Fale com especialista agora.</span>
        <a class="btn btn-primary" href="#produto-contato">Solicitar proposta</a>
      </div>
    `
    document.body.appendChild(sticky)
    const toggleSticky = () => {
      const scrollPercent = getScrollPercent()
      sticky.classList.toggle('is-visible', scrollPercent >= 30 && scrollPercent < 95)
    }
    window.addEventListener('scroll', toggleSticky, { passive: true })
    toggleSticky()
  }
}

function upsertMeta(nameOrProperty, content, isProperty = false) {
  if (!content) return
  const selector = isProperty ? `meta[property="${nameOrProperty}"]` : `meta[name="${nameOrProperty}"]`
  let el = document.head.querySelector(selector)
  if (!el) {
    el = document.createElement('meta')
    if (isProperty) {
      el.setAttribute('property', nameOrProperty)
    } else {
      el.setAttribute('name', nameOrProperty)
    }
    document.head.appendChild(el)
  }
  el.setAttribute('content', content)
}

function upsertCanonical(href) {
  if (!href) return
  let link = document.head.querySelector('link[rel="canonical"]')
  if (!link) {
    link = document.createElement('link')
    link.setAttribute('rel', 'canonical')
    document.head.appendChild(link)
  }
  link.setAttribute('href', href)
}

function upsertJsonLd(id, jsonObject) {
  let script = document.head.querySelector(`script[data-schema-id="${id}"]`)
  if (!script) {
    script = document.createElement('script')
    script.type = 'application/ld+json'
    script.setAttribute('data-schema-id', id)
    document.head.appendChild(script)
  }
  script.textContent = JSON.stringify(jsonObject)
}

function hasJsonLdType(type) {
  return [...document.head.querySelectorAll('script[type="application/ld+json"]')].some((script) => {
    const text = script.textContent || ''
    return text.includes(`"@type":"${type}"`) || text.includes(`"@type": "${type}"`)
  })
}

function getBreadcrumbItems(url) {
  const breadcrumbNav = document.querySelector('[data-breadcrumb-nav]') || document.querySelector('nav[aria-label="Breadcrumb"]')
  if (!(breadcrumbNav instanceof HTMLElement)) return []

  const breadcrumbLinks = [...breadcrumbNav.querySelectorAll('a[href]')].map((anchor, idx) => {
    const name = anchor.textContent?.trim() || ''
    const item = anchor.href
    if (!name || !item) return null

    return {
      '@type': 'ListItem',
      position: idx + 1,
      name,
      item
    }
  }).filter(Boolean)

  const breadcrumbCurrent = breadcrumbNav.querySelector('[aria-current="page"]')?.textContent?.trim()
  if (breadcrumbCurrent) {
    breadcrumbLinks.push({
      '@type': 'ListItem',
      position: breadcrumbLinks.length + 1,
      name: breadcrumbCurrent,
      item: url
    })
  }

  return breadcrumbLinks
}

function setupSeoEnhancements() {
  const { origin, pathname } = window.location
  const url = `${origin}${pathname}`
  const isGeneratedRoute = pathname === '/case/' || pathname.startsWith('/case/')
  const isProductPage = pathname.split('/').filter(Boolean).length === 3 && pathname.startsWith('/case/')
  const pageTitle = document.querySelector('title')?.textContent || 'IBL Máquinas'
  const h1 = document.querySelector('h1')?.textContent?.trim() || ''
  const firstDescription = document.querySelector('main p')?.textContent?.trim() || ''
  const description = firstDescription || 'Distribuidor oficial CASE com catálogo completo, suporte técnico e pós-venda regional.'
  const hasGeneratedSeoBaseline = isGeneratedRoute
    && document.head.querySelector('meta[name="description"]')
    && document.head.querySelector('meta[property="og:title"]')
    && document.head.querySelector('meta[name="twitter:title"]')
    && document.head.querySelector('link[rel="canonical"]')
    && hasJsonLdType('BreadcrumbList')

  const faqEntries = [...document.querySelectorAll('#product-faq-list .faq-item')].map((item) => {
    const q = item.querySelector('.faq-question span')?.textContent?.trim()
    const a = item.querySelector('.faq-answer p')?.textContent?.trim()
    return q && a ? {
      '@type': 'Question',
      name: q,
      acceptedAnswer: {
        '@type': 'Answer',
        text: a
      }
    } : null
  }).filter(Boolean)

  if (hasGeneratedSeoBaseline) {
    if (isProductPage && faqEntries.length > 0 && !hasJsonLdType('FAQPage')) {
      upsertJsonLd('faq-schema', {
        '@context': 'https://schema.org',
        '@type': 'FAQPage',
        mainEntity: faqEntries
      })
    }
    return
  }

  upsertMeta('description', description)
  upsertMeta('og:title', pageTitle, true)
  upsertMeta('og:description', description, true)
  upsertMeta('og:type', isProductPage ? 'product' : 'website', true)
  upsertMeta('og:url', url, true)
  upsertMeta('twitter:card', 'summary_large_image')
  upsertMeta('twitter:title', pageTitle)
  upsertMeta('twitter:description', description)
  upsertCanonical(url)

  if (!isProductPage) return

  const image = document.querySelector('main img')?.getAttribute('src') || `${origin}/ibl-logo.png`
  const absoluteImage = image.startsWith('http') ? image : `${origin}${image}`
  const breadcrumbLinks = getBreadcrumbItems(url)

  upsertJsonLd('product-schema', {
    '@context': 'https://schema.org',
    '@type': 'Product',
    name: h1 || pageTitle,
    description,
    image: absoluteImage,
    brand: {
      '@type': 'Brand',
      name: 'CASE Construction'
    },
    seller: {
      '@type': 'Organization',
      name: 'IBL Máquinas'
    },
    url
  })

  if (breadcrumbLinks.length > 0) {
    upsertJsonLd('breadcrumb-schema', {
      '@context': 'https://schema.org',
      '@type': 'BreadcrumbList',
      itemListElement: breadcrumbLinks
    })
  }

  if (faqEntries.length > 0) {
    upsertJsonLd('faq-schema', {
      '@context': 'https://schema.org',
      '@type': 'FAQPage',
      mainEntity: faqEntries
    })
  }
}

function setupUnitsMap() {
  const mapEl = document.getElementById('unit-map')
  const unitItems = [...document.querySelectorAll('.unit-item')]
  if (!mapEl || unitItems.length === 0) return

  const LEAFLET_BASE = '/vendor/leaflet'

  function getUnitMeta(item) {
    const unitId = item.getAttribute('data-unit-id')
    const lat = Number(item.getAttribute('data-lat'))
    const lng = Number(item.getAttribute('data-lng'))
    const address = item.getAttribute('data-address') || ''
    const title = item.querySelector('h3, h4')?.textContent?.trim() || 'Unidade'
    const hasCoords = !Number.isNaN(lat) && !Number.isNaN(lng)
    const mapsUrl = `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(`IBL Máquinas - ${address}`)}`
    return { unitId, lat, lng, address, title, hasCoords, mapsUrl }
  }

  function setActive(unitId) {
    unitItems.forEach((item) => {
      const isActive = item.getAttribute('data-unit-id') === unitId
      item.classList.toggle('is-active', isActive)
      item.setAttribute('aria-pressed', isActive ? 'true' : 'false')
    })
  }

  function ensureLeaflet() {
    return new Promise((resolve, reject) => {
      if (window.L) {
        resolve(window.L)
        return
      }
      if (!document.querySelector('link[data-leaflet]')) {
        const link = document.createElement('link')
        link.rel = 'stylesheet'
        link.href = `${LEAFLET_BASE}/leaflet.css`
        link.setAttribute('data-leaflet', '')
        document.head.appendChild(link)
      }
      const script = document.createElement('script')
      script.src = `${LEAFLET_BASE}/leaflet.js`
      script.onload = () => resolve(window.L)
      script.onerror = () => reject(new Error('leaflet_load_failed'))
      document.head.appendChild(script)
    })
  }

  function renderFallback() {
    mapEl.innerHTML = `
      <div class="unit-map-fallback">
        <span class="font-mono text-xs uppercase tracking-widest text-case-yellow">Cobertura IBL</span>
        <p class="text-gray-300 text-sm leading-relaxed">8 lojas em 6 estados do Norte e Centro-Oeste. Selecione uma unidade ao lado para ver endereço e telefone.</p>
      </div>
    `
  }

  function wireItems(activateUnit) {
    unitItems.forEach((item) => {
      const meta = getUnitMeta(item)
      if (!meta.unitId) return
      item.tabIndex = 0
      item.setAttribute('role', 'button')
      item.setAttribute('aria-label', `Selecionar unidade ${meta.title}`)
      item.setAttribute('aria-controls', 'unit-map')
      item.setAttribute('aria-pressed', 'false')
      item.addEventListener('click', () => activateUnit(item))
      item.addEventListener('keydown', (event) => {
        if (event.key !== 'Enter' && event.key !== ' ') return
        event.preventDefault()
        activateUnit(item)
      })

      const infoBlock = item.querySelector('h3, h4')?.parentElement
      if (infoBlock && !infoBlock.querySelector('.unit-maps-link')) {
        const mapsLink = document.createElement('a')
        mapsLink.href = meta.mapsUrl
        mapsLink.target = '_blank'
        mapsLink.rel = 'noopener noreferrer'
        mapsLink.className = 'unit-maps-link'
        mapsLink.setAttribute('data-track', 'unit_maps_link')
        mapsLink.setAttribute('aria-label', `Abrir ${meta.title} no Google Maps`)
        mapsLink.textContent = 'Google Maps ↗'
        mapsLink.addEventListener('click', (event) => event.stopPropagation())
        infoBlock.appendChild(mapsLink)
      }
    })
  }

  ensureLeaflet()
    .then((L) => {
      mapEl.innerHTML = ''
      const map = L.map(mapEl, { scrollWheelZoom: false, attributionControl: true })
      const tileUrlForTheme = () => document.documentElement.dataset.theme === 'light'
        ? 'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png'
        : 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png'
      const tiles = L.tileLayer(tileUrlForTheme(), {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="https://carto.com/attributions">CARTO</a>',
        subdomains: 'abcd',
        maxZoom: 18
      }).addTo(map)
      window.addEventListener('ibl:theme-change', () => tiles.setUrl(tileUrlForTheme()))

      const markers = new Map()
      const bounds = []
      unitItems.forEach((item) => {
        const meta = getUnitMeta(item)
        if (!meta.unitId || !meta.hasCoords) return
        const icon = L.divIcon({
          className: 'unit-marker',
          html: '<span class="unit-marker__dot"></span>',
          iconSize: [16, 16],
          iconAnchor: [8, 8]
        })
        const marker = L.marker([meta.lat, meta.lng], { icon, title: meta.title }).addTo(map)
        marker.bindPopup(`<strong>${meta.title}</strong><br>${meta.address}<br><a class="unit-popup-link" href="${meta.mapsUrl}" target="_blank" rel="noopener noreferrer">Abrir no Google Maps →</a>`)
        marker.on('click', () => setActive(meta.unitId))
        markers.set(meta.unitId, marker)
        bounds.push([meta.lat, meta.lng])
      })
      if (bounds.length) map.fitBounds(bounds, { padding: [36, 36] })

      function activateUnit(item) {
        const meta = getUnitMeta(item)
        if (!meta.unitId) return
        setActive(meta.unitId)
        const marker = markers.get(meta.unitId)
        if (marker) {
          map.flyTo(marker.getLatLng(), 11, { duration: 1.0 })
          marker.openPopup()
        }
        trackEvent('unit_map_focus', {
          page_path: window.location.pathname,
          unit_id: meta.unitId
        })
      }

      wireItems(activateUnit)

      const defaultItem = unitItems.find((item) => item.getAttribute('data-unit-id') === 'campo-grande') || unitItems[0]
      if (defaultItem) setActive(getUnitMeta(defaultItem).unitId)
    })
    .catch(() => {
      renderFallback()
      wireItems((item) => {
        const meta = getUnitMeta(item)
        if (!meta.unitId) return
        setActive(meta.unitId)
        trackEvent('unit_map_focus', {
          page_path: window.location.pathname,
          unit_id: meta.unitId
        })
      })
    })
}

function setupChatWidget() {
  const widget = document.getElementById('chat-widget')
  const trigger = document.getElementById('chat-widget-trigger')
  const panel = document.getElementById('chat-widget-panel')
  const messages = document.getElementById('chat-widget-messages')
  const form = document.getElementById('chat-widget-form')
  const input = document.getElementById('chat-widget-input')

  if (
    !(widget instanceof HTMLElement) ||
    !(trigger instanceof HTMLButtonElement) ||
    !(panel instanceof HTMLElement) ||
    !(messages instanceof HTMLElement) ||
    !(form instanceof HTMLFormElement) ||
    !(input instanceof HTMLInputElement)
  ) {
    return
  }

  const hasProductStickyCta = !!document.querySelector('.product-sticky-cta')
  widget.classList.add(hasProductStickyCta ? 'chat-widget--offset' : 'chat-widget--docked')

  let open = false
  let replyCursor = 0
  const agentReplies = [
    'Perfeito. Qual estado e cidade da sua operação?',
    'Entendi. Você precisa de máquina nova, seminova ou locação?',
    'Posso te indicar o modelo ideal e já acelerar a proposta.',
    'Se quiser, já te chamo no WhatsApp para fechar mais rápido.'
  ]

  function setOpen(nextOpen) {
    open = nextOpen
    widget.classList.toggle('is-open', open)
    trigger.setAttribute('aria-expanded', String(open))
    if (open) {
      window.setTimeout(() => input.focus(), 120)
    }
  }

  function nowTime() {
    return new Date().toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })
  }

  function appendMessage(author, text) {
    const isAgent = author === 'agent'
    const row = document.createElement('div')
    row.className = `chat-msg-row ${isAgent ? 'chat-msg-row-agent' : 'chat-msg-row-user'}`

    const avatar = document.createElement('div')
    avatar.className = 'chat-avatar'
    avatar.textContent = isAgent ? 'IBL' : 'VC'

    const stack = document.createElement('div')
    stack.className = 'chat-msg-stack'

    const bubble = document.createElement('div')
    bubble.className = `chat-msg-bubble ${isAgent ? 'chat-msg-bubble-agent' : 'chat-msg-bubble-user'}`
    bubble.textContent = text

    const time = document.createElement('div')
    time.className = 'chat-msg-time'
    time.textContent = nowTime()

    stack.appendChild(bubble)
    stack.appendChild(time)

    if (isAgent) {
      row.appendChild(avatar)
      row.appendChild(stack)
    } else {
      row.appendChild(stack)
      row.appendChild(avatar)
    }

    messages.appendChild(row)
    messages.scrollTop = messages.scrollHeight
  }

  function getAgentReply(userText) {
    const value = userText.toLowerCase()
    if (value.includes('preço') || value.includes('preco') || value.includes('orçamento') || value.includes('orcamento')) {
      return 'Consigo sim. Me passa nome e telefone que já envio uma proposta inicial.'
    }
    if (value.includes('whatsapp') || value.includes('zap')) {
      return 'Perfeito. Vou te redirecionar para o WhatsApp da equipe IBL agora.'
    }
    const reply = agentReplies[replyCursor % agentReplies.length]
    replyCursor += 1
    return reply
  }

  trigger.addEventListener('click', (event) => {
    event.stopPropagation()
    setOpen(!open)
  })

  document.addEventListener('click', (event) => {
    if (!open) return
    const target = event.target
    if (!(target instanceof Node)) return
    if (widget.contains(target)) return
    setOpen(false)
  })

  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && open) {
      setOpen(false)
      trigger.focus()
    }
  })

  form.addEventListener('submit', (event) => {
    event.preventDefault()
    const value = input.value.trim()
    if (!value) return

    appendMessage('user', value)
    input.value = ''

    const reply = getAgentReply(value)
    window.setTimeout(() => {
      appendMessage('agent', reply)
      if (value.toLowerCase().includes('whatsapp') || value.toLowerCase().includes('zap')) {
        const text = encodeURIComponent(`Olá, vim do chat do site IBL e quero falar com um consultor. Minha mensagem: "${value}"`)
        window.open(`${WHATSAPP_BASE_URL}?text=${text}`, '_blank', 'noopener,noreferrer')
      }
    }, 650)
  })

  panel.querySelectorAll('a').forEach((anchor) => {
    anchor.addEventListener('click', () => {
      setOpen(false)
    })
  })
}

// === Machine Showcase ===
// As imagens do hero saem de scripts/hero-normalizar.py: mesmo canvas, mesma
// linha de chão e porte relativo já embutidos. Trocar de máquina é só trocar
// a imagem e os textos — não há ajuste de posição por modelo.
// Gerado por generate_pages.py a partir das fichas (data/hero-machines.json).
// Não editar à mão: mude a ficha ou a lista HERO_MACHINES do gerador.
const showcaseMachines = heroMachines

let showcaseImageTimer = null
let showcaseStateRevision = 0

function scheduleHeroReady() {
  window.requestAnimationFrame(() => {
    window.requestAnimationFrame(() => {
      document.documentElement.classList.add('hero-ready')
    })
  })
}

function applyShowcaseState(m, { animate = true } = {}) {
  const img = document.getElementById('showcase-machine')

  showcaseStateRevision += 1
  const revision = showcaseStateRevision

  if (showcaseImageTimer) {
    window.clearTimeout(showcaseImageTimer)
    showcaseImageTimer = null
  }

  if (img instanceof HTMLElement) {
    const applyImage = () => {
      if (revision !== showcaseStateRevision) return
      img.src = m.img
      img.alt = `Case ${m.model}`
      img.style.opacity = '1'
    }

    if (animate) {
      img.style.opacity = '0'
      showcaseImageTimer = window.setTimeout(() => {
        showcaseImageTimer = null
        applyImage()
      }, 280)
    } else {
      applyImage()
    }
  }
}

function switchShowcase(idx, options = {}) {
  const { animate = true, track = true } = options
  const setText = (id, value) => {
    const el = document.getElementById(id)
    if (el) el.textContent = value
  }

  const m = showcaseMachines[idx] || showcaseMachines[0]
  applyShowcaseState(m, { animate })
  setText('showcase-model', m.model)
  setText('showcase-cat', m.cat)
  const showcaseLink = document.getElementById('showcase-link')
  if (showcaseLink) showcaseLink.href = m.page
  setText('tech-cat-value', m.cat)
  ;['a', 'b', 'c'].forEach((slot, i) => {
    setText(`tech-spec-${slot}-label`, m.specs[i]?.label || '')
    setText(`tech-spec-${slot}-value`, m.specs[i]?.value || '')
  })
  const fullLink = document.getElementById('tech-full-link')
  if (fullLink) fullLink.href = m.page
  document.querySelectorAll('.cat-btn').forEach((btn, i) => {
    btn.classList.toggle('is-active', i === idx)
  })
  // No celular o seletor é uma faixa horizontal: mantém a linha ativa à vista
  // rolando só a faixa (scrollIntoView rolaria a página inteira).
  const strip = document.getElementById('cat-selector')
  const activeBtn = strip?.querySelector('.cat-btn.is-active')
  if (strip && activeBtn && strip.scrollWidth > strip.clientWidth) {
    strip.scrollTo({
      left: activeBtn.offsetLeft - (strip.clientWidth - activeBtn.offsetWidth) / 2,
      behavior: prefersReducedMotion() ? 'auto' : 'smooth'
    })
  }
  if (track) {
    trackEvent('showcase_model_change', {
      page_path: window.location.pathname,
      category: m.cat,
      model: m.model
    })
  }
}

document.querySelectorAll('.cat-btn').forEach(btn => {
  btn.addEventListener('click', () => switchShowcase(Number(btn.dataset.idx)))
})

switchShowcase(0, { animate: false, track: false })
scheduleHeroReady()

initAttribution()
setupConsent()
trackEvent('page_view_custom', { page_path: window.location.pathname })
setupScrollDepthTracking()
setupClickTracking()
setupLeadForm()
setupProductCatalogTools()
setupProductPageEnhancements()
setupSeoEnhancements()
setupLeadOpsMonitor()
setupUnitsMap()
setupChatWidget()

// ─── Tema claro/escuro (dark é o padrão) ─────────────────────────────────────
function initThemeToggle() {
  const applyIcon = () => {
    const isLight = document.documentElement.dataset.theme === 'light'
    document.querySelectorAll('[data-theme-toggle] i').forEach((icon) => {
      icon.className = isLight ? 'ph-bold ph-moon text-lg' : 'ph-bold ph-sun text-lg'
    })
    document.querySelectorAll('[data-theme-toggle]').forEach((btn) => {
      btn.setAttribute('aria-label', isLight ? 'Ativar modo escuro' : 'Ativar modo claro')
      btn.title = isLight ? 'Modo escuro' : 'Modo claro'
    })
  }
  applyIcon()
  document.querySelectorAll('[data-theme-toggle]').forEach((btn) => {
    btn.addEventListener('click', () => {
      const next = document.documentElement.dataset.theme === 'light' ? 'dark' : 'light'
      document.documentElement.dataset.theme = next
      try { localStorage.setItem('ibl_theme', next) } catch (e) {}
      window.dispatchEvent(new CustomEvent('ibl:theme-change', { detail: { theme: next } }))
      applyIcon()
      trackEvent('theme_toggle', { theme: next, page_path: window.location.pathname })
    })
  })
}

/** Usuário pediu menos movimento no sistema operacional. */
function prefersReducedMotion() {
  return window.matchMedia?.('(prefers-reduced-motion: reduce)').matches === true
}

/** Números que sobem, passam levemente do alvo e assentam.
 *  Marcação: <span data-count-to="108">108</span>. */
function setupCountUp() {
  const elements = [...document.querySelectorAll('[data-count-to]')]
  if (!elements.length) return

  const format = new Intl.NumberFormat('pt-BR')
  // Desaceleração sem ultrapassar o alvo: um catálogo não pode exibir uma
  // quantidade falsa, nem por um quadro. O peso vem do pulo de escala no fim.
  const settle = (t) => 1 - Math.pow(1 - t, 3)

  const run = (el) => {
    const target = Number(el.dataset.countTo)
    if (!Number.isFinite(target)) return
    if (prefersReducedMotion() || typeof requestAnimationFrame !== 'function') {
      el.textContent = format.format(target)
      return
    }
    const duration = 900
    const started = performance.now()
    const step = (now) => {
      const t = Math.min(1, (now - started) / duration)
      const value = t >= 1 ? target : Math.round(target * settle(t))
      el.textContent = format.format(value)
      if (t < 1) {
        requestAnimationFrame(step)
        return
      }
      el.classList.add('count-settled')
    }
    requestAnimationFrame(step)
  }

  if (typeof IntersectionObserver !== 'function') {
    elements.forEach(run)
    return
  }
  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (!entry.isIntersecting) return
      observer.unobserve(entry.target)
      run(entry.target)
    })
  }, { threshold: 0.6 })
  elements.forEach((el) => observer.observe(el))
}

/** Traço que desliza até o item da navegação sob o cursor e
 *  volta para a seção atual ao sair. */
function setupNavGlide() {
  const nav = document.querySelector('header nav[aria-label="Navegação principal"]')
  if (!nav) return
  const links = [...nav.querySelectorAll('a[href]')]
  if (!links.length) return

  nav.style.position = 'relative'
  const pill = document.createElement('span')
  pill.className = 'nav-glide'
  pill.setAttribute('aria-hidden', 'true')
  nav.appendChild(pill)

  const path = window.location.pathname
  const current = links.find((link) => {
    const target = link.getAttribute('href') || ''
    return target.length > 1 && target.startsWith('/') && path.startsWith(target)
  }) || null

  const moveTo = (el, animate) => {
    if (!el) {
      pill.style.opacity = '0'
      return
    }
    const navBox = nav.getBoundingClientRect()
    const box = el.getBoundingClientRect()
    if (!box.width) return
    pill.style.transition = animate && !prefersReducedMotion()
      ? 'transform 320ms var(--ds-motion-glide), width 320ms var(--ds-motion-glide), opacity 160ms ease'
      : 'none'
    pill.style.width = `${box.width}px`
    pill.style.transform = `translateX(${box.left - navBox.left}px)`
    pill.style.opacity = '1'
  }

  moveTo(current, false)
  links.forEach((link) => {
    link.addEventListener('mouseenter', () => moveTo(link, true))
    link.addEventListener('focus', () => moveTo(link, true))
  })
  nav.addEventListener('mouseleave', () => moveTo(current, true))
  window.addEventListener('resize', () => moveTo(current, false))
}

/** Resposta tátil no clique das ações que geram negócio.
 *  Marca por função (WhatsApp, orçamento, envio, CTA rastreada) porque as
 *  páginas geradas usam classes utilitárias, sem um seletor comum de botão. */
function setupPressFeedback() {
  const seletores = [
    '.btn',
    '.footer-cta',
    '[data-track]',
    'button[type="submit"]',
    'a[href^="https://wa.me/"]',
    'a[href*="#captacao-lead"]',
    'a[href*="#consorcio-lead"]'
  ].join(',')
  document.querySelectorAll(seletores).forEach((el) => el.classList.add('press-target'))
}

setupPressFeedback()
setupCountUp()
setupNavGlide()
initThemeToggle()
