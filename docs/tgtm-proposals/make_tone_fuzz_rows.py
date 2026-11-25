import re,unicodedata
from lxml import etree
from collections import defaultdict
sup='⁰¹²³⁴⁵'
SRC='sandbox2/TGTM/'
fz=etree.parse(SRC+'TGTM.fuzzy.fuz.xml'); root=fz.getroot()
have={(it.get('dial'),f.text) for it in root.iter('item') for f in it.findall('from')}
def first_tone(s): return re.match('['+sup+']+',s).group(0)
def cls(lg,s):
    f=first_tone(s); h=int(unicodedata.digit(f[0]))
    if lg=='mar':
        return '³' if h<=2 else '˥'
    # syang, following the existing single-tone rows
    if f=='⁵¹': return 'X'
    if f=='³³': return 'X'
    if h>=4 or f=='³⁴': return '˥'
    return '˩'
new={}
for lg in ('mar','syang'):
    t=etree.parse(SRC+'TGTM.%s.data.xml'%lg)
    for e in t.iterfind('entry'):
        hw=e.find('hw')
        if hw is None: continue
        m=re.match(r"^((?:["+sup+"]+')*["+sup+"]+)",(hw.text or '').strip())
        if m and "'" in m.group(1) and (lg,m.group(1)) not in have: new[(lg,m.group(1))]=cls(lg,m.group(1))
g=defaultdict(list)
for (lg,s),c in new.items(): g[(lg,c)].append(s)
for (lg,c),L in sorted(g.items()):
    it=etree.SubElement(root,'item',dial=lg,to=c)
    for s in sorted(L): etree.SubElement(it,'from').text=s
    print(lg,c,len(L))
fz.write(SRC+'TGTM.fuzzy2.fuz.xml',encoding='utf-8',xml_declaration=True,pretty_print=True)
# also write a human-readable proposal
with open('fuzzy-tone-proposal.tsv','w') as o:
    o.write('lg\tfrom\tto\n')
    for (lg,s),c in sorted(new.items()): o.write('%s\t%s\t%s\n'%(lg,s,c))
