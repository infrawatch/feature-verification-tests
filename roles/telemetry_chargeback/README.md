telemetry_chargeback
===================

The **`telemetry_chargeback`** role validates and tests the **RHOSO CloudKitty** chargeback feature. It generates synthetic Loki log data, pushes it to Loki, retrieves it back, and asserts that CloudKitty's rating matches the expected synthetic totals within a configurable tolerance.

**Note:** This role contains tests specific to the CloudKitty feature. Generic OpenStack tests (deployment validation, basic networking) should be placed the common role.

Requirements
------------

### System Requirements

* **Ansible:** Version 2.9 or newer
* **Python 3** with the following libraries:
  * `PyYAML` - YAML parsing and generation
  * `Jinja2` - Template rendering
* **OpenStack CLI:** Installed and configured with administrative credentials
  * Package: `python3-openstackclient`
* **Network:** Connectivity to OpenStack API endpoints

### Infrastructure Requirements

This role must be run **after** successful deployment of:

* **OpenStack (RHOSO):** Functional cloud environment
* **CloudKitty:** Chargeback service installed, configured, and running
* **Loki/OpenShift:** Required for data ingestion and retrieval
  * Control host needs `oc` CLI access
  * CloudKitty Loki stack (route, certificates, ingester) deployed

Role Variables
--------------

### User-Configurable Variables (defaults/main.yml)

| Variable | Default Value | Description |
|----------|---------------|-------------|
| `openstack_cmd` | `"openstack"` | OpenStack CLI command |
| `cloudkitty_debug` | `false` | Enable debug mode for CloudKitty operations |
| `cloudkitty_debug_dir` | `"{{ ... }}"` | Directory for debug output (auto-set based on debug flag) |
| `ck_artifacts_dir` | `"{{ cifmw_basedir }}/artifacts"` | Directory for generated artifacts and test output |
| `cert_dir` | `"{{ cifmw_basedir }}/ck-certs"` | Directory for CloudKitty client certificates |
| `local_cert_dir` | `"{{ cifmw_basedir }}/flush_certs"` | Local directory for flush certificates |
| `remote_cert_dir` | `"osp-certs"` | Remote directory inside OpenStack pod for certificates |
| `cert_secret_name` | `"cert-cloudkitty-client-internal"` | OpenShift secret name for client certificates |
| `client_secret` | `"secret/cloudkitty-lokistack-gateway-client-http"` | Secret for flush client certificates |
| `ca_configmap` | `"cm/cloudkitty-lokistack-ca-bundle"` | ConfigMap for CA bundle |
| `logql_query` | `'{service="cloudkitty"}'` | LogQL query for Loki |
| `cloudkitty_namespace` | `"openstack"` | Kubernetes namespace where CloudKitty is deployed |
| `openstackpod` | `"openstackclient"` | OpenStack client pod name |
| `limit` | `1500` | Maximum entries for Loki query results |
| `cloudkitty_test_scenarios` | `["test_static", "test_dyn_basic"]` | List of test scenario names (without `.yml` extension) |

### Internal Variables (vars/main.yml)

| Variable | Default | Description |
|----------|---------|-------------|
| `rating_tolerance_pct` | `0.005` | Tolerance for synthetic-vs-CK rating comparison (0.5%) |
| `total_rate_job` | `0` | Accumulated total rate across all scenarios |
| `job_earliest_start_time` | `""` | Earliest begin time across all scenarios |
| `job_latest_end_time` | `""` | Latest end time across all scenarios |
| `previous_scenario_end_time` | `""` | End time of previous scenario (for chaining) |

How It Works
------------

The role executes the following workflow:

### 1. CloudKitty Validation (`chargeback_tests.yml`)
- Verifies CloudKitty pods are running
- Validates endpoints and services
- Enables the hashmap rating module (priority 100)
- Validates module state

### 2. Loki Environment Setup (`setup_loki_env.yml`)
- Extracts Loki route information from OpenShift
- Retrieves certificates from secrets/configmaps
- Configures Loki push/query URLs

### 3. Test Scenario Loop (`run_test_scenarios.yml`)

