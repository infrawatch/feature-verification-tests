These are the functional tests for stf client-side. They check that OpenStack is running.

The deployment templates are in infrared, and have the following names:

 - 'collectd-write-qdr-edge-only'
 - 'collectd-write-qdr-mesh'
 - 'ceilometer-write-qdr-edge-only'
 - 'ceilometer-write-qdr-mesh'
 - 'enable-stf'

The tags for the ansible playbook correspond to these templates and run the appropriate tests for each deployment.

The current set of functional tests are:

 - Check collectd is running
   This checks that the collectd container has been deployed and is generating ANY metrics
   The test currently runs when the ``collectd-*`` tags are passed.

 - Check QDR is running
   This checks that the ``metrics_qdr`` container has been deployed and is receiving ANY metrics
   This test runs when the ``*-write-qdr-*`` tags are passed.


Running tests locally
---------------------

If you have deployed client-side STF and want to test it locally, you can run the following command::

    ansible-playbook -i `infrared workspace inventory` stf_functional_tests.yml

OR

    ansible-playbook -i `infrared workspace inventory` stf_functional_tests.yml --tags "<one of the tags from above>"

To get a summarised output of the tests at the end, whitelist the provided logging callback.::

    ANSIBLE_CALLBACK_WHITELIST=custom_logger ansible-playbook -i `infrared workspace inventory` stf_functional_tests.yml

The logging callback will summarise the tests run on each node and whether they passes or failed.
The callback will only report on the status of tasks that have a name beinging with "[Test]".

Note::
    If you haven't deployed using infrared, you can still run the tests if you create your own inventory file, containing one group of hosts called ``overcloud_nodes``.
    Alternatively, you can create your own playbook that imports the tasks in ``tasks/*.yml``

Adding new tests
----------------

Adding a new test for existing deployment templates requires no changes in
Jenkins.
Adding tests for new deployment templates requires that the template is in
Infrared and deployed in Jenkins.

The changes required in this repo for tests is to add additional tasks under
``tasks/test_<your_test_name>.yml``.

```
     - name: "[Test] My test name"
       shell: |
           my_test_command
       register: command_output
       failed_when: command_output.stdout == some_value

```

Most of the functional tests are a series of shell commands that one would run
when verifying that particular features were deployed correctly, and can be
adapted from any manual testing that is done.


The task can then be imported in ``stf_functional_tests.yml`` like so::

```
    - name: Collectd checks
      hosts: overcloud_nodes
      become: true
      tags:
        - collectd-write-qdr-edge-only
        - collectd-write-qdr-mesh
        - some-other-template-name
      tasks:
        - import_tasks: tasks/test_<your_test_name>

```


Configuration
-------------
The following vars can be passed to change the behaviour.

* collectd_container_name
  The name of the container where collectd is running, e.g. ``collectd-test``
  default: ``collectd``

* qdr_container_name
  The name of the container where qdr is running, e.g. ``metrics_qdr``, ``qdr-test``
  default: ``metrics_qdr``
