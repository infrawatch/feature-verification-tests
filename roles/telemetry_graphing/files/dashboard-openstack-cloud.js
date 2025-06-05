describe('OpenShift Console Login', () => {

  it('should successfully login to OpenShift console', () => {
    const openshiftUrl = Cypress.env('OPENSHIFT_URL') || 'https://console-openshift-console.apps-crc.testing';
    const username = Cypress.env('OPENSHIFT_USERNAME') || 'kubeadmin';
    const password = Cypress.env('OPENSHIFT_PASSWORD') || '12345678';
    const provider = 'kube:admin';

    // Visit the OpenShift console
    cy.visit(openshiftUrl);


    cy.task('log', `  Logging in as ${username}`);
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
  });
});