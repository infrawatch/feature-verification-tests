telemetry_logging
=========

Test logging in Openstack

Requirements
------------

Role Variables
--------------

  For journal_tests.yml
    
    identifiers_test_id
      - polarion id for test
    identifiers_list  
      - Lists identifier strings to look for in the journalctl of the compute nodes
   

Dependencies
------------

Openstack on Openshift deployed and logging enabled for Openstack

Example Playbook
----------------

Each tasks/playbook.yml should be called independently via "ansible.builtin.import_role" with appropriate vars passed:

- name: "Verify logging journalctl identifiers" 
  hosts: computes
  gather_facts: no
  vars:
    identifiers_test_id: "RHOSO-12681"
    identifiers_list:
      - ceilometer_agent_compute
      - nova_compute

  tasks:
    - name: "Verify journalctl logging identifiers" 
      ansible.builtin.import_role:
        name: telemetry_logging
  

License
-------

Apache 2

Author Information
------------------

An optional section for the role authors to include contact information, or a website (HTML is not allowed).
