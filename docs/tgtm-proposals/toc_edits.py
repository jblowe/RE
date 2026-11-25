from lxml import etree
def modify(src,dst,edits):
    t=etree.parse(src); root=t.getroot()
    for kind,*a in edits:
        if kind=='canon':
            for c in root.iter('canon'): c.set('value',a[0])
        elif kind=='addseg':
            n,lg,seg=a
            for c in root.findall('corr'):
                if c.get('num')==n:
                    for m in c.findall('modern'):
                        if m.get('dialecte')==lg:
                            segs=[s.text for s in m.findall('seg')]
                            if segs==['?'] or segs==[]:
                                for s in m.findall('seg'): m.remove(s)
                            if seg not in [s.text for s in m.findall('seg')]:
                                e=etree.SubElement(m,'seg'); e.text=seg
    t.write(dst,encoding='utf-8',xml_declaration=True)
