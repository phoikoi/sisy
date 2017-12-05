"""Setup module for sisy

REQUIRES Python 3.6
"""
# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path
from pathlib import Path

here = Path(__file__).parent

long_description = (here / 'README.rst').read_text()

setup(
    name='sisy',
    python_requires='>=3.6',

    version='1.0b1',

    description='A lightweight repeating task runner app for Django',
    long_description=long_description,

    url='https://github.com/phoikoi/sisy',

    author='Peter Hull',
    author_email='z8kflt@gmail.com',

    license='MIT',

    classifiers=[
        'Development Status :: 4 - Beta',

        'Intended Audience :: Developers',

        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.6',

    ],

    keywords=[
        'django',
        'channels',
        'cron',
        'croniter',
        'background-tasks',
    ],

    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=False,
    zip_safe=False,
    install_requires=[
        'django>=1.11',
        'channels',
        'croniter',
        'pytz',
    ],
)
