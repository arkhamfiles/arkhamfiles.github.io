#!/usr/bin/env python3
""" Autometic symbol generator class
"""
from typing import FrozenSet, List, Dict, MutableSet, Optional
import logging
import re
import os
import unittest

class SymbolGenerator:
    """Symbol Generator

    convert symbol such as [action] in arkhamDB notation
    """
    def __init__(self):
        self._logger = logging.getLogger(type(self).__name__)
        self._re = '\\[([^\\[^\\]^ ^가-힣^ㄱ-ㅎ^ㅏ-ㅣ]+)\\]' # reject KOR
        self._format = '<span title="{0}" class="icon-{0}"></span>'
        self._symbols = self._get_symbols()
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
    def _get_ignores() -> FrozenSet[str]:
        """The ignore list (if you want not to print warning message)"""
        ignores = ['endif']
        return frozenset(ignores)

    """
    @staticmethod
    def _get_symbols(path_css: str) -> FrozenSet[str]:
        candidates: MutableSet[str] = set()
        with open(path_css) as filept:
            prop: Dict[str, str] = {}
            items: List[str] = []
            for line in filept:
                line = line.strip()
                if '{' in line:
                    line = line.replace('{', '').strip()
                    items = [x.strip() for x in line.split(',')]
                    prop = {}
                    continue
                if '}' not in line:
                    if ':' in line:
                        splited = line.replace(';', '').strip().split(':')
                        if len(splited) == 2:
                            prop[splited[0]] = splited[1]
                    continue
                if not any(map(lambda x: '.icon' in x, items)):
                    continue
                if not any(map(lambda x: x in prop, ['content', 'background-image'])):
                    continue
                for item in items:
                    match = re.search("\\.icon-([a-z_]+)(:[:]||[$])", item)
                    candidates.add(match.group(1))
        return frozenset(candidates)
    """

    @property
    def symbols(self) -> List[str]:
        """return able tokens"""
        return list(self._symbols)

    def __call__(self, target: str) -> str:
        """search in text and convert for symbols.
        This may work by call by reference!!

        Args:
            text (str): input

        Returns:
            str: output
        """
        matches = list(re.finditer(self._re, target))
        for match in reversed(matches):
            text = match.group(1)
            if text in self._ignores:
                continue
            if text not in self._symbols:
                self._logger.warning('unknown symbol name: %s', text)
                continue
            tagged = self._format.format(text)
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
