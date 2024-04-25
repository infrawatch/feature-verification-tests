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
        for host in stats.processed:
            summary = stats.summarize(host)
            self.results[host] = summary
            self._log_results(host, summary)

    def _log_results(self, host, summary):
        file_path = os.path.join(self.output_dir, f"test_run_results.log")
        with open(file_path, 'w') as f:
            f.write(f"Host: {host}\n")
            f.write(f"Tasks Succeeded: {summary['ok']}\n")
            f.write(f"Tasks Failed: {summary['failures']}\n")
            f.write(f"Tasks Skipped: {summary['skipped']}\n")
            if 'failed_task_names' in self.results[host]:
                f.write("Failed Tasks:\n")
                for task_name in self.results[host]['failed_task_names']:
                    f.write(f"  - {task_name}\n")
            if 'ok_task_names' in self.results[host]:
                f.write("Succeeded Tasks:\n")
                for task_name in self.results[host]['ok_task_names']:
                    f.write(f"  - {task_name}\n")

    def v2_runner_on_ok(self, result):
        host = result._host
        task_name = result.current_task
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
            self.results[host] = {'ok': 0, 'failures': 0, 'skipped': 0}
        if result == 'failed':
            if 'failed_task_names' not in self.results[host]:
                self.results[host]['failed_task_names'] = []
            self.results[host]['failed_task_names'].append(task_name)
        elif result == 'ok':
            if 'ok_task_names' not in self.results[host]:
                self.results[host]['ok_task_names'] = []
            self.results[host]['ok_task_names'].append(task_name)
        self.results[host][result] += 1
