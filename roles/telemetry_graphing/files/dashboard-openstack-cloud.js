describe('OpenShift Console Dashboard Test', () => {
  const username = 'kubeadmin';
  const password = '12345678';



  before(() => {

    Cypress.Commands.add('loginWithRequest', () => {
      cy.request({
        method: 'POST',
        url: 'https://oauth-openshift.apps-crc.testing/oauth/token', // or authorize, depending on your setup
        form: true,
        body: {
          grant_type: 'password',
          username: 'kubeadmin',
          password: '12345678',
          client_id: 'openshift-challenging-client', // standard OpenShift client
        },
      }).then((response) => {
        expect(response.status).to.eq(200);
        const accessToken = response.body.access_token;
        cy.setCookie('access_token', accessToken); // depends if Console uses cookie or localStorage
      });
    });
    cy.visit('https://console-openshift-console.apps-crc.testing/login');

    cy.get('input[id="inputUsername"]').invoke('val', username).trigger('input');
    cy.get('input[id="inputPassword"]').invoke('val', password).trigger('input');
    cy.get('button[type="submit"]').click();

    cy.wait(5000);

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