#!/usr/bin/env python3
#
# Argument Clinic
# Copyright 2012-2013 by Larry Hastings.
# Licensed to the PSF under a contributor agreement.
#

agiza abc
agiza ast
agiza collections
agiza contextlib
agiza copy
agiza cpp
agiza functools
agiza hashlib
agiza inspect
agiza io
agiza itertools
agiza os
agiza pprint
agiza re
agiza shlex
agiza string
agiza sys
agiza tempfile
agiza textwrap
agiza traceback
agiza types

kutoka types agiza *
TupuType = type(Tupu)

# TODO:
#
# soon:
#
# * allow mixing any two of {positional-only, positional-or-keyword,
#   keyword-only}
#       * dict constructor uses positional-only na keyword-only
#       * max na min use positional only ukijumuisha an optional group
#         na keyword-only
#

version = '1'

TupuType = type(Tupu)

kundi Unspecified:
    eleza __repr__(self):
        rudisha '<Unspecified>'

unspecified = Unspecified()


kundi Null:
    eleza __repr__(self):
        rudisha '<Null>'

NULL = Null()


kundi Unknown:
    eleza __repr__(self):
        rudisha '<Unknown>'

unknown = Unknown()

sig_end_marker = '--'


_text_accumulator_nt = collections.namedtuple("_text_accumulator", "text append output")

eleza _text_accumulator():
    text = []
    eleza output():
        s = ''.join(text)
        text.clear()
        rudisha s
    rudisha _text_accumulator_nt(text, text.append, output)


text_accumulator_nt = collections.namedtuple("text_accumulator", "text append")

eleza text_accumulator():
    """
    Creates a simple text accumulator / joiner.

    Returns a pair of callables:
        append, output
    "append" appends a string to the accumulator.
    "output" returns the contents of the accumulator
       joined together (''.join(accumulator)) na
       empties the accumulator.
    """
    text, append, output = _text_accumulator()
    rudisha text_accumulator_nt(append, output)


eleza warn_or_fail(fail=Uongo, *args, filename=Tupu, line_number=Tupu):
    joined = " ".join([str(a) kila a kwenye args])
    add, output = text_accumulator()
    ikiwa fail:
        add("Error")
    isipokua:
        add("Warning")
    ikiwa clinic:
        ikiwa filename ni Tupu:
            filename = clinic.filename
        ikiwa getattr(clinic, 'block_parser', Tupu) na (line_number ni Tupu):
            line_number = clinic.block_parser.line_number
    ikiwa filename ni sio Tupu:
        add(' kwenye file "' + filename + '"')
    ikiwa line_number ni sio Tupu:
        add(" on line " + str(line_number))
    add(':\n')
    add(joined)
    andika(output())
    ikiwa fail:
        sys.exit(-1)


eleza warn(*args, filename=Tupu, line_number=Tupu):
    rudisha warn_or_fail(Uongo, *args, filename=filename, line_number=line_number)

eleza fail(*args, filename=Tupu, line_number=Tupu):
    rudisha warn_or_fail(Kweli, *args, filename=filename, line_number=line_number)


eleza quoted_for_c_string(s):
    kila old, new kwenye (
        ('\\', '\\\\'), # must be first!
        ('"', '\\"'),
        ("'", "\\'"),
        ):
        s = s.replace(old, new)
    rudisha s

eleza c_repr(s):
    rudisha '"' + s + '"'


is_legal_c_identifier = re.compile('^[A-Za-z_][A-Za-z0-9_]*$').match

eleza is_legal_py_identifier(s):
    rudisha all(is_legal_c_identifier(field) kila field kwenye s.split('.'))

# identifiers that are okay kwenye Python but aren't a good idea kwenye C.
# so ikiwa they're used Argument Clinic will add "_value" to the end
# of the name kwenye C.
c_keywords = set("""
asm auto koma case char const endelea default do double
else enum extern float kila goto ikiwa inline int long
register rudisha short signed sizeof static struct switch
typeeleza typeof union unsigned void volatile while
""".strip().split())

eleza ensure_legal_c_identifier(s):
    # kila now, just complain ikiwa what we're given isn't legal
    ikiwa sio is_legal_c_identifier(s):
        fail("Illegal C identifier: {}".format(s))
    # but ikiwa we picked a C keyword, pick something isipokua
    ikiwa s kwenye c_keywords:
        rudisha s + "_value"
    rudisha s

eleza rstrip_lines(s):
    text, add, output = _text_accumulator()
    kila line kwenye s.split('\n'):
        add(line.rstrip())
        add('\n')
    text.pop()
    rudisha output()

eleza format_escape(s):
    # double up curly-braces, this string will be used
    # kama part of a format_map() template later
    s = s.replace('{', '{{')
    s = s.replace('}', '}}')
    rudisha s

eleza linear_format(s, **kwargs):
    """
    Perform str.format-like substitution, tatizo:
      * The strings substituted must be on lines by
        themselves.  (This line ni the "source line".)
      * If the substitution text ni empty, the source line
        ni removed kwenye the output.
      * If the field ni sio recognized, the original line
        ni pitaed unmodified through to the output.
      * If the substitution text ni sio empty:
          * Each line of the substituted text ni indented
            by the indent of the source line.
          * A newline will be added to the end.
    """

    add, output = text_accumulator()
    kila line kwenye s.split('\n'):
        indent, curly, trailing = line.partition('{')
        ikiwa sio curly:
            add(line)
            add('\n')
            endelea

        name, curly, trailing = trailing.partition('}')
        ikiwa sio curly ama name haiko kwenye kwargs:
            add(line)
            add('\n')
            endelea

        ikiwa trailing:
            fail("Text found after {" + name + "} block marker!  It must be on a line by itself.")
        ikiwa indent.strip():
            fail("Non-whitespace characters found before {" + name + "} block marker!  It must be on a line by itself.")

        value = kwargs[name]
        ikiwa sio value:
            endelea

        value = textwrap.indent(rstrip_lines(value), indent)
        add(value)
        add('\n')

    rudisha output()[:-1]

eleza indent_all_lines(s, prefix):
    """
    Returns 's', ukijumuisha 'prefix' prepended to all lines.

    If the last line ni empty, prefix ni sio prepended
    to it.  (If s ni blank, returns s unchanged.)

    (textwrap.indent only adds to non-blank lines.)
    """
    split = s.split('\n')
    last = split.pop()
    final = []
    kila line kwenye split:
        final.append(prefix)
        final.append(line)
        final.append('\n')
    ikiwa last:
        final.append(prefix)
        final.append(last)
    rudisha ''.join(final)

eleza suffix_all_lines(s, suffix):
    """
    Returns 's', ukijumuisha 'suffix' appended to all lines.

    If the last line ni empty, suffix ni sio appended
    to it.  (If s ni blank, returns s unchanged.)
    """
    split = s.split('\n')
    last = split.pop()
    final = []
    kila line kwenye split:
        final.append(line)
        final.append(suffix)
        final.append('\n')
    ikiwa last:
        final.append(last)
        final.append(suffix)
    rudisha ''.join(final)


eleza version_splitter(s):
    """Splits a version string into a tuple of integers.

    The following ASCII characters are allowed, na employ
    the following conversions:
        a -> -3
        b -> -2
        c -> -1
    (This permits Python-style version strings such kama "1.4b3".)
    """
    version = []
    accumulator = []
    eleza flush():
        ikiwa sio accumulator:
            ashiria ValueError('Unsupported version string: ' + repr(s))
        version.append(int(''.join(accumulator)))
        accumulator.clear()

    kila c kwenye s:
        ikiwa c.isdigit():
            accumulator.append(c)
        lasivyo c == '.':
            flush()
        lasivyo c kwenye 'abc':
            flush()
            version.append('abc'.index(c) - 3)
        isipokua:
            ashiria ValueError('Illegal character ' + repr(c) + ' kwenye version string ' + repr(s))
    flush()
    rudisha tuple(version)

eleza version_comparitor(version1, version2):
    iterator = itertools.zip_longest(version_splitter(version1), version_splitter(version2), fillvalue=0)
    kila i, (a, b) kwenye enumerate(iterator):
        ikiwa a < b:
            rudisha -1
        ikiwa a > b:
            rudisha 1
    rudisha 0


kundi CRenderData:
    eleza __init__(self):

        # The C statements to declare variables.
        # Should be full lines ukijumuisha \n eol characters.
        self.declarations = []

        # The C statements required to initialize the variables before the parse call.
        # Should be full lines ukijumuisha \n eol characters.
        self.initializers = []

        # The C statements needed to dynamically modify the values
        # parsed by the parse call, before calling the impl.
        self.modifications = []

        # The entries kila the "keywords" array kila PyArg_ParseTuple.
        # Should be individual strings representing the names.
        self.keywords = []

        # The "format units" kila PyArg_ParseTuple.
        # Should be individual strings that will get
        self.format_units = []

        # The varargs arguments kila PyArg_ParseTuple.
        self.parse_arguments = []

        # The parameter declarations kila the impl function.
        self.impl_parameters = []

        # The arguments to the impl function at the time it's called.
        self.impl_arguments = []

        # For rudisha converters: the name of the variable that
        # should receive the value returned by the impl.
        self.return_value = "return_value"

        # For rudisha converters: the code to convert the rudisha
        # value kutoka the parse function.  This ni also where
        # you should check the _return_value kila errors, na
        # "goto exit" ikiwa there are any.
        self.return_conversion = []

        # The C statements required to clean up after the impl call.
        self.cleanup = []


kundi FormatCounterFormatter(string.Formatter):
    """
    This counts how many instances of each formatter
    "replacement string" appear kwenye the format string.

    e.g. after evaluating "string {a}, {b}, {c}, {a}"
         the counts dict would now look like
         {'a': 2, 'b': 1, 'c': 1}
    """
    eleza __init__(self):
        self.counts = collections.Counter()

    eleza get_value(self, key, args, kwargs):
        self.counts[key] += 1
        rudisha ''

kundi Language(metaclass=abc.ABCMeta):

    start_line = ""
    body_prefix = ""
    stop_line = ""
    checksum_line = ""

    eleza __init__(self, filename):
        pita

    @abc.abstractmethod
    eleza render(self, clinic, signatures):
        pita

    eleza parse_line(self, line):
        pita

    eleza validate(self):
        eleza assert_only_one(attr, *additional_fields):
            """
            Ensures that the string found at getattr(self, attr)
            contains exactly one formatter replacement string for
            each valid field.  The list of valid fields is
            ['dsl_name'] extended by additional_fields.

            e.g.
                self.fmt = "{dsl_name} {a} {b}"

                # this pitaes
                self.assert_only_one('fmt', 'a', 'b')

                # this fails, the format string has a {b} kwenye it
                self.assert_only_one('fmt', 'a')

                # this fails, the format string doesn't have a {c} kwenye it
                self.assert_only_one('fmt', 'a', 'b', 'c')

                # this fails, the format string has two {a}s kwenye it,
                # it must contain exactly one
                self.fmt2 = '{dsl_name} {a} {a}'
                self.assert_only_one('fmt2', 'a')

            """
            fields = ['dsl_name']
            fields.extend(additional_fields)
            line = getattr(self, attr)
            fcf = FormatCounterFormatter()
            fcf.format(line)
            eleza local_fail(should_be_there_but_isnt):
                ikiwa should_be_there_but_isnt:
                    fail("{} {} must contain {{{}}} exactly once!".format(
                        self.__class__.__name__, attr, name))
                isipokua:
                    fail("{} {} must sio contain {{{}}}!".format(
                        self.__class__.__name__, attr, name))

            kila name, count kwenye fcf.counts.items():
                ikiwa name kwenye fields:
                    ikiwa count > 1:
                        local_fail(Kweli)
                isipokua:
                    local_fail(Uongo)
            kila name kwenye fields:
                ikiwa fcf.counts.get(name) != 1:
                    local_fail(Kweli)

        assert_only_one('start_line')
        assert_only_one('stop_line')

        field = "arguments" ikiwa "{arguments}" kwenye self.checksum_line isipokua "checksum"
        assert_only_one('checksum_line', field)



kundi PythonLanguage(Language):

    language      = 'Python'
    start_line    = "#/*[{dsl_name} input]"
    body_prefix   = "#"
    stop_line     = "#[{dsl_name} start generated code]*/"
    checksum_line = "#/*[{dsl_name} end generated code: {arguments}]*/"


eleza permute_left_option_groups(l):
    """
    Given [1, 2, 3], should yield:
       ()
       (3,)
       (2, 3)
       (1, 2, 3)
    """
    tuma tuple()
    accumulator = []
    kila group kwenye reversed(l):
        accumulator = list(group) + accumulator
        tuma tuple(accumulator)


eleza permute_right_option_groups(l):
    """
    Given [1, 2, 3], should yield:
      ()
      (1,)
      (1, 2)
      (1, 2, 3)
    """
    tuma tuple()
    accumulator = []
    kila group kwenye l:
        accumulator.extend(group)
        tuma tuple(accumulator)


eleza permute_optional_groups(left, required, right):
    """
    Generator function that computes the set of acceptable
    argument lists kila the provided iterables of
    argument groups.  (Actually it generates a tuple of tuples.)

    Algorithm: prefer left options over right options.

    If required ni empty, left must also be empty.
    """
    required = tuple(required)
    result = []

    ikiwa sio required:
        assert sio left

    accumulator = []
    counts = set()
    kila r kwenye permute_right_option_groups(right):
        kila l kwenye permute_left_option_groups(left):
            t = l + required + r
            ikiwa len(t) kwenye counts:
                endelea
            counts.add(len(t))
            accumulator.append(t)

    accumulator.sort(key=len)
    rudisha tuple(accumulator)


eleza strip_leading_and_trailing_blank_lines(s):
    lines = s.rstrip().split('\n')
    wakati lines:
        line = lines[0]
        ikiwa line.strip():
            koma
        toa lines[0]
    rudisha '\n'.join(lines)

@functools.lru_cache()
eleza normalize_snippet(s, *, indent=0):
    """
    Reformats s:
        * removes leading na trailing blank lines
        * ensures that it does sio end ukijumuisha a newline
        * dedents so the first nonwhite character on any line ni at column "indent"
    """
    s = strip_leading_and_trailing_blank_lines(s)
    s = textwrap.dedent(s)
    ikiwa indent:
        s = textwrap.indent(s, ' ' * indent)
    rudisha s


eleza wrap_declarations(text, length=78):
    """
    A simple-minded text wrapper kila C function declarations.

    It views a declaration line kama looking like this:
        xxxxxxxx(xxxxxxxxx,xxxxxxxxx)
    If called ukijumuisha length=30, it would wrap that line into
        xxxxxxxx(xxxxxxxxx,
                 xxxxxxxxx)
    (If the declaration has zero ama one parameters, this
    function won't wrap it.)

    If this doesn't work properly, it's probably better to
    start kutoka scratch ukijumuisha a more sophisticated algorithm,
    rather than try na improve/debug this dumb little function.
    """
    lines = []
    kila line kwenye text.split('\n'):
        prefix, _, after_l_paren = line.partition('(')
        ikiwa sio after_l_paren:
            lines.append(line)
            endelea
        parameters, _, after_r_paren = after_l_paren.partition(')')
        ikiwa sio _:
            lines.append(line)
            endelea
        ikiwa ',' haiko kwenye parameters:
            lines.append(line)
            endelea
        parameters = [x.strip() + ", " kila x kwenye parameters.split(',')]
        prefix += "("
        ikiwa len(prefix) < length:
            spaces = " " * len(prefix)
        isipokua:
            spaces = " " * 4

        wakati parameters:
            line = prefix
            first = Kweli
            wakati parameters:
                ikiwa (sio first na
                    (len(line) + len(parameters[0]) > length)):
                    koma
                line += parameters.pop(0)
                first = Uongo
            ikiwa sio parameters:
                line = line.rstrip(", ") + ")" + after_r_paren
            lines.append(line.rstrip())
            prefix = spaces
    rudisha "\n".join(lines)


