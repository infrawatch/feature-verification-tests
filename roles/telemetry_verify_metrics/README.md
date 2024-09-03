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
- Verify NodeExporter metrics are being exposed and stored
    - Use openstack observabilityclient to verify NodeExporter metrics are stored in Prometheus

Role Variables
--------------
openstack\_cmd - command to access openstack cli. For example: "oc rsh openstackclient openstack"

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
