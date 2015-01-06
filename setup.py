#!/usr/bin/env python
import os
import setuptools
import sys

def read(*paths):
    """Build a file path from *paths* and return the contents."""
    with open(os.path.join(*paths), 'r') as f:
        return f.read()

setuptools.setup(
        name='delbert',
        version=0.1,
        description='Python/Twisted IRC bot',
        license='BSD',
        long_description=(read('README.rst')),
        author='Justin Bronder',
        author_email='jsbronder@gmail.com',
        url='http://github.com/jsbronder/delbert',
        keywords='irc bot python twisted',
        packages=['delbert'],
        package_data = {
          '': ['*.rst', 'db/*', 'LICENSE'],
        },
        install_requires=['beautifulsoup', 'pyyaml', 'requests', 'requests-oauthlib', 'twisted',],
        classifiers=[
            'Development Status :: 3 - Alpha',
            'Environment :: Console',
            'Intended Audience :: Developers',
            'Intended Audience :: End Users/Desktop',
            'License :: OSI Approved :: BSD License',
            'Operating System :: POSIX',
            'Programming Language :: Python',
            'Programming Language :: Python :: 2',
            'Programming Language :: Python :: 2.7',
            'Topic :: Communications :: Chat',
            'Topic :: Communications :: Chat :: Internet Relay Chat',
            'Topic :: Utilities',
        ]
)
