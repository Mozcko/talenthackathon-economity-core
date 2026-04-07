import { defineConfig } from 'astro/config';
import react from '@astrojs/react';
import tailwind from '@tailwindcss/vite';
import node from "@astrojs/node";

// https://astro.build/config
export default defineConfig({
  integrations: [react()],
  vite: {
    plugins: [tailwind()],
  },
  adapter: node({
    mode: "standalone"
  }),
  server: {
    proxy: {
      '/api': {
        target: 'https://talenthackathon-economity-backend-production.up.railway.app',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
    },
  },
  // Opcional: si usas 'hybrid' o 'server' para el admin en el futuro
  output: 'server', 
});