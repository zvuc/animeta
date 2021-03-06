# -*- encoding: utf-8 -*-
import re
import itertools
from django import template

register = template.Library()

def first_char(string):
    if not string:
        return '#'

    if string[:4].lower() == 'the ':
        string = string[4:]

    ch = ord(string[0])
    if ch >= 0xAC00 and ch <= 0xD7A3:
        lead = (ch - 0xAC00) // 588
        if lead in (1, 4, 8, 10, 13):
            lead -= 1
        return unichr(0xAC00 + lead * 588)
    elif re.match('^[A-Za-z]', string):
        return string[0].upper()
    else:
        return '#'

def group_records(records):
    groups = {}
    for record in records:
        key = first_char(record.title)
        if key not in groups:
            groups[key] = []
        groups[key].append(record)

    result = []
    for key in sorted(groups.keys()):
        result.append((key, groups[key]))
    return result

def make_index(records, continued='cont.'):
    return group_records(records)

    ngroups = len(set(first_char(r.work.title) for r in records))
    titleheight = 2.2
    per_column = ((len(records) + ngroups * titleheight) / 3) or 1

    records = sorted(records, key=lambda r: first_char(r.work.title))

    cols = [], [], []
    col = 0
    colheight = 0
    lastgroup = None
    for i, record in enumerate(records):
        group = first_char(record.work.title)
        if lastgroup is None or group != lastgroup:
            colheight += titleheight
            lastgroup = group
        cols[col].append(record)
        colheight += 1
        if colheight > per_column:
            lastgroup = None
            colheight = 0
            col = min(col + 1, 2)

    cols = map(group_records, cols)
    
    for n, col in enumerate(cols):
        try:
            group = cols[n + 1][0]
            if group[0] == col[len(col) - 1][0]:
                cols[n + 1][0] = (group[0] + u' (%s)' % continued, group[1])
        except:
            pass

    return cols

@register.tag
def index(parser, token):
    tag_name, records_var, as_, columns_var = token.split_contents()
    return MakeIndexNode(records_var, columns_var)

class MakeIndexNode(template.Node):
    def __init__(self, records_var, columns_var):
        self.records_var = records_var
        self.columns_var = columns_var

    def render(self, context):
        context[self.columns_var] = group_records(context[self.records_var])
        return ''
