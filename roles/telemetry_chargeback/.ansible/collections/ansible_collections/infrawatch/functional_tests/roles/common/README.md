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

    common_pod_list
      - list of pods to validate
    common_pod_status_str
      - status of pods to check
    common_pod_nspace
      - list of projects where pods exist


For subscription_tests.yml tasks:

    common_subscription_nspace
      - namespace
    common_subscription_list
      - list of subscription to validate

For crd_tests.yml tasks:

    common_crd_list
      - list of crd to validate

For endpoint_tests.yml tasks:

    common_endpoint_list
      - list of endpoints to validate
    openstack_cmd
      - The command used to run openstack

For project_tests.yml tasks:

    common_project_list
      - list of projects to validate

For service_tests.yml tasks:

    common_service_nspace
      - namespace
    common_service_list
      - list of services to validate

For file_tests.yml tasks:

    common_file_list
      - list of files to validate

For manifest_tests.yml tasks:

     manifest_list
       - list of package manifests to validate

For cr\_tests.yml tasks:

    common\_cr\_list is defined
       - list of CRs to check
        Each dict should include the following keys: kind, name
	A dict can optionally include a "condition\_type" key.
        Example:
           kind: metricstorage
           name: metric-storage
           condition\_type: Ready



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
          common_pod_status_str: "Running"
          common_pod_nspace: openstack
          common_pod_list:
            - openstackclient

      - name: "Verify subscription"
        ansible.builtin.import_role:
          name: common
        vars:
          common_subscription_nspace: openshift-operators-redhat
          common_subscription_l :
            - loki-operator

      - name: "Verify status of multiple containers"
        ansible.builtin.include_role:
          name: common
        vars:
            common_container_list:
                - ceilometer_agent_compute
                - ceilometer_agent_ipmi
                - node_exporter
                - kepler
                - openstack_network_exporter

      - name: "Verify Endpoint"
        ansible.builtin.import_role:
          name: common
        vars:
          common_endpoint_list:
            - [nova,compute,public]
            - [nova,compute,internal]
            - [placement,placement,public]

      - name: "Verify projects"
        ansible.builtin.import_role:
          name: common
        vars:
          common_project_list:
            - openshift-openstack-infra
            - openshift

      - name: "Verify services"
        ansible.builtin.import_role:
          name: common
        vars:
          common_service_nspace: openshift-logging
          common_service_list:
            - cluster-logging-operator-metrics
            - logging-loki-compactor-grpc
            - logging-loki-compactor-http
            - logging-loki-distributor-grpc
            - logging-loki-distributor-http
            - logging-loki-gateway-http
            - logging-loki-gossip-ring
            - logging-loki-index-gateway-grpc
            - logging-loki-index-gateway-http
            - logging-loki-ingester-grpc
            - logging-loki-ingester-http
            - logging-loki-querier-grpc
            - logging-loki-querier-http
            - logging-loki-query-frontend-grpc
            - logging-loki-query-frontend-http
            - logging-view-plugin
            - openstack-logging

      - name: "Verify files"
        ansible.builtin.import_role:
          name: common
        vars:
          common_file_list:
            - /etc/rsyslog.d/10-telemetry.conf

      - name: "Verify crd"
        ansible.builtin.import_role:
          name: common
        vars:
          common_crd_list:
            - list of crd to validate


License
-------

Apache 2

Author Information
------------------

alexy@redhat.com
