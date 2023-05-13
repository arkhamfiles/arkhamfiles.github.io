#!/usr/bin/env python3
""" Autometic generate code
  reference.html only
"""

from typing import Iterable
import logging
import re
import bs4
from .mics import FileType, load_filetype
from .link_generator import LinkGenerator
from .symbol_generator import SymbolGenerator

def load_file(file: FileType):
    logger = logging.getLogger('load_file')
    file_p = load_filetype(file)
    soup = bs4.BeautifulSoup(file_p, 'html.parser')
    filept = open('output.txt', 'w', encoding='utf-8')
    re_h = re.compile('h[0-9]')
    tags: Iterable[bs4.element.ResultSet] = soup.find_all([re_h, 'p', 'ul', 'ol'])
    for tag in tags:
        name: str = tag.name
        print('-'*10, file=filept, sep='\n')
        print('name: {}, id: {}, length: {}'.format(
            tag.name, tag['id'] if tag.has_attr('id') else '-', len(tag.contents)
            ), file=filept, sep='\n')
        print(tag, file=filept, sep='\n\n')
    filept.close()

def generate_reference(filein: FileType, fileout: FileType, rr: str, faq: str):
    rr = load_file(rr)
    faq = load_file(faq)

