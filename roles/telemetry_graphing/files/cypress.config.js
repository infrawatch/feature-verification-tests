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
    video: true,
    viewportWidth: 1280,
    viewportHeight: 720,
    retries: {
      runMode: 2,      // Retry 2 times when running in CI
      openMode: 0      // Don't retry in interactive mode
    },
    video: true,
    screenshotOnRunFailure: true,

  },
})
