import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Backend address for the /api proxy. Override when port 8000 is taken (e.g. by Docker): SEWA_API_PORT=8010 npm run dev
const api = `http://127.0.0.1:${process.env.SEWA_API_PORT ?? '8000'}`

export default defineConfig({
  plugins: [react()],
  build: { rolldownOptions: { output: { codeSplitting: { groups: [
    { name: 'react-vendor', test: /node_modules\/(?:react|react-dom|scheduler)\//, minSize: 0 },
    { name: 'three-core', test: /node_modules\/three\//, minSize: 0 },
    { name: 'three-fiber', test: /node_modules\/(?:@react-three\/fiber|react-reconciler)\//, minSize: 0 },
  ] } } } },
  server: { port: 5173, proxy: { '/api': api } },
  preview: { port: 4173, proxy: { '/api': api } },
})
