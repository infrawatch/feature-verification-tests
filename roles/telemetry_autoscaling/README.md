telemetry_autoscaling
=========

Test autoscaling in OpenStack using heat and aodh

Requirements
------------
The following resources are required in the OpenStack cloud
* network called public
* network called provate
* security group called basic with ssh and tcp enabled to the VMs
* a flavor called m1.small
* an image called cirros

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
