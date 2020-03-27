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
    with open(os.path.join(BASE_PATH, "README.rst")) as readme:
        result = readme.read()
    result += "\n\n"
    with open(os.path.join(BASE_PATH, "CHANGES.rst")) as changes:
        result += changes.read()
    return result


setup(
    name="ami2py",
    version="0.1.0",
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
    long_description="No long description yet",
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
)
