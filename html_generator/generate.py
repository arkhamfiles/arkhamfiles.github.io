#!/usr/bin/env python3
""" Autometic generate code
  * table of contents
  * link
  * symbol like [---]
"""

from typing import Iterable
import logging
import io
from functools import reduce
from .mics import generate_toc
from .generator import GeneratorInterface

def generate(file_input: io.TextIOWrapper,
             file_output: io.TextIOWrapper,
             generators: Iterable[GeneratorInterface]):
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
    toc = reduce(lambda text, gen: gen(text), generators, toc)

    file_input.seek(0)
    for line in file_input:
        # ToC case
        line = line.replace("../", "") # rewind link
        if line.strip() == "<!-- TOC placeholder -->":
            file_output.write(toc)
            continue
        line = reduce(lambda text, gen: gen(text), generators, line)
        file_output.write(line)
