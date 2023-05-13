#!/usr/bin/env python3
""" mics functions
"""
import functools
import logging
import os
import re
import unittest
from functools import reduce
from collections import deque
from dataclasses import dataclass, field
from io import StringIO, TextIOBase
from typing import Any, Callable, Iterable, List, Union, Tuple

import bs4

from .defines import EXPANSION

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
        if hasattr(file, 'name'):
            file_p = open(getattr(file, 'name'), 'r', encoding=file.encoding)
            return file_p
        else:
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
        filename = os.urandom(6).hex()
        while os.path.exists(filename):
            filename = os.urandom(6).hex()
        try:
            filep = open(filename, 'w+')
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
        finally:
            filep.close()
            os.remove(filename)

    def test_str(self):
        """load string Path or html"""
        filename = os.urandom(6).hex()
        while os.path.exists(filename):
            filename = os.urandom(6).hex()
        try:
            filep = open(filename, 'w+')
            filep.write(self._test_string)
            loaded = load_filetype(filep.name)
            self.assertFalse(loaded.closed)
            loaded.close()
        finally:
            filep.close()
            os.remove(filename)
        self.assertRaises(ValueError, load_filetype, "UNPROPER_PATH_IS_GIVEN")
        loaded = load_filetype(self._test_string)
        self.assertIsNotNone(loaded)


_re_number = re.compile("\\(([0-9]+)[.]([0-9]+)\\)")
_re_ver = re.compile("V([0-9]+)_([0-9]+)")
_exps: List[str] = list(EXPANSION.keys())
@dataclass
class _Tag:
    id: str
    contents: str
    level: int
    version: Tuple[int, int] = field(init=False, default=(1, 0))
    _expansion: int = field(init=False, default=1001)
    is_number: bool = field(init=False, default=False)
    _value: int = field(init=False, default=0)

    def __post_init__(self):
        match = _re_number.search(self.contents)
        if match:
            self.is_number = True
            self._value = int(match.group(2))
            self.contents = self.contents[match.end():]

    def update(self, targets: Iterable[str]):
        """update class information"""
        for tar in targets:
            self._update(tar)
        return self

    def _update(self, target: str):
        try:
            idx = _exps.index(target)
            if idx < self._expansion:
                self._expansion = idx
            return self
        except ValueError:
            pass
        match = _re_ver.search(target)
        if match:
            version = int(match.group(1)), int(match.group(2))
            if version[0] > self.version[0] or (version[0] == self.version[0] and version[1] > self.version[1]):
                self.version = version
            return self
        return self
    
    def done(self):
        if self._expansion > 1000:
            self._expansion = 0

    @property
    def expansion(self):
        try:
            return _exps[self._expansion]
        except:
            print("unknown expansion: ", self._expansion)
            return _exps[0]

    def __str__(self):
        classes = []
        if self._expansion > 0:
            classes.append(self.expansion)
        if self.version != (1, 0):
            classes.append("V{}_{}".format(*self.version))
        class_str = ' class="{}"'.format(' '.join(classes)) if classes else ''
        result = '<li{}'.format(class_str)
        result += ' value={}'.format(self._value) if self.is_number else ''
        result += '><a href="#{}"{}>'.format(self.id, class_str)
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

    soup = bs4.BeautifulSoup(file_p, 'html.parser')
    tags: List[_Tag] = []
    classes_ignore = frozenset([
        'rules-reference', 'errata', 'rules'
    ])
    for tag in soup.find_all(True):
        if tag.name[0] != 'h':
            if tags and tag.name != 'div' and tag.has_attr('class'):
                tags[-1].update(tag['class'])
            continue
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
        classes: List[str] = [
            x for x in tag.parent['class'] if x not in classes_ignore
        ] if tag.parent.has_attr('class') else []
        if not classes:
            classes.append('core')
        logger.debug("level: %d, id: %s, string: %s, class: %s", level, curr_id, string, classes)
        if curr_id in ids:
            continue
        if curr_id[0] == '_':
            # if no header
            continue
        if tags:
            tags[-1].done()
        tags.append(_Tag(curr_id, string, level))
        tags[-1].update(classes)

    header_string = ""
    tags_list: "deque[str]" = deque(maxlen=9)
    if sum(map(lambda x: 1 if x.level == 1 else 0, tags)) == 1:
        tags = [x for x in tags if x.level > 1]
        for tag in tags:
            tag.level -= 1
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

def check_update_necessary(base: str, want: str) -> bool:
    """check whether update is necessary based on fixed time

    Args:
        base (str): target based file
        want (str): generated

    Returns:
        bool: True if update is necessary
    """
    logger = logging.getLogger("check_update")
    if not os.path.isfile(want):
        logger.debug("target doesn't exist: %s", want)
        return True
    baseinfo = os.stat(base)
    wantinfo = os.stat(want)
    logger.debug("basetime: %d, wanttime: %d", baseinfo.st_mtime_ns, wantinfo.st_mtime_ns)
    if baseinfo.st_mtime_ns > wantinfo.st_mtime_ns:
        logger.debug("base is newer; updated")
        return True
    module_path = os.path.split(__file__)[0]
    geninfo = [os.stat(os.path.join(module_path, x)) for x in os.listdir(module_path)
               if os.path.splitext(x)[-1].lower() == '.py']
    if geninfo and max(geninfo, key=lambda x: x.st_mtime_ns).st_mtime_ns > wantinfo.st_mtime_ns:
        logger.debug("generator is newer; updated")
        return True
    logger.debug("base is older; skip")
    return False

if __name__ == '__main__':
    unittest.main()
