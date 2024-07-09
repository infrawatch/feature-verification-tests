telemetry_logging
=========

Test logging in Openstack

Requirements
------------

Role Variables
--------------

  For journal_tests.yml
    
    identifiers_list  
      - Lists identifier strings to look for in the journalctl of the compute nodes
   

Dependencies
------------

Openstack on Openshift deployed and logging enabled for Openstack

Example Playbook
----------------

Each tasks/playbook.yml should be called independently via "ansible.builtin.include_role" with appropriate vars passed:

    tasks:
    - name: Verify journalctl identifiers 
      ansible.builtin.include_role:
        name: telemetry_logging
        tasks_from: journal_tests.yml
      loop: "{{ identifiers_list }}"

License
-------

Apache 2

Author Information
------------------

An optional section for the role authors to include contact information, or a website (HTML is not allowed).
