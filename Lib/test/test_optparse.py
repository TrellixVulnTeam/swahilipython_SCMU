#
# Test suite kila Optik.  Supplied by Johannes Gijsbers
# (taradino@softhome.net) -- translated kutoka the original Optik
# test suite to this PyUnit-based version.
#
# $Id$
#

agiza sys
agiza os
agiza re
agiza copy
agiza unittest

kutoka io agiza StringIO
kutoka test agiza support


agiza optparse
kutoka optparse agiza make_option, Option, \
     TitledHelpFormatter, OptionParser, OptionGroup, \
     SUPPRESS_USAGE, OptionError, OptionConflictError, \
     BadOptionError, OptionValueError, Values
kutoka optparse agiza _match_abbrev
kutoka optparse agiza _parse_num

kundi InterceptedError(Exception):
    eleza __init__(self,
                 error_message=Tupu,
                 exit_status=Tupu,
                 exit_message=Tupu):
        self.error_message = error_message
        self.exit_status = exit_status
        self.exit_message = exit_message

    eleza __str__(self):
        rudisha self.error_message ama self.exit_message ama "intercepted error"

kundi InterceptingOptionParser(OptionParser):
    eleza exit(self, status=0, msg=Tupu):
         ashiria InterceptedError(exit_status=status, exit_message=msg)

    eleza error(self, msg):
         ashiria InterceptedError(error_message=msg)


kundi BaseTest(unittest.TestCase):
    eleza assertParseOK(self, args, expected_opts, expected_positional_args):
        """Assert the options are what we expected when parsing arguments.

        Otherwise, fail ukijumuisha a nicely formatted message.

        Keyword arguments:
        args -- A list of arguments to parse ukijumuisha OptionParser.
        expected_opts -- The options expected.
        expected_positional_args -- The positional arguments expected.

        Returns the options na positional args kila further testing.
        """

        (options, positional_args) = self.parser.parse_args(args)
        optdict = vars(options)

        self.assertEqual(optdict, expected_opts,
                         """
Options are %(optdict)s.
Should be %(expected_opts)s.
Args were %(args)s.""" % locals())

        self.assertEqual(positional_args, expected_positional_args,
                         """
Positional arguments are %(positional_args)s.
Should be %(expected_positional_args)s.
Args were %(args)s.""" % locals ())

        rudisha (options, positional_args)

    eleza assertRaises(self,
                     func,
                     args,
                     kwargs,
                     expected_exception,
                     expected_message):
        """
        Assert that the expected exception ni raised when calling a
        function, na that the right error message ni included with
        that exception.

        Arguments:
          func -- the function to call
          args -- positional arguments to `func`
          kwargs -- keyword arguments to `func`
          expected_exception -- exception that should be raised
          expected_message -- expected exception message (or pattern
            ikiwa a compiled regex object)

        Returns the exception raised kila further testing.
        """
        ikiwa args ni Tupu:
            args = ()
        ikiwa kwargs ni Tupu:
            kwargs = {}

        jaribu:
            func(*args, **kwargs)
        except expected_exception as err:
            actual_message = str(err)
            ikiwa isinstance(expected_message, re.Pattern):
                self.assertKweli(expected_message.search(actual_message),
                             """\
expected exception message pattern:
/%s/
actual exception message:
'''%s'''
""" % (expected_message.pattern, actual_message))
            isipokua:
                self.assertEqual(actual_message,
                                 expected_message,
                                 """\
expected exception message:
'''%s'''
actual exception message:
'''%s'''
""" % (expected_message, actual_message))

            rudisha err
        isipokua:
            self.fail("""expected exception %(expected_exception)s sio raised
called %(func)r
ukijumuisha args %(args)r
and kwargs %(kwargs)r
""" % locals ())


    # -- Assertions used kwenye more than one kundi --------------------

    eleza assertParseFail(self, cmdline_args, expected_output):
        """
        Assert the parser fails ukijumuisha the expected message.  Caller
        must ensure that self.parser ni an InterceptingOptionParser.
        """
        jaribu:
            self.parser.parse_args(cmdline_args)
        except InterceptedError as err:
            self.assertEqual(err.error_message, expected_output)
        isipokua:
            self.assertUongo("expected parse failure")

    eleza assertOutput(self,
                     cmdline_args,
                     expected_output,
                     expected_status=0,
                     expected_error=Tupu):
        """Assert the parser prints the expected output on stdout."""
        save_stdout = sys.stdout
        jaribu:
            jaribu:
                sys.stdout = StringIO()
                self.parser.parse_args(cmdline_args)
            mwishowe:
                output = sys.stdout.getvalue()
                sys.stdout = save_stdout

        except InterceptedError as err:
            self.assertKweli(
                isinstance(output, str),
                "expected output to be an ordinary string, sio %r"
                % type(output))

            ikiwa output != expected_output:
                self.fail("expected: \n'''\n" + expected_output +
                          "'''\nbut got \n'''\n" + output + "'''")
            self.assertEqual(err.exit_status, expected_status)
            self.assertEqual(err.exit_message, expected_error)
        isipokua:
            self.assertUongo("expected parser.exit()")

    eleza assertTypeError(self, func, expected_message, *args):
        """Assert that TypeError ni raised when executing func."""
        self.assertRaises(func, args, Tupu, TypeError, expected_message)

    eleza assertHelp(self, parser, expected_help):
        actual_help = parser.format_help()
        ikiwa actual_help != expected_help:
             ashiria self.failureException(
                'help text failure; expected:\n"' +
                expected_help + '"; got:\n"' +
                actual_help + '"\n')

# -- Test make_option() aka Option -------------------------------------

# It's sio necessary to test correct options here.  All the tests kwenye the
# parser.parse_args() section deal ukijumuisha those, because they're needed
# there.

