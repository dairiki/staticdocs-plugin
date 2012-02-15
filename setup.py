from setuptools import setup
import os

from version import get_git_version

PACKAGE = 'staticdocs-plugin'

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
CHANGES = open(os.path.join(here, 'CHANGES.rst')).read()

tests_require = [
    'Mock >= 0.7',
    ]

from unittest import TestCase
if not hasattr(TestCase, 'assertIn'):
    # for python < 2.7
    tests_require += [ 'unittest2' ]

setup(name='staticdocs-plugin',
      version=get_git_version(),
      description="A Trac plugin to allow access to static documents",
      long_description=README + "\n\n" + CHANGES,
      platforms = ['Any'],
      classifiers=[
          "Development Status :: 4 - Beta",
          "Environment :: Plugins",
          "Environment :: Web Environment",
          "Framework :: Trac",
          "Intended Audience :: System Administrators",
          "Topic :: Internet :: WWW/HTTP",
          "Programming Language :: Python :: 2",
          "License :: OSI Approved :: BSD License",
          ],
      keywords='trac',
      author='Jeff Dairiki',
      author_email='dairiki@dairiki.org',
      url='http://github.com/dairiki/staticdocs-plugin',
      license='BSD',
      packages=[
          'staticdocsplugin',
          ],
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          'trac',
          ],
      tests_require=tests_require,
      setup_requires=[
          'setuptools-git',
          ],
      test_suite='staticdocsplugin.test',
      entry_points={
          'trac.plugins': [
              '%s = staticdocsplugin.staticdocs' % PACKAGE,
              ],
          },
      )
