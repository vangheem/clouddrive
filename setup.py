# -*- coding: utf-8 -*-

import os

from setuptools import setup
from setuptools import find_packages


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()


setup(
    name='clouddrive',
    version='0.1.dev0',
    description='',
    long_description='',
    classifiers=[
        "Programming Language :: Python",
    ],
    author='Nathan Van Gheem',
    author_email='nathan@vangheem.us',
    url='',
    license='BSD',
    packages=find_packages(exclude=['ez_setup']),
    install_requires=[
        'requests',
        'flask',
        'ZEO',
        'ZODB',
        'python-dateutil'
    ],
    entry_points="""
      # -*- Entry points: -*-

      [console_scripts]
      run-server = clouddrive:run_server
      run-monitor = clouddrive.monitor:run
      """,
    include_package_data=True,
    zip_safe=False,
)
