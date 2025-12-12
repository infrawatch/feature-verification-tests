telemetry_chargeback
=========
The **`telemetry_chargeback`** role is designed to test the **RHOSO Cloudkitty** feature. These tests are specific to the Cloudkitty feature. Tests that are not specific to this feature (e.g., standard OpenStack deployment validation, basic networking) should be added to a common role.

Requirements
------------
It relies on the following being available on the target or control host:

* This role requires **Ansible 2.9** or newer.
* The **OpenStack CLI client** must be installed and configured with administrative credentials.
* Required Python libraries for the `openstack` CLI (e.g., `python3-openstackclient`).
* Connectivity to the OpenStack API endpoint.

It is expected to be run **after** a successful deployment and configuration of the following components:

* **OpenStack:** A functional OpenStack cloud (RHOSO) environment.
* **Cloudkitty:** The Cloudkitty service must be installed, configured, and running.

Role Variables
--------------
The role uses a few primary variables to control the testing environment and execution.

| Variable | Default Value | Description |
|----------|---------------|-------------|
| `openstack_cmd` | `openstack` | The command used to execute OpenStack CLI calls. This can be customized if the binary is not in the standard PATH. |

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
