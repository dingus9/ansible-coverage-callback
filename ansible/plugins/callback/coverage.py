# -*- coding: utf-8 -*-
"""
Simple Ansible coverage callback
(c) Lev Aminov <l.aminov@tinkoff.ru>
"""

__metaclass__ = type

import os
import json

import yaml

from ansible import constants as C
from ansible.utils.color import colorize
from ansible.plugins.callback import CallbackBase


class CallbackModule(CallbackBase):
    """
    Ansible callback
    ref: https://docs.ansible.com/ansible/2.5/dev_guide/developing_plugins.html
    ref: https://docs.ansible.com/ansible/2.6/plugins/callback.html
    """
    CALLBACK_VERSION = '1.0.2'
    CALLBACK_TYPE = 'aggregate'
    CALLBACK_NAME = 'coverage'
    CALLBACK_NEEDS_WHITELIST = True
    COVERAGE_FILE_PATH = '.coverage_ansible'

    MOLECULE_ENV_CURSOR = 'MOLECULE_SCENARIO_NAME'

    RUN_STATES = ('changed', 'ok', 'failed')
    NOT_RUN_STATES = ('skipped', 'unreachable', 'no_hosts')

    def __init__(self):
        super(CallbackModule, self).__init__()
        self.molecule_env = False
        self.ignored_molecule_scenarios = [
            'destroy',
            'create',
            'prepare',
            'verify',
            'side_effect'
        ]

        self.playbook_name = ""
        self.scenario_name = ""
        self.total_tasks = 0
        self.executed_tasks = 0
        self.coverage = 0.0
        self._result = {}

    def _register_task(self, result, status):
        assert status in ('skipped', 'unreachable', 'no_hosts', 'ok', 'failed'), (
            'Unhandled coverage task status type {status}'.format(status=status))
        if 'skip_coverage' in result._task.tags:
            return

        task_name = result._task.get_name().strip()
        if task_name == 'Gathering Facts':
            return

        if task_name not in self._result:
            self._result[task_name] = (result, status)

    def _prints_calls(self):
        for task_name in self._result:
            result = self._result[task_name][1] in self.RUN_STATES
            task_color = None
            if result:
                msg = u"{0:-<{2}}{1:->9}".format(task_name + u' ', u' changed', self._display.columns - 9)
            else:
                task_color = C.COLOR_SKIP
                msg = u"{0:-<{2}}{1:->9}".format(task_name + u' ', u' skipped', self._display.columns - 9)
            self._display.display(msg, task_color)

    def _prints_report(self):
        coverage_color = C.COLOR_ERROR
        unreachable_color = coverage_color
        if self.total_tasks == self.executed_tasks:
            coverage_color = C.COLOR_OK
            unreachable_color = None

        num_unreachable_tasks = self.total_tasks-self.executed_tasks
        self._display.banner('COVERAGE')
        self._prints_calls()
        self._display.display(u"%-26s : %s %s %s %s" % (
            self.playbook_name,
            colorize(u'coverage', '%.0f' % self.coverage, coverage_color),
            colorize(u'ok', self.total_tasks, C.COLOR_OK),
            colorize(u'changed', self.executed_tasks, C.COLOR_CHANGED),
            colorize(u'unreachable', num_unreachable_tasks, unreachable_color)
            ), screen_only=True)

        self._display.display("", screen_only=True)

    def _aggregate_counters(self, stats):

        for task_name in self._result:
            result = self._result[task_name]
            self.total_tasks += 1

            if result[1] in self.RUN_STATES:
                self.executed_tasks += 1

        if self.executed_tasks > 0:
            self.coverage = self.executed_tasks * 100.0 / self.total_tasks

    def _export_stats(self):

        if self.molecule_env:
            target = self.scenario_name + '.' + self.playbook_name
        else:
            target = self.playbook_name

        current_cov = {'total_coverage': self.coverage,
                       'executed_tasks': self.executed_tasks,
                       'total_tasks': self.total_tasks,
                       'playbook_name': self.playbook_name,
                       'tasks': [(name, val[1]) for name, val in self._result.items()]}

        with open(self.COVERAGE_FILE_PATH, 'a+') as cov_report:
            try:
                cov_report.seek(0)
                report = json.load(cov_report)
            except Exception:
                report = {}

            if target in report:
                combine = report[target]
                combine.append(current_cov)
            else:
                report[target] = [current_cov]

            cov_report.seek(0)
            cov_report.truncate()
            json.dump(report,
                      cov_report)

    def v2_playbook_on_start(self, playbook):
        if self.MOLECULE_ENV_CURSOR in os.environ:
            self.molecule_env = True
            self.scenario_name = self._get_molecule_scenario(os.environ['MOLECULE_FILE'])['name']
            playbooks = self._get_molecule_playbooks(os.environ['MOLECULE_FILE'])

            if os.path.sep in playbook._file_name:
                pb_name = os.path.basename(playbook._file_name)
                pb_map = {os.path.basename(val): key for key, val in playbooks.items()}
                if pb_name in pb_map:
                    self.playbook_name = pb_map[pb_name]
        else:
            self.playbook_name = os.path.splitext(os.path.basename(playbook._file_name))[0]

    def v2_runner_on_skipped(self, result, **kwargs):
        self._register_task(result, 'skipped')

    def v2_runner_on_ok(self, result, **kwargs):
        self._register_task(result, 'ok')

    def v2_runner_on_failed(self, result, **kwargs):
        self._register_task(result, 'failed')

    def v2_runner_on_unreachable(self, result, **kwargs):
        self._register_task(result, 'unreachable')

    def v2_runner_on_no_hosts(self, result, **kwargs):
        self._register_task(result, 'hosts')

    def v2_playbook_on_stats(self, stats):
        if self.playbook_name in self.ignored_molecule_scenarios:
            return
        self._aggregate_counters(stats)
        if self.total_tasks > 0:
            self._export_stats()

    def _get_molecule_playbooks(self, molecule_file):
        with open(molecule_file, 'r') as mfile:
            contents = yaml.safe_load(mfile)

        return contents['provisioner']['playbooks']

    def _get_molecule_scenario(self, molecule_file):
        with open(molecule_file, 'r') as mfile:
            contents = yaml.safe_load(mfile)

        return contents['scenario']
