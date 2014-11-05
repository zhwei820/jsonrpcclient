#!/usr/bin/env python
"""setup.py"""

from distutils.core import setup

setup(
    name='rpcclient',
    version='0.01',
    description='JSON-RPC 2.0 client library.',
    author='Beau Barker',
    author_email='beauinmelbourne@gmail.com',
    url='https://bitbucket.org/beau-barker/rpcclient',
    packages=['jsonschema', 'requests'],
    )