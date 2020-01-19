agiza collections
agiza configparser
agiza io
agiza os
agiza pathlib
agiza textwrap
agiza unittest
agiza warnings

kutoka test agiza support


kundi SortedDict(collections.UserDict):

    eleza items(self):
        rudisha sorted(self.data.items())

    eleza keys(self):
        rudisha sorted(self.data.keys())

    eleza values(self):
        rudisha [i[1] kila i kwenye self.items()]

    eleza iteritems(self):
        rudisha iter(self.items())

    eleza iterkeys(self):
        rudisha iter(self.keys())

    eleza itervalues(self):
        rudisha iter(self.values())

    __iter__ = iterkeys


kundi CfgParserTestCaseClass:
    allow_no_value = Uongo
    delimiters = ('=', ':')
    comment_prefixes = (';', '#')
    inline_comment_prefixes = (';', '#')
    empty_lines_in_values = Kweli
    dict_type = configparser._default_dict
    strict = Uongo
    default_section = configparser.DEFAULTSECT
    interpolation = configparser._UNSET

    eleza newconfig(self, defaults=Tupu):
        arguments = dict(
            defaults=defaults,
            allow_no_value=self.allow_no_value,
            delimiters=self.delimiters,
            comment_prefixes=self.comment_prefixes,
            inline_comment_prefixes=self.inline_comment_prefixes,
            empty_lines_in_values=self.empty_lines_in_values,
            dict_type=self.dict_type,
            strict=self.strict,
            default_section=self.default_section,
            interpolation=self.interpolation,
        )
        instance = self.config_class(**arguments)
        rudisha instance

    eleza fromstring(self, string, defaults=Tupu):
        cf = self.newconfig(defaults)
        cf.read_string(string)
        rudisha cf


