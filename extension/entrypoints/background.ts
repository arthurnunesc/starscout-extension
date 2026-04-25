export default defineBackground(() => {
  console.info('StarScout extension background loaded', { id: browser.runtime.id });
});
