#!/usr/bin/env python3
""" Autometic generate code
  * table of contents
  * link
  * symbol like [---]
"""

from typing import Iterable
import logging
import io
import tempfile
from functools import reduce
from .generator import GeneratorInterface
from .script_factory import ScriptRunner

def generate(file_input: io.TextIOWrapper,
             file_output: io.TextIOWrapper,
             generators: Iterable[GeneratorInterface]):
    """generate html from RAW html file

    Args:
        file_input (io.TextIOWrapper): raw html as wrapper
        file_output (io.TextIOWrapper): output html as wrapper
        generators (Iterable[GeneratorInterface]): generators to apply in raw html
    """
    logger = logging.getLogger("main")
    logger.debug("input: %s, output: %s", file_input, file_output)

    runner = ScriptRunner()

    file_input.seek(0)
    while True:
        line = file_input.readline()
        if not line:
            break
        line = line.replace("../", "") # rewind link
        line = runner(line, file_input)
        line = reduce(lambda text, gen: gen(text), generators, line)
        file_output.write(line)
