import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

// VITE_API_URL is injected as a build arg in Docker (see Dockerfile.dev).
// Locally it falls back to http://localhost:8000.
// All /api/* requests are proxied — the frontend never hardcodes a hostname.
const API_TARGET = process.env.VITE_API_URL || 'http://localhost:8000';

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    host: '0.0.0.0',
    port: 3000,
    proxy: {
      '/api': {
        target: API_TARGET,
        changeOrigin: true,
        secure: false,
      },
    },
  },
  preview: {
    host: '0.0.0.0',
    port: 3000,
    proxy: {
      '/api': {
        target: API_TARGET,
        changeOrigin: true,
        secure: false,
      },
    },
  },
});
