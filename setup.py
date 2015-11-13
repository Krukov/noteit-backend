#!/usr/bin/env python
from setuptools import setup

from client.noteit import get_version


setup(
    name='noteit',
    version=get_version(),
    packages=['client'],
    
    entry_points={
        'console_scripts': [
            'noteit = client.noteit:main',
        ]
    },
    url='https://github.com/Krukov/noteit',
    download_url='https://github.com/Krukov/noteit/tarball/' + get_version(),
    license='MIT',
    author='Dmitry Krukov',
    author_email='glebov.ru@gmail.com',
    description='Tool for create shared notes',
    long_description=open('README.rst').read(),
    keywords='noteit note console command line messages', 
    classifiers=[
        'Development Status :: 4 - Beta',
        "Environment :: Console",
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
    ],
)