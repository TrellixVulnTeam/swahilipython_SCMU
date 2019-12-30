# Argument Clinic
# Copyright 2012-2013 by Larry Hastings.
# Licensed to the PSF under a contributor agreement.

kutoka test agiza support
kutoka unittest agiza TestCase
agiza collections
agiza inspect
agiza os.path
agiza sys
agiza unittest


clinic_path = os.path.join(os.path.dirname(__file__), '..', '..', 'Tools', 'clinic')
clinic_path = os.path.normpath(clinic_path)
ikiwa sio os.path.exists(clinic_path):
     ashiria unittest.SkipTest(f'{clinic_path!r} path does sio exist')
sys.path.append(clinic_path)
jaribu:
    agiza clinic
    kutoka clinic agiza DSLParser
mwishowe:
    toa sys.path[-1]


kundi FakeConverter:
    eleza __init__(self, name, args):
        self.name = name
        self.args = args


kundi FakeConverterFactory:
    eleza __init__(self, name):
        self.name = name

    eleza __call__(self, name, default, **kwargs):
        rudisha FakeConverter(self.name, kwargs)


kundi FakeConvertersDict:
    eleza __init__(self):
        self.used_converters = {}

    eleza get(self, name, default):
        rudisha self.used_converters.setdefault(name, FakeConverterFactory(name))

c = clinic.Clinic(language='C', filename = "file")

kundi FakeClinic:
    eleza __init__(self):
        self.converters = FakeConvertersDict()
        self.legacy_converters = FakeConvertersDict()
        self.language = clinic.CLanguage(Tupu)
        self.filename = Tupu
        self.destination_buffers = {}
        self.block_parser = clinic.BlockParser('', self.language)
        self.modules = collections.OrderedDict()
        self.classes = collections.OrderedDict()
        clinic.clinic = self
        self.name = "FakeClinic"
        self.line_prefix = self.line_suffix = ''
        self.destinations = {}
        self.add_destination("block", "buffer")
        self.add_destination("file", "buffer")
        self.add_destination("suppress", "suppress")
        d = self.destinations.get
        self.field_destinations = collections.OrderedDict((
            ('docstring_prototype', d('suppress')),
            ('docstring_definition', d('block')),
            ('methoddef_define', d('block')),
            ('impl_prototype', d('block')),
            ('parser_prototype', d('suppress')),
            ('parser_definition', d('block')),
            ('impl_definition', d('block')),
        ))

    eleza get_destination(self, name):
        d = self.destinations.get(name)
        ikiwa sio d:
            sys.exit("Destination does sio exist: " + repr(name))
        rudisha d

    eleza add_destination(self, name, type, *args):
        ikiwa name kwenye self.destinations:
            sys.exit("Destination already exists: " + repr(name))
        self.destinations[name] = clinic.Destination(name, type, self, *args)

    eleza is_directive(self, name):
        rudisha name == "module"

    eleza directive(self, name, args):
        self.called_directives[name] = args

    _module_and_kundi = clinic.Clinic._module_and_class

kundi ClinicWholeFileTest(TestCase):
    eleza test_eol(self):
        # regression test:
        # clinic's block parser didn't recognize
        # the "end line" kila the block ikiwa it
        # didn't end kwenye "\n" (as in, the last)
        # byte of the file was '/'.
        # so it would spit out an end line kila you.
        # na since you really already had one,
        # the last line of the block got corrupted.
        c = clinic.Clinic(clinic.CLanguage(Tupu), filename="file")
        raw = "/*[clinic]\nfoo\n[clinic]*/"
        cooked = c.parse(raw).splitlines()
        end_line = cooked[2].rstrip()
        # this test ni redundant, it's just here explicitly to catch
        # the regression test so we don't forget what it looked like
        self.assertNotEqual(end_line, "[clinic]*/[clinic]*/")
        self.assertEqual(end_line, "[clinic]*/")