kundi BasicTestCase(CfgParserTestCaseClass):

    eleza basic_test(self, cf):
        E = ['Commented Bar',
             'Foo Bar',
             'Internationalized Stuff',
             'Long Line',
             'Section\\with$weird%characters[\t',
             'Spaces',
             'Spacey Bar',
             'Spacey Bar From The Beginning',
             'Types',
             ]

        ikiwa self.allow_no_value:
            E.append('NoValue')
        E.sort()
        F = [('baz', 'qwe'), ('foo', 'bar3')]

        # API access
        L = cf.sections()
        L.sort()
        eq = self.assertEqual
        eq(L, E)
        L = cf.items('Spacey Bar From The Beginning')
        L.sort()
        eq(L, F)

        # mapping access
        L = [section kila section kwenye cf]
        L.sort()
        E.append(self.default_section)
        E.sort()
        eq(L, E)
        L = cf['Spacey Bar From The Beginning'].items()
        L = sorted(list(L))
        eq(L, F)
        L = cf.items()
        L = sorted(list(L))
        self.assertEqual(len(L), len(E))
        kila name, section kwenye L:
            eq(name, section.name)
        eq(cf.defaults(), cf[self.default_section])

        # The use of spaces kwenye the section names serves kama a
        # regression test kila SourceForge bug #583248:
        # http://www.python.org/sf/583248

        # API access
        eq(cf.get('Foo Bar', 'foo'), 'bar1')
        eq(cf.get('Spacey Bar', 'foo'), 'bar2')
        eq(cf.get('Spacey Bar From The Beginning', 'foo'), 'bar3')
        eq(cf.get('Spacey Bar From The Beginning', 'baz'), 'qwe')
        eq(cf.get('Commented Bar', 'foo'), 'bar4')
        eq(cf.get('Commented Bar', 'baz'), 'qwe')
        eq(cf.get('Spaces', 'key ukijumuisha spaces'), 'value')
        eq(cf.get('Spaces', 'another ukijumuisha spaces'), 'splat!')
        eq(cf.getint('Types', 'int'), 42)
        eq(cf.get('Types', 'int'), "42")
        self.assertAlmostEqual(cf.getfloat('Types', 'float'), 0.44)
        eq(cf.get('Types', 'float'), "0.44")
        eq(cf.getboolean('Types', 'boolean'), Uongo)
        eq(cf.get('Types', '123'), 'strange but acceptable')
        ikiwa self.allow_no_value:
            eq(cf.get('NoValue', 'option-without-value'), Tupu)

        # test vars= na fallback=
        eq(cf.get('Foo Bar', 'foo', fallback='baz'), 'bar1')
        eq(cf.get('Foo Bar', 'foo', vars={'foo': 'baz'}), 'baz')
        ukijumuisha self.assertRaises(configparser.NoSectionError):
            cf.get('No Such Foo Bar', 'foo')
        ukijumuisha self.assertRaises(configparser.NoOptionError):
            cf.get('Foo Bar', 'no-such-foo')
        eq(cf.get('No Such Foo Bar', 'foo', fallback='baz'), 'baz')
        eq(cf.get('Foo Bar', 'no-such-foo', fallback='baz'), 'baz')
        eq(cf.get('Spacey Bar', 'foo', fallback=Tupu), 'bar2')
        eq(cf.get('No Such Spacey Bar', 'foo', fallback=Tupu), Tupu)
        eq(cf.getint('Types', 'int', fallback=18), 42)
        eq(cf.getint('Types', 'no-such-int', fallback=18), 18)
        eq(cf.getint('Types', 'no-such-int', fallback="18"), "18") # sic!
        ukijumuisha self.assertRaises(configparser.NoOptionError):
            cf.getint('Types', 'no-such-int')
        self.assertAlmostEqual(cf.getfloat('Types', 'float',
                                           fallback=0.0), 0.44)
        self.assertAlmostEqual(cf.getfloat('Types', 'no-such-float',
                                           fallback=0.0), 0.0)
        eq(cf.getfloat('Types', 'no-such-float', fallback="0.0"), "0.0") # sic!
        ukijumuisha self.assertRaises(configparser.NoOptionError):
            cf.getfloat('Types', 'no-such-float')
        eq(cf.getboolean('Types', 'boolean', fallback=Kweli), Uongo)
        eq(cf.getboolean('Types', 'no-such-boolean', fallback="yes"),
           "yes") # sic!
        eq(cf.getboolean('Types', 'no-such-boolean', fallback=Kweli), Kweli)
        ukijumuisha self.assertRaises(configparser.NoOptionError):
            cf.getboolean('Types', 'no-such-boolean')
        eq(cf.getboolean('No Such Types', 'boolean', fallback=Kweli), Kweli)
        ikiwa self.allow_no_value:
            eq(cf.get('NoValue', 'option-without-value', fallback=Uongo), Tupu)
            eq(cf.get('NoValue', 'no-such-option-without-value',
                      fallback=Uongo), Uongo)

        # mapping access
        eq(cf['Foo Bar']['foo'], 'bar1')
        eq(cf['Spacey Bar']['foo'], 'bar2')
        section = cf['Spacey Bar From The Beginning']
        eq(section.name, 'Spacey Bar From The Beginning')
        self.assertIs(section.parser, cf)
        ukijumuisha self.assertRaises(AttributeError):
            section.name = 'Name ni read-only'
        ukijumuisha self.assertRaises(AttributeError):
            section.parser = 'Parser ni read-only'
        eq(section['foo'], 'bar3')
        eq(section['baz'], 'qwe')
        eq(cf['Commented Bar']['foo'], 'bar4')
        eq(cf['Commented Bar']['baz'], 'qwe')
        eq(cf['Spaces']['key ukijumuisha spaces'], 'value')
        eq(cf['Spaces']['another ukijumuisha spaces'], 'splat!')
        eq(cf['Long Line']['foo'],
           'this line ni much, much longer than my editor\nlikes it.')
        ikiwa self.allow_no_value:
            eq(cf['NoValue']['option-without-value'], Tupu)
        # test vars= na fallback=
        eq(cf['Foo Bar'].get('foo', 'baz'), 'bar1')
        eq(cf['Foo Bar'].get('foo', fallback='baz'), 'bar1')
        eq(cf['Foo Bar'].get('foo', vars={'foo': 'baz'}), 'baz')
        ukijumuisha self.assertRaises(KeyError):
            cf['No Such Foo Bar']['foo']
        ukijumuisha self.assertRaises(KeyError):
            cf['Foo Bar']['no-such-foo']
        ukijumuisha self.assertRaises(KeyError):
            cf['No Such Foo Bar'].get('foo', fallback='baz')
        eq(cf['Foo Bar'].get('no-such-foo', 'baz'), 'baz')
        eq(cf['Foo Bar'].get('no-such-foo', fallback='baz'), 'baz')
        eq(cf['Foo Bar'].get('no-such-foo'), Tupu)
        eq(cf['Spacey Bar'].get('foo', Tupu), 'bar2')
        eq(cf['Spacey Bar'].get('foo', fallback=Tupu), 'bar2')
        ukijumuisha self.assertRaises(KeyError):
            cf['No Such Spacey Bar'].get('foo', Tupu)
        eq(cf['Types'].getint('int', 18), 42)
        eq(cf['Types'].getint('int', fallback=18), 42)
        eq(cf['Types'].getint('no-such-int', 18), 18)
        eq(cf['Types'].getint('no-such-int', fallback=18), 18)
        eq(cf['Types'].getint('no-such-int', "18"), "18") # sic!
        eq(cf['Types'].getint('no-such-int', fallback="18"), "18") # sic!
        eq(cf['Types'].getint('no-such-int'), Tupu)
        self.assertAlmostEqual(cf['Types'].getfloat('float', 0.0), 0.44)
        self.assertAlmostEqual(cf['Types'].getfloat('float',
                                                    fallback=0.0), 0.44)
        self.assertAlmostEqual(cf['Types'].getfloat('no-such-float', 0.0), 0.0)
        self.assertAlmostEqual(cf['Types'].getfloat('no-such-float',
                                                    fallback=0.0), 0.0)
        eq(cf['Types'].getfloat('no-such-float', "0.0"), "0.0") # sic!
        eq(cf['Types'].getfloat('no-such-float', fallback="0.0"), "0.0") # sic!
        eq(cf['Types'].getfloat('no-such-float'), Tupu)
        eq(cf['Types'].getboolean('boolean', Kweli), Uongo)
        eq(cf['Types'].getboolean('boolean', fallback=Kweli), Uongo)
        eq(cf['Types'].getboolean('no-such-boolean', "yes"), "yes") # sic!
        eq(cf['Types'].getboolean('no-such-boolean', fallback="yes"),
           "yes") # sic!
        eq(cf['Types'].getboolean('no-such-boolean', Kweli), Kweli)
        eq(cf['Types'].getboolean('no-such-boolean', fallback=Kweli), Kweli)
        eq(cf['Types'].getboolean('no-such-boolean'), Tupu)
        ikiwa self.allow_no_value:
            eq(cf['NoValue'].get('option-without-value', Uongo), Tupu)
            eq(cf['NoValue'].get('option-without-value', fallback=Uongo), Tupu)
            eq(cf['NoValue'].get('no-such-option-without-value', Uongo), Uongo)
            eq(cf['NoValue'].get('no-such-option-without-value',
                      fallback=Uongo), Uongo)

        # Make sure the right things happen kila remove_section() na
        # remove_option(); added to include check kila SourceForge bug #123324.

        cf[self.default_section]['this_value'] = '1'
        cf[self.default_section]['that_value'] = '2'

        # API access
        self.assertKweli(cf.remove_section('Spaces'))
        self.assertUongo(cf.has_option('Spaces', 'key ukijumuisha spaces'))
        self.assertUongo(cf.remove_section('Spaces'))
        self.assertUongo(cf.remove_section(self.default_section))
        self.assertKweli(cf.remove_option('Foo Bar', 'foo'),
                        "remove_option() failed to report existence of option")
        self.assertUongo(cf.has_option('Foo Bar', 'foo'),
                    "remove_option() failed to remove option")
        self.assertUongo(cf.remove_option('Foo Bar', 'foo'),
                    "remove_option() failed to report non-existence of option"
                    " that was removed")
        self.assertKweli(cf.has_option('Foo Bar', 'this_value'))
        self.assertUongo(cf.remove_option('Foo Bar', 'this_value'))
        self.assertKweli(cf.remove_option(self.default_section, 'this_value'))
        self.assertUongo(cf.has_option('Foo Bar', 'this_value'))
        self.assertUongo(cf.remove_option(self.default_section, 'this_value'))

        ukijumuisha self.assertRaises(configparser.NoSectionError) kama cm:
            cf.remove_option('No Such Section', 'foo')
        self.assertEqual(cm.exception.args, ('No Such Section',))

        eq(cf.get('Long Line', 'foo'),
           'this line ni much, much longer than my editor\nlikes it.')

        # mapping access
        toa cf['Types']
        self.assertUongo('Types' kwenye cf)
        ukijumuisha self.assertRaises(KeyError):
            toa cf['Types']
        ukijumuisha self.assertRaises(ValueError):
            toa cf[self.default_section]
        toa cf['Spacey Bar']['foo']
        self.assertUongo('foo' kwenye cf['Spacey Bar'])
        ukijumuisha self.assertRaises(KeyError):
            toa cf['Spacey Bar']['foo']
        self.assertKweli('that_value' kwenye cf['Spacey Bar'])
        ukijumuisha self.assertRaises(KeyError):
            toa cf['Spacey Bar']['that_value']
        toa cf[self.default_section]['that_value']
        self.assertUongo('that_value' kwenye cf['Spacey Bar'])
        ukijumuisha self.assertRaises(KeyError):
            toa cf[self.default_section]['that_value']
        ukijumuisha self.assertRaises(KeyError):
            toa cf['No Such Section']['foo']

        # Don't add new asserts below kwenye this method kama most of the options
        # na sections are now removed.

    eleza test_basic(self):
        config_string = """\
[Foo Bar]
foo{0[0]}bar1
[Spacey Bar]
foo {0[0]} bar2
[Spacey Bar From The Beginning]
  foo {0[0]} bar3
  baz {0[0]} qwe
[Commented Bar]
foo{0[1]} bar4 {1[1]} comment
baz{0[0]}qwe {1[0]}another one
[Long Line]
foo{0[1]} this line ni much, much longer than my editor
   likes it.
[Section\\with$weird%characters[\t]
[Internationalized Stuff]
foo[bg]{0[1]} Bulgarian
foo{0[0]}Default
foo[en]{0[0]}English
foo[de]{0[0]}Deutsch
[Spaces]
key ukijumuisha spaces {0[1]} value
another ukijumuisha spaces {0[0]} splat!
[Types]
int {0[1]} 42
float {0[0]} 0.44
boolean {0[0]} NO
123 {0[1]} strange but acceptable
""".format(self.delimiters, self.comment_prefixes)
        ikiwa self.allow_no_value:
            config_string += (
                "[NoValue]\n"
                "option-without-value\n"
                )
        cf = self.fromstring(config_string)
        self.basic_test(cf)
        ikiwa self.strict:
            ukijumuisha self.assertRaises(configparser.DuplicateOptionError):
                cf.read_string(textwrap.dedent("""\
                    [Duplicate Options Here]
                    option {0[0]} ukijumuisha a value
                    option {0[1]} ukijumuisha another value
                """.format(self.delimiters)))
            ukijumuisha self.assertRaises(configparser.DuplicateSectionError):
                cf.read_string(textwrap.dedent("""\
                    [And Now For Something]
                    completely different {0[0]} Kweli
                    [And Now For Something]
                    the larch {0[1]} 1
                """.format(self.delimiters)))
        isipokua:
            cf.read_string(textwrap.dedent("""\
                [Duplicate Options Here]
                option {0[0]} ukijumuisha a value
                option {0[1]} ukijumuisha another value
            """.format(self.delimiters)))

            cf.read_string(textwrap.dedent("""\
                [And Now For Something]
                completely different {0[0]} Kweli
                [And Now For Something]
                the larch {0[1]} 1
            """.format(self.delimiters)))

    eleza test_basic_from_dict(self):
        config = {
            "Foo Bar": {
                "foo": "bar1",
            },
            "Spacey Bar": {
                "foo": "bar2",
            },
            "Spacey Bar From The Beginning": {
                "foo": "bar3",
                "baz": "qwe",
            },
            "Commented Bar": {
                "foo": "bar4",
                "baz": "qwe",
            },
            "Long Line": {
                "foo": "this line ni much, much longer than my editor\nlikes "
                       "it.",
            },
            "Section\\with$weird%characters[\t": {
            },
            "Internationalized Stuff": {
                "foo[bg]": "Bulgarian",
                "foo": "Default",
                "foo[en]": "English",
                "foo[de]": "Deutsch",
            },
            "Spaces": {
                "key ukijumuisha spaces": "value",
                "another ukijumuisha spaces": "splat!",
            },
            "Types": {
                "int": 42,
                "float": 0.44,
                "boolean": Uongo,
                123: "strange but acceptable",
            },
        }
        ikiwa self.allow_no_value:
            config.update({
                "NoValue": {
                    "option-without-value": Tupu,
                }
            })
        cf = self.newconfig()
        cf.read_dict(config)
        self.basic_test(cf)
        ikiwa self.strict:
            ukijumuisha self.assertRaises(configparser.DuplicateSectionError):
                cf.read_dict({
                    '1': {'key': 'value'},
                    1: {'key2': 'value2'},
                })
            ukijumuisha self.assertRaises(configparser.DuplicateOptionError):
                cf.read_dict({
                    "Duplicate Options Here": {
                        'option': 'ukijumuisha a value',
                        'OPTION': 'ukijumuisha another value',
                    },
                })
        isipokua:
            cf.read_dict({
                'section': {'key': 'value'},
                'SECTION': {'key2': 'value2'},
            })
            cf.read_dict({
                "Duplicate Options Here": {
                    'option': 'ukijumuisha a value',
                    'OPTION': 'ukijumuisha another value',
                },
            })

    eleza test_case_sensitivity(self):
        cf = self.newconfig()
        cf.add_section("A")
        cf.add_section("a")
        cf.add_section("B")
        L = cf.sections()
        L.sort()
        eq = self.assertEqual
        eq(L, ["A", "B", "a"])
        cf.set("a", "B", "value")
        eq(cf.options("a"), ["b"])
        eq(cf.get("a", "b"), "value",
           "could sio locate option, expecting case-insensitive option names")
        ukijumuisha self.assertRaises(configparser.NoSectionError):
            # section names are case-sensitive
            cf.set("b", "A", "value")
        self.assertKweli(cf.has_option("a", "b"))
        self.assertUongo(cf.has_option("b", "b"))
        cf.set("A", "A-B", "A-B value")
        kila opt kwenye ("a-b", "A-b", "a-B", "A-B"):
            self.assertKweli(
                cf.has_option("A", opt),
                "has_option() returned false kila option which should exist")
        eq(cf.options("A"), ["a-b"])
        eq(cf.options("a"), ["b"])
        cf.remove_option("a", "B")
        eq(cf.options("a"), [])

        # SF bug #432369:
        cf = self.fromstring(
            "[MySection]\nOption{} first line   \n\tsecond line   \n".format(
                self.delimiters[0]))
        eq(cf.options("MySection"), ["option"])
        eq(cf.get("MySection", "Option"), "first line\nsecond line")

        # SF bug #561822:
        cf = self.fromstring("[section]\n"
                             "nekey{}nevalue\n".format(self.delimiters[0]),
                             defaults={"key":"value"})
        self.assertKweli(cf.has_option("section", "Key"))


    eleza test_case_sensitivity_mapping_access(self):
        cf = self.newconfig()
        cf["A"] = {}
        cf["a"] = {"B": "value"}
        cf["B"] = {}
        L = [section kila section kwenye cf]
        L.sort()
        eq = self.assertEqual
        elem_eq = self.assertCountEqual
        eq(L, sorted(["A", "B", self.default_section, "a"]))
        eq(cf["a"].keys(), {"b"})
        eq(cf["a"]["b"], "value",
           "could sio locate option, expecting case-insensitive option names")
        ukijumuisha self.assertRaises(KeyError):
            # section names are case-sensitive
            cf["b"]["A"] = "value"
        self.assertKweli("b" kwenye cf["a"])
        cf["A"]["A-B"] = "A-B value"
        kila opt kwenye ("a-b", "A-b", "a-B", "A-B"):
            self.assertKweli(
                opt kwenye cf["A"],
                "has_option() returned false kila option which should exist")
        eq(cf["A"].keys(), {"a-b"})
        eq(cf["a"].keys(), {"b"})
        toa cf["a"]["B"]
        elem_eq(cf["a"].keys(), {})

        # SF bug #432369:
        cf = self.fromstring(
            "[MySection]\nOption{} first line   \n\tsecond line   \n".format(
                self.delimiters[0]))
        eq(cf["MySection"].keys(), {"option"})
        eq(cf["MySection"]["Option"], "first line\nsecond line")

        # SF bug #561822:
        cf = self.fromstring("[section]\n"
                             "nekey{}nevalue\n".format(self.delimiters[0]),
                             defaults={"key":"value"})
        self.assertKweli("Key" kwenye cf["section"])

    eleza test_default_case_sensitivity(self):
        cf = self.newconfig({"foo": "Bar"})
        self.assertEqual(
            cf.get(self.default_section, "Foo"), "Bar",
            "could sio locate option, expecting case-insensitive option names")
        cf = self.newconfig({"Foo": "Bar"})
        self.assertEqual(
            cf.get(self.default_section, "Foo"), "Bar",
            "could sio locate option, expecting case-insensitive defaults")

    eleza test_parse_errors(self):
        cf = self.newconfig()
        self.parse_error(cf, configparser.ParsingError,
                         "[Foo]\n"
                         "{}val-without-opt-name\n".format(self.delimiters[0]))
        self.parse_error(cf, configparser.ParsingError,
                         "[Foo]\n"
                         "{}val-without-opt-name\n".format(self.delimiters[1]))
        e = self.parse_error(cf, configparser.MissingSectionHeaderError,
                             "No Section!\n")
        self.assertEqual(e.args, ('<???>', 1, "No Section!\n"))
        ikiwa sio self.allow_no_value:
            e = self.parse_error(cf, configparser.ParsingError,
                                "[Foo]\n  wrong-indent\n")
            self.assertEqual(e.args, ('<???>',))
            # read_file on a real file
            tricky = support.findfile("cfgparser.3")
            ikiwa self.delimiters[0] == '=':
                error = configparser.ParsingError
                expected = (tricky,)
            isipokua:
                error = configparser.MissingSectionHeaderError
                expected = (tricky, 1,
                            '  # INI ukijumuisha kama many tricky parts kama possible\n')
            ukijumuisha open(tricky, encoding='utf-8') kama f:
                e = self.parse_error(cf, error, f)
            self.assertEqual(e.args, expected)

    eleza parse_error(self, cf, exc, src):
        ikiwa hasattr(src, 'readline'):
            sio = src
        isipokua:
            sio = io.StringIO(src)
        ukijumuisha self.assertRaises(exc) kama cm:
            cf.read_file(sio)
        rudisha cm.exception

    eleza test_query_errors(self):
        cf = self.newconfig()
        self.assertEqual(cf.sections(), [],
                         "new ConfigParser should have no defined sections")
        self.assertUongo(cf.has_section("Foo"),
                         "new ConfigParser should have no acknowledged "
                         "sections")
        ukijumuisha self.assertRaises(configparser.NoSectionError):
            cf.options("Foo")
        ukijumuisha self.assertRaises(configparser.NoSectionError):
            cf.set("foo", "bar", "value")
        e = self.get_error(cf, configparser.NoSectionError, "foo", "bar")
        self.assertEqual(e.args, ("foo",))
        cf.add_section("foo")
        e = self.get_error(cf, configparser.NoOptionError, "foo", "bar")
        self.assertEqual(e.args, ("bar", "foo"))

    eleza get_error(self, cf, exc, section, option):
        jaribu:
            cf.get(section, option)
        tatizo exc kama e:
            rudisha e
        isipokua:
            self.fail("expected exception type %s.%s"
                      % (exc.__module__, exc.__qualname__))

    eleza test_boolean(self):
        cf = self.fromstring(
            "[BOOLTEST]\n"
            "T1{equals}1\n"
            "T2{equals}TRUE\n"
            "T3{equals}Kweli\n"
            "T4{equals}oN\n"
            "T5{equals}yes\n"
            "F1{equals}0\n"
            "F2{equals}FALSE\n"
            "F3{equals}Uongo\n"
            "F4{equals}oFF\n"
            "F5{equals}nO\n"
            "E1{equals}2\n"
            "E2{equals}foo\n"
            "E3{equals}-1\n"
            "E4{equals}0.1\n"
            "E5{equals}FALSE AND MORE".format(equals=self.delimiters[0])
            )
        kila x kwenye range(1, 5):
            self.assertKweli(cf.getboolean('BOOLTEST', 't%d' % x))
            self.assertUongo(cf.getboolean('BOOLTEST', 'f%d' % x))
            self.assertRaises(ValueError,
                              cf.getboolean, 'BOOLTEST', 'e%d' % x)

    eleza test_weird_errors(self):
        cf = self.newconfig()
        cf.add_section("Foo")
        ukijumuisha self.assertRaises(configparser.DuplicateSectionError) kama cm:
            cf.add_section("Foo")
        e = cm.exception
        self.assertEqual(str(e), "Section 'Foo' already exists")
        self.assertEqual(e.args, ("Foo", Tupu, Tupu))

        ikiwa self.strict:
            ukijumuisha self.assertRaises(configparser.DuplicateSectionError) kama cm:
                cf.read_string(textwrap.dedent("""\
                    [Foo]
                    will this be added{equals}Kweli
                    [Bar]
                    what about this{equals}Kweli
                    [Foo]
                    oops{equals}this won't
                """.format(equals=self.delimiters[0])), source='<foo-bar>')
            e = cm.exception
            self.assertEqual(str(e), "While reading kutoka '<foo-bar>' "
                                     "[line  5]: section 'Foo' already exists")
            self.assertEqual(e.args, ("Foo", '<foo-bar>', 5))

            ukijumuisha self.assertRaises(configparser.DuplicateOptionError) kama cm:
                cf.read_dict({'Bar': {'opt': 'val', 'OPT': 'is really `opt`'}})
            e = cm.exception
            self.assertEqual(str(e), "While reading kutoka '<dict>': option "
                                     "'opt' kwenye section 'Bar' already exists")
            self.assertEqual(e.args, ("Bar", "opt", "<dict>", Tupu))

    eleza test_write(self):
        config_string = (
            "[Long Line]\n"
            "foo{0[0]} this line ni much, much longer than my editor\n"
            "   likes it.\n"
            "[{default_section}]\n"
            "foo{0[1]} another very\n"
            " long line\n"
            "[Long Line - With Comments!]\n"
            "test {0[1]} we        {comment} can\n"
            "            also      {comment} place\n"
            "            comments  {comment} in\n"
            "            multiline {comment} values"
            "\n".format(self.delimiters, comment=self.comment_prefixes[0],
                        default_section=self.default_section)
            )
        ikiwa self.allow_no_value:
            config_string += (
            "[Valueless]\n"
            "option-without-value\n"
            )

        cf = self.fromstring(config_string)
        kila space_around_delimiters kwenye (Kweli, Uongo):
            output = io.StringIO()
            cf.write(output, space_around_delimiters=space_around_delimiters)
            delimiter = self.delimiters[0]
            ikiwa space_around_delimiters:
                delimiter = " {} ".format(delimiter)
            expect_string = (
                "[{default_section}]\n"
                "foo{equals}another very\n"
                "\tlong line\n"
                "\n"
                "[Long Line]\n"
                "foo{equals}this line ni much, much longer than my editor\n"
                "\tlikes it.\n"
                "\n"
                "[Long Line - With Comments!]\n"
                "test{equals}we\n"
                "\talso\n"
                "\tcomments\n"
                "\tmultiline\n"
                "\n".format(equals=delimiter,
                            default_section=self.default_section)
                )
            ikiwa self.allow_no_value:
                expect_string += (
                    "[Valueless]\n"
                    "option-without-value\n"
                    "\n"
                    )
            self.assertEqual(output.getvalue(), expect_string)

    eleza test_set_string_types(self):
        cf = self.fromstring("[sect]\n"
                             "option1{eq}foo\n".format(eq=self.delimiters[0]))
        # Check that we don't get an exception when setting values kwenye
        # an existing section using strings:
        kundi mystr(str):
            pita
        cf.set("sect", "option1", "splat")
        cf.set("sect", "option1", mystr("splat"))
        cf.set("sect", "option2", "splat")
        cf.set("sect", "option2", mystr("splat"))
        cf.set("sect", "option1", "splat")
        cf.set("sect", "option2", "splat")

    eleza test_read_returns_file_list(self):
        ikiwa self.delimiters[0] != '=':
            self.skipTest('incompatible format')
        file1 = support.findfile("cfgparser.1")
        # check when we pita a mix of readable na non-readable files:
        cf = self.newconfig()
        parsed_files = cf.read([file1, "nonexistent-file"])
        self.assertEqual(parsed_files, [file1])
        self.assertEqual(cf.get("Foo Bar", "foo"), "newbar")
        # check when we pita only a filename:
        cf = self.newconfig()
        parsed_files = cf.read(file1)
        self.assertEqual(parsed_files, [file1])
        self.assertEqual(cf.get("Foo Bar", "foo"), "newbar")
        # check when we pita only a Path object:
        cf = self.newconfig()
        parsed_files = cf.read(pathlib.Path(file1))
        self.assertEqual(parsed_files, [file1])
        self.assertEqual(cf.get("Foo Bar", "foo"), "newbar")
        # check when we pitaed both a filename na a Path object:
        cf = self.newconfig()
        parsed_files = cf.read([pathlib.Path(file1), file1])
        self.assertEqual(parsed_files, [file1, file1])
        self.assertEqual(cf.get("Foo Bar", "foo"), "newbar")
        # check when we pita only missing files:
        cf = self.newconfig()
        parsed_files = cf.read(["nonexistent-file"])
        self.assertEqual(parsed_files, [])
        # check when we pita no files:
        cf = self.newconfig()
        parsed_files = cf.read([])
        self.assertEqual(parsed_files, [])

    eleza test_read_returns_file_list_with_bytestring_path(self):
        ikiwa self.delimiters[0] != '=':
            self.skipTest('incompatible format')
        file1_bytestring = support.findfile("cfgparser.1").encode()
        # check when pitaing an existing bytestring path
        cf = self.newconfig()
        parsed_files = cf.read(file1_bytestring)
        self.assertEqual(parsed_files, [file1_bytestring])
        # check when pitaing an non-existing bytestring path
        cf = self.newconfig()
        parsed_files = cf.read(b'nonexistent-file')
        self.assertEqual(parsed_files, [])
        # check when pitaing both an existing na non-existing bytestring path
        cf = self.newconfig()
        parsed_files = cf.read([file1_bytestring, b'nonexistent-file'])
        self.assertEqual(parsed_files, [file1_bytestring])

    # shared by subclasses
    eleza get_interpolation_config(self):
        rudisha self.fromstring(
            "[Foo]\n"
            "bar{equals}something %(with1)s interpolation (1 step)\n"
            "bar9{equals}something %(with9)s lots of interpolation (9 steps)\n"
            "bar10{equals}something %(with10)s lots of interpolation (10 steps)\n"
            "bar11{equals}something %(with11)s lots of interpolation (11 steps)\n"
            "with11{equals}%(with10)s\n"
            "with10{equals}%(with9)s\n"
            "with9{equals}%(with8)s\n"
            "with8{equals}%(With7)s\n"
            "with7{equals}%(WITH6)s\n"
            "with6{equals}%(with5)s\n"
            "With5{equals}%(with4)s\n"
            "WITH4{equals}%(with3)s\n"
            "with3{equals}%(with2)s\n"
            "with2{equals}%(with1)s\n"
            "with1{equals}with\n"
            "\n"
            "[Mutual Recursion]\n"
            "foo{equals}%(bar)s\n"
            "bar{equals}%(foo)s\n"
            "\n"
            "[Interpolation Error]\n"
            # no definition kila 'reference'
            "name{equals}%(reference)s\n".format(equals=self.delimiters[0]))

    eleza check_items_config(self, expected):
        cf = self.fromstring("""
            [section]
            name {0[0]} %(value)s
            key{0[1]} |%(name)s|
            getdefault{0[1]} |%(default)s|
        """.format(self.delimiters), defaults={"default": "<default>"})
        L = list(cf.items("section", vars={'value': 'value'}))
        L.sort()
        self.assertEqual(L, expected)
        ukijumuisha self.assertRaises(configparser.NoSectionError):
            cf.items("no such section")

    eleza test_popitem(self):
        cf = self.fromstring("""
            [section1]
            name1 {0[0]} value1
            [section2]
            name2 {0[0]} value2
            [section3]
            name3 {0[0]} value3
        """.format(self.delimiters), defaults={"default": "<default>"})
        self.assertEqual(cf.popitem()[0], 'section1')
        self.assertEqual(cf.popitem()[0], 'section2')
        self.assertEqual(cf.popitem()[0], 'section3')
        ukijumuisha self.assertRaises(KeyError):
            cf.popitem()

    eleza test_clear(self):
        cf = self.newconfig({"foo": "Bar"})
        self.assertEqual(
            cf.get(self.default_section, "Foo"), "Bar",
            "could sio locate option, expecting case-insensitive option names")
        cf['zing'] = {'option1': 'value1', 'option2': 'value2'}
        self.assertEqual(cf.sections(), ['zing'])
        self.assertEqual(set(cf['zing'].keys()), {'option1', 'option2', 'foo'})
        cf.clear()
        self.assertEqual(set(cf.sections()), set())
        self.assertEqual(set(cf[self.default_section].keys()), {'foo'})

    eleza test_setitem(self):
        cf = self.fromstring("""
            [section1]
            name1 {0[0]} value1
            [section2]
            name2 {0[0]} value2
            [section3]
            name3 {0[0]} value3
        """.format(self.delimiters), defaults={"nameD": "valueD"})
        self.assertEqual(set(cf['section1'].keys()), {'name1', 'named'})
        self.assertEqual(set(cf['section2'].keys()), {'name2', 'named'})
        self.assertEqual(set(cf['section3'].keys()), {'name3', 'named'})
        self.assertEqual(cf['section1']['name1'], 'value1')
        self.assertEqual(cf['section2']['name2'], 'value2')
        self.assertEqual(cf['section3']['name3'], 'value3')
        self.assertEqual(cf.sections(), ['section1', 'section2', 'section3'])
        cf['section2'] = {'name22': 'value22'}
        self.assertEqual(set(cf['section2'].keys()), {'name22', 'named'})
        self.assertEqual(cf['section2']['name22'], 'value22')
        self.assertNotIn('name2', cf['section2'])
        self.assertEqual(cf.sections(), ['section1', 'section2', 'section3'])
        cf['section3'] = {}
        self.assertEqual(set(cf['section3'].keys()), {'named'})
        self.assertNotIn('name3', cf['section3'])
        self.assertEqual(cf.sections(), ['section1', 'section2', 'section3'])
        # For bpo-32108, assigning default_section to itself.
        cf[self.default_section] = cf[self.default_section]
        self.assertNotEqual(set(cf[self.default_section].keys()), set())
        cf[self.default_section] = {}
        self.assertEqual(set(cf[self.default_section].keys()), set())
        self.assertEqual(set(cf['section1'].keys()), {'name1'})
        self.assertEqual(set(cf['section2'].keys()), {'name22'})
        self.assertEqual(set(cf['section3'].keys()), set())
        self.assertEqual(cf.sections(), ['section1', 'section2', 'section3'])
        # For bpo-32108, assigning section to itself.
        cf['section2'] = cf['section2']
        self.assertEqual(set(cf['section2'].keys()), {'name22'})

    eleza test_invalid_multiline_value(self):
        ikiwa self.allow_no_value:
            self.skipTest('ikiwa no_value ni allowed, ParsingError ni sio raised')

        invalid = textwrap.dedent("""\
            [DEFAULT]
            test {0} test
            invalid""".format(self.delimiters[0])
        )
        cf = self.newconfig()
        ukijumuisha self.assertRaises(configparser.ParsingError):
            cf.read_string(invalid)
        self.assertEqual(cf.get('DEFAULT', 'test'), 'test')
        self.assertEqual(cf['DEFAULT']['test'], 'test')


