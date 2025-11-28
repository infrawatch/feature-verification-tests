from ansible.plugins.callback.junit import CallbackModule as JunitCallbackModule
from ansible.plugins.callback.junit import HostData

import os
import time
import re
from ansible.utils._junit_xml import TestCase, TestError, TestFailure, TestSuite, TestSuites

DOCUMENTATION = '''
    callback: custom_junit
    type: notification
    short_description: TODO
    description:
      custom_junit generates an XML files that Polarion can read.
      Only the tasks marked with $test_case_prefix are reported.
      The first line of the task name (excluding the prefix_ is converted
      to snake_case, and this becomes the testcase name in the results file.
    options:
      test_case_prefix:
        description: todo
        ini:
          - section: custom_junit
            key: test_case_prefix
        env:
          - name: JUNIT_TEST_CASE_PREFIX
        default: "TEST"
        type: string
      classname:
        description: The classname for the tests.
        ini:
          - section: custom_junit
            key: classname
        env:
          - name: CUSTOM_JUNIT_CLASSNAME
        default: "openstack-observability"
        type: string
      output_dir:
        description: the direcory which the output files are saved to
        ini:
          - section: custom_junit
            key: output_dir
        env:
          - name: JUNIT_OUTPUT_DIR
        default: "~/ci-framework-data/tests/feature-verification-tests/"
        type: path
      debug:
        description: Whether or not to print extra debugging information
        ini:
          - section: custom_junit
            key: debug
        env:
          - name: CUSTOM_JUNIT_DEBUG
        default: false
        type: boolean
'''

class CallbackModule(JunitCallbackModule):
    """
    Custom callback that overrides the default JUnit callback
    """
    CALLBACK_NAME = 'custom_junit'

    def __init__(self):
        self._defs = None
        super(CallbackModule, self).__init__()
        self.set_options()

        # Update this to parse these values from the config file, as well as the env.
        self._output_dir = self.get_option("output_dir")
        self._test_case_prefix = self.get_option("test_case_prefix")
        self._classname = self.get_option("classname")

        self._debug = self.get_option("debug")
        self._fail_on_ignore = 'true'  # this is needed because we use "ignore_errors" on the playbooks so that all the tests are run
        self._include_setup_tasks_in_report = os.getenv('JUNIT_INCLUDE_SETUP_TASKS_IN_REPORT', 'False').lower()
        self._hide_task_arguments = os.getenv('JUNIT_HIDE_TASK_ARGUMENTS', 'True').lower()
        self._task_class = False

        if self._debug:
            print("The output_dir is: %s" % self._output_dir)
        # Ensure the output directory exists
        if not os.path.exists(self._output_dir):
            if self._debug:
                print("Creating output dir: %s" % (self._output_dir))
            os.makedirs(self._output_dir)

    def _finish_task(self, status, result):
        """ record the results of a task for a single host """
        task_uuid = result._task._uuid
        if hasattr(result, '_host'):
            host_uuid = result._host._uuid
            host_name = result._host.name
        else:
            host_uuid = 'include'
            host_name = 'include'

        task_data = self._task_data[task_uuid]

        if self._fail_on_change == 'true' and status == 'ok' and result._result.get('changed', False):
            status = 'failed'

        # ignore failure if expected and toggle result if asked for
        if status == 'failed' and 'EXPECTED FAILURE' in task_data.name:
            status = 'ok'
        elif 'TOGGLE RESULT' in task_data.name:
            if status == 'failed':
                status = 'ok'
            elif status == 'ok':
                status = 'failed'

        if self._test_case_prefix in task_data.name:
            task_data.add_host(HostData(host_uuid, host_name, status, result))

        # Debugging
        if self._debug and task_data.name.startswith(self._test_case_prefix):
            print(f"This task ({task_data.name}) starts with the test_prefix({self._test_case_prefix})")
        if self._debug and self._test_case_prefix in task_data.name:
            print(f"This task ({task_data.name}) should be reported because it contains test_prefix({self._test_case_prefix})")
        if self._debug and status == 'failed':
            print(f"This task ({task_data.name}) failed, but may not be reported")

    def mutate_task_name(self, task_name):
        # Debugging
        if self._debug and not self._test_case_prefix in task_name:
            print("task_name (%s) does not contain prefix (%s)" % (task_name, self._test_case_prefix))
        new_name = task_name
        new_name = new_name.split("\n")[0]  # only use the first line, so we can include IDs and additional description
        # this covers when a task is included, but the including task is the one that is the test
        new_name = new_name.split(":")[-1]  # only provide the last part of the name when the role name is included

        if len(self._test_case_prefix) > 0:
            # this one may not be needed...
            new_name = new_name.split(self._test_case_prefix)[-1]  # remove the test prefix and everything before it

        new_name = new_name.lower()
        new_name = re.sub(r'\W', ' ', new_name)  # replace all non-alphanumeric characters (except _) with a space
        new_name = re.sub(r'(^\W*|\W*$)', '', new_name)  # trim any trailing or leading non-alphanumeric characters
        new_name = re.sub(r' +', '_', new_name)  # replace any number of spaces with _

        return new_name

    def _build_test_case(self, task_data, host_data):
        """
           This is used in generate_report. The task_data and host data will get passed.
        """
        # Use the original task name to define the final name

        if self._debug:
            print("%s\t(task_name, pre-_build_test_case)" % task_data.name)
        tc = super()._build_test_case(task_data, host_data)
        if self._debug:
            print("%s\t(tc.name, post-_build_test_case)" % tc.name)
        tc.name = self.mutate_task_name(tc.name)

        if self._debug:
            print("%s\t(tc.name, post-mutate_task_name)" % tc.name)

        # These can be able to omit with a config option
        # These two control whether testcases contain the system_out and
        # system_err elements that show STDOUT and STDERR
        tc.system_out = None
        tc.system_err = None
        tc.classname = self._classname
        return tc