kundi CLanguage(Language):

    body_prefix   = "#"
    language      = 'C'
    start_line    = "/*[{dsl_name} input]"
    body_prefix   = ""
    stop_line     = "[{dsl_name} start generated code]*/"
    checksum_line = "/*[{dsl_name} end generated code: {arguments}]*/"

    eleza __init__(self, filename):
        super().__init__(filename)
        self.cpp = cpp.Monitor(filename)
        self.cpp.fail = fail

    eleza parse_line(self, line):
        self.cpp.writeline(line)

    eleza render(self, clinic, signatures):
        function = Tupu
        kila o kwenye signatures:
            ikiwa isinstance(o, Function):
                ikiwa function:
                    fail("You may specify at most one function per block.\nFound a block containing at least two:\n\t" + repr(function) + " na " + repr(o))
                function = o
        rudisha self.render_function(clinic, function)

    eleza docstring_for_c_string(self, f):
        ikiwa re.search(r'[^\x00-\x7F]', f.docstring):
            warn("Non-ascii character appear kwenye docstring.")

        text, add, output = _text_accumulator()
        # turn docstring into a properly quoted C string
        kila line kwenye f.docstring.split('\n'):
            add('"')
            add(quoted_for_c_string(line))
            add('\\n"\n')

        ikiwa text[-2] == sig_end_marker:
            # If we only have a signature, add the blank line that the
            # __text_signature__ getter expects to be there.
            add('"\\n"')
        isipokua:
            text.pop()
            add('"')
        rudisha ''.join(text)

    eleza output_templates(self, f):
        parameters = list(f.parameters.values())
        assert parameters
        assert isinstance(parameters[0].converter, self_converter)
        toa parameters[0]
        converters = [p.converter kila p kwenye parameters]

        has_option_groups = parameters na (parameters[0].group ama parameters[-1].group)
        default_return_converter = (sio f.return_converter ama
            f.return_converter.type == 'PyObject *')

        new_or_init = f.kind kwenye (METHOD_NEW, METHOD_INIT)

        pos_only = min_pos = max_pos = min_kw_only = 0
        kila i, p kwenye enumerate(parameters, 1):
            ikiwa p.is_keyword_only():
                assert sio p.is_positional_only()
                ikiwa sio p.is_optional():
                    min_kw_only = i - max_pos
            isipokua:
                max_pos = i
                ikiwa p.is_positional_only():
                    pos_only = i
                ikiwa sio p.is_optional():
                    min_pos = i

        meth_o = (len(parameters) == 1 na
              parameters[0].is_positional_only() na
              sio converters[0].is_optional() na
              sio new_or_init)

        # we have to set these things before we're done:
        #
        # docstring_prototype
        # docstring_definition
        # impl_prototype
        # methoddef_define
        # parser_prototype
        # parser_definition
        # impl_definition
        # cpp_if
        # cpp_endif
        # methoddef_ifndef

        return_value_declaration = "PyObject *return_value = NULL;"

        methoddef_define = normalize_snippet("""
            #define {methoddef_name}    \\
                {{"{name}", {methoddef_cast}{c_basename}, {methoddef_flags}, {c_basename}__doc__}},
            """)
        ikiwa new_or_init na sio f.docstring:
            docstring_prototype = docstring_definition = ''
        isipokua:
            docstring_prototype = normalize_snippet("""
                PyDoc_VAR({c_basename}__doc__);
                """)
            docstring_definition = normalize_snippet("""
                PyDoc_STRVAR({c_basename}__doc__,
                {docstring});
                """)
        impl_definition = normalize_snippet("""
            static {impl_return_type}
            {c_basename}_impl({impl_parameters})
            """)
        impl_prototype = parser_prototype = parser_definition = Tupu

        parser_prototype_keyword = normalize_snippet("""
            static PyObject *
            {c_basename}({self_type}{self_name}, PyObject *args, PyObject *kwargs)
            """)

        parser_prototype_varargs = normalize_snippet("""
            static PyObject *
            {c_basename}({self_type}{self_name}, PyObject *args)
            """)

        parser_prototype_fastcall = normalize_snippet("""
            static PyObject *
            {c_basename}({self_type}{self_name}, PyObject *const *args, Py_ssize_t nargs)
            """)

        parser_prototype_fastcall_keywords = normalize_snippet("""
            static PyObject *
            {c_basename}({self_type}{self_name}, PyObject *const *args, Py_ssize_t nargs, PyObject *kwnames)
            """)

        # parser_body_fields remembers the fields pitaed kwenye to the
        # previous call to parser_body. this ni used kila an awful hack.
        parser_body_fields = ()
        parser_body_declarations = ''
        eleza parser_body(prototype, *fields, declarations=''):
            nonlocal parser_body_fields, parser_body_declarations
            add, output = text_accumulator()
            add(prototype)
            parser_body_fields = fields
            parser_body_declarations = declarations

            fields = list(fields)
            fields.insert(0, normalize_snippet("""
                {{
                    {return_value_declaration}
                    {parser_declarations}
                    {declarations}
                    {initializers}
                """) + "\n")
            # just imagine--your code ni here kwenye the middle
            fields.append(normalize_snippet("""
                    {modifications}
                    {return_value} = {c_basename}_impl({impl_arguments});
                    {return_conversion}

                {exit_label}
                    {cleanup}
                    rudisha return_value;
                }}
                """))
            kila field kwenye fields:
                add('\n')
                add(field)
            rudisha linear_format(output(), parser_declarations=declarations)

        ikiwa sio parameters:
            # no parameters, METH_NOARGS

            flags = "METH_NOARGS"

            parser_prototype = normalize_snippet("""
                static PyObject *
                {c_basename}({self_type}{self_name}, PyObject *Py_UNUSED(ignored))
                """)
            parser_definition = parser_prototype

            ikiwa default_return_converter:
                parser_definition = parser_prototype + '\n' + normalize_snippet("""
                    {{
                        rudisha {c_basename}_impl({impl_arguments});
                    }}
                    """)
            isipokua:
                parser_definition = parser_body(parser_prototype)

        lasivyo meth_o:
            flags = "METH_O"

            ikiwa (isinstance(converters[0], object_converter) na
                converters[0].format_unit == 'O'):
                meth_o_prototype = normalize_snippet("""
                    static PyObject *
                    {c_basename}({impl_parameters})
                    """)

                ikiwa default_return_converter:
                    # maps perfectly to METH_O, doesn't need a rudisha converter.
                    # so we skip making a parse function
                    # na call directly into the impl function.
                    impl_prototype = parser_prototype = parser_definition = ''
                    impl_definition = meth_o_prototype
                isipokua:
                    # SLIGHT HACK
                    # use impl_parameters kila the parser here!
                    parser_prototype = meth_o_prototype
                    parser_definition = parser_body(parser_prototype)

            isipokua:
                argname = 'arg'
                ikiwa parameters[0].name == argname:
                    argname += '_'
                parser_prototype = normalize_snippet("""
                    static PyObject *
                    {c_basename}({self_type}{self_name}, PyObject *%s)
                    """ % argname)

                displayname = parameters[0].get_displayname(0)
                parsearg = converters[0].parse_arg(argname, displayname)
                ikiwa parsearg ni Tupu:
                    parsearg = """
                        ikiwa (!PyArg_Parse(%s, "{format_units}:{name}", {parse_arguments})) {{
                            goto exit;
                        }}
                        """ % argname
                parser_definition = parser_body(parser_prototype,
                                                normalize_snippet(parsearg, indent=4))

        lasivyo has_option_groups:
            # positional parameters ukijumuisha option groups
            # (we have to generate lots of PyArg_ParseTuple calls
            #  kwenye a big switch statement)

            flags = "METH_VARARGS"
            parser_prototype = parser_prototype_varargs

            parser_definition = parser_body(parser_prototype, '    {option_group_parsing}')

        lasivyo pos_only == len(parameters):
            ikiwa sio new_or_init:
                # positional-only, but no option groups
                # we only need one call to _PyArg_ParseStack

                flags = "METH_FASTCALL"
                parser_prototype = parser_prototype_fastcall
                nargs = 'nargs'
                argname_fmt = 'args[%d]'
            isipokua:
                # positional-only, but no option groups
                # we only need one call to PyArg_ParseTuple

                flags = "METH_VARARGS"
                parser_prototype = parser_prototype_varargs
                nargs = 'PyTuple_GET_SIZE(args)'
                argname_fmt = 'PyTuple_GET_ITEM(args, %d)'

            parser_code = [normalize_snippet("""
                ikiwa (!_PyArg_CheckPositional("{name}", %s, %d, %d)) {{
                    goto exit;
                }}
                """ % (nargs, min_pos, max_pos), indent=4)]
            has_optional = Uongo
            kila i, p kwenye enumerate(parameters):
                displayname = p.get_displayname(i+1)
                parsearg = p.converter.parse_arg(argname_fmt % i, displayname)
                ikiwa parsearg ni Tupu:
                    #andika('Cannot convert %s %r kila %s' % (p.converter.__class__.__name__, p.converter.format_unit, p.converter.name), file=sys.stderr)
                    parser_code = Tupu
                    koma
                ikiwa has_optional ama p.is_optional():
                    has_optional = Kweli
                    parser_code.append(normalize_snippet("""
                        ikiwa (%s < %d) {{
                            goto skip_optional;
                        }}
                        """, indent=4) % (nargs, i + 1))
                parser_code.append(normalize_snippet(parsearg, indent=4))

            ikiwa parser_code ni sio Tupu:
                ikiwa has_optional:
                    parser_code.append("skip_optional:")
            isipokua:
                ikiwa sio new_or_init:
                    parser_code = [normalize_snippet("""
                        ikiwa (!_PyArg_ParseStack(args, nargs, "{format_units}:{name}",
                            {parse_arguments})) {{
                            goto exit;
                        }}
                        """, indent=4)]
                isipokua:
                    parser_code = [normalize_snippet("""
                        ikiwa (!PyArg_ParseTuple(args, "{format_units}:{name}",
                            {parse_arguments})) {{
                            goto exit;
                        }}
                        """, indent=4)]
            parser_definition = parser_body(parser_prototype, *parser_code)

        isipokua:
            has_optional_kw = (max(pos_only, min_pos) + min_kw_only < len(converters))
            ikiwa sio new_or_init:
                flags = "METH_FASTCALL|METH_KEYWORDS"
                parser_prototype = parser_prototype_fastcall_keywords
                argname_fmt = 'args[%d]'
                declarations = normalize_snippet("""
                    static const char * const _keywords[] = {{{keywords}, NULL}};
                    static _PyArg_Parser _parser = {{NULL, _keywords, "{name}", 0}};
                    PyObject *argsbuf[%s];
                    """ % len(converters))
                ikiwa has_optional_kw:
                    declarations += "\nPy_ssize_t noptargs = nargs + (kwnames ? PyTuple_GET_SIZE(kwnames) : 0) - %d;" % (min_pos + min_kw_only)
                parser_code = [normalize_snippet("""
                    args = _PyArg_UnpackKeywords(args, nargs, NULL, kwnames, &_parser, %d, %d, %d, argsbuf);
                    ikiwa (!args) {{
                        goto exit;
                    }}
                    """ % (min_pos, max_pos, min_kw_only), indent=4)]
            isipokua:
                # positional-or-keyword arguments
                flags = "METH_VARARGS|METH_KEYWORDS"
                parser_prototype = parser_prototype_keyword
                argname_fmt = 'fastargs[%d]'
                declarations = normalize_snippet("""
                    static const char * const _keywords[] = {{{keywords}, NULL}};
                    static _PyArg_Parser _parser = {{NULL, _keywords, "{name}", 0}};
                    PyObject *argsbuf[%s];
                    PyObject * const *fastargs;
                    Py_ssize_t nargs = PyTuple_GET_SIZE(args);
                    """ % len(converters))
                ikiwa has_optional_kw:
                    declarations += "\nPy_ssize_t noptargs = nargs + (kwargs ? PyDict_GET_SIZE(kwargs) : 0) - %d;" % (min_pos + min_kw_only)
                parser_code = [normalize_snippet("""
                    fastargs = _PyArg_UnpackKeywords(_PyTuple_CAST(args)->ob_item, nargs, kwargs, NULL, &_parser, %d, %d, %d, argsbuf);
                    ikiwa (!fastargs) {{
                        goto exit;
                    }}
                    """ % (min_pos, max_pos, min_kw_only), indent=4)]

            add_label = Tupu
            kila i, p kwenye enumerate(parameters):
                displayname = p.get_displayname(i+1)
                parsearg = p.converter.parse_arg(argname_fmt % i, displayname)
                ikiwa parsearg ni Tupu:
                    #andika('Cannot convert %s %r kila %s' % (p.converter.__class__.__name__, p.converter.format_unit, p.converter.name), file=sys.stderr)
                    parser_code = Tupu
                    koma
                ikiwa add_label na (i == pos_only ama i == max_pos):
                    parser_code.append("%s:" % add_label)
                    add_label = Tupu
                ikiwa sio p.is_optional():
                    parser_code.append(normalize_snippet(parsearg, indent=4))
                lasivyo i < pos_only:
                    add_label = 'skip_optional_posonly'
                    parser_code.append(normalize_snippet("""
                        ikiwa (nargs < %d) {{
                            goto %s;
                        }}
                        """ % (i + 1, add_label), indent=4))
                    ikiwa has_optional_kw:
                        parser_code.append(normalize_snippet("""
                            noptargs--;
                            """, indent=4))
                    parser_code.append(normalize_snippet(parsearg, indent=4))
                isipokua:
                    ikiwa i < max_pos:
                        label = 'skip_optional_pos'
                        first_opt = max(min_pos, pos_only)
                    isipokua:
                        label = 'skip_optional_kwonly'
                        first_opt = max_pos + min_kw_only
                    ikiwa i == first_opt:
                        add_label = label
                        parser_code.append(normalize_snippet("""
                            ikiwa (!noptargs) {{
                                goto %s;
                            }}
                            """ % add_label, indent=4))
                    ikiwa i + 1 == len(parameters):
                        parser_code.append(normalize_snippet(parsearg, indent=4))
                    isipokua:
                        add_label = label
                        parser_code.append(normalize_snippet("""
                            ikiwa (%s) {{
                            """ % (argname_fmt % i), indent=4))
                        parser_code.append(normalize_snippet(parsearg, indent=8))
                        parser_code.append(normalize_snippet("""
                                ikiwa (!--noptargs) {{
                                    goto %s;
                                }}
                            }}
                            """ % add_label, indent=4))

            ikiwa parser_code ni sio Tupu:
                ikiwa add_label:
                    parser_code.append("%s:" % add_label)
            isipokua:
                declarations = (
                    'static const char * const _keywords[] = {{{keywords}, NULL}};\n'
                    'static _PyArg_Parser _parser = {{"{format_units}:{name}", _keywords, 0}};')
                ikiwa sio new_or_init:
                    parser_code = [normalize_snippet("""
                        ikiwa (!_PyArg_ParseStackAndKeywords(args, nargs, kwnames, &_parser,
                            {parse_arguments})) {{
                            goto exit;
                        }}
                        """, indent=4)]
                isipokua:
                    parser_code = [normalize_snippet("""
                        ikiwa (!_PyArg_ParseTupleAndKeywordsFast(args, kwargs, &_parser,
                            {parse_arguments})) {{
                            goto exit;
                        }}
                        """, indent=4)]
            parser_definition = parser_body(parser_prototype, *parser_code,
                                            declarations=declarations)


        ikiwa new_or_init:
            methoddef_define = ''

            ikiwa f.kind == METHOD_NEW:
                parser_prototype = parser_prototype_keyword
            isipokua:
                return_value_declaration = "int return_value = -1;"
                parser_prototype = normalize_snippet("""
                    static int
                    {c_basename}({self_type}{self_name}, PyObject *args, PyObject *kwargs)
                    """)

            fields = list(parser_body_fields)
            parses_positional = 'METH_NOARGS' haiko kwenye flags
            parses_keywords = 'METH_KEYWORDS' kwenye flags
            ikiwa parses_keywords:
                assert parses_positional

            ikiwa sio parses_keywords:
                fields.insert(0, normalize_snippet("""
                    ikiwa ({self_type_check}!_PyArg_NoKeywords("{name}", kwargs)) {{
                        goto exit;
                    }}
                    """, indent=4))
                ikiwa sio parses_positional:
                    fields.insert(0, normalize_snippet("""
                        ikiwa ({self_type_check}!_PyArg_NoPositional("{name}", args)) {{
                            goto exit;
                        }}
                        """, indent=4))

            parser_definition = parser_body(parser_prototype, *fields,
                                            declarations=parser_body_declarations)


        ikiwa flags kwenye ('METH_NOARGS', 'METH_O', 'METH_VARARGS'):
            methoddef_cast = "(PyCFunction)"
        isipokua:
            methoddef_cast = "(PyCFunction)(void(*)(void))"

        ikiwa f.methoddef_flags:
            flags += '|' + f.methoddef_flags

        methoddef_define = methoddef_define.replace('{methoddef_flags}', flags)
        methoddef_define = methoddef_define.replace('{methoddef_cast}', methoddef_cast)

        methoddef_ifneleza = ''
        conditional = self.cpp.condition()
        ikiwa sio conditional:
            cpp_ikiwa = cpp_endikiwa = ''
        isipokua:
            cpp_ikiwa = "#ikiwa " + conditional
            cpp_endikiwa = "#endikiwa /* " + conditional + " */"

            ikiwa methoddef_define na f.full_name haiko kwenye clinic.ifndef_symbols:
                clinic.ifndef_symbols.add(f.full_name)
                methoddef_ifneleza = normalize_snippet("""
                    #ifneleza {methoddef_name}
                        #define {methoddef_name}
                    #endikiwa /* !defined({methoddef_name}) */
                    """)


        # add ';' to the end of parser_prototype na impl_prototype
        # (they mustn't be Tupu, but they could be an empty string.)
        assert parser_prototype ni sio Tupu
        ikiwa parser_prototype:
            assert sio parser_prototype.endswith(';')
            parser_prototype += ';'

        ikiwa impl_prototype ni Tupu:
            impl_prototype = impl_definition
        ikiwa impl_prototype:
            impl_prototype += ";"

        parser_definition = parser_definition.replace("{return_value_declaration}", return_value_declaration)

        d = {
            "docstring_prototype" : docstring_prototype,
            "docstring_definition" : docstring_definition,
            "impl_prototype" : impl_prototype,
            "methoddef_define" : methoddef_define,
            "parser_prototype" : parser_prototype,
            "parser_definition" : parser_definition,
            "impl_definition" : impl_definition,
            "cpp_if" : cpp_if,
            "cpp_endif" : cpp_endif,
            "methoddef_ifndef" : methoddef_ifndef,
        }

        # make sure we didn't forget to assign something,
        # na wrap each non-empty value kwenye \n's
        d2 = {}
        kila name, value kwenye d.items():
            assert value ni sio Tupu, "got a Tupu value kila template " + repr(name)
            ikiwa value:
                value = '\n' + value + '\n'
            d2[name] = value
        rudisha d2

    @staticmethod
    eleza group_to_variable_name(group):
        adjective = "left_" ikiwa group < 0 isipokua "right_"
        rudisha "group_" + adjective + str(abs(group))

    eleza render_option_group_parsing(self, f, template_dict):
        # positional only, grouped, optional arguments!
        # can be optional on the left ama right.
        # here's an example:
        #
        # [ [ [ A1 A2 ] B1 B2 B3 ] C1 C2 ] D1 D2 D3 [ E1 E2 E3 [ F1 F2 F3 ] ]
        #
        # Here group D are required, na all other groups are optional.
        # (Group D's "group" ni actually Tupu.)
        # We can figure out which sets of arguments we have based on
        # how many arguments are kwenye the tuple.
        #
        # Note that you need to count up on both sides.  For example,
        # you could have groups C+D, ama C+D+E, ama C+D+E+F.
        #
        # What ikiwa the number of arguments leads us to an ambiguous result?
        # Clinic prefers groups on the left.  So kwenye the above example,
        # five arguments would map to B+C, sio C+D.

        add, output = text_accumulator()
        parameters = list(f.parameters.values())
        ikiwa isinstance(parameters[0].converter, self_converter):
            toa parameters[0]

        groups = []
        group = Tupu
        left = []
        right = []
        required = []
        last = unspecified

        kila p kwenye parameters:
            group_id = p.group
            ikiwa group_id != last:
                last = group_id
                group = []
                ikiwa group_id < 0:
                    left.append(group)
                lasivyo group_id == 0:
                    group = required
                isipokua:
                    right.append(group)
            group.append(p)

        count_min = sys.maxsize
        count_max = -1

        add("switch (PyTuple_GET_SIZE(args)) {\n")
        kila subset kwenye permute_optional_groups(left, required, right):
            count = len(subset)
            count_min = min(count_min, count)
            count_max = max(count_max, count)

            ikiwa count == 0:
                add("""    case 0:
        koma;
""")
                endelea

            group_ids = {p.group kila p kwenye subset}  # eliminate duplicates
            d = {}
            d['count'] = count
            d['name'] = f.name
            d['format_units'] = "".join(p.converter.format_unit kila p kwenye subset)

            parse_arguments = []
            kila p kwenye subset:
                p.converter.parse_argument(parse_arguments)
            d['parse_arguments'] = ", ".join(parse_arguments)

            group_ids.discard(0)
            lines = [self.group_to_variable_name(g) + " = 1;" kila g kwenye group_ids]
            lines = "\n".join(lines)

            s = """
    case {count}:
        ikiwa (!PyArg_ParseTuple(args, "{format_units}:{name}", {parse_arguments})) {{
            goto exit;
        }}
        {group_booleans}
        koma;
"""[1:]
            s = linear_format(s, group_booleans=lines)
            s = s.format_map(d)
            add(s)

        add("    default:\n")
        s = '        PyErr_SetString(PyExc_TypeError, "{} requires {} to {} arguments");\n'
        add(s.format(f.full_name, count_min, count_max))
        add('        goto exit;\n')
        add("}")
        template_dict['option_group_parsing'] = format_escape(output())

    eleza render_function(self, clinic, f):
        ikiwa sio f:
            rudisha ""

        add, output = text_accumulator()
        data = CRenderData()

        assert f.parameters, "We should always have a 'self' at this point!"
        parameters = f.render_parameters
        converters = [p.converter kila p kwenye parameters]

        templates = self.output_templates(f)

        f_self = parameters[0]
        selfless = parameters[1:]
        assert isinstance(f_self.converter, self_converter), "No self parameter kwenye " + repr(f.full_name) + "!"

        last_group = 0
        first_optional = len(selfless)
        positional = selfless na selfless[-1].is_positional_only()
        new_or_init = f.kind kwenye (METHOD_NEW, METHOD_INIT)
        default_return_converter = (sio f.return_converter ama
            f.return_converter.type == 'PyObject *')
        has_option_groups = Uongo

        # offset i by -1 because first_optional needs to ignore self
        kila i, p kwenye enumerate(parameters, -1):
            c = p.converter

            ikiwa (i != -1) na (p.default ni sio unspecified):
                first_optional = min(first_optional, i)

            # insert group variable
            group = p.group
            ikiwa last_group != group:
                last_group = group
                ikiwa group:
                    group_name = self.group_to_variable_name(group)
                    data.impl_arguments.append(group_name)
                    data.declarations.append("int " + group_name + " = 0;")
                    data.impl_parameters.append("int " + group_name)
                    has_option_groups = Kweli

            c.render(p, data)

        ikiwa has_option_groups na (sio positional):
            fail("You cannot use optional groups ('[' na ']')\nunless all parameters are positional-only ('/').")

        # HACK
        # when we're METH_O, but have a custom rudisha converter,
        # we use "impl_parameters" kila the parsing function
        # because that works better.  but that means we must
        # suppress actually declaring the impl's parameters
        # kama variables kwenye the parsing function.  but since it's
        # METH_O, we have exactly one anyway, so we know exactly
        # where it is.
        ikiwa ("METH_O" kwenye templates['methoddef_define'] na
            '{impl_parameters}' kwenye templates['parser_prototype']):
            data.declarations.pop(0)

        template_dict = {}

        full_name = f.full_name
        template_dict['full_name'] = full_name

        ikiwa new_or_init:
            name = f.cls.name
        isipokua:
            name = f.name

        template_dict['name'] = name

        ikiwa f.c_basename:
            c_basename = f.c_basename
        isipokua:
            fields = full_name.split(".")
            ikiwa fields[-1] == '__new__':
                fields.pop()
            c_basename = "_".join(fields)

        template_dict['c_basename'] = c_basename

        methoddef_name = "{}_METHODDEF".format(c_basename.upper())
        template_dict['methoddef_name'] = methoddef_name

        template_dict['docstring'] = self.docstring_for_c_string(f)

        template_dict['self_name'] = template_dict['self_type'] = template_dict['self_type_check'] = ''
        f_self.converter.set_template_dict(template_dict)

        f.return_converter.render(f, data)
        template_dict['impl_return_type'] = f.return_converter.type

        template_dict['declarations'] = format_escape("\n".join(data.declarations))
        template_dict['initializers'] = "\n\n".join(data.initializers)
        template_dict['modifications'] = '\n\n'.join(data.modifications)
        template_dict['keywords'] = '"' + '", "'.join(data.keywords) + '"'
        template_dict['format_units'] = ''.join(data.format_units)
        template_dict['parse_arguments'] = ', '.join(data.parse_arguments)
        template_dict['impl_parameters'] = ", ".join(data.impl_parameters)
        template_dict['impl_arguments'] = ", ".join(data.impl_arguments)
        template_dict['return_conversion'] = format_escape("".join(data.return_conversion).rstrip())
        template_dict['cleanup'] = format_escape("".join(data.cleanup))
        template_dict['return_value'] = data.return_value

        # used by unpack tuple code generator
        ignore_self = -1 ikiwa isinstance(converters[0], self_converter) isipokua 0
        unpack_min = first_optional
        unpack_max = len(selfless)
        template_dict['unpack_min'] = str(unpack_min)
        template_dict['unpack_max'] = str(unpack_max)

        ikiwa has_option_groups:
            self.render_option_group_parsing(f, template_dict)

        # buffers, sio destination
        kila name, destination kwenye clinic.destination_buffers.items():
            template = templates[name]
            ikiwa has_option_groups:
                template = linear_format(template,
                        option_group_parsing=template_dict['option_group_parsing'])
            template = linear_format(template,
                declarations=template_dict['declarations'],
                return_conversion=template_dict['return_conversion'],
                initializers=template_dict['initializers'],
                modifications=template_dict['modifications'],
                cleanup=template_dict['cleanup'],
                )

            # Only generate the "exit:" label
            # ikiwa we have any gotos
            need_exit_label = "goto exit;" kwenye template
            template = linear_format(template,
                exit_label="exit:" ikiwa need_exit_label isipokua ''
                )

            s = template.format_map(template_dict)

            # mild hack:
            # reflow long impl declarations
            ikiwa name kwenye {"impl_prototype", "impl_definition"}:
                s = wrap_declarations(s)

            ikiwa clinic.line_prefix:
                s = indent_all_lines(s, clinic.line_prefix)
            ikiwa clinic.line_suffix:
                s = suffix_all_lines(s, clinic.line_suffix)

            destination.append(s)

        rudisha clinic.get_destination('block').dump()




