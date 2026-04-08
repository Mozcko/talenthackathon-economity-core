import { defineConfig } from 'astro/config';
import react from '@astrojs/react';
import tailwind from '@tailwindcss/vite';
import node from "@astrojs/node";
import clerk from '@clerk/astro'
import { loadEnv } from 'vite';

const env = loadEnv(process.env.NODE_ENV || 'development', process.cwd(), '');

// https://astro.build/config
export default defineConfig({
  integrations: [react(), clerk()],
  vite: {
    plugins: [tailwind()],
  },
  adapter: node({ mode: 'standalone' }),
  output: 'server',
  server: {
    proxy: {
      '/api': {
        target: env.PUBLIC_API_URL,
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
    },
  },
});