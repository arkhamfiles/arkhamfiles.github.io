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

    header_string = generate_toc(file_input)

    file_input.seek(0)
    for line in file_input:
        # ToC case
        if line.strip() == "<!-- TOC placeholder -->":
            file_output.write(header_string)
            continue
        line = linkgen(line)
        line = symbolgen(line)
        file_output.write(line)

"""
if __name__ == '__main__':
    PARSER = argparse.ArgumentParser(description="Auto-generator for rule-reference")
    PARSER.add_argument("input", nargs='?', type=argparse.FileType('r'),
                        help="path of original html")
    PARSER.add_argument("output", nargs='?', type=argparse.FileType('w'),
                        default="output.html", help="path of processed html")
    PARSER.add_argument("--raw", action='store_true',
                        help="when you convert raw RR")
    PARSER.add_argument("-r", "--rr", type=str, default=None,
                        help="path of rr")
    PARSER.add_argument("-f", "--faq", type=str, default=None,
                        help="path of faq")
    PARSER.add_argument("-s", "--css", type=str, default=None,
                        help="path of symbol for css")
    ARGS = PARSER.parse_args()
    if ARGS.raw:
        LINKGEN = LinkGeneratorRaw(ARGS.input)
    else:
        LINKGEN = LinkGenerator(ARGS.input, ARGS.rr, ARGS.faq)
    SYMBOLGEN = SymbolGenerator(ARGS.css)
    generate(ARGS.input, ARGS.output, LINKGEN, SYMBOLGEN)
"""