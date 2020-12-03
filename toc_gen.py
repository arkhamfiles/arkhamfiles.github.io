# /usr/local/bin python3
import sys
import logging
import os
import argparse
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO)
parser = argparse.ArgumentParser(description="Auto-generator of table of contents for HTML file")
parser.add_argument("input", type=str, help="path to generate ToC (html)")
parser.add_argument("-o", "--output", type=str, default="output.txt",
                    help="output text path for ToC")

def main(file_input: str, file_output: str):
    logger = logging.getLogger("main")
    logger.debug("input: %s, output: %s", file_input, file_output)
    if not os.path.isfile(file_input):
        logger.critical("file %s cannot be found.")
        return

    with open(file_input) as fp:
        soup = BeautifulSoup(fp, 'html5lib')

    result = "<ul>\n"

    prev_level = 1
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
        if curr_id == "rop":
            logger.info("skip toc header. level: %d, id: %s, string: %s",
                        level, curr_id, string)
            continue
        logger.debug("level: %d, id: %s, string: %s", level, curr_id, string)

        while prev_level > level:
            prev_level -= 1
            result += "\t"*prev_level + "</ul>\n"
        while prev_level < level:
            result += "\t"*prev_level + "<ul>\n"
            prev_level += 1
        result += "\t"*level
        result += '<li><a href="#%s">%s</a></li>\n'%(curr_id, string)

    level = 1
    while prev_level > level:
        prev_level -= 1
        result += "\t"*prev_level + "</ul>\n"
    while prev_level < level:
        result += "\t"*prev_level + "<ul>\n"
        prev_level += 1
    result += "</ul>\n"
    with open(file_output, 'w') as fp:
        fp.write(result)

if __name__ == '__main__':
    args = parser.parse_args()
    main(args.input, args.output)
