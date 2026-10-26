import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/server-options.html#server-proxy
export default defineConfig({
  plugins: [react()],
  server: {
    host: '127.0.0.1',
    port: 5173,
    strictPort: true,
    proxy: {
      '/api': 'http://127.0.0.1:8000',
    },
  },
})
