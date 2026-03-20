import { existsSync, readFileSync } from 'node:fs'
import { join } from 'node:path'

const root = process.cwd()
const requiredPaths = [
  'dist/index.html',
  'dist/mobile/index.html',
  'dist/produtos/index.html',
  'dist/produtos/retroescavadeiras/index.html',
  'dist/produtos/retroescavadeiras/580n/index.html',
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
  'dist/mobile/index.html',
  'dist/produtos/index.html',
  'dist/produtos/retroescavadeiras/index.html',
  'dist/produtos/retroescavadeiras/580n/index.html',
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

console.log('verify-dist: representative packaged routes and built assets are present')
