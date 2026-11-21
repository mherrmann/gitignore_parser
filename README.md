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

Alternatively, you can use the `parse_gitignore_str` function:

    >>> from gitignore_parser import parse_gitignore_str
    >>> matches = parse_gitignore_str(
        '__pycache__/\n*.py[cod]', base_dir='/home/michael/project')
    >>> matches('/home/michael/project/main.py')
    False
    >>> matches('/home/michael/project/main.pyc')
    True

The matcher does not query the filesystem. By default it matches paths without
knowing whether they refer to files or directories. Pass `is_dir=True` or
`is_dir=False` to distinguish them when using directory-only patterns:

    >>> matches = parse_gitignore_str('build*/', base_dir='/home/michael/project')
    >>> matches('/home/michael/project/build.sh', is_dir=False)
    False
    >>> matches('/home/michael/project/build_debug', is_dir=True)
    True
    >>> matches('/home/michael/project/build_debug/main.c', is_dir=False)
    True

The optional hint works with both parsers and with string or `pathlib.Path`
arguments. It also applies to directory-only negations such as `!build/` and
overrides any trailing slash on the path. Omitting it preserves the existing
path-only behavior.

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
