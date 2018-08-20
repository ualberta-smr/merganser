from setuptools import setup
from setuptools import find_packages

long_description = '''
This repository helps developers and researchers with collecting the data of merge scenarios and conflicts.
'''

setup(name='Merge Excavator',
      version='0.0.1',
      description='Merge Data Extraction and Analysis',
      long_description=long_description,
      author='Francois Chollet',
      author_email='owhadika@ualberta.ca',
      url='-',
      download_url='-',
      license='-',
      install_requires=['numpy>=1.9.1'],
      classifiers=[
          'Programming Language :: Python :: 3.6',
          'Topic :: Software Development :: Libraries',
          'Topic :: Software Development :: Libraries :: Python Modules'
      ],
      packages=find_packages())
