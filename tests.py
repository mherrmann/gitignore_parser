from gitignore_parser import parse_gitignore
from tempfile import NamedTemporaryFile
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

def _parse_gitignore_string(s, fake_base_dir=None):
	with NamedTemporaryFile('w') as tmp:
		tmp.write(s)
		tmp.seek(0)
		return parse_gitignore(tmp.name, fake_base_dir)