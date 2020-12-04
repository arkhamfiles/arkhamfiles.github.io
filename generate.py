#!/usr/bin/env python3
"""
Autometic generate code for rr_raw.html
  * table of contents
  * link
  * symbol like [---]

TODO
  * sanity check for symbol list
"""
from typing import Tuple
import logging
import io
import re
import argparse
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO)

def main(file_input: io.TextIOWrapper, file_output: io.TextIOWrapper,
         link_info: Tuple[str, str, int]):
    """main function

    Args:
        file_input (str): path for input html file
        file_output (str): path for output txt file
        link_info (str, str, int): regex, format, # of string
    """
    logger = logging.getLogger("main")
    logger.debug("input: %s, output: %s", file_input, file_output)
    soup = BeautifulSoup(file_input, 'html5lib')

    # generation of ToC
    header_string = "<ul>\n"
    prev_level = 1
    dict_id = {}
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

    file_input.seek(0)
    for line in file_input:
        # ToC case
        if line.strip() == "<!-- TOC placeholder -->":
            file_output.write(header_string)
            continue
        # find link
        matches = [x for x in re.finditer(link_info[0], line)]
        for match in reversed(matches):
            groups = match.groups()
            string = groups[link_info[2]]
            if string not in dict_id:
                logger.warning("exported string: %s not found.", string)
                continue
            tagged = link_info[1].format(*groups, id=dict_id[string])
            line = line[:match.start()] + tagged + line[match.end():]
        # find symbol
        matches = [x for x in re.finditer('[[]([a-z_]+)[]]', line)]
        for match in reversed(matches):
            start, end = match.start(), match.end()
            string = line[start+1:end-1]
            tagged = '<span title="{0}" class="icon-{0}"></span>'.format(string)
            line = line[:start] + tagged + line[end:]
        # write
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
