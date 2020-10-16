# gitignore_parser

![CI](https://github.com/mherrmann/gitignore_parser/workflows/CI/badge.svg)
[![PyPI version](https://badge.fury.io/py/gitignore-parser.svg)](https://badge.fury.io/py/gitignore-parser)

A spec-compliant gitignore parser for Python

## Installation

    pip install gitignore_parser

## Usage

Suppose `/home/michael/project/.gitignore` contains the following:

    __pycache__/
    *.py[cod]

Then:

    >>> from gitignore_parser import parse_gitignore
    >>> matches = parse_gitignore('/home/michael/project/.gitignore')
    >>> matches('/home/michael/project/main.py')
    False
    >>> matches('/home/michael/project/main.pyc')
    True
    >>> matches('/home/michael/project/dir/main.pyc')
    True
    >>> matches('/home/michael/project/__pycache__')
    True

## Motivation

I couldn't find a good library for doing the above on PyPI. There are
several other libraries, but they don't seem to support all features,
be it the square brackets in `*.py[cod]` or top-level paths `/...`.

## Contributing

I'm very open to merging PRs. But before you start working on one, please
read through my
[guidelines for PRs](https://gist.github.com/mherrmann/5ce21814789152c17abd91c0b3eaadca).
It will save us both time and unnecessary effort.

## Attribution

The implementation is based on https://github.com/snark/ignorance/ by
Steve Cook.
