# -*- coding: utf-8 -*-
"""
Simple Ansible coverage callback
(c) Lev Aminov <l.aminov@tinkoff.ru>
"""

__metaclass__ = type

from ansible import constants as C
from ansible.utils.color import colorize
from ansible.plugins.callback import CallbackBase


class CallbackModule(CallbackBase):
    """
    Ansible callback
    ref: https://docs.ansible.com/ansible/2.5/dev_guide/developing_plugins.html
    ref: https://docs.ansible.com/ansible/2.6/plugins/callback.html
    """
    CALLBACK_VERSION = '1.0.0'
    CALLBACK_TYPE = 'aggregate'
    CALLBACK_NAME = 'coverage'
    CALLBACK_NEEDS_WHITELIST = True

    def __init__(self):
        super(CallbackModule, self).__init__()

        self.num_tested_tasks = 0
        self.num_changed_tasks = 0
        self.coverage = 0.0
        self._result = {}

    def _register_task(self, result, skipped):
        if 'skip_coverage' in result._task.tags:
            return

        task_name = result._task.get_name().strip()
        if task_name == 'Gathering Facts':
            return

        if task_name not in self._result:
            self._result[task_name] = False

        if skipped:
            return

        if result._result.get('changed', True):
            self._result[task_name] = True

    def _prints_report(self):
        if self.num_tested_tasks == self.num_changed_tasks:
            color = C.COLOR_OK
        else:
            color = C.COLOR_ERROR

        self._display.banner('COVERAGE')
        self._display.display(u"report : %s %s %s" % (
            colorize(u'coverage', '%.0f' % self.coverage, color),
            colorize(u'ok', self.num_tested_tasks, C.COLOR_OK),
            colorize(u'changed', self.num_changed_tasks, None)
            ), screen_only=True)

    def _aggregate_counters(self, stats):
        hosts = sorted(stats.processed.keys())
        for h in hosts:
            s = stats.summarize(h)
            if s['failures'] > 0:
                return
            if s['unreachable'] > 0:
                return

        for task_name in self._result:
            result = self._result[task_name]
            self.num_tested_tasks += 1
            if result:
                self.num_changed_tasks += 1

        if self.num_changed_tasks > 0:
            self.coverage = self.num_changed_tasks * 100.0 / self.num_tested_tasks

    def v2_runner_on_skipped(self, result):
        self._register_task(result, True)

    def v2_runner_on_ok(self, result):
        self._register_task(result, False)

    def v2_playbook_on_stats(self, stats):
        self._aggregate_counters(stats)
        if self.coverage > 0.0:
            self._prints_report()
