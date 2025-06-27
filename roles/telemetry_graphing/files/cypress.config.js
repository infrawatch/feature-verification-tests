const { defineConfig } = require('cypress')
module.exports = defineConfig({
  e2e: {
    baseUrl: 'https://console-openshift-console.apps-crc.testing/login',
    specPattern: 'cypress/integration/**/*.{js,jsx,ts,tsx}',
    supportFile: false,
    chromeWebSecurity: false,
    defaultCommandTimeout: 10000,
    pageLoadTimeout: 30000,
    viewportWidth: 1280,
    viewportHeight: 720,
    video: true,
  },
})