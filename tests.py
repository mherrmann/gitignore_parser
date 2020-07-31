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