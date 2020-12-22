#!/usr/bin/env python3
""" Autometic symbol generator class
"""
import logging
import re
import unittest
from enum import Enum, auto

from .generator import GeneratorInterface
from .defines import EXPANSION

class _State(Enum):
    UNKNOWN = auto()
    CHAIN = auto()
    MUTATE = auto()
    MUTATE_ITEM = auto()
    FORBIDDEN = auto()

class TabooGenerator(GeneratorInterface):
    """Symbol Generator

    auto-generation of expansion class for taboo list
    """
    def __init__(self):
        self._logger = logging.getLogger('taboo_generator')
        self._expansion = frozenset(EXPANSION.keys())
        self._re_header = re.compile('<h[0-9] id="(.+)">(.+)</h[0-9]>')
        self._re_text = re.compile('<li>.+\\(\\[([a-z]+)\\] [0-9]+\\)')
        self._re_mutate_end = re.compile('</tbody></table>')
        self.state = _State.UNKNOWN

    def _check_cycle(self, cycle: str):
        if cycle not in self._expansion:
            self._logger.warning('unknown cycle: %s', cycle)
        if cycle in ['nc', 'hw', 'wh', 'jf', 'sc']:
            cycle = 'starter'
        return cycle

    def __call__(self, text: str) -> str:
        match = self._re_header.search(text)
        if match:
            curr_id = match.group(1)
            content = match.group(2)
            if 'chained' in curr_id or '속박' in content:
                self.state = _State.CHAIN
            if 'mutated' in curr_id or '변형' in content:
                self.state = _State.MUTATE
            if 'forbidden' in curr_id or '금지' in content:
                self.state = _State.FORBIDDEN
        elif self.state in [_State.CHAIN, _State.FORBIDDEN]:
            match = self._re_text.search(text)
            if match:
                cycle = self._check_cycle(match.group(1))
                text = text[:match.start()] +\
                       '<li class="{}">'.format(cycle) +\
                       text[match.start()+4:]
        elif self.state == _State.MUTATE:
            match = self._re_text.search(text)
            if match:
                cycle = self._check_cycle(match.group(1))
                text = text[:match.start()] +\
                       '<div class="{}">'.format(cycle) +\
                       text[match.start():]
                self.state = _State.MUTATE_ITEM
        elif self.state == _State.MUTATE_ITEM:
            match = self._re_mutate_end.search(text)
            if match:
                text = text[:match.end()] + '</div>' + text[match.end():]
                self.state = _State.MUTATE
        return text

class TestTabooGenerator(unittest.TestCase):
    """test taboo generator"""
    def test_header(self):
        """test header parsing"""
        generator = TabooGenerator()
        text = '    <h3 id="V1_chained">속박</h3>'
        generator(text)
        self.assertEqual(
            generator.state, _State.CHAIN
        )

    def test_chained(self):
        """test chained parsing"""
        generator = TabooGenerator()
        generator('<h3 id="V1_chained">속박</h3>')
        self.assertEqual(generator.state, _State.CHAIN)
        self.assertEqual(
            generator('    <li>접이식 칼 (레벨 2) ([tdl] 152): +1 경험치</li>'),
            '    <li class="tdl">접이식 칼 (레벨 2) ([tdl] 152): +1 경험치</li>'
        )

    def test_mutated(self):
        """test mutated parsing"""
        generator = TabooGenerator()
        generator('<h3 id="V1_mutated">변형</h3>')
        self.assertEqual(generator.state, _State.MUTATE)
        generator('<p>변형 범주의 카드는 아래와 같이 문구가 추가되거나 바뀝니다.</p>')
        generator('<ul>')
        self.assertEqual(
            generator('    <li>밀란 크리스토퍼 박사 ([core] 33)</li>'),
            '    <div class="core"><li>밀란 크리스토퍼 박사 ([core] 33)</li>'
        )
        self.assertEqual(generator.state, _State.MUTATE_ITEM)
        self.assertEqual(
            generator('    </tbody></table>'),
            '    </tbody></table></div>'
        )
        self.assertEqual(generator.state, _State.MUTATE)

if __name__ == '__main__':
    unittest.main()