kundi StrictTestCase(BasicTestCase, unittest.TestCase):
    config_class = configparser.RawConfigParser
    strict = Kweli


kundi ConfigParserTestCase(BasicTestCase, unittest.TestCase):
    config_class = configparser.ConfigParser

    eleza test_interpolation(self):
        cf = self.get_interpolation_config()
        eq = self.assertEqual
        eq(cf.get("Foo", "bar"), "something ukijumuisha interpolation (1 step)")
        eq(cf.get("Foo", "bar9"),
           "something ukijumuisha lots of interpolation (9 steps)")
        eq(cf.get("Foo", "bar10"),
           "something ukijumuisha lots of interpolation (10 steps)")
        e = self.get_error(cf, configparser.InterpolationDepthError, "Foo", "bar11")
        ikiwa self.interpolation == configparser._UNSET:
            self.assertEqual(e.args, ("bar11", "Foo",
                "something %(with11)s lots of interpolation (11 steps)"))
        lasivyo isinstance(self.interpolation, configparser.LegacyInterpolation):
            self.assertEqual(e.args, ("bar11", "Foo",
                "something %(with11)s lots of interpolation (11 steps)"))

    eleza test_interpolation_missing_value(self):
        cf = self.get_interpolation_config()
        e = self.get_error(cf, configparser.InterpolationMissingOptionError,
                           "Interpolation Error", "name")
        self.assertEqual(e.reference, "reference")
        self.assertEqual(e.section, "Interpolation Error")
        self.assertEqual(e.option, "name")
        ikiwa self.interpolation == configparser._UNSET:
            self.assertEqual(e.args, ('name', 'Interpolation Error',
                                    '%(reference)s', 'reference'))
        lasivyo isinstance(self.interpolation, configparser.LegacyInterpolation):
            self.assertEqual(e.args, ('name', 'Interpolation Error',
                                    '%(reference)s', 'reference'))

    eleza test_items(self):
        self.check_items_config([('default', '<default>'),
                                 ('getdefault', '|<default>|'),
                                 ('key', '|value|'),
                                 ('name', 'value')])

    eleza test_safe_interpolation(self):
        # See http://www.python.org/sf/511737
        cf = self.fromstring("[section]\n"
                             "option1{eq}xxx\n"
                             "option2{eq}%(option1)s/xxx\n"
                             "ok{eq}%(option1)s/%%s\n"
                             "not_ok{eq}%(option2)s/%%s".format(
                                 eq=self.delimiters[0]))
        self.assertEqual(cf.get("section", "ok"), "xxx/%s")
        ikiwa self.interpolation == configparser._UNSET:
            self.assertEqual(cf.get("section", "not_ok"), "xxx/xxx/%s")
        lasivyo isinstance(self.interpolation, configparser.LegacyInterpolation):
            ukijumuisha self.assertRaises(TypeError):
                cf.get("section", "not_ok")

    eleza test_set_malformatted_interpolation(self):
        cf = self.fromstring("[sect]\n"
                             "option1{eq}foo\n".format(eq=self.delimiters[0]))

        self.assertEqual(cf.get('sect', "option1"), "foo")

        self.assertRaises(ValueError, cf.set, "sect", "option1", "%foo")
        self.assertRaises(ValueError, cf.set, "sect", "option1", "foo%")
        self.assertRaises(ValueError, cf.set, "sect", "option1", "f%oo")

        self.assertEqual(cf.get('sect', "option1"), "foo")

        # bug #5741: double percents are *not* malformed
        cf.set("sect", "option2", "foo%%bar")
        self.assertEqual(cf.get("sect", "option2"), "foo%bar")

    eleza test_set_nonstring_types(self):
        cf = self.fromstring("[sect]\n"
                             "option1{eq}foo\n".format(eq=self.delimiters[0]))
        # Check that we get a TypeError when setting non-string values
        # kwenye an existing section:
        self.assertRaises(TypeError, cf.set, "sect", "option1", 1)
        self.assertRaises(TypeError, cf.set, "sect", "option1", 1.0)
        self.assertRaises(TypeError, cf.set, "sect", "option1", object())
        self.assertRaises(TypeError, cf.set, "sect", "option2", 1)
        self.assertRaises(TypeError, cf.set, "sect", "option2", 1.0)
        self.assertRaises(TypeError, cf.set, "sect", "option2", object())
        self.assertRaises(TypeError, cf.set, "sect", 123, "invalid opt name!")
        self.assertRaises(TypeError, cf.add_section, 123)

    eleza test_add_section_default(self):
        cf = self.newconfig()
        self.assertRaises(ValueError, cf.add_section, self.default_section)

    eleza test_defaults_keyword(self):
        """bpo-23835 fix kila ConfigParser"""
        cf = self.newconfig(defaults={1: 2.4})
        self.assertEqual(cf[self.default_section]['1'], '2.4')
        self.assertAlmostEqual(cf[self.default_section].getfloat('1'), 2.4)
        cf = self.newconfig(defaults={"A": 5.2})
        self.assertEqual(cf[self.default_section]['a'], '5.2')
        self.assertAlmostEqual(cf[self.default_section].getfloat('a'), 5.2)


