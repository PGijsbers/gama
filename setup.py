#!/usr/bin/env python

from setuptools import setup, find_packages

requirements = [
    'numpy==1.15.4',
    'scipy>=1.0.0',
    'scikit-learn==0.20.2',
    'stopit>=1.1.1',
    'liac-arff>=2.2.2',
    'category-encoders>=1.2.8'
]

setup(
    name='gama',
    version='19.01.0.d3m',
    description='A package for automated machine learning based on scikit-learn.',
    long_description='',
    long_description_content_type='text/markdown',
    author='Pieter Gijsbers',
    author_email='p.gijsbers@tue.nl',
    url='https://github.com/PGijsbers/GAMA',
    packages=find_packages(exclude=['tests']),
    install_requires=requirements,
    python_requires='>=3.5.0'
)
