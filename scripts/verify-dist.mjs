import { existsSync, readdirSync, readFileSync } from 'node:fs'
import { join } from 'node:path'

const root = process.cwd()
const requiredPaths = [
  'dist/index.html',
  'dist/case/index.html',
  'dist/case/catalogo/index.html',
  'dist/case/retroescavadeiras/580n/index.html',
  'dist/dynapac/index.html',
  'dist/dynapac/compactacao/ca25d-rhino/index.html',
]

const missing = requiredPaths.filter((relativePath) => !existsSync(join(root, relativePath)))

if (missing.length > 0) {
  console.error('Missing packaged routes:')
  for (const relativePath of missing) {
    console.error(`- ${relativePath}`)
  }
  process.exit(1)
}

const representativeHtml = [
  'dist/index.html',
  'dist/case/index.html',
  'dist/case/catalogo/index.html',
  'dist/case/retroescavadeiras/580n/index.html',
  'dist/dynapac/index.html',
  'dist/dynapac/compactacao/ca25d-rhino/index.html',
]

for (const relativePath of representativeHtml) {
  const html = readFileSync(join(root, relativePath), 'utf8')

  if (html.includes('src="/main.js"') || html.includes('src="/mobile/main.js"')) {
    console.error(`Raw source runtime reference still present in ${relativePath}`)
    process.exit(1)
  }

  if (html.includes('href="/style.css"') || html.includes('href="/mobile/style.css"')) {
    console.error(`Raw source stylesheet reference still present in ${relativePath}`)
    process.exit(1)
  }

  if (!/\/assets\/.+\.js/.test(html)) {
    console.error(`Built JS asset reference missing in ${relativePath}`)
    process.exit(1)
  }

  if (!/\/assets\/.+\.css/.test(html)) {
    console.error(`Built CSS asset reference missing in ${relativePath}`)
    process.exit(1)
  }
}

// Mapa das filiais: todo link do Google Maps abre o perfil da filial (query_place_id),
// nunca uma coordenada solta (T116).
function htmlFiles(dir) {
  return readdirSync(dir, { withFileTypes: true }).flatMap((entry) => {
    const path = join(dir, entry.name)
    if (entry.isDirectory()) return htmlFiles(path)
    return entry.name.endsWith('.html') ? [path] : []
  })
}

let mapsLinks = 0
const badMapsLinks = []
for (const file of htmlFiles(join(root, 'dist'))) {
  const html = readFileSync(file, 'utf8')
  for (const [, url] of html.matchAll(/"(https:\/\/www\.google\.com\/maps[^"]*)"/g)) {
    mapsLinks += 1
    if (!/[?&](amp;)?query_place_id=ChIJ[\w-]+/.test(url) || /query=-?\d+(\.\d+)?,-?\d+/.test(url)) {
      badMapsLinks.push(`${file.slice(root.length + 1)}: ${url}`)
    }
  }
}

if (badMapsLinks.length > 0) {
  console.error('Google Maps links without the branch profile (query_place_id):')
  for (const line of badMapsLinks.slice(0, 20)) console.error(`- ${line}`)
  process.exit(1)
}

console.log(`verify-dist: representative packaged routes and built assets are present; ${mapsLinks} Google Maps links open the branch profile`)