@contextlib.contextmanager
eleza OverrideStdioWith(stdout):
    saved_stdout = sys.stdout
    sys.stdout = stdout
    jaribu:
        yield
    mwishowe:
        assert sys.stdout ni stdout
        sys.stdout = saved_stdout


eleza create_regex(before, after, word=Kweli, whole_line=Kweli):
    """Create an re object kila matching marker lines."""
    group_re = r"\w+" ikiwa word isipokua ".+"
    pattern = r'{}({}){}'
    ikiwa whole_line:
        pattern = '^' + pattern + '$'
    pattern = pattern.format(re.escape(before), group_re, re.escape(after))
    rudisha re.compile(pattern)


kundi Block:
    r"""
    Represents a single block of text embedded in
    another file.  If dsl_name ni Tupu, the block represents
    verbatim text, raw original text kutoka the file, in
    which case "input" will be the only non-false member.
    If dsl_name ni sio Tupu, the block represents a Clinic
    block.

    input ni always str, ukijumuisha embedded \n characters.
    input represents the original text kutoka the file;
    ikiwa it's a Clinic block, it ni the original text with
    the body_prefix na redundant leading whitespace removed.

    dsl_name ni either str ama Tupu.  If str, it's the text
    found on the start line of the block between the square
    brackets.

    signatures ni either list ama Tupu.  If it's a list,
    it may only contain clinic.Module, clinic.Class, na
    clinic.Function objects.  At the moment it should
    contain at most one of each.

    output ni either str ama Tupu.  If str, it's the output
    kutoka this block, ukijumuisha embedded '\n' characters.

    indent ni either str ama Tupu.  It's the leading whitespace
    that was found on every line of input.  (If body_prefix is
    sio empty, this ni the indent *after* removing the
    body_prefix.)

    preindent ni either str ama Tupu.  It's the whitespace that
    was found kwenye front of every line of input *before* the
    "body_prefix" (see the Language object).  If body_prefix
    ni empty, preindent must always be empty too.

    To illustrate indent na preindent: Assume that '_'
    represents whitespace.  If the block processed was kwenye a
    Python file, na looked like this:
      ____#/*[python]
      ____#__kila a kwenye range(20):
      ____#____andika(a)
      ____#[python]*/
    "preindent" would be "____" na "indent" would be "__".

    """
    eleza __init__(self, input, dsl_name=Tupu, signatures=Tupu, output=Tupu, indent='', preindent=''):
        assert isinstance(input, str)
        self.input = input
        self.dsl_name = dsl_name
        self.signatures = signatures ama []
        self.output = output
        self.indent = indent
        self.preindent = preindent

    eleza __repr__(self):
        dsl_name = self.dsl_name ama "text"
        eleza summarize(s):
            s = repr(s)
            ikiwa len(s) > 30:
                rudisha s[:26] + "..." + s[0]
            rudisha s
        rudisha "".join((
            "<Block ", dsl_name, " input=", summarize(self.input), " output=", summarize(self.output), ">"))


kundi BlockParser:
    """
    Block-oriented parser kila Argument Clinic.
    Iterator, yields Block objects.
    """

    eleza __init__(self, input, language, *, verify=Kweli):
        """
        "input" should be a str object
        ukijumuisha embedded \n characters.

        "language" should be a Language object.
        """
        language.validate()

        self.input = collections.deque(reversed(input.splitlines(keepends=Kweli)))
        self.block_start_line_number = self.line_number = 0

        self.language = language
        before, _, after = language.start_line.partition('{dsl_name}')
        assert _ == '{dsl_name}'
        self.find_start_re = create_regex(before, after, whole_line=Uongo)
        self.start_re = create_regex(before, after)
        self.verify = verify
        self.last_checksum_re = Tupu
        self.last_dsl_name = Tupu
        self.dsl_name = Tupu
        self.first_block = Kweli

    eleza __iter__(self):
        rudisha self

    eleza __next__(self):
        wakati Kweli:
            ikiwa sio self.input:
                ashiria StopIteration

            ikiwa self.dsl_name:
                return_value = self.parse_clinic_block(self.dsl_name)
                self.dsl_name = Tupu
                self.first_block = Uongo
                rudisha return_value
            block = self.parse_verbatim_block()
            ikiwa self.first_block na sio block.input:
                endelea
            self.first_block = Uongo
            rudisha block


    eleza is_start_line(self, line):
        match = self.start_re.match(line.lstrip())
        rudisha match.group(1) ikiwa match isipokua Tupu

    eleza _line(self, lookahead=Uongo):
        self.line_number += 1
        line = self.input.pop()
        ikiwa sio lookahead:
            self.language.parse_line(line)
        rudisha line

    eleza parse_verbatim_block(self):
        add, output = text_accumulator()
        self.block_start_line_number = self.line_number

        wakati self.input:
            line = self._line()
            dsl_name = self.is_start_line(line)
            ikiwa dsl_name:
                self.dsl_name = dsl_name
                koma
            add(line)

        rudisha Block(output())

    eleza parse_clinic_block(self, dsl_name):
        input_add, input_output = text_accumulator()
        self.block_start_line_number = self.line_number + 1
        stop_line = self.language.stop_line.format(dsl_name=dsl_name)
        body_prefix = self.language.body_prefix.format(dsl_name=dsl_name)

        eleza is_stop_line(line):
            # make sure to recognize stop line even ikiwa it
            # doesn't end ukijumuisha EOL (it could be the very end of the file)
            ikiwa sio line.startswith(stop_line):
                rudisha Uongo
            remainder = line[len(stop_line):]
            rudisha (sio remainder) ama remainder.isspace()

        # consume body of program
        wakati self.input:
            line = self._line()
            ikiwa is_stop_line(line) ama self.is_start_line(line):
                koma
            ikiwa body_prefix:
                line = line.lstrip()
                assert line.startswith(body_prefix)
                line = line[len(body_prefix):]
            input_add(line)

        # consume output na checksum line, ikiwa present.
        ikiwa self.last_dsl_name == dsl_name:
            checksum_re = self.last_checksum_re
        isipokua:
            before, _, after = self.language.checksum_line.format(dsl_name=dsl_name, arguments='{arguments}').partition('{arguments}')
            assert _ == '{arguments}'
            checksum_re = create_regex(before, after, word=Uongo)
            self.last_dsl_name = dsl_name
            self.last_checksum_re = checksum_re

        # scan forward kila checksum line
        output_add, output_output = text_accumulator()
        arguments = Tupu
        wakati self.input:
            line = self._line(lookahead=Kweli)
            match = checksum_re.match(line.lstrip())
            arguments = match.group(1) ikiwa match isipokua Tupu
            ikiwa arguments:
                koma
            output_add(line)
            ikiwa self.is_start_line(line):
                koma

        output = output_output()
        ikiwa arguments:
            d = {}
            kila field kwenye shlex.split(arguments):
                name, equals, value = field.partition('=')
                ikiwa sio equals:
                    fail("Mangled Argument Clinic marker line: {!r}".format(line))
                d[name.strip()] = value.strip()

            ikiwa self.verify:
                ikiwa 'input' kwenye d:
                    checksum = d['output']
                    input_checksum = d['input']
                isipokua:
                    checksum = d['checksum']
                    input_checksum = Tupu

                computed = compute_checksum(output, len(checksum))
                ikiwa checksum != computed:
                    fail("Checksum mismatch!\nExpected: {}\nComputed: {}\n"
                         "Suggested fix: remove all generated code including "
                         "the end marker,\n"
                         "or use the '-f' option."
                        .format(checksum, computed))
        isipokua:
            # put back output
            output_lines = output.splitlines(keepends=Kweli)
            self.line_number -= len(output_lines)
            self.input.extend(reversed(output_lines))
            output = Tupu

        rudisha Block(input_output(), dsl_name, output=output)


kundi BlockPrinter:

    eleza __init__(self, language, f=Tupu):
        self.language = language
        self.f = f ama io.StringIO()

    eleza print_block(self, block):
        input = block.input
        output = block.output
        dsl_name = block.dsl_name
        write = self.f.write

        assert sio ((dsl_name == Tupu) ^ (output == Tupu)), "you must specify dsl_name na output together, dsl_name " + repr(dsl_name)

        ikiwa sio dsl_name:
            write(input)
            rudisha

        write(self.language.start_line.format(dsl_name=dsl_name))
        write("\n")

        body_prefix = self.language.body_prefix.format(dsl_name=dsl_name)
        ikiwa sio body_prefix:
            write(input)
        isipokua:
            kila line kwenye input.split('\n'):
                write(body_prefix)
                write(line)
                write("\n")

        write(self.language.stop_line.format(dsl_name=dsl_name))
        write("\n")

        input = ''.join(block.input)
        output = ''.join(block.output)
        ikiwa output:
            ikiwa sio output.endswith('\n'):
                output += '\n'
            write(output)

        arguments="output={} input={}".format(compute_checksum(output, 16), compute_checksum(input, 16))
        write(self.language.checksum_line.format(dsl_name=dsl_name, arguments=arguments))
        write("\n")

    eleza write(self, text):
        self.f.write(text)


kundi BufferSeries:
    """
    Behaves like a "defaultlist".
    When you ask kila an index that doesn't exist yet,
    the object grows the list until that item exists.
    So o[n] will always work.

    Supports negative indices kila actual items.
    e.g. o[-1] ni an element immediately preceding o[0].
    """

    eleza __init__(self):
        self._start = 0
        self._array = []
        self._constructor = _text_accumulator

    eleza __getitem__(self, i):
        i -= self._start
        ikiwa i < 0:
            self._start += i
            prefix = [self._constructor() kila x kwenye range(-i)]
            self._array = prefix + self._array
            i = 0
        wakati i >= len(self._array):
            self._array.append(self._constructor())
        rudisha self._array[i]

    eleza clear(self):
        kila ta kwenye self._array:
            ta._text.clear()

    eleza dump(self):
        texts = [ta.output() kila ta kwenye self._array]
        rudisha "".join(texts)


kundi Destination:
    eleza __init__(self, name, type, clinic, *args):
        self.name = name
        self.type = type
        self.clinic = clinic
        valid_types = ('buffer', 'file', 'suppress')
        ikiwa type haiko kwenye valid_types:
            fail("Invalid destination type " + repr(type) + " kila " + name + " , must be " + ', '.join(valid_types))
        extra_arguments = 1 ikiwa type == "file" isipokua 0
        ikiwa len(args) < extra_arguments:
            fail("Not enough arguments kila destination " + name + " new " + type)
        ikiwa len(args) > extra_arguments:
            fail("Too many arguments kila destination " + name + " new " + type)
        ikiwa type =='file':
            d = {}
            filename = clinic.filename
            d['path'] = filename
            dirname, basename = os.path.split(filename)
            ikiwa sio dirname:
                dirname = '.'
            d['dirname'] = dirname
            d['basename'] = basename
            d['basename_root'], d['basename_extension'] = os.path.splitext(filename)
            self.filename = args[0].format_map(d)

        self.buffers = BufferSeries()

    eleza __repr__(self):
        ikiwa self.type == 'file':
            file_repr = " " + repr(self.filename)
        isipokua:
            file_repr = ''
        rudisha "".join(("<Destination ", self.name, " ", self.type, file_repr, ">"))

    eleza clear(self):
        ikiwa self.type != 'buffer':
            fail("Can't clear destination" + self.name + " , it's sio of type buffer")
        self.buffers.clear()

    eleza dump(self):
        rudisha self.buffers.dump()


# maps strings to Language objects.
# "languages" maps the name of the language ("C", "Python").
# "extensions" maps the file extension ("c", "py").
languages = { 'C': CLanguage, 'Python': PythonLanguage }
extensions = { name: CLanguage kila name kwenye "c cc cpp cxx h hh hpp hxx".split() }
extensions['py'] = PythonLanguage


# maps strings to callables.
# these callables must be of the form:
#   eleza foo(name, default, *, ...)
# The callable may have any number of keyword-only parameters.
# The callable must rudisha a CConverter object.
# The callable should sio call builtins.print.
converters = {}

# maps strings to callables.
# these callables follow the same rules kama those kila "converters" above.
# note however that they will never be called ukijumuisha keyword-only parameters.
legacy_converters = {}


# maps strings to callables.
# these callables must be of the form:
#   eleza foo(*, ...)
# The callable may have any number of keyword-only parameters.
# The callable must rudisha a CConverter object.
# The callable should sio call builtins.print.
return_converters = {}

clinic = Tupu
kundi Clinic:

    presets_text = """
preset block
everything block
methoddef_ifneleza buffer 1
docstring_prototype suppress
parser_prototype suppress
cpp_ikiwa suppress
cpp_endikiwa suppress

preset original
everything block
methoddef_ifneleza buffer 1
docstring_prototype suppress
parser_prototype suppress
cpp_ikiwa suppress
cpp_endikiwa suppress

preset file
everything file
methoddef_ifneleza file 1
docstring_prototype suppress
parser_prototype suppress
impl_definition block

preset buffer
everything buffer
methoddef_ifneleza buffer 1
impl_definition block
docstring_prototype suppress
impl_prototype suppress
parser_prototype suppress

preset partial-buffer
everything buffer
methoddef_ifneleza buffer 1
docstring_prototype block
impl_prototype suppress
methoddef_define block
parser_prototype block
impl_definition block

"""

    eleza __init__(self, language, printer=Tupu, *, force=Uongo, verify=Kweli, filename=Tupu):
        # maps strings to Parser objects.
        # (instantiated kutoka the "parsers" global.)
        self.parsers = {}
        self.language = language
        ikiwa printer:
            fail("Custom printers are broken right now")
        self.printer = printer ama BlockPrinter(language)
        self.verify = verify
        self.force = force
        self.filename = filename
        self.modules = collections.OrderedDict()
        self.classes = collections.OrderedDict()
        self.functions = []

        self.line_prefix = self.line_suffix = ''

        self.destinations = {}
        self.add_destination("block", "buffer")
        self.add_destination("suppress", "suppress")
        self.add_destination("buffer", "buffer")
        ikiwa filename:
            self.add_destination("file", "file", "{dirname}/clinic/{basename}.h")

        d = self.get_destination_buffer
        self.destination_buffers = collections.OrderedDict((
            ('cpp_if', d('file')),
            ('docstring_prototype', d('suppress')),
            ('docstring_definition', d('file')),
            ('methoddef_define', d('file')),
            ('impl_prototype', d('file')),
            ('parser_prototype', d('suppress')),
            ('parser_definition', d('file')),
            ('cpp_endif', d('file')),
            ('methoddef_ifndef', d('file', 1)),
            ('impl_definition', d('block')),
        ))

        self.destination_buffers_stack = []
        self.ifndef_symbols = set()

        self.presets = {}
        preset = Tupu
        kila line kwenye self.presets_text.strip().split('\n'):
            line = line.strip()
            ikiwa sio line:
                endelea
            name, value, *options = line.split()
            ikiwa name == 'preset':
                self.presets[value] = preset = collections.OrderedDict()
                endelea

            ikiwa len(options):
                index = int(options[0])
            isipokua:
                index = 0
            buffer = self.get_destination_buffer(value, index)

            ikiwa name == 'everything':
                kila name kwenye self.destination_buffers:
                    preset[name] = buffer
                endelea

            assert name kwenye self.destination_buffers
            preset[name] = buffer

        global clinic
        clinic = self

    eleza add_destination(self, name, type, *args):
        ikiwa name kwenye self.destinations:
            fail("Destination already exists: " + repr(name))
        self.destinations[name] = Destination(name, type, self, *args)

    eleza get_destination(self, name):
        d = self.destinations.get(name)
        ikiwa sio d:
            fail("Destination does sio exist: " + repr(name))
        rudisha d

    eleza get_destination_buffer(self, name, item=0):
        d = self.get_destination(name)
        rudisha d.buffers[item]

    eleza parse(self, input):
        printer = self.printer
        self.block_parser = BlockParser(input, self.language, verify=self.verify)
        kila block kwenye self.block_parser:
            dsl_name = block.dsl_name
            ikiwa dsl_name:
                ikiwa dsl_name haiko kwenye self.parsers:
                    assert dsl_name kwenye parsers, "No parser to handle {!r} block.".format(dsl_name)
                    self.parsers[dsl_name] = parsers[dsl_name](self)
                parser = self.parsers[dsl_name]
                jaribu:
                    parser.parse(block)
                tatizo Exception:
                    fail('Exception raised during parsing:\n' +
                         traceback.format_exc().rstrip())
            printer.print_block(block)

        second_pita_replacements = {}

        # these are destinations sio buffers
        kila name, destination kwenye self.destinations.items():
            ikiwa destination.type == 'suppress':
                endelea
            output = destination.dump()

            ikiwa output:

                block = Block("", dsl_name="clinic", output=output)

                ikiwa destination.type == 'buffer':
                    block.input = "dump " + name + "\n"
                    warn("Destination buffer " + repr(name) + " sio empty at end of file, emptying.")
                    printer.write("\n")
                    printer.print_block(block)
                    endelea

                ikiwa destination.type == 'file':
                    jaribu:
                        dirname = os.path.dirname(destination.filename)
                        jaribu:
                            os.makedirs(dirname)
                        tatizo FileExistsError:
                            ikiwa sio os.path.isdir(dirname):
                                fail("Can't write to destination {}, "
                                     "can't make directory {}!".format(
                                        destination.filename, dirname))
                        ikiwa self.verify:
                            ukijumuisha open(destination.filename, "rt") kama f:
                                parser_2 = BlockParser(f.read(), language=self.language)
                                blocks = list(parser_2)
                                ikiwa (len(blocks) != 1) ama (blocks[0].input != 'preserve\n'):
                                    fail("Modified destination file " + repr(destination.filename) + ", sio overwriting!")
                    tatizo FileNotFoundError:
                        pita

                    block.input = 'preserve\n'
                    printer_2 = BlockPrinter(self.language)
                    printer_2.print_block(block)
                    ukijumuisha open(destination.filename, "wt") kama f:
                        f.write(printer_2.f.getvalue())
                    endelea
        text = printer.f.getvalue()

        ikiwa second_pita_replacements:
            printer_2 = BlockPrinter(self.language)
            parser_2 = BlockParser(text, self.language)
            changed = Uongo
            kila block kwenye parser_2:
                ikiwa block.dsl_name:
                    kila id, replacement kwenye second_pita_replacements.items():
                        ikiwa id kwenye block.output:
                            changed = Kweli
                            block.output = block.output.replace(id, replacement)
                printer_2.print_block(block)
            ikiwa changed:
                text = printer_2.f.getvalue()

        rudisha text


    eleza _module_and_class(self, fields):
        """
        fields should be an iterable of field names.
        returns a tuple of (module, class).
        the module object could actually be self (a clinic object).
        this function ni only ever used to find the parent of where
        a new class/module should go.
        """
        in_classes = Uongo
        parent = module = self
        cls = Tupu
        so_far = []

        kila field kwenye fields:
            so_far.append(field)
            ikiwa sio in_classes:
                child = parent.modules.get(field)
                ikiwa child:
                    parent = module = child
                    endelea
                in_classes = Kweli
            ikiwa sio hasattr(parent, 'classes'):
                rudisha module, cls
            child = parent.classes.get(field)
            ikiwa sio child:
                fail('Parent kundi ama module ' + '.'.join(so_far) + " does sio exist.")
            cls = parent = child

        rudisha module, cls


