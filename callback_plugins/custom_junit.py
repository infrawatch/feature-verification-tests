from ansible.plugins.callback.junit import CallbackModule as JunitCallbackModule
from ansible.plugins.callback.junit import HostData

import os
import time
import re
from ansible.utils._junit_xml import TestCase, TestError, TestFailure, TestSuite, TestSuites

class CallbackModule(JunitCallbackModule):
    """
    Custom callback that overrides the default JUnit callback
    """
    CALLBACK_NAME = 'custom_junit'

    def __init__(self):
        super(CallbackModule, self).__init__()
        # Custom environment variable handling
        #self._output_dir = os.getcwd()
        self._output_dir = os.path.expanduser("~/")
        self._test_case_prefix = os.getenv('JUNIT_TEST_CASE_PREFIX', 'RHOSO')
        #self._fail_on_ignore = os.getenv('JUNIT_FAIL_ON_IGNORE', 'False').lower()
        self._fail_on_ignore = 'true'
        self._include_setup_tasks_in_report = os.getenv('JUNIT_INCLUDE_SETUP_TASKS_IN_REPORT', 'False').lower()
        self._hide_task_arguments = os.getenv('JUNIT_HIDE_TASK_ARGUMENTS', 'True').lower()
        self._task_class = False

        # Ensure the output directory exists
        if not os.path.exists(self._output_dir):
            os.makedirs(self._output_dir)

    def _start_task(self, task):
        """
        Custom start task method
        """
        super(CallbackModule, self)._start_task(task)
        print(f"Starting task {task.get_name()} with custom behavior")

    def _finish_task(self, status, result):
        """
        Custom finish task method
        """
        super(CallbackModule, self)._finish_task(status, result)
        # At this point, we want to update the task.... to add if there's another matching behaviour
        # Need to add a name? task_id?
        # also update task if it CONTAINS the prefix
        task_uuid = result._task._uuid
        task_data = self._task_data[task_uuid]
        if hasattr(result, '_host'):
            host_uuid = result._host._uuid
            host_name = result._host.name
        else:
            host_uuid = 'include'
            host_name = 'include'

        if self._test_case_prefix in task_data.name or status == 'failed':
            task_data.add_host(HostData(host_uuid, host_name, status, result))

        print(f"Finishing task {result._task.get_name()} with custom behavior")

    def _build_test_case(self, task_data, host_data):
        """
           This is used in generate_report. The task_data and host data will get passed.
        """
        ## I want to test updating the name after the super class has done its thing
        tc = super()._build_test_case(task_data, host_data)

        new_name = task_data.name.lower()
        new_name = new_name.split("\n")[0]  # only use the first line, so we can include IDs and additional description

        new_name = re.sub(r'\S*%s\S*' % (self._test_case_prefix.lower()), '', new_name)  # remove the task_id i.e. the test prefix and the numeric ID that follows
        new_name = re.sub(r'(^\W*|\W*$)', '', new_name)  # trim any trailing or leading non-alphanumeric characters

        new_name = re.sub(r' +', '_', new_name)  # replace any number of spaces with _

        new_name = re.sub(r'\W', '', new_name)  # remove all non-alphanumeric characters (except _)

        tc.name = new_name

        # I don't want these properties for now; I may be able to omit them with a config option
        tc.system_out = None
        tc.system_err = None
        tc.classname = "openstack-observability"
        return tc

    def _generate_report(self):
        """
        Custom generate report method
        """
        super(CallbackModule, self)._generate_report()
        print("Generating report with custom behavior")
