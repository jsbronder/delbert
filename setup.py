#!/usr/bin/env python
import os
import sys

VERSION = '0.1'
PACKAGE = 'delbert'

import setuptools

scripts = []
if os.path.exists('bin/%s' % (PACKAGE,)):
    scripts = ['bin/%s' % (PACKAGE,)]

setuptools.setup(
        name=PACKAGE,
        version=VERSION,
        description='Python/Twisted IRC bot',
        license='BSD',
        long_description=open('README.rst').read(),
        author='Justin Bronder',
        author_email='jsbronder@cold-front.org',
        url='http://github.com/jsbronder/%s' % (PACKAGE,),
        keywords='irc bot python twisted',
        packages=[PACKAGE],
        package_data = {
            '': ['*.rst', 'db/*', 'LICENSE'],
        },
        scripts=scripts,
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
        ],
)
