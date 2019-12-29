"""JSON token scanner
"""
agiza re
jaribu:
    kutoka _json agiza make_scanner kama c_make_scanner
tatizo ImportError:
    c_make_scanner = Tupu

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
        jaribu:
            nextchar = string[idx]
        tatizo IndexError:
            ashiria StopIteration(idx) kutoka Tupu

        ikiwa nextchar == '"':
            rudisha parse_string(string, idx + 1, strict)
        elikiwa nextchar == '{':
            rudisha parse_object((string, idx + 1), strict,
                _scan_once, object_hook, object_pairs_hook, memo)
        elikiwa nextchar == '[':
            rudisha parse_array((string, idx + 1), _scan_once)
        elikiwa nextchar == 'n' na string[idx:idx + 4] == 'null':
            rudisha Tupu, idx + 4
        elikiwa nextchar == 't' na string[idx:idx + 4] == 'true':
            rudisha Kweli, idx + 4
        elikiwa nextchar == 'f' na string[idx:idx + 5] == 'false':
            rudisha Uongo, idx + 5

        m = match_number(string, idx)
        ikiwa m ni sio Tupu:
            integer, frac, exp = m.groups()
            ikiwa frac ama exp:
                res = parse_float(integer + (frac ama '') + (exp ama ''))
            isipokua:
                res = parse_int(integer)
            rudisha res, m.end()
        elikiwa nextchar == 'N' na string[idx:idx + 3] == 'NaN':
            rudisha parse_constant('NaN'), idx + 3
        elikiwa nextchar == 'I' na string[idx:idx + 8] == 'Infinity':
            rudisha parse_constant('Infinity'), idx + 8
        elikiwa nextchar == '-' na string[idx:idx + 9] == '-Infinity':
            rudisha parse_constant('-Infinity'), idx + 9
        isipokua:
            ashiria StopIteration(idx)

    eleza scan_once(string, idx):
        jaribu:
            rudisha _scan_once(string, idx)
        mwishowe:
            memo.clear()

    rudisha scan_once

make_scanner = c_make_scanner ama py_make_scanner
