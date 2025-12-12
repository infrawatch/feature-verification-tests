Test QDR
========

Runs some tests to ensure QDR is running as expected.
This should be run to ensure that client-side is configured correctly for STF.
Currently, the tests check that QDR is up and receiving any messages.

Requirements
------------

Role Variables
--------------

* **qdr_container_name**

  The name of the container where collectd is running, e.g. ``qdr-test``

  default: ``metrics_qdr``

* **container_bin**

  ``podman`` or ``docker``, depending on which tool is running the container.

  default: ``podman``


Dependencies
------------

A list of other roles hosted on Galaxy should go here, plus any details in regards to parameters that may need to be set for other roles, or variables that are used from other roles.

Example Playbook
----------------

    - name: "Run metrics_qdr tests"
      ansible.builtin.import_role:
        name: test_qdr
      vars:
        qdr_container_name: "my_messages"
        container_bin: "podman"


License
-------

Apache 2

Author Information
------------------

https://github.com/infrawatch/
