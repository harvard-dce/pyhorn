import os
import re
import codecs
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

def read(path):
    return codecs.open(os.path.join(here, path), 'r', 'utf-8').read()

readme = read('README.rst')
history = read('HISTORY.rst')
version_file = read('pyhorn/__init__.py')
version = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M).group(1)

install_requires = ["requests", "requests-cache"]
tests_require = ["nose", "httmock"]

setup(
    name='pyhorn',
    version=version,
    packages=find_packages(exclude=["docs", "tests*"]),
    url='https://github.com/harvard-dce/pyhorn',
    license='Apache 2.0',
    author='Jay Luker',
    author_email='lbjay@reallywow.com',
    description='Python wrapper for the Matterhorn RESTful APIs',
    long_description=readme + '\n\n' + history,
    install_requires=install_requires,
    tests_require=tests_require,
    zip_safe=True,
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
