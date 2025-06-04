describe('OpenShift Console Login', () => {

  it('should successfully login to OpenShift console', () => {
    const openshiftUrl = Cypress.env('OPENSHIFT_URL') || 'https://console-openshift-console.apps-crc.testing';
    const username = Cypress.env('OPENSHIFT_USERNAME') || 'developer';
    const password = Cypress.env('OPENSHIFT_PASSWORD') || 'developer';

    // Visit the OpenShift console
    cy.visit(openshiftUrl);

    // Wait for the login page to load
    cy.url().should('include', 'oauth');

    // Look for common OpenShift login elements
    // This handles the OAuth provider selection page if present
    cy.get('body').then(($body) => {
      if ($body.find('a[href*="htpasswd"]').length > 0) {
        // If htpasswd provider is available, click it
        cy.get('a[href*="htpasswd"]').click();
      } else if ($body.find('a').filter(':contains("htpasswd")').length > 0) {
        // Alternative selector for htpasswd
        cy.contains('a', 'htpasswd').click();
      }
    });

    cy.get('input[id="inputUsername"]').invoke('val', username).trigger('input');
    cy.get('input[id="inputPassword"]').invoke('val', password).trigger('input');

    // Submit the login form
    cy.get('button[type="submit"]').click();

    // Wait for successful login and redirect to console
    cy.url({ timeout: 15000 }).should('include', 'console-openshift-console');
    cy.screenshot("login");
  });
});