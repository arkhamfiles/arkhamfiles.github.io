#!/usr/bin/env python3
""" Autometic link generator class
"""
import logging
import os
import re
import tempfile
import unittest
from abc import abstractmethod
from io import StringIO, TextIOBase
from typing import Dict, Optional, Union

import bs4

from .mics import load_filetype
from .generator import GeneratorInterface

FileType = Union[str, TextIOBase]

class LinkGeneratorInterface(GeneratorInterface):
    """Abstract class for link generator

    Note: you need to override __call__
    """
    def __init__(self):
        self._logger = logging.getLogger(type(self).__name__)

    @staticmethod
    def _build_id_map(file: FileType) -> Dict[str, str]:
        file_p = load_filetype(file)
        soup = bs4.BeautifulSoup(file_p, 'html.parser')
        id_map: Dict[str, str] = {}
        for tag in soup.find_all(re.compile("h[0-9]")): #type: bs4.element.Tag
            if not tag.has_attr('id'):
                continue
            curr_id: str = tag['id']
            text = re.sub("[\\(\\[\\<].*?[\\)\\]\\>]", "", str(tag))
            text = re.sub("[\\(\\[\\<\\)\\]\\>]", "", text).strip()
            if curr_id is not None and curr_id[-1] == '_':
                continue
            id_map[text] = curr_id
        del soup
        file_p.close()
        return id_map

    @abstractmethod
    def __call__(self, text: str) -> str:
        """search in text and convert for link.
        This may work by call by reference!!

        Args:
            text (str): input

        Returns:
            str: output
        """

class LinkGeneratorRaw(LinkGeneratorInterface):
    """Link Generator for RAW RR

    (NUMBER)쪽 "TEXT" --> "<a href=#id>TEXT</a>"
    TEXT should be same as one of text in header


    example: 22쪽 "비용" --> "<a href="#Cost">비용</a>"

    """
    def __init__(self, file: FileType):
        super().__init__()
        self._text2id = self._build_id_map(file)
        self._re = re.compile('([0-9]+)쪽 [“"”]([^“^"^”]+)[“"”]')
        self._format = '"<a href="#{id}">{text}</a>"'

    def __call__(self, target: str) -> str:
        matches = list(self._re.finditer(target))
        for match in reversed(matches):
            text = match.group(2)
            if text not in self._text2id:
                self._logger.warning("text[%s] not found.", text)
                continue
            tagged = self._format.format(
                text=text, id=self._text2id[text])
            target = target[:match.start()] + tagged + target[match.end():]
        return target

class LinkGenerator(LinkGeneratorInterface):
    """default link generator

    SEARCH :
      * 링크 "TEXT" --> TEXT should be text in header. (TEXT should not contain #)
      * 링크 "TEXT#ID" --> ID should be id in header. (TEXT is fine.)
      * 참조/파큐 ~~~
    anything more?
    """
    def __init__(self, file: FileType,
                 rr: Optional[str] = None,
                 faq: Optional[str] = None,
                 out_dir: Optional[str] = None):
        super().__init__()
        if isinstance(file, str):
            _file = self._check_path(file, out_dir)
            if _file is None:
                raise ValueError('file is necessary.')
            file = _file
        rr = self._check_path(rr, out_dir)
        faq = self._check_path(faq, out_dir)
        self._text2id: Dict[str, Dict[str, str]] = {
            '링크': self._build_id_map(file),
            '참조': self._build_id_map(rr) if rr else {},
            '파큐': self._build_id_map(faq) if faq else {}
        }
        self._ids = {
            key: set(dictionary.values()) for key, dictionary in self._text2id.items()
        }
        self._paths: Dict[str, str] = {
            '링크': '',
            '참조': os.path.normpath(os.path.relpath(rr, out_dir)) if rr is not None else '',
            '파큐': os.path.normpath(os.path.relpath(faq, out_dir)) if faq is not None else ''
        }
        self._re = re.compile('(링크|참조|파큐|[0-9]+쪽) [“"”]([^“^"^”]+)[“"”]')
        self._format = '"<a href="{path}#{id}">{text}</a>"'

    def _check_path(self, path: Optional[str], out_dir: Optional[str]) -> Optional[str]:
        if path is None:
            return None
        out_dir = '.' if out_dir is None else out_dir
        if os.path.isfile(os.path.join(out_dir, path)):
            path = os.path.join(out_dir, path)
        elif not os.path.isfile(path):
            self._logger.warning("the path(%s) is not file.", path)
            return None
        #out_dir = os.curdir if out_dir is None else out_dir
        #path = os.path.normpath(os.path.relpath(path, out_dir))
        return path


    def __call__(self, target: str) -> str:
        matches = list(self._re.finditer(target))
        for match in reversed(matches):
            where = match.group(1)
            where = '링크' if where[-1] == '쪽' else where
            if where not in self._text2id:
                self._logger.warning("insane: %s", where)
                continue
            text = match.group(2).split('#')
            if len(text) == 2:
                text, curr_id = text
                if curr_id not in self._ids[where]:
                    self._logger.warning(
                        "ID[%s] not found at %s for text[%s].",
                        curr_id, where, text)
                    continue
                tagged = self._format.format(
                    id=curr_id, text=text, path=self._paths[where]
                )
                self._logger.debug("ID: %s, text: %s, where: %s, tag: %s", curr_id, text, where, tagged)
            elif len(text) == 1:
                text = text[0]
                if text not in self._text2id[where]:
                    self._logger.warning("text[%s] not found at %s.", text, where)
                    continue
                tagged = self._format.format(
                    id=self._text2id[where][text], text=text, path=self._paths[where]
                )
                self._logger.debug("text: %s, where: %s, tag: %s", text, where, tagged)
            else:
                self._logger.warning("Don't use # except for ID: %s", match.group(2))
                continue
            target = target[:match.start()] + tagged + target[match.end():]
        return target

