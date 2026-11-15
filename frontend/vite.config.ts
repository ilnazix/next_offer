import react from '@vitejs/plugin-react'
import { loadEnv } from 'vite'
import { defineConfig } from 'vitest/config'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, '.', '')

  return {
    // GitHub Pages serves project sites from /<repo>/, so the build passes
    // VITE_BASE_PATH=/next_offer/ in CI. Local dev/build defaults to /.
    base: env.VITE_BASE_PATH || '/',
    plugins: [react()],
    server: {
      port: 5173,
    },
    test: {
      environment: 'jsdom',
      setupFiles: './tests/setup.ts',
    },
  }
})