kundi TestOptionChecks(BaseTest):
    eleza setUp(self):
        self.parser = OptionParser(usage=SUPPRESS_USAGE)

    eleza assertOptionError(self, expected_message, args=[], kwargs={}):
        self.assertRaises(make_option, args, kwargs,
                          OptionError, expected_message)

    eleza test_opt_string_empty(self):
        self.assertTypeError(make_option,
                             "at least one option string must be supplied")

    eleza test_opt_string_too_short(self):
        self.assertOptionError(
            "invalid option string 'b': must be at least two characters long",
            ["b"])

    eleza test_opt_string_short_invalid(self):
        self.assertOptionError(
            "invalid short option string '--': must be "
            "of the form -x, (x any non-dash char)",
            ["--"])

    eleza test_opt_string_long_invalid(self):
        self.assertOptionError(
            "invalid long option string '---': "
            "must start ukijumuisha --, followed by non-dash",
            ["---"])

    eleza test_attr_invalid(self):
        self.assertOptionError(
            "option -b: invalid keyword arguments: bar, foo",
            ["-b"], {'foo': Tupu, 'bar': Tupu})

    eleza test_action_invalid(self):
        self.assertOptionError(
            "option -b: invalid action: 'foo'",
            ["-b"], {'action': 'foo'})

    eleza test_type_invalid(self):
        self.assertOptionError(
            "option -b: invalid option type: 'foo'",
            ["-b"], {'type': 'foo'})
        self.assertOptionError(
            "option -b: invalid option type: 'tuple'",
            ["-b"], {'type': tuple})

    eleza test_no_type_for_action(self):
        self.assertOptionError(
            "option -b: must sio supply a type kila action 'count'",
            ["-b"], {'action': 'count', 'type': 'int'})

    eleza test_no_choices_list(self):
        self.assertOptionError(
            "option -b/--bad: must supply a list of "
            "choices kila type 'choice'",
            ["-b", "--bad"], {'type': "choice"})

    eleza test_bad_choices_list(self):
        typename = type('').__name__
        self.assertOptionError(
            "option -b/--bad: choices must be a list of "
            "strings ('%s' supplied)" % typename,
            ["-b", "--bad"],
            {'type': "choice", 'choices':"bad choices"})

    eleza test_no_choices_for_type(self):
        self.assertOptionError(
            "option -b: must sio supply choices kila type 'int'",
            ["-b"], {'type': 'int', 'choices':"bad"})

    eleza test_no_const_for_action(self):
        self.assertOptionError(
            "option -b: 'const' must sio be supplied kila action 'store'",
            ["-b"], {'action': 'store', 'const': 1})

    eleza test_no_nargs_for_action(self):
        self.assertOptionError(
            "option -b: 'nargs' must sio be supplied kila action 'count'",
            ["-b"], {'action': 'count', 'nargs': 2})

    eleza test_callback_not_callable(self):
        self.assertOptionError(
            "option -b: callback sio callable: 'foo'",
            ["-b"], {'action': 'callback',
                     'callback': 'foo'})

    eleza dummy(self):
        pass

    eleza test_callback_args_no_tuple(self):
        self.assertOptionError(
            "option -b: callback_args, ikiwa supplied, "
            "must be a tuple: sio 'foo'",
            ["-b"], {'action': 'callback',
                     'callback': self.dummy,
                     'callback_args': 'foo'})

    eleza test_callback_kwargs_no_dict(self):
        self.assertOptionError(
            "option -b: callback_kwargs, ikiwa supplied, "
            "must be a dict: sio 'foo'",
            ["-b"], {'action': 'callback',
                     'callback': self.dummy,
                     'callback_kwargs': 'foo'})

    eleza test_no_callback_for_action(self):
        self.assertOptionError(
            "option -b: callback supplied ('foo') kila non-callback option",
            ["-b"], {'action': 'store',
                     'callback': 'foo'})

    eleza test_no_callback_args_for_action(self):
        self.assertOptionError(
            "option -b: callback_args supplied kila non-callback option",
            ["-b"], {'action': 'store',
                     'callback_args': 'foo'})

    eleza test_no_callback_kwargs_for_action(self):
        self.assertOptionError(
            "option -b: callback_kwargs supplied kila non-callback option",
            ["-b"], {'action': 'store',
                     'callback_kwargs': 'foo'})

    eleza test_no_single_dash(self):
        self.assertOptionError(
            "invalid long option string '-debug': "
            "must start ukijumuisha --, followed by non-dash",
            ["-debug"])

        self.assertOptionError(
            "option -d: invalid long option string '-debug': must start with"
            " --, followed by non-dash",
            ["-d", "-debug"])

        self.assertOptionError(
            "invalid long option string '-debug': "
            "must start ukijumuisha --, followed by non-dash",
            ["-debug", "--debug"])

kundi TestOptionParser(BaseTest):
    eleza setUp(self):
        self.parser = OptionParser()
        self.parser.add_option("-v", "--verbose", "-n", "--noisy",
                          action="store_true", dest="verbose")
        self.parser.add_option("-q", "--quiet", "--silent",
                          action="store_false", dest="verbose")

    eleza test_add_option_no_Option(self):
        self.assertTypeError(self.parser.add_option,
                             "not an Option instance: Tupu", Tupu)

    eleza test_add_option_invalid_arguments(self):
        self.assertTypeError(self.parser.add_option,
                             "invalid arguments", Tupu, Tupu)

    eleza test_get_option(self):
        opt1 = self.parser.get_option("-v")
        self.assertIsInstance(opt1, Option)
        self.assertEqual(opt1._short_opts, ["-v", "-n"])
        self.assertEqual(opt1._long_opts, ["--verbose", "--noisy"])
        self.assertEqual(opt1.action, "store_true")
        self.assertEqual(opt1.dest, "verbose")

    eleza test_get_option_equals(self):
        opt1 = self.parser.get_option("-v")
        opt2 = self.parser.get_option("--verbose")
        opt3 = self.parser.get_option("-n")
        opt4 = self.parser.get_option("--noisy")
        self.assertKweli(opt1 ni opt2 ni opt3 ni opt4)

    eleza test_has_option(self):
        self.assertKweli(self.parser.has_option("-v"))
        self.assertKweli(self.parser.has_option("--verbose"))

    eleza assertKweliremoved(self):
        self.assertKweli(self.parser.get_option("-v") ni Tupu)
        self.assertKweli(self.parser.get_option("--verbose") ni Tupu)
        self.assertKweli(self.parser.get_option("-n") ni Tupu)
        self.assertKweli(self.parser.get_option("--noisy") ni Tupu)

        self.assertUongo(self.parser.has_option("-v"))
        self.assertUongo(self.parser.has_option("--verbose"))
        self.assertUongo(self.parser.has_option("-n"))
        self.assertUongo(self.parser.has_option("--noisy"))

        self.assertKweli(self.parser.has_option("-q"))
        self.assertKweli(self.parser.has_option("--silent"))

    eleza test_remove_short_opt(self):
        self.parser.remove_option("-n")
        self.assertKweliremoved()

    eleza test_remove_long_opt(self):
        self.parser.remove_option("--verbose")
        self.assertKweliremoved()

    eleza test_remove_nonexistent(self):
        self.assertRaises(self.parser.remove_option, ('foo',), Tupu,
                          ValueError, "no such option 'foo'")

    @support.impl_detail('Relies on sys.getrefcount', cpython=Kweli)
    eleza test_refleak(self):
        # If an OptionParser ni carrying around a reference to a large
        # object, various cycles can prevent it kutoka being GC'd in
        # a timely fashion.  destroy() komas the cycles to ensure stuff
        # can be cleaned up.
        big_thing = [42]
        refcount = sys.getrefcount(big_thing)
        parser = OptionParser()
        parser.add_option("-a", "--aaarggh")
        parser.big_thing = big_thing

        parser.destroy()
        #self.assertEqual(refcount, sys.getrefcount(big_thing))
        toa parser
        self.assertEqual(refcount, sys.getrefcount(big_thing))


kundi TestOptionValues(BaseTest):
    eleza setUp(self):
        pass

    eleza test_basics(self):
        values = Values()
        self.assertEqual(vars(values), {})
        self.assertEqual(values, {})
        self.assertNotEqual(values, {"foo": "bar"})
        self.assertNotEqual(values, "")

        dict = {"foo": "bar", "baz": 42}
        values = Values(defaults=dict)
        self.assertEqual(vars(values), dict)
        self.assertEqual(values, dict)
        self.assertNotEqual(values, {"foo": "bar"})
        self.assertNotEqual(values, {})
        self.assertNotEqual(values, "")
        self.assertNotEqual(values, [])


kundi TestTypeAliases(BaseTest):
    eleza setUp(self):
        self.parser = OptionParser()

    eleza test_str_aliases_string(self):
        self.parser.add_option("-s", type="str")
        self.assertEqual(self.parser.get_option("-s").type, "string")

    eleza test_type_object(self):
        self.parser.add_option("-s", type=str)
        self.assertEqual(self.parser.get_option("-s").type, "string")
        self.parser.add_option("-x", type=int)
        self.assertEqual(self.parser.get_option("-x").type, "int")