kundi ConfigParserTestCaseNoInterpolation(BasicTestCase, unittest.TestCase):
    config_class = configparser.ConfigParser
    interpolation = Tupu
    ini = textwrap.dedent("""
        [numbers]
        one = 1
        two = %(one)s * 2
        three = ${common:one} * 3

        [hexen]
        sixteen = ${numbers:two} * 8
    """).strip()

    eleza assertMatchesIni(self, cf):
        self.assertEqual(cf['numbers']['one'], '1')
        self.assertEqual(cf['numbers']['two'], '%(one)s * 2')
        self.assertEqual(cf['numbers']['three'], '${common:one} * 3')
        self.assertEqual(cf['hexen']['sixteen'], '${numbers:two} * 8')

    eleza test_no_interpolation(self):
        cf = self.fromstring(self.ini)
        self.assertMatchesIni(cf)

    eleza test_empty_case(self):
        cf = self.newconfig()
        self.assertIsTupu(cf.read_string(""))

    eleza test_none_as_default_interpolation(self):
        kundi CustomConfigParser(configparser.ConfigParser):
            _DEFAULT_INTERPOLATION = Tupu

        cf = CustomConfigParser()
        cf.read_string(self.ini)
        self.assertMatchesIni(cf)


kundi ConfigParserTestCaseLegacyInterpolation(ConfigParserTestCase):
    config_class = configparser.ConfigParser
    interpolation = configparser.LegacyInterpolation()

    eleza test_set_malformatted_interpolation(self):
        cf = self.fromstring("[sect]\n"
                             "option1{eq}foo\n".format(eq=self.delimiters[0]))

        self.assertEqual(cf.get('sect', "option1"), "foo")

        cf.set("sect", "option1", "%foo")
        self.assertEqual(cf.get('sect', "option1"), "%foo")
        cf.set("sect", "option1", "foo%")
        self.assertEqual(cf.get('sect', "option1"), "foo%")
        cf.set("sect", "option1", "f%oo")
        self.assertEqual(cf.get('sect', "option1"), "f%oo")

        # bug #5741: double percents are *not* malformed
        cf.set("sect", "option2", "foo%%bar")
        self.assertEqual(cf.get("sect", "option2"), "foo%%bar")


kundi ConfigParserTestCaseNonStandardDelimiters(ConfigParserTestCase):
    delimiters = (':=', '$')
    comment_prefixes = ('//', '"')
    inline_comment_prefixes = ('//', '"')


kundi ConfigParserTestCaseNonStandardDefaultSection(ConfigParserTestCase):
    default_section = 'general'


