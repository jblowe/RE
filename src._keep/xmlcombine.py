#!/usr/bin/env python
#
# respectfully and with appreciation pillaged from:
#
# https://stackoverflow.com/questions/9004135/merge-multiple-xml-files-from-command-line
#
# a couple minor modifications for our purposes made.

import sys
from xml.etree import ElementTree

def run(files):
    first = None
    for filename in files:
        data = ElementTree.parse(filename).getroot()
        if first is None:
            first = data
        else:
            first.append(data)
    if first is not None:
        print(ElementTree.tostring(first, encoding='unicode'))

if __name__ == "__main__":
    run(sys.argv[1:])
