""" Install
"""
from setuptools import setup, find_packages

PACKAGE_NAME = "pdfdiff"
PACKAGE_VERSION = "1.0"
SUMMARY = (
    "Compare two PDF files and generate diff images "
    "and mark differences with red"
)
DESCRIPTION = (
    open("README.rst", 'r').read() + '\n\n' +
    open('HISTORY.rst', 'r').read()
)

setup(
    name=PACKAGE_NAME,
    version=PACKAGE_VERSION,
    description=SUMMARY,
    long_description=DESCRIPTION,
    author='Ovidiu Miron',
    author_email='ovidiu.miron@eaudeweb.com',
    url='http://github.com/eea/pdfdiff',
    license='MPL',
    packages=find_packages(exclude=['ez_setup']),
    entry_points = {
      'console_scripts': [
          'pdfdiff = pdfdiff.pdfdiff:main'
      ]},
    classifiers=[
      'Environment :: Console',
      'Intended Audience :: Developers',
      "Programming Language :: Python",
      'Operating System :: OS Independent',
      'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    install_requires=[
        'wand',
        'Pillow',
    ]
)
