import collections
import os
import re

from os.path import dirname, abspath
from pathlib import Path

def parse_gitignore(full_path, base_dir=None):
	if base_dir is None:
		base_dir = dirname(full_path)
	rules = []
	with open(full_path) as ignore_file:
		counter = 0
		for line in ignore_file:
			counter += 1
			line = line.rstrip('\n')
			rule = rule_from_pattern(line, abspath(base_dir),
									 source=(full_path, counter))
			if rule:
				rules.append(rule)
	return lambda file_path: any(r.match(file_path) for r in rules)

def rule_from_pattern(pattern, base_path=None, source=None):
	"""
	Take a .gitignore match pattern, such as "*.py[cod]" or "**/*.bak",
	and return an IgnoreRule suitable for matching against files and
	directories. Patterns which do not match files, such as comments
	and blank lines, will return None.
	Because git allows for nested .gitignore files, a base_path value
	is required for correct behavior. The base path should be absolute.
	"""
	if base_path and base_path != abspath(base_path):
		raise ValueError('base_path must be absolute')
	# Store the exact pattern for our repr and string functions
	orig_pattern = pattern
	# Early returns follow
	# Discard comments and seperators
	if pattern.strip() == '' or pattern[0] == '#':
		return
	# Discard anything with more than two consecutive asterisks
	if pattern.find('***') > -1:
		return
	# Strip leading bang before examining double asterisks
	if pattern[0] == '!':
		negation = True
		pattern = pattern[1:]
	else:
		negation = False
	# Discard anything with invalid double-asterisks -- they can appear
	# at the start or the end, or be surrounded by slashes
	for m in re.finditer(r'\*\*', pattern):
		start_index = m.start()
		if (start_index != 0 and start_index != len(pattern) - 2 and
				(pattern[start_index - 1] != '/' or
				 pattern[start_index + 2] != '/')):
			return

	# Special-casing '/', which doesn't match any files or directories
	if pattern.rstrip() == '/':
		return

	directory_only = pattern[-1] == '/'
	# A slash is a sign that we're tied to the base_path of our rule
	# set.
	anchored = '/' in pattern[:-1]
	if pattern[0] == '/':
		pattern = pattern[1:]
	if pattern[0] == '*' and pattern[1] == '*':
		pattern = pattern[2:]
		anchored = False
	if pattern[0] == '/':
		pattern = pattern[1:]
	if pattern[-1] == '/':
		pattern = pattern[:-1]
	regex = fnmatch_pathname_to_regex(
		pattern
	)
	if anchored:
		regex = ''.join(['^', regex])
	return IgnoreRule(
		pattern=orig_pattern,
		regex=regex,
		negation=negation,
		directory_only=directory_only,
		anchored=anchored,
		base_path=Path(base_path) if base_path else None,
		source=source
	)

whitespace_re = re.compile(r'(\\ )+$')

IGNORE_RULE_FIELDS = [
	'pattern', 'regex',  # Basic values
	'negation', 'directory_only', 'anchored',  # Behavior flags
	'base_path',  # Meaningful for gitignore-style behavior
	'source'  # (file, line) tuple for reporting
]


class IgnoreRule(collections.namedtuple('IgnoreRule_', IGNORE_RULE_FIELDS)):
	def __str__(self):
		return self.pattern

	def __repr__(self):
		return ''.join(['IgnoreRule(\'', self.pattern, '\')'])

	def match(self, abs_path):
		matched = False
		if self.base_path:
			rel_path = str(Path(abs_path).relative_to(self.base_path))
		else:
			rel_path = str(Path(abs_path))
		if rel_path.startswith('./'):
			rel_path = rel_path[2:]
		if re.search(self.regex, rel_path):
			matched = True
		return matched


# Frustratingly, python's fnmatch doesn't provide the FNM_PATHNAME
# option that .gitignore's behavior depends on.
def fnmatch_pathname_to_regex(pattern):
	"""
	Implements fnmatch style-behavior, as though with FNM_PATHNAME flagged;
	the path seperator will not match shell-style '*' and '.' wildcards.
	"""
	i, n = 0, len(pattern)
	
	seps = [re.escape(os.sep)]
	if os.altsep is not None:
		seps.append(re.escape(os.altsep))
	seps_group = '[' + '|'.join(seps) + ']'
	nonsep = r'[^{}]'.format('|'.join(seps))

	res = []
	while i < n:
		c = pattern[i]
		i += 1
		if c == '*':
			try:
				if pattern[i] == '*':
					i += 1
					res.append('.*')
					if pattern[i] == '/':
						i += 1
						res.append(''.join([seps_group, '?']))
				else:
					res.append(''.join([nonsep, '*']))
			except IndexError:
				res.append(''.join([nonsep, '*']))
		elif c == '?':
			res.append(nonsep)
		elif c == '/':
			res.append(seps_group)
		elif c == '[':
			j = i
			if j < n and pattern[j] == '!':
				j += 1
			if j < n and pattern[j] == ']':
				j += 1
			while j < n and pattern[j] != ']':
				j += 1
			if j >= n:
				res.append('\\[')
			else:
				stuff = pattern[i:j].replace('\\', '\\\\')
				i = j + 1
				if stuff[0] == '!':
					stuff = ''.join(['^', stuff[1:]])
				elif stuff[0] == '^':
					stuff = ''.join('\\' + stuff)
				res.append('[{}]'.format(stuff))
		else:
			res.append(re.escape(c))
	res.insert(0, '(?ms)')
	res.append('$')
	return ''.join(res)