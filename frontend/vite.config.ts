import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Vite config file
// - This is used only during development (dev server / build tooling).
// - Production deployment should not rely on this proxy; instead point your app to the real API host or use environment variables.
export default defineConfig({
  // Vite plugins. @vitejs/plugin-react adds fast refresh, JSX support, etc.
  plugins: [react()],

  // Dev server options
  server: {
    // Port to run the Vite dev server on
    port: 3000,

    // Proxy allows frontend dev server to forward requests to your backend (avoids CORS during development)
    proxy: {
      // Any request starting with /api will be proxied to http://localhost:8888
      '/api': {
        target: 'http://localhost:8888', // backend dev server
        changeOrigin: true,               // set Host header to target URL
      }
    }
  }
})
