import glob
import time
import os
import lxml.etree as ET
import xml2dict
from collections import defaultdict

run_date = time.asctime()

def walk(files):
    results = ET.Element('stats')
    ET.SubElement(results, 'createdat').text = run_date
    language_stats = defaultdict(dict)
    totals = defaultdict(dict)
    for x, filename in enumerate(files):
        root = ET.parse(filename).getroot()
        stats_dict = xml2dict.etree_to_dict(root)
        # pprint(stats_dict)
        stats = stats_dict['stats']
        for t in stats.keys():
            if t == 'totals':
                for i in stats['totals']:
                    totals[i][f'v{x}'] = stats['totals'][i]['@value']
            elif t == 'lexicon':
                for i in stats['lexicon']:
                    language = i['@language']
                    for stat in i.keys():
                        if not language in language_stats[stat]:
                            language_stats[stat][language] = defaultdict(dict)
                        if stat != '@language':
                            language_stats[stat][language][f'v{x}'] = i[stat]['@value']

    lexicons = [{'@type': l, 'lgs': language_stats[l]} for l in language_stats.keys()]

    return {'stats': {'file': files, 'totals': totals, 'stat': lexicons}}


def compare(project_dir, project, what_to_compare):
    compare_xml_files = os.path.join(project_dir, f'{project}.*.statistics.xml')
    files = sorted(glob.glob(compare_xml_files))
    files = [f for f in files if what_to_compare in f and 'compare' not in f]

    if len(files) > 1:
        root = xml2dict.dict_to_etree(walk(files))

        with open(f'{project_dir}/{project}.{what_to_compare}.compare.xml', 'w', encoding='utf-8') as f:
            f.write(ET.tostring(root, pretty_print=True, encoding='unicode'))
