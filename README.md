# ansible-coverage-callback

Coverage Tool for Ansible.

## Requirements

* Ansible >=2.4

## Installation

* Copy `callback_plugins/coverage.py` to your playbook callback directory (by default `callback_plugins/` in your playbook's root directory). Create the directory if it doesn't exist;
* Be sure to whitelist the plugin in your `ansible.cfg`:

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
