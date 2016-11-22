import os
import sys

from setuptools import setup, find_packages

setup(
    name='mailingSHARK',
    version='0.1',
    description='Collect data from mailing lists',
    install_requires=['mongoengine', 'pymongo', 'requests'],
    author='Fabian Trautsch',
    author_email='ftrautsch@googlemail.com',
    url='https://github.com/smartshark/mailingSHARK',
    test_suite='tests',
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache2.0 License",
        "Operating System :: POSIX :: Linux",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)