# Custom type kila testing processing of default values.
_time_units = { 's' : 1, 'm' : 60, 'h' : 60*60, 'd' : 60*60*24 }

eleza _check_duration(option, opt, value):
    jaribu:
        ikiwa value[-1].isdigit():
            rudisha int(value)
        isipokua:
            rudisha int(value[:-1]) * _time_units[value[-1]]
    except (ValueError, IndexError):
         ashiria OptionValueError(
            'option %s: invalid duration: %r' % (opt, value))

kundi DurationOption(Option):
    TYPES = Option.TYPES + ('duration',)
    TYPE_CHECKER = copy.copy(Option.TYPE_CHECKER)
    TYPE_CHECKER['duration'] = _check_duration

kundi TestDefaultValues(BaseTest):
    eleza setUp(self):
        self.parser = OptionParser()
        self.parser.add_option("-v", "--verbose", default=Kweli)
        self.parser.add_option("-q", "--quiet", dest='verbose')
        self.parser.add_option("-n", type="int", default=37)
        self.parser.add_option("-m", type="int")
        self.parser.add_option("-s", default="foo")
        self.parser.add_option("-t")
        self.parser.add_option("-u", default=Tupu)
        self.expected = { 'verbose': Kweli,
                          'n': 37,
                          'm': Tupu,
                          's': "foo",
                          't': Tupu,
                          'u': Tupu }

    eleza test_basic_defaults(self):
        self.assertEqual(self.parser.get_default_values(), self.expected)

    eleza test_mixed_defaults_post(self):
        self.parser.set_defaults(n=42, m=-100)
        self.expected.update({'n': 42, 'm': -100})
        self.assertEqual(self.parser.get_default_values(), self.expected)

    eleza test_mixed_defaults_pre(self):
        self.parser.set_defaults(x="barf", y="blah")
        self.parser.add_option("-x", default="frob")
        self.parser.add_option("-y")

        self.expected.update({'x': "frob", 'y': "blah"})
        self.assertEqual(self.parser.get_default_values(), self.expected)

        self.parser.remove_option("-y")
        self.parser.add_option("-y", default=Tupu)
        self.expected.update({'y': Tupu})
        self.assertEqual(self.parser.get_default_values(), self.expected)

    eleza test_process_default(self):
        self.parser.option_kundi = DurationOption
        self.parser.add_option("-d", type="duration", default=300)
        self.parser.add_option("-e", type="duration", default="6m")
        self.parser.set_defaults(n="42")
        self.expected.update({'d': 300, 'e': 360, 'n': 42})
        self.assertEqual(self.parser.get_default_values(), self.expected)

        self.parser.set_process_default_values(Uongo)
        self.expected.update({'d': 300, 'e': "6m", 'n': "42"})
        self.assertEqual(self.parser.get_default_values(), self.expected)


kundi TestProgName(BaseTest):
    """
    Test that %prog expands to the right thing kwenye usage, version,
    na help strings.
    """

    eleza assertUsage(self, parser, expected_usage):
        self.assertEqual(parser.get_usage(), expected_usage)

    eleza assertVersion(self, parser, expected_version):
        self.assertEqual(parser.get_version(), expected_version)


    eleza test_default_progname(self):
        # Make sure that program name taken kutoka sys.argv[0] by default.
        save_argv = sys.argv[:]
        jaribu:
            sys.argv[0] = os.path.join("foo", "bar", "baz.py")
            parser = OptionParser("%prog ...", version="%prog 1.2")
            expected_usage = "Usage: baz.py ...\n"
            self.assertUsage(parser, expected_usage)
            self.assertVersion(parser, "baz.py 1.2")
            self.assertHelp(parser,
                            expected_usage + "\n" +
                            "Options:\n"
                            "  --version   show program's version number na exit\n"
                            "  -h, --help  show this help message na exit\n")
        mwishowe:
            sys.argv[:] = save_argv

    eleza test_custom_progname(self):
        parser = OptionParser(prog="thingy",
                              version="%prog 0.1",
                              usage="%prog arg arg")
        parser.remove_option("-h")
        parser.remove_option("--version")
        expected_usage = "Usage: thingy arg arg\n"
        self.assertUsage(parser, expected_usage)
        self.assertVersion(parser, "thingy 0.1")
        self.assertHelp(parser, expected_usage + "\n")


kundi TestExpandDefaults(BaseTest):
    eleza setUp(self):
        self.parser = OptionParser(prog="test")
        self.help_prefix = """\
Usage: test [options]

Options:
  -h, --help            show this help message na exit
"""
        self.file_help = "read kutoka FILE [default: %default]"
        self.expected_help_file = self.help_prefix + \
            "  -f FILE, --file=FILE  read kutoka FILE [default: foo.txt]\n"
        self.expected_help_none = self.help_prefix + \
            "  -f FILE, --file=FILE  read kutoka FILE [default: none]\n"

    eleza test_option_default(self):
        self.parser.add_option("-f", "--file",
                               default="foo.txt",
                               help=self.file_help)
        self.assertHelp(self.parser, self.expected_help_file)

    eleza test_parser_default_1(self):
        self.parser.add_option("-f", "--file",
                               help=self.file_help)
        self.parser.set_default('file', "foo.txt")
        self.assertHelp(self.parser, self.expected_help_file)

    eleza test_parser_default_2(self):
        self.parser.add_option("-f", "--file",
                               help=self.file_help)
        self.parser.set_defaults(file="foo.txt")
        self.assertHelp(self.parser, self.expected_help_file)

    eleza test_no_default(self):
        self.parser.add_option("-f", "--file",
                               help=self.file_help)
        self.assertHelp(self.parser, self.expected_help_none)

    eleza test_default_none_1(self):
        self.parser.add_option("-f", "--file",
                               default=Tupu,
                               help=self.file_help)
        self.assertHelp(self.parser, self.expected_help_none)

    eleza test_default_none_2(self):
        self.parser.add_option("-f", "--file",
                               help=self.file_help)
        self.parser.set_defaults(file=Tupu)
        self.assertHelp(self.parser, self.expected_help_none)

    eleza test_float_default(self):
        self.parser.add_option(
            "-p", "--prob",
            help="blow up ukijumuisha probability PROB [default: %default]")
        self.parser.set_defaults(prob=0.43)
        expected_help = self.help_prefix + \
            "  -p PROB, --prob=PROB  blow up ukijumuisha probability PROB [default: 0.43]\n"
        self.assertHelp(self.parser, expected_help)

    eleza test_alt_expand(self):
        self.parser.add_option("-f", "--file",
                               default="foo.txt",
                               help="read kutoka FILE [default: *DEFAULT*]")
        self.parser.formatter.default_tag = "*DEFAULT*"
        self.assertHelp(self.parser, self.expected_help_file)

    eleza test_no_expand(self):
        self.parser.add_option("-f", "--file",
                               default="foo.txt",
                               help="read kutoka %default file")
        self.parser.formatter.default_tag = Tupu
        expected_help = self.help_prefix + \
            "  -f FILE, --file=FILE  read kutoka %default file\n"
        self.assertHelp(self.parser, expected_help)


# -- Test parser.parse_args() ------------------------------------------

