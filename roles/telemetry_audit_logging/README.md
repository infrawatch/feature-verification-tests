telemetry_audit_logging
=======================

Verify that OpenStack API audit events are emitted in CADF format and forwarded
to the dedicated audit Loki stack. The scenarios follow the manual verification
steps in
[Manually enable audit logs](https://redhat.atlassian.net/wiki/spaces/CLOUDOPS/pages/389779771/Manually+enable+audit+logs).

For each OpenStack service the role:

1. Generates API activity with an ``openstack`` command
2. Checks the service API pod logs for CADF audit notifications using ``oc logs``

After all service checks, the role verifies Loki log separation using ``oc`` and
``curl`` with an OpenShift bearer token, as documented in the forwarding section:

* Default Loki (``logging-loki``) must **not** contain CADF audit events
* Audit Loki (``logging-loki-audit``) **must** contain CADF audit events

Requirements
------------

* OpenStack deployed with audit logging enabled
* Audit Loki stack and ClusterLogForwarder configured in ``openshift-logging``
* ``oc``, ``curl``, and ``openstack`` CLI access via ``openstackclient``

Service verification steps
--------------------------

+----------+---------------------------+-----------------------------------------------+
| Service  | API activity              | Pod log check                                 |
+==========+===========================+===============================================+
| Barbican | ``openstack secret list`` | ``grep barbican-api``                         |
| Cinder   | ``openstack volume list`` | ``grep cinder-api``                           |
| Glance   | ``openstack image list``  | ``grep glance-default``                       |
| Keystone | ``openstack project list``| ``oc get pod -l service=keystone ...``        |
| Neutron  | ``openstack network list``| ``grep neutron``                            |
| Nova     | ``openstack server list`` | ``grep nova-api``                             |
+----------+---------------------------+-----------------------------------------------+

Role Variables
--------------

| Variable | Default | Description |
|----------|---------|-------------|
| ``openstack_cmd`` | ``oc rsh openstackclient openstack`` | OpenStack CLI command |
| ``audit_logging_namespace`` | ``openshift-logging`` | Namespace for Loki routes |
| ``audit_logging_default_loki_route`` | ``logging-loki`` | Main Loki route name |
| ``audit_logging_loki_route`` | ``logging-loki-audit`` | Audit Loki route name |
| ``audit_logging_loki_tenant`` | ``application`` | Loki tenant in query URL |
| ``audit_logging_loki_logql_query`` | ``{log_type="application"} \|= "..."`` | LogQL query for Loki checks |
| ``audit_logging_services`` | see ``defaults/main.yml`` | List of service scenarios |

Each service entry supports:

* ``name`` - service identifier
* ``trigger_args`` - arguments passed to ``openstack_cmd``
* ``pod_pattern`` - substring used to locate the API pod
* ``pod_label_selector`` - optional ``oc get pod -l`` selector (used for Keystone)

Example Playbook
----------------

.. code-block:: yaml

  - hosts: localhost
    gather_facts: true
    environment:
      KUBECONFIG: "{{ cifmw_openshift_kubeconfig }}"
      PATH: "{{ cifmw_path }}"
    vars_files:
      - vars/osp18_env.yml
    tasks:
      - name: "Run audit logging service tests"
        ansible.builtin.import_role:
          name: telemetry_audit_logging

License
-------

Apache 2
