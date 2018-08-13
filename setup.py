import os
import re

from os import path
from setuptools import setup


VERSIONFILE = path.join("ansible", "plugins", "callback", "coverage.py")
VSRE = r"CALLBACK\_VERSION\s\=\s['\"]([^'\"]*)['\"]"


def get_version():
    verstrline = open(VERSIONFILE, "rt").read()
    re_result = re.search(VSRE, verstrline, re.M)
    if re_result:
        return re_result.group(1)
    else:
        raise RuntimeError(
            "Unable to find version string in %s." % VERSIONFILE)

setup(
    name='ansible-coverage-callback',
    version=get_version(),
    description='Simple Ansible Coverage callback',
    long_description=open('README.md').read(),
    url='https://github.com/leominov/ansible-coverage-callback',
    author='Lev Aminov',
    author_email='l.aminov@tinkoff.ru',
    license='MIT',
    py_modules=[
        'ansible/plugins/callback/coverage'
    ],
    install_requires=[
        'ansible>=2.4'
    ]
)
