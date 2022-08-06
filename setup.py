# -*- coding: utf-8 -*-

# Learn more: https://github.com/kennethreitz/setup.py

from setuptools import setup, find_packages


with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='airconcontroller',
    version='0.1.0',
    description='Command the Air Conditioner to do stuff.',
    long_description=readme,
    author='Cameron Frazier',
    author_email='frazier.cameron@gmail.com',
    url='https://github.com/cameronfrazier/AirConController',
    license=license,
    packages=["airconcontroller"]
)
