# -*- coding: utf-8 -*-

import sys
import re
import csv
import collections

skip = r'[\(\)\*,\-\./<>\[\] ]'
tones = r'([ABCDXHL0123456789]?’??[ab]?)$'
cons = r'([^GKMNORSWZbcdfghjklmnqpqrstvwxyzɟɢʁɲȡʥɬɦɳʐʔʨɣȴɴȶʑʃʈɭʂɕȵŋθð ̥]*)'
notrimes = r'^([ABCDXHL0123456789DGHKMNORSWXZbcdfghjklmnpqrstvwxyzɟɢʁɲȡʥɬɦɳʐʔʨɣȴɴȶʑʃʈɭʂɕȵŋθð ̥]*)'


LANGUAGES = ['lg'+ str(i+1) for i in range(11)]
NLG = len(LANGUAGES)

def make_header(prefix):
    return prefix.split(',') + LANGUAGES

def try_match(thing):
    try:
        x = re.search(r'(.*?)' + tones, thing)
        tone = x[2]
        y =  re.search(notrimes + r'(.*)', x[1])
        initial = y[1]
        rime = y[2]
        return initial, rime, tone
    except:
        return thing,'',''

def make_corrs(row):
    row = row[4:]
    row[1] = ''
    clean_row = [re.sub(skip, '', r) for r in row]
    best_row = [try_match(r) for r in clean_row]
    ic = ['I'] + [r[0] for r in best_row]
    rc = ['R'] + [r[1] for r in best_row]
    tc = ['T'] + [r[2] for r in best_row]
    #ic = ['I'] + [re.sub(cons, '', r) for r in clean]
    #rc = ['R'] + [re.sub(notrimes, '', r) for r in clean]
    return tc, ic, rc


def filter_corrs(corrs):
    ancestor = collections.defaultdict(list)
    for corr in corrs:
        if corr[1] == '': corr[1] = 'U'
        ancestor[corr[1]].append(corr)
    new_corrs = []
    for key in sorted(ancestor):
        this_one = [[] for i in range(NLG + 5)]
        for corr in ancestor[key]:
            for i,c in enumerate(corr):
                if c == '': continue
                if c in this_one[i]: continue
                this_one[i].append(c)
        # this is the needed 'context' column, blank for now
        #this_one.insert(1, '')
        new_corrs.append(tuple(this_one))
    return new_corrs


i = 0
tcs = []
ics = []
rcs = []

with open(sys.argv[1],'r') as input_file:
    with open(sys.argv[2],'w') as f1:
        with open(sys.argv[3],'w') as f2:
            output_file = csv.writer(f1, delimiter='\t')

            header = make_header('id,gloss,PHM,class')
            output_file.writerow(header)

            corr_file = csv.writer(f2, delimiter='\t')
            header = make_header('id,level,type,proto,context')
            corr_file.writerow(header)

            for row in csv.reader(input_file, delimiter='\t'):
                if len(row) > 3:
                    #if row[1] in 'D E'.split(' '):
                    if row[1] == 'D':
                        i += 1
                        row = [r.replace('--','') for r in row]
                        row[2] = str(i)
                        output_file.writerow(row[2:])
                        tc, ic, rc = make_corrs(row)
                        ics.append(ic)
                        rcs.append(rc)
                        tcs.append(tc)
            corrs = {}
            corrs['T'] = filter_corrs(tcs)
            corrs['I'] = filter_corrs(ics)
            corrs['R'] = filter_corrs(rcs)

            id = 0
            for x in corrs:
                for row in corrs[x]:
                    id += 1
                    corr_file.writerow(tuple([id, ''] + [','.join(cell) for cell in row]))

