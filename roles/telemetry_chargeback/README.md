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

### Internal Variables (vars/main.yml)

| Variable | Default Value | Description |
|----------|---------------|-------------|
| `logs_dir_zuul` | `/home/zuul/ci-framework-data/logs` | Remote directory for log files. |
| `artifacts_dir_zuul` | `/home/zuul/ci-framework-data/artifacts` | Remote directory for generated artifacts. |
| `ck_scenario_dir` | `{{ role_path }}/files` | Local directory containing scenario files (test_*.yml). |
| `ck_synth_script` | `{{ role_path }}/files/gen_synth_loki_data.py` | Path to the Python script that generates synthetic Loki data. |
| `ck_data_template` | `{{ role_path }}/template/loki_data_templ.j2` | Path to the Jinja2 template for Loki data format. |

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
