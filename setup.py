# -*- coding: utf-8 -*-

import os
from setuptools import setup, find_packages


def read(*rnames):
    return open(
        os.path.join(
            os.path.join(os.path.dirname(__file__), 'docs'),
            *rnames)).read()

version = '1.0'
long_description = read('README.txt') + '\n' + read('HISTORY.txt')

install_requires = [
    'barrel',
    'cromlech.browser',
    'cromlech.dawnlight',
    'cromlech.security',
    'cromlech.webob',
    'dolmen.view',
    'grokcore.component',
    'grokcore.security',
    'ul.browser',
    'webob',
    'zope.event',
    'zope.interface',
    'zope.location',
    'zope.security',
    ]

tests_require = [
    ]

setup(
    name='ul.auth',
    version=version,
    author='Grok & Dolmen Teams',
    author_email='dolmen@list.dolmen-project.org',
    url='http://gitweb.dolmen-project.org',
    download_url='http://pypi.python.org/pypi/ul.auth',
    description='Authentication components for uvclight',
    long_description=long_description,
    license='ZPL',
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Programming Language :: Python',
        ],
    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['ul'],
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    tests_require=tests_require,
    extras_require={
        'test': tests_require
        },
    )
