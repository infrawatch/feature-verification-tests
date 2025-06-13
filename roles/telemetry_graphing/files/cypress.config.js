const { defineConfig } = require('cypress')
module.exports = defineConfig({
  e2e: {
    baseUrl: 'https://console-openshift-console.apps-crc.testing/login',
    specPattern: 'cypress/integration/**/*.{js,jsx,ts,tsx}',
    supportFile: false,
    defaultCommandTimeout: 10000,
    pageLoadTimeout: 30000,
    video: true,
    retries: {
      runMode: 2,      // Retry 2 times when running in CI
      openMode: 0      // Don't retry in interactive mode
    },
    screenshotOnRunFailure: true,
  },
})