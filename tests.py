from typing import Optional
from shutil import which
from unittest.mock import patch, mock_open
from pathlib import Path
from tempfile import TemporaryDirectory

from gitignore_parser import parse_gitignore

from unittest import TestCase, main, skipUnless

import tempfile
from subprocess import run


class Test(TestCase):
    def test_simple(self):
        matches = self._parse_gitignore_string(
            '__pycache__/\n'
            '*.py[cod]',
            fake_base_dir='/home/michael'
        )
        self.assertFalse(matches('/home/michael/main.py'))
        self.assertTrue(matches('/home/michael/main.pyc'))
        self.assertTrue(matches('/home/michael/dir/main.pyc'))
        self.assertTrue(matches('/home/michael/__pycache__/'))

    def test_incomplete_filename(self):
        matches = self._parse_gitignore_string('o.py', fake_base_dir='/home/michael')
        self.assertTrue(matches('/home/michael/o.py'))
        self.assertFalse(matches('/home/michael/foo.py'))
        self.assertFalse(matches('/home/michael/o.pyc'))
        self.assertTrue(matches('/home/michael/dir/o.py'))
        self.assertFalse(matches('/home/michael/dir/foo.py'))
        self.assertFalse(matches('/home/michael/dir/o.pyc'))

    def test_wildcard(self):
        matches = self._parse_gitignore_string(
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
        matches = self._parse_gitignore_string(
            '/hello.*',
            fake_base_dir='/home/michael'
        )
        self.assertTrue(matches('/home/michael/hello.txt'))
        self.assertTrue(matches('/home/michael/hello.c'))
        self.assertFalse(matches('/home/michael/a/hello.java'))

    def test_trailingspaces(self):
        matches = self._parse_gitignore_string(
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
        matches = self._parse_gitignore_string(
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
        matches = \
            self._parse_gitignore_string('.venv/', fake_base_dir='/home/michael')
        self.assertTrue(matches('/home/michael/.venv'))
        self.assertTrue(matches('/home/michael/.venv/folder'))
        self.assertTrue(matches('/home/michael/.venv/file.txt'))
        self.assertFalse(matches('/home/michael/.venv_other_folder'))
        self.assertFalse(matches('/home/michael/.venv_no_folder.py'))

    def test_ignore_directory_asterisk(self):
        matches = \
            self._parse_gitignore_string('.venv/*', fake_base_dir='/home/michael')
        self.assertFalse(matches('/home/michael/.venv'))
        self.assertTrue(matches('/home/michael/.venv/folder'))
        self.assertTrue(matches('/home/michael/.venv/file.txt'))

    def test_negation(self):
        matches = self._parse_gitignore_string(
            '''
*.ignore
!keep.ignore
            ''',
            fake_base_dir='/home/michael'
        )
        self.assertTrue(matches('/home/michael/trash.ignore'))
        self.assertFalse(matches('/home/michael/keep.ignore'))
        self.assertTrue(matches('/home/michael/waste.ignore'))

    def test_literal_exclamation_mark(self):
        matches = self._parse_gitignore_string(
            '\\!ignore_me!', fake_base_dir='/home/michael'
        )
        self.assertTrue(matches('/home/michael/!ignore_me!'))
        self.assertFalse(matches('/home/michael/ignore_me!'))
        self.assertFalse(matches('/home/michael/ignore_me'))

    def test_double_asterisks(self):
        matches = self._parse_gitignore_string(
            'foo/**/Bar', fake_base_dir='/home/michael'
        )
        self.assertTrue(matches('/home/michael/foo/hello/Bar'))
        self.assertTrue(matches('/home/michael/foo/world/Bar'))
        self.assertTrue(matches('/home/michael/foo/Bar'))
        self.assertFalse(matches('/home/michael/foo/BarBar'))

    def test_double_asterisk_without_slashes_handled_like_single_asterisk(self):
        matches = \
            self._parse_gitignore_string('a/b**c/d', fake_base_dir='/home/michael')
        self.assertTrue(matches('/home/michael/a/bc/d'))
        self.assertTrue(matches('/home/michael/a/bXc/d'))
        self.assertTrue(matches('/home/michael/a/bbc/d'))
        self.assertTrue(matches('/home/michael/a/bcc/d'))
        self.assertFalse(matches('/home/michael/a/bcd'))
        self.assertFalse(matches('/home/michael/a/b/c/d'))
        self.assertFalse(matches('/home/michael/a/bb/cc/d'))
        self.assertFalse(matches('/home/michael/a/bb/XX/cc/d'))

    def test_more_asterisks_handled_like_single_asterisk(self):
        matches = \
            self._parse_gitignore_string('***a/b', fake_base_dir='/home/michael')
        self.assertTrue(matches('/home/michael/XYZa/b'))
        self.assertFalse(matches('/home/michael/foo/a/b'))
        matches = \
            self._parse_gitignore_string('a/b***', fake_base_dir='/home/michael')
        self.assertTrue(matches('/home/michael/a/bXYZ'))
        self.assertFalse(matches('/home/michael/a/b/foo'))

    def test_directory_only_negation(self):
        matches = self._parse_gitignore_string('''
data/**
!data/**/
!.gitkeep
!data/01_raw/*
            ''',
            fake_base_dir='/home/michael'
        )
        self.assertFalse(matches('/home/michael/data/01_raw/'))
        self.assertFalse(matches('/home/michael/data/01_raw/.gitkeep'))
        self.assertFalse(matches('/home/michael/data/01_raw/raw_file.csv'))
        self.assertFalse(matches('/home/michael/data/02_processed/'))
        self.assertFalse(matches('/home/michael/data/02_processed/.gitkeep'))
        self.assertTrue(
            matches('/home/michael/data/02_processed/processed_file.csv')
        )

    def test_single_asterisk(self):
        matches = self._parse_gitignore_string('*', fake_base_dir='/home/michael')
        self.assertTrue(matches('/home/michael/file.txt'))
        self.assertTrue(matches('/home/michael/directory'))
        self.assertTrue(matches('/home/michael/directory-trailing/'))

    def test_supports_path_type_argument(self):
        matches = self._parse_gitignore_string(
            'file1\n!file2', fake_base_dir='/home/michael'
        )
        self.assertTrue(matches(Path('/home/michael/file1')))
        self.assertFalse(matches(Path('/home/michael/file2')))

    def test_slash_in_range_does_not_match_dirs(self):
        matches = self._parse_gitignore_string(
            'abc[X-Z/]def', fake_base_dir='/home/michael'
        )
        self.assertFalse(matches('/home/michael/abcdef'))
        self.assertTrue(matches('/home/michael/abcXdef'))
        self.assertTrue(matches('/home/michael/abcYdef'))
        self.assertTrue(matches('/home/michael/abcZdef'))
        self.assertFalse(matches('/home/michael/abc/def'))
        self.assertFalse(matches('/home/michael/abcXYZdef'))

    def test_symlink_to_another_directory(self):
        with TemporaryDirectory() as project_dir:
            with TemporaryDirectory() as another_dir:
                matches = \
                    self._parse_gitignore_string('link', fake_base_dir=project_dir)

                # Create a symlink to another directory.
                link = Path(project_dir, 'link')
                target = Path(another_dir, 'target')
                link.symlink_to(target)

                # Check the intended behavior according to
                # https://git-scm.com/docs/gitignore#_notes:
                # Symbolic links are not followed and are matched as if they
                # were regular files.
                self.assertTrue(matches(link))

    def test_symlink_to_symlink_directory(self):
        with TemporaryDirectory() as project_dir:
            with TemporaryDirectory() as link_dir:
                link = Path(link_dir, 'link')
                link.symlink_to(project_dir)
                file = Path(link, 'file.txt')
                matches = \
                    self._parse_gitignore_string('file.txt', fake_base_dir=str(link))
                self.assertTrue(matches(file))

    def _parse_gitignore_string(self, data: str, fake_base_dir: Optional[str] = None):
        with patch('builtins.open', mock_open(read_data=data)):
            success = parse_gitignore(f'{fake_base_dir}/.gitignore', fake_base_dir)
            return success


@skipUnless(which("git"), "Git not installed")
class TestAgainstGit(Test):
    """Testcase running tests against `git check-ignore`.

    This is not to test if git is right, this is to validate that all
    tests from the Test class are valid according to git.
    """
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        run(["git", "init"], cwd=self.tmpdir.name)

    def tearDown(self):
        self.tmpdir.cleanup()

    def _parse_gitignore_string(self, data: str, fake_base_dir: Optional[str] = None):
        (Path(self.tmpdir.name) / ".gitignore").write_text(data, encoding="UTF-8")

        def matcher(path):
            path = str(path).replace(fake_base_dir + "/", "")
            return run(["git", "check-ignore", path], cwd=self.tmpdir.name, check=False).returncode == 0

        return matcher


if __name__ == '__main__':
    main()
