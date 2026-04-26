import { defineConfig } from 'wxt';

// See https://wxt.dev/api/config.html
export default defineConfig({
  modules: ['@wxt-dev/module-react'],
  manifest: {
    name: 'StarScout Star Integrity',
    description: 'Shows heuristic suspected non-legit star signals on public GitHub repository pages.',
    permissions: [],
    host_permissions: ['https://github.com/*', 'http://127.0.0.1:8000/*', 'http://localhost:8000/*'],
  },
});
