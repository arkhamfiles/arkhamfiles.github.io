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

def list_to_html(lst: list):
    result = ["<ul>"]
    for item in lst:
        if isinstance(item, list):
            result.append(list_to_html(item))
        else:
            result.append('<li><a href="#{}">{}</a></li>'.format(item[0], item[1]))
    result.append("</ul>")
    return " ".join(result)

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
        result += "<li><a herf=#%s>%s</a></li>\n"%(curr_id, string)

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