eleza parse_file(filename, *, force=Uongo, verify=Kweli, output=Tupu, encoding='utf-8'):
    extension = os.path.splitext(filename)[1][1:]
    ikiwa sio extension:
        fail("Can't extract file type kila file " + repr(filename))

    jaribu:
        language = extensions[extension](filename)
    tatizo KeyError:
        fail("Can't identify file type kila file " + repr(filename))

    ukijumuisha open(filename, 'r', encoding=encoding) kama f:
        raw = f.read()

    # exit quickly ikiwa there are no clinic markers kwenye the file
    find_start_re = BlockParser("", language).find_start_re
    ikiwa sio find_start_re.search(raw):
        rudisha

    clinic = Clinic(language, force=force, verify=verify, filename=filename)
    cooked = clinic.parse(raw)
    ikiwa (cooked == raw) na sio force:
        rudisha

    directory = os.path.dirname(filename) ama '.'

    ukijumuisha tempfile.TemporaryDirectory(prefix="clinic", dir=directory) kama tmpdir:
        bytes = cooked.encode(encoding)
        tmpfilename = os.path.join(tmpdir, os.path.basename(filename))
        ukijumuisha open(tmpfilename, "wb") kama f:
            f.write(bytes)
        os.replace(tmpfilename, output ama filename)


eleza compute_checksum(input, length=Tupu):
    input = input ama ''
    s = hashlib.sha1(input.encode('utf-8')).hexdigest()
    ikiwa length:
        s = s[:length]
    rudisha s




kundi PythonParser:
    eleza __init__(self, clinic):
        pita

    eleza parse(self, block):
        s = io.StringIO()
        ukijumuisha OverrideStdioWith(s):
            exec(block.input)
        block.output = s.getvalue()


kundi Module:
    eleza __init__(self, name, module=Tupu):
        self.name = name
        self.module = self.parent = module

        self.modules = collections.OrderedDict()
        self.classes = collections.OrderedDict()
        self.functions = []

    eleza __repr__(self):
        rudisha "<clinic.Module " + repr(self.name) + " at " + str(id(self)) + ">"

kundi Class:
    eleza __init__(self, name, module=Tupu, cls=Tupu, typedef=Tupu, type_object=Tupu):
        self.name = name
        self.module = module
        self.cls = cls
        self.typeeleza = typedef
        self.type_object = type_object
        self.parent = cls ama module

        self.classes = collections.OrderedDict()
        self.functions = []

    eleza __repr__(self):
        rudisha "<clinic.Class " + repr(self.name) + " at " + str(id(self)) + ">"

unsupported_special_methods = set("""

__abs__
__add__
__and__
__bytes__
__call__
__complex__
__delitem__
__divmod__
__eq__
__float__
__floordiv__
__ge__
__getattr__
__getattribute__
__getitem__
__gt__
__hash__
__iadd__
__iand__
__ifloordiv__
__ilshift__
__imatmul__
__imod__
__imul__
__index__
__int__
__invert__
__ior__
__ipow__
__irshift__
__isub__
__iter__
__itruediv__
__ixor__
__le__
__len__
__lshift__
__lt__
__matmul__
__mod__
__mul__
__neg__
__new__
__next__
__or__
__pos__
__pow__
__radd__
__rand__
__rdivmod__
__repr__
__rfloordiv__
__rlshift__
__rmatmul__
__rmod__
__rmul__
__ror__
__rpow__
__rrshift__
__rshift__
__rsub__
__rtruediv__
__rxor__
__setattr__
__setitem__
__str__
__sub__
__truediv__
__xor__

""".strip().split())


INVALID, CALLABLE, STATIC_METHOD, CLASS_METHOD, METHOD_INIT, METHOD_NEW = """
INVALID, CALLABLE, STATIC_METHOD, CLASS_METHOD, METHOD_INIT, METHOD_NEW
""".replace(",", "").strip().split()

kundi Function:
    """
    Mutable duck type kila inspect.Function.

    docstring - a str containing
        * embedded line komas
        * text outdented to the left margin
        * no trailing whitespace.
        It will always be true that
            (sio docstring) ama ((sio docstring[0].isspace()) na (docstring.rstrip() == docstring))
    """

    eleza __init__(self, parameters=Tupu, *, name,
                 module, cls=Tupu, c_basename=Tupu,
                 full_name=Tupu,
                 return_converter, return_annotation=inspect.Signature.empty,
                 docstring=Tupu, kind=CALLABLE, coexist=Uongo,
                 docstring_only=Uongo):
        self.parameters = parameters ama collections.OrderedDict()
        self.return_annotation = return_annotation
        self.name = name
        self.full_name = full_name
        self.module = module
        self.cls = cls
        self.parent = cls ama module
        self.c_basename = c_basename
        self.return_converter = return_converter
        self.docstring = docstring ama ''
        self.kind = kind
        self.coexist = coexist
        self.self_converter = Tupu
        # docstring_only means "don't generate a machine-readable
        # signature, just a normal docstring".  it's Kweli for
        # functions ukijumuisha optional groups because we can't represent
        # those accurately ukijumuisha inspect.Signature kwenye 3.4.
        self.docstring_only = docstring_only

        self.rendered_parameters = Tupu

    __render_parameters__ = Tupu
    @property
    eleza render_parameters(self):
        ikiwa sio self.__render_parameters__:
            self.__render_parameters__ = l = []
            kila p kwenye self.parameters.values():
                p = p.copy()
                p.converter.pre_render()
                l.append(p)
        rudisha self.__render_parameters__

    @property
    eleza methoddef_flags(self):
        ikiwa self.kind kwenye (METHOD_INIT, METHOD_NEW):
            rudisha Tupu
        flags = []
        ikiwa self.kind == CLASS_METHOD:
            flags.append('METH_CLASS')
        lasivyo self.kind == STATIC_METHOD:
            flags.append('METH_STATIC')
        isipokua:
            assert self.kind == CALLABLE, "unknown kind: " + repr(self.kind)
        ikiwa self.coexist:
            flags.append('METH_COEXIST')
        rudisha '|'.join(flags)

    eleza __repr__(self):
        rudisha '<clinic.Function ' + self.name + '>'

    eleza copy(self, **overrides):
        kwargs = {
            'name': self.name, 'module': self.module, 'parameters': self.parameters,
            'cls': self.cls, 'c_basename': self.c_basename,
            'full_name': self.full_name,
            'return_converter': self.return_converter, 'return_annotation': self.return_annotation,
            'docstring': self.docstring, 'kind': self.kind, 'coexist': self.coexist,
            'docstring_only': self.docstring_only,
            }
        kwargs.update(overrides)
        f = Function(**kwargs)

        parameters = collections.OrderedDict()
        kila name, value kwenye f.parameters.items():
            value = value.copy(function=f)
            parameters[name] = value
        f.parameters = parameters
        rudisha f


kundi Parameter:
    """
    Mutable duck type of inspect.Parameter.
    """

    eleza __init__(self, name, kind, *, default=inspect.Parameter.empty,
                 function, converter, annotation=inspect.Parameter.empty,
                 docstring=Tupu, group=0):
        self.name = name
        self.kind = kind
        self.default = default
        self.function = function
        self.converter = converter
        self.annotation = annotation
        self.docstring = docstring ama ''
        self.group = group

    eleza __repr__(self):
        rudisha '<clinic.Parameter ' + self.name + '>'

    eleza is_keyword_only(self):
        rudisha self.kind == inspect.Parameter.KEYWORD_ONLY

    eleza is_positional_only(self):
        rudisha self.kind == inspect.Parameter.POSITIONAL_ONLY

    eleza is_optional(self):
        rudisha (self.default ni sio unspecified)

    eleza copy(self, **overrides):
        kwargs = {
            'name': self.name, 'kind': self.kind, 'default':self.default,
                 'function': self.function, 'converter': self.converter, 'annotation': self.annotation,
                 'docstring': self.docstring, 'group': self.group,
            }
        kwargs.update(overrides)
        ikiwa 'converter' haiko kwenye overrides:
            converter = copy.copy(self.converter)
            converter.function = kwargs['function']
            kwargs['converter'] = converter
        rudisha Parameter(**kwargs)

    eleza get_displayname(self, i):
        ikiwa i == 0:
            rudisha '"argument"'
        ikiwa sio self.is_positional_only():
            rudisha '''"argument '{}'"'''.format(self.name)
        isipokua:
            rudisha '"argument {}"'.format(i)


kundi LandMine:
    # try to access any
    eleza __init__(self, message):
        self.__message__ = message

    eleza __repr__(self):
        rudisha '<LandMine ' + repr(self.__message__) + ">"

    eleza __getattribute__(self, name):
        ikiwa name kwenye ('__repr__', '__message__'):
            rudisha super().__getattribute__(name)
        # ashiria RuntimeError(repr(name))
        fail("Stepped on a land mine, trying to access attribute " + repr(name) + ":\n" + self.__message__)


eleza add_c_converter(f, name=Tupu):
    ikiwa sio name:
        name = f.__name__
        ikiwa sio name.endswith('_converter'):
            rudisha f
        name = name[:-len('_converter')]
    converters[name] = f
    rudisha f

eleza add_default_legacy_c_converter(cls):
    # automatically add converter kila default format unit
    # (but without stomping on the existing one ikiwa it's already
    # set, kwenye case you subclass)
    ikiwa ((cls.format_unit haiko kwenye ('O&', '')) na
        (cls.format_unit haiko kwenye legacy_converters)):
        legacy_converters[cls.format_unit] = cls
    rudisha cls

eleza add_legacy_c_converter(format_unit, **kwargs):
    """
    Adds a legacy converter.
    """
    eleza closure(f):
        ikiwa sio kwargs:
            added_f = f
        isipokua:
            added_f = functools.partial(f, **kwargs)
        ikiwa format_unit:
            legacy_converters[format_unit] = added_f
        rudisha f
    rudisha closure

kundi CConverterAutoRegister(type):
    eleza __init__(cls, name, bases, classdict):
        add_c_converter(cls)
        add_default_legacy_c_converter(cls)

kundi CConverter(metaclass=CConverterAutoRegister):
    """
    For the init function, self, name, function, na default
    must be keyword-or-positional parameters.  All other
    parameters must be keyword-only.
    """

    # The C name to use kila this variable.
    name = Tupu

    # The Python name to use kila this variable.
    py_name = Tupu

    # The C type to use kila this variable.
    # 'type' should be a Python string specifying the type, e.g. "int".
    # If this ni a pointer type, the type string should end ukijumuisha ' *'.
    type = Tupu

    # The Python default value kila this parameter, kama a Python value.
    # Or the magic value "unspecified" ikiwa there ni no default.
    # Or the magic value "unknown" ikiwa this value ni a cannot be evaluated
    # at Argument-Clinic-preprocessing time (but ni presumed to be valid
    # at runtime).
    default = unspecified

    # If sio Tupu, default must be isinstance() of this type.
    # (You can also specify a tuple of types.)
    default_type = Tupu

    # "default" converted into a C value, kama a string.
    # Or Tupu ikiwa there ni no default.
    c_default = Tupu

    # "default" converted into a Python value, kama a string.
    # Or Tupu ikiwa there ni no default.
    py_default = Tupu

    # The default value used to initialize the C variable when
    # there ni no default, but sio specifying a default may
    # result kwenye an "uninitialized variable" warning.  This can
    # easily happen when using option groups--although
    # properly-written code won't actually use the variable,
    # the variable does get pitaed kwenye to the _impl.  (Ah, if
    # only dataflow analysis could inline the static function!)
    #
    # This value ni specified kama a string.
    # Every non-abstract subkundi should supply a valid value.
    c_ignored_default = 'NULL'

    # The C converter *function* to be used, ikiwa any.
    # (If this ni sio Tupu, format_unit must be 'O&'.)
    converter = Tupu

    # Should Argument Clinic add a '&' before the name of
    # the variable when pitaing it into the _impl function?
    impl_by_reference = Uongo

    # Should Argument Clinic add a '&' before the name of
    # the variable when pitaing it into PyArg_ParseTuple (AndKeywords)?
    parse_by_reference = Kweli

    #############################################################
    #############################################################
    ## You shouldn't need to read anything below this point to ##
    ## write your own converter functions.                     ##
    #############################################################
    #############################################################

    # The "format unit" to specify kila this variable when
    # parsing arguments using PyArg_ParseTuple (AndKeywords).
    # Custom converters should always use the default value of 'O&'.
    format_unit = 'O&'

    # What encoding do we want kila this variable?  Only used
    # by format units starting ukijumuisha 'e'.
    encoding = Tupu

    # Should this object be required to be a subkundi of a specific type?
    # If sio Tupu, should be a string representing a pointer to a
    # PyTypeObject (e.g. "&PyUnicode_Type").
    # Only used by the 'O!' format unit (and the "object" converter).
    subclass_of = Tupu

    # Do we want an adjacent '_length' variable kila this variable?
    # Only used by format units ending ukijumuisha '#'.
    length = Uongo

    # Should we show this parameter kwenye the generated
    # __text_signature__? This ni *almost* always Kweli.
    # (It's only Uongo kila __new__, __init__, na METH_STATIC functions.)
    show_in_signature = Kweli

    # Overrides the name used kwenye a text signature.
    # The name used kila a "self" parameter must be one of
    # self, type, ama module; however users can set their own.
    # This lets the self_converter overrule the user-settable
    # name, *just* kila the text signature.
    # Only set by self_converter.
    signature_name = Tupu

    # keep kwenye sync ukijumuisha self_converter.__init__!
    eleza __init__(self, name, py_name, function, default=unspecified, *, c_default=Tupu, py_default=Tupu, annotation=unspecified, **kwargs):
        self.name = ensure_legal_c_identifier(name)
        self.py_name = py_name

        ikiwa default ni sio unspecified:
            ikiwa self.default_type na sio isinstance(default, (self.default_type, Unknown)):
                ikiwa isinstance(self.default_type, type):
                    types_str = self.default_type.__name__
                isipokua:
                    types_str = ', '.join((cls.__name__ kila cls kwenye self.default_type))
                fail("{}: default value {!r} kila field {} ni sio of type {}".format(
                    self.__class__.__name__, default, name, types_str))
            self.default = default

        ikiwa c_default:
            self.c_default = c_default
        ikiwa py_default:
            self.py_default = py_default

        ikiwa annotation != unspecified:
            fail("The 'annotation' parameter ni sio currently permitted.")

        # this ni deliberate, to prevent you kutoka caching information
        # about the function kwenye the init.
        # (that komas ikiwa we get cloned.)
        # so after this change we will noisily fail.
        self.function = LandMine("Don't access members of self.function inside converter_init!")
        self.converter_init(**kwargs)
        self.function = function

    eleza converter_init(self):
        pita

    eleza is_optional(self):
        rudisha (self.default ni sio unspecified)

    eleza _render_self(self, parameter, data):
        self.parameter = parameter
        name = self.name

        # impl_arguments
        s = ("&" ikiwa self.impl_by_reference isipokua "") + name
        data.impl_arguments.append(s)
        ikiwa self.length:
            data.impl_arguments.append(self.length_name())

        # impl_parameters
        data.impl_parameters.append(self.simple_declaration(by_reference=self.impl_by_reference))
        ikiwa self.length:
            data.impl_parameters.append("Py_ssize_clean_t " + self.length_name())

    eleza _render_non_self(self, parameter, data):
        self.parameter = parameter
        name = self.name

        # declarations
        d = self.declaration()
        data.declarations.append(d)

        # initializers
        initializers = self.initialize()
        ikiwa initializers:
            data.initializers.append('/* initializers kila ' + name + ' */\n' + initializers.rstrip())

        # modifications
        modifications = self.modify()
        ikiwa modifications:
            data.modifications.append('/* modifications kila ' + name + ' */\n' + modifications.rstrip())

        # keywords
        ikiwa parameter.is_positional_only():
            data.keywords.append('')
        isipokua:
            data.keywords.append(parameter.name)

        # format_units
        ikiwa self.is_optional() na '|' haiko kwenye data.format_units:
            data.format_units.append('|')
        ikiwa parameter.is_keyword_only() na '$' haiko kwenye data.format_units:
            data.format_units.append('$')
        data.format_units.append(self.format_unit)

        # parse_arguments
        self.parse_argument(data.parse_arguments)

        # cleanup
        cleanup = self.cleanup()
        ikiwa cleanup:
            data.cleanup.append('/* Cleanup kila ' + name + ' */\n' + cleanup.rstrip() + "\n")

    eleza render(self, parameter, data):
        """
        parameter ni a clinic.Parameter instance.
        data ni a CRenderData instance.
        """
        self._render_self(parameter, data)
        self._render_non_self(parameter, data)

    eleza length_name(self):
        """Computes the name of the associated "length" variable."""
        ikiwa sio self.length:
            rudisha Tupu
        rudisha self.name + "_length"

    # Why ni this one broken out separately?
    # For "positional-only" function parsing,
    # which generates a bunch of PyArg_ParseTuple calls.
    eleza parse_argument(self, list):
        assert sio (self.converter na self.encoding)
        ikiwa self.format_unit == 'O&':
            assert self.converter
            list.append(self.converter)

        ikiwa self.encoding:
            list.append(c_repr(self.encoding))
        lasivyo self.subclass_of:
            list.append(self.subclass_of)

        s = ("&" ikiwa self.parse_by_reference isipokua "") + self.name
        list.append(s)

        ikiwa self.length:
            list.append("&" + self.length_name())

    #
    # All the functions after here are intended kama extension points.
    #

    eleza simple_declaration(self, by_reference=Uongo):
        """
        Computes the basic declaration of the variable.
        Used kwenye computing the prototype declaration na the
        variable declaration.
        """
        prototype = [self.type]
        ikiwa by_reference ama sio self.type.endswith('*'):
            prototype.append(" ")
        ikiwa by_reference:
            prototype.append('*')
        prototype.append(self.name)
        rudisha "".join(prototype)

    eleza declaration(self):
        """
        The C statement to declare this variable.
        """
        declaration = [self.simple_declaration()]
        default = self.c_default
        ikiwa sio default na self.parameter.group:
            default = self.c_ignored_default
        ikiwa default:
            declaration.append(" = ")
            declaration.append(default)
        declaration.append(";")
        ikiwa self.length:
            declaration.append('\nPy_ssize_clean_t ')
            declaration.append(self.length_name())
            declaration.append(';')
        rudisha "".join(declaration)

    eleza initialize(self):
        """
        The C statements required to set up this variable before parsing.
        Returns a string containing this code indented at column 0.
        If no initialization ni necessary, returns an empty string.
        """
        rudisha ""

    eleza modify(self):
        """
        The C statements required to modify this variable after parsing.
        Returns a string containing this code indented at column 0.
        If no initialization ni necessary, returns an empty string.
        """
        rudisha ""

    eleza cleanup(self):
        """
        The C statements required to clean up after this variable.
        Returns a string containing this code indented at column 0.
        If no cleanup ni necessary, returns an empty string.
        """
        rudisha ""

    eleza pre_render(self):
        """
        A second initialization function, like converter_init,
        called just before rendering.
        You are permitted to examine self.function here.
        """
        pita

    eleza parse_arg(self, argname, displayname):
        ikiwa self.format_unit == 'O&':
            rudisha """
                ikiwa (!{converter}({argname}, &{paramname})) {{{{
                    goto exit;
                }}}}
                """.format(argname=argname, paramname=self.name,
                           converter=self.converter)
        ikiwa self.format_unit == 'O!':
            cast = '(%s)' % self.type ikiwa self.type != 'PyObject *' isipokua ''
            ikiwa self.subclass_of kwenye type_checks:
                typecheck, typename = type_checks[self.subclass_of]
                rudisha """
                    ikiwa (!{typecheck}({argname})) {{{{
                        _PyArg_BadArgument("{{name}}", {displayname}, "{typename}", {argname});
                        goto exit;
                    }}}}
                    {paramname} = {cast}{argname};
                    """.format(argname=argname, paramname=self.name,
                               displayname=displayname, typecheck=typecheck,
                               typename=typename, cast=cast)
            rudisha """
                ikiwa (!PyObject_TypeCheck({argname}, {subclass_of})) {{{{
                    _PyArg_BadArgument("{{name}}", {displayname}, ({subclass_of})->tp_name, {argname});
                    goto exit;
                }}}}
                {paramname} = {cast}{argname};
                """.format(argname=argname, paramname=self.name,
                           subclass_of=self.subclass_of, cast=cast,
                           displayname=displayname)
        ikiwa self.format_unit == 'O':
            cast = '(%s)' % self.type ikiwa self.type != 'PyObject *' isipokua ''
            rudisha """
                {paramname} = {cast}{argname};
                """.format(argname=argname, paramname=self.name, cast=cast)
        rudisha Tupu

type_checks = {
    '&PyLong_Type': ('PyLong_Check', 'int'),
    '&PyTuple_Type': ('PyTuple_Check', 'tuple'),
    '&PyList_Type': ('PyList_Check', 'list'),
    '&PySet_Type': ('PySet_Check', 'set'),
    '&PyFrozenSet_Type': ('PyFrozenSet_Check', 'frozenset'),
    '&PyDict_Type': ('PyDict_Check', 'dict'),
    '&PyUnicode_Type': ('PyUnicode_Check', 'str'),
    '&PyBytes_Type': ('PyBytes_Check', 'bytes'),
    '&PyByteArray_Type': ('PyByteArray_Check', 'bytearray'),
}


