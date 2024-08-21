from __future__ import (absolute_import, division, print_function)
#__metaclass__ = type

import os
import re


from ansible.errors import AnsibleCallbackError
from ansible.errors import AnsibleError
from ansible.plugins.callback import CallbackBase

DOCUMENTATION = '''
    callback: log_to_file
    type: notification
    short_description: output logs to a file
    description:
    - This callback function creates two log files for each host.
        - The first log file records the result (pass/fail) for each task executed on the host.
        - The second log file contains a summary of all tasks executed on the host, including their results.
    - Log file names:
        - test_run_result.out
        - summary_results.log
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
        self.output_dir =  os.path.expanduser("~/")
        self.results = {}
        
    def v2_playbook_on_stats(self, stats):
        #Log results for each host
        hosts= stats.processed
        for host in hosts:
            self.log_summary_results(host)

    def log_task_result(self, host, result, task_name):
        print("logging task result: %s - %s - %s" % (host, result, task_name))
        # test_run_result.out only interested in the test tasks, not setup or debug.
        if "RHELOSP" in task_name or "RHOSO" in task_name:
            if "RHELOSP" in task_name:
                test_id = re.search(r'RHELOSP\S*', task_name).group(0)
            elif "RHOSO" in task_name:
                test_id = re.search(r'RHOSO\S*', task_name).group(0)

            file_path = os.path.join(self.output_dir, f"test_run_result.out")
            test_result_message = self.MSG_FORMAT.format(task=test_id, status=result)
            with open(file_path, 'a') as f:
                f.write(test_result_message)

            # Gather the result data to be used in the summary log.
            if host not in self.results:
                print("host was not in results, adding a new value to self.results")
                self.results[host] = {'passed': 0, 'failed': 0, 'skipped': 0, 'failed_task_names':[], 'ok_task_names':[] }
            if result == 'failed':
                self.results[host]['failed_task_names'].append(task_name)
            elif result == 'passed':
                self.results[host]['ok_task_names'].append(task_name)
            self.results[host][result] += 1

    def log_summary_results(self, host):
        # The issue is presenting itself in this method
        file_path = os.path.join(self.output_dir, f"summary_results.log")
        print("Writing results to %s" % file_path)
        # temperorily add more detail to the output
        print(self.results)

        with open(file_path, 'w') as f:
            f.write(f"Host: {host}\n")
            # This is the failed issue.
            # Why is it happening?
            # Unknown. But does it happen for the other values.
            # It is happening for compute-0
            # I need to see the partial log file, so this should NOT cause a failure.
            # try/catch ANY exception
            # It could be a nice upgrade to use jinja2 template to render this file.
            # IS the issue that there were 'f's preceeding the strings?
            try:
                f.write("Tasks Succeeded: {self.results[host]['passed']}\n")
                f.write("Tasks Failed: {self.results[host]['failed']}\n")
                f.write("Tasks Skipped: {self.results[host]['skipped']}\n")
                f.write("Failed Tasks:\n")
                for task_name in self.results[host]['failed_task_names']:
                    f.write(f"  - {task_name}\n")
                f.write("Succeeded Tasks:\n")
                for task_name in self.results[host]['ok_task_names']:
                    f.write(f"  - {task_name}\n")
            except AnsibleError as e:
                # this is probably an AnsibleCallbackError
                print("Ooops, there was an error")
                print(e)

    def v2_runner_on_ok(self, result):
        host = result._host.get_name()
        task_name = result._task.get_name()
        self.log_task_result(host, 'passed', task_name)

    def v2_runner_on_failed(self, result, ignore_errors=False):
        host = result._host.get_name()
        task_name = result._task.get_name()
        self.log_task_result(host, 'failed', task_name)

    def v2_runner_on_skipped(self, result):
        host = result._host.get_name()
        task_name = result._task.get_name()
        self.log_task_result(host, 'skipped', task_name)
