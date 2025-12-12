Test collectd
=============

Runs some tests to ensure collectd is running as expected.
This should be run to ensure the client-side is configured correctly for STF.
Current tests are limited to "is collectd running?" and "is collectd generating any metrics?"

Requirements
------------

Role Variables
--------------

* **collectd_container_name**

  The name of the container where collectd is running, e.g. ``collectd-test``

  default: ``collectd``

* **container_bin**

  ``podman`` or ``docker``, depending on which tool is running the container.

  default: ``podman``

Dependencies
------------

Example Playbook
----------------

    - name: "Run collectd tests"
      ansible.builtin.import_role:
        name: test_collectd
      vars:
        collectd_container_name: "my_collectd"
        container_bin: docker

License
-------

Apache 2

Author Information
------------------

http://github.com/infrawatch
