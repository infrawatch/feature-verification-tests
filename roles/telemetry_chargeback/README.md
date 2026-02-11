telemetry_chargeback
=========
The **`telemetry_chargeback`** role is designed to test the **RHOSO Cloudkitty** feature. These tests are specific to the Cloudkitty feature. Tests that are not specific to this feature (e.g., standard OpenStack deployment validation, basic networking) should be added to a common role.

The role performs two main functions:

1. **CloudKitty Validation** - Enables and configures the CloudKitty hashmap rating module, then validates its state.
2. **Synthetic Data Generation** - Generates synthetic Loki log data for testing chargeback scenarios using a Python script and Jinja2 template. The role automatically discovers and processes all scenario files matching `test_*.yml` in the files directory.

Requirements
------------
It relies on the following being available on the target or control host:

* This role requires **Ansible 2.9** or newer.
* The **OpenStack CLI client** must be installed and configured with administrative credentials.
* Required Python libraries for the `openstack` CLI (e.g., `python3-openstackclient`).
* Connectivity to the OpenStack API endpoint.
* **Python 3** with the following libraries for synthetic data generation:
  * `PyYAML`
  * `Jinja2`

It is expected to be run **after** a successful deployment and configuration of the following components:

* **OpenStack:** A functional OpenStack cloud (RHOSO) environment.
* **Cloudkitty:** The Cloudkitty service must be installed, configured, and running.

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
| `logs_dir_zuul` | `/home/zuul/ci-framework-data/logs` | Remote directory for log files. |
| `artifacts_dir_zuul` | `/home/zuul/ci-framework-data/artifacts` | Directory for generated artifacts. |
| `ck_scenario_dir` | `{{ role_path }}/files` | Directory containing scenario files (`test_*.yml`). |
| `ck_synth_script` | `{{ role_path }}/files/gen_synth_loki_data.py` | Path to the synthetic data generation script. |
| `ck_data_template` | `{{ role_path }}/template/loki_data_templ.j2` | Path to the Jinja2 template for Loki data format. |

### Dynamically Set Variables (gen_synth_loki_data.yml)

These variables are set dynamically for each scenario file during the loop:

| Variable | Description |
|----------|-------------|
| `ck_data_file` | Local path for generated JSON data (`{{ artifacts_dir_zuul }}/{{ scenario_name }}.json`) |
| `ck_data_log` | Remote destination for log file (`{{ logs_dir_zuul }}/{{ scenario_name }}.log`) |
| `ck_test_file` | Path to the scenario configuration file (`{{ ck_scenario_dir }}/{{ scenario_name }}.yml`) |

Scenario Configuration
----------------------
The synthetic data generation is controlled by YAML configuration files in the `files/` directory. Any file matching `test_*.yml` will be automatically discovered and processed.

Each scenario file defines:

* **generation** - Time range configuration (days, step_seconds)
* **log_types** - List of log type definitions with name, type, unit, qty, price, groupby, and metadata
* **required_fields** - Fields required for validation
* **date_fields** - Date fields to add to groupby (week_of_the_year, day_of_the_year, month, year)
* **loki_stream** - Loki stream configuration (service name)

Example scenario files:
* `test_static_basic.yml` - Basic static values for qty and price
* `test_dyn_basic.yml` - Dynamic values distributed across time steps
* `test_all_qty_zero.yml` - All quantities set to zero for testing
* `test_all_price_zero.yml` - All prices set to zero for testing

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
