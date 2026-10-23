Feature-verification-tests are made up of two parts: tests and callback plugins.

The callback plugins output the test results in different ways.
The custom_logger plugin takes a test-id from the task names and reports the results of the tests in a file, where each line contains a test ID and a result (pass/fail).
The custom_junit plugin extends the standard ansible junit plugin and report in XML format that Polarion expects.


The tests are for STF and for telemetry services in RHOSO.

STF tests
These are the functional tests for stf. They check that OpenStack components are running and connected to STF and that the system works end-to-end.
They are based on an infrared depoyment.

RHOSO telemetry tests
These tests cover telemetry features in RHOSO-18. These tests check that the telemetry-operator has deployed and configured the required services as expected.


Running the tests locally
=========================

The playbooks in ``ci/`` are run by ci-framework in CI, but they can also be
run directly against any reachable cluster. Everything that CI normally
supplies (``cifmw_openshift_kubeconfig``, ``cifmw_path``, ``cifmw_basedir``,
``cifmw_openshift_user``/``cifmw_openshift_password``, the ``zuul`` variables)
has a local fallback in ``ci/vars/defaults.yml``, so no extra variables are
needed for the common cases. Anything CI does pass still takes precedence.

Prerequisites:

* ``oc`` on ``PATH``, and a kubeconfig for a logged-in cluster. ``KUBECONFIG``
  is used if set, otherwise ``~/.kube/config``.
* RHOSO deployed in the ``openstack`` namespace with an ``openstackclient`` pod.
* ``OCP_PASSWORD`` exported for the graphing tests (the console login).

Run a playbook with the helper script, which supplies the sample inventory::

    ci/run_functional_tests_locally.sh run_verify_metrics_osp18.yml
    ci/run_functional_tests_locally.sh run_verify_metrics_osp18.yml --tags precheck
    ci/run_functional_tests_locally.sh run_chargeback_tests.yml

or call ``ansible-playbook`` from the ``ci`` directory, so that ``ci/ansible.cfg``
is picked up::

    cd ci
    ansible-playbook -i inventory/local.yml run_verify_metrics_osp18.yml

Local behaviour differences:

* Artifacts and results are written under ``~/ci-framework-data`` unless
  ``cifmw_basedir`` is set.
* ``{{ cifmw_basedir }}/artifacts/parameters`` is only loaded when it exists.
* The autoscaling play does not create the instance it scales from. Create it
  yourself, or pass ``-e fvt_create_test_vm=true -e install_yamls_dir=<path>``
  to have it run ``make edpm_deploy_instance`` from an install_yamls checkout.
* The compute-node logging tests (``logging_tests_computes.yml``) need real
  EDPM hosts; add them to the ``computes`` group in ``ci/inventory/local.yml``.
* The container-registry variables in ``ci/vars/common.yml`` only apply to the
  Zuul content provider and fall back to the default registry locally.