Scenarios are processed sequentially in reverse list order. For each scenario:

**a. Generate Synthetic Data** (`gen_synth_loki_data.yml`)
- Runs `gen_synth_loki_data.py` to produce Loki-format JSON
- Runs `gen_db_summary.py` to calculate expected metrics summary

**b. Load Data to Loki** (`load_loki_data.yml`)
- POSTs synthetic JSON to the Loki push API
- Flushes Loki ingester to persist data

**c. Retrieve and Validate** (`loki_diff_db_upload-vs-download.yml`)
- Queries Loki to retrieve the ingested data
- Asserts all expected log entries are returned
- Generates metrics summary from retrieved data
- Compares synthetic vs Loki-retrieved summaries

**d. Accumulate Job Statistics** (`job_scenario_stats.yml`)
- Accumulates `total_rate_job` across scenarios
- Tracks `job_earliest_start_time` and `job_latest_end_time`

### 4. Rating Comparison (`loki_total_rate.yml`)

After all scenarios complete:

- Queries Loki for all CloudKitty data in the current month
- Retrieves CloudKitty rating summary (`rating summary get`) and dataframes
- Compares accumulated synthetic rating against CloudKitty's rating
- **Asserts match within configurable tolerance** (default 0.5%)

The assertion uses the formula:
```
tolerance = (synth_rating + ck_rating) * rating_tolerance_pct / 2
pass if |synth_rating - ck_rating| < tolerance
```

### 5. Cleanup (`cleanup_ck.yml`)
- Removes temporary certificate directories
- Always runs (even on failure) via block/rescue/always structure

Price Calculation
-----------------

The role's price calculation matches CloudKitty's internal computation:

```
price = unit_cost * _apply_mutate(qty, mutate)
```

Where `_apply_mutate` applies one of:
- **NONE** (default): No transformation, use qty as-is
- **CEIL**: Round qty up to nearest integer
- **FLOOR**: Round qty down to nearest integer
- **NUMBOOL**: 1.0 if qty > 0, else 0.0
- **NOTNUMBOOL**: 0.0 if qty > 0, else 1.0

The `price` field in each log entry is pre-computed at generation time, and `gen_db_summary.py` sums these prices directly to get the total rating per type and overall.

Python Scripts
--------------

### gen_synth_loki_data.py

Generates synthetic Loki-format JSON log data from scenario YAML files and a Jinja2 template.

**Usage:**
```bash
python3 gen_synth_loki_data.py --tmpl <template> -t <scenario> -o <output> [options]
```

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `--tmpl PATH` | Yes | - | Path to Jinja2 template file |
| `-t, --test PATH` | Yes | - | Path to scenario YAML file |
| `-o, --output PATH` | Yes | - | Path for output JSON file |
| `--end_time TIMESTAMP` | No | Current UTC | End timestamp in ISO 8601 format |
| `--ascending` | No | - | Sort timestamps oldest-first |
| `--descending` | No | Yes | Sort timestamps newest-first |
| `--debug BOOL` | No | `false` | Enable debug logging |

**Output:** Each log entry contains: `start`, `end`, `type`, `unit`, `description`, `qty`, `unit_cost`, `price`, `groupby`, `metadata`, `mutate`.

### gen_db_summary.py

Parses Loki JSON log data and generates a YAML summary with per-type and total rating.

**Usage:**
```bash
python3 gen_db_summary.py -j <input_json> [-o <output>] [--debug BOOL] [--debug_dir DIR]
```

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `-j, --json PATH` | Yes | - | Input JSON file (Loki format) |
| `-o, --output PATH` | No | `<stem>_total.yml` | Output YAML file |
| `--debug BOOL` | No | `false` | Write debug diff file |
| `--debug_dir DIR` | No | Output dir | Directory for debug files |

**Output YAML Structure:**
```yaml
time:
  begin_step: {nanosec, begin, end}
  end_step: {nanosec, begin, end}
data_summary:
  total_timesteps: <count>
  metrics_per_step: <count>
  log_count: <total_entries>
  total_rate_scenario: <sum_of_all_prices>
rate_by_type:
  - {Begin, End, Qty, Rate, Type}
```