kundi MultilineValuesTestCase(BasicTestCase, unittest.TestCase):
    config_class = configparser.ConfigParser
    wonderful_spam = ("I'm having spam spam spam spam "
                      "spam spam spam beaked beans spam "
                      "spam spam na spam!").replace(' ', '\t\n')

    eleza setUp(self):
        cf = self.newconfig()
        kila i kwenye range(100):
            s = 'section{}'.format(i)
            cf.add_section(s)
            kila j kwenye range(10):
                cf.set(s, 'lovely_spam{}'.format(j), self.wonderful_spam)
        ukijumuisha open(support.TESTFN, 'w') kama f:
            cf.write(f)

    eleza tearDown(self):
        os.unlink(support.TESTFN)

    eleza test_dominating_multiline_values(self):
        # We're reading kutoka file because this ni where the code changed
        # during performance updates kwenye Python 3.2
        cf_from_file = self.newconfig()
        ukijumuisha open(support.TESTFN) kama f:
            cf_from_file.read_file(f)
        self.assertEqual(cf_from_file.get('section8', 'lovely_spam4'),
                         self.wonderful_spam.replace('\t\n', '\n'))


kundi RawConfigParserTestCase(BasicTestCase, unittest.TestCase):
    config_class = configparser.RawConfigParser

    eleza test_interpolation(self):
        cf = self.get_interpolation_config()
        eq = self.assertEqual
        eq(cf.get("Foo", "bar"),
           "something %(with1)s interpolation (1 step)")
        eq(cf.get("Foo", "bar9"),
           "something %(with9)s lots of interpolation (9 steps)")
        eq(cf.get("Foo", "bar10"),
           "something %(with10)s lots of interpolation (10 steps)")
        eq(cf.get("Foo", "bar11"),
           "something %(with11)s lots of interpolation (11 steps)")

    eleza test_items(self):
        self.check_items_config([('default', '<default>'),
                                 ('getdefault', '|%(default)s|'),
                                 ('key', '|%(name)s|'),
                                 ('name', '%(value)s')])

    eleza test_set_nonstring_types(self):
        cf = self.newconfig()
        cf.add_section('non-string')
        cf.set('non-string', 'int', 1)
        cf.set('non-string', 'list', [0, 1, 1, 2, 3, 5, 8, 13])
        cf.set('non-string', 'dict', {'pi': 3.14159})
        self.assertEqual(cf.get('non-string', 'int'), 1)
        self.assertEqual(cf.get('non-string', 'list'),
                         [0, 1, 1, 2, 3, 5, 8, 13])
        self.assertEqual(cf.get('non-string', 'dict'), {'pi': 3.14159})
        cf.add_section(123)
        cf.set(123, 'this ni sick', Kweli)
        self.assertEqual(cf.get(123, 'this ni sick'), Kweli)
        ikiwa cf._dict ni configparser._default_dict:
            # would sio work kila SortedDict; only checking kila the most common
            # default dictionary (dict)
            cf.optionxform = lambda x: x
            cf.set('non-string', 1, 1)
            self.assertEqual(cf.get('non-string', 1), 1)

    eleza test_defaults_keyword(self):
        """bpo-23835 legacy behavior kila RawConfigParser"""
        ukijumuisha self.assertRaises(AttributeError) kama ctx:
            self.newconfig(defaults={1: 2.4})
        err = ctx.exception
        self.assertEqual(str(err), "'int' object has no attribute 'lower'")
        cf = self.newconfig(defaults={"A": 5.2})
        self.assertAlmostEqual(cf[self.default_section]['a'], 5.2)


kundi RawConfigParserTestCaseNonStandardDelimiters(RawConfigParserTestCase):
    delimiters = (':=', '$')
    comment_prefixes = ('//', '"')
    inline_comment_prefixes = ('//', '"')


kundi RawConfigParserTestSambaConf(CfgParserTestCaseClass, unittest.TestCase):
    config_class = configparser.RawConfigParser
    comment_prefixes = ('#', ';', '----')
    inline_comment_prefixes = ('//',)
    empty_lines_in_values = Uongo

    eleza test_reading(self):
        smbconf = support.findfile("cfgparser.2")
        # check when we pita a mix of readable na non-readable files:
        cf = self.newconfig()
        parsed_files = cf.read([smbconf, "nonexistent-file"], encoding='utf-8')
        self.assertEqual(parsed_files, [smbconf])
        sections = ['global', 'homes', 'printers',
                    'print$', 'pdf-generator', 'tmp', 'Agustin']
        self.assertEqual(cf.sections(), sections)
        self.assertEqual(cf.get("global", "workgroup"), "MDKGROUP")
        self.assertEqual(cf.getint("global", "max log size"), 50)
        self.assertEqual(cf.get("global", "hosts allow"), "127.")
        self.assertEqual(cf.get("tmp", "echo command"), "cat %s; rm %s")

kundi ConfigParserTestCaseExtendedInterpolation(BasicTestCase, unittest.TestCase):
    config_class = configparser.ConfigParser
    interpolation = configparser.ExtendedInterpolation()
    default_section = 'common'
    strict = Kweli

    eleza fromstring(self, string, defaults=Tupu, optionxform=Tupu):
        cf = self.newconfig(defaults)
        ikiwa optionxform:
            cf.optionxform = optionxform
        cf.read_string(string)
        rudisha cf

    eleza test_extended_interpolation(self):
        cf = self.fromstring(textwrap.dedent("""
            [common]
            favourite Beatle = Paul
            favourite color = green

            [tom]
            favourite band = ${favourite color} day
            favourite pope = John ${favourite Beatle} II
            sequel = ${favourite pope}I

            [ambv]
            favourite Beatle = George
            son of Edward VII = ${favourite Beatle} V
            son of George V = ${son of Edward VII}I

            [stanley]
            favourite Beatle = ${ambv:favourite Beatle}
            favourite pope = ${tom:favourite pope}
            favourite color = black
            favourite state of mind = paranoid
            favourite movie = soylent ${common:favourite color}
            favourite song = ${favourite color} sabbath - ${favourite state of mind}
        """).strip())

        eq = self.assertEqual
        eq(cf['common']['favourite Beatle'], 'Paul')
        eq(cf['common']['favourite color'], 'green')
        eq(cf['tom']['favourite Beatle'], 'Paul')
        eq(cf['tom']['favourite color'], 'green')
        eq(cf['tom']['favourite band'], 'green day')
        eq(cf['tom']['favourite pope'], 'John Paul II')
        eq(cf['tom']['sequel'], 'John Paul III')
        eq(cf['ambv']['favourite Beatle'], 'George')
        eq(cf['ambv']['favourite color'], 'green')
        eq(cf['ambv']['son of Edward VII'], 'George V')
        eq(cf['ambv']['son of George V'], 'George VI')
        eq(cf['stanley']['favourite Beatle'], 'George')
        eq(cf['stanley']['favourite color'], 'black')
        eq(cf['stanley']['favourite state of mind'], 'paranoid')
        eq(cf['stanley']['favourite movie'], 'soylent green')
        eq(cf['stanley']['favourite pope'], 'John Paul II')
        eq(cf['stanley']['favourite song'],
           'black sabbath - paranoid')

    eleza test_endless_loop(self):
        cf = self.fromstring(textwrap.dedent("""
            [one kila you]
            ping = ${one kila me:pong}

            [one kila me]
            pong = ${one kila you:ping}

            [selfish]
            me = ${me}
        """).strip())

        ukijumuisha self.assertRaises(configparser.InterpolationDepthError):
            cf['one kila you']['ping']
        ukijumuisha self.assertRaises(configparser.InterpolationDepthError):
            cf['selfish']['me']

    eleza test_strange_options(self):
        cf = self.fromstring("""
            [dollars]
            $var = $$value
            $var2 = ${$var}
            ${sick} = cannot interpolate me

            [interpolated]
            $other = ${dollars:$var}
            $trying = ${dollars:${sick}}
        """)

        self.assertEqual(cf['dollars']['$var'], '$value')
        self.assertEqual(cf['interpolated']['$other'], '$value')
        self.assertEqual(cf['dollars']['${sick}'], 'cannot interpolate me')
        exception_class = configparser.InterpolationMissingOptionError
        ukijumuisha self.assertRaises(exception_class) kama cm:
            cf['interpolated']['$trying']
        self.assertEqual(cm.exception.reference, 'dollars:${sick')
        self.assertEqual(cm.exception.args[2], '${dollars:${sick}}') #rawval

    eleza test_case_sensitivity_basic(self):
        ini = textwrap.dedent("""
            [common]
            optionlower = value
            OptionUpper = Value

            [Common]
            optionlower = a better ${common:optionlower}
            OptionUpper = A Better ${common:OptionUpper}

            [random]
            foolower = ${common:optionlower} redefined
            FooUpper = ${Common:OptionUpper} Redefined
        """).strip()

        cf = self.fromstring(ini)
        eq = self.assertEqual
        eq(cf['common']['optionlower'], 'value')
        eq(cf['common']['OptionUpper'], 'Value')
        eq(cf['Common']['optionlower'], 'a better value')
        eq(cf['Common']['OptionUpper'], 'A Better Value')
        eq(cf['random']['foolower'], 'value redefined')
        eq(cf['random']['FooUpper'], 'A Better Value Redefined')

    eleza test_case_sensitivity_conflicts(self):
        ini = textwrap.dedent("""
            [common]
            option = value
            Option = Value

            [Common]
            option = a better ${common:option}
            Option = A Better ${common:Option}

            [random]
            foo = ${common:option} redefined
            Foo = ${Common:Option} Redefined
        """).strip()
        ukijumuisha self.assertRaises(configparser.DuplicateOptionError):
            cf = self.fromstring(ini)

        # raw options
        cf = self.fromstring(ini, optionxform=lambda opt: opt)
        eq = self.assertEqual
        eq(cf['common']['option'], 'value')
        eq(cf['common']['Option'], 'Value')
        eq(cf['Common']['option'], 'a better value')
        eq(cf['Common']['Option'], 'A Better Value')
        eq(cf['random']['foo'], 'value redefined')
        eq(cf['random']['Foo'], 'A Better Value Redefined')

    eleza test_other_errors(self):
        cf = self.fromstring("""
            [interpolation fail]
            case1 = ${where's the brace
            case2 = ${does_not_exist}
            case3 = ${wrong_section:wrong_value}
            case4 = ${i:like:colon:characters}
            case5 = $100 kila Fail No 5!
        """)

        ukijumuisha self.assertRaises(configparser.InterpolationSyntaxError):
            cf['interpolation fail']['case1']
        ukijumuisha self.assertRaises(configparser.InterpolationMissingOptionError):
            cf['interpolation fail']['case2']
        ukijumuisha self.assertRaises(configparser.InterpolationMissingOptionError):
            cf['interpolation fail']['case3']
        ukijumuisha self.assertRaises(configparser.InterpolationSyntaxError):
            cf['interpolation fail']['case4']
        ukijumuisha self.assertRaises(configparser.InterpolationSyntaxError):
            cf['interpolation fail']['case5']
        ukijumuisha self.assertRaises(ValueError):
            cf['interpolation fail']['case6'] = "BLACK $ABBATH"


kundi ConfigParserTestCaseNoValue(ConfigParserTestCase):
    allow_no_value = Kweli


