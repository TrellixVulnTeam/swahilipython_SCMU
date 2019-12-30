#!/usr/bin/env python3
# This script converts a C file to use the PEP 384 type definition API
# Usage: abitype.py < old_code > new_code
agiza re, sys

###### Replacement of PyTypeObject static instances ##############

# classify each token, giving it a one-letter code:
# S: static
# T: PyTypeObject
# I: ident
# W: whitespace
# =, {, }, ; : themselves
eleza classify():
    res = []
    kila t,v kwenye tokens:
        ikiwa t == 'other' na v kwenye "={};":
            res.append(v)
        lasivyo t == 'ident':
            ikiwa v == 'PyTypeObject':
                res.append('T')
            lasivyo v == 'static':
                res.append('S')
            isipokua:
                res.append('I')
        lasivyo t == 'ws':
            res.append('W')
        isipokua:
            res.append('.')
    rudisha ''.join(res)

# Obtain a list of fields of a PyTypeObject, kwenye declaration order,
# skipping ob_base
# All comments are dropped kutoka the variable (which are typically
# just the slot names, anyway), na information ni discarded whether
# the original type was static.
eleza get_fields(start, real_end):
    pos = start
    # static?
    ikiwa tokens[pos][1] == 'static':
        pos += 2
    # PyTypeObject
    pos += 2
    # name
    name = tokens[pos][1]
    pos += 1
    wakati tokens[pos][1] != '{':
        pos += 1
    pos += 1
    # PyVarObject_HEAD_INIT
    wakati tokens[pos][0] kwenye ('ws', 'comment'):
        pos += 1
    ikiwa tokens[pos][1] != 'PyVarObject_HEAD_INIT':
        ashiria Exception('%s has no PyVarObject_HEAD_INIT' % name)
    wakati tokens[pos][1] != ')':
        pos += 1
    pos += 1
    # field definitions: various tokens, comma-separated
    fields = []
    wakati Kweli:
        wakati tokens[pos][0] kwenye ('ws', 'comment'):
            pos += 1
        end = pos
        wakati tokens[end][1] haiko kwenye ',}':
            ikiwa tokens[end][1] == '(':
                nesting = 1
                wakati nesting:
                    end += 1
                    ikiwa tokens[end][1] == '(': nesting+=1
                    ikiwa tokens[end][1] == ')': nesting-=1
            end += 1
        assert end < real_end
        # join field, excluding separator na trailing ws
        end1 = end-1
        wakati tokens[end1][0] kwenye ('ws', 'comment'):
            end1 -= 1
        fields.append(''.join(t[1] kila t kwenye tokens[pos:end1+1]))
        ikiwa tokens[end][1] == '}':
            koma
        pos = end+1
    rudisha name, fields

# List of type slots kama of Python 3.2, omitting ob_base
typeslots = [
    'tp_name',
    'tp_basicsize',
    'tp_itemsize',
    'tp_dealloc',
    'tp_print',
    'tp_getattr',
    'tp_setattr',
    'tp_reserved',
    'tp_repr',
    'tp_as_number',
    'tp_as_sequence',
    'tp_as_mapping',
    'tp_hash',
    'tp_call',
    'tp_str',
    'tp_getattro',
    'tp_setattro',
    'tp_as_buffer',
    'tp_flags',
    'tp_doc',
    'tp_traverse',
    'tp_clear',
    'tp_richcompare',
    'tp_weaklistoffset',
    'tp_iter',
    'iternextfunc',
    'tp_methods',
    'tp_members',
    'tp_getset',
    'tp_base',
    'tp_dict',
    'tp_descr_get',
    'tp_descr_set',
    'tp_dictoffset',
    'tp_init',
    'tp_alloc',
    'tp_new',
    'tp_free',
    'tp_is_gc',
    'tp_bases',
    'tp_mro',
    'tp_cache',
    'tp_subclasses',
    'tp_weaklist',
    'tp_del',
    'tp_version_tag',
]

# Generate a PyType_Spec definition
eleza make_slots(name, fields):
    res = []
    res.append('static PyType_Slot %s_slots[] = {' % name)
    # defaults kila spec
    spec = { 'tp_itemsize':'0' }
    kila i, val kwenye enumerate(fields):
        ikiwa val.endswith('0'):
            endelea
        ikiwa typeslots[i] kwenye ('tp_name', 'tp_doc', 'tp_basicsize',
                         'tp_itemsize', 'tp_flags'):
            spec[typeslots[i]] = val
            endelea
        res.append('    {Py_%s, %s},' % (typeslots[i], val))
    res.append('};')
    res.append('static PyType_Spec %s_spec = {' % name)
    res.append('    %s,' % spec['tp_name'])
    res.append('    %s,' % spec['tp_basicsize'])
    res.append('    %s,' % spec['tp_itemsize'])
    res.append('    %s,' % spec['tp_flags'])
    res.append('    %s_slots,' % name)
    res.append('};\n')
    rudisha '\n'.join(res)


ikiwa __name__ == '__main__':

    ############ Simplistic C scanner ##################################
    tokenizer = re.compile(
        r"(?P<preproc>#.*\n)"
        r"|(?P<comment>/\*.*?\*/)"
        r"|(?P<ident>[a-zA-Z_][a-zA-Z0-9_]*)"
        r"|(?P<ws>[ \t\n]+)"
        r"|(?P<other>.)",
        re.MULTILINE)

    tokens = []
    source = sys.stdin.read()
    pos = 0
    wakati pos != len(source):
        m = tokenizer.match(source, pos)
        tokens.append([m.lastgroup, m.group()])
        pos += len(tokens[-1][1])
        ikiwa tokens[-1][0] == 'preproc':
            # continuation lines are considered
            # only kwenye preprocess statements
            wakati tokens[-1][1].endswith('\\\n'):
                nl = source.find('\n', pos)
                ikiwa nl == -1:
                    line = source[pos:]
                isipokua:
                    line = source[pos:nl+1]
                tokens[-1][1] += line
                pos += len(line)

    # Main loop: replace all static PyTypeObjects until
    # there are none left.
    wakati 1:
        c = classify()
        m = re.search('(SW)?TWIW?=W?{.*?};', c)
        ikiwa sio m:
            koma
        start = m.start()
        end = m.end()
        name, fields = get_fields(start, end)
        tokens[start:end] = [('',make_slots(name, fields))]

    # Output result to stdout
    kila t, v kwenye tokens:
        sys.stdout.write(v)
