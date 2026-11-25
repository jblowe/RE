import pickle, re, sys, collections, os
OUT = os.path.dirname(os.path.abspath(__file__))        # write next to this script; run from the dir holding accepted.pkl
# language of the glosses in each source lexicon (checked against the data files)
GLOSS_LANG = {'mar': 'fr', 'syang': 'fr', 'tang': 'fr',
              'gha': 'en', 'ris': 'en', 'sahu': 'en', 'pra': 'en', 'tag': 'en', 'tuk': 'en'}
XML_LANG = '{http://www.w3.org/XML/1998/namespace}lang'
sys.path.insert(0,'/Users/johnlowe/GitHub/RE2/src')
from mel import normalize_gloss
from lxml import etree
acc, border, st = pickle.load(open('accepted.pkl','rb'))
def heads(g):
    out=[]
    for alt in re.split(r'[;,/]', g or ''):
        alt=alt.strip()
        if not alt: continue
        n=normalize_gloss(alt)
        h=(n[0] if n else alt).lower().strip()
        if len(h)>1 and h not in ('be','do','have','get','go','make') and h not in out: out.append(h)
    return out
def components(pairs):
    parent={}
    def f(x):
        parent.setdefault(x,x)
        while parent[x]!=x:
            parent[x]=parent[parent[x]]; x=parent[x]
        return x
    ev=collections.defaultdict(list)
    langs=collections.defaultdict(set)      # head -> gloss languages of the lexicons it came from
    for sid,pf,a,b,e,w,m in pairs:
        ha,hb=heads(a['gl']),heads(b['gl'])
        if not ha or not hb: continue
        for x in ha: langs[x].add(GLOSS_LANG[a['lg']])
        for x in hb: langs[x].add(GLOSS_LANG[b['lg']])
        for x in ha+hb: f(x)
        for x in ha[1:]+hb: parent[f(x)]=f(ha[0])
        ev[f(ha[0])].append((pf,a,b,e,w,m))
    comp=collections.defaultdict(set)
    for x in list(parent): comp[f(x)].add(x)
    return comp,ev,f,langs
def write(pairs,path,prefix):
    comp,ev,f,langs=components(pairs)
    root=etree.Element('semantics')
    n=0; sizes=[]
    for r,gls in sorted(comp.items(),key=lambda kv: sorted(kv[1])[0]):
        n+=1; sizes.append(len(gls))
        evs=ev[f(next(iter(gls)))]
        exs='; '.join('%s %s "%s" ~ %s %s "%s"'%(a['lg'],a['lx'],(a['gl'] or '')[:24],b['lg'],b['lx'],(b['gl'] or '')[:24]) for pf,a,b,e,w,m in evs[:2])
        root.append(etree.Comment(' %s ' % exs.replace('--','-')))
        el=etree.SubElement(root,'mel',id='%s%d'%(prefix,n))
        for g in sorted(gls):
            gl=etree.SubElement(el,'gl'); gl.text=g
            l=langs[g]
            if len(l)==1: gl.set(XML_LANG,next(iter(l)))
            else: gl.set(XML_LANG,'xx')          # same string came from both an English and a French lexicon
    etree.ElementTree(root).write(path,encoding='utf-8',xml_declaration=True,pretty_print=True)
    print(path,n,'proposed MEL entries; sizes',collections.Counter(sizes))
write(acc,os.path.join(OUT,'TGTM.mel-additions.xml'),'p')
write(acc+border,os.path.join(OUT,'TGTM.mel-additions-loose.xml'),'q')
