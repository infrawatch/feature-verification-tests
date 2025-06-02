describe('OpenShift Console Dashboard Test', () => {
  const username = 'kubeadmin';
  const password = '12345678';



  before(() => {

    cy.visit('https://console-openshift-console.apps-crc.testing/login');

    // Wait for redirect to OAuth page, then handle login there
    cy.url().should('include', 'oauth-openshift.apps-crc.testing');

    cy.screenshot('before-login');
    cy.origin(
      'https://oauth-openshift.apps-crc.testing',
      { args: { username, password } },
      ({ username, password }) => {

        // Debug: Log what we can see
        cy.get('body').then($body => {
          console.log('OAuth page loaded');
          console.log('Username input exists:', $body.find('input[name="username"]').length > 0);
          console.log('Password input exists:', $body.find('input[name="password"]').length > 0);
          console.log('Submit button exists:', $body.find('button[type="submit"]').length > 0);
        });

        cy.get('input[name="username"]', { timeout: 10000 }).should('be.visible');

        // Clear and type username (in case it's pre-filled)
        cy.get('input[name="username"]').clear().type(username);

        // Type password
        cy.get('input[name="password"]').type(password);

        // Click the Log in button
        cy.contains('button', 'Log in').click();
      }
    );

    cy.screenshot('after-login');

    cy.url().should('include', 'console-openshift-console.apps-crc.testing');

    cy.get('body').then($body => {
      if ($body.find('button:contains("Skip tour")').length > 0) {
        cy.contains('button', 'Skip tour').click(); // Only click if the button is found
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