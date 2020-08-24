from unittest.mock import patch, mock_open

from gitignore_parser import parse_gitignore

from unittest import TestCase


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
        self.assertTrue(matches('/home/michael/othermatch'))
        self.assertTrue(matches('/home/michael/#imnocomment'))

    def test_ignore_directory(self):
        matches = _parse_gitignore_string('.venv/', fake_base_dir='/home/michael')
        self.assertTrue(matches('/home/michael/.venv'))
        self.assertTrue(matches('/home/michael/.venv/folder'))
        self.assertTrue(matches('/home/michael/.venv/file.txt'))

    def test_ignore_directory_asterisk(self):
        matches = _parse_gitignore_string('.venv/*', fake_base_dir='/home/michael')
        self.assertFalse(matches('/home/michael/.venv'))
        self.assertTrue(matches('/home/michael/.venv/folder'))
        self.assertTrue(matches('/home/michael/.venv/file.txt'))

    def test_negation(self):
        matches = _parse_gitignore_string(
            '''
*.ignore
!keep.ignore
            ''',
            fake_base_dir='/home/michael'
        )
        self.assertTrue(matches('/home/michael/trash.ignore'))
        self.assertFalse(matches('/home/michael/keep.ignore'))
        self.assertTrue(matches('/home/michael/waste.ignore'))


    def test_double_asterisks(self):
        matches = _parse_gitignore_string('foo/**/Bar', fake_base_dir='/home/michael')
        self.assertTrue(matches('/home/michael/foo/hello/Bar'))
        self.assertTrue(matches('/home/michael/foo/world/Bar'))
        self.assertTrue(matches('/home/michael/foo/Bar'))

    def test_single_asterisk(self):
        matches = _parse_gitignore_string('*', fake_base_dir='/home/michael')
        self.assertTrue(matches('/home/michael/file.txt'))
        self.assertTrue(matches('/home/michael/directory'))
        self.assertTrue(matches('/home/michael/directory-trailing/'))


def _parse_gitignore_string(data: str, fake_base_dir: str = None):
    with patch('builtins.open', mock_open(read_data=data)):
        success = parse_gitignore(f'{fake_base_dir}/.gitignore', fake_base_dir)
        return success
