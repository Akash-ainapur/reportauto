import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    react(),
  ],
  server: {
    // The form reads backend/data/departments_context.json, one folder above the frontend
    fs: { allow: ['..'] },
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:5000', // Reverted to Local Backend
        changeOrigin: true,
        secure: false,
      }
    }
  }
})
