telemetry_chargeback
=========
The **`telemetry_chargeback`** role is designed to test the **RHOSO Cloudkitty** feature. These tests are specific to the Cloudkitty feature. Tests that are not specific to this feature (e.g., standard OpenStack deployment validation, basic networking) should be added to a common role.

The role performs four main functions:

1. **CloudKitty Validation** - Enables and configures the CloudKitty hashmap rating module, then validates its state.
2. **Synthetic Data Generation** - Generates synthetic Loki log data for testing chargeback scenarios using a Python script and 
Jinja2 template.
3. **Ingest data and Flush to Loki** - Ingests synthetic CloudKitty log data and Flush Loki Ingester Memory to Storage
4. **Retrieval of data** - Verifies retrieval of data from loki

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
| `ck_synth_script` | `{{ role_path }}/files/gen_synth_loki_data.py` | Path to the synthetic data generation script. |
| `ck_data_template` | `{{ role_path }}/template/loki_data_templ.j2` | Path to the Jinja2 template for Loki data format. |
| `ck_data_config` | `{{ role_path }}/files/test_static.yml` | Path to the scenario configuration file. |
| `ck_output_file_local` | `{{ artifacts_dir_zuul }}/loki_synth_data.json` | Local path for generated synthetic data. |
| `ck_output_file_remote` | `{{ logs_dir_zuul }}/gen_loki_synth_data.log` | Remote destination for synthetic data. |
| `ck_loki_retrieve_file` | `{{ logs_dir_zuul }}/retrieve_loki_op.json` | Path where the retrieval of loki data is stored. |

Scenario Configuration
----------------------
The synthetic data generation is controlled by a YAML configuration file (`files/test_static.yml`). This file defines:

* **generation** - Time range configuration (days, step_seconds)
* **log_types** - List of log type definitions with name, type, unit, qty, price, groupby, and metadata
* **required_fields** - Fields required for validation
* **date_fields** - Date fields to add to groupby (week_of_the_year, day_of_the_year, month, year)
* **loki_stream** - Loki stream configuration (service name)

Dependencies
------------
This role has no direct hard dependencies on other Ansible roles.

This runs 5 playbooks
---------------------
```yaml
- name: "Validate Chargeback Feature"
  ansible.builtin.include_tasks: "chargeback_tests.yml"

- name: "Generate Synthetic Data"
  ansible.builtin.include_tasks: "gen_synth_loki_data.yml"

- name: "Ingests Cloudkitty Data log"
  ansible.builtin.include_tasks: "ingest_loki_data.yml"

- name: "Flush Data to loki Storage"
  ansible.builtin.include_tasks: "flush_loki_data.yml"

- name: "Retrieve Data log from loki"
  ansible.builtin.include_tasks: "retrieve_loki_data.yml"
```

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

Alex Yefimov, Muneesha Yadla