kundi bool_converter(CConverter):
    type = 'int'
    default_type = bool
    format_unit = 'p'
    c_ignored_default = '0'

    eleza converter_init(self, *, accept={object}):
        ikiwa accept == {int}:
            self.format_unit = 'i'
        lasivyo accept != {object}:
            fail("bool_converter: illegal 'accept' argument " + repr(accept))
        ikiwa self.default ni sio unspecified:
            self.default = bool(self.default)
            self.c_default = str(int(self.default))

    eleza parse_arg(self, argname, displayname):
        ikiwa self.format_unit == 'i':
            # XXX PyFloat_Check can be removed after the end of the
            # deprecation kwenye _PyLong_FromNbIndexOrNbInt.
            rudisha """
                ikiwa (PyFloat_Check({argname})) {{{{
                    PyErr_SetString(PyExc_TypeError,
                                    "integer argument expected, got float" );
                    goto exit;
                }}}}
                {paramname} = _PyLong_AsInt({argname});
                ikiwa ({paramname} == -1 && PyErr_Occurred()) {{{{
                    goto exit;
                }}}}
                """.format(argname=argname, paramname=self.name)
        lasivyo self.format_unit == 'p':
            rudisha """
                {paramname} = PyObject_IsKweli({argname});
                ikiwa ({paramname} < 0) {{{{
                    goto exit;
                }}}}
                """.format(argname=argname, paramname=self.name)
        rudisha super().parse_arg(argname, displayname)

kundi char_converter(CConverter):
    type = 'char'
    default_type = (bytes, bytearray)
    format_unit = 'c'
    c_ignored_default = "'\0'"

    eleza converter_init(self):
        ikiwa isinstance(self.default, self.default_type):
            ikiwa len(self.default) != 1:
                fail("char_converter: illegal default value " + repr(self.default))

            self.c_default = repr(bytes(self.default))[1:]
            ikiwa self.c_default == '"\'"':
                self.c_default = r"'\''"

    eleza parse_arg(self, argname, displayname):
        ikiwa self.format_unit == 'c':
            rudisha """
                ikiwa (PyBytes_Check({argname}) && PyBytes_GET_SIZE({argname}) == 1) {{{{
                    {paramname} = PyBytes_AS_STRING({argname})[0];
                }}}}
                isipokua ikiwa (PyByteArray_Check({argname}) && PyByteArray_GET_SIZE({argname}) == 1) {{{{
                    {paramname} = PyByteArray_AS_STRING({argname})[0];
                }}}}
                isipokua {{{{
                    _PyArg_BadArgument("{{name}}", {displayname}, "a byte string of length 1", {argname});
                    goto exit;
                }}}}
                """.format(argname=argname, paramname=self.name,
                           displayname=displayname)
        rudisha super().parse_arg(argname, displayname)


@add_legacy_c_converter('B', bitwise=Kweli)
kundi unsigned_char_converter(CConverter):
    type = 'unsigned char'
    default_type = int
    format_unit = 'b'
    c_ignored_default = "'\0'"

    eleza converter_init(self, *, bitwise=Uongo):
        ikiwa bitwise:
            self.format_unit = 'B'

    eleza parse_arg(self, argname, displayname):
        ikiwa self.format_unit == 'b':
            rudisha """
                ikiwa (PyFloat_Check({argname})) {{{{
                    PyErr_SetString(PyExc_TypeError,
                                    "integer argument expected, got float" );
                    goto exit;
                }}}}
                {{{{
                    long ival = PyLong_AsLong({argname});
                    ikiwa (ival == -1 && PyErr_Occurred()) {{{{
                        goto exit;
                    }}}}
                    isipokua ikiwa (ival < 0) {{{{
                        PyErr_SetString(PyExc_OverflowError,
                                        "unsigned byte integer ni less than minimum");
                        goto exit;
                    }}}}
                    isipokua ikiwa (ival > UCHAR_MAX) {{{{
                        PyErr_SetString(PyExc_OverflowError,
                                        "unsigned byte integer ni greater than maximum");
                        goto exit;
                    }}}}
                    isipokua {{{{
                        {paramname} = (unsigned char) ival;
                    }}}}
                }}}}
                """.format(argname=argname, paramname=self.name)
        lasivyo self.format_unit == 'B':
            rudisha """
                ikiwa (PyFloat_Check({argname})) {{{{
                    PyErr_SetString(PyExc_TypeError,
                                    "integer argument expected, got float" );
                    goto exit;
                }}}}
                {{{{
                    long ival = PyLong_AsUnsignedLongMask({argname});
                    ikiwa (ival == -1 && PyErr_Occurred()) {{{{
                        goto exit;
                    }}}}
                    isipokua {{{{
                        {paramname} = (unsigned char) ival;
                    }}}}
                }}}}
                """.format(argname=argname, paramname=self.name)
        rudisha super().parse_arg(argname, displayname)

kundi byte_converter(unsigned_char_converter): pita

kundi short_converter(CConverter):
    type = 'short'
    default_type = int
    format_unit = 'h'
    c_ignored_default = "0"

    eleza parse_arg(self, argname, displayname):
        ikiwa self.format_unit == 'h':
            rudisha """
                ikiwa (PyFloat_Check({argname})) {{{{
                    PyErr_SetString(PyExc_TypeError,
                                    "integer argument expected, got float" );
                    goto exit;
                }}}}
                {{{{
                    long ival = PyLong_AsLong({argname});
                    ikiwa (ival == -1 && PyErr_Occurred()) {{{{
                        goto exit;
                    }}}}
                    isipokua ikiwa (ival < SHRT_MIN) {{{{
                        PyErr_SetString(PyExc_OverflowError,
                                        "signed short integer ni less than minimum");
                        goto exit;
                    }}}}
                    isipokua ikiwa (ival > SHRT_MAX) {{{{
                        PyErr_SetString(PyExc_OverflowError,
                                        "signed short integer ni greater than maximum");
                        goto exit;
                    }}}}
                    isipokua {{{{
                        {paramname} = (short) ival;
                    }}}}
                }}}}
                """.format(argname=argname, paramname=self.name)
        rudisha super().parse_arg(argname, displayname)

kundi unsigned_short_converter(CConverter):
    type = 'unsigned short'
    default_type = int
    c_ignored_default = "0"

    eleza converter_init(self, *, bitwise=Uongo):
        ikiwa bitwise:
            self.format_unit = 'H'
        isipokua:
            self.converter = '_PyLong_UnsignedShort_Converter'

    eleza parse_arg(self, argname, displayname):
        ikiwa self.format_unit == 'H':
            rudisha """
                ikiwa (PyFloat_Check({argname})) {{{{
                    PyErr_SetString(PyExc_TypeError,
                                    "integer argument expected, got float" );
                    goto exit;
                }}}}
                {paramname} = (unsigned short)PyLong_AsUnsignedLongMask({argname});
                ikiwa ({paramname} == (unsigned short)-1 && PyErr_Occurred()) {{{{
                    goto exit;
                }}}}
                """.format(argname=argname, paramname=self.name)
        rudisha super().parse_arg(argname, displayname)

@add_legacy_c_converter('C', accept={str})
kundi int_converter(CConverter):
    type = 'int'
    default_type = int
    format_unit = 'i'
    c_ignored_default = "0"

    eleza converter_init(self, *, accept={int}, type=Tupu):
        ikiwa accept == {str}:
            self.format_unit = 'C'
        lasivyo accept != {int}:
            fail("int_converter: illegal 'accept' argument " + repr(accept))
        ikiwa type != Tupu:
            self.type = type

    eleza parse_arg(self, argname, displayname):
        ikiwa self.format_unit == 'i':
            rudisha """
                ikiwa (PyFloat_Check({argname})) {{{{
                    PyErr_SetString(PyExc_TypeError,
                                    "integer argument expected, got float" );
                    goto exit;
                }}}}
                {paramname} = _PyLong_AsInt({argname});
                ikiwa ({paramname} == -1 && PyErr_Occurred()) {{{{
                    goto exit;
                }}}}
                """.format(argname=argname, paramname=self.name)
        lasivyo self.format_unit == 'C':
            rudisha """
                ikiwa (!PyUnicode_Check({argname})) {{{{
                    _PyArg_BadArgument("{{name}}", {displayname}, "a unicode character", {argname});
                    goto exit;
                }}}}
                ikiwa (PyUnicode_READY({argname})) {{{{
                    goto exit;
                }}}}
                ikiwa (PyUnicode_GET_LENGTH({argname}) != 1) {{{{
                    _PyArg_BadArgument("{{name}}", {displayname}, "a unicode character", {argname});
                    goto exit;
                }}}}
                {paramname} = PyUnicode_READ_CHAR({argname}, 0);
                """.format(argname=argname, paramname=self.name,
                           displayname=displayname)
        rudisha super().parse_arg(argname, displayname)

kundi unsigned_int_converter(CConverter):
    type = 'unsigned int'
    default_type = int
    c_ignored_default = "0"

    eleza converter_init(self, *, bitwise=Uongo):
        ikiwa bitwise:
            self.format_unit = 'I'
        isipokua:
            self.converter = '_PyLong_UnsignedInt_Converter'

    eleza parse_arg(self, argname, displayname):
        ikiwa self.format_unit == 'I':
            rudisha """
                ikiwa (PyFloat_Check({argname})) {{{{
                    PyErr_SetString(PyExc_TypeError,
                                    "integer argument expected, got float" );
                    goto exit;
                }}}}
                {paramname} = (unsigned int)PyLong_AsUnsignedLongMask({argname});
                ikiwa ({paramname} == (unsigned int)-1 && PyErr_Occurred()) {{{{
                    goto exit;
                }}}}
                """.format(argname=argname, paramname=self.name)
        rudisha super().parse_arg(argname, displayname)

kundi long_converter(CConverter):
    type = 'long'
    default_type = int
    format_unit = 'l'
    c_ignored_default = "0"

    eleza parse_arg(self, argname, displayname):
        ikiwa self.format_unit == 'l':
            rudisha """
                ikiwa (PyFloat_Check({argname})) {{{{
                    PyErr_SetString(PyExc_TypeError,
                                    "integer argument expected, got float" );
                    goto exit;
                }}}}
                {paramname} = PyLong_AsLong({argname});
                ikiwa ({paramname} == -1 && PyErr_Occurred()) {{{{
                    goto exit;
                }}}}
                """.format(argname=argname, paramname=self.name)
        rudisha super().parse_arg(argname, displayname)

kundi unsigned_long_converter(CConverter):
    type = 'unsigned long'
    default_type = int
    c_ignored_default = "0"

    eleza converter_init(self, *, bitwise=Uongo):
        ikiwa bitwise:
            self.format_unit = 'k'
        isipokua:
            self.converter = '_PyLong_UnsignedLong_Converter'

    eleza parse_arg(self, argname, displayname):
        ikiwa self.format_unit == 'k':
            rudisha """
                ikiwa (!PyLong_Check({argname})) {{{{
                    _PyArg_BadArgument("{{name}}", {displayname}, "int", {argname});
                    goto exit;
                }}}}
                {paramname} = PyLong_AsUnsignedLongMask({argname});
                """.format(argname=argname, paramname=self.name,
                           displayname=displayname)
        rudisha super().parse_arg(argname, displayname)

kundi long_long_converter(CConverter):
    type = 'long long'
    default_type = int
    format_unit = 'L'
    c_ignored_default = "0"

    eleza parse_arg(self, argname, displayname):
        ikiwa self.format_unit == 'L':
            rudisha """
                ikiwa (PyFloat_Check({argname})) {{{{
                    PyErr_SetString(PyExc_TypeError,
                                    "integer argument expected, got float" );
                    goto exit;
                }}}}
                {paramname} = PyLong_AsLongLong({argname});
                ikiwa ({paramname} == (PY_LONG_LONG)-1 && PyErr_Occurred()) {{{{
                    goto exit;
                }}}}
                """.format(argname=argname, paramname=self.name)
        rudisha super().parse_arg(argname, displayname)

kundi unsigned_long_long_converter(CConverter):
    type = 'unsigned long long'
    default_type = int
    c_ignored_default = "0"

    eleza converter_init(self, *, bitwise=Uongo):
        ikiwa bitwise:
            self.format_unit = 'K'
        isipokua:
            self.converter = '_PyLong_UnsignedLongLong_Converter'

    eleza parse_arg(self, argname, displayname):
        ikiwa self.format_unit == 'K':
            rudisha """
                ikiwa (!PyLong_Check({argname})) {{{{
                    _PyArg_BadArgument("{{name}}", {displayname}, "int", {argname});
                    goto exit;
                }}}}
                {paramname} = PyLong_AsUnsignedLongLongMask({argname});
                """.format(argname=argname, paramname=self.name,
                           displayname=displayname)
        rudisha super().parse_arg(argname, displayname)

kundi Py_ssize_t_converter(CConverter):
    type = 'Py_ssize_t'
    c_ignored_default = "0"

    eleza converter_init(self, *, accept={int}):
        ikiwa accept == {int}:
            self.format_unit = 'n'
            self.default_type = int
        lasivyo accept == {int, TupuType}:
            self.converter = '_Py_convert_optional_to_ssize_t'
        isipokua:
            fail("Py_ssize_t_converter: illegal 'accept' argument " + repr(accept))

    eleza parse_arg(self, argname, displayname):
        ikiwa self.format_unit == 'n':
            rudisha """
                ikiwa (PyFloat_Check({argname})) {{{{
                    PyErr_SetString(PyExc_TypeError,
                                    "integer argument expected, got float" );
                    goto exit;
                }}}}
                {{{{
                    Py_ssize_t ival = -1;
                    PyObject *iobj = PyNumber_Index({argname});
                    ikiwa (iobj != NULL) {{{{
                        ival = PyLong_AsSsize_t(iobj);
                        Py_DECREF(iobj);
                    }}}}
                    ikiwa (ival == -1 && PyErr_Occurred()) {{{{
                        goto exit;
                    }}}}
                    {paramname} = ival;
                }}}}
                """.format(argname=argname, paramname=self.name)
        rudisha super().parse_arg(argname, displayname)


kundi slice_index_converter(CConverter):
    type = 'Py_ssize_t'

    eleza converter_init(self, *, accept={int, TupuType}):
        ikiwa accept == {int}:
            self.converter = '_PyEval_SliceIndexNotTupu'
        lasivyo accept == {int, TupuType}:
            self.converter = '_PyEval_SliceIndex'
        isipokua:
            fail("slice_index_converter: illegal 'accept' argument " + repr(accept))

kundi size_t_converter(CConverter):
    type = 'size_t'
    converter = '_PyLong_Size_t_Converter'
    c_ignored_default = "0"

    eleza parse_arg(self, argname, displayname):
        ikiwa self.format_unit == 'n':
            rudisha """
                {paramname} = PyNumber_AsSsize_t({argname}, PyExc_OverflowError);
                ikiwa ({paramname} == -1 && PyErr_Occurred()) {{{{
                    goto exit;
                }}}}
                """.format(argname=argname, paramname=self.name)
        rudisha super().parse_arg(argname, displayname)


kundi float_converter(CConverter):
    type = 'float'
    default_type = float
    format_unit = 'f'
    c_ignored_default = "0.0"

    eleza parse_arg(self, argname, displayname):
        ikiwa self.format_unit == 'f':
            rudisha """
                ikiwa (PyFloat_CheckExact({argname})) {{{{
                    {paramname} = (float) (PyFloat_AS_DOUBLE({argname}));
                }}}}
                isipokua
                {{{{
                    {paramname} = (float) PyFloat_AsDouble({argname});
                    ikiwa ({paramname} == -1.0 && PyErr_Occurred()) {{{{
                        goto exit;
                    }}}}
                }}}}
                """.format(argname=argname, paramname=self.name)
        rudisha super().parse_arg(argname, displayname)

kundi double_converter(CConverter):
    type = 'double'
    default_type = float
    format_unit = 'd'
    c_ignored_default = "0.0"

    eleza parse_arg(self, argname, displayname):
        ikiwa self.format_unit == 'd':
            rudisha """
                ikiwa (PyFloat_CheckExact({argname})) {{{{
                    {paramname} = PyFloat_AS_DOUBLE({argname});
                }}}}
                isipokua
                {{{{
                    {paramname} = PyFloat_AsDouble({argname});
                    ikiwa ({paramname} == -1.0 && PyErr_Occurred()) {{{{
                        goto exit;
                    }}}}
                }}}}
                """.format(argname=argname, paramname=self.name)
        rudisha super().parse_arg(argname, displayname)


kundi Py_complex_converter(CConverter):
    type = 'Py_complex'
    default_type = complex
    format_unit = 'D'
    c_ignored_default = "{0.0, 0.0}"

    eleza parse_arg(self, argname, displayname):
        ikiwa self.format_unit == 'D':
            rudisha """
                {paramname} = PyComplex_AsCComplex({argname});
                ikiwa (PyErr_Occurred()) {{{{
                    goto exit;
                }}}}
                """.format(argname=argname, paramname=self.name)
        rudisha super().parse_arg(argname, displayname)


kundi object_converter(CConverter):
    type = 'PyObject *'
    format_unit = 'O'

    eleza converter_init(self, *, converter=Tupu, type=Tupu, subclass_of=Tupu):
        ikiwa converter:
            ikiwa subclass_of:
                fail("object: Cannot pita kwenye both 'converter' na 'subclass_of'")
            self.format_unit = 'O&'
            self.converter = converter
        lasivyo subclass_of:
            self.format_unit = 'O!'
            self.subclass_of = subclass_of

        ikiwa type ni sio Tupu:
            self.type = type


#
# We define three conventions kila buffer types kwenye the 'accept' argument:
#
#  buffer  : any object supporting the buffer interface
#  rwbuffer: any object supporting the buffer interface, but must be writeable
#  robuffer: any object supporting the buffer interface, but must sio be writeable
#

kundi buffer: pita
kundi rwbuffer: pita
kundi robuffer: pita

eleza str_converter_key(types, encoding, zeroes):
    rudisha (frozenset(types), bool(encoding), bool(zeroes))

str_converter_argument_map = {}

kundi str_converter(CConverter):
    type = 'const char *'
    default_type = (str, Null, TupuType)
    format_unit = 's'

    eleza converter_init(self, *, accept={str}, encoding=Tupu, zeroes=Uongo):

        key = str_converter_key(accept, encoding, zeroes)
        format_unit = str_converter_argument_map.get(key)
        ikiwa sio format_unit:
            fail("str_converter: illegal combination of arguments", key)

        self.format_unit = format_unit
        self.length = bool(zeroes)
        ikiwa encoding:
            ikiwa self.default haiko kwenye (Null, Tupu, unspecified):
                fail("str_converter: Argument Clinic doesn't support default values kila encoded strings")
            self.encoding = encoding
            self.type = 'char *'
            # sorry, clinic can't support preallocated buffers
            # kila es# na et#
            self.c_default = "NULL"
        ikiwa TupuType kwenye accept na self.c_default == "Py_Tupu":
            self.c_default = "NULL"

    eleza cleanup(self):
        ikiwa self.encoding:
            name = self.name
            rudisha "".join(["ikiwa (", name, ") {\n   PyMem_FREE(", name, ");\n}\n"])

    eleza parse_arg(self, argname, displayname):
        ikiwa self.format_unit == 's':
            rudisha """
                ikiwa (!PyUnicode_Check({argname})) {{{{
                    _PyArg_BadArgument("{{name}}", {displayname}, "str", {argname});
                    goto exit;
                }}}}
                Py_ssize_t {paramname}_length;
                {paramname} = PyUnicode_AsUTF8AndSize({argname}, &{paramname}_length);
                ikiwa ({paramname} == NULL) {{{{
                    goto exit;
                }}}}
                ikiwa (strlen({paramname}) != (size_t){paramname}_length) {{{{
                    PyErr_SetString(PyExc_ValueError, "embedded null character");
                    goto exit;
                }}}}
                """.format(argname=argname, paramname=self.name,
                           displayname=displayname)
        ikiwa self.format_unit == 'z':
            rudisha """
                ikiwa ({argname} == Py_Tupu) {{{{
                    {paramname} = NULL;
                }}}}
                isipokua ikiwa (PyUnicode_Check({argname})) {{{{
                    Py_ssize_t {paramname}_length;
                    {paramname} = PyUnicode_AsUTF8AndSize({argname}, &{paramname}_length);
                    ikiwa ({paramname} == NULL) {{{{
                        goto exit;
                    }}}}
                    ikiwa (strlen({paramname}) != (size_t){paramname}_length) {{{{
                        PyErr_SetString(PyExc_ValueError, "embedded null character");
                        goto exit;
                    }}}}
                }}}}
                isipokua {{{{
                    _PyArg_BadArgument("{{name}}", {displayname}, "str ama Tupu", {argname});
                    goto exit;
                }}}}
                """.format(argname=argname, paramname=self.name,
                           displayname=displayname)
        rudisha super().parse_arg(argname, displayname)

