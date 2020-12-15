#!/usr/bin/env python3
""" mics functions
"""
import functools
import logging
import os
import tempfile
import unittest
from io import StringIO, TextIOBase
from typing import Iterable, Union, Callable, Any, List

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


def generate_toc(file: FileType,
                 id_ignore: Union[str, Iterable[str], None] = None) -> str:
    """
    generate ToC string & collect header id

    Args:
        file (Union[str, TextIOBase]): path or file string or fileIO

    Returns:
        str: header string
    """
    logger = logging.getLogger('generate_toc')
    file_p = load_filetype(file)
    # id update
    ids = set()
    if id_ignore is None:
        ids.add('rop')
    elif isinstance(id_ignore, str):
        ids.add(str(id_ignore))
    else:
        ids.update(id_ignore)

    soup = bs4.BeautifulSoup(file, 'html5lib')
    header_string: str = "<ul>\n"
    prev_level = 1

    for tag in soup.findAll(True):
        if not tag.name or tag.name[0] != 'h':
            # we only consider h#
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
        classes: List[str] = [x for x in tag.parent['class'] if x != 'rules-reference']
        logger.debug("level: %d, id: %s, string: %s, class: %s", level, curr_id, string, classes)
        if curr_id == "rop":
            continue
        if curr_id[0] == '_':
            # if no header
            continue
        while prev_level > level:
            prev_level -= 1
            header_string += "\t"*prev_level + "</ul>\n"
        while prev_level < level:
            header_string += "\t"*prev_level + "<ul>\n"
            prev_level += 1
        header_string += "\t"*level
        header_string += '<li{cls}><a href="#{id}"{cls}>{text}</a></li>\n'.format(
            cls = ' class="'+' '.join(classes)+'"' if classes else '',
            id = curr_id,
            text = string
        )
    level = 1
    while prev_level > level:
        prev_level -= 1
        header_string += "\t"*prev_level + "</ul>\n"
    while prev_level < level:
        header_string += "\t"*prev_level + "<ul>\n"
        prev_level += 1
    header_string += "</ul>\n"
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
