import os
from urllib.request import pathname2url
from lxml import etree
parser = etree.XMLParser(load_dtd=True,
                         no_network=True)

tree = etree.parse("parts/_datasets.xml", parser=parser)

#tree.write("datasets_joined.xml", pretty_print=True, doctype="<?xml version='1.0' encoding='iso-8859-1' ?>", encoding='iso-8859-1')
tree.write("datasets_joined.xml", pretty_print=True, doctype='', encoding='iso-8859-1')

