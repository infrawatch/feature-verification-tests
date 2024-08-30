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
        # self._output_dir = os.getcwd()
        # Update this to parse these values from the config file, as well as the env.
        self._output_dir = os.path.expanduser("~/.ansible.log")
        self._test_case_prefix = os.getenv('JUNIT_TEST_CASE_PREFIX', '[TEST]')
        #self._fail_on_ignore = os.getenv('JUNIT_FAIL_ON_IGNORE', 'False').lower()
        self._fail_on_ignore = 'true'  # this is needed because we use "ignore_errors" on the playbooks so that all the tests are run
        self._include_setup_tasks_in_report = os.getenv('JUNIT_INCLUDE_SETUP_TASKS_IN_REPORT', 'False').lower()
        self._hide_task_arguments = os.getenv('JUNIT_HIDE_TASK_ARGUMENTS', 'True').lower()
        self._task_class = False

        print("The output_dir is: %s" % self._output_dir)
        # Ensure the output directory exists
        if not os.path.exists(self._output_dir):
            print("Creating output dir: %s" % (self._output_dir))
            os.makedirs(self._output_dir)

    # Don't need this. since we're going to be filtering on the [TEST] prefix (or similar), which will be at the start of the taskname
    # If the prefix is at the start of the name, we can filter on that, and remove anything that comes before it (e.g. if a tasks comes from an included role, then "role_name :" is prefixed
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

        if self._test_case_prefix in task_data.name:
            task_data.add_host(HostData(host_uuid, host_name, status, result))

    def mutate_task_name(self, task_name):

        print("enter mutate_task_name(task_name=%s" % task_name)

        new_name = task_name
        new_name = new_name.split("\n")[0]  # only use the first line, so we can include IDs and additional description
        print(new_name)

        # this cover when a task is included, but the including task is the one that is the test
        new_name = new_name.split(":")[-1]  # only provide the last part of the name when the role name is included
        print("%s\t(split at :, take last element)" % new_name)

        # this one may not be needed...
        new_name = re.sub(r'^.*?\S*%s\S*' % (self._test_case_prefix), '', new_name)  # remove the test prefix and everything before it
        print("%s\t(remove test prefix)" % new_name)

        new_name = new_name.lower()
        print("%s\t(lowercase)" % new_name)

        new_name = re.sub(r'\W', ' ', new_name)  # replace all non-alphanumeric characters (except _) with a space
        print("%s (Replace non-alphanumerics with a space)" % new_name)

        new_name = re.sub(r'(^\W*|\W*$)', '', new_name)  # trim any trailing or leading non-alphanumeric characters
        print("%s\t(trim leading or trailing characters" % new_name)

        new_name = re.sub(r' +', '_', new_name)  # replace any number of spaces with _
        print("%s\t(spaces -> _)" % new_name)

        #print(new_name == task_name)
        print("exit mutate_task_name")
        return new_name

    def _build_test_case(self, task_data, host_data):
        """
           This is used in generate_report. The task_data and host data will get passed.
        """
        ## I want to test updating the name after the super class has done its thing
        print("What is the task name prior to running super?\n\t%s" % task_data.name)

        # Use the original task name to define the final name
        new_name = self.mutate_task_name(task_data.name)

        tc = super()._build_test_case(task_data, host_data)

        tc.name = new_name

        print("%s\t(tc.name)" % tc.name)

        # I don't want these properties for now; I may be able to omit them with a config option
        tc.system_out = None
        tc.system_err = None
        tc.classname = "openstack-observability"
        return tc

