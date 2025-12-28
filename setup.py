#!/usr/bin/env python3

"""
Setup script for the Chert SDK Python package.
"""

from setuptools import setup, find_packages
import os

# Read the README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='chert-sdk',
    version='0.1.0',
    description='Official Python SDK for the Chert/Silica blockchain network',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Chert Team',
    author_email='team@chert.com',
    url='https://github.com/silica-network/chert',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Security :: Cryptography',
    ],
    keywords='blockchain, sdk, cryptocurrency, silica, chert, web3',
    python_requires='>=3.8',
    install_requires=[
        'aiohttp>=3.8.0',
        'pydantic>=2.0.0',
        'typing-extensions>=4.0.0',
        'cryptography>=41.0.0',
        'hexbytes>=0.3.0',
    ],
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'pytest-asyncio>=0.21.0',
            'black>=23.0.0',
            'isort>=5.12.0',
            'mypy>=1.0.0',
            'flake8>=6.0.0',
        ],
        'docs': [
            'sphinx>=5.0.0',
            'sphinx-rtd-theme>=1.2.0',
        ],
    },
    project_urls={
        'Documentation': 'https://docs.chert.com/python-sdk',
        'Source': 'https://github.com/silica-network/chert/tree/main/sdk/python',
        'Tracker': 'https://github.com/silica-network/chert/issues',
    },
)