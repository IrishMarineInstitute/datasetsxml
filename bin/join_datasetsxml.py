#!/usr/bin/env python3
from tidyxml import tidy
import os
import sys

if __name__ == "__main__":
    filename = "{0}/../parts/_datasets.xml".format(os.path.dirname(sys.argv[0]))
    if len(sys.argv) == 2:
        filename = sys.argv[1]
    tidy(filename)

