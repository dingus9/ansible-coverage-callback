# ansible-coverage-callback

[![Latest version](https://img.shields.io/pypi/v/ansible-coverage-callback.svg)](https://pypi.python.org/pypi/ansible-coverage-callback/)
[![License](https://img.shields.io/badge/license-MIT-brightgreen.svg)](https://opensource.org/licenses/MIT)

Coverage Tool for Ansible.

## Requirements

* Ansible >=2.4

## Installation

Install this Ansible plugin with:

```
$ pip install ansible-coverage-callback
```

Be sure to whitelist the plugin in your `ansible.cfg`:

```
[defaults]
callback_whitelist = coverage
```

## Skip coverage tag

You may skip task or tasks from coverage report by adding `skip_coverage` tag:

```
---
- name: Test handler
  command: whoami
  when:
    - test_var == False
  tags:
    - skip_coverage
```

## Acknowledged issues

* Imported handlers has no tags, so they can't be skipped
* There is some magic hacks for skipping Molecule's system playbooks
* Tasks from non imported files are not counted
