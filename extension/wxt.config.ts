import { defineConfig } from 'wxt';

const apiBaseUrl =
  process.env.WXT_PUBLIC_STARSCOUT_API_BASE_URL ?? 'https://starscout-extension-api.arthurnun.es';
const apiHostPermission = apiBaseUrl ? `${new URL(apiBaseUrl).origin}/*` : null;

// See https://wxt.dev/api/config.html
export default defineConfig({
  modules: ['@wxt-dev/module-react'],
  manifest: {
    name: 'StarScout - See Suspected Non-Legit Stars on GitHub repos',
    description: 'Shows suspected non-legit stars on public GitHub repository pages.',
    action: {
      default_title: 'StarScout - See Suspected Non-Legit Stars on GitHub repos',
    },
    permissions: [],
    host_permissions: [
      'https://github.com/*',
      ...(apiHostPermission ? [apiHostPermission] : []),
    ],
  },
});
