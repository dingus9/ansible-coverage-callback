import os
import re
from setuptools import setup


READMEFILE = "README.md"
VERSIONFILE = os.path.join("callback_plugins", "coverage.py")
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
    long_description=open(READMEFILE).read(),
    url='https://github.com/leominov/ansible-coverage-callback',
    author='Lev Aminov',
    author_email='l.aminov@tinkoff.ru',
    license='MIT',
    packages=['callback_plugins'],
    install_requires=[
        'ansible>=2.4'
    ],
    include_package_data=True,
)
