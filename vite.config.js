import { readdirSync } from 'node:fs'
import { defineConfig } from 'vite'
import tailwindcss from '@tailwindcss/vite'
import { relative, resolve } from 'node:path'

function collectHtmlEntries(dir) {
  const absoluteDir = resolve(__dirname, dir)
  const entries = {}

  function walk(currentDir) {
    for (const entry of readdirSync(currentDir, { withFileTypes: true })) {
      const absolutePath = resolve(currentDir, entry.name)

      if (entry.isDirectory()) {
        walk(absolutePath)
        continue
      }

      if (!entry.isFile() || !entry.name.endsWith('.html')) {
        continue
      }

      const relativePath = relative(__dirname, absolutePath).replaceAll('\\', '/')
      const key = relativePath.replace(/\.html$/, '')
      entries[key] = absolutePath
    }
  }

  walk(absoluteDir)

  return entries
}

export default defineConfig({
  plugins: [
    tailwindcss(),
  ],
  build: {
    rollupOptions: {
      input: {
        index: resolve(__dirname, 'index.html'),
        mobile: resolve(__dirname, 'mobile/index.html'),
        ...collectHtmlEntries('produtos')
      }
    }
  }
})
