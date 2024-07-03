qe_common
=========

The tests in this role are not specific to any one functional area.

Requirements
------------

None

Role Variables
--------------

This role should not have any default variables as this is a common role for tests that can be used for multiple test roles.

Dependencies
------------

None

Example Playbook
----------------

Typically, for this role the tests should *not* use a "main.yml" and import or include all the tests in the role. On the contrary, a tests should explicitly include specific tests needed for a given job.  

  hosts: controller
  gather_facts: no
  vars:
     proj_out_file: verify_logging_projects_exist_lresults.log
     proj_list:
       - openshift-openstack-infra
       - openshift
       - openstack-operators
       - openshift-logging

  tasks:
    - name: Remove "{{ proj_out_file }}"
      ansible.builtin.file:
        path: "{{ proj_out_file }}"
        state: absent
      changed_when: false  

    - name: Verify projects created
      ansible.builtin.include_role:
        name: qe_common
        tasks_from: proj_tests.yml
      loop: "{{ proj_list }}"
      

License
-------

Apache 2

Author Information
------------------

alexy@redhat.com