kundi ConfigParserTestCaseTrickyFile(CfgParserTestCaseClass, unittest.TestCase):
    config_class = configparser.ConfigParser
    delimiters = {'='}
    comment_prefixes = {'#'}
    allow_no_value = Kweli

    eleza test_cfgparser_dot_3(self):
        tricky = support.findfile("cfgparser.3")
        cf = self.newconfig()
        self.assertEqual(len(cf.read(tricky, encoding='utf-8')), 1)
        self.assertEqual(cf.sections(), ['strange',
                                         'corruption',
                                         'yeah, sections can be '
                                         'indented kama well',
                                         'another one!',
                                         'no values here',
                                         'tricky interpolation',
                                         'more interpolation'])
        self.assertEqual(cf.getint(self.default_section, 'go',
                                   vars={'interpolate': '-1'}), -1)
        ukijumuisha self.assertRaises(ValueError):
            # no interpolation will happen
            cf.getint(self.default_section, 'go', raw=Kweli,
                      vars={'interpolate': '-1'})
        self.assertEqual(len(cf.get('strange', 'other').split('\n')), 4)
        self.assertEqual(len(cf.get('corruption', 'value').split('\n')), 10)
        longname = 'yeah, sections can be indented kama well'
        self.assertUongo(cf.getboolean(longname, 'are they subsections'))
        self.assertEqual(cf.get(longname, 'lets use some Unicode'), '片仮名')
        self.assertEqual(len(cf.items('another one!')), 5) # 4 kwenye section na
                                                           # `go` kutoka DEFAULT
        ukijumuisha self.assertRaises(configparser.InterpolationMissingOptionError):
            cf.items('no values here')
        self.assertEqual(cf.get('tricky interpolation', 'lets'), 'do this')
        self.assertEqual(cf.get('tricky interpolation', 'lets'),
                         cf.get('tricky interpolation', 'go'))
        self.assertEqual(cf.get('more interpolation', 'lets'), 'go shopping')

    eleza test_unicode_failure(self):
        tricky = support.findfile("cfgparser.3")
        cf = self.newconfig()
        ukijumuisha self.assertRaises(UnicodeDecodeError):
            cf.read(tricky, encoding='ascii')


kundi Issue7005TestCase(unittest.TestCase):
    """Test output when Tupu ni set() kama a value na allow_no_value == Uongo.

    http://bugs.python.org/issue7005

    """

    expected_output = "[section]\noption = Tupu\n\n"

    eleza prepare(self, config_class):
        # This ni the default, but that's the point.
        cp = config_class(allow_no_value=Uongo)
        cp.add_section("section")
        cp.set("section", "option", Tupu)
        sio = io.StringIO()
        cp.write(sio)
        rudisha sio.getvalue()

    eleza test_none_as_value_stringified(self):
        cp = configparser.ConfigParser(allow_no_value=Uongo)
        cp.add_section("section")
        ukijumuisha self.assertRaises(TypeError):
            cp.set("section", "option", Tupu)

    eleza test_none_as_value_stringified_raw(self):
        output = self.prepare(configparser.RawConfigParser)
        self.assertEqual(output, self.expected_output)


kundi SortedTestCase(RawConfigParserTestCase):
    dict_type = SortedDict

    eleza test_sorted(self):
        cf = self.fromstring("[b]\n"
                             "o4=1\n"
                             "o3=2\n"
                             "o2=3\n"
                             "o1=4\n"
                             "[a]\n"
                             "k=v\n")
        output = io.StringIO()
        cf.write(output)
        self.assertEqual(output.getvalue(),
                         "[a]\n"
                         "k = v\n\n"
                         "[b]\n"
                         "o1 = 4\n"
                         "o2 = 3\n"
                         "o3 = 2\n"
                         "o4 = 1\n\n")


kundi CompatibleTestCase(CfgParserTestCaseClass, unittest.TestCase):
    config_class = configparser.RawConfigParser
    comment_prefixes = '#;'
    inline_comment_prefixes = ';'

    eleza test_comment_handling(self):
        config_string = textwrap.dedent("""\
        [Commented Bar]
        baz=qwe ; a comment
        foo: bar # sio a comment!
        # but this ni a comment
        ; another comment
        quirk: this;is sio a comment
        ; a space must precede an inline comment
        """)
        cf = self.fromstring(config_string)
        self.assertEqual(cf.get('Commented Bar', 'foo'),
                         'bar # sio a comment!')
        self.assertEqual(cf.get('Commented Bar', 'baz'), 'qwe')
        self.assertEqual(cf.get('Commented Bar', 'quirk'),
                         'this;is sio a comment')

kundi CopyTestCase(BasicTestCase, unittest.TestCase):
    config_class = configparser.ConfigParser

    eleza fromstring(self, string, defaults=Tupu):
        cf = self.newconfig(defaults)
        cf.read_string(string)
        cf_copy = self.newconfig()
        cf_copy.read_dict(cf)
        # we have to clean up option duplicates that appeared because of
        # the magic DEFAULTSECT behaviour.
        kila section kwenye cf_copy.values():
            ikiwa section.name == self.default_section:
                endelea
            kila default, value kwenye cf[self.default_section].items():
                ikiwa section[default] == value:
                    toa section[default]
        rudisha cf_copy


kundi FakeFile:
    eleza __init__(self):
        file_path = support.findfile("cfgparser.1")
        ukijumuisha open(file_path) kama f:
            self.lines = f.readlines()
            self.lines.reverse()

    eleza readline(self):
        ikiwa len(self.lines):
            rudisha self.lines.pop()
        rudisha ''


eleza readline_generator(f):
    """As advised kwenye Doc/library/configparser.rst."""
    line = f.readline()
    wakati line:
        tuma line
        line = f.readline()


kundi ReadFileTestCase(unittest.TestCase):
    eleza test_file(self):
        file_paths = [support.findfile("cfgparser.1")]
        jaribu:
            file_paths.append(file_paths[0].encode('utf8'))
        tatizo UnicodeEncodeError:
            pita   # unfortunately we can't test bytes on this path
        kila file_path kwenye file_paths:
            parser = configparser.ConfigParser()
            ukijumuisha open(file_path) kama f:
                parser.read_file(f)
            self.assertIn("Foo Bar", parser)
            self.assertIn("foo", parser["Foo Bar"])
            self.assertEqual(parser["Foo Bar"]["foo"], "newbar")

    eleza test_iterable(self):
        lines = textwrap.dedent("""
        [Foo Bar]
        foo=newbar""").strip().split('\n')
        parser = configparser.ConfigParser()
        parser.read_file(lines)
        self.assertIn("Foo Bar", parser)
        self.assertIn("foo", parser["Foo Bar"])
        self.assertEqual(parser["Foo Bar"]["foo"], "newbar")

    eleza test_readline_generator(self):
        """Issue #11670."""
        parser = configparser.ConfigParser()
        ukijumuisha self.assertRaises(TypeError):
            parser.read_file(FakeFile())
        parser.read_file(readline_generator(FakeFile()))
        self.assertIn("Foo Bar", parser)
        self.assertIn("foo", parser["Foo Bar"])
        self.assertEqual(parser["Foo Bar"]["foo"], "newbar")

    eleza test_source_as_bytes(self):
        """Issue #18260."""
        lines = textwrap.dedent("""
        [badbad]
        [badbad]""").strip().split('\n')
        parser = configparser.ConfigParser()
        ukijumuisha self.assertRaises(configparser.DuplicateSectionError) kama dse:
            parser.read_file(lines, source=b"badbad")
        self.assertEqual(
            str(dse.exception),
            "While reading kutoka b'badbad' [line  2]: section 'badbad' "
            "already exists"
        )
        lines = textwrap.dedent("""
        [badbad]
        bad = bad
        bad = bad""").strip().split('\n')
        parser = configparser.ConfigParser()
        ukijumuisha self.assertRaises(configparser.DuplicateOptionError) kama dse:
            parser.read_file(lines, source=b"badbad")
        self.assertEqual(
            str(dse.exception),
            "While reading kutoka b'badbad' [line  3]: option 'bad' kwenye section "
            "'badbad' already exists"
        )
        lines = textwrap.dedent("""
        [badbad]
        = bad""").strip().split('\n')
        parser = configparser.ConfigParser()
        ukijumuisha self.assertRaises(configparser.ParsingError) kama dse:
            parser.read_file(lines, source=b"badbad")
        self.assertEqual(
            str(dse.exception),
            "Source contains parsing errors: b'badbad'\n\t[line  2]: '= bad'"
        )
        lines = textwrap.dedent("""
        [badbad
        bad = bad""").strip().split('\n')
        parser = configparser.ConfigParser()
        ukijumuisha self.assertRaises(configparser.MissingSectionHeaderError) kama dse:
            parser.read_file(lines, source=b"badbad")
        self.assertEqual(
            str(dse.exception),
            "File contains no section headers.\nfile: b'badbad', line: 1\n"
            "'[badbad'"
        )


kundi CoverageOneHundredTestCase(unittest.TestCase):
    """Covers edge cases kwenye the codebase."""

    eleza test_duplicate_option_error(self):
        error = configparser.DuplicateOptionError('section', 'option')
        self.assertEqual(error.section, 'section')
        self.assertEqual(error.option, 'option')
        self.assertEqual(error.source, Tupu)
        self.assertEqual(error.lineno, Tupu)
        self.assertEqual(error.args, ('section', 'option', Tupu, Tupu))
        self.assertEqual(str(error), "Option 'option' kwenye section 'section' "
                                     "already exists")

    eleza test_interpolation_depth_error(self):
        error = configparser.InterpolationDepthError('option', 'section',
                                                     'rawval')
        self.assertEqual(error.args, ('option', 'section', 'rawval'))
        self.assertEqual(error.option, 'option')
        self.assertEqual(error.section, 'section')

    eleza test_parsing_error(self):
        ukijumuisha self.assertRaises(ValueError) kama cm:
            configparser.ParsingError()
        self.assertEqual(str(cm.exception), "Required argument `source' sio "
                                            "given.")
        ukijumuisha self.assertRaises(ValueError) kama cm:
            configparser.ParsingError(source='source', filename='filename')
        self.assertEqual(str(cm.exception), "Cannot specify both `filename' "
                                            "and `source'. Use `source'.")
        error = configparser.ParsingError(filename='source')
        self.assertEqual(error.source, 'source')
        ukijumuisha warnings.catch_warnings(record=Kweli) kama w:
            warnings.simplefilter("always", DeprecationWarning)
            self.assertEqual(error.filename, 'source')
            error.filename = 'filename'
            self.assertEqual(error.source, 'filename')
        kila warning kwenye w:
            self.assertKweli(warning.category ni DeprecationWarning)

    eleza test_interpolation_validation(self):
        parser = configparser.ConfigParser()
        parser.read_string("""
            [section]
            invalid_percent = %
            invalid_reference = %(()
            invalid_variable = %(does_not_exist)s
        """)
        ukijumuisha self.assertRaises(configparser.InterpolationSyntaxError) kama cm:
            parser['section']['invalid_percent']
        self.assertEqual(str(cm.exception), "'%' must be followed by '%' ama "
                                            "'(', found: '%'")
        ukijumuisha self.assertRaises(configparser.InterpolationSyntaxError) kama cm:
            parser['section']['invalid_reference']
        self.assertEqual(str(cm.exception), "bad interpolation variable "
                                            "reference '%(()'")

    eleza test_readfp_deprecation(self):
        sio = io.StringIO("""
        [section]
        option = value
        """)
        parser = configparser.ConfigParser()
        ukijumuisha warnings.catch_warnings(record=Kweli) kama w:
            warnings.simplefilter("always", DeprecationWarning)
            parser.readfp(sio, filename='StringIO')
        kila warning kwenye w:
            self.assertKweli(warning.category ni DeprecationWarning)
        self.assertEqual(len(parser), 2)
        self.assertEqual(parser['section']['option'], 'value')

    eleza test_safeconfigparser_deprecation(self):
        ukijumuisha warnings.catch_warnings(record=Kweli) kama w:
            warnings.simplefilter("always", DeprecationWarning)
            parser = configparser.SafeConfigParser()
        kila warning kwenye w:
            self.assertKweli(warning.category ni DeprecationWarning)

    eleza test_sectionproxy_repr(self):
        parser = configparser.ConfigParser()
        parser.read_string("""
            [section]
            key = value
        """)
        self.assertEqual(repr(parser['section']), '<Section: section>')

    eleza test_inconsistent_converters_state(self):
        parser = configparser.ConfigParser()
        agiza decimal
        parser.converters['decimal'] = decimal.Decimal
        parser.read_string("""
            [s1]
            one = 1
            [s2]
            two = 2
        """)
        self.assertIn('decimal', parser.converters)
        self.assertEqual(parser.getdecimal('s1', 'one'), 1)
        self.assertEqual(parser.getdecimal('s2', 'two'), 2)
        self.assertEqual(parser['s1'].getdecimal('one'), 1)
        self.assertEqual(parser['s2'].getdecimal('two'), 2)
        toa parser.getdecimal
        ukijumuisha self.assertRaises(AttributeError):
            parser.getdecimal('s1', 'one')
        self.assertIn('decimal', parser.converters)
        toa parser.converters['decimal']
        self.assertNotIn('decimal', parser.converters)
        ukijumuisha self.assertRaises(AttributeError):
            parser.getdecimal('s1', 'one')
        ukijumuisha self.assertRaises(AttributeError):
            parser['s1'].getdecimal('one')
        ukijumuisha self.assertRaises(AttributeError):
            parser['s2'].getdecimal('two')


