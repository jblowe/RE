import sys, math, pickle, collections, itertools, re
sys.path.insert(0,'/Users/johnlowe/GitHub/RE2/src')
from lxml import etree
import mel as M
from nltk.corpus import wordnet as wn
SRC={'hand':'sandbox/TGTM/TGTM.hand.mel.xml','ext':'sandbox/TGTM/TGTM.hand-extended-v4.mel.xml',
     'clics':'sandbox/TGTM/TGTM.clics.mel.xml','wordnet':'sandbox/TGTM/TGTM.wordnet.mel.xml',
     'stedt':'sandbox/TGTM/TGTM.s94_stedt-reduced.mel.xml','semkey':'sandbox/TGTM/TGTM.s94_stedtsemkey.mel.xml'}
index={}; msize={}
import os
SKIP=set(os.environ.get('SKIP_SRC','').split(','))
for name,p in SRC.items():
    if name in SKIP: continue
    idx=collections.defaultdict(set)
    for m in etree.parse(p).getroot().findall('mel'):
        gl=[g.text for g in m.findall('gl') if g.text]
        mid=(name,m.get('id')); msize[mid]=len(gl)
        for g in gl:
            for c in M._candidates_lower(g): idx[c].add(mid)
    index[name]=idx
_cand={}
def cands(g):
    if g not in _cand: _cand[g]=M._candidates_lower(g) if g else frozenset()
    return _cand[g]
def mel_votes(g1,g2):
    c1,c2=cands(g1),cands(g2); out={}
    for name,idx in index.items():
        m1=set().union(*[idx.get(c,set()) for c in c1]) if c1 else set()
        m2=set().union(*[idx.get(c,set()) for c in c2]) if c2 else set()
        sh=m1&m2
        if sh: out[name]=min(msize[x] for x in sh)
    return out
_syn={}
def syns(g):
    if g in _syn: return _syn[g]
    S=set()
    for c in list(cands(g))[:6]:
        if len(c.split())>3: continue
        w=c.replace(' ','_')
        for lang in ('eng','fra'):
            try: S.update(wn.synsets(w,lang=lang)[:4])
            except Exception: pass
    _syn[g]=S; return S
def wn_vote(g1,g2):
    s1,s2=syns(g1),syns(g2)
    if s1&s2: return 'syn'
    best=0
    for a in list(s1)[:6]:
        for b in list(s2)[:6]:
            if a.pos()==b.pos() and a.pos() in 'nv':
                try: best=max(best,a.wup_similarity(b) or 0)
                except Exception: pass
    return 'wup' if best>=0.9 else None
def score(g1,g2):
    v=mel_votes(g1,g2); w=wn_vote(g1,g2)
    nsrc=len(v); small=any(s<=8 for s in v.values())
    if (nsrc>=2 and small) or (nsrc>=1 and w=='syn'): tier='A'
    elif nsrc>=2 or (nsrc==1 and small) or w=='syn': tier='B'
    elif nsrc==1 or w=='wup': tier='C'
    else: tier=None
    return tier,v,w
if __name__=='__main__':
    st,forms,sets=pickle.load(open('best_strict.pkl','rb')); stn,formsn,setsn=pickle.load(open('best_nomel.pkl','rb'))
    # reconstruction per nomel set
    pairs=collections.defaultdict(set)   # (i,j)-> set of pfm
    for s in setsn:
        for i in s['sf']:
            for j in s['sf']:
                if formsn[i][0]!=formsn[j][0]: pairs[(i,j)].update(s['pfm'])
    iso=set(i for i,v in st.items() if v=='iso')
    res=collections.defaultdict(list)
    cache={}
    n=0
    for (i,j),pf in pairs.items():
        if i not in iso: continue
        g1,g2=formsn[i][2],formsn[j][2]
        k=(g1,g2)
        if k not in cache: cache[k]=score(g1,g2)
        t,v,w=cache[k]
        if t: res[i].append((t,j,sorted(pf)[:3],v,w))
    pickle.dump(dict(res),open('placements.pkl','wb'))
    tiers=collections.Counter()
    for i,l in res.items():
        best=min(t for t,*_ in l); tiers[best]+=1
    print('isolates with a scored partner, by best tier:',dict(tiers),'of',len(iso),'; gloss pairs scored',len(cache))
