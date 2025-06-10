describe('OpenShift Console Login', () => {

  it('should successfully login to OpenShift console', () => {;
    const username = Cypress.env('OPENSHIFT_USERNAME') || 'kubeadmin';
    const password = Cypress.env('OPENSHIFT_PASSWORD') || '12345678';
    const provider = 'kube:admin';

    // Visit the OpenShift console
    cy.visit(Cypress.config('baseUrl'));

    cy.url().should('include', 'oauth-openshift.apps-crc.testing');

    cy.origin(
      'oauth-openshift.apps-crc.testing',
      { args: { provider, username, password } },
      // eslint-disable-next-line @typescript-eslint/no-shadow
      ({ provider, username, password }) => {
        cy.get('[data-test-id="login"]').should('be.visible');
        cy.get('body').then(($body) => {
          if ($body.text().includes(provider)) {
            cy.contains(provider).should('be.visible').click();
          }
        });
        cy.wait(5000);
        cy.get('#inputUsername').type(username);
        cy.wait(5000);
        cy.get('#inputPassword').type(password);
        cy.wait(5000);
        cy.get('button[type=submit]').click();
      },
    );


    cy.visit(Cypress.config('baseUrl'));
    // Wait for successful login and redirect to console

    cy.screenshot("login");

  });
});