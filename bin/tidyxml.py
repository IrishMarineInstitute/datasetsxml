#!/usr/bin/env python3
import os
import sys
from lxml import etree

def parse_tree(filename):
    parser = etree.XMLParser(load_dtd=True,
                         no_network=True,
                         strip_cdata=False)
    return etree.parse(filename, parser=parser)

def tidy(filename):
    tree = parse_tree(filename)
    tree.write(sys.stdout.buffer, pretty_print=True, doctype='', encoding=tree.docinfo.encoding)

if __name__ == "__main__":
    if len(sys.argv) == 2:
        filename = sys.argv[1]
        tidy(filename)
        exit(0)
    else:
        usage = '''USAGE: {0} path/to/file.xml
        '''.format(sys.argv[0])
        print(usage , file=sys.stderr)
        exit(2)
