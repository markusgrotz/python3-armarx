from setuptools import setup, find_packages
setup(
    name='python3-armarx',
    version='0.23.3',
    author='',
    author_email='',
    description="This package contains armarx python bindings, "
                "this is temporal setup script for testing armarx_control features",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        'zeroc-ice==3.7.0',
        'lxml>=4.8.0',
        'numpy>=1.19.5',
        'transforms3d>=0.4.1',
        'marshmallow',
        'marshmallow_dataclass',
        'pyyaml',
        'icecream',
        'rich'
    ]
)