kundi TestStandard(BaseTest):
    eleza setUp(self):
        options = [make_option("-a", type="string"),
                   make_option("-b", "--boo", type="int", dest='boo'),
                   make_option("--foo", action="append")]

        self.parser = InterceptingOptionParser(usage=SUPPRESS_USAGE,
                                               option_list=options)

    eleza test_required_value(self):
        self.assertParseFail(["-a"], "-a option requires 1 argument")

    eleza test_invalid_integer(self):
        self.assertParseFail(["-b", "5x"],
                             "option -b: invalid integer value: '5x'")

    eleza test_no_such_option(self):
        self.assertParseFail(["--boo13"], "no such option: --boo13")

    eleza test_long_invalid_integer(self):
        self.assertParseFail(["--boo=x5"],
                             "option --boo: invalid integer value: 'x5'")

    eleza test_empty(self):
        self.assertParseOK([], {'a': Tupu, 'boo': Tupu, 'foo': Tupu}, [])

    eleza test_shortopt_empty_longopt_append(self):
        self.assertParseOK(["-a", "", "--foo=blah", "--foo="],
                           {'a': "", 'boo': Tupu, 'foo': ["blah", ""]},
                           [])

    eleza test_long_option_append(self):
        self.assertParseOK(["--foo", "bar", "--foo", "", "--foo=x"],
                           {'a': Tupu,
                            'boo': Tupu,
                            'foo': ["bar", "", "x"]},
                           [])

    eleza test_option_argument_joined(self):
        self.assertParseOK(["-abc"],
                           {'a': "bc", 'boo': Tupu, 'foo': Tupu},
                           [])

    eleza test_option_argument_split(self):
        self.assertParseOK(["-a", "34"],
                           {'a': "34", 'boo': Tupu, 'foo': Tupu},
                           [])

    eleza test_option_argument_joined_integer(self):
        self.assertParseOK(["-b34"],
                           {'a': Tupu, 'boo': 34, 'foo': Tupu},
                           [])

    eleza test_option_argument_split_negative_integer(self):
        self.assertParseOK(["-b", "-5"],
                           {'a': Tupu, 'boo': -5, 'foo': Tupu},
                           [])

    eleza test_long_option_argument_joined(self):
        self.assertParseOK(["--boo=13"],
                           {'a': Tupu, 'boo': 13, 'foo': Tupu},
                           [])

    eleza test_long_option_argument_split(self):
        self.assertParseOK(["--boo", "111"],
                           {'a': Tupu, 'boo': 111, 'foo': Tupu},
                           [])

    eleza test_long_option_short_option(self):
        self.assertParseOK(["--foo=bar", "-axyz"],
                           {'a': 'xyz', 'boo': Tupu, 'foo': ["bar"]},
                           [])

    eleza test_abbrev_long_option(self):
        self.assertParseOK(["--f=bar", "-axyz"],
                           {'a': 'xyz', 'boo': Tupu, 'foo': ["bar"]},
                           [])

    eleza test_defaults(self):
        (options, args) = self.parser.parse_args([])
        defaults = self.parser.get_default_values()
        self.assertEqual(vars(defaults), vars(options))

    eleza test_ambiguous_option(self):
        self.parser.add_option("--foz", action="store",
                               type="string", dest="foo")
        self.assertParseFail(["--f=bar"],
                             "ambiguous option: --f (--foo, --foz?)")


    eleza test_short_and_long_option_split(self):
        self.assertParseOK(["-a", "xyz", "--foo", "bar"],
                           {'a': 'xyz', 'boo': Tupu, 'foo': ["bar"]},
                           [])

    eleza test_short_option_split_long_option_append(self):
        self.assertParseOK(["--foo=bar", "-b", "123", "--foo", "baz"],
                           {'a': Tupu, 'boo': 123, 'foo': ["bar", "baz"]},
                           [])

    eleza test_short_option_split_one_positional_arg(self):
        self.assertParseOK(["-a", "foo", "bar"],
                           {'a': "foo", 'boo': Tupu, 'foo': Tupu},
                           ["bar"])

    eleza test_short_option_consumes_separator(self):
        self.assertParseOK(["-a", "--", "foo", "bar"],
                           {'a': "--", 'boo': Tupu, 'foo': Tupu},
                           ["foo", "bar"])
        self.assertParseOK(["-a", "--", "--foo", "bar"],
                           {'a': "--", 'boo': Tupu, 'foo': ["bar"]},
                           [])

    eleza test_short_option_joined_and_separator(self):
        self.assertParseOK(["-ab", "--", "--foo", "bar"],
                           {'a': "b", 'boo': Tupu, 'foo': Tupu},
                           ["--foo", "bar"]),

    eleza test_hyphen_becomes_positional_arg(self):
        self.assertParseOK(["-ab", "-", "--foo", "bar"],
                           {'a': "b", 'boo': Tupu, 'foo': ["bar"]},
                           ["-"])

    eleza test_no_append_versus_append(self):
        self.assertParseOK(["-b3", "-b", "5", "--foo=bar", "--foo", "baz"],
                           {'a': Tupu, 'boo': 5, 'foo': ["bar", "baz"]},
                           [])

    eleza test_option_consumes_optionlike_string(self):
        self.assertParseOK(["-a", "-b3"],
                           {'a': "-b3", 'boo': Tupu, 'foo': Tupu},
                           [])

    eleza test_combined_single_invalid_option(self):
        self.parser.add_option("-t", action="store_true")
        self.assertParseFail(["-test"],
                             "no such option: -e")

kundi TestBool(BaseTest):
    eleza setUp(self):
        options = [make_option("-v",
                               "--verbose",
                               action="store_true",
                               dest="verbose",
                               default=''),
                   make_option("-q",
                               "--quiet",
                               action="store_false",
                               dest="verbose")]
        self.parser = OptionParser(option_list = options)

    eleza test_bool_default(self):
        self.assertParseOK([],
                           {'verbose': ''},
                           [])

    eleza test_bool_false(self):
        (options, args) = self.assertParseOK(["-q"],
                                             {'verbose': 0},
                                             [])
        self.assertKweli(options.verbose ni Uongo)

    eleza test_bool_true(self):
        (options, args) = self.assertParseOK(["-v"],
                                             {'verbose': 1},
                                             [])
        self.assertKweli(options.verbose ni Kweli)

    eleza test_bool_flicker_on_and_off(self):
        self.assertParseOK(["-qvq", "-q", "-v"],
                           {'verbose': 1},
                           [])

kundi TestChoice(BaseTest):
    eleza setUp(self):
        self.parser = InterceptingOptionParser(usage=SUPPRESS_USAGE)
        self.parser.add_option("-c", action="store", type="choice",
                               dest="choice", choices=["one", "two", "three"])

    eleza test_valid_choice(self):
        self.assertParseOK(["-c", "one", "xyz"],
                           {'choice': 'one'},
                           ["xyz"])

    eleza test_invalid_choice(self):
        self.assertParseFail(["-c", "four", "abc"],
                             "option -c: invalid choice: 'four' "
                             "(choose kutoka 'one', 'two', 'three')")

    eleza test_add_choice_option(self):
        self.parser.add_option("-d", "--default",
                               choices=["four", "five", "six"])
        opt = self.parser.get_option("-d")
        self.assertEqual(opt.type, "choice")
        self.assertEqual(opt.action, "store")

