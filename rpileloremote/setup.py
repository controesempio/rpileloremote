#!/usr/bin/env python

from setuptools import setup, find_packages

with open('README.rst') as file:
    long_description = file.read()

setup(
    name='rpileloremote',
    version='1.0',
    description='Interfacing with Lelo(tm) Remote controllers',
    long_description = long_description,
    author='lucha',
    author_email='lucha@paranoici.org',
    license='GPLv3',
    url='https://github.com/controesempio/rpileloremote',
    install_requires=["spidev","RPi.GPIO>=0.5.0"],
    packages=find_packages(),
)