#
# This ni the fourth ama fifth rewrite of registering all the
# string converter format units.  Previous approaches hid
# bugs--generally mismatches between the semantics of the format
# unit na the arguments necessary to represent those semantics
# properly.  Hopefully ukijumuisha this approach we'll get it 100% right.
#
# The r() function (short kila "register") both registers the
# mapping kutoka arguments to format unit *and* registers the
# legacy C converter kila that format unit.
#
eleza r(format_unit, *, accept, encoding=Uongo, zeroes=Uongo):
    ikiwa sio encoding na format_unit != 's':
        # add the legacy c converters here too.
        #
        # note: add_legacy_c_converter can't work for
        #   es, es#, et, ama et#
        #   because of their extra encoding argument
        #
        # also don't add the converter kila 's' because
        # the metakundi kila CConverter adds it kila us.
        kwargs = {}
        ikiwa accept != {str}:
            kwargs['accept'] = accept
        ikiwa zeroes:
            kwargs['zeroes'] = Kweli
        added_f = functools.partial(str_converter, **kwargs)
        legacy_converters[format_unit] = added_f

    d = str_converter_argument_map
    key = str_converter_key(accept, encoding, zeroes)
    ikiwa key kwenye d:
        sys.exit("Duplicate keys specified kila str_converter_argument_map!")
    d[key] = format_unit

r('es',  encoding=Kweli,              accept={str})
r('es#', encoding=Kweli, zeroes=Kweli, accept={str})
r('et',  encoding=Kweli,              accept={bytes, bytearray, str})
r('et#', encoding=Kweli, zeroes=Kweli, accept={bytes, bytearray, str})
r('s',                               accept={str})
r('s#',                 zeroes=Kweli, accept={robuffer, str})
r('y',                               accept={robuffer})
r('y#',                 zeroes=Kweli, accept={robuffer})
r('z',                               accept={str, TupuType})
r('z#',                 zeroes=Kweli, accept={robuffer, str, TupuType})
toa r


kundi PyBytesObject_converter(CConverter):
    type = 'PyBytesObject *'
    format_unit = 'S'
    # accept = {bytes}

    eleza parse_arg(self, argname, displayname):
        ikiwa self.format_unit == 'S':
            rudisha """
                ikiwa (!PyBytes_Check({argname})) {{{{
                    _PyArg_BadArgument("{{name}}", {displayname}, "bytes", {argname});
                    goto exit;
                }}}}
                {paramname} = ({type}){argname};
                """.format(argname=argname, paramname=self.name,
                           type=self.type, displayname=displayname)
        rudisha super().parse_arg(argname, displayname)

kundi PyByteArrayObject_converter(CConverter):
    type = 'PyByteArrayObject *'
    format_unit = 'Y'
    # accept = {bytearray}

    eleza parse_arg(self, argname, displayname):
        ikiwa self.format_unit == 'Y':
            rudisha """
                ikiwa (!PyByteArray_Check({argname})) {{{{
                    _PyArg_BadArgument("{{name}}", {displayname}, "bytearray", {argname});
                    goto exit;
                }}}}
                {paramname} = ({type}){argname};
                """.format(argname=argname, paramname=self.name,
                           type=self.type, displayname=displayname)
        rudisha super().parse_arg(argname, displayname)

kundi unicode_converter(CConverter):
    type = 'PyObject *'
    default_type = (str, Null, TupuType)
    format_unit = 'U'

    eleza parse_arg(self, argname, displayname):
        ikiwa self.format_unit == 'U':
            rudisha """
                ikiwa (!PyUnicode_Check({argname})) {{{{
                    _PyArg_BadArgument("{{name}}", {displayname}, "str", {argname});
                    goto exit;
                }}}}
                ikiwa (PyUnicode_READY({argname}) == -1) {{{{
                    goto exit;
                }}}}
                {paramname} = {argname};
                """.format(argname=argname, paramname=self.name,
                           displayname=displayname)
        rudisha super().parse_arg(argname, displayname)

@add_legacy_c_converter('u#', zeroes=Kweli)
@add_legacy_c_converter('Z', accept={str, TupuType})
@add_legacy_c_converter('Z#', accept={str, TupuType}, zeroes=Kweli)
kundi Py_UNICODE_converter(CConverter):
    type = 'const Py_UNICODE *'
    default_type = (str, Null, TupuType)
    format_unit = 'u'

    eleza converter_init(self, *, accept={str}, zeroes=Uongo):
        format_unit = 'Z' ikiwa accept=={str, TupuType} isipokua 'u'
        ikiwa zeroes:
            format_unit += '#'
            self.length = Kweli
        self.format_unit = format_unit

@add_legacy_c_converter('s*', accept={str, buffer})
@add_legacy_c_converter('z*', accept={str, buffer, TupuType})
@add_legacy_c_converter('w*', accept={rwbuffer})
kundi Py_buffer_converter(CConverter):
    type = 'Py_buffer'
    format_unit = 'y*'
    impl_by_reference = Kweli
    c_ignored_default = "{NULL, NULL}"

    eleza converter_init(self, *, accept={buffer}):
        ikiwa self.default haiko kwenye (unspecified, Tupu):
            fail("The only legal default value kila Py_buffer ni Tupu.")

        self.c_default = self.c_ignored_default

        ikiwa accept == {str, buffer, TupuType}:
            format_unit = 'z*'
        lasivyo accept == {str, buffer}:
            format_unit = 's*'
        lasivyo accept == {buffer}:
            format_unit = 'y*'
        lasivyo accept == {rwbuffer}:
            format_unit = 'w*'
        isipokua:
            fail("Py_buffer_converter: illegal combination of arguments")

        self.format_unit = format_unit

    eleza cleanup(self):
        name = self.name
        rudisha "".join(["ikiwa (", name, ".obj) {\n   PyBuffer_Release(&", name, ");\n}\n"])

    eleza parse_arg(self, argname, displayname):
        ikiwa self.format_unit == 'y*':
            rudisha """
                ikiwa (PyObject_GetBuffer({argname}, &{paramname}, PyBUF_SIMPLE) != 0) {{{{
                    goto exit;
                }}}}
                ikiwa (!PyBuffer_IsContiguous(&{paramname}, 'C')) {{{{
                    _PyArg_BadArgument("{{name}}", {displayname}, "contiguous buffer", {argname});
                    goto exit;
                }}}}
                """.format(argname=argname, paramname=self.name,
                           displayname=displayname)
        lasivyo self.format_unit == 's*':
            rudisha """
                ikiwa (PyUnicode_Check({argname})) {{{{
                    Py_ssize_t len;
                    const char *ptr = PyUnicode_AsUTF8AndSize({argname}, &len);
                    ikiwa (ptr == NULL) {{{{
                        goto exit;
                    }}}}
                    PyBuffer_FillInfo(&{paramname}, {argname}, (void *)ptr, len, 1, 0);
                }}}}
                isipokua {{{{ /* any bytes-like object */
                    ikiwa (PyObject_GetBuffer({argname}, &{paramname}, PyBUF_SIMPLE) != 0) {{{{
                        goto exit;
                    }}}}
                    ikiwa (!PyBuffer_IsContiguous(&{paramname}, 'C')) {{{{
                        _PyArg_BadArgument("{{name}}", {displayname}, "contiguous buffer", {argname});
                        goto exit;
                    }}}}
                }}}}
                """.format(argname=argname, paramname=self.name,
                           displayname=displayname)
        lasivyo self.format_unit == 'w*':
            rudisha """
                ikiwa (PyObject_GetBuffer({argname}, &{paramname}, PyBUF_WRITABLE) < 0) {{{{
                    PyErr_Clear();
                    _PyArg_BadArgument("{{name}}", {displayname}, "read-write bytes-like object", {argname});
                    goto exit;
                }}}}
                ikiwa (!PyBuffer_IsContiguous(&{paramname}, 'C')) {{{{
                    _PyArg_BadArgument("{{name}}", {displayname}, "contiguous buffer", {argname});
                    goto exit;
                }}}}
                """.format(argname=argname, paramname=self.name,
                           displayname=displayname)
        rudisha super().parse_arg(argname, displayname)


eleza correct_name_for_self(f):
    ikiwa f.kind kwenye (CALLABLE, METHOD_INIT):
        ikiwa f.cls:
            rudisha "PyObject *", "self"
        rudisha "PyObject *", "module"
    ikiwa f.kind == STATIC_METHOD:
        rudisha "void *", "null"
    ikiwa f.kind kwenye (CLASS_METHOD, METHOD_NEW):
        rudisha "PyTypeObject *", "type"
    ashiria RuntimeError("Unhandled type of function f: " + repr(f.kind))

eleza required_type_for_self_for_parser(f):
    type, _ = correct_name_for_self(f)
    ikiwa f.kind kwenye (METHOD_INIT, METHOD_NEW, STATIC_METHOD, CLASS_METHOD):
        rudisha type
    rudisha Tupu


kundi self_converter(CConverter):
    """
    A special-case converter:
    this ni the default converter used kila "self".
    """
    type = Tupu
    format_unit = ''

    eleza converter_init(self, *, type=Tupu):
        self.specified_type = type

    eleza pre_render(self):
        f = self.function
        default_type, default_name = correct_name_for_self(f)
        self.signature_name = default_name
        self.type = self.specified_type ama self.type ama default_type

        kind = self.function.kind
        new_or_init = kind kwenye (METHOD_NEW, METHOD_INIT)

        ikiwa (kind == STATIC_METHOD) ama new_or_init:
            self.show_in_signature = Uongo

    # tp_new (METHOD_NEW) functions are of type newfunc:
    #     typeeleza PyObject *(*newfunc)(struct _typeobject *, PyObject *, PyObject *);
    # PyTypeObject ni a typeeleza kila struct _typeobject.
    #
    # tp_init (METHOD_INIT) functions are of type initproc:
    #     typeeleza int (*initproc)(PyObject *, PyObject *, PyObject *);
    #
    # All other functions generated by Argument Clinic are stored in
    # PyMethodDef structures, kwenye the ml_meth slot, which ni of type PyCFunction:
    #     typeeleza PyObject *(*PyCFunction)(PyObject *, PyObject *);
    # However!  We habitually cast these functions to PyCFunction,
    # since functions that accept keyword arguments don't fit this signature
    # but are stored there anyway.  So strict type equality isn't important
    # kila these functions.
    #
    # So:
    #
    # * The name of the first parameter to the impl na the parsing function will always
    #   be self.name.
    #
    # * The type of the first parameter to the impl will always be of self.type.
    #
    # * If the function ni neither tp_new (METHOD_NEW) nor tp_init (METHOD_INIT):
    #   * The type of the first parameter to the parsing function ni also self.type.
    #     This means that ikiwa you step into the parsing function, your "self" parameter
    #     ni of the correct type, which may make debugging more pleasant.
    #
    # * Else ikiwa the function ni tp_new (METHOD_NEW):
    #   * The type of the first parameter to the parsing function ni "PyTypeObject *",
    #     so the type signature of the function call ni an exact match.
    #   * If self.type != "PyTypeObject *", we cast the first parameter to self.type
    #     kwenye the impl call.
    #
    # * Else ikiwa the function ni tp_init (METHOD_INIT):
    #   * The type of the first parameter to the parsing function ni "PyObject *",
    #     so the type signature of the function call ni an exact match.
    #   * If self.type != "PyObject *", we cast the first parameter to self.type
    #     kwenye the impl call.

    @property
    eleza parser_type(self):
        rudisha required_type_for_self_for_parser(self.function) ama self.type

    eleza render(self, parameter, data):
        """
        parameter ni a clinic.Parameter instance.
        data ni a CRenderData instance.
        """
        ikiwa self.function.kind == STATIC_METHOD:
            rudisha

        self._render_self(parameter, data)

        ikiwa self.type != self.parser_type:
            # insert cast to impl_argument[0], aka self.
            # we know we're kwenye the first slot kwenye all the CRenderData lists,
            # because we render parameters kwenye order, na self ni always first.
            assert len(data.impl_arguments) == 1
            assert data.impl_arguments[0] == self.name
            data.impl_arguments[0] = '(' + self.type + ")" + data.impl_arguments[0]

    eleza set_template_dict(self, template_dict):
        template_dict['self_name'] = self.name
        template_dict['self_type'] = self.parser_type
        kind = self.function.kind
        cls = self.function.cls

        ikiwa ((kind kwenye (METHOD_NEW, METHOD_INIT)) na cls na cls.typedef):
            ikiwa kind == METHOD_NEW:
                pitaed_in_type = self.name
            isipokua:
                pitaed_in_type = 'Py_TYPE({})'.format(self.name)

            line = '({pitaed_in_type} == {type_object}) &&\n        '
            d = {
                'type_object': self.function.cls.type_object,
                'pitaed_in_type': pitaed_in_type
                }
            template_dict['self_type_check'] = line.format_map(d)



eleza add_c_return_converter(f, name=Tupu):
    ikiwa sio name:
        name = f.__name__
        ikiwa sio name.endswith('_return_converter'):
            rudisha f
        name = name[:-len('_return_converter')]
    return_converters[name] = f
    rudisha f


kundi CReturnConverterAutoRegister(type):
    eleza __init__(cls, name, bases, classdict):
        add_c_return_converter(cls)

kundi CReturnConverter(metaclass=CReturnConverterAutoRegister):

    # The C type to use kila this variable.
    # 'type' should be a Python string specifying the type, e.g. "int".
    # If this ni a pointer type, the type string should end ukijumuisha ' *'.
    type = 'PyObject *'

    # The Python default value kila this parameter, kama a Python value.
    # Or the magic value "unspecified" ikiwa there ni no default.
    default = Tupu

    eleza __init__(self, *, py_default=Tupu, **kwargs):
        self.py_default = py_default
        jaribu:
            self.return_converter_init(**kwargs)
        tatizo TypeError kama e:
            s = ', '.join(name + '=' + repr(value) kila name, value kwenye kwargs.items())
            sys.exit(self.__class__.__name__ + '(' + s + ')\n' + str(e))

    eleza return_converter_init(self):
        pita

    eleza declare(self, data, name="_return_value"):
        line = []
        add = line.append
        add(self.type)
        ikiwa sio self.type.endswith('*'):
            add(' ')
        add(name + ';')
        data.declarations.append(''.join(line))
        data.return_value = name

    eleza err_occurred_if(self, expr, data):
        data.return_conversion.append('ikiwa (({}) && PyErr_Occurred()) {{\n    goto exit;\n}}\n'.format(expr))

    eleza err_occurred_if_null_pointer(self, variable, data):
        data.return_conversion.append('ikiwa ({} == NULL) {{\n    goto exit;\n}}\n'.format(variable))

    eleza render(self, function, data):
        """
        function ni a clinic.Function instance.
        data ni a CRenderData instance.
        """
        pita

add_c_return_converter(CReturnConverter, 'object')

kundi TupuType_return_converter(CReturnConverter):
    eleza render(self, function, data):
        self.declare(data)
        data.return_conversion.append('''
ikiwa (_return_value != Py_Tupu) {
    goto exit;
}
return_value = Py_Tupu;
Py_INCREF(Py_Tupu);
'''.strip())

kundi bool_return_converter(CReturnConverter):
    type = 'int'

    eleza render(self, function, data):
        self.declare(data)
        self.err_occurred_if("_return_value == -1", data)
        data.return_conversion.append('return_value = PyBool_FromLong((long)_return_value);\n')

kundi long_return_converter(CReturnConverter):
    type = 'long'
    conversion_fn = 'PyLong_FromLong'
    cast = ''
    unsigned_cast = ''

    eleza render(self, function, data):
        self.declare(data)
        self.err_occurred_if("_return_value == {}-1".format(self.unsigned_cast), data)
        data.return_conversion.append(
            ''.join(('return_value = ', self.conversion_fn, '(', self.cast, '_return_value);\n')))

kundi int_return_converter(long_return_converter):
    type = 'int'
    cast = '(long)'

kundi init_return_converter(long_return_converter):
    """
    Special rudisha converter kila __init__ functions.
    """
    type = 'int'
    cast = '(long)'

    eleza render(self, function, data):
        pita

kundi unsigned_long_return_converter(long_return_converter):
    type = 'unsigned long'
    conversion_fn = 'PyLong_FromUnsignedLong'
    unsigned_cast = '(unsigned long)'

kundi unsigned_int_return_converter(unsigned_long_return_converter):
    type = 'unsigned int'
    cast = '(unsigned long)'
    unsigned_cast = '(unsigned int)'

kundi Py_ssize_t_return_converter(long_return_converter):
    type = 'Py_ssize_t'
    conversion_fn = 'PyLong_FromSsize_t'

kundi size_t_return_converter(long_return_converter):
    type = 'size_t'
    conversion_fn = 'PyLong_FromSize_t'
    unsigned_cast = '(size_t)'


kundi double_return_converter(CReturnConverter):
    type = 'double'
    cast = ''

    eleza render(self, function, data):
        self.declare(data)
        self.err_occurred_if("_return_value == -1.0", data)
        data.return_conversion.append(
            'return_value = PyFloat_FromDouble(' + self.cast + '_return_value);\n')

kundi float_return_converter(double_return_converter):
    type = 'float'
    cast = '(double)'


eleza eval_ast_expr(node, globals, *, filename='-'):
    """
    Takes an ast.Expr node.  Compiles na evaluates it.
    Returns the result of the expression.

    globals represents the globals dict the expression
    should see.  (There's no equivalent kila "locals" here.)
    """

    ikiwa isinstance(node, ast.Expr):
        node = node.value

    node = ast.Expression(node)
    co = compile(node, filename, 'eval')
    fn = types.FunctionType(co, globals)
    rudisha fn()


kundi IndentStack:
    eleza __init__(self):
        self.indents = []
        self.margin = Tupu

    eleza _ensure(self):
        ikiwa sio self.indents:
            fail('IndentStack expected indents, but none are defined.')

    eleza measure(self, line):
        """
        Returns the length of the line's margin.
        """
        ikiwa '\t' kwenye line:
            fail('Tab characters are illegal kwenye the Argument Clinic DSL.')
        stripped = line.lstrip()
        ikiwa sio len(stripped):
            # we can't tell anything kutoka an empty line
            # so just pretend it's indented like our current indent
            self._ensure()
            rudisha self.indents[-1]
        rudisha len(line) - len(stripped)

    eleza infer(self, line):
        """
        Infer what ni now the current margin based on this line.
        Returns:
            1 ikiwa we have indented (or this ni the first margin)
            0 ikiwa the margin has sio changed
           -N ikiwa we have dedented N times
        """
        indent = self.measure(line)
        margin = ' ' * indent
        ikiwa sio self.indents:
            self.indents.append(indent)
            self.margin = margin
            rudisha 1
        current = self.indents[-1]
        ikiwa indent == current:
            rudisha 0
        ikiwa indent > current:
            self.indents.append(indent)
            self.margin = margin
            rudisha 1
        # indent < current
        ikiwa indent haiko kwenye self.indents:
            fail("Illegal outdent.")
        outdent_count = 0
        wakati indent != current:
            self.indents.pop()
            current = self.indents[-1]
            outdent_count -= 1
        self.margin = margin
        rudisha outdent_count

    @property
    eleza depth(self):
        """
        Returns how many margins are currently defined.
        """
        rudisha len(self.indents)

    eleza indent(self, line):
        """
        Indents a line by the currently defined margin.
        """
        rudisha self.margin + line

    eleza dedent(self, line):
        """
        Dedents a line by the currently defined margin.
        (The inverse of 'indent'.)
        """
        margin = self.margin
        indent = self.indents[-1]
        ikiwa sio line.startswith(margin):
            fail('Cannot dedent, line does sio start ukijumuisha the previous margin:')
        rudisha line[indent:]


