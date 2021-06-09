#!/bin/env python

"""
Setup script for ami2py
"""

import os
import sys

from setuptools import setup, find_packages


BASE_PATH = os.path.dirname(os.path.abspath(__file__))


if sys.version_info < (3, 6):
    print("ami2py requires python 3.6 because sorted dictionaries are mandatory")
    sys.exit(1)


def long_description():
    with open(os.path.join(BASE_PATH, "README.md")) as readme:
        return readme.read()

setup(
    name="ami2py",
    version="0.7.12",
    packages=find_packages("."),
    package_dir={"": "."},
    include_package_data=True,
    python_requires=">= 3.6",
    license="MIT",
    # install_requires=["setuptools", "pip", "docutils", "purepng>=0.1.1"],
    # extras_require={"bitmap": ["Pillow"]},
    # setup_requires=["pytest-runner"],
    # tests_require=["pytest>=2.0.0", "pytest-assume", "requests", "PyPDF2"],
    author="Dark Ligt alias FB2011B",
    description="Python Package for reading a amibroker database",
    long_description=long_description(),
    long_description_content_type='text/markdown',
    url="https://github.com/F2011B/ami2py",
    keywords="amibroker database pandas",
    classifiers=[
        "Environment :: Console",
        "Environment :: Other Environment",
        "Environment :: Web Environment",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    install_requires=[
        'construct==2.10.67',
        'dataclass-type-validator'
    ]
)
