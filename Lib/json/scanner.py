"""JSON token scanner
"""
agiza re
try:
    kutoka _json agiza make_scanner as c_make_scanner
except ImportError:
    c_make_scanner = None

__all__ = ['make_scanner']

NUMBER_RE = re.compile(
    r'(-?(?:0|[1-9]\d*))(\.\d+)?([eE][-+]?\d+)?',
    (re.VERBOSE | re.MULTILINE | re.DOTALL))

eleza py_make_scanner(context):
    parse_object = context.parse_object
    parse_array = context.parse_array
    parse_string = context.parse_string
    match_number = NUMBER_RE.match
    strict = context.strict
    parse_float = context.parse_float
    parse_int = context.parse_int
    parse_constant = context.parse_constant
    object_hook = context.object_hook
    object_pairs_hook = context.object_pairs_hook
    memo = context.memo

    eleza _scan_once(string, idx):
        try:
            nextchar = string[idx]
        except IndexError:
            raise StopIteration(idx) kutoka None

        ikiwa nextchar == '"':
            rudisha parse_string(string, idx + 1, strict)
        elikiwa nextchar == '{':
            rudisha parse_object((string, idx + 1), strict,
                _scan_once, object_hook, object_pairs_hook, memo)
        elikiwa nextchar == '[':
            rudisha parse_array((string, idx + 1), _scan_once)
        elikiwa nextchar == 'n' and string[idx:idx + 4] == 'null':
            rudisha None, idx + 4
        elikiwa nextchar == 't' and string[idx:idx + 4] == 'true':
            rudisha True, idx + 4
        elikiwa nextchar == 'f' and string[idx:idx + 5] == 'false':
            rudisha False, idx + 5

        m = match_number(string, idx)
        ikiwa m is not None:
            integer, frac, exp = m.groups()
            ikiwa frac or exp:
                res = parse_float(integer + (frac or '') + (exp or ''))
            else:
                res = parse_int(integer)
            rudisha res, m.end()
        elikiwa nextchar == 'N' and string[idx:idx + 3] == 'NaN':
            rudisha parse_constant('NaN'), idx + 3
        elikiwa nextchar == 'I' and string[idx:idx + 8] == 'Infinity':
            rudisha parse_constant('Infinity'), idx + 8
        elikiwa nextchar == '-' and string[idx:idx + 9] == '-Infinity':
            rudisha parse_constant('-Infinity'), idx + 9
        else:
            raise StopIteration(idx)

    eleza scan_once(string, idx):
        try:
            rudisha _scan_once(string, idx)
        finally:
            memo.clear()

    rudisha scan_once

make_scanner = c_make_scanner or py_make_scanner