kundi TestCount(BaseTest):
    eleza setUp(self):
        self.parser = InterceptingOptionParser(usage=SUPPRESS_USAGE)
        self.v_opt = make_option("-v", action="count", dest="verbose")
        self.parser.add_option(self.v_opt)
        self.parser.add_option("--verbose", type="int", dest="verbose")
        self.parser.add_option("-q", "--quiet",
                               action="store_const", dest="verbose", const=0)

    eleza test_empty(self):
        self.assertParseOK([], {'verbose': Tupu}, [])

    eleza test_count_one(self):
        self.assertParseOK(["-v"], {'verbose': 1}, [])

    eleza test_count_three(self):
        self.assertParseOK(["-vvv"], {'verbose': 3}, [])

    eleza test_count_three_apart(self):
        self.assertParseOK(["-v", "-v", "-v"], {'verbose': 3}, [])

    eleza test_count_override_amount(self):
        self.assertParseOK(["-vvv", "--verbose=2"], {'verbose': 2}, [])

    eleza test_count_override_quiet(self):
        self.assertParseOK(["-vvv", "--verbose=2", "-q"], {'verbose': 0}, [])

    eleza test_count_overriding(self):
        self.assertParseOK(["-vvv", "--verbose=2", "-q", "-v"],
                           {'verbose': 1}, [])

    eleza test_count_interspersed_args(self):
        self.assertParseOK(["--quiet", "3", "-v"],
                           {'verbose': 1},
                           ["3"])

    eleza test_count_no_interspersed_args(self):
        self.parser.disable_interspersed_args()
        self.assertParseOK(["--quiet", "3", "-v"],
                           {'verbose': 0},
                           ["3", "-v"])

    eleza test_count_no_such_option(self):
        self.assertParseFail(["-q3", "-v"], "no such option: -3")

    eleza test_count_option_no_value(self):
        self.assertParseFail(["--quiet=3", "-v"],
                             "--quiet option does sio take a value")

    eleza test_count_with_default(self):
        self.parser.set_default('verbose', 0)
        self.assertParseOK([], {'verbose':0}, [])

    eleza test_count_overriding_default(self):
        self.parser.set_default('verbose', 0)
        self.assertParseOK(["-vvv", "--verbose=2", "-q", "-v"],
                           {'verbose': 1}, [])

kundi TestMultipleArgs(BaseTest):
    eleza setUp(self):
        self.parser = InterceptingOptionParser(usage=SUPPRESS_USAGE)
        self.parser.add_option("-p", "--point",
                               action="store", nargs=3, type="float", dest="point")

    eleza test_nargs_with_positional_args(self):
        self.assertParseOK(["foo", "-p", "1", "2.5", "-4.3", "xyz"],
                           {'point': (1.0, 2.5, -4.3)},
                           ["foo", "xyz"])

    eleza test_nargs_long_opt(self):
        self.assertParseOK(["--point", "-1", "2.5", "-0", "xyz"],
                           {'point': (-1.0, 2.5, -0.0)},
                           ["xyz"])

    eleza test_nargs_invalid_float_value(self):
        self.assertParseFail(["-p", "1.0", "2x", "3.5"],
                             "option -p: "
                             "invalid floating-point value: '2x'")

    eleza test_nargs_required_values(self):
        self.assertParseFail(["--point", "1.0", "3.5"],
                             "--point option requires 3 arguments")

kundi TestMultipleArgsAppend(BaseTest):
    eleza setUp(self):
        self.parser = InterceptingOptionParser(usage=SUPPRESS_USAGE)
        self.parser.add_option("-p", "--point", action="store", nargs=3,
                               type="float", dest="point")
        self.parser.add_option("-f", "--foo", action="append", nargs=2,
                               type="int", dest="foo")
        self.parser.add_option("-z", "--zero", action="append_const",
                               dest="foo", const=(0, 0))

    eleza test_nargs_append(self):
        self.assertParseOK(["-f", "4", "-3", "blah", "--foo", "1", "666"],
                           {'point': Tupu, 'foo': [(4, -3), (1, 666)]},
                           ["blah"])

    eleza test_nargs_append_required_values(self):
        self.assertParseFail(["-f4,3"],
                             "-f option requires 2 arguments")

    eleza test_nargs_append_simple(self):
        self.assertParseOK(["--foo=3", "4"],
                           {'point': Tupu, 'foo':[(3, 4)]},
                           [])

    eleza test_nargs_append_const(self):
        self.assertParseOK(["--zero", "--foo", "3", "4", "-z"],
                           {'point': Tupu, 'foo':[(0, 0), (3, 4), (0, 0)]},
                           [])

kundi TestVersion(BaseTest):
    eleza test_version(self):
        self.parser = InterceptingOptionParser(usage=SUPPRESS_USAGE,
                                               version="%prog 0.1")
        save_argv = sys.argv[:]
        jaribu:
            sys.argv[0] = os.path.join(os.curdir, "foo", "bar")
            self.assertOutput(["--version"], "bar 0.1\n")
        mwishowe:
            sys.argv[:] = save_argv

    eleza test_no_version(self):
        self.parser = InterceptingOptionParser(usage=SUPPRESS_USAGE)
        self.assertParseFail(["--version"],
                             "no such option: --version")

# -- Test conflicting default values na parser.parse_args() -----------

kundi TestConflictingDefaults(BaseTest):
    """Conflicting default values: the last one should win."""
    eleza setUp(self):
        self.parser = OptionParser(option_list=[
            make_option("-v", action="store_true", dest="verbose", default=1)])

    eleza test_conflict_default(self):
        self.parser.add_option("-q", action="store_false", dest="verbose",
                               default=0)
        self.assertParseOK([], {'verbose': 0}, [])

    eleza test_conflict_default_none(self):
        self.parser.add_option("-q", action="store_false", dest="verbose",
                               default=Tupu)
        self.assertParseOK([], {'verbose': Tupu}, [])

kundi TestOptionGroup(BaseTest):
    eleza setUp(self):
        self.parser = OptionParser(usage=SUPPRESS_USAGE)

    eleza test_option_group_create_instance(self):
        group = OptionGroup(self.parser, "Spam")
        self.parser.add_option_group(group)
        group.add_option("--spam", action="store_true",
                         help="spam spam spam spam")
        self.assertParseOK(["--spam"], {'spam': 1}, [])

    eleza test_add_group_no_group(self):
        self.assertTypeError(self.parser.add_option_group,
                             "not an OptionGroup instance: Tupu", Tupu)

    eleza test_add_group_invalid_arguments(self):
        self.assertTypeError(self.parser.add_option_group,
                             "invalid arguments", Tupu, Tupu)

    eleza test_add_group_wrong_parser(self):
        group = OptionGroup(self.parser, "Spam")
        group.parser = OptionParser()
        self.assertRaises(self.parser.add_option_group, (group,), Tupu,
                          ValueError, "invalid OptionGroup (wrong parser)")

    eleza test_group_manipulate(self):
        group = self.parser.add_option_group("Group 2",
                                             description="Some more options")
        group.set_title("Bacon")
        group.add_option("--bacon", type="int")
        self.assertKweli(self.parser.get_option_group("--bacon"), group)

# -- Test extending na parser.parse_args() ----------------------------

