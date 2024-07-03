telemetry_logging
=========

Test logging in Openstack

Requirements
------------
The following resources are required in the OpenStack cloud
* network called public
* network called provate
* security group called basic with ssh and tcp enabled to the VMs 
* a flavor called m1.small
* an image called cirros

Role Variables
--------------

None

Dependencies
------------

Openstack on Openshift deployed. Then logging enabled for Openstack

Example Playbook
----------------

Each tasks/playbook.yml should be called independently via "ansible.builtin.include_role" with appropriate vars passed:

  tasks:
    - name: Remove "{{ container_out_file }}" 
      ansible.builtin.file:
        path: "{{ container_out_file }}" 
        state: absent
      changed_when: false

    - name: Verify containers on edpm-compute nodes
      ansible.builtin.include_role: 
        name: qe_common
        tasks_from: container_tests.yml
      loop: "{{ container_list }}" 

    - name: Copy output file to hypervisor
      ansible.builtin.fetch:
        src: "/root/{{ container_out_file }}" 
        dest: ./
        flat: true
      changed_when: false



License
-------

Apache 2

Author Information
------------------

An optional section for the role authors to include contact information, or a website (HTML is not allowed).
