telemetry_chargeback

The **`telemetry_chargeback`** role validates and tests the **RHOSO CloudKitty** chargeback feature. It performs CloudKitty configuration validation and generates synthetic test data for chargeback scenario testing.


The **`telemetry_chargeback`** role is designed to test the **RHOSO Cloudkitty** feature. These tests are specific to the Cloudkitty feature. Tests that are not specific to this feature (e.g., standard OpenStack deployment validation, basic networking) should be added to a common role.

The **`telemetry_chargeback`** role validates and tests the **RHOSO CloudKitty** chargeback feature. It performs CloudKitty configuration validation and generates synthetic test data for chargeback scenario testing.

1. **CloudKitty Validation** - Enables and configures the CloudKitty hashmap rating module, then validates its state.
2. **Synthetic Data Generation & Analysis** - Generates synthetic Loki log data for testing chargeback scenarios and calculates metric totals. The role automatically discovers and processes all scenario files matching `test_*.yml` in the `files/` directory. For each scenario it runs: generate synthetic data, compute syn-totals, ingest to Loki, flush Loki ingester memory, and get cost via CloudKitty rating summary (using begin/end from syn-totals). Retrieve-from-Loki is included in the load_loki_data flow. After all scenarios, the role runs cleanup (`cleanup_ck.yml`) to remove the local flush cert directory.
**Note:** This role contains tests specific to the CloudKitty feature. Generic OpenStack tests (deployment validation, basic networking) should be placed in a common role.

Requirements
------------

* This role requires **Ansible 2.9** or newer.
* The **OpenStack CLI client** must be installed and configured with administrative credentials.
* Required Python libraries for the `openstack` CLI (e.g., `python3-openstackclient`).
* Connectivity to the OpenStack API endpoint.
* **Python 3** with the following libraries for synthetic data generation and analysis:
  * `PyYAML`
  * `Jinja2`

* **Ansible:** Version 2.9 or newer
* **Python 3** with the following libraries:
  * `PyYAML` - YAML parsing and generation
  * `Jinja2` - Template rendering
* **OpenStack CLI:** Installed and configured with administrative credentials
  * Package: `python3-openstackclient`
* **Network:** Connectivity to OpenStack API endpoints

* **OpenStack:** A functional OpenStack cloud (RHOSO) environment.
* **Cloudkitty:** The Cloudkitty service must be installed, configured, and running.
* **Loki / OpenShift (for ingest and flush):** When using ingest and flush tasks, the control host must have `oc` CLI access, and the Cloudkitty Loki stack (route, certificates, ingester) must be deployed. The role sets Loki push/query URLs and extracts certificates via `setup_loki_env.yml`.

Role Variables
--------------

### User-Configurable Variables (defaults/main.yml)

These variables can be overridden when importing the role or set at the play level. Users can customize these based on their deployment environment and test requirements.

| Variable | Default Value | Description |
|----------|---------------|-------------|
| `openstack_cmd` | `"openstack"` | OpenStack CLI command (customize if not in PATH) |
| `cloudkitty_debug` | `false` | Enable debug mode for CloudKitty operations |
| `cloudkitty_debug_dir` | `"{{ (cloudkitty_debug \| bool) \| ternary(artifacts_dir_zuul + '/debug_ck_db', '') }}"` | Directory for debug output (auto-set based on debug flag) |
| `logs_dir_zuul` | `"{{ cifmw_basedir }}/logs"` | Directory for log files |
| `artifacts_dir_zuul` | `"{{ cifmw_basedir }}/artifacts"` | Directory for generated artifacts and test output |
| `cert_dir` | `"{{ ansible_user_dir }}/ck-certs"` | Directory for CloudKitty client certificates |
| `local_cert_dir` | `"{{ cifmw_basedir }}/flush_certs"` | Local directory for flush certificates (cleaned up after run) |
| `remote_cert_dir` | `"osp-certs"` | Remote directory inside OpenStack pod for certificates |
| `cert_secret_name` | `"cert-cloudkitty-client-internal"` | OpenShift secret name for client certificates |
| `client_secret` | `"secret/cloudkitty-lokistack-gateway-client-http"` | Secret for flush client certificates |
| `ca_configmap` | `"cm/cloudkitty-lokistack-ca-bundle"` | ConfigMap for CA bundle |
| `logql_query` | `"{service=\"cloudkitty\"}"` | LogQL query for Loki (overridable via `loki_query`) |
| `cloudkitty_namespace` | `"openstack"` | Kubernetes namespace where CloudKitty is deployed |
| `openstackpod` | `"openstackclient"` | OpenStack client pod name for exec/cp operations |
| `lookback` | `6` | Days to look back for Loki query time range |
| `limit` | `50` | Limit for Loki query results |
| `cloudkitty_test_scenarios` | `[]` | List of test scenario files to run (empty = auto-discover) |

