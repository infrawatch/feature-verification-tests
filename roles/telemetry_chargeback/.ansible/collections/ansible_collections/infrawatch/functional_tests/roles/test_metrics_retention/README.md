test_metrics_retention
======================

Tests for metrics retention  functionality deployed in STF.
This role test the metrics retention following the procedure set out in https://infrawatch.github.io/documentation/#metrics-retention-time-period_assembly-advanced-features

Requirements
------------

The ``oc`` client is required
See `https://docs.openshift.com/container-platform/latest/cli_reference/openshift_cli/getting-started-cli.html`_ for installation instructions.
``grep`` and ``wc`` are required.

Role Variables
--------------

..
  A description of the settable variables for this role should go here, including any variables that are in defaults/main.yml, vars/main.yml, and any variables that can/should be set via parameters to the role. Any variables that are read from other roles and/or the global scope (ie. hostvars, group vars, etc.) should be mentioned here as well.

Dependencies
------------

..
  A list of other roles hosted on Galaxy should go here, plus any details in regards to parameters that may need to be set for other roles, or variables that are used from other roles.

Example Playbook
----------------

Including an example of how to use your role (for instance, with variables passed in as parameters) is always nice for users too:

    - hosts: servers
      roles:
         - { role: username.rolename, x: 42 }

License
-------

Apache 2

Author Information
------------------

.. An optional section for the role authors to include contact information, or a website (HTML is not allowed).