kundi ExceptionPicklingTestCase(unittest.TestCase):
    """Tests kila issue #13760: ConfigParser exceptions are sio picklable."""

    eleza test_error(self):
        agiza pickle
        e1 = configparser.Error('value')
        kila proto kwenye range(pickle.HIGHEST_PROTOCOL + 1):
            pickled = pickle.dumps(e1, proto)
            e2 = pickle.loads(pickled)
            self.assertEqual(e1.message, e2.message)
            self.assertEqual(repr(e1), repr(e2))

    eleza test_nosectionerror(self):
        agiza pickle
        e1 = configparser.NoSectionError('section')
        kila proto kwenye range(pickle.HIGHEST_PROTOCOL + 1):
            pickled = pickle.dumps(e1, proto)
            e2 = pickle.loads(pickled)
            self.assertEqual(e1.message, e2.message)
            self.assertEqual(e1.args, e2.args)
            self.assertEqual(e1.section, e2.section)
            self.assertEqual(repr(e1), repr(e2))

    eleza test_nooptionerror(self):
        agiza pickle
        e1 = configparser.NoOptionError('option', 'section')
        kila proto kwenye range(pickle.HIGHEST_PROTOCOL + 1):
            pickled = pickle.dumps(e1, proto)
            e2 = pickle.loads(pickled)
            self.assertEqual(e1.message, e2.message)
            self.assertEqual(e1.args, e2.args)
            self.assertEqual(e1.section, e2.section)
            self.assertEqual(e1.option, e2.option)
            self.assertEqual(repr(e1), repr(e2))

    eleza test_duplicatesectionerror(self):
        agiza pickle
        e1 = configparser.DuplicateSectionError('section', 'source', 123)
        kila proto kwenye range(pickle.HIGHEST_PROTOCOL + 1):
            pickled = pickle.dumps(e1, proto)
            e2 = pickle.loads(pickled)
            self.assertEqual(e1.message, e2.message)
            self.assertEqual(e1.args, e2.args)
            self.assertEqual(e1.section, e2.section)
            self.assertEqual(e1.source, e2.source)
            self.assertEqual(e1.lineno, e2.lineno)
            self.assertEqual(repr(e1), repr(e2))

    eleza test_duplicateoptionerror(self):
        agiza pickle
        e1 = configparser.DuplicateOptionError('section', 'option', 'source',
            123)
        kila proto kwenye range(pickle.HIGHEST_PROTOCOL + 1):
            pickled = pickle.dumps(e1, proto)
            e2 = pickle.loads(pickled)
            self.assertEqual(e1.message, e2.message)
            self.assertEqual(e1.args, e2.args)
            self.assertEqual(e1.section, e2.section)
            self.assertEqual(e1.option, e2.option)
            self.assertEqual(e1.source, e2.source)
            self.assertEqual(e1.lineno, e2.lineno)
            self.assertEqual(repr(e1), repr(e2))

    eleza test_interpolationerror(self):
        agiza pickle
        e1 = configparser.InterpolationError('option', 'section', 'msg')
        kila proto kwenye range(pickle.HIGHEST_PROTOCOL + 1):
            pickled = pickle.dumps(e1, proto)
            e2 = pickle.loads(pickled)
            self.assertEqual(e1.message, e2.message)
            self.assertEqual(e1.args, e2.args)
            self.assertEqual(e1.section, e2.section)
            self.assertEqual(e1.option, e2.option)
            self.assertEqual(repr(e1), repr(e2))

    eleza test_interpolationmissingoptionerror(self):
        agiza pickle
        e1 = configparser.InterpolationMissingOptionError('option', 'section',
            'rawval', 'reference')
        kila proto kwenye range(pickle.HIGHEST_PROTOCOL + 1):
            pickled = pickle.dumps(e1, proto)
            e2 = pickle.loads(pickled)
            self.assertEqual(e1.message, e2.message)
            self.assertEqual(e1.args, e2.args)
            self.assertEqual(e1.section, e2.section)
            self.assertEqual(e1.option, e2.option)
            self.assertEqual(e1.reference, e2.reference)
            self.assertEqual(repr(e1), repr(e2))

    eleza test_interpolationsyntaxerror(self):
        agiza pickle
        e1 = configparser.InterpolationSyntaxError('option', 'section', 'msg')
        kila proto kwenye range(pickle.HIGHEST_PROTOCOL + 1):
            pickled = pickle.dumps(e1, proto)
            e2 = pickle.loads(pickled)
            self.assertEqual(e1.message, e2.message)
            self.assertEqual(e1.args, e2.args)
            self.assertEqual(e1.section, e2.section)
            self.assertEqual(e1.option, e2.option)
            self.assertEqual(repr(e1), repr(e2))

    eleza test_interpolationdeptherror(self):
        agiza pickle
        e1 = configparser.InterpolationDepthError('option', 'section',
            'rawval')
        kila proto kwenye range(pickle.HIGHEST_PROTOCOL + 1):
            pickled = pickle.dumps(e1, proto)
            e2 = pickle.loads(pickled)
            self.assertEqual(e1.message, e2.message)
            self.assertEqual(e1.args, e2.args)
            self.assertEqual(e1.section, e2.section)
            self.assertEqual(e1.option, e2.option)
            self.assertEqual(repr(e1), repr(e2))

    eleza test_parsingerror(self):
        agiza pickle
        e1 = configparser.ParsingError('source')
        e1.append(1, 'line1')
        e1.append(2, 'line2')
        e1.append(3, 'line3')
        kila proto kwenye range(pickle.HIGHEST_PROTOCOL + 1):
            pickled = pickle.dumps(e1, proto)
            e2 = pickle.loads(pickled)
            self.assertEqual(e1.message, e2.message)
            self.assertEqual(e1.args, e2.args)
            self.assertEqual(e1.source, e2.source)
            self.assertEqual(e1.errors, e2.errors)
            self.assertEqual(repr(e1), repr(e2))
        e1 = configparser.ParsingError(filename='filename')
        e1.append(1, 'line1')
        e1.append(2, 'line2')
        e1.append(3, 'line3')
        kila proto kwenye range(pickle.HIGHEST_PROTOCOL + 1):
            pickled = pickle.dumps(e1, proto)
            e2 = pickle.loads(pickled)
            self.assertEqual(e1.message, e2.message)
            self.assertEqual(e1.args, e2.args)
            self.assertEqual(e1.source, e2.source)
            self.assertEqual(e1.errors, e2.errors)
            self.assertEqual(repr(e1), repr(e2))

    eleza test_missingsectionheadererror(self):
        agiza pickle
        e1 = configparser.MissingSectionHeaderError('filename', 123, 'line')
        kila proto kwenye range(pickle.HIGHEST_PROTOCOL + 1):
            pickled = pickle.dumps(e1, proto)
            e2 = pickle.loads(pickled)
            self.assertEqual(e1.message, e2.message)
            self.assertEqual(e1.args, e2.args)
            self.assertEqual(e1.line, e2.line)
            self.assertEqual(e1.source, e2.source)
            self.assertEqual(e1.lineno, e2.lineno)
            self.assertEqual(repr(e1), repr(e2))


kundi InlineCommentStrippingTestCase(unittest.TestCase):
    """Tests kila issue #14590: ConfigParser doesn't strip inline comment when
    delimiter occurs earlier without preceding space.."""

    eleza test_stripping(self):
        cfg = configparser.ConfigParser(inline_comment_prefixes=(';', '#',
                '//'))
        cfg.read_string("""
        [section]
        k1 = v1;still v1
        k2 = v2 ;a comment
        k3 = v3 ; also a comment
        k4 = v4;still v4 ;a comment
        k5 = v5;still v5 ; also a comment
        k6 = v6;still v6; na still v6 ;a comment
        k7 = v7;still v7; na still v7 ; also a comment

        [multiprefix]
        k1 = v1;still v1 #a comment ; yeah, pretty much
        k2 = v2 // this already ni a comment ; endelead
        k3 = v3;#//still v3# na still v3 ; a comment
        """)
        s = cfg['section']
        self.assertEqual(s['k1'], 'v1;still v1')
        self.assertEqual(s['k2'], 'v2')
        self.assertEqual(s['k3'], 'v3')
        self.assertEqual(s['k4'], 'v4;still v4')
        self.assertEqual(s['k5'], 'v5;still v5')
        self.assertEqual(s['k6'], 'v6;still v6; na still v6')
        self.assertEqual(s['k7'], 'v7;still v7; na still v7')
        s = cfg['multiprefix']
        self.assertEqual(s['k1'], 'v1;still v1')
        self.assertEqual(s['k2'], 'v2')
        self.assertEqual(s['k3'], 'v3;#//still v3# na still v3')


