""" Install
"""
import os
from setuptools import setup, find_packages

PACKAGE_NAME = "pdfdiff"
SUMMARY = (
    "Compare two PDF files and generate diff images "
    "and mark differences with red"
)
DESCRIPTION = (
    open("README.rst", 'r').read() + '\n\n' +
    open(os.path.join("docs", 'HISTORY.rst')).read()
)

VERSION = open('version.txt').read().strip()

setup(
    name=PACKAGE_NAME,
    version=VERSION,
    description=SUMMARY,
    long_description=DESCRIPTION,
    author='Ovidiu Miron',
    author_email='ovidiu.miron@eaudeweb.com',
    url='http://github.com/eea/pdfdiff',
    license='MPL',
    packages=find_packages('src', exclude=['ez_setup']),
    package_dir = {'':'src'},
    entry_points = {
      'console_scripts': [
          'pdfdiff = pdfdiff:main'
      ]},
    classifiers=[
      'Environment :: Console',
      'Intended Audience :: Developers',
      "Programming Language :: Python",
      'Operating System :: OS Independent',
      'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    install_requires=[
        'argparse',
        'wand',
        'Pillow',
    ]
)
