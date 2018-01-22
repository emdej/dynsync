import re

def _ant_to_regex(pattern):
    ans_parts = []
    if not pattern.startswith('/'):
        pattern = '/**/' + pattern
    for part in pattern.split('/**'):
        ans_part = ''
        for x in part:
            if x == '*':
                ans_part += '[^/]*'
            elif x == '?':
                ans_part += '[^/]'
            else:
                ans_part += x
        ans_parts.append(ans_part)
    return '(/.*)?'.join(ans_parts).replace('//','/')

def ant_match(path, pattern):
    return re.match(_ant_to_regex(pattern), path) is not None

