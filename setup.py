import os
import re
import sys
import codecs
from setuptools import setup, find_packages

from setuptools.command.test import test as TestCommand
class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]
    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True
    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)

here = os.path.abspath(os.path.dirname(__file__))

def read(path):
    return codecs.open(os.path.join(here, path), 'r', 'utf-8').read()

readme = read('README.rst')
history = read('HISTORY.rst')
version_file = read('pyhorn/__init__.py')
version = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M).group(1)

install_requires = ["requests", "requests-cache", "arrow", "rwlock", "six"]
tests_require = ["pytest", "httmock", "mock", "freezegun"]

setup(
    name='pyhorn',
    version=version,
    packages=find_packages(exclude=["docs", "tests*"]),
    url='https://bitbucket.org/lbjay/pyhorn',
    license='Apache 2.0',
    author='Jay Luker',
    author_email='lbjay@reallywow.com',
    description='Python wrapper for the Matterhorn RESTful APIs',
    long_description=readme + '\n\n' + history,
    install_requires=install_requires,
    tests_require=tests_require,
    cmdclass={'test': PyTest},
    classifiers=(
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    )
)
