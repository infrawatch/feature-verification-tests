from ansible.plugins.callback import CallbackModule as OriginalCallbackModule
import os
import time
import re
from ansible import constants as C
from ansible.module_utils._text import to_bytes, to_text
from ansible.utils._junit_xml import TestCase, TestError, TestFailure, TestSuite, TestSuites

class CustomCallbackModule(OriginalCallbackModule):
    """
    Custom callback that overrides the default JUnit callback
    """
    CALLBACK_NAME = 'custom_junit'

    def __init__(self):
        super(CustomCallbackModule, self).__init__()

        # Custom environment variable handling
        self._output_dir = os.getcwd()
        self._test_case_prefix = os.getenv('JUNIT_TEST_CASE_PREFIX', 'RHOSO')
        self._fail_on_ignore = os.getenv('JUNIT_FAIL_ON_IGNORE', 'False').lower()
        self._include_setup_tasks_in_report = os.getenv('JUNIT_INCLUDE_SETUP_TASKS_IN_REPORT', 'False').lower()
        self._hide_task_arguments = os.getenv('JUNIT_HIDE_TASK_ARGUMENTS', 'True').lower()


        # Ensure the output directory exists
        if not os.path.exists(self._output_dir):
            os.makedirs(self._output_dir)

    def _start_task(self, task):
        """
        Custom start task method
        """
        super(CustomCallbackModule, self)._start_task(task)
        print(f"Starting task {task.get_name()} with custom behavior")

    def _finish_task(self, status, result):
        """
        Custom finish task method
        """
        super(CustomCallbackModule, self)._finish_task(status, result)
        print(f"Finishing task {result._task.get_name()} with custom behavior")

    def _generate_report(self):
        """
        Custom generate report method
        """
        super(CustomCallbackModule, self)._generate_report()
        print("Generating report with custom behavior")
