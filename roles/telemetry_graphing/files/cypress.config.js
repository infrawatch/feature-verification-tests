const { defineConfig } = require('cypress')
module.exports = defineConfig({
  e2e: {
    baseUrl: 'https://console-openshift-console.apps-crc.testing',
    specPattern: 'cypress/integration/**/*.{js,jsx,ts,tsx}',
    supportFile: false,
    chromeWebSecurity: false,
    experimentalSessionAndOrigin: true,
    defaultCommandTimeout: 10000,
    pageLoadTimeout: 30000,
  },
})
