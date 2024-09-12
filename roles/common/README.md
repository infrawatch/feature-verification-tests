common
======

The tests in this role are not specific to any one functional area but are an
aggregate of common tests that can be used in all OSP 18.0/OCP jobs.

The available tasks tests are:

* pod tests

Requirements
------------

The requirements vary according to the tests run.

For the pod tests, access to a kubernetes cluster and the oc command is needed,
this is done by passing the KUBECONFIG env var and PATH into the play.

Role Variables
--------------
Variable required for all tasks to run

For pod_tests.yml tasks:

    common_pod_test_id
    common_pod_list
      - list of pods to validate
    common_pod_status_str
      - status of pods to check
    common_pod_nspace
      - list of projects where pods exist


Dependencies
------------

None

Example Playbook
----------------

The tasks run in this role are dependant on the vars that are configured
As such, the role can be called multiple times within the same play, with the
tests being configured at the task level (e.g. with import_role) or the vars
can be set at the play level.

  - hosts: controller
    gather_facts: no
    ignore_errors: true
    environment:
      KUBECONFIG: "{{ cifmw_openshift_kubeconfig }}"
      PATH: "{{ cifmw_path }}"
    vars:
      common_pod_test_id: "RHOSO-12752"
      common_pod_status_str: "Running"
      common_pod_nspace: openstack
      common_pod_list:
        - openstackclient
    tasks:
      - name: "Verify Running Pods"
        ansible.builtin.import_role:
          name: common


License
-------

Apache 2

Author Information
------------------

alexy@redhat.com
