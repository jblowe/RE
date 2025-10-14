import re

def compute_gloss(gloss):
    if not gloss: return ''
    original_gloss = gloss
    gloss = gloss.split(' (')[0]
    gloss = gloss.replace('*', '')
    gloss = gloss.replace('? ', '')
    gloss = re.sub(r'\(.*?\) +', '', gloss)
    gloss = re.sub(r'\(.*?\)', '', gloss)
    gloss = re.sub(r'[\(\)]', '', gloss)
    gloss = re.sub(r'\(.*?to_\)', '', gloss)
    gloss = re.sub(r'^a kind of ', '', gloss)
    gloss = re.sub(r'^a ', '', gloss)
    gloss = re.sub(r'^to ', '', gloss)
    gloss = re.sub(r'^be ', '', gloss)
    gloss = re.sub(r'^become ', '', gloss)
    gloss = re.sub(r'^go ', '', gloss)
    gloss = re.sub(r'^être ', '', gloss)
    gloss = re.sub(r' +', ' ', gloss)
    gloss = gloss.replace('_', ' ')
    gloss = gloss.strip().lower()
    if not gloss: gloss = original_gloss
    return gloss