kundi ClinicGroupPermuterTest(TestCase):
    eleza _test(self, l, m, r, output):
        computed = clinic.permute_optional_groups(l, m, r)
        self.assertEqual(output, computed)

    eleza test_range(self):
        self._test([['start']], ['stop'], [['step']],
          (
            ('stop',),
            ('start', 'stop',),
            ('start', 'stop', 'step',),
          ))

    eleza test_add_window(self):
        self._test([['x', 'y']], ['ch'], [['attr']],
          (
            ('ch',),
            ('ch', 'attr'),
            ('x', 'y', 'ch',),
            ('x', 'y', 'ch', 'attr'),
          ))

    eleza test_ludicrous(self):
        self._test([['a1', 'a2', 'a3'], ['b1', 'b2']], ['c1'], [['d1', 'd2'], ['e1', 'e2', 'e3']],
          (
          ('c1',),
          ('b1', 'b2', 'c1'),
          ('b1', 'b2', 'c1', 'd1', 'd2'),
          ('a1', 'a2', 'a3', 'b1', 'b2', 'c1'),
          ('a1', 'a2', 'a3', 'b1', 'b2', 'c1', 'd1', 'd2'),
          ('a1', 'a2', 'a3', 'b1', 'b2', 'c1', 'd1', 'd2', 'e1', 'e2', 'e3'),
          ))

    eleza test_right_only(self):
        self._test([], [], [['a'],['b'],['c']],
          (
          (),
          ('a',),
          ('a', 'b'),
          ('a', 'b', 'c')
          ))

    eleza test_have_left_options_but_required_is_empty(self):
        eleza fn():
            clinic.permute_optional_groups(['a'], [], [])
        self.assertRaises(AssertionError, fn)


kundi ClinicLinearFormatTest(TestCase):
    eleza _test(self, input, output, **kwargs):
        computed = clinic.linear_format(input, **kwargs)
        self.assertEqual(output, computed)

    eleza test_empty_strings(self):
        self._test('', '')

    eleza test_solo_newline(self):
        self._test('\n', '\n')

    eleza test_no_substitution(self):
        self._test("""
          abc
          """, """
          abc
          """)

    eleza test_empty_substitution(self):
        self._test("""
          abc
          {name}
          def
          """, """
          abc
          def
          """, name='')

    eleza test_single_line_substitution(self):
        self._test("""
          abc
          {name}
          def
          """, """
          abc
          GARGLE
          def
          """, name='GARGLE')

    eleza test_multiline_substitution(self):
        self._test("""
          abc
          {name}
          def
          """, """
          abc
          bingle
          bungle

          def
          """, name='bingle\nbungle\n')

kundi InertParser:
    eleza __init__(self, clinic):
        pass

    eleza parse(self, block):
        pass

kundi CopyParser:
    eleza __init__(self, clinic):
        pass

    eleza parse(self, block):
        block.output = block.input


kundi ClinicBlockParserTest(TestCase):
    eleza _test(self, input, output):
        language = clinic.CLanguage(Tupu)

        blocks = list(clinic.BlockParser(input, language))
        writer = clinic.BlockPrinter(language)
        kila block kwenye blocks:
            writer.print_block(block)
        output = writer.f.getvalue()
        assert output == input, "output != input!\n\noutput " + repr(output) + "\n\n input " + repr(input)

    eleza round_trip(self, input):
        rudisha self._test(input, input)

    eleza test_round_trip_1(self):
        self.round_trip("""
    verbatim text here
    lah dee dah
""")
    eleza test_round_trip_2(self):
        self.round_trip("""
    verbatim text here
    lah dee dah
/*[inert]
abc
[inert]*/
def
/*[inert checksum: 7b18d017f89f61cf17d47f92749ea6930a3f1deb]*/
xyz
""")

    eleza _test_clinic(self, input, output):
        language = clinic.CLanguage(Tupu)
        c = clinic.Clinic(language, filename="file")
        c.parsers['inert'] = InertParser(c)
        c.parsers['copy'] = CopyParser(c)
        computed = c.parse(input)
        self.assertEqual(output, computed)

    eleza test_clinic_1(self):
        self._test_clinic("""
    verbatim text here
    lah dee dah
/*[copy input]
def
[copy start generated code]*/
abc
/*[copy end generated code: output=03cfd743661f0797 input=7b18d017f89f61cf]*/
xyz
""", """
    verbatim text here
    lah dee dah
/*[copy input]
def
[copy start generated code]*/
def
/*[copy end generated code: output=7b18d017f89f61cf input=7b18d017f89f61cf]*/
xyz
""")


