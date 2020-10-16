import collections
import os
import re
from pathlib import Path
from typing import Callable
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union


whitespace_re = re.compile(r'(\\ )+$')

IGNORE_RULE_FIELDS = [
    'pattern',
    'regex',  # Basic values
    'negation',
    'directory_only',
    'anchored',  # Behavior flags
    'base_path',  # Meaningful for gitignore-style behavior
    'source',  # (file, line) tuple for reporting
]


class IgnoreRule(collections.namedtuple('IgnoreRule_', IGNORE_RULE_FIELDS)):
    def __str__(self):
        return self.pattern

    def __repr__(self):
        return ''.join(['IgnoreRule('', self.pattern, '')'])

    def match(self, abs_path):
        matched = False
        if self.base_path:
            rel_path = str(Path(abs_path).resolve().relative_to(self.base_path))
        else:
            rel_path = str(Path(abs_path))
        if rel_path.startswith('./'):
            rel_path = rel_path[2:]
        if re.search(self.regex, rel_path):
            matched = True
        return matched


def handle_negation(file_path: Union[Path, str], rules: List[IgnoreRule]) -> bool:
    matched = False
    for rule in rules:
        if rule.match(file_path):
            if rule.negation:
                matched = False
            else:
                matched = True
    return matched


def rule_from_pattern(
    pattern: str,
    base_path: Union[Path, str] = None,
    source: Optional[Tuple[Union[Path, str], int]] = None,
) -> Optional[IgnoreRule]:
    """
    Take a .gitignore match pattern, such as '*.py[cod]' or '**/*.bak',
    and return an IgnoreRule suitable for matching against files and
    directories. Patterns which do not match files, such as comments
    and blank lines, will return None.
    Because git allows for nested .gitignore files, a base_path value
    is required for correct behavior. The base path should be absolute.
    """
    if base_path and base_path != Path(base_path).resolve():
        raise ValueError('base_path must be absolute')
    # Store the exact pattern for our repr and string functions
    orig_pattern = pattern
    # Early returns follow
    # Discard comments and separators
    if pattern.strip() == '' or pattern[0] == '#':
        return None
    # Discard anything with more than two consecutive asterisks
    if pattern.find('***') > -1:
        return None
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
            return None

    # Special-casing '/', which doesn't match any files or directories
    if pattern.rstrip() == '/':
        return None

    directory_only = pattern[-1] == '/'
    # A slash is a sign that we're tied to the base_path of our rule
    # set.
    anchored = '/' in pattern[:-1]
    if pattern[0] == '/':
        pattern = pattern[1:]
    if pattern[0] == '*' and len(pattern) >= 2 and pattern[1] == '*':
        pattern = pattern[2:]
        anchored = False
    if pattern[0] == '/':
        pattern = pattern[1:]
    if pattern[-1] == '/':
        pattern = pattern[:-1]
    # patterns with leading hashes are escaped with a backslash in front, unescape it
    if pattern[0] == '\\' and pattern[1] == '#':
        pattern = pattern[1:]
    # trailing spaces are ignored unless they are escaped with a backslash
    i = len(pattern)-1
    striptrailingspaces = True
    while i > 1 and pattern[i] == ' ':
        if pattern[i-1] == '\\':
            pattern = pattern[:i-1] + pattern[i:]
            i = i - 1
            striptrailingspaces = False
        else:
            if striptrailingspaces:
                pattern = pattern[:i]
        i = i - 1
    regex = fnmatch_pathname_to_regex(pattern, directory_only)
    if anchored:
        regex = ''.join(['^', regex])
    return IgnoreRule(
        pattern=orig_pattern,
        regex=regex,
        negation=negation,
        directory_only=directory_only,
        anchored=anchored,
        base_path=Path(base_path) if base_path else None,
        source=source,
    )


def parse_gitignore(
    base_dir: Union[Path, str], filename: str = '.gitignore'
) -> Callable[[Union[Path, str]], bool]:
    """
    Parse the ignore file and returns a Callable that will, given a Path or Pathlike object will return True or false
    if the path matches the ignore file

    :param filename: The name of the ignore file
    :param base_dir: The base directory where the ignore file and files to be excluded lives.
    """
    rules: List[IgnoreRule] = []
    full_path = Path(base_dir) / filename
    with open(full_path) as ignore_file:
        counter = 0
        for line in ignore_file:
            counter += 1
            line = line.rstrip('\n')
            rule = rule_from_pattern(
                line, base_path=Path(base_dir).resolve(), source=(full_path, counter)
            )
            if rule:
                rules.append(rule)
    if not any(r.negation for r in rules):
        return lambda file_path: any(r.match(file_path) for r in rules)
    else:
        # We have negation rules. We can't use a simple 'any' to evaluate them.
        # Later rules override earlier rules.
        return lambda file_path: handle_negation(file_path, rules)


# Frustratingly, python's fnmatch doesn't provide the FNM_PATHNAME
# option that .gitignore's behavior depends on.
def fnmatch_pathname_to_regex(pattern: str, directory_only: bool) -> str:
    """
    Implements fnmatch style-behavior, as though with FNM_PATHNAME flagged;
    the path separator will not match shell-style '*' and '.' wildcards.
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
    if not directory_only:
        res.append('$')
    return ''.join(res)
