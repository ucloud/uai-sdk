#!/usr/bin/env python
# -*- coding: utf-8 -*-

import io
import os
import re

try:
    import setuptools
    setup = setuptools.setup
except ImportError:
    setuptools = None
    from distutils.core import setup

packages = ['uai', 'uai/arch', 'uai/arch_conf', 'uai/deploy', 'uai/pack', 'uai/utils', 'uai/cmd',
            'uaitrain', 'uaitrain/arch', 'uaitrain/arch/tensorflow', 'uaitrain/cmd', 'uaitrain/arch_conf', 'uaitrain/pack']


def read(*names, **kwargs):
    return io.open(
        os.path.join(os.path.dirname(__file__), *names),
        encoding=kwargs.get("encoding", "utf8")).read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


setup(
    name='uai',
    version=find_version("uai/__init__.py"),
    description='UCloud DeepLearning Python SDK',
    maintainer_email='charlie.song@ucloud.cn',
    platforms='any',
    packages=packages,
    classifiers=[
        'Intended Audience :: Developers',
        'Operating System :: OS Independent', 'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
    # install_requires=['requests==0.0.1'],
)
