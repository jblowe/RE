#
# -*- coding: utf-8 -*-

import codecs,sys

input  = codecs.open(sys.argv[1], 'r', encoding='utf-8')
output = codecs.open(sys.argv[2], 'w', encoding='utf-8')

for line in input.readlines():
    line = line.rstrip()
    line = line.replace('#"e','ë')
    line = line.replace('#"i','ï')
    line = line.replace('##a','à')
    line = line.replace('##e','è')
    line = line.replace('##u','ù')
    line = line.replace("#'a",'á')
    line = line.replace("#'e",'é')
    line = line.replace('#\*a','*a')
    line = line.replace('#,c','ç')
    line = line.replace('#^a','â')
    line = line.replace('#^e','ê')
    line = line.replace('#^i','î')
    line = line.replace('#^o','ô')
    line = line.replace('#^u','û')

    line = line.replace('#ɾa','â')
    line = line.replace('#ɾe','ê')
    line = line.replace('#ɾi','î')
    line = line.replace('#ɾo','ô')
    line = line.replace('#ɾu','û')

    print(line, file=output)
