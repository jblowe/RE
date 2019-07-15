#
# -*- coding: utf-8 -*-

import sys

out = sys.stdout
with open(sys.argv[1], 'r', encoding='utf-8') as input:
    with open(sys.argv[2], 'w', encoding='utf-8') as sys.stdout:

        for line in input.readlines():
            line = line.rstrip()
            if 'hw' in line:
                s = line
                s = s.replace('1', '¹')
                s = s.replace('2', '²')
                s = s.replace('3', '³')
                s = s.replace('4', '⁴')
                s = s.replace(':', 'ː')
                s = s.replace('Th', 'ʈʰ')
                s = s.replace('kh', 'kʰ')
                s = s.replace('tsh', 'tsʰ')
                s = s.replace('th', 'tʰ')
                s = s.replace('ng', 'ŋ')
                s = s.replace('oM', 'õ')
                s = s.replace('uM', 'ũ')
                s = s.replace('oM', 'õ')
                s = s.replace('iM', 'ĩ')
                s = s.replace('T', 'ʈ')
                line = s
            print(line)
