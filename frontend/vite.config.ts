import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/today': {
        target: 'http://127.0.0.1', 
        changeOrigin: true,
        headers: {
          Host: 'weather.local' 
        }
      },
      '/predict': {
        target: 'http://127.0.0.1',
        changeOrigin: true,
        headers: {
          Host: 'weather.local'
        }
      }
    }
  }
})