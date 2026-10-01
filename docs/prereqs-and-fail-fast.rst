Pre-requisites and failing fast
===============================

Most checks in this repo depend on something else having worked first. A
metric can only be queried if the ``openstackclient`` pod is reachable; a
stack can only scale if it was created; it could only be created if the heat
templates were rendered.

When a shared pre-requisite is broken, every dependent check fails - but each
one works through its own retry budget first. A ``retries: 10`` with
``delay: 30`` is five minutes, and there are dozens of them, so the suite can
spend hours arriving at a verdict it could have reached in seconds.

The naive fix is to skip the dependent checks. Don't: a skipped task produces
no JUnit testcase, so the check disappears from the report and the run looks
smaller rather than broken.

The rule
--------

**A check whose pre-requisites were not met must still fail, and must say why.**

Three things have to hold:

* the check is still *reported* - the ``TEST`` task runs and the callback emits
  a testcase for it;
* the testcase is a *failure*, not a skip or an omission;
* the failure message says the check was **blocked**, so nobody debugs a
  symptom when they should be debugging the cause.

The pattern
-----------

Split each check into two tasks: an unnamed-for-reporting *gather* that does
the work, and a ``TEST``-prefixed *assert* that reports it.

Declare one cumulative flag and one blocked message in the role's
``defaults/main.yml``::

    myrole_prereqs_ok: true
    myrole_blocked_msg: >-
      BLOCKED: <what failed earlier>, so this check was not attempted

Gate the gather on the flag, and let the assert run unconditionally::

    - name: Query the node exporter build info metric
      when: myrole_prereqs_ok | bool
      ansible.builtin.shell: |
        {{ openstack_cmd }} metric show --disable-rbac node_exporter_build_info
      register: build_info_metric
      delay: 30
      retries: 10
      changed_when: false
      ignore_errors: true
      until: build_info_metric.rc == 0 and "node_exporter_build_info" in build_info_metric.stdout

    - name: |
        TEST Use openstack observabilityclient to verify Node Exporter metrics are stored in prometheus
      ansible.builtin.assert:
        that:
          - build_info_metric is not skipped
          - build_info_metric is not failed
        success_msg: "node_exporter_build_info is stored in prometheus"
        fail_msg: >-
          {{ (build_info_metric is not skipped)
             | ternary('node_exporter_build_info was not found in prometheus',
                       myrole_blocked_msg) }}

A task skipped by ``when:`` still registers its variable with
``skipped: true``, which is what makes the two cases distinguishable:
``is skipped`` means the gather never ran, so the failure is *blocked*;
``is failed`` means it ran and the thing really is wrong.

Latching the flag
-----------------

The flag only ever goes from true to false, and it is set from the result of a
check that other checks depend on::

    - name: Record whether the stack was created
      ansible.builtin.set_fact:
        myrole_prereqs_ok: "{{ myrole_prereqs_ok | bool and not (test_stack_create is failed) }}"

Where the gather is a block that needs a ``rescue:``, override the inherited
``ignore_errors``::

    - name: Check that metrics can be queried from Prometheus
      ignore_errors: false
      block:
        - name: Query the Prometheus up metric
          ...
      rescue:
        - name: Record that metrics cannot be queried from Prometheus
          ansible.builtin.set_fact:
            myrole_prereqs_ok: false

Rules of thumb
--------------

**One cumulative flag per role, not one per stage.** The dependency chain in
these roles is linear - heat config, then stack creation, then scale up, then
scale down - so a single latch expresses it. Per-stage flags multiply without
saying anything extra.

**Independent peers get their own flag.** The metric sources in
``telemetry_verify_metrics`` are peers: ``volume_pool`` failing says nothing
about ``node_exporter``. A per-source failure latches a source-local flag
(``volume_pool_ok``, ``central_ok``, ``compute_ok``) and never the shared one,
or one bad source blocks every source that happens to run after it.

**Gate on the cheapest thing that proves the path works.** In
``telemetry_verify_metrics`` that is a single ``openstack metric query up``.
Resist gating on anything richer: a custom resource that is not ``Ready``
does *not* break the query path, it makes particular metrics missing, which is
a legitimate per-source failure and should be reported as one.

**Keep ``TEST`` task names byte-identical when refactoring.** They are the
testcase names in the JUnit XML and the mapping into Polarion. Move the work
out from under the name; don't move the name.

**Tag the gate for every tag that can select the checks it guards.** The
shared probe in ``telemetry_verify_metrics`` carries both ``precheck`` and
``test``, because ``--tags test`` still needs it. When neither tag is
selected the flag keeps its default of ``true`` and nothing changes.

Gotchas
-------

**Never put a ``TEST`` prefix on an ``include_tasks``.** ``custom_junit``
records an include as an ``included`` event, which renders as a *passing*
testcase no matter what happens inside it. Name the include plainly and let
the tasks within it report themselves.

**``ignore_errors: true`` on ``import_role`` propagates to every task in the
role**, and a task whose error is ignored does not trigger ``rescue:``. The CI
playbooks import these roles that way, so any block that relies on its rescue
has to set ``ignore_errors: false`` on itself.

**A failing item aborts the rest of the loop.** The later items never run and
produce no result, so one loop cannot feed several separate testcases. If you
need five testcases, write five gather/assert pairs.

**Jinja's ``ternary`` evaluates both branches.** Guard sub-attribute
references in ``fail_msg`` with ``| default()`` or the message blows up on the
very runs where you need to read it.

**``assert`` short-circuits at the first false condition in ``that:``.** The
parent JUnit callback takes ``<failure message=...>`` from ``result.msg``,
which ``assert`` sets from ``fail_msg``, so the ordering of conditions decides
which message a reader sees.

Naming the blocked failure
--------------------------

Start the message with ``BLOCKED:`` and name the cause, not the symptom::

    BLOCKED: metrics could not be queried from Prometheus, so this check was not attempted
    BLOCKED: an earlier autoscaling stage failed, so this check was not attempted

Where a check can be blocked for more than one reason, say which::

    - name: Set the blocked message for the compute metric checks
      ansible.builtin.set_fact:
        compute_blocked_msg: >-
          {{ verify_metrics_prereqs_ok | bool
             | ternary('BLOCKED: the test instance for ceilometer compute metrics was not created or stopped successfully',
                       verify_metrics_blocked_msg) }}

Testing it
----------

The gates only fire when the environment is broken, so on a healthy deployment
they are dead code and no normal job exercises them. ``ci/run_fail_fast_demo.yml``
breaks the environment on purpose and asserts that the suite still behaves:
it finished inside its budget, at least one testcase carries a ``BLOCKED``
reason, and nothing was silently skipped. Fault profiles live in
``ci/vars/fault_injection.yml``; the default,
``unreachable_openstackclient``, only redirects ``openstack_cmd`` and touches
nothing on the cluster::

    ansible-playbook -i inventory ci/run_fail_fast_demo.yml
    ansible-playbook -i inventory ci/run_fail_fast_demo.yml -e fvt_fault=prometheus_down

To measure what the gates save, run the same thing with the flags forced true
on the command line. Extra vars outrank ``set_fact``, so every latch becomes a
no-op and the roles behave as they did before::

    ansible-playbook -i inventory ci/run_fail_fast_demo.yml \
      -e fvt_fail_fast_baseline=true \
      -e autoscaling_prereqs_ok=true -e verify_metrics_prereqs_ok=true

That baseline takes hours. Keep it out of gate jobs.
