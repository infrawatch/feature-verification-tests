qe_common
=========

The tests in this role are not specific to any one functional area but are an aggregate of common tests that can be used in all OSP 18.0/OCP jobs.

Requirements
------------

None

Role Variables
--------------
Variable required for all tasks to run:

  For container_tests.yml tasks:

    container_polar_id
    container_list
      - list of containers to validate

  For cred_tests.yml tasks:

    cred_polar_id
    cred_list   
      - list of credentials to validate

  For endpoint_tests.yml tasks:
    
    endpoint_polar_id
    endpoint_list   
      - list of endpoints to validate

  For file_tests.yml tasks:
    
    file_polar_id
    file_list
      - list of files to verify

  For node_tests.yml tasks:

    node_polar_id
    node_list  
      - list of nodes to validate

  For proj_test.yml tasks:

    proj_polar_id
    proj_list   
      - list of projects to validate

  For pod_tests.yml tasks:

    pod_polar_id
    pod_list
      - list of pods to validate
    pod_status_str 
      - status of pods to check
    pod_nspace
      - list of projects where pods exist

   For service_tests.yml tasks:

     service_polar_id
     service_list  
       - list of services to validate
     service_nspace
       - project where services are running
    
  For manifest_tests.yml tasks:

     manifest_polar_id
     manifest_list  
       - list of package manifests to validate

  For subscription_tests.yml tasks: 

     subscription_polar_id
     subscription_list  
       - list of subscriptions to validate
     subscription_nspace
       - project where the subscription lives


Dependencies
------------

None

Example Playbook
----------------

Typically, for this role the tests should *not* use a "main.yml" and import or include all the tests in the role. On the contrary, a tests should explicitly include specific tests needed for a given job.


  hosts: controller
  gather_facts: no
  vars:
     proj_out_file: verify_logging_projects_exist_lresults.log
     proj_list:
       - openshift-openstack-infra
       - openshift
       - openstack-operators
       - openshift-logging

  tasks:
    - name: Run projects tests
      ansible.builtin.import_role:
        name: qe_common


License
-------

Apache 2

Author Information
------------------

alexy@redhat.com