How It Works
------------

The role executes the following workflow:

1. **CloudKitty Validation** (`chargeback_tests.yml`)
   - Enables the hashmap rating module
   - Sets priority to 100
   - Validates module state

2. **Loki Environment Setup** (`setup_loki_env.yml`)
   - Extracts Loki route information from OpenShift
   - Retrieves certificates from secrets/configmaps
   - Configures Loki push/query URLs

3. **Test Scenario Discovery**
   - **Auto-discovery** (default): Finds all `test_*.yml` files in `files/` directory
   - **User-provided**: Uses scenarios from `cloudkitty_test_scenarios` variable

4. **Scenario Execution Loop** (for each discovered scenario)
   - Generates synthetic Loki log data (`gen_synth_loki_data.py`)
   - Calculates expected chargeback metrics (`gen_db_summary.py`)
   - Loads metrics for validation

5. **Cleanup** (`cleanup_ck.yml`)
   - Removes temporary certificate directories
   - Always runs (even on failure) via block/rescue/always structure

### Loop Variable

The role uses `{{ scenario_name }}` as the loop variable when processing multiple test scenarios, making it easy to track which scenario is currently executing.

Python Scripts
--------------

The role includes two Python scripts for synthetic data generation and metrics calculation.

### gen_synth_loki_data.py

**Purpose:** Generates synthetic Loki-format JSON log data from scenario YAML files.

**Description:**
This script reads a scenario configuration file (YAML), processes time-series data according to the specified parameters, and renders it through a Jinja2 template to produce Loki-compatible JSON output. It supports metric transformations, date field injection, and configurable timestamp ordering.

**Usage:**
```bash
python3 gen_synth_loki_data.py --tmpl <template> -t <scenario> -o <output> [options]
```

**Required Arguments:**
| Argument | Description |
|----------|-------------|
| `--tmpl PATH` | Path to Jinja2 template file (e.g., `loki_data_templ.j2`) |
| `-t, --test PATH` | Path to scenario YAML file (e.g., `test_dyn_basic.yml`) |
| `-o, --output PATH` | Path for output JSON file |

**Optional Arguments:**
| Argument | Default | Description |
|----------|---------|-------------|
| `--ascending` | - | Sort timestamps in ascending order (oldest first, newest last) |
| `--descending` | **Yes** | Sort timestamps in descending order (newest first, oldest last) |
| `--debug` | `False` | Enable debug logging to stdout |

**Output:**
- Loki-compatible JSON file with timestamped log entries
- Each entry contains: type, unit, description, qty, price, groupby, metadata
- Optional transformation fields: mutate, factor, offset

**Example:**
```bash
python3 gen_synth_loki_data.py \
  --tmpl templates/loki_data_templ.j2 \
  -t files/test_dyn_basic.yml \
  -o artifacts/test_dyn_basic-synth_data.json \
  --descending
```

### gen_db_summary.py

**Purpose:** Parses Loki JSON log data and generates YAML summary with rating calculations.

**Description:**
This script extracts timestamped log entries from Loki JSON (either from synthetic generation or Loki query results), sorts them chronologically, applies chargeback transformations (mutate, factor, offset), and calculates per-type and total ratings. The output is a structured YAML summary suitable for validation and comparison.

**Usage:**
```bash
python3 gen_db_summary.py -j <input_json> [-o <output>] [--debug] [--debug_dir <dir>]
```

**Required Arguments:**
| Argument | Description |
|----------|-------------|
| `-j, --json PATH` | Input JSON file (Loki format or synthetic data) |

