telemetry_autoscaling
=========

Test autoscaling in OpenStack using heat and aodh

Requirements
------------
The following resources are required in the OpenStack cloud
* network called public
* network called private
* security group called basic with ssh and tcp enabled to the VMs
* a flavor called m1.small
* an image called cirros

Tests:
------
Verify overcloud deployment for autoscaling
    Test service API endpoints
    Verify all the services are running on overcloud
    Verify time-series database service is available
Using the heat service for autoscaling
    Create an archive policy
    Configure heat template for automatically scaling instances
    Create the deployment template for heat to control instance scaling
Create stack deployment for autoscaling
    Verify that the stack and resources are created
    Verify that the alarms were created for the stack
    Verify the deployment and metric resources exist for the stack
Testing and troubleshooting autoscaling
    Verify that alarms are triggered with traffic
    Verify that Orchestration service has scaled the instances

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
