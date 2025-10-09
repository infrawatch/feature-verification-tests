telemetry\_autoscaling
=========

Test autoscaling in OpenStack using heat and aodh as described in the Red Hat documentation.

Requirements
------------
The following resources are required in the OpenStack cloud
* network called public
* network called private
* security group called basic with ssh and tcp enabled to the VMs
* a flavor called m1.small
* an image called cirros

Role Variables
--------------
* `telemetry_autoscaling_cleanup` (default: `true`) - Controls whether the autoscaling stack
  cleanup task runs at the end of the role. Set to `false` to skip cleanup during the main role
  execution, allowing cleanup to be deferred to a later task (e.g., in a block's `always`
  section to ensure cleanup runs even on failure).

Tests:
------
* Verify overcloud deployment for autoscaling
  * Test service API endpoints
  * Verify all the services are running on overcloud
  * Verify time-series database service is available
* Using the heat service for autoscaling
  * Create an archive policy
  * Configure heat template for automatically scaling instances
  * Create the deployment template for heat to control instance scaling
* Create stack deployment for autoscaling
  * Verify that the stack and resources are created
  * Verify that the alarms were created for the stack
  * Verify the deployment and metric resources exist for the stack
* Testing and troubleshooting autoscaling
  * Verify that alarms are triggered with traffic
  * Verify that Orchestration service has scaled the instances

Example Playbook
----------------
[run\_autoscaling\_osp18.yml](https://github.com/infrawatch/feature-verification-tests/blob/master/ci/run_autoscaling_osp18.yml)

License
-------

Apache 2