kundi TestExtendAddTypes(BaseTest):
    eleza setUp(self):
        self.parser = InterceptingOptionParser(usage=SUPPRESS_USAGE,
                                               option_class=self.MyOption)
        self.parser.add_option("-a", Tupu, type="string", dest="a")
        self.parser.add_option("-f", "--file", type="file", dest="file")

    eleza tearDown(self):
        ikiwa os.path.isdir(support.TESTFN):
            os.rmdir(support.TESTFN)
        elikiwa os.path.isfile(support.TESTFN):
            os.unlink(support.TESTFN)

    kundi MyOption (Option):
        eleza check_file(option, opt, value):
            ikiwa sio os.path.exists(value):
                 ashiria OptionValueError("%s: file does sio exist" % value)
            elikiwa sio os.path.isfile(value):
                 ashiria OptionValueError("%s: sio a regular file" % value)
            rudisha value

        TYPES = Option.TYPES + ("file",)
        TYPE_CHECKER = copy.copy(Option.TYPE_CHECKER)
        TYPE_CHECKER["file"] = check_file

    eleza test_filetype_ok(self):
        support.create_empty_file(support.TESTFN)
        self.assertParseOK(["--file", support.TESTFN, "-afoo"],
                           {'file': support.TESTFN, 'a': 'foo'},
                           [])

    eleza test_filetype_noexist(self):
        self.assertParseFail(["--file", support.TESTFN, "-afoo"],
                             "%s: file does sio exist" %
                             support.TESTFN)

    eleza test_filetype_notfile(self):
        os.mkdir(support.TESTFN)
        self.assertParseFail(["--file", support.TESTFN, "-afoo"],
                             "%s: sio a regular file" %
                             support.TESTFN)


kundi TestExtendAddActions(BaseTest):
    eleza setUp(self):
        options = [self.MyOption("-a", "--apple", action="extend",
                                 type="string", dest="apple")]
        self.parser = OptionParser(option_list=options)

    kundi MyOption (Option):
        ACTIONS = Option.ACTIONS + ("extend",)
        STORE_ACTIONS = Option.STORE_ACTIONS + ("extend",)
        TYPED_ACTIONS = Option.TYPED_ACTIONS + ("extend",)

        eleza take_action(self, action, dest, opt, value, values, parser):
            ikiwa action == "extend":
                lvalue = value.split(",")
                values.ensure_value(dest, []).extend(lvalue)
            isipokua:
                Option.take_action(self, action, dest, opt, parser, value,
                                   values)

    eleza test_extend_add_action(self):
        self.assertParseOK(["-afoo,bar", "--apple=blah"],
                           {'apple': ["foo", "bar", "blah"]},
                           [])

    eleza test_extend_add_action_normal(self):
        self.assertParseOK(["-a", "foo", "-abar", "--apple=x,y"],
                           {'apple': ["foo", "bar", "x", "y"]},
                           [])

# -- Test callbacks na parser.parse_args() ----------------------------

kundi TestCallback(BaseTest):
    eleza setUp(self):
        options = [make_option("-x",
                               Tupu,
                               action="callback",
                               callback=self.process_opt),
                   make_option("-f",
                               "--file",
                               action="callback",
                               callback=self.process_opt,
                               type="string",
                               dest="filename")]
        self.parser = OptionParser(option_list=options)

    eleza process_opt(self, option, opt, value, parser_):
        ikiwa opt == "-x":
            self.assertEqual(option._short_opts, ["-x"])
            self.assertEqual(option._long_opts, [])
            self.assertKweli(parser_ ni self.parser)
            self.assertKweli(value ni Tupu)
            self.assertEqual(vars(parser_.values), {'filename': Tupu})

            parser_.values.x = 42
        elikiwa opt == "--file":
            self.assertEqual(option._short_opts, ["-f"])
            self.assertEqual(option._long_opts, ["--file"])
            self.assertKweli(parser_ ni self.parser)
            self.assertEqual(value, "foo")
            self.assertEqual(vars(parser_.values), {'filename': Tupu, 'x': 42})

            setattr(parser_.values, option.dest, value)
        isipokua:
            self.fail("Unknown option %r kwenye process_opt." % opt)

    eleza test_callback(self):
        self.assertParseOK(["-x", "--file=foo"],
                           {'filename': "foo", 'x': 42},
                           [])

    eleza test_callback_help(self):
        # This test was prompted by SF bug #960515 -- the point is
        # sio to inspect the help text, just to make sure that
        # format_help() doesn't crash.
        parser = OptionParser(usage=SUPPRESS_USAGE)
        parser.remove_option("-h")
        parser.add_option("-t", "--test", action="callback",
                          callback=lambda: Tupu, type="string",
                          help="foo")

        expected_help = ("Options:\n"
                         "  -t TEST, --test=TEST  foo\n")
        self.assertHelp(parser, expected_help)


kundi TestCallbackExtraArgs(BaseTest):
    eleza setUp(self):
        options = [make_option("-p", "--point", action="callback",
                               callback=self.process_tuple,
                               callback_args=(3, int), type="string",
                               dest="points", default=[])]
        self.parser = OptionParser(option_list=options)

    eleza process_tuple(self, option, opt, value, parser_, len, type):
        self.assertEqual(len, 3)
        self.assertKweli(type ni int)

        ikiwa opt == "-p":
            self.assertEqual(value, "1,2,3")
        elikiwa opt == "--point":
            self.assertEqual(value, "4,5,6")

        value = tuple(map(type, value.split(",")))
        getattr(parser_.values, option.dest).append(value)

    eleza test_callback_extra_args(self):
        self.assertParseOK(["-p1,2,3", "--point", "4,5,6"],
                           {'points': [(1,2,3), (4,5,6)]},
                           [])

kundi TestCallbackMeddleArgs(BaseTest):
    eleza setUp(self):
        options = [make_option(str(x), action="callback",
                               callback=self.process_n, dest='things')
                   kila x kwenye range(-1, -6, -1)]
        self.parser = OptionParser(option_list=options)

    # Callback that meddles kwenye rargs, largs
    eleza process_n(self, option, opt, value, parser_):
        # option ni -3, -5, etc.
        nargs = int(opt[1:])
        rargs = parser_.rargs
        ikiwa len(rargs) < nargs:
            self.fail("Expected %d arguments kila %s option." % (nargs, opt))
        dest = parser_.values.ensure_value(option.dest, [])
        dest.append(tuple(rargs[0:nargs]))
        parser_.largs.append(nargs)
        toa rargs[0:nargs]

    eleza test_callback_meddle_args(self):
        self.assertParseOK(["-1", "foo", "-3", "bar", "baz", "qux"],
                           {'things': [("foo",), ("bar", "baz", "qux")]},
                           [1, 3])

    eleza test_callback_meddle_args_separator(self):
        self.assertParseOK(["-2", "foo", "--"],
                           {'things': [('foo', '--')]},
                           [2])

kundi TestCallbackManyArgs(BaseTest):
    eleza setUp(self):
        options = [make_option("-a", "--apple", action="callback", nargs=2,
                               callback=self.process_many, type="string"),
                   make_option("-b", "--bob", action="callback", nargs=3,
                               callback=self.process_many, type="int")]
        self.parser = OptionParser(option_list=options)

    eleza process_many(self, option, opt, value, parser_):
        ikiwa opt == "-a":
            self.assertEqual(value, ("foo", "bar"))
        elikiwa opt == "--apple":
            self.assertEqual(value, ("ding", "dong"))
        elikiwa opt == "-b":
            self.assertEqual(value, (1, 2, 3))
        elikiwa opt == "--bob":
            self.assertEqual(value, (-666, 42, 0))

    eleza test_many_args(self):
        self.assertParseOK(["-a", "foo", "bar", "--apple", "ding", "dong",
                            "-b", "1", "2", "3", "--bob", "-666", "42",
                            "0"],
                           {"apple": Tupu, "bob": Tupu},
                           [])

