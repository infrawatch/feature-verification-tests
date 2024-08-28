telemetry_autoscaling
=========

Test that expected metrics appear in Prometheus

Requirements
------------
OpenStack deployed with the following enabled:
- telemetry
- metricstorage
- ceilometer
- rabbitmq

Tests:
------
- Verify OpenStack is deployed correctly
* Verify telemetry is ready
* Verify metricstorage is ready
* Verify ceilometer is ready
* Verify rabbitmq is ready
- Verify RabbitMQ metrics are being exposed and stored
* Check the rabbitmq metrics endpoint
* Use openstack observabilityclient to verify RabbitMQ metrics are stored in Prometheus

Role Variables
--------------

A description of the settable variables for this role should go here, including any variables that are in defaults/main.yml, vars/main.yml, and any variables that can/should be set via parameters to the role. Any variables that are read from other roles and/or the global scope (ie. hostvars, group vars, etc.) should be mentioned here as well.

Dependencies
------------

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

An optional section for the role authors to include contact information, or a website (HTML is not allowed).
