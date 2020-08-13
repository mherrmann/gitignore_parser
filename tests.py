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


def _parse_gitignore_string(data: str, fake_base_dir: str = None):
    with patch('builtins.open', mock_open(read_data=data)):
        success = parse_gitignore(f'{fake_base_dir}/.gitignore', fake_base_dir)
        return success
