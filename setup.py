import sys

from setuptools import setup, find_packages

if not sys.version_info[0] == 3:
    print('only python3 supported!')
    sys.exit(1)

setup(
    name='mailingSHARK',
    version='2.0.1',
    author='Fabian Trautsch',
    author_email='trautsch@cs.uni-goettingen.de',
    description='Collect data from issue mailing lists',
    install_requires=['mongoengine', 'pymongo', 'requests', 'bs4', 'pycoshark>=1.0.3', 'mock'],
    url='https://github.com/smartshark/mailingSHARK',
    download_url='https://github.com/smartshark/mailingSHARK/zipball/master',
    packages=find_packages(),
    test_suite ='tests',
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


