import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  build: { rolldownOptions: { output: { codeSplitting: { groups: [
    { name: 'react-vendor', test: /node_modules\/(?:react|react-dom|scheduler)\//, minSize: 0 },
    { name: 'three-core', test: /node_modules\/three\//, minSize: 0 },
    { name: 'three-fiber', test: /node_modules\/(?:@react-three\/fiber|react-reconciler)\//, minSize: 0 },
  ] } } } },
  server: { port: 5173, proxy: { '/api': 'http://127.0.0.1:8000' } },
  preview: { port: 4173, proxy: { '/api': 'http://127.0.0.1:8000' } },
})
