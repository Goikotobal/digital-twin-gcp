import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// ✅ Use the correct bucket path as the base
export default defineConfig({
  base: '/tuin-dev-frontend-119759378611/', // ← update this
  plugins: [react()],
})
