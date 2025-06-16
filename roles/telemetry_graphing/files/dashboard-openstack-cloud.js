describe('OpenShift Console Dashboard Test', () => {
  const username = 'kubeadmin';
  const password = '123456789';

  beforeEach(() => {
    cy.session('login', () => {
      cy.visit('https://console-openshift-console.apps-crc.testing/login');
      cy.origin(
        'https://oauth-openshift.apps-crc.testing',
        { args: { username, password } },
        ({ username, password }) => {
          cy.get('input[id="inputUsername"]').invoke('val', username).trigger('input');
          cy.get('input[id="inputPassword"]').invoke('val', password).trigger('input');
          cy.get('button[type="submit"]').click();
        }
      );
      cy.url().should('include', 'console-openshift-console');
    });
  });

  it('should load and validate the OpenStack dashboards', () => {

    cy.visit(`https://console-openshift-console.apps-crc.testing/monitoring/dashboards/grafana-dashboard-openstack-cloud`);
    cy.get('div[data-test-id="dashboard"]', { timeout: 20000 }).should('exist');
    cy.wait(1000);
    cy.screenshot("openshift-dashboard");
    
    const dashboards = [
      { url: '/grafana-dashboard-openstack-cloud', screenshot: 'openstack-cluster' },
      { url: '/grafana-dashboard-openstack-rabbitmq', screenshot: 'openstack-rabbitmq' },
      { url: '/grafana-dashboard-openstack-node', screenshot: 'openstack-node' },
      { url: '/grafana-dashboard-openstack-vm', screenshot: 'openstack-vms' },
      { url: '/grafana-dashboard-openstack-network-traffic', screenshot: 'openstack-network-traffic'}
    ];

    dashboards.forEach(({ url, screenshot }) => {
      cy.visit(`https://console-openshift-console.apps-crc.testing/monitoring/dashboards${url}`);
      cy.get('div[data-test-id="dashboard"]', { timeout: 20000 }).should('exist');
      cy.wait(1000);
      cy.screenshot(screenshot);
    });
  });
});
