from unittest.mock import patch, mock_open
from pathlib import Path
from tempfile import TemporaryDirectory

from gitignore_parser import parse_gitignore

from unittest import TestCase, main, SkipTest


class Test(TestCase):
    def test_simple(self):
        matches = _parse_gitignore_string(
            '__pycache__/\n'
            '*.py[cod]',
            fake_base_dir='/home/michael'
        )
        self.assertFalse(matches('/home/michael/main.py'))
        self.assertTrue(matches('/home/michael/main.pyc'))
        self.assertTrue(matches('/home/michael/dir/main.pyc'))
        self.assertTrue(matches('/home/michael/__pycache__'))

    def test_incomplete_filename(self):
        matches = _parse_gitignore_string('o.py', fake_base_dir='/home/michael')
        self.assertTrue(matches('/home/michael/o.py'))
        self.assertFalse(matches('/home/michael/foo.py'))
        self.assertFalse(matches('/home/michael/o.pyc'))
        self.assertTrue(matches('/home/michael/dir/o.py'))
        self.assertFalse(matches('/home/michael/dir/foo.py'))
        self.assertFalse(matches('/home/michael/dir/o.pyc'))

    def test_wildcard(self):
        matches = _parse_gitignore_string(
            'hello.*',
            fake_base_dir='/home/michael'
        )
        self.assertTrue(matches('/home/michael/hello.txt'))
        self.assertTrue(matches('/home/michael/hello.foobar/'))
        self.assertTrue(matches('/home/michael/dir/hello.txt'))
        self.assertTrue(matches('/home/michael/hello.'))
        self.assertFalse(matches('/home/michael/hello'))
        self.assertFalse(matches('/home/michael/helloX'))

    def test_anchored_wildcard(self):
        matches = _parse_gitignore_string(
            '/hello.*',
            fake_base_dir='/home/michael'
        )
        self.assertTrue(matches('/home/michael/hello.txt'))
        self.assertTrue(matches('/home/michael/hello.c'))
        self.assertFalse(matches('/home/michael/a/hello.java'))

    def test_trailingspaces(self):
        matches = _parse_gitignore_string(
            'ignoretrailingspace \n'
            'notignoredspace\\ \n'
            'partiallyignoredspace\\  \n'
            'partiallyignoredspace2 \\  \n'
            'notignoredmultiplespace\\ \\ \\ ',
            fake_base_dir='/home/michael'
        )
        self.assertTrue(matches('/home/michael/ignoretrailingspace'))
        self.assertFalse(matches('/home/michael/ignoretrailingspace '))
        self.assertTrue(matches('/home/michael/partiallyignoredspace '))
        self.assertFalse(matches('/home/michael/partiallyignoredspace  '))
        self.assertFalse(matches('/home/michael/partiallyignoredspace'))
        self.assertTrue(matches('/home/michael/partiallyignoredspace2  '))
        self.assertFalse(matches('/home/michael/partiallyignoredspace2   '))
        self.assertFalse(matches('/home/michael/partiallyignoredspace2 '))
        self.assertFalse(matches('/home/michael/partiallyignoredspace2'))
        self.assertTrue(matches('/home/michael/notignoredspace '))
        self.assertFalse(matches('/home/michael/notignoredspace'))
        self.assertTrue(matches('/home/michael/notignoredmultiplespace   '))
        self.assertFalse(matches('/home/michael/notignoredmultiplespace'))

    def test_comment(self):
        matches = _parse_gitignore_string(
                        'somematch\n'
                        '#realcomment\n'
                        'othermatch\n'
                        '\\#imnocomment',
            fake_base_dir='/home/michael'
        )
        self.assertTrue(matches('/home/michael/somematch'))
        self.assertFalse(matches('/home/michael/#realcomment'))