kundi DSLParser:
    eleza __init__(self, clinic):
        self.clinic = clinic

        self.directives = {}
        kila name kwenye dir(self):
            # functions that start ukijumuisha directive_ are added to directives
            _, s, key = name.partition("directive_")
            ikiwa s:
                self.directives[key] = getattr(self, name)

            # functions that start ukijumuisha at_ are too, ukijumuisha an @ kwenye front
            _, s, key = name.partition("at_")
            ikiwa s:
                self.directives['@' + key] = getattr(self, name)

        self.reset()

    eleza reset(self):
        self.function = Tupu
        self.state = self.state_dsl_start
        self.parameter_indent = Tupu
        self.keyword_only = Uongo
        self.positional_only = Uongo
        self.group = 0
        self.parameter_state = self.ps_start
        self.seen_positional_with_default = Uongo
        self.indent = IndentStack()
        self.kind = CALLABLE
        self.coexist = Uongo
        self.parameter_continuation = ''
        self.preserve_output = Uongo

    eleza directive_version(self, required):
        global version
        ikiwa version_comparitor(version, required) < 0:
            fail("Insufficient Clinic version!\n  Version: " + version + "\n  Required: " + required)

    eleza directive_module(self, name):
        fields = name.split('.')
        new = fields.pop()
        module, cls = self.clinic._module_and_class(fields)
        ikiwa cls:
            fail("Can't nest a module inside a class!")

        ikiwa name kwenye module.classes:
            fail("Already defined module " + repr(name) + "!")

        m = Module(name, module)
        module.modules[name] = m
        self.block.signatures.append(m)

    eleza directive_class(self, name, typedef, type_object):
        fields = name.split('.')
        in_classes = Uongo
        parent = self
        name = fields.pop()
        so_far = []
        module, cls = self.clinic._module_and_class(fields)

        parent = cls ama module
        ikiwa name kwenye parent.classes:
            fail("Already defined kundi " + repr(name) + "!")

        c = Class(name, module, cls, typedef, type_object)
        parent.classes[name] = c
        self.block.signatures.append(c)

    eleza directive_set(self, name, value):
        ikiwa name haiko kwenye ("line_prefix", "line_suffix"):
            fail("unknown variable", repr(name))

        value = value.format_map({
            'block comment start': '/*',
            'block comment end': '*/',
            })

        self.clinic.__dict__[name] = value

    eleza directive_destination(self, name, command, *args):
        ikiwa command == 'new':
            self.clinic.add_destination(name, *args)
            rudisha

        ikiwa command == 'clear':
            self.clinic.get_destination(name).clear()
        fail("unknown destination command", repr(command))


    eleza directive_output(self, command_or_name, destination=''):
        fd = self.clinic.destination_buffers

        ikiwa command_or_name == "preset":
            preset = self.clinic.presets.get(destination)
            ikiwa sio preset:
                fail("Unknown preset " + repr(destination) + "!")
            fd.update(preset)
            rudisha

        ikiwa command_or_name == "push":
            self.clinic.destination_buffers_stack.append(fd.copy())
            rudisha

        ikiwa command_or_name == "pop":
            ikiwa sio self.clinic.destination_buffers_stack:
                fail("Can't 'output pop', stack ni empty!")
            previous_fd = self.clinic.destination_buffers_stack.pop()
            fd.update(previous_fd)
            rudisha

        # secret command kila debugging!
        ikiwa command_or_name == "print" ama command_or_name == "andika":
            self.block.output.append(pprint.pformat(fd))
            self.block.output.append('\n')
            rudisha

        d = self.clinic.get_destination(destination)

        ikiwa command_or_name == "everything":
            kila name kwenye list(fd):
                fd[name] = d
            rudisha

        ikiwa command_or_name haiko kwenye fd:
            fail("Invalid command / destination name " + repr(command_or_name) + ", must be one of:\n  preset push pop print everything " + " ".join(fd))
        fd[command_or_name] = d

    eleza directive_dump(self, name):
        self.block.output.append(self.clinic.get_destination(name).dump())

    eleza directive_andika(self, *args):
        self.block.output.append(' '.join(args))
        self.block.output.append('\n')

    eleza directive_preserve(self):
        ikiwa self.preserve_output:
            fail("Can't have preserve twice kwenye one block!")
        self.preserve_output = Kweli

    eleza at_classmethod(self):
        ikiwa self.kind ni sio CALLABLE:
            fail("Can't set @classmethod, function ni sio a normal callable")
        self.kind = CLASS_METHOD

    eleza at_staticmethod(self):
        ikiwa self.kind ni sio CALLABLE:
            fail("Can't set @staticmethod, function ni sio a normal callable")
        self.kind = STATIC_METHOD

    eleza at_coexist(self):
        ikiwa self.coexist:
            fail("Called @coexist twice!")
        self.coexist = Kweli

    eleza parse(self, block):
        self.reset()
        self.block = block
        self.saved_output = self.block.output
        block.output = []
        block_start = self.clinic.block_parser.line_number
        lines = block.input.split('\n')
        kila line_number, line kwenye enumerate(lines, self.clinic.block_parser.block_start_line_number):
            ikiwa '\t' kwenye line:
                fail('Tab characters are illegal kwenye the Clinic DSL.\n\t' + repr(line), line_number=block_start)
            self.state(line)

        self.next(self.state_terminal)
        self.state(Tupu)

        block.output.extend(self.clinic.language.render(clinic, block.signatures))

        ikiwa self.preserve_output:
            ikiwa block.output:
                fail("'preserve' only works kila blocks that don't produce any output!")
            block.output = self.saved_output

    @staticmethod
    eleza ignore_line(line):
        # ignore comment-only lines
        ikiwa line.lstrip().startswith('#'):
            rudisha Kweli

        # Ignore empty lines too
        # (but haiko kwenye docstring sections!)
        ikiwa sio line.strip():
            rudisha Kweli

        rudisha Uongo

    @staticmethod
    eleza calculate_indent(line):
        rudisha len(line) - len(line.strip())

    eleza next(self, state, line=Tupu):
        # real_andika(self.state.__name__, "->", state.__name__, ", line=", line)
        self.state = state
        ikiwa line ni sio Tupu:
            self.state(line)

    eleza state_dsl_start(self, line):
        # self.block = self.ClinicOutputBlock(self)
        ikiwa self.ignore_line(line):
            rudisha

        # ni it a directive?
        fields = shlex.split(line)
        directive_name = fields[0]
        directive = self.directives.get(directive_name, Tupu)
        ikiwa directive:
            jaribu:
                directive(*fields[1:])
            tatizo TypeError kama e:
                fail(str(e))
            rudisha

        self.next(self.state_modulename_name, line)

    eleza state_modulename_name(self, line):
        # looking kila declaration, which establishes the leftmost column
        # line should be
        #     modulename.fnname [as c_basename] [-> rudisha annotation]
        # square brackets denote optional syntax.
        #
        # alternatively:
        #     modulename.fnname [as c_basename] = modulename.existing_fn_name
        # clones the parameters na rudisha converter kutoka that
        # function.  you can't modify them.  you must enter a
        # new docstring.
        #
        # (but we might find a directive first!)
        #
        # this line ni permitted to start ukijumuisha whitespace.
        # we'll call this number of spaces F (kila "function").

        ikiwa sio line.strip():
            rudisha

        self.indent.infer(line)

        # are we cloning?
        before, equals, existing = line.rpartition('=')
        ikiwa equals:
            full_name, _, c_basename = before.partition(' kama ')
            full_name = full_name.strip()
            c_basename = c_basename.strip()
            existing = existing.strip()
            ikiwa (is_legal_py_identifier(full_name) na
                (sio c_basename ama is_legal_c_identifier(c_basename)) na
                is_legal_py_identifier(existing)):
                # we're cloning!
                fields = [x.strip() kila x kwenye existing.split('.')]
                function_name = fields.pop()
                module, cls = self.clinic._module_and_class(fields)

                kila existing_function kwenye (cls ama module).functions:
                    ikiwa existing_function.name == function_name:
                        koma
                isipokua:
                    existing_function = Tupu
                ikiwa sio existing_function:
                    andika("class", cls, "module", module, "existing", existing)
                    andika("cls. functions", cls.functions)
                    fail("Couldn't find existing function " + repr(existing) + "!")

                fields = [x.strip() kila x kwenye full_name.split('.')]
                function_name = fields.pop()
                module, cls = self.clinic._module_and_class(fields)

                ikiwa sio (existing_function.kind == self.kind na existing_function.coexist == self.coexist):
                    fail("'kind' of function na cloned function don't match!  (@classmethod/@staticmethod/@coexist)")
                self.function = existing_function.copy(name=function_name, full_name=full_name, module=module, cls=cls, c_basename=c_basename, docstring='')

                self.block.signatures.append(self.function)
                (cls ama module).functions.append(self.function)
                self.next(self.state_function_docstring)
                rudisha

        line, _, returns = line.partition('->')

        full_name, _, c_basename = line.partition(' kama ')
        full_name = full_name.strip()
        c_basename = c_basename.strip() ama Tupu

        ikiwa sio is_legal_py_identifier(full_name):
            fail("Illegal function name: {}".format(full_name))
        ikiwa c_basename na sio is_legal_c_identifier(c_basename):
            fail("Illegal C basename: {}".format(c_basename))

        return_converter = Tupu
        ikiwa returns:
            ast_input = "eleza x() -> {}: pita".format(returns)
            module = Tupu
            jaribu:
                module = ast.parse(ast_input)
            tatizo SyntaxError:
                pita
            ikiwa sio module:
                fail("Badly-formed annotation kila " + full_name + ": " + returns)
            jaribu:
                name, legacy, kwargs = self.parse_converter(module.body[0].returns)
                ikiwa legacy:
                    fail("Legacy converter {!r} sio allowed kama a rudisha converter"
                         .format(name))
                ikiwa name haiko kwenye return_converters:
                    fail("No available rudisha converter called " + repr(name))
                return_converter = return_converters[name](**kwargs)
            tatizo ValueError:
                fail("Badly-formed annotation kila " + full_name + ": " + returns)

        fields = [x.strip() kila x kwenye full_name.split('.')]
        function_name = fields.pop()
        module, cls = self.clinic._module_and_class(fields)

        fields = full_name.split('.')
        ikiwa fields[-1] == '__new__':
            ikiwa (self.kind != CLASS_METHOD) ama (sio cls):
                fail("__new__ must be a kundi method!")
            self.kind = METHOD_NEW
        lasivyo fields[-1] == '__init__':
            ikiwa (self.kind != CALLABLE) ama (sio cls):
                fail("__init__ must be a normal method, sio a kundi ama static method!")
            self.kind = METHOD_INIT
            ikiwa sio return_converter:
                return_converter = init_return_converter()
        lasivyo fields[-1] kwenye unsupported_special_methods:
            fail(fields[-1] + " ni a special method na cannot be converted to Argument Clinic!  (Yet.)")

        ikiwa sio return_converter:
            return_converter = CReturnConverter()

        ikiwa sio module:
            fail("Undefined module used kwenye declaration of " + repr(full_name.strip()) + ".")
        self.function = Function(name=function_name, full_name=full_name, module=module, cls=cls, c_basename=c_basename,
                                 return_converter=return_converter, kind=self.kind, coexist=self.coexist)
        self.block.signatures.append(self.function)

        # insert a self converter automatically
        type, name = correct_name_for_self(self.function)
        kwargs = {}
        ikiwa cls na type == "PyObject *":
            kwargs['type'] = cls.typedef
        sc = self.function.self_converter = self_converter(name, name, self.function, **kwargs)
        p_self = Parameter(sc.name, inspect.Parameter.POSITIONAL_ONLY, function=self.function, converter=sc)
        self.function.parameters[sc.name] = p_self

        (cls ama module).functions.append(self.function)
        self.next(self.state_parameters_start)

    # Now entering the parameters section.  The rules, formally stated:
    #
    #   * All lines must be indented ukijumuisha spaces only.
    #   * The first line must be a parameter declaration.
    #   * The first line must be indented.
    #       * This first line establishes the indent kila parameters.
    #       * We'll call this number of spaces P (kila "parameter").
    #   * Thenceforth:
    #       * Lines indented ukijumuisha P spaces specify a parameter.
    #       * Lines indented ukijumuisha > P spaces are docstrings kila the previous
    #         parameter.
    #           * We'll call this number of spaces D (kila "docstring").
    #           * All subsequent lines indented ukijumuisha >= D spaces are stored as
    #             part of the per-parameter docstring.
    #           * All lines will have the first D spaces of the indent stripped
    #             before they are stored.
    #           * It's illegal to have a line starting ukijumuisha a number of spaces X
    #             such that P < X < D.
    #       * A line ukijumuisha < P spaces ni the first line of the function
    #         docstring, which ends processing kila parameters na per-parameter
    #         docstrings.
    #           * The first line of the function docstring must be at the same
    #             indent kama the function declaration.
    #       * It's illegal to have any line kwenye the parameters section starting
    #         ukijumuisha X spaces such that F < X < P.  (As before, F ni the indent
    #         of the function declaration.)
    #
    # Also, currently Argument Clinic places the following restrictions on groups:
    #   * Each group must contain at least one parameter.
    #   * Each group may contain at most one group, which must be the furthest
    #     thing kwenye the group kutoka the required parameters.  (The nested group
    #     must be the first kwenye the group when it's before the required
    #     parameters, na the last thing kwenye the group when after the required
    #     parameters.)
    #   * There may be at most one (top-level) group to the left ama right of
    #     the required parameters.
    #   * You must specify a slash, na it must be after all parameters.
    #     (In other words: either all parameters are positional-only,
    #      ama none are.)
    #
    #  Said another way:
    #   * Each group must contain at least one parameter.
    #   * All left square brackets before the required parameters must be
    #     consecutive.  (You can't have a left square bracket followed
    #     by a parameter, then another left square bracket.  You can't
    #     have a left square bracket, a parameter, a right square bracket,
    #     na then a left square bracket.)
    #   * All right square brackets after the required parameters must be
    #     consecutive.
    #
    # These rules are enforced ukijumuisha a single state variable:
    # "parameter_state".  (Previously the code was a miasma of ifs na
    # separate boolean state variables.)  The states are:
    #
    #  [ [ a, b, ] c, ] d, e, f=3, [ g, h, [ i ] ]   <- line
    # 01   2          3       4    5           6     <- state transitions
    #
    # 0: ps_start.  before we've seen anything.  legal transitions are to 1 ama 3.
    # 1: ps_left_square_before.  left square brackets before required parameters.
    # 2: ps_group_before.  kwenye a group, before required parameters.
    # 3: ps_required.  required parameters, positional-or-keyword ama positional-only
    #     (we don't know yet).  (renumber left groups!)
    # 4: ps_optional.  positional-or-keyword ama positional-only parameters that
    #    now must have default values.
    # 5: ps_group_after.  kwenye a group, after required parameters.
    # 6: ps_right_square_after.  right square brackets after required parameters.
    ps_start, ps_left_square_before, ps_group_before, ps_required, \
    ps_optional, ps_group_after, ps_right_square_after = range(7)

    eleza state_parameters_start(self, line):
        ikiwa self.ignore_line(line):
            rudisha

        # ikiwa this line ni sio indented, we have no parameters
        ikiwa sio self.indent.infer(line):
            rudisha self.next(self.state_function_docstring, line)

        self.parameter_continuation = ''
        rudisha self.next(self.state_parameter, line)


    eleza to_required(self):
        """
        Transition to the "required" parameter state.
        """
        ikiwa self.parameter_state != self.ps_required:
            self.parameter_state = self.ps_required
            kila p kwenye self.function.parameters.values():
                p.group = -p.group

    eleza state_parameter(self, line):
        ikiwa self.parameter_continuation:
            line = self.parameter_continuation + ' ' + line.lstrip()
            self.parameter_continuation = ''

        ikiwa self.ignore_line(line):
            rudisha

        assert self.indent.depth == 2
        indent = self.indent.infer(line)
        ikiwa indent == -1:
            # we outdented, must be to definition column
            rudisha self.next(self.state_function_docstring, line)

        ikiwa indent == 1:
            # we indented, must be to new parameter docstring column
            rudisha self.next(self.state_parameter_docstring_start, line)

        line = line.rstrip()
        ikiwa line.endswith('\\'):
            self.parameter_continuation = line[:-1]
            rudisha

        line = line.lstrip()

        ikiwa line kwenye ('*', '/', '[', ']'):
            self.parse_special_symbol(line)
            rudisha

        ikiwa self.parameter_state kwenye (self.ps_start, self.ps_required):
            self.to_required()
        lasivyo self.parameter_state == self.ps_left_square_before:
            self.parameter_state = self.ps_group_before
        lasivyo self.parameter_state == self.ps_group_before:
            ikiwa sio self.group:
                self.to_required()
        lasivyo self.parameter_state kwenye (self.ps_group_after, self.ps_optional):
            pita
        isipokua:
            fail("Function " + self.function.name + " has an unsupported group configuration. (Unexpected state " + str(self.parameter_state) + ".a)")

        # handle "as" kila  parameters too
        c_name = Tupu
        name, have_as_token, trailing = line.partition(' kama ')
        ikiwa have_as_token:
            name = name.strip()
            ikiwa ' ' haiko kwenye name:
                fields = trailing.strip().split(' ')
                ikiwa sio fields:
                    fail("Invalid 'as' clause!")
                c_name = fields[0]
                ikiwa c_name.endswith(':'):
                    name += ':'
                    c_name = c_name[:-1]
                fields[0] = name
                line = ' '.join(fields)

        base, equals, default = line.rpartition('=')
        ikiwa sio equals:
            base = default
            default = Tupu

        module = Tupu
        jaribu:
            ast_input = "eleza x({}): pita".format(base)
            module = ast.parse(ast_input)
        tatizo SyntaxError:
            jaribu:
                # the last = was probably inside a function call, like
                #   c: int(accept={str})
                # so assume there was no actual default value.
                default = Tupu
                ast_input = "eleza x({}): pita".format(line)
                module = ast.parse(ast_input)
            tatizo SyntaxError:
                pita
        ikiwa sio module:
            fail("Function " + self.function.name + " has an invalid parameter declaration:\n\t" + line)

        function_args = module.body[0].args

        ikiwa len(function_args.args) > 1:
            fail("Function " + self.function.name + " has an invalid parameter declaration (comma?):\n\t" + line)
        ikiwa function_args.defaults ama function_args.kw_defaults:
            fail("Function " + self.function.name + " has an invalid parameter declaration (default value?):\n\t" + line)
        ikiwa function_args.vararg ama function_args.kwarg:
            fail("Function " + self.function.name + " has an invalid parameter declaration (*args? **kwargs?):\n\t" + line)

        parameter = function_args.args[0]

        parameter_name = parameter.arg
        name, legacy, kwargs = self.parse_converter(parameter.annotation)

        ikiwa sio default:
            ikiwa self.parameter_state == self.ps_optional:
                fail("Can't have a parameter without a default (" + repr(parameter_name) + ")\nafter a parameter ukijumuisha a default!")
            value = unspecified
            ikiwa 'py_default' kwenye kwargs:
                fail("You can't specify py_default without specifying a default value!")
        isipokua:
            ikiwa self.parameter_state == self.ps_required:
                self.parameter_state = self.ps_optional
            default = default.strip()
            bad = Uongo
            ast_input = "x = {}".format(default)
            bad = Uongo
            jaribu:
                module = ast.parse(ast_input)

                ikiwa 'c_default' haiko kwenye kwargs:
                    # we can only represent very simple data values kwenye C.
                    # detect whether default ni okay, via a blacklist
                    # of disallowed ast nodes.
                    kundi DetectBadNodes(ast.NodeVisitor):
                        bad = Uongo
                        eleza bad_node(self, node):
                            self.bad = Kweli

                        # inline function call
                        visit_Call = bad_node
                        # inline ikiwa statement ("x = 3 ikiwa y isipokua z")
                        visit_IfExp = bad_node

                        # comprehensions na generator expressions
                        visit_ListComp = visit_SetComp = bad_node
                        visit_DictComp = visit_GeneratorExp = bad_node

                        # literals kila advanced types
                        visit_Dict = visit_Set = bad_node
                        visit_List = visit_Tuple = bad_node

                        # "starred": "a = [1, 2, 3]; *a"
                        visit_Starred = bad_node

                    blacklist = DetectBadNodes()
                    blacklist.visit(module)
                    bad = blacklist.bad
                isipokua:
                    # ikiwa they specify a c_default, we can be more lenient about the default value.
                    # but at least make an attempt at ensuring it's a valid expression.
                    jaribu:
                        value = eval(default)
                        ikiwa value == unspecified:
                            fail("'unspecified' ni sio a legal default value!")
                    tatizo NameError:
                        pita # probably a named constant
                    tatizo Exception kama e:
                        fail("Malformed expression given kama default value\n"
                             "{!r} caused {!r}".format(default, e))
                ikiwa bad:
                    fail("Unsupported expression kama default value: " + repr(default))

                expr = module.body[0].value
                # mild hack: explicitly support NULL kama a default value
                ikiwa isinstance(expr, ast.Name) na expr.id == 'NULL':
                    value = NULL
                    py_default = '<unrepresentable>'
                    c_default = "NULL"
                lasivyo (isinstance(expr, ast.BinOp) ama
                    (isinstance(expr, ast.UnaryOp) na
                     sio (isinstance(expr.operand, ast.Num) ama
                          (hasattr(ast, 'Constant') na
                           isinstance(expr.operand, ast.Constant) na
                           type(expr.operand.value) kwenye (int, float, complex)))
                    )):
                    c_default = kwargs.get("c_default")
                    ikiwa sio (isinstance(c_default, str) na c_default):
                        fail("When you specify an expression (" + repr(default) + ") kama your default value,\nyou MUST specify a valid c_default." + ast.dump(expr))
                    py_default = default
                    value = unknown
                lasivyo isinstance(expr, ast.Attribute):
                    a = []
                    n = expr
                    wakati isinstance(n, ast.Attribute):
                        a.append(n.attr)
                        n = n.value
                    ikiwa sio isinstance(n, ast.Name):
                        fail("Unsupported default value " + repr(default) + " (looked like a Python constant)")
                    a.append(n.id)
                    py_default = ".".join(reversed(a))

                    c_default = kwargs.get("c_default")
                    ikiwa sio (isinstance(c_default, str) na c_default):
                        fail("When you specify a named constant (" + repr(py_default) + ") kama your default value,\nyou MUST specify a valid c_default.")

                    jaribu:
                        value = eval(py_default)
                    tatizo NameError:
                        value = unknown
                isipokua:
                    value = ast.literal_eval(expr)
                    py_default = repr(value)
                    ikiwa isinstance(value, (bool, Tupu.__class__)):
                        c_default = "Py_" + py_default
                    lasivyo isinstance(value, str):
                        c_default = c_repr(value)
                    isipokua:
                        c_default = py_default

            tatizo SyntaxError kama e:
                fail("Syntax error: " + repr(e.text))
            tatizo (ValueError, AttributeError):
                value = unknown
                c_default = kwargs.get("c_default")
                py_default = default
                ikiwa sio (isinstance(c_default, str) na c_default):
                    fail("When you specify a named constant (" + repr(py_default) + ") kama your default value,\nyou MUST specify a valid c_default.")

            kwargs.setdefault('c_default', c_default)
            kwargs.setdefault('py_default', py_default)

        dict = legacy_converters ikiwa legacy isipokua converters
        legacy_str = "legacy " ikiwa legacy isipokua ""
        ikiwa name haiko kwenye dict:
            fail('{} ni sio a valid {}converter'.format(name, legacy_str))
        # ikiwa you use a c_name kila the parameter, we just give that name to the converter
        # but the parameter object gets the python name
        converter = dict[name](c_name ama parameter_name, parameter_name, self.function, value, **kwargs)

        kind = inspect.Parameter.KEYWORD_ONLY ikiwa self.keyword_only isipokua inspect.Parameter.POSITIONAL_OR_KEYWORD

        ikiwa isinstance(converter, self_converter):
            ikiwa len(self.function.parameters) == 1:
                ikiwa (self.parameter_state != self.ps_required):
                    fail("A 'self' parameter cannot be marked optional.")
                ikiwa value ni sio unspecified:
                    fail("A 'self' parameter cannot have a default value.")
                ikiwa self.group:
                    fail("A 'self' parameter cannot be kwenye an optional group.")
                kind = inspect.Parameter.POSITIONAL_ONLY
                self.parameter_state = self.ps_start
                self.function.parameters.clear()
            isipokua:
                fail("A 'self' parameter, ikiwa specified, must be the very first thing kwenye the parameter block.")

        p = Parameter(parameter_name, kind, function=self.function, converter=converter, default=value, group=self.group)

        ikiwa parameter_name kwenye self.function.parameters:
            fail("You can't have two parameters named " + repr(parameter_name) + "!")
        self.function.parameters[parameter_name] = p

    eleza parse_converter(self, annotation):
        ikiwa (hasattr(ast, 'Constant') na
            isinstance(annotation, ast.Constant) na
            type(annotation.value) ni str):
            rudisha annotation.value, Kweli, {}

        ikiwa isinstance(annotation, ast.Str):
            rudisha annotation.s, Kweli, {}

        ikiwa isinstance(annotation, ast.Name):
            rudisha annotation.id, Uongo, {}

        ikiwa sio isinstance(annotation, ast.Call):
            fail("Annotations must be either a name, a function call, ama a string.")

        name = annotation.func.id
        symbols = globals()

        kwargs = {node.arg: eval_ast_expr(node.value, symbols) kila node kwenye annotation.keywords}
        rudisha name, Uongo, kwargs

    eleza parse_special_symbol(self, symbol):
        ikiwa symbol == '*':
            ikiwa self.keyword_only:
                fail("Function " + self.function.name + " uses '*' more than once.")
            self.keyword_only = Kweli
        lasivyo symbol == '[':
            ikiwa self.parameter_state kwenye (self.ps_start, self.ps_left_square_before):
                self.parameter_state = self.ps_left_square_before
            lasivyo self.parameter_state kwenye (self.ps_required, self.ps_group_after):
                self.parameter_state = self.ps_group_after
            isipokua:
                fail("Function " + self.function.name + " has an unsupported group configuration. (Unexpected state " + str(self.parameter_state) + ".b)")
            self.group += 1
            self.function.docstring_only = Kweli
        lasivyo symbol == ']':
            ikiwa sio self.group:
                fail("Function " + self.function.name + " has a ] without a matching [.")
            ikiwa sio any(p.group == self.group kila p kwenye self.function.parameters.values()):
                fail("Function " + self.function.name + " has an empty group.\nAll groups must contain at least one parameter.")
            self.group -= 1
            ikiwa self.parameter_state kwenye (self.ps_left_square_before, self.ps_group_before):
                self.parameter_state = self.ps_group_before
            lasivyo self.parameter_state kwenye (self.ps_group_after, self.ps_right_square_after):
                self.parameter_state = self.ps_right_square_after
            isipokua:
                fail("Function " + self.function.name + " has an unsupported group configuration. (Unexpected state " + str(self.parameter_state) + ".c)")
        lasivyo symbol == '/':
            ikiwa self.positional_only:
                fail("Function " + self.function.name + " uses '/' more than once.")
            self.positional_only = Kweli
            # ps_required na ps_optional are allowed here, that allows positional-only without option groups
            # to work (and have default values!)
            ikiwa (self.parameter_state haiko kwenye (self.ps_required, self.ps_optional, self.ps_right_square_after, self.ps_group_before)) ama self.group:
                fail("Function " + self.function.name + " has an unsupported group configuration. (Unexpected state " + str(self.parameter_state) + ".d)")
            ikiwa self.keyword_only:
                fail("Function " + self.function.name + " mixes keyword-only na positional-only parameters, which ni unsupported.")
            # fixup preceding parameters
            kila p kwenye self.function.parameters.values():
                ikiwa (p.kind != inspect.Parameter.POSITIONAL_OR_KEYWORD na sio isinstance(p.converter, self_converter)):
                    fail("Function " + self.function.name + " mixes keyword-only na positional-only parameters, which ni unsupported.")
                p.kind = inspect.Parameter.POSITIONAL_ONLY

    eleza state_parameter_docstring_start(self, line):
        self.parameter_docstring_indent = len(self.indent.margin)
        assert self.indent.depth == 3
        rudisha self.next(self.state_parameter_docstring, line)

    # every line of the docstring must start ukijumuisha at least F spaces,
    # where F > P.
    # these F spaces will be stripped.
    eleza state_parameter_docstring(self, line):
        stripped = line.strip()
        ikiwa stripped.startswith('#'):
            rudisha

        indent = self.indent.measure(line)
        ikiwa indent < self.parameter_docstring_indent:
            self.indent.infer(line)
            assert self.indent.depth < 3
            ikiwa self.indent.depth == 2:
                # back to a parameter
                rudisha self.next(self.state_parameter, line)
            assert self.indent.depth == 1
            rudisha self.next(self.state_function_docstring, line)

        assert self.function.parameters
        last_parameter = next(reversed(list(self.function.parameters.values())))

        new_docstring = last_parameter.docstring

        ikiwa new_docstring:
            new_docstring += '\n'
        ikiwa stripped:
            new_docstring += self.indent.dedent(line)

        last_parameter.docstring = new_docstring

    # the final stanza of the DSL ni the docstring.
    eleza state_function_docstring(self, line):
        ikiwa self.group:
            fail("Function " + self.function.name + " has a ] without a matching [.")

        stripped = line.strip()
        ikiwa stripped.startswith('#'):
            rudisha

        new_docstring = self.function.docstring
        ikiwa new_docstring:
            new_docstring += "\n"
        ikiwa stripped:
            line = self.indent.dedent(line).rstrip()
        isipokua:
            line = ''
        new_docstring += line
        self.function.docstring = new_docstring

    eleza format_docstring(self):
        f = self.function

        new_or_init = f.kind kwenye (METHOD_NEW, METHOD_INIT)
        ikiwa new_or_init na sio f.docstring:
            # don't render a docstring at all, no signature, nothing.
            rudisha f.docstring

        text, add, output = _text_accumulator()
        parameters = f.render_parameters

        ##
        ## docstring first line
        ##

        ikiwa new_or_init:
            # classes get *just* the name of the class
            # sio __new__, sio __init__, na sio module.classname
            assert f.cls
            add(f.cls.name)
        isipokua:
            add(f.name)
        add('(')

        # populate "right_bracket_count" field kila every parameter
        assert parameters, "We should always have a self parameter. " + repr(f)
        assert isinstance(parameters[0].converter, self_converter)
        # self ni always positional-only.
        assert parameters[0].is_positional_only()
        parameters[0].right_bracket_count = 0
        positional_only = Kweli
        kila p kwenye parameters[1:]:
            ikiwa sio p.is_positional_only():
                positional_only = Uongo
            isipokua:
                assert positional_only
            ikiwa positional_only:
                p.right_bracket_count = abs(p.group)
            isipokua:
                # don't put any right brackets around non-positional-only parameters, ever.
                p.right_bracket_count = 0

        right_bracket_count = 0

        eleza fix_right_bracket_count(desired):
            nonlocal right_bracket_count
            s = ''
            wakati right_bracket_count < desired:
                s += '['
                right_bracket_count += 1
            wakati right_bracket_count > desired:
                s += ']'
                right_bracket_count -= 1
            rudisha s

        need_slash = Uongo
        added_slash = Uongo
        need_a_trailing_slash = Uongo

        # we only need a trailing slash:
        #   * ikiwa this ni sio a "docstring_only" signature
        #   * na ikiwa the last *shown* parameter is
        #     positional only
        ikiwa sio f.docstring_only:
            kila p kwenye reversed(parameters):
                ikiwa sio p.converter.show_in_signature:
                    endelea
                ikiwa p.is_positional_only():
                    need_a_trailing_slash = Kweli
                koma


        added_star = Uongo

        first_parameter = Kweli
        last_p = parameters[-1]
        line_length = len(''.join(text))
        indent = " " * line_length
        eleza add_parameter(text):
            nonlocal line_length
            nonlocal first_parameter
            ikiwa first_parameter:
                s = text
                first_parameter = Uongo
            isipokua:
                s = ' ' + text
                ikiwa line_length + len(s) >= 72:
                    add('\n')
                    add(indent)
                    line_length = len(indent)
                    s = text
            line_length += len(s)
            add(s)

        kila p kwenye parameters:
            ikiwa sio p.converter.show_in_signature:
                endelea
            assert p.name

            is_self = isinstance(p.converter, self_converter)
            ikiwa is_self na f.docstring_only:
                # this isn't a real machine-parsable signature,
                # so let's sio print the "self" parameter
                endelea

            ikiwa p.is_positional_only():
                need_slash = sio f.docstring_only
            lasivyo need_slash na sio (added_slash ama p.is_positional_only()):
                added_slash = Kweli
                add_parameter('/,')

            ikiwa p.is_keyword_only() na sio added_star:
                added_star = Kweli
                add_parameter('*,')

            p_add, p_output = text_accumulator()
            p_add(fix_right_bracket_count(p.right_bracket_count))

            ikiwa isinstance(p.converter, self_converter):
                # annotate first parameter kama being a "self".
                #
                # ikiwa inspect.Signature gets this function,
                # na it's already bound, the self parameter
                # will be stripped off.
                #
                # ikiwa it's sio bound, it should be marked
                # kama positional-only.
                #
                # note: we don't print "self" kila __init__,
                # because this isn't actually the signature
                # kila __init__.  (it can't be, __init__ doesn't
                # have a docstring.)  ikiwa this ni an __init__
                # (or __new__), then this signature ni for
                # calling the kundi to construct a new instance.
                p_add('$')

            name = p.converter.signature_name ama p.name
            p_add(name)

            ikiwa p.converter.is_optional():
                p_add('=')
                value = p.converter.py_default
                ikiwa sio value:
                    value = repr(p.converter.default)
                p_add(value)

            ikiwa (p != last_p) ama need_a_trailing_slash:
                p_add(',')

            add_parameter(p_output())

        add(fix_right_bracket_count(0))
        ikiwa need_a_trailing_slash:
            add_parameter('/')
        add(')')

        # PEP 8 says:
        #
        #     The Python standard library will sio use function annotations
        #     kama that would result kwenye a premature commitment to a particular
        #     annotation style. Instead, the annotations are left kila users
        #     to discover na experiment ukijumuisha useful annotation styles.
        #
        # therefore this ni commented out:
        #
        # ikiwa f.return_converter.py_default:
        #     add(' -> ')
        #     add(f.return_converter.py_default)

        ikiwa sio f.docstring_only:
            add("\n" + sig_end_marker + "\n")

        docstring_first_line = output()

        # now fix up the places where the brackets look wrong
        docstring_first_line = docstring_first_line.replace(', ]', ',] ')

        # okay.  now we're officially building the "parameters" section.
        # create substitution text kila {parameters}
        spacer_line = Uongo
        kila p kwenye parameters:
            ikiwa sio p.docstring.strip():
                endelea
            ikiwa spacer_line:
                add('\n')
            isipokua:
                spacer_line = Kweli
            add("  ")
            add(p.name)
            add('\n')
            add(textwrap.indent(rstrip_lines(p.docstring.rstrip()), "    "))
        parameters = output()
        ikiwa parameters:
            parameters += '\n'

        ##
        ## docstring body
        ##

        docstring = f.docstring.rstrip()
        lines = [line.rstrip() kila line kwenye docstring.split('\n')]

        # Enforce the summary line!
        # The first line of a docstring should be a summary of the function.
        # It should fit on one line (80 columns? 79 maybe?) na be a paragraph
        # by itself.
        #
        # Argument Clinic enforces the following rule:
        #  * either the docstring ni empty,
        #  * ama it must have a summary line.
        #
        # Guido said Clinic should enforce this:
        # http://mail.python.org/pipermail/python-dev/2013-June/127110.html

        ikiwa len(lines) >= 2:
            ikiwa lines[1]:
                fail("Docstring kila " + f.full_name + " does sio have a summary line!\n" +
                    "Every non-blank function docstring must start with\n" +
                    "a single line summary followed by an empty line.")
        lasivyo len(lines) == 1:
            # the docstring ni only one line right now--the summary line.
            # add an empty line after the summary line so we have space
            # between it na the {parameters} we're about to add.
            lines.append('')

        parameters_marker_count = len(docstring.split('{parameters}')) - 1
        ikiwa parameters_marker_count > 1:
            fail('You may sio specify {parameters} more than once kwenye a docstring!')

        ikiwa sio parameters_marker_count:
            # insert after summary line
            lines.insert(2, '{parameters}')

        # insert at front of docstring
        lines.insert(0, docstring_first_line)

        docstring = "\n".join(lines)

        add(docstring)
        docstring = output()

        docstring = linear_format(docstring, parameters=parameters)
        docstring = docstring.rstrip()

        rudisha docstring

    eleza state_terminal(self, line):
        """
        Called when processing the block ni done.
        """
        assert sio line

        ikiwa sio self.function:
            rudisha

        ikiwa self.keyword_only:
            values = self.function.parameters.values()
            ikiwa sio values:
                no_parameter_after_star = Kweli
            isipokua:
                last_parameter = next(reversed(list(values)))
                no_parameter_after_star = last_parameter.kind != inspect.Parameter.KEYWORD_ONLY
            ikiwa no_parameter_after_star:
                fail("Function " + self.function.name + " specifies '*' without any parameters afterwards.")

        # remove trailing whitespace kutoka all parameter docstrings
        kila name, value kwenye self.function.parameters.items():
            ikiwa sio value:
                endelea
            value.docstring = value.docstring.rstrip()

        self.function.docstring = self.format_docstring()




