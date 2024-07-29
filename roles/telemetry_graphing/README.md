Telemetry_graphing
=========

Verify that openstack dashboards exist in the openshift-console URL in RHOSO18 env.

Requirements
------------
1- Valid OSP18 env
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


