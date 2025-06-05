describe('OpenShift Console Login', () => {

  it('should successfully login to OpenShift console', () => {
    const openshiftUrl = Cypress.env('OPENSHIFT_URL') || 'https://console-openshift-console.apps-crc.testing';
    const username = Cypress.env('OPENSHIFT_USERNAME') || 'kubeadmin';
    const password = Cypress.env('OPENSHIFT_PASSWORD') || '12345678';

    // Visit the OpenShift console
    cy.visit(openshiftUrl);

    // Wait for the login page to load
    cy.url().should('include', 'oauth');

    cy.get('input[id="inputUsername"]').invoke('val', username).trigger('input');
    cy.get('input[id="inputPassword"]').invoke('val', password).trigger('input');
    cy.get('input[id="inputUsername"]').should('be.visible').type(username, { delay: 50 , force: true });
    cy.get('input[id="inputPassword"]').should('be.visible').type(password, { delay: 50, force: true });

    cy.get('#inputUsername').then($input => {
      const input = $input[0];
      input.value = username;
      input.dispatchEvent(new Event('input', { bubbles: true }));
      input.dispatchEvent(new Event('change', { bubbles: true }));
    });

    // Submit the login form
    cy.get('button[type="submit"]').click();

    // Wait for successful login and redirect to console
    cy.url({ timeout: 15000 }).should('include', 'console-openshift-console');
    cy.screenshot("login");
  });
});