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
- Verfiy OpenstackNetworkExporter metrics are being exposed and stored
    - Use openstack observabilityclient to verify OpenstackNetworkExporter metrics are stored in Prometheus
- Verify OVN metrics are being exposed and stored
    - Use openstack observabilityclient to verify OVN metrics are stored in Prometheus

How the metric checks work
--------------------------
Most checks only need to know that a metric name exists, so they share one
`openstack metric list -f value` call per source instead of one
`openstack metric show` per metric. In this CLI the list command returns a
single `metric_name` column, so each output line is one bare name and the
checks can use exact membership against those lines. `--disable-rbac` is a
deprecated no-op that defaults to `True`, so it is not passed.

`tasks/get_metric_list.yml` performs the gather and records the names that are
missing. Callers supply the expected names:

    - name: Get the <source> metric list
      ansible.builtin.include_tasks:
        file: get_metric_list.yml
      vars:
        metric_list_gate: "{{ verify_metrics_prereqs_ok | bool }}"
        metric_list_expected:
          - <metric-a>
          - <metric-b>

The gate is applied to the command rather than to the include, so a blocked
source still registers `metric_list` (as a skipped task) and the asserts can
use `metric_list.stdout_lines` and `metric_list_missing` unconditionally. The
gather waits for every expected name, using 10 retries at 30 second intervals.
A group with missing metrics is reported once, listing all of them, rather
than once per metric, and the shared budget means a group with one missing
metric costs the same as a group with many.

Checks that need a label or a scrape target cannot use the name list. RabbitMQ
and MariaDB verify a `pod` label per pod with `openstack metric query`, and the
OVN controller and RAFT checks verify the scraped instance. Those keep their
own queries; only the existence part of the OVN checks uses the shared list.

Role Variables
--------------
openstack\_cmd - command to access openstack cli. For example: "oc rsh openstackclient openstack"
telemetry\_verify\_metrics\_metric\_sources\_to\_test - List of sources to test. Current set of possible sources: ceilometer\_compute\_agent, ceilometer\_central\_agent, ceilometer\_ipmi_\_agent, node\_exporter, rabbitmq, openstack\_network\_exporter, volume\_pool, ovn

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
