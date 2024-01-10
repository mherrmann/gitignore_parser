"""A spec-compliant gitignore parser for Python 3.5+

See:
https://github.com/mherrmann/gitignore_parser
"""

from setuptools import setup

description = 'A spec-compliant gitignore parser for Python 3.5+'
setup(
    name='gitignore_parser',
    version='0.1.10',
    description=description,
    long_description=
        description + '\n\nhttps://github.com/mherrmann/gitignore_parser',
    author='Michael Herrmann',
    author_email='michael+removethisifyouarehuman@herrmann.io',
    url='https://github.com/mherrmann/gitignore_parser',
    py_modules=['gitignore_parser'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',

        'License :: OSI Approved :: MIT License',

        'Operating System :: OS Independent',

        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',

        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    license='MIT',
    keywords='gitignore',
    platforms=['MacOS', 'Windows', 'Debian', 'Fedora', 'CentOS']
)
