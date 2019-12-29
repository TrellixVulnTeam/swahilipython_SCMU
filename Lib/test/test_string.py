agiza unittest
agiza string
kutoka string agiza Template


kundi ModuleTest(unittest.TestCase):

    eleza test_attrs(self):
        # While the exact order of the items kwenye these attributes ni not
        # technically part of the "language spec", kwenye practice there ni almost
        # certainly user code that depends on the order, so de-facto it *is*
        # part of the spec.
        self.assertEqual(string.whitespace, ' \t\n\r\x0b\x0c')
        self.assertEqual(string.ascii_lowercase, 'abcdefghijklmnopqrstuvwxyz')
        self.assertEqual(string.ascii_uppercase, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ')
        self.assertEqual(string.ascii_letters, string.ascii_lowercase + string.ascii_uppercase)
        self.assertEqual(string.digits, '0123456789')
        self.assertEqual(string.hexdigits, string.digits + 'abcdefABCDEF')
        self.assertEqual(string.octdigits, '01234567')
        self.assertEqual(string.punctuation, '!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~')
        self.assertEqual(string.printable, string.digits + string.ascii_lowercase + string.ascii_uppercase + string.punctuation + string.whitespace)

    eleza test_capwords(self):
        self.assertEqual(string.capwords('abc eleza ghi'), 'Abc Def Ghi')
        self.assertEqual(string.capwords('abc\tdef\nghi'), 'Abc Def Ghi')
        self.assertEqual(string.capwords('abc\t   eleza  \nghi'), 'Abc Def Ghi')
        self.assertEqual(string.capwords('ABC DEF GHI'), 'Abc Def Ghi')
        self.assertEqual(string.capwords('ABC-DEF-GHI', '-'), 'Abc-Def-Ghi')
        self.assertEqual(string.capwords('ABC-eleza DEF-ghi GHI'), 'Abc-eleza Def-ghi Ghi')
        self.assertEqual(string.capwords('   aBc  DeF   '), 'Abc Def')
        self.assertEqual(string.capwords('\taBc\tDeF\t'), 'Abc Def')
        self.assertEqual(string.capwords('\taBc\tDeF\t', '\t'), '\tAbc\tDef\t')

    eleza test_basic_formatter(self):
        fmt = string.Formatter()
        self.assertEqual(fmt.format("foo"), "foo")
        self.assertEqual(fmt.format("foo{0}", "bar"), "foobar")
        self.assertEqual(fmt.format("foo{1}{0}-{1}", "bar", 6), "foo6bar-6")
        self.assertRaises(TypeError, fmt.format)
        self.assertRaises(TypeError, string.Formatter.format)

    eleza test_format_keyword_arguments(self):
        fmt = string.Formatter()
        self.assertEqual(fmt.format("-{arg}-", arg='test'), '-test-')
        self.assertRaises(KeyError, fmt.format, "-{arg}-")
        self.assertEqual(fmt.format("-{self}-", self='test'), '-test-')
        self.assertRaises(KeyError, fmt.format, "-{self}-")
        self.assertEqual(fmt.format("-{format_string}-", format_string='test'),
                         '-test-')
        self.assertRaises(KeyError, fmt.format, "-{format_string}-")
        ukijumuisha self.assertRaisesRegex(TypeError, "format_string"):
            fmt.format(format_string="-{arg}-", arg='test')

    eleza test_auto_numbering(self):
        fmt = string.Formatter()
        self.assertEqual(fmt.format('foo{}{}', 'bar', 6),
                         'foo{}{}'.format('bar', 6))
        self.assertEqual(fmt.format('foo{1}{num}{1}', Tupu, 'bar', num=6),
                         'foo{1}{num}{1}'.format(Tupu, 'bar', num=6))
        self.assertEqual(fmt.format('{:^{}}', 'bar', 6),
                         '{:^{}}'.format('bar', 6))
        self.assertEqual(fmt.format('{:^{}} {}', 'bar', 6, 'X'),
                         '{:^{}} {}'.format('bar', 6, 'X'))
        self.assertEqual(fmt.format('{:^{pad}}{}', 'foo', 'bar', pad=6),
                         '{:^{pad}}{}'.format('foo', 'bar', pad=6))

        ukijumuisha self.assertRaises(ValueError):
            fmt.format('foo{1}{}', 'bar', 6)

        ukijumuisha self.assertRaises(ValueError):
            fmt.format('foo{}{1}', 'bar', 6)

    eleza test_conversion_specifiers(self):
        fmt = string.Formatter()
        self.assertEqual(fmt.format("-{arg!r}-", arg='test'), "-'test'-")
        self.assertEqual(fmt.format("{0!s}", 'test'), 'test')
        self.assertRaises(ValueError, fmt.format, "{0!h}", 'test')
        # issue13579
        self.assertEqual(fmt.format("{0!a}", 42), '42')
        self.assertEqual(fmt.format("{0!a}",  string.ascii_letters),
            "'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'")
        self.assertEqual(fmt.format("{0!a}",  chr(255)), "'\\xff'")
        self.assertEqual(fmt.format("{0!a}",  chr(256)), "'\\u0100'")

    eleza test_name_lookup(self):
        fmt = string.Formatter()
        kundi AnyAttr:
            eleza __getattr__(self, attr):
                rudisha attr
        x = AnyAttr()
        self.assertEqual(fmt.format("{0.lumber}{0.jack}", x), 'lumberjack')
        ukijumuisha self.assertRaises(AttributeError):
            fmt.format("{0.lumber}{0.jack}", '')

    eleza test_index_lookup(self):
        fmt = string.Formatter()
        lookup = ["eggs", "and", "spam"]
        self.assertEqual(fmt.format("{0[2]}{0[0]}", lookup), 'spameggs')
        ukijumuisha self.assertRaises(IndexError):
            fmt.format("{0[2]}{0[0]}", [])
        ukijumuisha self.assertRaises(KeyError):
            fmt.format("{0[2]}{0[0]}", {})

    eleza test_override_get_value(self):
        kundi NamespaceFormatter(string.Formatter):
            eleza __init__(self, namespace={}):
                string.Formatter.__init__(self)
                self.namespace = namespace

            eleza get_value(self, key, args, kwds):
                ikiwa isinstance(key, str):
                    jaribu:
                        # Check explicitly pitaed arguments first
                        rudisha kwds[key]
                    tatizo KeyError:
                        rudisha self.namespace[key]
                isipokua:
                    string.Formatter.get_value(key, args, kwds)

        fmt = NamespaceFormatter({'greeting':'hello'})
        self.assertEqual(fmt.format("{greeting}, world!"), 'hello, world!')


    eleza test_override_format_field(self):
        kundi CallFormatter(string.Formatter):
            eleza format_field(self, value, format_spec):
                rudisha format(value(), format_spec)

        fmt = CallFormatter()
        self.assertEqual(fmt.format('*{0}*', lambda : 'result'), '*result*')


    eleza test_override_convert_field(self):
        kundi XFormatter(string.Formatter):
            eleza convert_field(self, value, conversion):
                ikiwa conversion == 'x':
                    rudisha Tupu
                rudisha super().convert_field(value, conversion)

        fmt = XFormatter()
        self.assertEqual(fmt.format("{0!r}:{0!x}", 'foo', 'foo'), "'foo':Tupu")


    eleza test_override_parse(self):
        kundi BarFormatter(string.Formatter):
            # rudishas an iterable that contains tuples of the form:
            # (literal_text, field_name, format_spec, conversion)
            eleza parse(self, format_string):
                kila field kwenye format_string.split('|'):
                    ikiwa field[0] == '+':
                        # it's markup
                        field_name, _, format_spec = field[1:].partition(':')
                        tuma '', field_name, format_spec, Tupu
                    isipokua:
                        tuma field, Tupu, Tupu, Tupu

        fmt = BarFormatter()
        self.assertEqual(fmt.format('*|+0:^10s|*', 'foo'), '*   foo    *')

    eleza test_check_unused_args(self):
        kundi CheckAllUsedFormatter(string.Formatter):
            eleza check_unused_args(self, used_args, args, kwargs):
                # Track which arguments actually got used
                unused_args = set(kwargs.keys())
                unused_args.update(range(0, len(args)))

                kila arg kwenye used_args:
                    unused_args.remove(arg)

                ikiwa unused_args:
                    ashiria ValueError("unused arguments")

        fmt = CheckAllUsedFormatter()
        self.assertEqual(fmt.format("{0}", 10), "10")
        self.assertEqual(fmt.format("{0}{i}", 10, i=100), "10100")
        self.assertEqual(fmt.format("{0}{i}{1}", 10, 20, i=100), "1010020")
        self.assertRaises(ValueError, fmt.format, "{0}{i}{1}", 10, 20, i=100, j=0)
        self.assertRaises(ValueError, fmt.format, "{0}", 10, 20)
        self.assertRaises(ValueError, fmt.format, "{0}", 10, 20, i=100)
        self.assertRaises(ValueError, fmt.format, "{i}", 10, 20, i=100)

    eleza test_vformat_recursion_limit(self):
        fmt = string.Formatter()
        args = ()
        kwargs = dict(i=100)
        ukijumuisha self.assertRaises(ValueError) kama err:
            fmt._vformat("{i}", args, kwargs, set(), -1)
        self.assertIn("recursion", str(err.exception))


# Template tests (formerly housed kwenye test_pep292.py)

kundi Bag:
    pita

kundi Mapping:
    eleza __getitem__(self, name):
        obj = self
        kila part kwenye name.split('.'):
            jaribu:
                obj = getattr(obj, part)
            tatizo AttributeError:
                ashiria KeyError(name)
        rudisha obj


kundi TestTemplate(unittest.TestCase):
    eleza test_regular_templates(self):
        s = Template('$who likes to eat a bag of $what worth $$100')
        self.assertEqual(s.substitute(dict(who='tim', what='ham')),
                         'tim likes to eat a bag of ham worth $100')
        self.assertRaises(KeyError, s.substitute, dict(who='tim'))
        self.assertRaises(TypeError, Template.substitute)

    eleza test_regular_templates_with_braces(self):
        s = Template('$who likes ${what} kila ${meal}')
        d = dict(who='tim', what='ham', meal='dinner')
        self.assertEqual(s.substitute(d), 'tim likes ham kila dinner')
        self.assertRaises(KeyError, s.substitute,
                          dict(who='tim', what='ham'))

    eleza test_regular_templates_with_upper_case(self):
        s = Template('$WHO likes ${WHAT} kila ${MEAL}')
        d = dict(WHO='tim', WHAT='ham', MEAL='dinner')
        self.assertEqual(s.substitute(d), 'tim likes ham kila dinner')

    eleza test_regular_templates_with_non_letters(self):
        s = Template('$_wh0_ likes ${_w_h_a_t_} kila ${mea1}')
        d = dict(_wh0_='tim', _w_h_a_t_='ham', mea1='dinner')
        self.assertEqual(s.substitute(d), 'tim likes ham kila dinner')

    eleza test_escapes(self):
        eq = self.assertEqual
        s = Template('$who likes to eat a bag of $$what worth $$100')
        eq(s.substitute(dict(who='tim', what='ham')),
           'tim likes to eat a bag of $what worth $100')
        s = Template('$who likes $$')
        eq(s.substitute(dict(who='tim', what='ham')), 'tim likes $')

    eleza test_percents(self):
        eq = self.assertEqual
        s = Template('%(foo)s $foo ${foo}')
        d = dict(foo='baz')
        eq(s.substitute(d), '%(foo)s baz baz')
        eq(s.safe_substitute(d), '%(foo)s baz baz')

    eleza test_stringification(self):
        eq = self.assertEqual
        s = Template('tim has eaten $count bags of ham today')
        d = dict(count=7)
        eq(s.substitute(d), 'tim has eaten 7 bags of ham today')
        eq(s.safe_substitute(d), 'tim has eaten 7 bags of ham today')
        s = Template('tim has eaten ${count} bags of ham today')
        eq(s.substitute(d), 'tim has eaten 7 bags of ham today')

    eleza test_tupleargs(self):
        eq = self.assertEqual
        s = Template('$who ate ${meal}')
        d = dict(who=('tim', 'fred'), meal=('ham', 'kung pao'))
        eq(s.substitute(d), "('tim', 'fred') ate ('ham', 'kung pao')")
        eq(s.safe_substitute(d), "('tim', 'fred') ate ('ham', 'kung pao')")

    eleza test_SafeTemplate(self):
        eq = self.assertEqual
        s = Template('$who likes ${what} kila ${meal}')
        eq(s.safe_substitute(dict(who='tim')), 'tim likes ${what} kila ${meal}')
        eq(s.safe_substitute(dict(what='ham')), '$who likes ham kila ${meal}')
        eq(s.safe_substitute(dict(what='ham', meal='dinner')),
           '$who likes ham kila dinner')
        eq(s.safe_substitute(dict(who='tim', what='ham')),
           'tim likes ham kila ${meal}')
        eq(s.safe_substitute(dict(who='tim', what='ham', meal='dinner')),
           'tim likes ham kila dinner')

    eleza test_invalid_placeholders(self):
        ashirias = self.assertRaises
        s = Template('$who likes $')
        ashirias(ValueError, s.substitute, dict(who='tim'))
        s = Template('$who likes ${what)')
        ashirias(ValueError, s.substitute, dict(who='tim'))
        s = Template('$who likes $100')
        ashirias(ValueError, s.substitute, dict(who='tim'))
        # Template.idpattern should match to only ASCII characters.
        # https://bugs.python.org/issue31672
        s = Template("$who likes $\u0131")  # (DOTLESS I)
        ashirias(ValueError, s.substitute, dict(who='tim'))
        s = Template("$who likes $\u0130")  # (LATIN CAPITAL LETTER I WITH DOT ABOVE)
        ashirias(ValueError, s.substitute, dict(who='tim'))

    eleza test_idpattern_override(self):
        kundi PathPattern(Template):
            idpattern = r'[_a-z][._a-z0-9]*'
        m = Mapping()
        m.bag = Bag()
        m.bag.foo = Bag()
        m.bag.foo.who = 'tim'
        m.bag.what = 'ham'
        s = PathPattern('$bag.foo.who likes to eat a bag of $bag.what')
        self.assertEqual(s.substitute(m), 'tim likes to eat a bag of ham')

    eleza test_flags_override(self):
        kundi MyPattern(Template):
            flags = 0
        s = MyPattern('$wHO likes ${WHAT} kila ${meal}')
        d = dict(wHO='tim', WHAT='ham', meal='dinner', w='fred')
        self.assertRaises(ValueError, s.substitute, d)
        self.assertEqual(s.safe_substitute(d), 'fredHO likes ${WHAT} kila dinner')

    eleza test_idpattern_override_inside_outside(self):
        # bpo-1198569: Allow the regexp inside na outside braces to be
        # different when deriving kutoka Template.
        kundi MyPattern(Template):
            idpattern = r'[a-z]+'
            braceidpattern = r'[A-Z]+'
            flags = 0
        m = dict(foo='foo', BAR='BAR')
        s = MyPattern('$foo ${BAR}')
        self.assertEqual(s.substitute(m), 'foo BAR')

    eleza test_idpattern_override_inside_outside_invalid_unbraced(self):
        # bpo-1198569: Allow the regexp inside na outside braces to be
        # different when deriving kutoka Template.
        kundi MyPattern(Template):
            idpattern = r'[a-z]+'
            braceidpattern = r'[A-Z]+'
            flags = 0
        m = dict(foo='foo', BAR='BAR')
        s = MyPattern('$FOO')
        self.assertRaises(ValueError, s.substitute, m)
        s = MyPattern('${bar}')
        self.assertRaises(ValueError, s.substitute, m)

    eleza test_pattern_override(self):
        kundi MyPattern(Template):
            pattern = r"""
            (?P<escaped>@{2})                   |
            @(?P<named>[_a-z][._a-z0-9]*)       |
            @{(?P<braced>[_a-z][._a-z0-9]*)}    |
            (?P<invalid>@)
            """
        m = Mapping()
        m.bag = Bag()
        m.bag.foo = Bag()
        m.bag.foo.who = 'tim'
        m.bag.what = 'ham'
        s = MyPattern('@bag.foo.who likes to eat a bag of @bag.what')
        self.assertEqual(s.substitute(m), 'tim likes to eat a bag of ham')

        kundi BadPattern(Template):
            pattern = r"""
            (?P<badname>.*)                     |
            (?P<escaped>@{2})                   |
            @(?P<named>[_a-z][._a-z0-9]*)       |
            @{(?P<braced>[_a-z][._a-z0-9]*)}    |
            (?P<invalid>@)                      |
            """
        s = BadPattern('@bag.foo.who likes to eat a bag of @bag.what')
        self.assertRaises(ValueError, s.substitute, {})
        self.assertRaises(ValueError, s.safe_substitute, {})

    eleza test_braced_override(self):
        kundi MyTemplate(Template):
            pattern = r"""
            \$(?:
              (?P<escaped>$)                     |
              (?P<named>[_a-z][_a-z0-9]*)        |
              @@(?P<braced>[_a-z][_a-z0-9]*)@@   |
              (?P<invalid>)                      |
           )
           """

        tmpl = 'PyCon kwenye $@@location@@'
        t = MyTemplate(tmpl)
        self.assertRaises(KeyError, t.substitute, {})
        val = t.substitute({'location': 'Cleveland'})
        self.assertEqual(val, 'PyCon kwenye Cleveland')

    eleza test_braced_override_safe(self):
        kundi MyTemplate(Template):
            pattern = r"""
            \$(?:
              (?P<escaped>$)                     |
              (?P<named>[_a-z][_a-z0-9]*)        |
              @@(?P<braced>[_a-z][_a-z0-9]*)@@   |
              (?P<invalid>)                      |
           )
           """

        tmpl = 'PyCon kwenye $@@location@@'
        t = MyTemplate(tmpl)
        self.assertEqual(t.safe_substitute(), tmpl)
        val = t.safe_substitute({'location': 'Cleveland'})
        self.assertEqual(val, 'PyCon kwenye Cleveland')

    eleza test_invalid_with_no_lines(self):
        # The error formatting kila invalid templates
        # has a special case kila no data that the default
        # pattern can't trigger (always has at least '$')
        # So we craft a pattern that ni always invalid
        # ukijumuisha no leading data.
        kundi MyTemplate(Template):
            pattern = r"""
              (?P<invalid>) |
              unreachable(
                (?P<named>)   |
                (?P<braced>)  |
                (?P<escaped>)
              )
            """
        s = MyTemplate('')
        ukijumuisha self.assertRaises(ValueError) kama err:
            s.substitute({})
        self.assertIn('line 1, col 1', str(err.exception))

    eleza test_unicode_values(self):
        s = Template('$who likes $what')
        d = dict(who='t\xffm', what='f\xfe\fed')
        self.assertEqual(s.substitute(d), 't\xffm likes f\xfe\x0ced')

    eleza test_keyword_arguments(self):
        eq = self.assertEqual
        s = Template('$who likes $what')
        eq(s.substitute(who='tim', what='ham'), 'tim likes ham')
        eq(s.substitute(dict(who='tim'), what='ham'), 'tim likes ham')
        eq(s.substitute(dict(who='fred', what='kung pao'),
                        who='tim', what='ham'),
           'tim likes ham')
        s = Template('the mapping ni $mapping')
        eq(s.substitute(dict(foo='none'), mapping='bozo'),
           'the mapping ni bozo')
        eq(s.substitute(dict(mapping='one'), mapping='two'),
           'the mapping ni two')

        s = Template('the self ni $self')
        eq(s.substitute(self='bozo'), 'the self ni bozo')

    eleza test_keyword_arguments_safe(self):
        eq = self.assertEqual
        ashirias = self.assertRaises
        s = Template('$who likes $what')
        eq(s.safe_substitute(who='tim', what='ham'), 'tim likes ham')
        eq(s.safe_substitute(dict(who='tim'), what='ham'), 'tim likes ham')
        eq(s.safe_substitute(dict(who='fred', what='kung pao'),
                        who='tim', what='ham'),
           'tim likes ham')
        s = Template('the mapping ni $mapping')
        eq(s.safe_substitute(dict(foo='none'), mapping='bozo'),
           'the mapping ni bozo')
        eq(s.safe_substitute(dict(mapping='one'), mapping='two'),
           'the mapping ni two')
        d = dict(mapping='one')
        ashirias(TypeError, s.substitute, d, {})
        ashirias(TypeError, s.safe_substitute, d, {})

        s = Template('the self ni $self')
        eq(s.safe_substitute(self='bozo'), 'the self ni bozo')

    eleza test_delimiter_override(self):
        eq = self.assertEqual
        ashirias = self.assertRaises
        kundi AmpersandTemplate(Template):
            delimiter = '&'
        s = AmpersandTemplate('this &gift ni kila &{who} &&')
        eq(s.substitute(gift='bud', who='you'), 'this bud ni kila you &')
        ashirias(KeyError, s.substitute)
        eq(s.safe_substitute(gift='bud', who='you'), 'this bud ni kila you &')
        eq(s.safe_substitute(), 'this &gift ni kila &{who} &')
        s = AmpersandTemplate('this &gift ni kila &{who} &')
        ashirias(ValueError, s.substitute, dict(gift='bud', who='you'))
        eq(s.safe_substitute(), 'this &gift ni kila &{who} &')

        kundi PieDelims(Template):
            delimiter = '@'
        s = PieDelims('@who likes to eat a bag of @{what} worth $100')
        self.assertEqual(s.substitute(dict(who='tim', what='ham')),
                         'tim likes to eat a bag of ham worth $100')


ikiwa __name__ == '__main__':
    unittest.main()
