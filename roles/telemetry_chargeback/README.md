telemetry_chargeback
===================

The **`telemetry_chargeback`** role validates and tests the **RHOSO CloudKitty** chargeback feature. It performs CloudKitty configuration validation and generates synthetic test data for chargeback scenario testing.

**Note:** This role contains tests specific to the CloudKitty feature. Generic OpenStack tests (deployment validation, basic networking) should be placed in a common role.

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
* **Loki/OpenShift** (optional): Required only for Loki integration features
  * Control host needs `oc` CLI access
  * CloudKitty Loki stack (route, certificates, ingester) deployed

Role Variables
--------------

### User-Configurable Variables (defaults/main.yml)

| Variable | Default Value | Description |
|----------|---------------|-------------|
| `openstack_cmd` | `"openstack"` | OpenStack CLI command (customize if not in PATH) |
| `cloudkitty_debug` | `false` | Enable debug mode for CloudKitty operations |
| `cloudkitty_debug_dir` | `"{{ (cloudkitty_debug \| bool) \| ternary(artifacts_dir_zuul + '/debug_ck_db', '') }}"` | Directory for debug output (auto-set based on debug flag) |
| `logs_dir_zuul` | `"{{ cifmw_basedir }}/logs"` | Directory for log files |
| `artifacts_dir_zuul` | `"{{ cifmw_basedir }}/artifacts"` | Directory for generated artifacts and test output |
| `cert_dir` | `"{{ cifmw_basedir }}/ck-certs"` | Directory for CloudKitty client certificates |
| `local_cert_dir` | `"{{ cifmw_basedir }}/flush_certs"` | Local directory for flush certificates (cleaned up after run) |
| `remote_cert_dir` | `"osp-certs"` | Remote directory inside OpenStack pod for certificates |
| `cert_secret_name` | `"cert-cloudkitty-client-internal"` | OpenShift secret name for client certificates |
| `client_secret` | `"secret/cloudkitty-lokistack-gateway-client-http"` | Secret for flush client certificates |
| `ca_configmap` | `"cm/cloudkitty-lokistack-ca-bundle"` | ConfigMap for CA bundle |
| `logql_query` | `"{{ loki_query \| default('{service=\"cloudkitty\"}') }}"` | LogQL query for Loki (overridable via `loki_query` variable) |
| `cloudkitty_namespace` | `"openstack"` | Kubernetes namespace where CloudKitty is deployed |
| `openstackpod` | `"openstackclient"` | OpenStack client pod name for exec/cp operations |
| `lookback` | `6` | Days to look back for Loki query time range |
| `limit` | `50` | Limit for Loki query results |

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
   - Automatically finds all `test_*.yml` files in `files/` directory

4. **Scenario Execution Loop** (for each discovered scenario)
   - Generates synthetic Loki log data (`gen_synth_loki_data.py`)
   - Calculates expected chargeback metrics (`gen_db_summary.py`)
   - Loads metrics for validation

5. **Cleanup** (`cleanup_ck.yml`)
   - Removes temporary certificate directories
   - Always runs (even on failure) via block/rescue/always structure


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

**gen_synth_loki_data.py** — Generates Loki-format JSON from a scenario YAML and template. By default, timestamps in the output are in descending order (newest first, oldest last). Use `--sort=ascending` to generate in chronological order (oldest first, newest last).

| Option | Description |
|--------|--------------|
| `--tmpl` | Path to the Jinja2 template (e.g. `loki_data_templ.j2`). |
| `-t`, `--test` | Path to the scenario YAML (e.g. `test_dyn_basic.yml`). |
| `-o`, `--output` | Path to the output JSON file. |
| `--sort` | Sort order for timestamps: `ascending` (oldest first, newest last) or `descending` (newest first, oldest last). Default: `descending`. |
| `--debug` | Enable debug logging. |

Scenario Configuration
----------------------

Test scenarios are defined in YAML files located in the `files/` directory. Any file matching the pattern `test_*.yml` will be automatically discovered and executed.

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

**Note:** Use consistent `resource` values by metric type across scenario files to ensure proper aggregation.

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
        lookback: 10
```

License
-------

Apache 2.0

Author Information
------------------

Alex Yefimov, Red Hat

**Project:** RHOSO (Red Hat OpenStack Services on OpenShift)  
**Component:** Telemetry - CloudKitty Chargeback
