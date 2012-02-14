from setuptools import setup, find_packages
import sys, os

version = '0.0'

setup(name='staticdocs-plugin',
      version=version,
      description="A Trac plugin to allow access to static documents",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='trac',
      author='Jeff Dairiki',
      author_email='dairiki@dairiki.org',
      url='',
      license='',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
