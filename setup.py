#!/usr/bin/env python3
from setuptools import setup, find_packages
try: # for pip >= 10
    from pip._internal.req import parse_requirements
except ImportError: # for pip <= 9.0.3
    from pip.req import parse_requirements
    
install_reqs = parse_requirements('requirements.txt', session='_dummy_session')
test_req = parse_requirements('test_requirements.txt', session='_dummy_session')
reqs = [str(i.req) for i in install_reqs]
test_reqs = [str(i.req) for i in test_req]

setup(
    name='armarx-dev',
    version='0.11.1',
    description='python bindings for ArmarX',
    author='Markus Grotz',
    author_email='markus.grotz@kit.edu',
    url='https://armarx.humanoids.kit.edu/',
    install_requires=reqs,
    tests_require=test_reqs,
    test_suite='nose.collector',
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
)
