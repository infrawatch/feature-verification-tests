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

The following tools are also needed:
* grep
* awk

Role Variables
--------------
Variable required for all tasks to run

For pod_tests.yml tasks:

    common_pod_test_id
      - polarion ID number for each test.
    common_pod_list
      - list of pods to validate
    common_pod_status_str
      - status of pods to check
    common_pod_nspace
      - list of projects where pods exist

For check\_openstack\_services\_rhoso.yml tasks:

    common\_verify\_resources\_are\_ready
      - List of dicts of resources to check if they're ready
        Each dict should include the following keys: kind, name, condition\_type
        Example:
           kind: metricstorage
           name: metric-storage
           condition_type: Ready

For crd_tests.yml tasks:

    common_crd_test_id
      - polarion ID number for each test.
    common_crd_list
      - list of crd to validate

For endpoint_tests.yml tasks:

    common_endpoint_test_id
      - polarion ID number for each test.
    common_endpoint_list
      - list of endpoints to validate

For project_tests.yml tasks:

    common_project_test_id
      - polarion ID number for each test
    common_project_list
      - list of projects to validate


For manifest_tests.yml tasks:

     manifest_test_id
       - polarion ID number for each test
     manifest_list
       - list of package manifests to validate

For cr\_tests.yml tasks:

    common\_cr\_test\_id is defined
       - polarion ID number for each test
    common\_cr\_list is defined
       - list of CRs to check for existence



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
    tasks:
      - name: "Verify Running Pods"
        ansible.builtin.import_role:
          name: common
        vars:
            common_pod_test_id: "RHOSO-12752"
            common_pod_status_str: "Running"
            common_pod_nspace: openstack
            common_pod_list:
              - openstackclient

      - name: "Verify status of multiple containers"
        ansible.builtin.include_role:
          name: common
        vars:
            common_container_test_id: "RHOSO-12753"
            common_container_list:
                - ceilometer_agent_compute
                - ceilometer_agent_ipmi
                - node_exporter

      - name: "Verify Endpoint"
        ansible.builtin.import_role:
          name: common
        vars:
          common_endpoint_test_id: "RHOSO-12682"
          common_endpoint_list:
            - [nova,compute,public]
            - [nova,compute,internal]
            - [placement,placement,public]

      - name: "Verify projects"
        ansible.builtin.import_role:
          name: common
        vars:
          common_project_test_id: "RHOSO-12668"
          common_project_list:
            - openshift-openstack-infra
            - openshift

      - name: "Verify crd"
        ansible.builtin.import_role:
          name: common
        vars:
          common_crd_test_id : "crd_test_id"
          common_crd_list:
            - list of crd to validate


License
-------

Apache 2

Author Information
------------------

alexy@redhat.com
