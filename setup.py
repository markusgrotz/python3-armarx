#!/usr/bin/env python3
from setuptools import setup, find_packages

def parse_requirements(filename):
    lines = [l.strip() for l in open(filename)]
    return [l for l in lines if l and not l.startswith('#')]

reqs = parse_requirements('requirements.txt')
test_reqs = parse_requirements('test_requirements.txt')

setup(
    name='armarx-dev',
    version='0.12.0',
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
