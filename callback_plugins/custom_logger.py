from ansible.plugins.callback import CallbackBase
import os

class CallbackModule(CallbackBase):

    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'notification'
    CALLBACK_NAME = 'log_to_file'
    CALLBACK_NEEDS_WHITELIST = True

    def __init__(self):
        super(CallbackModule, self).__init__()
        self.output_dir = os.getcwd()
        self.results = {}

    def playbook_on_stats(self, stats):
        # Log results for each host
        hosts= stats.processed
        for host in hosts:
            self._log_results(host)
        self._summary_results(hosts)

    def _summary_results(self, hosts):
        file_path = os.path.join(self.output_dir, f"test_run_result.out")
        for host in hosts:
            with open(file_path, 'w') as f:
                f.write(f"Host: {host}\n")
                f.write(f"Tasks Succeeded: {self.results[host]['ok']}\n")
                f.write(f"Tasks Failed: {self.results[host]['failed']}\n")
                f.write(f"Tasks Skipped: {self.results[host]['skipped']}\n")
                f.write(f"More Details: {host}_results.log\n" )

    def _log_results(self, host):
        file_path = os.path.join(self.output_dir, f"{host}_results.log")
        with open(file_path, 'w') as f:
            f.write(f"Host: {host}\n")
            f.write(f"Tasks Succeeded: {self.results[host]['ok']}\n")
            f.write(f"Tasks Failed: {self.results[host]['failed']}\n")
            f.write(f"Tasks Skipped: {self.results[host]['skipped']}\n")
            f.write("Failed Tasks:\n")
            for task_name in self.results[host]['failed_task_names']:
                f.write(f"  - {task_name}\n")
            f.write("Succeeded Tasks:\n")
            for task_name in self.results[host]['ok_task_names']:
                f.write(f"  - {task_name}\n")

    def v2_runner_on_ok(self, result):
        host = result._host.get_name()
        task_name = result._task.get_name()
        self._log_task_result(host, 'ok', task_name)

    def v2_runner_on_failed(self, result, ignore_errors=False):
        host = result._host.get_name()
        task_name = result._task.get_name()
        self._log_task_result(host, 'failed', task_name)

    def v2_runner_on_skipped(self, result):
        host = result._host.get_name()
        task_name = result._task.get_name()
        self._log_task_result(host, 'skipped', task_name)

    def _log_task_result(self, host, result, task_name):
        if host not in self.results:
            self.results[host] = {'ok': 0, 'failed': 0, 'skipped': 0, 'failed_task_names':[], 'ok_task_names':[] }
        if result == 'failed':
            self.results[host]['failed_task_names'].append(task_name)
        elif result == 'ok':
            self.results[host]['ok_task_names'].append(task_name)
        self.results[host][result] += 1