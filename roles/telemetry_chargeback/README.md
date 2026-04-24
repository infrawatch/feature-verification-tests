telemetry_chargeback
=========
The **`telemetry_chargeback`** role is designed to test the **RHOSO Cloudkitty** feature. These tests are specific to the Cloudkitty feature. Tests that are not specific to this feature (e.g., standard OpenStack deployment validation, basic networking) should be added to a common role.

The role performs two main functions:

1. **CloudKitty Validation** - Enables and configures the CloudKitty hashmap rating module, then validates its state.
2. **Synthetic Data Generation** - Generates synthetic Loki log data for testing chargeback scenarios using a Python script and Jinja2 template.

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
| `cloudkitty_debug` | `false` | Enable debug mode for CloudKitty database dumps. |
| `logs_dir_zuul` | `{{ ansible_env.HOME }}/ci-framework-data/logs` | Directory for log files. |
| `artifacts_dir_zuul` | `{{ ansible_env.HOME }}/ci-framework-data/artifacts` | Directory for generated artifacts and test output. |
| `cert_dir` | `{{ ansible_user_dir }}/ck-certs` | Directory for CloudKitty client certificates. |
| `local_cert_dir` | `{{ ansible_env.HOME }}/ci-framework-data/flush_certs` | Local directory for certificate extraction. |
| `cloudkitty_namespace` | `openstack` | Kubernetes namespace where CloudKitty is deployed. |

How It Works
------------

The role executes the following workflow:

1. **CloudKitty Validation** - Enables the hashmap rating module and sets its priority to 100.
2. **Loki Environment Setup** - Extracts Loki route information and certificates from the OpenShift cluster.
3. **Admin Credentials** - Retrieves admin project ID and user ID for test data generation.
4. **Scenario Discovery** - Finds all `test_*.yml` scenario files in the scenario directory.
5. **Scenario Loop** - For each scenario file found (exposed as `{{ scenario_name }}`):
   - Generates synthetic Loki log data based on the scenario configuration
   - Calculates expected chargeback metrics from the generated data
   - Loads the metrics for validation
6. **Cleanup** - Removes temporary certificate directories.

The role uses `{{ scenario_name }}` as the loop variable when processing multiple test scenarios, making it easy to track which scenario is currently being executed.

Scenario Configuration
----------------------
The synthetic data generation is controlled by YAML configuration files in the `files/` directory. Any file matching the pattern `test_*.yml` will be automatically discovered and executed.

**Available scenarios:**
- `test_static.yml` - Static test scenario with predefined values
- `test_dyn_basic.yml` - Dynamic test scenario with variable values over time

Each scenario file defines:

* **generation** - Time range configuration (days, step_seconds)
* **log_types** - List of log type definitions with name, type, unit, qty, price, groupby, and metadata
* **required_fields** - Fields required for validation
* **date_fields** - Date fields to add to groupby (week_of_the_year, day_of_the_year, month, year)
* **loki_stream** - Loki stream configuration (service name)

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
