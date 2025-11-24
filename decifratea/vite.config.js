import { defineConfig } from 'vite';
import { resolve } from 'path';

export default defineConfig({
  root: resolve('./frontend/src'),
  base: '/static/',
  server: {
    host: 'localhost',
    port: 3000,
    open: false,
    watch: {
      usePolling: true,
      disableGlobbing: false,
    },
  },
  resolve: {
    extensions: ['.js', '.json'],
  },
  build: {
    outDir: resolve('./static/dist'),
    assetsDir: '',
    manifest: true,
    emptyOutDir: true,
    target: 'es2015',
    rollupOptions: {
      input: {
        main: resolve('./frontend/src/js/main.js'),
        styles: resolve('./frontend/src/css/main.css'),
      },
      output: {
        chunkFileNames: undefined,
      },
    },
  },
});
