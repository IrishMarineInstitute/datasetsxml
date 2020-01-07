#!/usr/bin/env python3
import sys
from lxml import etree
import os

def parse_tree(filename):
    parser = etree.XMLParser(load_dtd=True,
                         no_network=True,
                         strip_cdata=False,
                         remove_blank_text=True)
    return etree.parse(filename, parser=parser)

def diff_datasets(a,b):
    diffs = []
    datasets = {}
    for dataset in a.findall("dataset"):
        datasets[dataset.get("datasetID")] = etree.tostring(dataset)
    for dataset in b.findall("dataset"):
        id = dataset.get("datasetID")
        if id in datasets and etree.tostring(dataset) == datasets[id]:
            pass
        else:
            diffs.append(id)
        del datasets[id]
    for id in datasets.keys():
        diffs.append(id)
    return diffs

if __name__ == "__main__":
    if len(sys.argv) == 3:
        for filename in sys.argv[1:]:
            if not os.path.isfile(filename):
                print("File not found: {0}".format(filename), file=sys.stderr)
                exit(1)
        a = parse_tree(sys.argv[1])
        b = parse_tree(sys.argv[2])
        for datasetID in diff_datasets(a,b):
            print(datasetID)
        exit(0)
    else:
        usage = '''USAGE: {0} path/to/A-datsets.xml path/to/B-datasets.xml
        '''.format(sys.argv[0])
        print(usage , file=sys.stderr)
        exit(2)