class TestLinkGenerator(unittest.TestCase):
    """test class"""
    def test_raw_simple(self):
        """LinkGeneratorRaw -- simple case"""
        file_target = StringIO(
            '''<html><body>
            <h2 id="Chicken">치킨</h2>
            <h2 id="Pizza">피자</h2>
            <h3 id="Beer">맥주</h3>
            </body></html>'''
        )
        generator = LinkGeneratorRaw(file_target)
        self.assertEqual(
            generator('3쪽 "치킨"'),
            '"<a href="#Chicken">치킨</a>"'
        )
        self.assertEqual(
            generator('3쪽 "치킨", 9쪽 "맥주"'),
            '"<a href="#Chicken">치킨</a>", "<a href="#Beer">맥주</a>"'
        )
        self.assertEqual(
            generator('dghfongdiflm3쪽 "치킨", 9쪽 "맥주"bjoinosdf'),
            'dghfongdiflm"<a href="#Chicken">치킨</a>", "<a href="#Beer">맥주</a>"bjoinosdf'
        )

    def test_raw_strange(self):
        """LinkGeneratorRaw -- tag, symbol case"""
        file_target = StringIO(
            '''<html><body>
            <h2 id="Chicken"><b>치킨</b></h2>
            <h2 id="Pizza">피자<br></br></h2>
            <h3 id="Beer">맥주([beer])</h3>
            </body></html>'''
        )
        generator = LinkGeneratorRaw(file_target)
        self.assertEqual(
            generator('3쪽 "치킨"'),
            '"<a href="#Chicken">치킨</a>"'
        )
        self.assertEqual(
            generator('3쪽 "피자"'),
            '"<a href="#Pizza">피자</a>"'
        )
        self.assertEqual(
            generator('3쪽 "맥주"'),
            '"<a href="#Beer">맥주</a>"'
        )

    def test_simple(self):
        """LinkGenerator -- simple itself case"""
        file_target = StringIO(
            '''<html><body>
            <h2 id="Chicken">치킨</h2>
            <h2 id="Pizza">피자</h2>
            <h3 id="Beer">맥주</h3>
            </body></html>'''
        )
        generator = LinkGenerator(file_target)
        self.assertEqual(
            generator('링크 "치킨"'),
            '"<a href="#Chicken">치킨</a>"'
        )
        self.assertEqual(
            generator('3쪽 "치킨"'),
            '"<a href="#Chicken">치킨</a>"'
        )
        self.assertEqual(
            generator('링크 "시공조아#Pizza"'),
            '"<a href="#Pizza">시공조아</a>"'
        )

    def test_rrfaq(self):
        """LinkGenerator -- RR and FAQ case"""
        with tempfile.TemporaryDirectory() as folder:
            with open(os.path.join(folder, 'target.html'), 'w', encoding='utf-8') as filept:
                filept.write('''
                    <html><body>
                    <h2 id="Chicken">치킨</h2>
                    <h2 id="Pizza">피자</h2>
                    <h3 id="Beer">맥주</h3>
                    </body></html>
                ''')
            with open(os.path.join(folder, 'rr.html'), 'w', encoding='utf-8') as filept:
                filept.write(
                    '<html><body><h2 id="Chicken">치킨</h2></body></html>'
                    )
            with open(os.path.join(folder, 'faq.html'), 'w', encoding='utf-8') as filept:
                filept.write(
                    '<html><body><h2 id="Chicken">치킨</h2></body></html>'
                    )
            generator = LinkGenerator(
                'target.html', 'rr.html', 'faq.html', folder
            )
            self.assertEqual(
                generator('링크 "치킨"'),
                '"<a href="#Chicken">치킨</a>"'
            )
            self.assertEqual(
                generator('참조 "치킨"'),
                '"<a href="rr.html#Chicken">치킨</a>"'
            )
            self.assertEqual(
                generator('파큐 "치킨"'),
                '"<a href="faq.html#Chicken">치킨</a>"'
            )
