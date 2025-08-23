import lxml.etree as ET
from pprint import pprint
from collections import defaultdict

# https://stackoverflow.com/questions/2148119/how-to-convert-an-xml-string-to-a-dictionary

def etree_to_dict(t):
    d = {t.tag: {} if t.attrib else None}
    children = list(t)
    if children:
        dd = defaultdict(list)
        for dc in map(etree_to_dict, children):
            for k, v in dc.items():
                dd[k].append(v)
        d = {t.tag: {k: v[0] if len(v) == 1 else v for k, v in dd.items()}}
    if t.attrib:
        d[t.tag].update(('@' + k, v) for k, v in t.attrib.items())
    if t.text:
        text = t.text.strip()
        if children or t.attrib:
            if text:
                d[t.tag]['#text'] = text
        else:
            d[t.tag] = text
    return d


def dict_to_etree(d):
    def _to_etree(d, root):
        if not d:
            pass
        elif isinstance(d, str):
            root.text = d
        elif isinstance(d, dict) or isinstance(d, defaultdict):
            for k, v in d.items():
                assert isinstance(k, str)
                if k.startswith('#'):
                    assert k == '#text' and isinstance(v, str)
                    root.text = v
                elif k.startswith('@'):
                    # assert isinstance(v, str)
                    root.set(k[1:], str(v))
                elif isinstance(v, list):
                    for e in v:
                        _to_etree(str(e), ET.SubElement(root, k))
                else:
                    _to_etree(str(v), ET.SubElement(root, k))
        else:
            raise TypeError('invalid type: ' + str(type(d)))

    assert isinstance(d, dict) and len(d) == 1
    tag, body = next(iter(d.items()))
    node = ET.Element(tag)
    _to_etree(body, node)
    return node

