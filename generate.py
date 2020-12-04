#!/usr/bin/env python3
"""
Autometic generate code for rr_raw.html
 * table of contents
 * link
"""

import logging
import os
import re
import argparse
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO)

def main(file_input: str, file_output: str):
    """main function

    Args:
        file_input (str): path for input html file
        file_output (str): path for output txt file
    """
    logger = logging.getLogger("main")
    logger.debug("input: %s, output: %s", file_input, file_output)
    if not os.path.isfile(file_input):
        logger.critical("file %s cannot be found.")
        return

    with open(file_input) as file_pointer:
        soup = BeautifulSoup(file_pointer, 'html5lib')

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

    fp_in = open(file_input)
    fp_out = open(file_output, 'w')
    for line in fp_in:
        # ToC case
        if line.strip() == "<!-- TOC placeholder -->":
            fp_out.write(header_string)
            continue
        # otherwise: find link
        matches = [x for x in re.finditer('([0-9]+)쪽 [“"”]([가-힣 .0-9IVX]+)[“"”]', line)]
        for match in reversed(matches):
            string = match[2]
            if string not in dict_id:
                logger.warning("exported string: %s (page %d) not found.",
                               match[2], int(match[1]))
                continue
            start, end = match.start(2), match.end(2)
            tagged = '<a href="#%s">'%dict_id[string] + string + '</a>'
            line = line[:start] + tagged + line[end:]
        fp_out.write(line)
    fp_in.close()
    fp_out.close()

if __name__ == '__main__':
    PARSER = argparse.ArgumentParser(description="Auto-generator for rule-reference")
    PARSER.add_argument("input", type=str, help="path of original html")
    PARSER.add_argument("-o", "--output", type=str, default="output.html",
                        help="path of processed html")
    ARGS = PARSER.parse_args()
    main(ARGS.input, ARGS.output)
