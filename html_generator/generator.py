#!/usr/bin/env python3
""" Autometic generate code
  * table of contents
  * link
  * symbol like [---]
"""
import logging
import io
from .mics import generate_toc
from .link_generator import LinkGeneratorInterface
from .symbol_generator import SymbolGenerator

def generate(file_input: io.TextIOWrapper,
             file_output: io.TextIOWrapper,
             linkgen: LinkGeneratorInterface,
             symbolgen: SymbolGenerator):
    """
    generate function

    Args:
        file_input (str): path for input html file
        file_output (str): path for output txt file
        linkgen (LinkGenerator): link generator
        symbolgen (SymbolGenerator): symbol generator
    """
    logger = logging.getLogger("main")
    logger.debug("input: %s, output: %s", file_input, file_output)

    toc = generate_toc(file_input)
    toc = symbolgen(toc)

    file_input.seek(0)
    for line in file_input:
        # ToC case
        line = line.replace("../", "") # rewind link
        if line.strip() == "<!-- TOC placeholder -->":
            file_output.write(toc)
            continue
        line = linkgen(line)
        line = symbolgen(line)
        file_output.write(line)