kundi TestCallbackCheckAbbrev(BaseTest):
    eleza setUp(self):
        self.parser = OptionParser()
        self.parser.add_option("--foo-bar", action="callback",
                               callback=self.check_abbrev)

    eleza check_abbrev(self, option, opt, value, parser):
        self.assertEqual(opt, "--foo-bar")

    eleza test_abbrev_callback_expansion(self):
        self.assertParseOK(["--foo"], {}, [])

kundi TestCallbackVarArgs(BaseTest):
    eleza setUp(self):
        options = [make_option("-a", type="int", nargs=2, dest="a"),
                   make_option("-b", action="store_true", dest="b"),
                   make_option("-c", "--callback", action="callback",
                               callback=self.variable_args, dest="c")]
        self.parser = InterceptingOptionParser(usage=SUPPRESS_USAGE,
                                               option_list=options)

    eleza variable_args(self, option, opt, value, parser):
        self.assertKweli(value ni Tupu)
        value = []
        rargs = parser.rargs
        wakati rargs:
            arg = rargs[0]
            ikiwa ((arg[:2] == "--" na len(arg) > 2) or
                (arg[:1] == "-" na len(arg) > 1 na arg[1] != "-")):
                koma
            isipokua:
                value.append(arg)
                toa rargs[0]
        setattr(parser.values, option.dest, value)

    eleza test_variable_args(self):
        self.assertParseOK(["-a3", "-5", "--callback", "foo", "bar"],
                           {'a': (3, -5), 'b': Tupu, 'c': ["foo", "bar"]},
                           [])

    eleza test_consume_separator_stop_at_option(self):
        self.assertParseOK(["-c", "37", "--", "xxx", "-b", "hello"],
                           {'a': Tupu,
                            'b': Kweli,
                            'c': ["37", "--", "xxx"]},
                           ["hello"])

    eleza test_positional_arg_and_variable_args(self):
        self.assertParseOK(["hello", "-c", "foo", "-", "bar"],
                           {'a': Tupu,
                            'b': Tupu,
                            'c':["foo", "-", "bar"]},
                           ["hello"])

    eleza test_stop_at_option(self):
        self.assertParseOK(["-c", "foo", "-b"],
                           {'a': Tupu, 'b': Kweli, 'c': ["foo"]},
                           [])

    eleza test_stop_at_invalid_option(self):
        self.assertParseFail(["-c", "3", "-5", "-a"], "no such option: -5")


# -- Test conflict handling na parser.parse_args() --------------------

kundi ConflictBase(BaseTest):
    eleza setUp(self):
        options = [make_option("-v", "--verbose", action="count",
                               dest="verbose", help="increment verbosity")]
        self.parser = InterceptingOptionParser(usage=SUPPRESS_USAGE,
                                               option_list=options)

    eleza show_version(self, option, opt, value, parser):
        parser.values.show_version = 1

kundi TestConflict(ConflictBase):
    """Use the default conflict resolution kila Optik 1.2: error."""
    eleza assertKweliconflict_error(self, func):
        err = self.assertRaises(
            func, ("-v", "--version"), {'action' : "callback",
                                        'callback' : self.show_version,
                                        'help' : "show version"},
            OptionConflictError,
            "option -v/--version: conflicting option string(s): -v")

        self.assertEqual(err.msg, "conflicting option string(s): -v")
        self.assertEqual(err.option_id, "-v/--version")

    eleza test_conflict_error(self):
        self.assertKweliconflict_error(self.parser.add_option)

    eleza test_conflict_error_group(self):
        group = OptionGroup(self.parser, "Group 1")
        self.assertKweliconflict_error(group.add_option)

    eleza test_no_such_conflict_handler(self):
        self.assertRaises(
            self.parser.set_conflict_handler, ('foo',), Tupu,
            ValueError, "invalid conflict_resolution value 'foo'")


kundi TestConflictResolve(ConflictBase):
    eleza setUp(self):
        ConflictBase.setUp(self)
        self.parser.set_conflict_handler("resolve")
        self.parser.add_option("-v", "--version", action="callback",
                               callback=self.show_version, help="show version")

    eleza test_conflict_resolve(self):
        v_opt = self.parser.get_option("-v")
        verbose_opt = self.parser.get_option("--verbose")
        version_opt = self.parser.get_option("--version")

        self.assertKweli(v_opt ni version_opt)
        self.assertKweli(v_opt ni sio verbose_opt)
        self.assertEqual(v_opt._long_opts, ["--version"])
        self.assertEqual(version_opt._short_opts, ["-v"])
        self.assertEqual(version_opt._long_opts, ["--version"])
        self.assertEqual(verbose_opt._short_opts, [])
        self.assertEqual(verbose_opt._long_opts, ["--verbose"])

    eleza test_conflict_resolve_help(self):
        self.assertOutput(["-h"], """\
Options:
  --verbose      increment verbosity
  -h, --help     show this help message na exit
  -v, --version  show version
""")

    eleza test_conflict_resolve_short_opt(self):
        self.assertParseOK(["-v"],
                           {'verbose': Tupu, 'show_version': 1},
                           [])

    eleza test_conflict_resolve_long_opt(self):
        self.assertParseOK(["--verbose"],
                           {'verbose': 1},
                           [])

    eleza test_conflict_resolve_long_opts(self):
        self.assertParseOK(["--verbose", "--version"],
                           {'verbose': 1, 'show_version': 1},
                           [])

kundi TestConflictOverride(BaseTest):
    eleza setUp(self):
        self.parser = InterceptingOptionParser(usage=SUPPRESS_USAGE)
        self.parser.set_conflict_handler("resolve")
        self.parser.add_option("-n", "--dry-run",
                               action="store_true", dest="dry_run",
                               help="don't do anything")
        self.parser.add_option("--dry-run", "-n",
                               action="store_const", const=42, dest="dry_run",
                               help="dry run mode")

    eleza test_conflict_override_opts(self):
        opt = self.parser.get_option("--dry-run")
        self.assertEqual(opt._short_opts, ["-n"])
        self.assertEqual(opt._long_opts, ["--dry-run"])

    eleza test_conflict_override_help(self):
        self.assertOutput(["-h"], """\
Options:
  -h, --help     show this help message na exit
  -n, --dry-run  dry run mode
""")

    eleza test_conflict_override_args(self):
        self.assertParseOK(["-n"],
                           {'dry_run': 42},
                           [])

# -- Other testing. ----------------------------------------------------

_expected_help_basic = """\
Usage: bar.py [options]

Options:
  -a APPLE           throw APPLEs at basket
  -b NUM, --boo=NUM  shout "boo!" NUM times (in order to frighten away all the
                     evil spirits that cause trouble na mayhem)
  --foo=FOO          store FOO kwenye the foo list kila later fooing
  -h, --help         show this help message na exit
"""

_expected_help_long_opts_first = """\
Usage: bar.py [options]

Options:
  -a APPLE           throw APPLEs at basket
  --boo=NUM, -b NUM  shout "boo!" NUM times (in order to frighten away all the
                     evil spirits that cause trouble na mayhem)
  --foo=FOO          store FOO kwenye the foo list kila later fooing
  --help, -h         show this help message na exit
"""

_expected_help_title_formatter = """\
Usage
=====
  bar.py [options]

Options
=======
-a APPLE           throw APPLEs at basket
--boo=NUM, -b NUM  shout "boo!" NUM times (in order to frighten away all the
                   evil spirits that cause trouble na mayhem)
--foo=FOO          store FOO kwenye the foo list kila later fooing
--help, -h         show this help message na exit
"""

