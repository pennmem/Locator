from setuptools import setup

from Locator import Locator

setup(
   name='Locator',
   version=Locator.__version__,
   description='Intracranial contact localization class',
   author='Ryan A. Colyer',
   author_email='rcolyer@sas.upenn.edu',
   packages=[], 
   install_requires=['cmlreaders']
)

