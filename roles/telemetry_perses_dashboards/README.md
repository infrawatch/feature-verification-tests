telemetry_perses_dashboards
===========================

Verify that the Perses-based OpenStack observability dashboards
are delivered correctly by the Telemetry Operator.

This role verifies:

- Perses CRDs are present (provided by COO 1.5.0)
- PersesDatasource CR exists and points to the MetricStorage Prometheus
- Expected PersesDashboard CRs are created in the openstack namespace
- Each dashboard is owned by the MetricStorage CR
- Legacy Grafana ConfigMaps are cleaned up from openshift-config-managed
- Dashboards listed in disabledDashboards are absent

This is the successor of `telemetry_graphing`, which covers the older
OpenShift console-native dashboards delivered as ConfigMaps. The new
dashboards are shipped as `PersesDashboard` custom resources, rendered
by the Cluster Observability Operator under Observe > Dashboards (Perses)
in the OpenShift Console interface.


Requirements
------------

1. Deployed RHOSO 19 environment
2. `dashboardsEnabled: true` in the OpenStackControlPlane telemetry config
3. UIPlugin of type Monitoring with `spec.monitoring.perses.enabled: true`
   (COO provisions the Perses backend from it)

Prerequisites (2, 3) are checked by `ci/run_perses_dashboard_tests.yml`,
which skips the play rather than failing when they are absent.


Example Playbook
----------------

```yaml
- hosts: servers
  tasks:
    - ansible.builtin.import_role:
        name: telemetry_perses_dashboards
```


Variables
---------

See `defaults/main.yml` for the full list. Key overrides:

- `telemetry_perses_expected_dashboards` -- dashboards asserted to be present
- `telemetry_perses_disabled_dashboards` -- dashboards expected to be absent
- `telemetry_perses_namespace` -- namespace for Perses CRs (default: openstack)


License
-------

[Apache 2](../../LICENSE)
