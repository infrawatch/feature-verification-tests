from __future__ import (absolute_import, division, print_function)
#__metaclass__ = type

import os

from ansible.plugins.callback import CallbackBase

DOCUMENTATION = '''
    callback: log_to_file
    type: notification
    short_description: output logs to a file
    description:
        - This summarises tasks per host and outputs it to a log file
'''

class CallbackModule(CallbackBase):
    """
    logs playbook results, per host, in /var/log/ansible/hosts
    """
    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'notification'
    CALLBACK_NAME = 'log_to_file'
    CALLBACK_NEEDS_WHITELIST = True

    MSG_FORMAT = "{task}={status}\n"

    def __init__(self):

        super(CallbackModule, self).__init__()
        self.current_task = ''
        self.passed = 0
        self.failed = 0
        self.output_dir = os.getcwd()
        self.path = os.path.join(self.output_dir, "test_run_result.out")
        # either create the file or truncate the existing file
        with open(self.path, 'w') as fp:
            pass

    def playbook_on_task_start(self, task, is_conditional):
        self.current_task = str(task)

#    def playbook_on_stats(self, stats):
#        with open(self.path, 'a') as fd:
#            fd.write("passed: {}\n".format(self.passed))
#            fd.write("failed: {}\n".format(self.failed))

    def log(self, host, category):
         # only interested in the test tasks, not setup or debug
         if self.current_task.startswith("RHELOSP") or self.current_task.startswith("RHOSO"):

             if category == "failed":
                self.failed +=1
             if category == "passed":
                 self.passed +=1

             test_result_message = self.MSG_FORMAT.format(task=self.current_task, status=category)

             with open(self.path, 'a') as fd:
                 fd.write(test_result_message)

             file_name = "_".join(["test_run_result", host])
             with open(os.path.join(self.output_dir, file_name ) , 'a') as fd:
                 fd.write(test_result_message)

    def runner_on_failed(self, host, res, ignore_errors=False):
         self.log(host,'failed')

    def runner_on_ok(self, host, res):
         self.log(host,'passed')

    def runner_on_skipped(self, host, res, item=None):
         self.log(host, 'skipped')