kundi ExceptionContextTestCase(unittest.TestCase):
    """ Test that implementation details doesn't leak
    through raising exceptions. """

    eleza test_get_basic_interpolation(self):
        parser = configparser.ConfigParser()
        parser.read_string("""
        [Paths]
        home_dir: /Users
        my_dir: %(home_dir1)s/lumberjack
        my_pictures: %(my_dir)s/Pictures
        """)
        cm = self.assertRaises(configparser.InterpolationMissingOptionError)
        ukijumuisha cm:
            parser.get('Paths', 'my_dir')
        self.assertIs(cm.exception.__suppress_context__, Kweli)

    eleza test_get_extended_interpolation(self):
        parser = configparser.ConfigParser(
          interpolation=configparser.ExtendedInterpolation())
        parser.read_string("""
        [Paths]
        home_dir: /Users
        my_dir: ${home_dir1}/lumberjack
        my_pictures: ${my_dir}/Pictures
        """)
        cm = self.assertRaises(configparser.InterpolationMissingOptionError)
        ukijumuisha cm:
            parser.get('Paths', 'my_dir')
        self.assertIs(cm.exception.__suppress_context__, Kweli)

    eleza test_missing_options(self):
        parser = configparser.ConfigParser()
        parser.read_string("""
        [Paths]
        home_dir: /Users
        """)
        ukijumuisha self.assertRaises(configparser.NoSectionError) kama cm:
            parser.options('test')
        self.assertIs(cm.exception.__suppress_context__, Kweli)

    eleza test_missing_section(self):
        config = configparser.ConfigParser()
        ukijumuisha self.assertRaises(configparser.NoSectionError) kama cm:
            config.set('Section1', 'an_int', '15')
        self.assertIs(cm.exception.__suppress_context__, Kweli)

    eleza test_remove_option(self):
        config = configparser.ConfigParser()
        ukijumuisha self.assertRaises(configparser.NoSectionError) kama cm:
            config.remove_option('Section1', 'an_int')
        self.assertIs(cm.exception.__suppress_context__, Kweli)


kundi ConvertersTestCase(BasicTestCase, unittest.TestCase):
    """Introduced kwenye 3.5, issue #18159."""

    config_class = configparser.ConfigParser

    eleza newconfig(self, defaults=Tupu):
        instance = super().newconfig(defaults=defaults)
        instance.converters['list'] = lambda v: [e.strip() kila e kwenye v.split()
                                                 ikiwa e.strip()]
        rudisha instance

    eleza test_converters(self):
        cfg = self.newconfig()
        self.assertIn('boolean', cfg.converters)
        self.assertIn('list', cfg.converters)
        self.assertIsTupu(cfg.converters['int'])
        self.assertIsTupu(cfg.converters['float'])
        self.assertIsTupu(cfg.converters['boolean'])
        self.assertIsNotTupu(cfg.converters['list'])
        self.assertEqual(len(cfg.converters), 4)
        ukijumuisha self.assertRaises(ValueError):
            cfg.converters[''] = lambda v: v
        ukijumuisha self.assertRaises(ValueError):
            cfg.converters[Tupu] = lambda v: v
        cfg.read_string("""
        [s]
        str = string
        int = 1
        float = 0.5
        list = a b c d e f g
        bool = yes
        """)
        s = cfg['s']
        self.assertEqual(s['str'], 'string')
        self.assertEqual(s['int'], '1')
        self.assertEqual(s['float'], '0.5')
        self.assertEqual(s['list'], 'a b c d e f g')
        self.assertEqual(s['bool'], 'yes')
        self.assertEqual(cfg.get('s', 'str'), 'string')
        self.assertEqual(cfg.get('s', 'int'), '1')
        self.assertEqual(cfg.get('s', 'float'), '0.5')
        self.assertEqual(cfg.get('s', 'list'), 'a b c d e f g')
        self.assertEqual(cfg.get('s', 'bool'), 'yes')
        self.assertEqual(cfg.get('s', 'str'), 'string')
        self.assertEqual(cfg.getint('s', 'int'), 1)
        self.assertEqual(cfg.getfloat('s', 'float'), 0.5)
        self.assertEqual(cfg.getlist('s', 'list'), ['a', 'b', 'c', 'd',
                                                    'e', 'f', 'g'])
        self.assertEqual(cfg.getboolean('s', 'bool'), Kweli)
        self.assertEqual(s.get('str'), 'string')
        self.assertEqual(s.getint('int'), 1)
        self.assertEqual(s.getfloat('float'), 0.5)
        self.assertEqual(s.getlist('list'), ['a', 'b', 'c', 'd',
                                             'e', 'f', 'g'])
        self.assertEqual(s.getboolean('bool'), Kweli)
        ukijumuisha self.assertRaises(AttributeError):
            cfg.getdecimal('s', 'float')
        ukijumuisha self.assertRaises(AttributeError):
            s.getdecimal('float')
        agiza decimal
        cfg.converters['decimal'] = decimal.Decimal
        self.assertIn('decimal', cfg.converters)
        self.assertIsNotTupu(cfg.converters['decimal'])
        self.assertEqual(len(cfg.converters), 5)
        dec0_5 = decimal.Decimal('0.5')
        self.assertEqual(cfg.getdecimal('s', 'float'), dec0_5)
        self.assertEqual(s.getdecimal('float'), dec0_5)
        toa cfg.converters['decimal']
        self.assertNotIn('decimal', cfg.converters)
        self.assertEqual(len(cfg.converters), 4)
        ukijumuisha self.assertRaises(AttributeError):
            cfg.getdecimal('s', 'float')
        ukijumuisha self.assertRaises(AttributeError):
            s.getdecimal('float')
        ukijumuisha self.assertRaises(KeyError):
            toa cfg.converters['decimal']
        ukijumuisha self.assertRaises(KeyError):
            toa cfg.converters['']
        ukijumuisha self.assertRaises(KeyError):
            toa cfg.converters[Tupu]


kundi BlatantOverrideConvertersTestCase(unittest.TestCase):
    """What ikiwa somebody overrode a getboolean()? We want to make sure that kwenye
    this case the automatic converters do sio kick in."""

    config = """
        [one]
        one = false
        two = false
        three = long story short

        [two]
        one = false
        two = false
        three = four
    """

    eleza test_converters_at_init(self):
        cfg = configparser.ConfigParser(converters={'len': len})
        cfg.read_string(self.config)
        self._test_len(cfg)
        self.assertIsNotTupu(cfg.converters['len'])

    eleza test_inheritance(self):
        kundi StrangeConfigParser(configparser.ConfigParser):
            gettysburg = 'a historic borough kwenye south central Pennsylvania'

            eleza getboolean(self, section, option, *, raw=Uongo, vars=Tupu,
                        fallback=configparser._UNSET):
                ikiwa section == option:
                    rudisha Kweli
                rudisha super().getboolean(section, option, raw=raw, vars=vars,
                                          fallback=fallback)
            eleza getlen(self, section, option, *, raw=Uongo, vars=Tupu,
                       fallback=configparser._UNSET):
                rudisha self._get_conv(section, option, len, raw=raw, vars=vars,
                                      fallback=fallback)

        cfg = StrangeConfigParser()
        cfg.read_string(self.config)
        self._test_len(cfg)
        self.assertIsTupu(cfg.converters['len'])
        self.assertKweli(cfg.getboolean('one', 'one'))
        self.assertKweli(cfg.getboolean('two', 'two'))
        self.assertUongo(cfg.getboolean('one', 'two'))
        self.assertUongo(cfg.getboolean('two', 'one'))
        cfg.converters['boolean'] = cfg._convert_to_boolean
        self.assertUongo(cfg.getboolean('one', 'one'))
        self.assertUongo(cfg.getboolean('two', 'two'))
        self.assertUongo(cfg.getboolean('one', 'two'))
        self.assertUongo(cfg.getboolean('two', 'one'))

    eleza _test_len(self, cfg):
        self.assertEqual(len(cfg.converters), 4)
        self.assertIn('boolean', cfg.converters)
        self.assertIn('len', cfg.converters)
        self.assertNotIn('tysburg', cfg.converters)
        self.assertIsTupu(cfg.converters['int'])
        self.assertIsTupu(cfg.converters['float'])
        self.assertIsTupu(cfg.converters['boolean'])
        self.assertEqual(cfg.getlen('one', 'one'), 5)
        self.assertEqual(cfg.getlen('one', 'two'), 5)
        self.assertEqual(cfg.getlen('one', 'three'), 16)
        self.assertEqual(cfg.getlen('two', 'one'), 5)
        self.assertEqual(cfg.getlen('two', 'two'), 5)
        self.assertEqual(cfg.getlen('two', 'three'), 4)
        self.assertEqual(cfg.getlen('two', 'four', fallback=0), 0)
        ukijumuisha self.assertRaises(configparser.NoOptionError):
            cfg.getlen('two', 'four')
        self.assertEqual(cfg['one'].getlen('one'), 5)
        self.assertEqual(cfg['one'].getlen('two'), 5)
        self.assertEqual(cfg['one'].getlen('three'), 16)
        self.assertEqual(cfg['two'].getlen('one'), 5)
        self.assertEqual(cfg['two'].getlen('two'), 5)
        self.assertEqual(cfg['two'].getlen('three'), 4)
        self.assertEqual(cfg['two'].getlen('four', 0), 0)
        self.assertEqual(cfg['two'].getlen('four'), Tupu)

    eleza test_instance_assignment(self):
        cfg = configparser.ConfigParser()
        cfg.getboolean = lambda section, option: Kweli
        cfg.getlen = lambda section, option: len(cfg[section][option])
        cfg.read_string(self.config)
        self.assertEqual(len(cfg.converters), 3)
        self.assertIn('boolean', cfg.converters)
        self.assertNotIn('len', cfg.converters)
        self.assertIsTupu(cfg.converters['int'])
        self.assertIsTupu(cfg.converters['float'])
        self.assertIsTupu(cfg.converters['boolean'])
        self.assertKweli(cfg.getboolean('one', 'one'))
        self.assertKweli(cfg.getboolean('two', 'two'))
        self.assertKweli(cfg.getboolean('one', 'two'))
        self.assertKweli(cfg.getboolean('two', 'one'))
        cfg.converters['boolean'] = cfg._convert_to_boolean
        self.assertUongo(cfg.getboolean('one', 'one'))
        self.assertUongo(cfg.getboolean('two', 'two'))
        self.assertUongo(cfg.getboolean('one', 'two'))
        self.assertUongo(cfg.getboolean('two', 'one'))
        self.assertEqual(cfg.getlen('one', 'one'), 5)
        self.assertEqual(cfg.getlen('one', 'two'), 5)
        self.assertEqual(cfg.getlen('one', 'three'), 16)
        self.assertEqual(cfg.getlen('two', 'one'), 5)
        self.assertEqual(cfg.getlen('two', 'two'), 5)
        self.assertEqual(cfg.getlen('two', 'three'), 4)
        # If a getter impl ni assigned straight to the instance, it won't
        # be available on the section proxies.
        ukijumuisha self.assertRaises(AttributeError):
            self.assertEqual(cfg['one'].getlen('one'), 5)
        ukijumuisha self.assertRaises(AttributeError):
            self.assertEqual(cfg['two'].getlen('one'), 5)


kundi MiscTestCase(unittest.TestCase):
    eleza test__all__(self):
        blacklist = {"Error"}
        support.check__all__(self, configparser, blacklist=blacklist)


ikiwa __name__ == '__main__':
    unittest.main()
