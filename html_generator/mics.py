#!/usr/bin/env python3
""" mics functions
"""
import functools
import logging
import os
import re
import tempfile
import unittest
from collections import deque
from dataclasses import dataclass, field
from io import StringIO, TextIOBase
from typing import Any, Callable, Iterable, List, Union

import bs4

FileType = Union[str, TextIOBase]

def _wrap_once(func: Callable[..., Any], func2: Callable[..., Any]) -> Callable[..., Any]:
    """First call: func2 is called, Next call: func is called

    Args:
        func (Callable): Original function
        func2 (Callable): function want to be called once
    """
    @functools.wraps(func)
    def warpper(*args: ..., **kwargs: ...):
        if not warpper.has_run:
            warpper.has_run = True
            return func2(*args, **kwargs)
        return func(*args, **kwargs)
    warpper.has_run = False
    return warpper

def load_filetype(file: FileType) -> TextIOBase:
    """load FileType

    Args:
        file (FileType): path(str), html string(str), or TextIOBase
        check (bool, optional): sanity check?. Defaults to True.

    Raises:
        ValueError: if file is wrong. only if check is True

    Returns:
        TextIOBase: output. None if not check and file is invalid.
    """
    if isinstance(file, str) and os.path.isfile(file):
        return open(file, encoding='utf-8')
    if isinstance(file, str) and all(map(lambda x: x in file, ['<', '>'])):
        return StringIO(file)
    if isinstance(file, TextIOBase):
        file_p = file
        init_pos = file.tell()
        file_p.close = _wrap_once(file_p.close, lambda: file_p.seek(init_pos))
        file_p.seek(0)
        return file_p
    raise ValueError("input seems to neither path nor html string.")

class TestFileReader(unittest.TestCase):
    """Test load_filetype class"""
    _test_string = '<html>\n<body>\n<h2 id="a">b</h2>\n</body>\n</html>'

    def test_file(self):
        """load TextIOWarper & check seek is contains after close"""
        with tempfile.NamedTemporaryFile('w+') as filep:
            filep.write(self._test_string)
            readonly = open(filep.name, encoding='utf-8')
            readonly.seek(5)
            curr_pos = readonly.tell()
            loaded = load_filetype(readonly)
            self.assertEqual(loaded.tell(), 0)
            loaded.close()
            self.assertEqual(curr_pos, readonly.tell())
            readonly.close()
            self.assertTrue(readonly.closed)

    def test_str(self):
        """load string Path or html"""
        with tempfile.NamedTemporaryFile('w+') as filep:
            filep.write(self._test_string)
            loaded = load_filetype(filep.name)
            self.assertFalse(loaded.closed)
            loaded.close()
        self.assertRaises(ValueError, load_filetype, "UNPROPER_PATH_IS_GIVEN")
        loaded = load_filetype(self._test_string)
        self.assertIsNotNone(loaded)

@dataclass
class _Tag:
    id: str
    contents: str
    level: int
    classes: List[str] = field(default_factory=list)
    is_number: bool = field(init=False, default=False)

    _pattern = re.compile("(\\([0-9]+\\.[0-9]+\\))")

    def __post_init__(self):
        match = _Tag._pattern.search(self.contents)
        if match:
            self.is_number = True
            self.contents = self.contents[match.end():]

    def __str__(self):
        str_class = ' class="{}"'.format(' '.join(self.classes)) if self.classes else ''
        result = '<li{}>'.format(str_class)
        result += '<a{} href="#{}">'.format(str_class, self.id)
        result += self.contents
        result += '</a></li>'
        return result

def generate_toc(file: FileType,
                 id_ignore: Union[str, Iterable[str], None] = None) -> str:
    """
    generate ToC string & collect header id

    Args:
        file (Union[str, TextIOBase]): path or file string or fileIO
        id_ignore (Union[str, Iterable[str], None]): id for ignore (default = 'rod')

    Returns:
        str: header string
    """
    logger = logging.getLogger('generate_toc')
    file_p = load_filetype(file)
    # id update
    if id_ignore is None:
        ids = frozenset(['rop'])
    elif isinstance(id_ignore, str):
        ids = frozenset([str(id_ignore)])
    else:
        ids = frozenset(id_ignore)

    soup = bs4.BeautifulSoup(file_p, 'html5lib')
    tags: List[_Tag] = []
    classes_ignore = frozenset([
        'rules-reference', 'errata', 'rules'
    ])
    for tag in soup.find_all(re.compile('h[0-9]')):
        if not tag.has_attr('id'):
            logger.debug("NO id: %s (omit)", tag.string)
            continue
        level = int(tag.name[1:])
        curr_id: str = tag['id']
        string: str = tag.string
        if string is None:
            # when string contains icon, remove icon & ()
            string = ''.join([x if isinstance(x, str) else '' for x in tag.contents])
            string = string.replace('(', '').replace(')', '').strip()
        classes: List[str] = [x for x in tag.parent['class'] if x not in classes_ignore]
        logger.debug("level: %d, id: %s, string: %s, class: %s", level, curr_id, string, classes)
        if curr_id in ids:
            continue
        if curr_id[0] == '_':
            # if no header
            continue
        tags.append(_Tag(curr_id, string, level, classes))

    header_string = ""
    tags_list: "deque[str]" = deque(maxlen=9)
    if sum(map(lambda x: 1 if x.level == 1 else 0, tags)) == 1:
        tags = [_Tag(x.id, x.contents, x.level-1, x.classes) for x in tags if x.level > 1]
    for tag in tags:
        while len(tags_list) > tag.level:
            curr_tag = tags_list.pop()
            header_string += "\t"*len(tags_list) + "</{}>\n".format(curr_tag)
        if len(tags_list)+1 == tag.level and tag.is_number:
            header_string += "\t"*len(tags_list) + "<ol>\n"
            tags_list.append('ol')
        while len(tags_list) < tag.level:
            header_string += "\t"*len(tags_list) + "<ul>\n"
            tags_list.append('ul')
        header_string += '\t'*tag.level
        header_string += str(tag)+'\n'
    while tags_list:
        tag = tags_list.pop()
        header_string += "\t"*len(tags_list) + "</{}>\n".format(tag)
    del soup
    file_p.close()
    return header_string
class TestToC(unittest.TestCase):
    """ToC Test"""
    def test_toc(self):
        """toc test"""
        test_string = '''
        <html><body>
        <h1 id="h1">h1</h1>
        <h2 id="h2">h2</h2>
        <h2 id="_hidden">hidden</h2>
        <h1 id="new">new</h1>
        </body></html>
        '''
        toc = generate_toc(test_string)
        self.assertIn('<a href="#h1">h1</a>', toc)
        self.assertIn('<a href="#h2">h2</a>', toc)
        self.assertNotIn('hidden', toc)
        self.assertIn('<a href="#new">new</a>', toc)

if __name__ == '__main__':
    unittest.main()
