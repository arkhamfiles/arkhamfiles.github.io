#!/usr/bin/env python3
""" Autometic symbol generator class
"""
import logging
import re
from typing import FrozenSet
import itertools
import unittest

from .generator import GeneratorInterface
from .defines import ICON, ICON_IGNORE, ICON_REDIRECT, EXPANSION, SYMBOLS

class SymbolGenerator(GeneratorInterface):
    """Symbol Generator

    convert symbol such as [action] in arkhamDB notation
    """

    def __init__(self):
        self._logger = logging.getLogger(type(self).__name__)
        self._re_trait = re.compile('\\[\\[([^\\[^\\]]+)\\]\\]')
        self._re_symbol = re.compile('\\[([^\\[^\\]^ ^가-힣^ㄱ-ㅎ^ㅏ-ㅣ]+)\\]')
        self._symbols_icon = ICON
        self._symbols_redirect = ICON_REDIRECT
        self._symbols_ignore = frozenset(ICON_IGNORE)
        self._symbols_symbol = SYMBOLS
        self._symbols_map = EXPANSION

    @property
    def icons(self) -> FrozenSet[str]:
        """get accepted icons as str"""
        return frozenset(itertools.chain(
            self._symbols_icon.keys(),
            self._symbols_redirect.keys(),
            self._symbols_ignore,
            self._symbols_symbol.keys(),
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
                    icon=text, title=self._symbols_icon[text]
                )
            elif text in self._symbols_symbol:
                tagged = '<span title="{title}" class="symbol-{icon}"></span>'.format(
                    icon=text, title=self._symbols_symbol[text]
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
            '<span title="기본판" class="symbol-core"></span> 38'
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