kundi ClinicParserTest(TestCase):
    eleza test_trivial(self):
        parser = DSLParser(FakeClinic())
        block = clinic.Block("module os\nos.access")
        parser.parse(block)
        module, function = block.signatures
        self.assertEqual("access", function.name)
        self.assertEqual("os", module.name)

    eleza test_ignore_line(self):
        block = self.parse("#\nmodule os\nos.access")
        module, function = block.signatures
        self.assertEqual("access", function.name)
        self.assertEqual("os", module.name)

    eleza test_param(self):
        function = self.parse_function("module os\nos.access\n   path: int")
        self.assertEqual("access", function.name)
        self.assertEqual(2, len(function.parameters))
        p = function.parameters['path']
        self.assertEqual('path', p.name)
        self.assertIsInstance(p.converter, clinic.int_converter)

    eleza test_param_default(self):
        function = self.parse_function("module os\nos.access\n    follow_symlinks: bool = Kweli")
        p = function.parameters['follow_symlinks']
        self.assertEqual(Kweli, p.default)

    eleza test_param_with_continuations(self):
        function = self.parse_function("module os\nos.access\n    follow_symlinks: \\\n   bool \\\n   =\\\n    Kweli")
        p = function.parameters['follow_symlinks']
        self.assertEqual(Kweli, p.default)

    eleza test_param_default_expression(self):
        function = self.parse_function("module os\nos.access\n    follow_symlinks: int(c_default='MAXSIZE') = sys.maxsize")
        p = function.parameters['follow_symlinks']
        self.assertEqual(sys.maxsize, p.default)
        self.assertEqual("MAXSIZE", p.converter.c_default)

        s = self.parse_function_should_fail("module os\nos.access\n    follow_symlinks: int = sys.maxsize")
        self.assertEqual(s, "Error on line 0:\nWhen you specify a named constant ('sys.maxsize') as your default value,\nyou MUST specify a valid c_default.\n")

    eleza test_param_no_docstring(self):
        function = self.parse_function("""
module os
os.access
    follow_symlinks: bool = Kweli
    something_isipokua: str = ''""")
        p = function.parameters['follow_symlinks']
        self.assertEqual(3, len(function.parameters))
        self.assertIsInstance(function.parameters['something_else'].converter, clinic.str_converter)

    eleza test_param_default_parameters_out_of_order(self):
        s = self.parse_function_should_fail("""
module os
os.access
    follow_symlinks: bool = Kweli
    something_isipokua: str""")
        self.assertEqual(s, """Error on line 0:
Can't have a parameter without a default ('something_else')
after a parameter ukijumuisha a default!
""")

    eleza disabled_test_converter_arguments(self):
        function = self.parse_function("module os\nos.access\n    path: path_t(allow_fd=1)")
        p = function.parameters['path']
        self.assertEqual(1, p.converter.args['allow_fd'])

    eleza test_function_docstring(self):
        function = self.parse_function("""
module os
os.stat as os_stat_fn

   path: str
       Path to be examined

Perform a stat system call on the given path.""")
        self.assertEqual("""
stat($module, /, path)
--

Perform a stat system call on the given path.

  path
    Path to be examined
""".strip(), function.docstring)

    eleza test_explicit_parameters_in_docstring(self):
        function = self.parse_function("""
module foo
foo.bar
  x: int
     Documentation kila x.
  y: int

This ni the documentation kila foo.

Okay, we're done here.
""")
        self.assertEqual("""
bar($module, /, x, y)
--

This ni the documentation kila foo.

  x
    Documentation kila x.

Okay, we're done here.
""".strip(), function.docstring)

    eleza test_parser_regression_special_character_in_parameter_column_of_docstring_first_line(self):
        function = self.parse_function("""
module os
os.stat
    path: str
This/used to koma Clinic!
""")
        self.assertEqual("stat($module, /, path)\n--\n\nThis/used to koma Clinic!", function.docstring)

    eleza test_c_name(self):
        function = self.parse_function("module os\nos.stat as os_stat_fn")
        self.assertEqual("os_stat_fn", function.c_basename)

    eleza test_return_converter(self):
        function = self.parse_function("module os\nos.stat -> int")
        self.assertIsInstance(function.return_converter, clinic.int_return_converter)

    eleza test_star(self):
        function = self.parse_function("module os\nos.access\n    *\n    follow_symlinks: bool = Kweli")
        p = function.parameters['follow_symlinks']
        self.assertEqual(inspect.Parameter.KEYWORD_ONLY, p.kind)
        self.assertEqual(0, p.group)

    eleza test_group(self):
        function = self.parse_function("module window\nwindow.border\n [\n ls : int\n ]\n /\n")
        p = function.parameters['ls']
        self.assertEqual(1, p.group)

    eleza test_left_group(self):
        function = self.parse_function("""
module curses
curses.addch
   [
   y: int
     Y-coordinate.
   x: int
     X-coordinate.
   ]
   ch: char
     Character to add.
   [
   attr: long
     Attributes kila the character.
   ]
   /
""")
        kila name, group kwenye (
            ('y', -1), ('x', -1),
            ('ch', 0),
            ('attr', 1),
            ):
            p = function.parameters[name]
            self.assertEqual(p.group, group)
            self.assertEqual(p.kind, inspect.Parameter.POSITIONAL_ONLY)
        self.assertEqual(function.docstring.strip(), """
addch([y, x,] ch, [attr])


  y
    Y-coordinate.
  x
    X-coordinate.
  ch
    Character to add.
  attr
    Attributes kila the character.
            """.strip())

    eleza test_nested_groups(self):
        function = self.parse_function("""
module curses
curses.imaginary
   [
   [
   y1: int
     Y-coordinate.
   y2: int
     Y-coordinate.
   ]
   x1: int
     X-coordinate.
   x2: int
     X-coordinate.
   ]
   ch: char
     Character to add.
   [
   attr1: long
     Attributes kila the character.
   attr2: long
     Attributes kila the character.
   attr3: long
     Attributes kila the character.
   [
   attr4: long
     Attributes kila the character.
   attr5: long
     Attributes kila the character.
   attr6: long
     Attributes kila the character.
   ]
   ]
   /
""")
        kila name, group kwenye (
            ('y1', -2), ('y2', -2),
            ('x1', -1), ('x2', -1),
            ('ch', 0),
            ('attr1', 1), ('attr2', 1), ('attr3', 1),
            ('attr4', 2), ('attr5', 2), ('attr6', 2),
            ):
            p = function.parameters[name]
            self.assertEqual(p.group, group)
            self.assertEqual(p.kind, inspect.Parameter.POSITIONAL_ONLY)

        self.assertEqual(function.docstring.strip(), """
imaginary([[y1, y2,] x1, x2,] ch, [attr1, attr2, attr3, [attr4, attr5,
          attr6]])


  y1
    Y-coordinate.
  y2
    Y-coordinate.
  x1
    X-coordinate.
  x2
    X-coordinate.
  ch
    Character to add.
  attr1
    Attributes kila the character.
  attr2
    Attributes kila the character.
  attr3
    Attributes kila the character.
  attr4
    Attributes kila the character.
  attr5
    Attributes kila the character.
  attr6
    Attributes kila the character.
                """.strip())

    eleza parse_function_should_fail(self, s):
        ukijumuisha support.captured_stdout() as stdout:
            ukijumuisha self.assertRaises(SystemExit):
                self.parse_function(s)
        rudisha stdout.getvalue()

    eleza test_disallowed_grouping__two_top_groups_on_left(self):
        s = self.parse_function_should_fail("""
module foo
foo.two_top_groups_on_left
    [
    group1 : int
    ]
    [
    group2 : int
    ]
    param: int
            """)
        self.assertEqual(s,
            ('Error on line 0:\n'
            'Function two_top_groups_on_left has an unsupported group configuration. (Unexpected state 2.b)\n'))

    eleza test_disallowed_grouping__two_top_groups_on_right(self):
        self.parse_function_should_fail("""
module foo
foo.two_top_groups_on_right
    param: int
    [
    group1 : int
    ]
    [
    group2 : int
    ]
            """)

    eleza test_disallowed_grouping__parameter_after_group_on_right(self):
        self.parse_function_should_fail("""
module foo
foo.parameter_after_group_on_right
    param: int
    [
    [
    group1 : int
    ]
    group2 : int
    ]
            """)

    eleza test_disallowed_grouping__group_after_parameter_on_left(self):
        self.parse_function_should_fail("""
module foo
foo.group_after_parameter_on_left
    [
    group2 : int
    [
    group1 : int
    ]
    ]
    param: int
            """)

    eleza test_disallowed_grouping__empty_group_on_left(self):
        self.parse_function_should_fail("""
module foo
foo.empty_group
    [
    [
    ]
    group2 : int
    ]
    param: int
            """)

    eleza test_disallowed_grouping__empty_group_on_right(self):
        self.parse_function_should_fail("""
module foo
foo.empty_group
    param: int
    [
    [
    ]
    group2 : int
    ]
            """)

    eleza test_no_parameters(self):
        function = self.parse_function("""
module foo
foo.bar

Docstring

""")
        self.assertEqual("bar($module, /)\n--\n\nDocstring", function.docstring)
        self.assertEqual(1, len(function.parameters)) # self!

    eleza test_init_with_no_parameters(self):
        function = self.parse_function("""
module foo
kundi foo.Bar "unused" "notneeded"
foo.Bar.__init__

Docstring

""", signatures_in_block=3, function_index=2)
        # self ni sio kwenye the signature
        self.assertEqual("Bar()\n--\n\nDocstring", function.docstring)
        # but it *is* a parameter
        self.assertEqual(1, len(function.parameters))

    eleza test_illegal_module_line(self):
        self.parse_function_should_fail("""
module foo
foo.bar => int
    /
""")

    eleza test_illegal_c_basename(self):
        self.parse_function_should_fail("""
module foo
foo.bar as 935
    /
""")

    eleza test_single_star(self):
        self.parse_function_should_fail("""
module foo
foo.bar
    *
    *
""")

    eleza test_parameters_required_after_star_without_initial_parameters_or_docstring(self):
        self.parse_function_should_fail("""
module foo
foo.bar
    *
""")

    eleza test_parameters_required_after_star_without_initial_parameters_with_docstring(self):
        self.parse_function_should_fail("""
module foo
foo.bar
    *
Docstring here.
""")

    eleza test_parameters_required_after_star_with_initial_parameters_without_docstring(self):
        self.parse_function_should_fail("""
module foo
foo.bar
    this: int
    *
""")

    eleza test_parameters_required_after_star_with_initial_parameters_and_docstring(self):
        self.parse_function_should_fail("""
module foo
foo.bar
    this: int
    *
Docstring.
""")

    eleza test_single_slash(self):
        self.parse_function_should_fail("""
module foo
foo.bar
    /
    /
""")

    eleza test_mix_star_and_slash(self):
        self.parse_function_should_fail("""
module foo
foo.bar
   x: int
   y: int
   *
   z: int
   /
""")

    eleza test_parameters_not_permitted_after_slash_for_now(self):
        self.parse_function_should_fail("""
module foo
foo.bar
    /
    x: int
""")

    eleza test_function_not_at_column_0(self):
        function = self.parse_function("""
  module foo
  foo.bar
    x: int
      Nested docstring here, goeth.
    *
    y: str
  Not at column 0!
""")
        self.assertEqual("""
bar($module, /, x, *, y)
--

Not at column 0!

  x
    Nested docstring here, goeth.
""".strip(), function.docstring)

    eleza test_directive(self):
        c = FakeClinic()
        parser = DSLParser(c)
        parser.flag = Uongo
        parser.directives['setflag'] = lambda : setattr(parser, 'flag', Kweli)
        block = clinic.Block("setflag")
        parser.parse(block)
        self.assertKweli(parser.flag)

    eleza test_legacy_converters(self):
        block = self.parse('module os\nos.access\n   path: "s"')
        module, function = block.signatures
        self.assertIsInstance((function.parameters['path']).converter, clinic.str_converter)

    eleza parse(self, text):
        c = FakeClinic()
        parser = DSLParser(c)
        block = clinic.Block(text)
        parser.parse(block)
        rudisha block

    eleza parse_function(self, text, signatures_in_block=2, function_index=1):
        block = self.parse(text)
        s = block.signatures
        self.assertEqual(len(s), signatures_in_block)
        assert isinstance(s[0], clinic.Module)
        assert isinstance(s[function_index], clinic.Function)
        rudisha s[function_index]

    eleza test_scaffolding(self):
        # test repr on special values
        self.assertEqual(repr(clinic.unspecified), '<Unspecified>')
        self.assertEqual(repr(clinic.NULL), '<Null>')

        # test that fail fails
        ukijumuisha support.captured_stdout() as stdout:
            ukijumuisha self.assertRaises(SystemExit):
                clinic.fail('The igloos are melting!', filename='clown.txt', line_number=69)
        self.assertEqual(stdout.getvalue(), 'Error kwenye file "clown.txt" on line 69:\nThe igloos are melting!\n')


kundi ClinicExternalTest(TestCase):
    maxDiff = Tupu

    eleza test_external(self):
        source = support.findfile('clinic.test')
        ukijumuisha open(source, 'r', encoding='utf-8') as f:
            original = f.read()
        ukijumuisha support.temp_dir() as testdir:
            testfile = os.path.join(testdir, 'clinic.test.c')
            ukijumuisha open(testfile, 'w', encoding='utf-8') as f:
                f.write(original)
            clinic.parse_file(testfile, force=Kweli)
            ukijumuisha open(testfile, 'r', encoding='utf-8') as f:
                result = f.read()
            self.assertEqual(result, original)


ikiwa __name__ == "__main__":
    unittest.main()