**Optional Arguments:**
| Argument | Default | Description |
|----------|---------|-------------|
| `-o, --output PATH` | `<input_stem>_total.yml` | Output YAML file path |
| `--debug` | `False` | Enable debug mode (writes `<stem>_diff.txt` file) |
| `--debug_dir DIR` | Output directory | Directory for debug files (defaults to output file's directory) |

**Output YAML Structure:**
```yaml
time:
  begin_step:
    nanosec: <timestamp_ns>
    begin: <ISO_timestamp>
    end: <ISO_timestamp>
  end_step:
    nanosec: <timestamp_ns>
    begin: <ISO_timestamp>
    end: <ISO_timestamp>

data_summary:
  total_timesteps: <count>
  metrics_per_step: <count_or_ERROR>
  log_count: <total_entries>
  total_rating: <sum_of_all_rates>

by_type:
  rate:
    - Begin: <ISO_timestamp>
      End: <ISO_timestamp>
      Qty: <quantity_sum>
      Rate: <calculated_rate>
      Type: <metric_type>
```

**Rating Calculation:**
For each log entry:
1. Apply `mutate` transformation to `qty` (CEIL, FLOOR, NUMBOOL, NOTNUMBOOL)
2. Apply linear transformation: `qty_transformed = qty_mutated * factor + offset`
3. Calculate rate: `rate = qty_transformed * price`
4. Sum rates by type and overall

**Supported Transformations:**
- `CEIL`: Round quantity up to nearest integer
- `FLOOR`: Round quantity down to nearest integer
- `NUMBOOL`: Convert to 1 if qty > 0, else 0
- `NOTNUMBOOL`: Convert to 0 if qty > 0, else 1
- `NONE`: No transformation

**Example:**
```bash
python3 gen_db_summary.py \
  -j artifacts/test_dyn_basic-synth_data.json \
  -o artifacts/test_dyn_basic-synth_metrics_summary.yml \
  --debug --debug_dir artifacts/debug
```

**Debug Output:**
When `--debug` is enabled, the script writes a `<stem>_diff.txt` file containing one JSON array per line: `[timestamp, log_entry]`. This is useful for troubleshooting data quality issues or timestamp ordering problems.

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

Test scenarios are defined in YAML files located in the `files/` directory. Any file matching the pattern `test_*.yml` will be automatically discovered unless you override with the `cloudkitty_test_scenarios` variable.

### Available Scenarios

| File | Description |
|------|-------------|
| `test_static.yml` | Static test scenario with predefined constant values |
| `test_dyn_basic.yml` | Dynamic test scenario with variable values over time, includes NUMBOOL transformations |

### Scenario File Structure

Each scenario file must define:

```yaml
# Time range configuration
generation:
  days: <number>              # Number of days to generate
  step_seconds: <seconds>     # Time step interval

# Validation configuration
required_fields:
  - type
  - unit
  - qty
  - price
  - groupby

# Date field injection
date_fields:
  - week_of_the_year
  - day_of_the_year
  - month
  - year

# Loki stream metadata
loki_stream:
  service: cloudkitty
```

### Field Details

**groupby fields:**
- `resource`: Tenant/resource identifier (e.g., `tenant-01`, `tenant-02`)
- `user`: User identifier (null for unspecified)
- `project`: Project identifier (null for unspecified)

**Transformation fields:**
- `mutate`: Type of transformation to apply to quantity
- `factor`: Multiplier applied after mutation (e.g., `1/1048576` for byte-to-MiB conversion)
- `offset`: Value added after factor multiplication

* **generation** — Time range configuration (days, step_seconds).
* **log_types** — List of log type definitions. Each entry has **type** (identifier and value in output), unit, description, qty, price, groupby, and metadata. The **groupby** dict typically includes dimension keys (e.g. resource, user, project); the generator merges **date_fields** into groupby at run time.
  * Optional rating calculation fields: **mutate**, **factor**, **offset** (transforms qty before rating calculation)
  * Supported mutate values: NUMBOOL, NOTNUMBOOL, CEIL, FLOOR
* **required_fields** — Top-level keys required for each log type (e.g. type, unit, qty, price, groupby).
* **date_fields** — Date field names to merge into groupby (week_of_the_year, day_of_the_year, month, year).
* **loki_stream** — Loki stream configuration (service name).

**groupby.resource** should be consistent by metric type across scenario files so that the same type always uses the same resource identifier.

Rating calculation applies transformations in this order:
1. **mutate** - Transform quantity (NUMBOOL: 0→0, >0→1; CEIL/FLOOR: round up/down)
2. **factor** - Multiply the mutated quantity
3. **offset** - Add to the result
4. **price** - Multiply to get final rate

Timestamps are formatted in ISO 8601 format with Z notation (e.g., `2023-10-26T14:30:00Z`).
**Note:** Use consistent `resource` values by metric type across scenario files to ensure proper aggregation.

### Overriding Auto-Discovery

To run specific scenarios instead of auto-discovering all `test_*.yml` files:

```yaml
- name: "Run specific chargeback tests"
  ansible.builtin.import_role:
    name: telemetry_chargeback
  vars:
    cloudkitty_test_scenarios:
      - test_dyn_basic
      - test_static
```

Or via command line:
```bash
ansible-playbook playbook.yml \
  --extra-vars "cloudkitty_test_scenarios=['test_dyn_basic']"
```

Dependencies
------------

This role has no direct hard dependencies on other Ansible roles.

Example Playbook
----------------

**Basic usage (auto-discover scenarios):**
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
        cloudkitty_test_scenarios:
          - test_dyn_basic
```

License
-------

Apache 2.0

Author Information
------------------

Alex Yefimov, Red Hat

**Project:** RHOSO (Red Hat OpenStack Services on OpenShift)  
**Component:** Telemetry - CloudKitty Chargeback
