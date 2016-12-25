import distutils.core as mod_distutilscore
from setuptools import setup, find_packages

mod_distutilscore.setup(
    name='strava-smooth',
    version='0.0.1',
    description='Smoothen latest activity on Strava',
    license='Apache License, Version 2.0',
    author='Jaap Onderwaater',
    author_email='jonderwaater@gmail.com',
    url='https://github.com/jonderwaater/strava-smooth',
    packages=find_packages(),
    install_requires=['stravalib'],
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
    ],
    scripts=['strava-smooth.py']
)
