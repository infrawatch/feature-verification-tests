telemetry_verify_metrics
=========

Test that expected metrics appear in Prometheus

Requirements
------------
OpenStack deployed with the following enabled:
- telemetry
- metricstorage
- ceilometer
- rabbitmq

Tests:
------
- Verify OpenStack is deployed correctly
    - Verify telemetry is ready
    - Verify metricstorage is ready
    - Verify ceilometer is ready
    - Verify rabbitmq is ready
- Verify RabbitMQ metrics are being exposed and stored
    - Check the rabbitmq metrics endpoint
    - Use openstack observabilityclient to verify RabbitMQ metrics are stored in Prometheus
- Verify Ceilometer metrics are being exposed and stored
    - Use openstack observabilityclient to verify Ceilometer central metrics are stored in Prometheus
    - Use openstack observabilityclient to verify Ceilometer compute metrics are stored in Prometheus
    - Use openstack observabilityclient to verify Ceilometer ipmi metrics are stored in Prometheus
- Verify NodeExporter metrics are being exposed and stored
    - Use openstack observabilityclient to verify NodeExporter metrics are stored in Prometheus
- Verify Kepler metrics are being exposed and stored
    - Use openstack observabilityclient to verify Kepler metrics are stored in Prometheus

Role Variables
--------------
openstack\_cmd - command to access openstack cli. For example: "oc rsh openstackclient openstack"
telemetry\_verify\_metrics\_metric\_sources\_to\_test - List of sources to test. Current set of possible sources: ceilometer\_compute\_agent, ceilometer\_central\_agent, ceilometer\_ipmi_\_agent, node\_exporter, rabbitmq, kepler

Example Playbook
----------------
- name: Run telemetry tests to verify metrics on osp18
  hosts:  "{{ cifmw\_target\_hook\_host | default('localhost')  }}"
  gather\_facts: true
  environment:
    KUBECONFIG: "path to kubeconfig"
    PATH: "PATH variable contents"
  tasks
    - name: "Run Telemetry Verify Metrics tests"
      ansible.builtin.import_role:
        name: telemetry_verify_metrics

License
-------

Apache 2
