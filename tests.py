"""
Run these tests with `python3 -m unittest`.
"""

from gitignore_parser import parse_gitignore
from tempfile import NamedTemporaryFile
import os
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

def _parse_gitignore_string(s, fake_base_dir=None):
	# The file returned by NamedTemporaryFile cannot be opened twice on Windows
	# without closing it first. Create it, close it, then open it again.
	# Manually delete when we're done.
	tmp = NamedTemporaryFile('w', delete=False)
	tmp.write(s)
	tmp.close()
	success = parse_gitignore(tmp.name, fake_base_dir)
	os.unlink(tmp.name)
	return success