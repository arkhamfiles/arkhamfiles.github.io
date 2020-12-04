#!/usr/bin/env python3
"""
Autometic generate code for rr_raw.html
  * table of contents
  * link
  * symbol like [---]

TODO
  * sanity check for symbol list
"""
from typing import Tuple, Dict
import logging
import io
import re
import argparse
import copy
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO)

def generate_toc(file_input: io.TextIOWrapper):
    """
    generate ToC string & collect header id

    Args:
        file_input (io.TextIOWrapper): file for read

    Returns:
        str: header string
        Dict[str, str]: header information (string to id)
    """
    logger = logging.getLogger('generate_toc')
    file_input.seek(0)
    soup = BeautifulSoup(file_input, 'html5lib')
    header_string = "<ul>\n"
    prev_level = 1
    dict_id: Dict[str, str] = {}
    for tag in soup.findAll(True):
        if not tag.name or tag.name[0] != 'h':
            # we only consider h#
            continue
        if not tag.has_attr('id'):
            logger.debug("NO id: %s (omit)", tag.string)
            continue
        level = int(tag.name[1:])
        curr_id = tag['id']
        string = tag.string
        if string is None:
            # when string contains icon, remove icon & ()
            string = ''.join([x if isinstance(x, str) else '' for x in tag.contents])
            string = string.replace('(', '').replace(')', '').strip()
        logger.debug("level: %d, id: %s, string: %s", level, curr_id, string)
        if curr_id == "rop":
            continue
        if curr_id[-1] != '_':
            # if not virtual id
            if string in dict_id:
                logger.warning("duplicated string: %s (%s & %s)",
                               string, dict_id[string], curr_id)
            dict_id[string] = curr_id
        if curr_id[0] == '_':
            # if no header
            continue
        while prev_level > level:
            prev_level -= 1
            header_string += "\t"*prev_level + "</ul>\n"
        while prev_level < level:
            header_string += "\t"*prev_level + "<ul>\n"
            prev_level += 1
        header_string += "\t"*level
        header_string += '<li><a href="#%s">%s</a></li>\n'%(curr_id, string)
    level = 1
    while prev_level > level:
        prev_level -= 1
        header_string += "\t"*prev_level + "</ul>\n"
    while prev_level < level:
        header_string += "\t"*prev_level + "<ul>\n"
        prev_level += 1
    header_string += "</ul>\n"
    del soup
    return header_string, dict_id

def make_symbol(text: str):
    """change symbol in text (in-place)

    Args:
        text (str): input str

    Returns:
        str: output str
    """
    matches = [x for x in re.finditer('[[]([a-z_]+)[]]', text)]
    for match in reversed(matches):
        start, end = match.start(), match.end()
        string = text[start+1:end-1]
        tagged = '<span title="{0}" class="icon-{0}"></span>'.format(string)
        text = text[:start] + tagged + text[end:]
    return text

def make_link(text: str, dict_id: Dict[str, str],
              regex_in: str, regex_out: str, idx: int):
    """make hyperlink by id map

    Args:
        text (str): target text
        dict_id (Dict[str, str]): map from text -> id
        regex_in (str): regex for search text
        regex_out (str): formatter for output text
        idx (int): the index for text in regex_in

    Returns:
        str: linked text
    """
    logger = logging.getLogger('make_link')
    matches = [x for x in re.finditer(regex_in, text)]
    for match in reversed(matches):
        groups = match.groups()
        string = groups[idx]
        if string not in dict_id:
            logger.warning("exported string: %s not found.", string)
            continue
        tagged = regex_out.format(*groups, id=dict_id[string])
        text = text[:match.start()] + tagged + text[match.end():]
    return text

def main(file_input: io.TextIOWrapper, file_output: io.TextIOWrapper,
         link_info: Tuple[str, str, int]):
    """
    main function

    Args:
        file_input (str): path for input html file
        file_output (str): path for output txt file
        link_info (str, str, int): regex, format, # of string
    """
    logger = logging.getLogger("main")
    logger.debug("input: %s, output: %s", file_input, file_output)

    header_string, dict_id = generate_toc(file_input)
    header_string = make_symbol(header_string)

    file_input.seek(0)
    for line in file_input:
        # ToC case
        if line.strip() == "<!-- TOC placeholder -->":
            file_output.write(header_string)
            continue
        line = make_link(line, dict_id, *link_info)
        line = make_symbol(line)
        file_output.write(line)

if __name__ == '__main__':
    PARSER = argparse.ArgumentParser(description="Auto-generator for rule-reference")
    PARSER.add_argument("input", nargs='?', type=argparse.FileType('r'),
                        help="path of original html")
    PARSER.add_argument("output", nargs='?', type=argparse.FileType('w'),
                        default="output.html", help="path of processed html")
    PARSER.add_argument("--raw", action='store_true',
                        help="when you convert raw RR")
    ARGS = PARSER.parse_args()
    if ARGS.raw:
        REGEX = '([0-9]+)쪽 [“"”]([가-힣 .0-9IVX~]+)[“"”]'
        FORMAT = '“<a href="#{id}">{1}</a>”'
        IDX = 1
    else:
        REGEX = '([0-9]+)쪽 [“"”]([가-힣 .0-9IVX~]+)[“"”]'
        FORMAT = '“<a href="#{id}">{1}</a>”'
        IDX = 1
    main(ARGS.input, ARGS.output, (REGEX, FORMAT, IDX))
