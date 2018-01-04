#!/usr/bin/env python
from setuptools import setup, find_packages
import __version__ as v
from pip.req import parse_requirements

#install_reqs = parse_requirements("requirements.txt")
#test_req = parse_requirements("test_requirements.txt")
#reqs = [str(i.req) for i in install_reqs]
#test_reqs = [str(i.req) for i in test_req]

setup(
    name="armarx",
    version=v.armarx_version,
    description="python tools for ArmarX",
    author="Markus Grotz",
    author_email="markus.grotz.edu",
    url="https://armarx.humanoids.kit.edu/",
#    install_requires=reqs,
#    tests_require=test_reqs,
    install_requires=['argcomplete', 'configparser'],
    tests_require=['nose', 'mock'],
    test_suite="nose.collector",
    packages=find_packages(exclude=["tests"]),
    include_package_data=True,
)
