telemetry_chargeback

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

These variables can be overridden when importing the role or set at the play level. Users can customize these based on their deployment environment and test requirements.

| Variable | Default Value | Description |
|----------|---------------|-------------|
| `openstack_cmd` | `openstack` | The command used to execute OpenStack CLI calls. This can be customized if the binary is not in the standard PATH. |
| `cloudkitty_debug` | `false` | Enable debug mode for the role. |
| `logs_dir_zuul` | `{{ ansible_env.HOME }}/ci-framework-data/logs` | Directory for log files. |
| `artifacts_dir_zuul` | `{{ ansible_env.HOME }}/ci-framework-data/artifacts` | Directory for generated artifacts. |
| `cert_dir` | `{{ ansible_user_dir }}/ck-certs` | Local directory for extracted ingest/query certs. |
| `local_cert_dir` | `{{ ansible_env.HOME }}/ci-framework-data/flush_certs` | Local directory for flush certs (removed by cleanup_ck.yml after the run). |
| `remote_cert_dir` | `osp-certs` | Directory inside the OpenStack pod for certs. |
| `cert_secret_name` | `cert-cloudkitty-client-internal` | OpenShift secret name for client certificates. |
| `client_secret` | `secret/cloudkitty-lokistack-gateway-client-http` | Secret for flush client certs. |
| `ca_configmap` | `cm/cloudkitty-lokistack-ca-bundle` | ConfigMap for CA bundle. |
| `logql_query` | `{service="cloudkitty"}` (overridable via `loki_query`) | LogQL query for Loki. |
| `cloudkitty_namespace` | `openstack` | OpenShift namespace for Cloudkitty/Loki resources. |
| `openstackpod` | `openstackclient` | OpenStack client pod name for exec/cp. |
| `lookback` | `6` | Days lookback for Loki query time range. |
| `limit` | `50` | Limit for Loki query results. |
| `cloudkitty_test_scenarios` | `[]` | List of test scenario files to run (default: auto-discover all `test_*.yml` files). |

**Example: Overriding variables when importing the role**
```yaml
- name: "Run chargeback tests"
  ansible.builtin.import_role:
    name: telemetry_chargeback
  vars:
    cloudkitty_namespace: "my-custom-namespace"
    lookback: 10
    cloudkitty_debug: true
```

How It Works
------------

The role executes the following workflow:

1. **CloudKitty Validation** - Enables the hashmap rating module and sets its priority to 100.
2. **Loki Environment Setup** - Extracts Loki route information and certificates from the OpenShift cluster.
3. **Admin Credentials** - Retrieves admin project ID and user ID for test data generation.
4. **Scenario Discovery** - Finds all `test_*.yml` scenario files in the scenario directory (unless overridden by `cloudkitty_test_scenarios`).
5. **Scenario Loop** - For each scenario file found (exposed as `{{ scenario_name }}`):
   - Generates synthetic Loki log data based on the scenario configuration
   - Calculates expected chargeback metrics from the generated data
   - Loads the metrics for validation
6. **Cleanup** - Removes temporary certificate directories.

The role uses `{{ scenario_name }}` as the loop variable when processing multiple test scenarios, making it easy to track which scenario is currently being executed.

### Synthetic Data Scripts

**gen_synth_loki_data.py** — Generates Loki-format JSON from a scenario YAML and template.

| Option | Description |
|--------|--------------|
| `--tmpl` | Path to the Jinja2 template (e.g. `loki_data_templ.j2`). |
| `-t`, `--test` | Path to the scenario YAML (e.g. `test_dyn_basic.yml`). |
| `-o`, `--output` | Path to the output JSON file. |
| `-p`, `--project-id` | Optional; overrides `groupby.project_id` in every log entry. |
| `-u`, `--user-id` | Optional; overrides `groupby.user_id` in every log entry. |
| `--ascending` | Sort timestamps in ascending order (oldest first, newest last). |
| `--descending` | Sort timestamps in descending order (newest first, oldest last) - **default**. |
| `--debug` | Enable debug logging to stdout. |

By default, the script generates data in descending order (newest timestamps first), which is the expected format for Loki ingestion.

**gen_db_summary.py** — Parses Loki-style JSON (streams or `data.result`), sorts entries by timestamp, and writes a YAML summary. This script is invoked by the role for **both** synthetic totals (in `gen_synth_loki_data.yml`) and Loki-retrieved totals (in `retrieve_loki_data.yml`). It applies rate calculations with support for `factor`, `offset`, and `mutate` transformations.

| Option | Description |
|--------|--------------|
| `-j`, `--json` | Path to the input JSON file (required). |
| `-o`, `--output` | Path to the output YAML file (default: `<input_stem>_total.yml`). |
| `--debug` | Enable debug mode (writes `<stem>_diff.txt` with one `[ts,log]` JSON per line). |
| `--debug_dir` | Directory for debug output files (default: same directory as `-o` output file). |

Output YAML structure:

* **time** — `begin_step` / `end_step`, each with `nanosec` (nanosecond timestamp), `begin`, `end` (ISO window strings from the log payload). The `nanosec` values are used for Loki query time range.
* **data_summary** — `total_timesteps`, `metrics_per_step`, `log_count`, `total_rating`.
* **by_type** — `rate` (flat list with `Begin`, `End`, `Qty`, `Rate`, `Type` for each metric type). Rate calculated as `Σ((qty_mutated * factor + offset) * price)` where `qty_mutated` is the quantity after applying the `mutate` transformation.

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
| `cloudkitty_synth_totals_file` | Local path for calculated metric totals (`{{ artifacts_dir_zuul }}/{{ scenario_name }}-synth_metrics_summary.yml`) |
| `cloudkitty_test_file` | Path to the scenario configuration file (`{{ role_path }}/files/{{ scenario_name }}.yml`) |

Scenario Configuration
----------------------
The synthetic data generation is controlled by YAML configuration files in the `files/` directory. Any file matching `test_*.yml` will be automatically discovered and processed. Files whose names start with an underscore (e.g. `_test_*.yml`) are **not** discovered by the role; they can be used as reference or for manual runs.

**Available scenarios:**
- `test_dyn_basic.yml` - Dynamic test scenario with variable values over time

Each scenario file defines:

* **generation** — Time range configuration (days, step_seconds).
* **log_types** — List of log type definitions. Each entry has **type** (identifier and value in output), unit, description, qty, price, groupby, and metadata. The **groupby** dict typically includes dimension keys (e.g. resource, user, project); the generator merges **date_fields** into groupby at run time.
* **required_fields** — Top-level keys required for each log type (e.g. type, unit, qty, price, groupby).
* **date_fields** — Date field names to merge into groupby (week_of_the_year, day_of_the_year, month, year).
* **loki_stream** — Loki stream configuration (service name).

**groupby.resource** should be consistent by metric type across scenario files so that the same type always uses the same resource identifier.

### Data Generation Script Options

The `gen_synth_loki_data.py` script supports the following options:

* `--tmpl` - Path to the Jinja2 template file (required)
* `-t, --test` - Path to the scenario YAML file (required)
* `-o, --output` - Path for the output JSON file (required)
* `-p, --project-id` - Optional project ID to override the scenario file value
* `-u, --user-id` - Optional user ID to override the scenario file value
* `--ascending` - Sort timestamps in ascending order (oldest first, newest last)
* `--descending` - Sort timestamps in descending order (newest first, oldest last) - **default**
* `--debug` - Enable debug logging

By default, the script generates data in descending order (newest timestamps first), which is the expected format for Loki ingestion.

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
