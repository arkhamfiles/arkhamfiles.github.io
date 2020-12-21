#!/usr/bin/env python3
""" Autometic symbol generator class
"""
import logging
import re
from typing import FrozenSet
import itertools
import unittest

class SymbolGenerator:
    """Symbol Generator

    convert symbol such as [action] in arkhamDB notation
    """
    _symbols_icon = {
        'reaction': '반응 격발', 'free': '자유 격발', 'action': '행동 격발',
        'elder_sign': '고대 표식', 'elder_thing': '옛것',
        'skull': '해골', 'auto_fail': '자동 실패',
        'cultist': '추종자', 'tablet': '석판',
        'bless': '축복', 'curse': '저주',
        'combat': '힘', 'agility': '민첩',
        'willpower': '의지', 'intellect': '지식', 'wild': '만능',
        'unique': '고유', 'per_investigator': '조사자당', 'null': '–',
        'guardian': '수호자', 'mystic': '신비주의자',
        'seeker': '탐구자', 'rogue': '무법자', 'survivor': '생존자'
    }
    _symbols_redirect = {
        'fast': 'free', 'elder_sign': 'elder_sign', 'elderthing': 'elder_thing',
        'autofail': 'auto_fail', 'will': 'willpower'
    }
    _symbols_ignore = frozenset([
        'endif', 'accessory', 'body', 'ally', 'hand', 'hand_2',
        'arcane', 'arcane_2', 'health', 'sanity'
    ])
    _symbols_map = {
        'core': '기본판',
        'tdl': '던위치의 유산',
        'tptc': '카르코사로 가는 길',
        'tfa': '잊힌 시대',
        'tcu': '끝맺지 못한 의식',
        'tde': '꿈을 먹는 자',
        'tic': '인스머스에 드리운 음모',
        'starter': '초심자 덱',
        'nc': '너새니얼 조',
        'hw': '하비 월터스',
        'wh': '위니프리드 해버먹',
        'jf': '재클린 파인',
        'sc': '스텔라 클라크',
        'book': '서적',
        'promo': '프로모',
        'parallel': '평행'
    }

    def __init__(self):
        self._logger = logging.getLogger(type(self).__name__)
        self._re_trait = re.compile('\\[\\[([^\\[^\\]]+)\\]\\]')
        self._re_symbol = re.compile('\\[([^\\[^\\]^ ^가-힣^ㄱ-ㅎ^ㅏ-ㅣ]+)\\]')

    @property
    def icons(self) -> FrozenSet[str]:
        """get accepted icons as str"""
        return frozenset(itertools.chain(
            self._symbols_icon.keys(),
            self._symbols_redirect.keys(),
            self._symbols_ignore,
            self._symbols_map.keys()
        ))

    def __call__(self, target: str) -> str:
        """search in text and convert for symbols.
        This may work by call by reference!!

        Args:
            text (str): input

        Returns:
            str: output
        """
        # traits update
        matches = list(self._re_trait.finditer(target))
        for match in reversed(matches):
            tagged = '<span class="trait">{0}</span>'.format(match.group(1))
            target = target[:match.start()] + tagged + target[match.end():]

        # symbol / code update
        matches = list(self._re_symbol.finditer(target))
        for match in reversed(matches):
            text = match.group(1).lower()
            if text in self._symbols_ignore:
                continue
            if text in self._symbols_redirect:
                text = self._symbols_redirect[text]
            if text in self._symbols_icon:
                tagged = '<span title="{title}" class="icon-{icon}"></span>'.format(
                    icon = text, title = self._symbols_icon[text]
                )
            elif text in self._symbols_map:
                tagged = self._symbols_map[text]
            else:
                self._logger.warning("cannot find symbol [%s]", text)
                continue
            target = target[:match.start()] + tagged + target[match.end():]
        return target

class TestSymbolGenerator(unittest.TestCase):
    """test class"""
    def test_single(self):
        """single word test"""
        generator = SymbolGenerator()
        self.assertEqual(
            generator("[action]"),
            '<span title="행동 격발" class="icon-action"></span>'
        )

    def test_code(self):
        """map test"""
        generator = SymbolGenerator()
        self.assertEqual(
            generator("[core] 38"),
            '기본판 38'
        )

    def test_trait(self):
        """trait test"""
        generator = SymbolGenerator()
        self.assertEqual(
            generator("[[마법]]"),
            '<span class="trait">마법</span>'
        )

    def test_sentense(self):
        """in sentense"""
        generator = SymbolGenerator()
        self.assertEqual(
            generator("[action]: Test bird."),
            '<span title="행동 격발" class="icon-action"></span>: Test bird.'
        )

    def test_icons(self):
        """test most icons"""
        generator = SymbolGenerator()
        for name in ['action', 'free', 'auto_fail', 'skull',
                     'elder_thing', 'elder_sign', 'cultist', 'tablet',
                     'combat', 'agility', 'intellect', 'willpower', 'wild']:
            self.assertIn(
                'class="icon-%s"'%name,
                generator("[%s]"%name)
            )

    def test_reject(self):
        """false icon case"""
        logging.basicConfig(level=logging.CRITICAL)
        generator = SymbolGenerator()
        for name in ['chicken', 'pizza', 'bird']:
            self.assertEqual(
                generator("[%s]"%name),
                "[%s]"%name
            )

    def test_property(self):
        """test property"""
        generator = SymbolGenerator()
        icons = generator.icons
        self.assertIn('free', icons)
        self.assertIn('fast', icons)
        self.assertIn('endif', icons)
        self.assertIn('core', icons)

if __name__ == '__main__':
    unittest.main()
