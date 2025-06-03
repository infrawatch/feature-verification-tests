describe('OpenShift Console Dashboard Test', () => {
  const username = 'kubeadmin';
  const password = '12345678';



  before(() => {


      // Configure Cypress for cross-origin handling
      Cypress.config('chromeWebSecurity', false);

      // Visit the console login page
      cy.visit('https://console-openshift-console.apps-crc.testing/login');

      // Wait for redirect to OAuth page
      cy.url({ timeout: 15000 }).should('include', 'oauth-openshift.apps-crc.testing');

      // Handle OAuth login using cy.origin for Cypress 14.4.0
      cy.origin('https://oauth-openshift.apps-crc.testing', { args: { username, password } }, ({ username, password }) => {
        // Wait for the login form to load
        cy.get('.pf-c-login__main', { timeout: 15000 }).should('be.visible');
        cy.screenshot("before-login");
        // Fill username field (clear first as it may be pre-filled)
        cy.get('input[type="text"]')
          .should('be.visible')
          .clear()
          .type(username);

        // Fill password field
        cy.get('input[type="password"]')
          .should('be.visible')
          .type(password);

        // Click login button
        cy.contains('button', 'Log in')
          .should('be.visible')
          .click();
      });

      // Wait for successful redirect back to console
      cy.url({ timeout: 30000 }).should('include', 'console-openshift-console.apps-crc.testing');

      // Wait for console page to load
      cy.get('body', { timeout: 15000 }).should('be.visible');
      cy.screenshot("after-login");
      // Handle "Skip tour" modal if it appears
      cy.get('body').then(($body) => {
        if ($body.find('button:contains("Skip tour")').length > 0) {
          cy.contains('button', 'Skip tour').click();
          cy.wait(2000);
        }
      });
    


  });

  it('should load and validate the OpenStack dashboards', () => {
    // List of dashboards to check
    const dashboards = [
      { url: '/grafana-dashboard-openstack-cloud', screenshot: 'openstack-cluster' },
      { url: '/grafana-dashboard-openstack-rabbitmq', screenshot: 'openstack-rabbitmq' },
      { url: '/grafana-dashboard-openstack-node', screenshot: 'openstack-node' },
      { url: '/grafana-dashboard-openstack-vm', screenshot: 'openstack-vms' },
      { url: '/grafana-dashboard-openstack-network-traffic', screenshot: 'openstack-network-traffic'},
      //{ url: '/grafana-dashboard-openstack-kepler', screenshot: 'openstack-kepler'},
      //{ url: '/grafana-dashboard-openstack-ceilometer-ipmi', screenshot: 'openstack-ceilometer-ipmi' }
    ];
    


    // Iterate through each dashboard
    dashboards.forEach(dashboard => {
      cy.visit(`https://console-openshift-console.apps-crc.testing/monitoring/dashboards${dashboard.url}`);

      // Wait for the dashboard to load and take a screenshot
      cy.get('div[data-test-id="dashboard"]', { timeout: 100000 })
        .find('[data-test-id^="panel-"]')

      cy.wait(5000); 
      cy.screenshot(dashboard.screenshot);
    });
  });
});