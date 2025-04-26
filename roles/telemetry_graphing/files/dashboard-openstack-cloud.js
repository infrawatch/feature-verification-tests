describe('OpenShift Console Dashboard Test', () => {
  const username = 'developer';
  const password = 'developer';


  before(() => {
    
    cy.session([username, password], () => {
      cy.visit('https://oauth-openshift.apps-crc.testing/login');

      cy.origin(
        'https://oauth-openshift.apps-crc.testing',
        { args: { username, password } },
        ({ username, password }) => {
          cy.get('input#inputUsername').type(username);
          cy.get('input#inputPassword').type(password);
          cy.get('button[type="submit"]').click();
        }
      );
    });

    cy.wait(5000);
    // Ensure redirected back to the main console

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