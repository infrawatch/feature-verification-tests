common
=========

The tests in this role are not specific to any one functional area but are an aggregate of common tests that can be used in all OSP 18.0/OCP jobs.

Requirements
------------

None

Role Variables
--------------
Variable required for all tasks to run:

  For pod_tests.yml tasks:

    pod_test_id
    pod_list
      - list of pods to validate
    pod_status_str 
      - status of pods to check
    pod_nspace
      - list of projects where pods exist


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
        name: common


License
-------

Apache 2

Author Information
------------------

alexy@redhat.com
