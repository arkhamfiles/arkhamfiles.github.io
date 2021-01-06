#!/usr/bin/env python3
import argparse
import logging
import time
import html_generator

def main():
    """main"""
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger('main')
    parser = argparse.ArgumentParser(description="Auto-generator for rule-reference")
    parser.add_argument("input", nargs='?', type=str,
                        help="path of original html")
    parser.add_argument("output", nargs='?', type=str,
                        default="output.html", help="path of processed html")
    parser.add_argument("--raw", action='store_true',
                        help="when you convert raw RR")
    parser.add_argument("-r", "--rr", type=str, default=None,
                        help="path of rr")
    parser.add_argument("-f", "--faq", type=str, default=None,
                        help="path of faq")
    parser.add_argument("--nolink", action='store_true',
                        help="when you disable link")
    parser.add_argument("--reference", action='store_true',
                        help="only if reference generation")
    args = parser.parse_args()
    is_update = html_generator.check_update_necessary(args.input, args.output)
    if not is_update:
        print('%s is not updated (no update exists).'%args.output)
        return
    start_time = time.time()
    args.input = open(args.input, 'r', encoding='utf-8')
    args.output = open(args.output, 'w', encoding='utf-8')
    if args.reference:
        logger.debug('reference generation')
        html_generator.generate_reference(
            args.input, args.output, args.rr, args.faq
        )
        return
    generators = []
    if args.nolink:
        logger.debug('nolink flaged')
    elif args.raw:
        logger.debug('raw flaged. input: %s', args.input)
        generators.append(html_generator.LinkGeneratorRaw(args.input))
    else:
        logger.debug('default. input: %s, rr: %s, faq: %s',
                     args.input, args.rr, args.faq)
        generators.append(html_generator.LinkGenerator(args.input, args.rr, args.faq))
    if args.output.name == 'taboo.html':
        generators.append(html_generator.TabooGenerator())
    generators.append(html_generator.SymbolGenerator())
    html_generator.generate(args.input, args.output, generators)
    args.input.close()
    args.output.close()
    print('generate done: %.2fms'%(time.time()-start_time)*1000)

main()