_expected_help_short_lines = """\
Usage: bar.py [options]

Options:
  -a APPLE           throw APPLEs at basket
  -b NUM, --boo=NUM  shout "boo!" NUM times (in order to
                     frighten away all the evil spirits
                     that cause trouble na mayhem)
  --foo=FOO          store FOO kwenye the foo list kila later
                     fooing
  -h, --help         show this help message na exit
"""

_expected_very_help_short_lines = """\
Usage: bar.py [options]

Options:
  -a APPLE
    throw
    APPLEs at
    basket
  -b NUM, --boo=NUM
    shout
    "boo!" NUM
    times (in
    order to
    frighten
    away all
    the evil
    spirits
    that cause
    trouble and
    mayhem)
  --foo=FOO
    store FOO
    kwenye the foo
    list for
    later
    fooing
  -h, --help
    show this
    help
    message and
    exit
"""

kundi TestHelp(BaseTest):
    eleza setUp(self):
        self.parser = self.make_parser(80)

    eleza make_parser(self, columns):
        options = [
            make_option("-a", type="string", dest='a',
                        metavar="APPLE", help="throw APPLEs at basket"),
            make_option("-b", "--boo", type="int", dest='boo',
                        metavar="NUM",
                        help=
                        "shout \"boo!\" NUM times (in order to frighten away "
                        "all the evil spirits that cause trouble na mayhem)"),
            make_option("--foo", action="append", type="string", dest='foo',
                        help="store FOO kwenye the foo list kila later fooing"),
            ]

        # We need to set COLUMNS kila the OptionParser constructor, but
        # we must restore its original value -- otherwise, this test
        # screws things up kila other tests when it's part of the Python
        # test suite.
        ukijumuisha support.EnvironmentVarGuard() as env:
            env['COLUMNS'] = str(columns)
            rudisha InterceptingOptionParser(option_list=options)

    eleza assertHelpEquals(self, expected_output):
        save_argv = sys.argv[:]
        jaribu:
            # Make optparse believe bar.py ni being executed.
            sys.argv[0] = os.path.join("foo", "bar.py")
            self.assertOutput(["-h"], expected_output)
        mwishowe:
            sys.argv[:] = save_argv

    eleza test_help(self):
        self.assertHelpEquals(_expected_help_basic)

    eleza test_help_old_usage(self):
        self.parser.set_usage("Usage: %prog [options]")
        self.assertHelpEquals(_expected_help_basic)

    eleza test_help_long_opts_first(self):
        self.parser.formatter.short_first = 0
        self.assertHelpEquals(_expected_help_long_opts_first)

    eleza test_help_title_formatter(self):
        ukijumuisha support.EnvironmentVarGuard() as env:
            env["COLUMNS"] = "80"
            self.parser.formatter = TitledHelpFormatter()
            self.assertHelpEquals(_expected_help_title_formatter)

    eleza test_wrap_columns(self):
        # Ensure that wrapping respects $COLUMNS environment variable.
        # Need to reconstruct the parser, since that's the only time
        # we look at $COLUMNS.
        self.parser = self.make_parser(60)
        self.assertHelpEquals(_expected_help_short_lines)
        self.parser = self.make_parser(0)
        self.assertHelpEquals(_expected_very_help_short_lines)

    eleza test_help_unicode(self):
        self.parser = InterceptingOptionParser(usage=SUPPRESS_USAGE)
        self.parser.add_option("-a", action="store_true", help="ol\u00E9!")
        expect = """\
Options:
  -h, --help  show this help message na exit
  -a          ol\u00E9!
"""
        self.assertHelpEquals(expect)

    eleza test_help_unicode_description(self):
        self.parser = InterceptingOptionParser(usage=SUPPRESS_USAGE,
                                               description="ol\u00E9!")
        expect = """\
ol\u00E9!

Options:
  -h, --help  show this help message na exit
"""
        self.assertHelpEquals(expect)

    eleza test_help_description_groups(self):
        self.parser.set_description(
            "This ni the program description kila %prog.  %prog has "
            "an option group as well as single options.")

        group = OptionGroup(
            self.parser, "Dangerous Options",
            "Caution: use of these options ni at your own risk.  "
            "It ni believed that some of them bite.")
        group.add_option("-g", action="store_true", help="Group option.")
        self.parser.add_option_group(group)

        expect = """\
Usage: bar.py [options]

This ni the program description kila bar.py.  bar.py has an option group as
well as single options.

Options:
  -a APPLE           throw APPLEs at basket
  -b NUM, --boo=NUM  shout "boo!" NUM times (in order to frighten away all the
                     evil spirits that cause trouble na mayhem)
  --foo=FOO          store FOO kwenye the foo list kila later fooing
  -h, --help         show this help message na exit

  Dangerous Options:
    Caution: use of these options ni at your own risk.  It ni believed
    that some of them bite.

    -g               Group option.
"""

        self.assertHelpEquals(expect)

        self.parser.epilog = "Please report bugs to /dev/null."
        self.assertHelpEquals(expect + "\nPlease report bugs to /dev/null.\n")


kundi TestMatchAbbrev(BaseTest):
    eleza test_match_abbrev(self):
        self.assertEqual(_match_abbrev("--f",
                                       {"--foz": Tupu,
                                        "--foo": Tupu,
                                        "--fie": Tupu,
                                        "--f": Tupu}),
                         "--f")

    eleza test_match_abbrev_error(self):
        s = "--f"
        wordmap = {"--foz": Tupu, "--foo": Tupu, "--fie": Tupu}
        self.assertRaises(
            _match_abbrev, (s, wordmap), Tupu,
            BadOptionError, "ambiguous option: --f (--fie, --foo, --foz?)")


kundi TestParseNumber(BaseTest):
    eleza setUp(self):
        self.parser = InterceptingOptionParser()
        self.parser.add_option("-n", type=int)
        self.parser.add_option("-l", type=int)

    eleza test_parse_num_fail(self):
        self.assertRaises(
            _parse_num, ("", int), {},
            ValueError,
            re.compile(r"invalid literal kila int().*: '?'?"))
        self.assertRaises(
            _parse_num, ("0xOoops", int), {},
            ValueError,
            re.compile(r"invalid literal kila int().*: s?'?0xOoops'?"))

    eleza test_parse_num_ok(self):
        self.assertEqual(_parse_num("0", int), 0)
        self.assertEqual(_parse_num("0x10", int), 16)
        self.assertEqual(_parse_num("0XA", int), 10)
        self.assertEqual(_parse_num("010", int), 8)
        self.assertEqual(_parse_num("0b11", int), 3)
        self.assertEqual(_parse_num("0b", int), 0)

    eleza test_numeric_options(self):
        self.assertParseOK(["-n", "42", "-l", "0x20"],
                           { "n": 42, "l": 0x20 }, [])
        self.assertParseOK(["-n", "0b0101", "-l010"],
                           { "n": 5, "l": 8 }, [])
        self.assertParseFail(["-n008"],
                             "option -n: invalid integer value: '008'")
        self.assertParseFail(["-l0b0123"],
                             "option -l: invalid integer value: '0b0123'")
        self.assertParseFail(["-l", "0x12x"],
                             "option -l: invalid integer value: '0x12x'")


kundi MiscTestCase(unittest.TestCase):
    eleza test__all__(self):
        blacklist = {'check_builtin', 'AmbiguousOptionError', 'NO_DEFAULT'}
        support.check__all__(self, optparse, blacklist=blacklist)


eleza test_main():
    support.run_unittest(__name__)

ikiwa __name__ == '__main__':
    test_main()
