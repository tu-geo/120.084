# -*- coding: utf-8 -*-

# Learn more: https://github.com/kennethreitz/setup.py

from setuptools import setup, find_packages


with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='prg1',
    version='0.0.1',
    description='Program 1 for lecture <Realtime...>',
    long_description=readme,
    author='Jürgen Fredriksosn',
    author_email='jiargei@gmail.com',
    url='https://github.com/kennethreitz/samplemod',
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)

