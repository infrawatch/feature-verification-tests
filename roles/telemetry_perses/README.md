Telemetry_perses
================

Verify that the Perses-based OpenStack observability dashboards
are delivered and reachable from the OpenShift console.

This is the successor of `telemetry_graphing`, which covers the older
OpenShift console-native/grafana-like dashboards delivered as ConfigMaps.
The new dashboards are shipped as `PersesDashboard` custom resources,
rendered by the Cluster Observability Operator under *Observe -> Dashboards
(Perses)* in the OpenShift Console interface.


Requirements
------------

1. Deployed RHOSO-19 environment.
2. The `dashboardsEnabled: true` setting in the controlplane.
3. The `UIPlugin` of type `Monitoring` with `spec.monitoring.perses.enabled:
   true` setting* – COO provisions the Perses backend from it to actually
   deliver the dashboards.

The prerequisites (2., 3.) are checked by `ci/run_perses_test.yml`,
which skips the play rather than failing when they are absent.

\* – The telemetry-operator deliberately does not create this object;
     without it the dashboards exist as CRs but render nowhere.


Example Playbook
----------------

No need for any extra steps or variables for a typical run,
see **Variables** below for optional overrides.

```yaml
- hosts: servers
  tasks:
    - ansible.builtin.import_role:
        name: telemetry_perses
```


Variables
---------

The parameters that may be worth overriding:

* `perses_expected_dashboards`
  – dashboards asserted to be present in the deployment.

See `defaults/main.yml` for details.


License
-------

[Apache 2](../../LICENSE)