Scenario Configuration
----------------------

Test scenarios are YAML files in the `files/` directory, referenced by name (without `.yml` extension) in `cloudkitty_test_scenarios`.

### Available Scenarios

| File | Description |
|------|-------------|
| `test_static.yml` | Static scenario with constant qty/unit_cost values, 2 metric types, 1-hour window |
| `test_dyn_basic.yml` | Dynamic scenario with 6 metric types including NUMBOOL mutations, 1-hour window |

### Scenario File Structure

```yaml
generation:
  days: 1/24              # Time window (fractional: 1/24 = 1 hour)
  step_seconds: 300        # Time step interval in seconds

log_types:
  - type: ceilometer_image_size
    unit: MiB
    description: null
    qty: 2324              # Scalar or list for step-based distribution
    unit_cost: 0.00009     # Scalar or list for step-based distribution
    groupby:
      resource: cloudkitty
      project: null
      user: null
    metadata:
      container_format: bare
    mutate: NUMBOOL        # Optional: NONE, CEIL, FLOOR, NUMBOOL, NOTNUMBOOL

required_fields:
  - type
  - unit
  - qty
  - unit_cost
  - groupby

date_fields:
  - week_of_the_year
  - day_of_the_year
  - month
  - year

loki_stream:
  service: cloudkitty
```

When `qty` or `unit_cost` is a list, values are distributed evenly across time steps (e.g., 4 values over 12 steps = 3 steps per value).

Task Files
----------

| File | Description |
|------|-------------|
| `main.yml` | Entry point: validation, setup, scenario loop, rating comparison, cleanup |
| `chargeback_tests.yml` | CloudKitty pod, endpoint, service, and module validation |
| `setup_loki_env.yml` | Loki route discovery and certificate extraction |
| `run_test_scenarios.yml` | Per-scenario orchestration (generate, load, retrieve, stats) |
| `gen_synth_loki_data.yml` | Runs gen_synth_loki_data.py and gen_db_summary.py |
| `load_loki_data.yml` | POSTs data to Loki and flushes ingester |
| `ingest_loki_data.yml` | Loki POST and flush operations |
| `flush_loki_data.yml` | Loki ingester flush via API |
| `retrieve_loki_data.yml` | Queries Loki API with retries and validates data integrity |
| `loki_diff_db_upload-vs-download.yml` | Compares synthetic vs Loki-retrieved data |
| `job_scenario_stats.yml` | Accumulates rate and tracks time range across scenarios |
| `loki_total_rate.yml` | Monthly Loki query, CK rating retrieval, and rating assertion |
| `cleanup_ck.yml` | Removes temporary certificate directories |

Dependencies
------------

This role has no direct hard dependencies on other Ansible roles.

Example Playbook
----------------

**Basic usage (runs default scenarios):**
```yaml
- name: "Run chargeback tests"
  hosts: controllers
  gather_facts: false

  tasks:
    - name: "Run chargeback validation"
      ansible.builtin.import_role:
        name: telemetry_chargeback
```

**With custom configuration:**
```yaml
- name: "Run chargeback tests with custom settings"
  hosts: controllers
  gather_facts: false

  tasks:
    - name: "Run chargeback validation"
      ansible.builtin.import_role:
        name: telemetry_chargeback
      vars:
        cloudkitty_namespace: "my-custom-namespace"
        cloudkitty_debug: true
        rating_tolerance_pct: 0.01
```

**Run specific test scenarios:**
```yaml
- name: "Run chargeback tests with specific scenarios"
  hosts: controllers
  gather_facts: false

  tasks:
    - name: "Run chargeback validation with custom scenarios"
      ansible.builtin.import_role:
        name: telemetry_chargeback
      vars:
        cloudkitty_test_scenarios:
          - "test_static"
```

License
-------

Apache 2.0

Author Information
------------------

Alex Yefimov, Red Hat

**Project:** RHOSO (Red Hat OpenStack Services on OpenShift)
**Component:** Telemetry - CloudKitty Chargeback
