# -*- coding: utf-8
#
# usage: python3 addlang.py lexicon.xml tag=lang [tag=lang ...]
#
#   e.g. python3 addlang.py TEMP.syang.data.xml dff=fr dfe=en dfn=ne-Latn
#
# Adds xml:lang="lang" to every element with the given tag (in entries,
# modes and subentries alike), in place. lang is a BCP 47 tag, the form
# xml:lang uses: an ISO 639 code, optionally with a script or region
# (ne-Latn = romanized Nepali), or 'und' if unknown.
#
# Tags that are not found in the file are reported on STDERR, since that
# usually means a typo in the pipeline. An existing xml:lang is replaced.
import sys
import lxml.etree as ET

XML_LANG = '{http://www.w3.org/XML/1998/namespace}lang'


def add_lang(dom, mapping):
    counts = {tag: 0 for tag in mapping}
    for element in dom.iter(*mapping):
        element.set(XML_LANG, mapping[element.tag])
        counts[element.tag] += 1
    return counts


def parse_mapping(args):
    mapping = {}
    for arg in args:
        tag, sep, lang = arg.partition('=')
        if not sep or not tag or not lang:
            sys.exit(f'addlang.py: expected tag=lang, got "{arg}"')
        mapping[tag] = lang
    return mapping


if __name__ == '__main__':
    if len(sys.argv) < 3:
        sys.exit('usage: python3 addlang.py lexicon.xml tag=lang [tag=lang ...]')
    filename = sys.argv[1]
    mapping = parse_mapping(sys.argv[2:])
    dom = ET.parse(filename)
    counts = add_lang(dom, mapping)
    for tag, n in counts.items():
        if n == 0:
            print(f'{filename}: no <{tag}> elements found', file=sys.stderr)
    output = ET.tostring(dom, xml_declaration=True, encoding='utf-8')
    with open(filename, 'wb') as output_file:
        output_file.write(output)
