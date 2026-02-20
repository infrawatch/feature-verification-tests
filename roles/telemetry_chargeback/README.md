telemetry_chargeback
=========
The **`telemetry_chargeback`** role is designed to test the **RHOSO Cloudkitty** feature. These tests are specific to the Cloudkitty feature. Tests that are not specific to this feature (e.g., standard OpenStack deployment validation, basic networking) should be added to a common role.

The role performs two main functions:

1. **CloudKitty Validation** - Enables and configures the CloudKitty hashmap rating module, then validates its state.
2. **Synthetic Data Generation & Analysis** - Generates synthetic Loki log data for testing chargeback scenarios and calculates metric totals. The role automatically discovers and processes all scenario files matching `test_*.yml` in the `files/` directory. For each scenario it runs: generate synthetic data, compute syn-totals, ingest to Loki, flush Loki ingester memory, and get cost via CloudKitty rating summary (using begin/end from syn-totals). Retrieve-from-Loki is included in the load_loki_data flow. After all scenarios, the role runs cleanup (`cleanup_ck.yml`) to remove the local flush cert directory.

Requirements
------------
It relies on the following being available on the target or control host:

* This role requires **Ansible 2.9** or newer.
* The **OpenStack CLI client** must be installed and configured with administrative credentials.
* Required Python libraries for the `openstack` CLI (e.g., `python3-openstackclient`).
* Connectivity to the OpenStack API endpoint.
* **Python 3** with the following libraries for synthetic data generation and analysis:
  * `PyYAML`
  * `Jinja2`

It is expected to be run **after** a successful deployment and configuration of the following components:

* **OpenStack:** A functional OpenStack cloud (RHOSO) environment.
* **Cloudkitty:** The Cloudkitty service must be installed, configured, and running.
* **Loki / OpenShift (for ingest and flush):** When using ingest and flush tasks, the control host must have `oc` CLI access, and the Cloudkitty Loki stack (route, certificates, ingester) must be deployed. The role sets Loki push/query URLs and extracts certificates via `setup_loki_env.yml`.

Role Variables
--------------
The role uses the following variables to control the testing environment and execution.

### User-Configurable Variables (defaults/main.yml)

| Variable | Default Value | Description |
|----------|---------------|-------------|
| `openstack_cmd` | `openstack` | The command used to execute OpenStack CLI calls. This can be customized if the binary is not in the standard PATH. |

### Internal Variables (vars/main.yml)

These variables are used internally by the role and typically do not need to be modified.

| Variable | Default Value | Description |
|----------|---------------|-------------|
| `logs_dir_zuul` | `{{ ansible_env.HOME }}/ci-framework-data/logs` | Remote directory for log files. |
| `artifacts_dir_zuul` | `{{ ansible_env.HOME }}/ci-framework-data/artifacts` | Directory for generated artifacts. |
| `cloudkitty_scenario_dir` | `{{ role_path }}/files` | Directory containing scenario files (`test_*.yml`). |
| `cloudkitty_synth_data_suffix` | `-synth_data.json` | Suffix for generated synthetic data files. |
| `cloudkitty_loki_data_suffix` | `-loki_data.json` | Suffix for Loki query result JSON files. |
| `cloudkitty_synth_totals_suffix` | `-synth_metrics_totals.yml` | Suffix for generated metric totals files (from synthetic data). |
| `cloudkitty_loki_totals_suffix` | `-loki_totals.yml` | Suffix for CloudKitty rating summary output files (from loki_rate task). |
| `cloudkitty_loki_totals_metrics_suffix` | `-loki_metrics_totals.yml` | Suffix for metric totals computed from Loki-retrieved JSON (retrieve_loki_data task). |
| `cloudkitty_synth_script` | `{{ role_path }}/files/gen_synth_loki_data.py` | Path to the synthetic data generation script. |
| `cloudkitty_data_template` | `{{ role_path }}/templates/loki_data_templ.j2` | Path to the Jinja2 template for Loki data format. |
| `cloudkitty_totals_script` | `{{ role_path }}/files/gen_synth_loki_metrics_totals.py` | Path to the metric totals calculation script. |

