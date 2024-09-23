Telemetry_graphing
=========

Verify that openstack dashboards exist in the openshift-console URL in RHOSO18 env.
By deploy Cypress and add the tests inside telemetry_graphing/files/*Cypress to confirm the dashboards exists.

Requirements
------------
1- Valid RHOSO-18 env
2- "EnableDashboard:true" in the controlplane



Example Playbook
----------------
No need for any extra steps or vars.

    - hosts: servers
      tasks:
      ansible.builtin.import_role:
        name: telemetry_graphing

License
-------

Apache 2