# maps strings to callables.
# the callable should rudisha an object
# that implements the clinic parser
# interface (__init__ na parse).
#
# example parsers:
#   "clinic", handles the Clinic DSL
#   "python", handles running Python code
#
parsers = {'clinic' : DSLParser, 'python': PythonParser}


clinic = Tupu


eleza main(argv):
    agiza sys

    ikiwa sys.version_info.major < 3 ama sys.version_info.minor < 3:
        sys.exit("Error: clinic.py requires Python 3.3 ama greater.")

    agiza argparse
    cmdline = argparse.ArgumentParser(
        description="""Preprocessor kila CPython C files.

The purpose of the Argument Clinic ni automating all the boilerplate involved
ukijumuisha writing argument parsing code kila builtins na providing introspection
signatures ("docstrings") kila CPython builtins.

For more information see https://docs.python.org/3/howto/clinic.html""")
    cmdline.add_argument("-f", "--force", action='store_true')
    cmdline.add_argument("-o", "--output", type=str)
    cmdline.add_argument("-v", "--verbose", action='store_true')
    cmdline.add_argument("--converters", action='store_true')
    cmdline.add_argument("--make", action='store_true',
                         help="Walk --srcdir to run over all relevant files.")
    cmdline.add_argument("--srcdir", type=str, default=os.curdir,
                         help="The directory tree to walk kwenye --make mode.")
    cmdline.add_argument("filename", type=str, nargs="*")
    ns = cmdline.parse_args(argv)

    ikiwa ns.converters:
        ikiwa ns.filename:
            andika("Usage error: can't specify --converters na a filename at the same time.")
            andika()
            cmdline.print_usage()
            sys.exit(-1)
        converters = []
        return_converters = []
        ignored = set("""
            add_c_converter
            add_c_return_converter
            add_default_legacy_c_converter
            add_legacy_c_converter
            """.strip().split())
        module = globals()
        kila name kwenye module:
            kila suffix, ids kwenye (
                ("_return_converter", return_converters),
                ("_converter", converters),
            ):
                ikiwa name kwenye ignored:
                    endelea
                ikiwa name.endswith(suffix):
                    ids.append((name, name[:-len(suffix)]))
                    koma
        andika()

        andika("Legacy converters:")
        legacy = sorted(legacy_converters)
        andika('    ' + ' '.join(c kila c kwenye legacy ikiwa c[0].isupper()))
        andika('    ' + ' '.join(c kila c kwenye legacy ikiwa c[0].islower()))
        andika()

        kila title, attribute, ids kwenye (
            ("Converters", 'converter_init', converters),
            ("Return converters", 'return_converter_init', return_converters),
        ):
            andika(title + ":")
            longest = -1
            kila name, short_name kwenye ids:
                longest = max(longest, len(short_name))
            kila name, short_name kwenye sorted(ids, key=lambda x: x[1].lower()):
                cls = module[name]
                callable = getattr(cls, attribute, Tupu)
                ikiwa sio callable:
                    endelea
                signature = inspect.signature(callable)
                parameters = []
                kila parameter_name, parameter kwenye signature.parameters.items():
                    ikiwa parameter.kind == inspect.Parameter.KEYWORD_ONLY:
                        ikiwa parameter.default != inspect.Parameter.empty:
                            s = '{}={!r}'.format(parameter_name, parameter.default)
                        isipokua:
                            s = parameter_name
                        parameters.append(s)
                andika('    {}({})'.format(short_name, ', '.join(parameters)))
            andika()
        andika("All converters also accept (c_default=Tupu, py_default=Tupu, annotation=Tupu).")
        andika("All rudisha converters also accept (py_default=Tupu).")
        sys.exit(0)

    ikiwa ns.make:
        ikiwa ns.output ama ns.filename:
            andika("Usage error: can't use -o ama filenames ukijumuisha --make.")
            andika()
            cmdline.print_usage()
            sys.exit(-1)
        ikiwa sio ns.srcdir:
            andika("Usage error: --srcdir must sio be empty ukijumuisha --make.")
            andika()
            cmdline.print_usage()
            sys.exit(-1)
        kila root, dirs, files kwenye os.walk(ns.srcdir):
            kila rcs_dir kwenye ('.svn', '.git', '.hg', 'build', 'externals'):
                ikiwa rcs_dir kwenye dirs:
                    dirs.remove(rcs_dir)
            kila filename kwenye files:
                ikiwa sio (filename.endswith('.c') ama filename.endswith('.h')):
                    endelea
                path = os.path.join(root, filename)
                ikiwa ns.verbose:
                    andika(path)
                parse_file(path, force=ns.force, verify=not ns.force)
        rudisha

    ikiwa sio ns.filename:
        cmdline.print_usage()
        sys.exit(-1)

    ikiwa ns.output na len(ns.filename) > 1:
        andika("Usage error: can't use -o ukijumuisha multiple filenames.")
        andika()
        cmdline.print_usage()
        sys.exit(-1)

    kila filename kwenye ns.filename:
        ikiwa ns.verbose:
            andika(filename)
        parse_file(filename, output=ns.output, force=ns.force, verify=not ns.force)


ikiwa __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
