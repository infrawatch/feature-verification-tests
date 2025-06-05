describe('OpenShift Console Login', () => {

  it('should successfully login to OpenShift console', () => {
    const openshiftUrl = Cypress.env('OPENSHIFT_URL') || 'https://console-openshift-console.apps-crc.testing';
    const username = Cypress.env('OPENSHIFT_USERNAME') || 'kubeadmin';
    const password = Cypress.env('OPENSHIFT_PASSWORD') || '12345678';
    const provider = 'kube:admin';
    const dashboards = [
      { url: '/grafana-dashboard-openstack-cloud', screenshot: 'openstack-cluster' },
      { url: '/grafana-dashboard-openstack-rabbitmq', screenshot: 'openstack-rabbitmq' },
      { url: '/grafana-dashboard-openstack-node', screenshot: 'openstack-node' },
      { url: '/grafana-dashboard-openstack-vm', screenshot: 'openstack-vms' },
      { url: '/grafana-dashboard-openstack-network-traffic', screenshot: 'openstack-network-traffic'},
      //{ url: '/grafana-dashboard-openstack-kepler', screenshot: 'openstack-kepler'},
      //{ url: '/grafana-dashboard-openstack-ceilometer-ipmi', screenshot: 'openstack-ceilometer-ipmi' }
    ];

    // Visit the OpenShift console
    cy.visit(openshiftUrl);

    cy.get('[data-test-id="login"]').should('be.visible');
    cy.get('body').then(($body) => {
      if ($body.text().includes(provider)) {
        cy.contains(provider).should('be.visible').click();
      }
    });
    cy.get('#inputUsername').type(username);
    cy.get('#inputPassword').type(password);
    cy.get('button[type=submit]').click();


    // Wait for successful login and redirect to console
    cy.url({ timeout: 15000 }).should('include', 'console-openshift-console');
    cy.screenshot("login");

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