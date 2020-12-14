#!/usr/bin/env python3
""" Autometic symbol generator class
"""
from typing import FrozenSet, List, Dict
import logging
import re
import unittest
from copy import deepcopy

class SymbolGenerator:
    """Symbol Generator

    convert symbol such as [action] in arkhamDB notation
    """
    def __init__(self):
        self._logger = logging.getLogger(type(self).__name__)
        self._re_trait = '\\[\\[([^\\[^\\]]+)\\]\\]'
        self._format_trait = '<span class="trait">{0}</span>'
        self._re = '\\[([^\\[^\\]^ ^가-힣^ㄱ-ㅎ^ㅏ-ㅣ]+)\\]' # reject KOR
        self._format = '<span title="{0}" class="icon-{0}"></span>'
        self._symbols = self._get_symbols()
        self._maps = self._get_maps()
        self._ignores = self._get_ignores()

    @staticmethod
    def _get_symbols() -> FrozenSet[str]:
        """The symbol list (if you want to convert)"""
        symbols = [
            'reaction', 'fast', 'free', 'action',
            'eldersign', 'elder_sign', 'elder_thing',
            'skull', 'auto_fail', 'cultist', 'tablet',
            'combat', 'agility', 'will', 'willpower', 'intellect', 'wild',
            'unique', 'per_investigator', 'null',
            'health', 'sanity',
            'guardian', 'mystic', 'seeker', 'rogue', 'survivor',
            'accessory', 'body', 'ally', 'hand', 'hand_2', 'arcane', 'arcane_2'
        ]
        return frozenset(symbols)

    @staticmethod
    def _get_maps() -> Dict[str, str]:
        maps = {
            'core': '기본판',
            'tdl': '던위치의 유산',
            'ptc': '카르코사로 가는 길',
            'tpa': '잊힌 시대',
            'tcu': '끝맺지 못한 의식',
            'tde': '꿈을 먹는 자',
            'tic': '인스머스에 드리운 음모',
            'nc': '너새니얼 조',
            'hw': '하비 월터스',
            'wh': '위니프리드 해버먹',
            'jf': '재클린 파인',
            'sc': '스텔라 클라크',
            'book': '서적',
            'promo': '프로모',
            'parallel': '평행'
        }
        return maps

    @staticmethod
    def _get_ignores() -> FrozenSet[str]:
        """The ignore list (if you want not to print warning message)"""
        ignores = ['endif']
        return frozenset(ignores)

    @property
    def symbols(self) -> List[str]:
        """return able tokens"""
        return list(self._symbols)

    @property
    def maps(self) -> Dict[str, str]:
        """return map"""
        return deepcopy(self._maps)

    def __call__(self, target: str) -> str:
        """search in text and convert for symbols.
        This may work by call by reference!!

        Args:
            text (str): input

        Returns:
            str: output
        """
        # traits update
        matches = list(re.finditer(self._re_trait, target))
        for match in reversed(matches):
            tagged = self._format_trait.format(match.group(1))
            target = target[:match.start()] + tagged + target[match.end():]
        
        # symbol / code update
        matches = list(re.finditer(self._re, target))
        for match in reversed(matches):
            text = match.group(1).lower()
            if text in self._ignores:
                continue
            if text in self._symbols:
                tagged = self._format.format(text)
            elif text in self._maps:
                tagged = self._maps[text]
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
            '<span title="action" class="icon-action"></span>'
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
            '<span title="action" class="icon-action"></span>: Test bird.'
        )

    def test_icons(self):
        """test most icons"""
        generator = SymbolGenerator()
        for name in ['action', 'fast', 'free', 'auto_fail', 'skull',
                     'elder_thing', 'elder_sign', 'cultist', 'tablet',
                     'combat', 'agility', 'intellect', 'willpower', 'wild']:
            self.assertEqual(
                generator("[%s]"%name),
                '<span title="%s" class="icon-%s"></span>'%(name, name)
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

if __name__ == '__main__':
    unittest.main()