### Loki / OpenShift Variables (vars/main.yml)

Used by setup, ingest, flush, and retrieve tasks when running against Loki on OpenShift:

| Variable | Default Value | Description |
|----------|---------------|-------------|
| `cert_secret_name` | `cert-cloudkitty-client-internal` | OpenShift secret name for client certificates. |
| `cert_dir` | `{{ ansible_user_dir }}/ck-certs` | Local directory for extracted ingest/query certs. |
| `client_secret` | `secret/cloudkitty-lokistack-gateway-client-http` | Secret for flush client certs. |
| `ca_configmap` | `cm/cloudkitty-lokistack-ca-bundle` | ConfigMap for CA bundle. |
| `remote_cert_dir` | `osp-certs` | Directory inside the OpenStack pod for certs. |
| `local_cert_dir` | `{{ ansible_env.HOME }}/ci-framework-data/flush_certs` | Local directory for flush certs (removed by cleanup_ck.yml after the run). |
| `logql_query` | `{service="cloudkitty"}` (overridable via `loki_query`) | LogQL query for Loki. |
| `cloudkitty_namespace` | `openstack` | OpenShift namespace for Cloudkitty/Loki resources. |
| `openstackpod` | `openstackclient` | OpenStack client pod name for exec/cp. |
| `lookback` | `6` | Days lookback for Loki query time range. |
| `limit` | `50` | Limit for Loki query results. |

Loki push/query URLs are set dynamically in `setup_loki_env.yml` from the Cloudkitty Loki route.

### Dynamically Set Variables

Set in **main.yml** from the OpenStack CLI (`openstack project show admin` / `openstack user show admin`):

| Variable | Description |
|----------|-------------|
| `cloudkitty_project_id` | ID of the OpenStack project named `admin` (empty string if not found). Passed as `-p` to the synthetic data generator when non-empty. |
| `cloudkitty_user_id` | ID of the OpenStack user named `admin` (empty string if not found). Passed as `-u` to the synthetic data generator when non-empty. |

Set in **gen_synth_loki_data.yml** for each scenario file during the loop:

| Variable | Description |
|----------|-------------|
| `cloudkitty_data_file` | Local path for generated JSON data (`{{ artifacts_dir_zuul }}/{{ scenario_name }}-synth_data.json`) |
| `cloudkitty_synth_totals_file` | Local path for calculated metric totals (`{{ artifacts_dir_zuul }}/{{ scenario_name }}{{ cloudkitty_synth_totals_suffix }}`) |
| `cloudkitty_test_file` | Path to the scenario configuration file (`{{ cloudkitty_scenario_dir }}/{{ scenario_name }}.yml`) |

Scenario Configuration
----------------------
The synthetic data generation is controlled by YAML configuration files in the `files/` directory. Any file matching `test_*.yml` will be automatically discovered and processed.

Each scenario file defines:

* **generation** - Time range configuration (days, step_seconds)
* **log_types** - List of log type definitions. Each entry has name, type, unit, description, qty, price, groupby, and metadata. The **groupby** dict typically includes dimension keys (e.g. id, user_id, project_id, tenant_id); the generator merges **date_fields** into groupby at run time.
* **required_fields** - Top-level keys required for each log type (e.g. type, unit, qty, price, groupby, metadata)
* **date_fields** - Date field names to merge into groupby (week_of_the_year, day_of_the_year, month, year)
* **loki_stream** - Loki stream configuration (service name)

Example scenario files:
* `test_static_basic.yml` - Basic static values for qty and price
* `test_dyn_basic.yml` - Dynamic values distributed across time steps
* `test_all_qty_zero.yml` - All quantities set to zero for testing

Dependencies
------------
This role has no direct hard dependencies on other Ansible roles.

Example Playbook
----------------
```yaml
- name: "Run chargeback tests"
  hosts: controllers
  gather_facts: no

  tasks:
    - name: "Run chargeback specific tests"
      ansible.builtin.import_role:
        name: telemetry_chargeback
```

Author Information
------------------

Alex Yefimov, Red Hat
