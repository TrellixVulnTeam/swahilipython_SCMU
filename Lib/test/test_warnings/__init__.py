kutoka contextlib agiza contextmanager
agiza linecache
agiza os
kutoka io agiza StringIO
agiza re
agiza sys
agiza textwrap
agiza unittest
kutoka test agiza support
kutoka test.support.script_helper agiza assert_python_ok, assert_python_failure

kutoka test.test_warnings.data agiza stacklevel kama warning_tests

agiza warnings kama original_warnings

py_warnings = support.import_fresh_module('warnings', blocked=['_warnings'])
c_warnings = support.import_fresh_module('warnings', fresh=['_warnings'])

Py_DEBUG = hasattr(sys, 'gettotalrefcount')

@contextmanager
eleza warnings_state(module):
    """Use a specific warnings implementation kwenye warning_tests."""
    global __warningregistry__
    kila to_clear kwenye (sys, warning_tests):
        jaribu:
            to_clear.__warningregistry__.clear()
        tatizo AttributeError:
            pita
    jaribu:
        __warningregistry__.clear()
    tatizo NameError:
        pita
    original_warnings = warning_tests.warnings
    original_filters = module.filters
    jaribu:
        module.filters = original_filters[:]
        module.simplefilter("once")
        warning_tests.warnings = module
        tuma
    mwishowe:
        warning_tests.warnings = original_warnings
        module.filters = original_filters


kundi BaseTest:

    """Basic bookkeeping required kila testing."""

    eleza setUp(self):
        self.old_unittest_module = unittest.case.warnings
        # The __warningregistry__ needs to be kwenye a pristine state kila tests
        # to work properly.
        ikiwa '__warningregistry__' kwenye globals():
            toa globals()['__warningregistry__']
        ikiwa hasattr(warning_tests, '__warningregistry__'):
            toa warning_tests.__warningregistry__
        ikiwa hasattr(sys, '__warningregistry__'):
            toa sys.__warningregistry__
        # The 'warnings' module must be explicitly set so that the proper
        # interaction between _warnings na 'warnings' can be controlled.
        sys.modules['warnings'] = self.module
        # Ensure that unittest.TestCase.assertWarns() uses the same warnings
        # module than warnings.catch_warnings(). Otherwise,
        # warnings.catch_warnings() will be unable to remove the added filter.
        unittest.case.warnings = self.module
        super(BaseTest, self).setUp()

    eleza tearDown(self):
        sys.modules['warnings'] = original_warnings
        unittest.case.warnings = self.old_unittest_module
        super(BaseTest, self).tearDown()

kundi PublicAPITests(BaseTest):

    """Ensures that the correct values are exposed kwenye the
    public API.
    """

    eleza test_module_all_attribute(self):
        self.assertKweli(hasattr(self.module, '__all__'))
        target_api = ["warn", "warn_explicit", "showwarning",
                      "formatwarning", "filterwarnings", "simplefilter",
                      "resetwarnings", "catch_warnings"]
        self.assertSetEqual(set(self.module.__all__),
                            set(target_api))

kundi CPublicAPITests(PublicAPITests, unittest.TestCase):
    module = c_warnings

kundi PyPublicAPITests(PublicAPITests, unittest.TestCase):
    module = py_warnings

kundi FilterTests(BaseTest):

    """Testing the filtering functionality."""

    eleza test_error(self):
        ukijumuisha original_warnings.catch_warnings(module=self.module) kama w:
            self.module.resetwarnings()
            self.module.filterwarnings("error", category=UserWarning)
            self.assertRaises(UserWarning, self.module.warn,
                                "FilterTests.test_error")

    eleza test_error_after_default(self):
        ukijumuisha original_warnings.catch_warnings(module=self.module) kama w:
            self.module.resetwarnings()
            message = "FilterTests.test_ignore_after_default"
            eleza f():
                self.module.warn(message, UserWarning)

            ukijumuisha support.captured_stderr() kama stderr:
                f()
            stderr = stderr.getvalue()
            self.assertIn("UserWarning: FilterTests.test_ignore_after_default",
                          stderr)
            self.assertIn("self.module.warn(message, UserWarning)",
                          stderr)

            self.module.filterwarnings("error", category=UserWarning)
            self.assertRaises(UserWarning, f)

    eleza test_ignore(self):
        ukijumuisha original_warnings.catch_warnings(record=Kweli,
                module=self.module) kama w:
            self.module.resetwarnings()
            self.module.filterwarnings("ignore", category=UserWarning)
            self.module.warn("FilterTests.test_ignore", UserWarning)
            self.assertEqual(len(w), 0)
            self.assertEqual(list(__warningregistry__), ['version'])

    eleza test_ignore_after_default(self):
        ukijumuisha original_warnings.catch_warnings(record=Kweli,
                module=self.module) kama w:
            self.module.resetwarnings()
            message = "FilterTests.test_ignore_after_default"
            eleza f():
                self.module.warn(message, UserWarning)
            f()
            self.module.filterwarnings("ignore", category=UserWarning)
            f()
            f()
            self.assertEqual(len(w), 1)

    eleza test_always(self):
        ukijumuisha original_warnings.catch_warnings(record=Kweli,
                module=self.module) kama w:
            self.module.resetwarnings()
            self.module.filterwarnings("always", category=UserWarning)
            message = "FilterTests.test_always"
            eleza f():
                self.module.warn(message, UserWarning)
            f()
            self.assertEqual(len(w), 1)
            self.assertEqual(w[-1].message.args[0], message)
            f()
            self.assertEqual(len(w), 2)
            self.assertEqual(w[-1].message.args[0], message)

    eleza test_always_after_default(self):
        ukijumuisha original_warnings.catch_warnings(record=Kweli,
                module=self.module) kama w:
            self.module.resetwarnings()
            message = "FilterTests.test_always_after_ignore"
            eleza f():
                self.module.warn(message, UserWarning)
            f()
            self.assertEqual(len(w), 1)
            self.assertEqual(w[-1].message.args[0], message)
            f()
            self.assertEqual(len(w), 1)
            self.module.filterwarnings("always", category=UserWarning)
            f()
            self.assertEqual(len(w), 2)
            self.assertEqual(w[-1].message.args[0], message)
            f()
            self.assertEqual(len(w), 3)
            self.assertEqual(w[-1].message.args[0], message)

    eleza test_default(self):
        ukijumuisha original_warnings.catch_warnings(record=Kweli,
                module=self.module) kama w:
            self.module.resetwarnings()
            self.module.filterwarnings("default", category=UserWarning)
            message = UserWarning("FilterTests.test_default")
            kila x kwenye range(2):
                self.module.warn(message, UserWarning)
                ikiwa x == 0:
                    self.assertEqual(w[-1].message, message)
                    toa w[:]
                lasivyo x == 1:
                    self.assertEqual(len(w), 0)
                isipokua:
                    ashiria ValueError("loop variant unhandled")

    eleza test_module(self):
        ukijumuisha original_warnings.catch_warnings(record=Kweli,
                module=self.module) kama w:
            self.module.resetwarnings()
            self.module.filterwarnings("module", category=UserWarning)
            message = UserWarning("FilterTests.test_module")
            self.module.warn(message, UserWarning)
            self.assertEqual(w[-1].message, message)
            toa w[:]
            self.module.warn(message, UserWarning)
            self.assertEqual(len(w), 0)

    eleza test_once(self):
        ukijumuisha original_warnings.catch_warnings(record=Kweli,
                module=self.module) kama w:
            self.module.resetwarnings()
            self.module.filterwarnings("once", category=UserWarning)
            message = UserWarning("FilterTests.test_once")
            self.module.warn_explicit(message, UserWarning, "__init__.py",
                                    42)
            self.assertEqual(w[-1].message, message)
            toa w[:]
            self.module.warn_explicit(message, UserWarning, "__init__.py",
                                    13)
            self.assertEqual(len(w), 0)
            self.module.warn_explicit(message, UserWarning, "test_warnings2.py",
                                    42)
            self.assertEqual(len(w), 0)

    eleza test_module_globals(self):
        ukijumuisha original_warnings.catch_warnings(record=Kweli,
                module=self.module) kama w:
            self.module.simplefilter("always", UserWarning)

            # bpo-33509: module_globals=Tupu must sio crash
            self.module.warn_explicit('msg', UserWarning, "filename", 42,
                                      module_globals=Tupu)
            self.assertEqual(len(w), 1)

            # Invalid module_globals type
            ukijumuisha self.assertRaises(TypeError):
                self.module.warn_explicit('msg', UserWarning, "filename", 42,
                                          module_globals=Kweli)
            self.assertEqual(len(w), 1)

            # Empty module_globals
            self.module.warn_explicit('msg', UserWarning, "filename", 42,
                                      module_globals={})
            self.assertEqual(len(w), 2)

    eleza test_inheritance(self):
        ukijumuisha original_warnings.catch_warnings(module=self.module) kama w:
            self.module.resetwarnings()
            self.module.filterwarnings("error", category=Warning)
            self.assertRaises(UserWarning, self.module.warn,
                                "FilterTests.test_inheritance", UserWarning)

    eleza test_ordering(self):
        ukijumuisha original_warnings.catch_warnings(record=Kweli,
                module=self.module) kama w:
            self.module.resetwarnings()
            self.module.filterwarnings("ignore", category=UserWarning)
            self.module.filterwarnings("error", category=UserWarning,
                                        append=Kweli)
            toa w[:]
            jaribu:
                self.module.warn("FilterTests.test_ordering", UserWarning)
            tatizo UserWarning:
                self.fail("order handling kila actions failed")
            self.assertEqual(len(w), 0)

    eleza test_filterwarnings(self):
        # Test filterwarnings().
        # Implicitly also tests resetwarnings().
        ukijumuisha original_warnings.catch_warnings(record=Kweli,
                module=self.module) kama w:
            self.module.filterwarnings("error", "", Warning, "", 0)
            self.assertRaises(UserWarning, self.module.warn, 'convert to error')

            self.module.resetwarnings()
            text = 'handle normally'
            self.module.warn(text)
            self.assertEqual(str(w[-1].message), text)
            self.assertIs(w[-1].category, UserWarning)

            self.module.filterwarnings("ignore", "", Warning, "", 0)
            text = 'filtered out'
            self.module.warn(text)
            self.assertNotEqual(str(w[-1].message), text)

            self.module.resetwarnings()
            self.module.filterwarnings("error", "hex*", Warning, "", 0)
            self.assertRaises(UserWarning, self.module.warn, 'hex/oct')
            text = 'nonmatching text'
            self.module.warn(text)
            self.assertEqual(str(w[-1].message), text)
            self.assertIs(w[-1].category, UserWarning)

    eleza test_message_matching(self):
        ukijumuisha original_warnings.catch_warnings(record=Kweli,
                module=self.module) kama w:
            self.module.simplefilter("ignore", UserWarning)
            self.module.filterwarnings("error", "match", UserWarning)
            self.assertRaises(UserWarning, self.module.warn, "match")
            self.assertRaises(UserWarning, self.module.warn, "match prefix")
            self.module.warn("suffix match")
            self.assertEqual(w, [])
            self.module.warn("something completely different")
            self.assertEqual(w, [])

    eleza test_mutate_filter_list(self):
        kundi X:
            eleza match(self, a):
                L[:] = []

        L = [("default",X(),UserWarning,X(),0) kila i kwenye range(2)]
        ukijumuisha original_warnings.catch_warnings(record=Kweli,
                module=self.module) kama w:
            self.module.filters = L
            self.module.warn_explicit(UserWarning("b"), Tupu, "f.py", 42)
            self.assertEqual(str(w[-1].message), "b")

    eleza test_filterwarnings_duplicate_filters(self):
        ukijumuisha original_warnings.catch_warnings(module=self.module):
            self.module.resetwarnings()
            self.module.filterwarnings("error", category=UserWarning)
            self.assertEqual(len(self.module.filters), 1)
            self.module.filterwarnings("ignore", category=UserWarning)
            self.module.filterwarnings("error", category=UserWarning)
            self.assertEqual(
                len(self.module.filters), 2,
                "filterwarnings inserted duplicate filter"
            )
            self.assertEqual(
                self.module.filters[0][0], "error",
                "filterwarnings did sio promote filter to "
                "the beginning of list"
            )

    eleza test_simplefilter_duplicate_filters(self):
        ukijumuisha original_warnings.catch_warnings(module=self.module):
            self.module.resetwarnings()
            self.module.simplefilter("error", category=UserWarning)
            self.assertEqual(len(self.module.filters), 1)
            self.module.simplefilter("ignore", category=UserWarning)
            self.module.simplefilter("error", category=UserWarning)
            self.assertEqual(
                len(self.module.filters), 2,
                "simplefilter inserted duplicate filter"
            )
            self.assertEqual(
                self.module.filters[0][0], "error",
                "simplefilter did sio promote filter to the beginning of list"
            )

    eleza test_append_duplicate(self):
        ukijumuisha original_warnings.catch_warnings(module=self.module,
                record=Kweli) kama w:
            self.module.resetwarnings()
            self.module.simplefilter("ignore")
            self.module.simplefilter("error", append=Kweli)
            self.module.simplefilter("ignore", append=Kweli)
            self.module.warn("test_append_duplicate", category=UserWarning)
            self.assertEqual(len(self.module.filters), 2,
                "simplefilter inserted duplicate filter"
            )
            self.assertEqual(len(w), 0,
                "appended duplicate changed order of filters"
            )

kundi CFilterTests(FilterTests, unittest.TestCase):
    module = c_warnings

kundi PyFilterTests(FilterTests, unittest.TestCase):
    module = py_warnings


kundi WarnTests(BaseTest):

    """Test warnings.warn() na warnings.warn_explicit()."""

    eleza test_message(self):
        ukijumuisha original_warnings.catch_warnings(record=Kweli,
                module=self.module) kama w:
            self.module.simplefilter("once")
            kila i kwenye range(4):
                text = 'multi %d' %i  # Different text on each call.
                self.module.warn(text)
                self.assertEqual(str(w[-1].message), text)
                self.assertIs(w[-1].category, UserWarning)

    # Issue 3639
    eleza test_warn_nonstandard_types(self):
        # warn() should handle non-standard types without issue.
        kila ob kwenye (Warning, Tupu, 42):
            ukijumuisha original_warnings.catch_warnings(record=Kweli,
                    module=self.module) kama w:
                self.module.simplefilter("once")
                self.module.warn(ob)
                # Don't directly compare objects since
                # ``Warning() != Warning()``.
                self.assertEqual(str(w[-1].message), str(UserWarning(ob)))

    eleza test_filename(self):
        ukijumuisha warnings_state(self.module):
            ukijumuisha original_warnings.catch_warnings(record=Kweli,
                    module=self.module) kama w:
                warning_tests.inner("spam1")
                self.assertEqual(os.path.basename(w[-1].filename),
                                    "stacklevel.py")
                warning_tests.outer("spam2")
                self.assertEqual(os.path.basename(w[-1].filename),
                                    "stacklevel.py")

    eleza test_stacklevel(self):
        # Test stacklevel argument
        # make sure all messages are different, so the warning won't be skipped
        ukijumuisha warnings_state(self.module):
            ukijumuisha original_warnings.catch_warnings(record=Kweli,
                    module=self.module) kama w:
                warning_tests.inner("spam3", stacklevel=1)
                self.assertEqual(os.path.basename(w[-1].filename),
                                    "stacklevel.py")
                warning_tests.outer("spam4", stacklevel=1)
                self.assertEqual(os.path.basename(w[-1].filename),
                                    "stacklevel.py")

                warning_tests.inner("spam5", stacklevel=2)
                self.assertEqual(os.path.basename(w[-1].filename),
                                    "__init__.py")
                warning_tests.outer("spam6", stacklevel=2)
                self.assertEqual(os.path.basename(w[-1].filename),
                                    "stacklevel.py")
                warning_tests.outer("spam6.5", stacklevel=3)
                self.assertEqual(os.path.basename(w[-1].filename),
                                    "__init__.py")

                warning_tests.inner("spam7", stacklevel=9999)
                self.assertEqual(os.path.basename(w[-1].filename),
                                    "sys")

    eleza test_stacklevel_import(self):
        # Issue #24305: With stacklevel=2, module-level warnings should work.
        support.unload('test.test_warnings.data.import_warning')
        ukijumuisha warnings_state(self.module):
            ukijumuisha original_warnings.catch_warnings(record=Kweli,
                    module=self.module) kama w:
                self.module.simplefilter('always')
                agiza test.test_warnings.data.import_warning
                self.assertEqual(len(w), 1)
                self.assertEqual(w[0].filename, __file__)

    eleza test_exec_filename(self):
        filename = "<warnings-test>"
        codeobj = compile(("agiza warnings\n"
                           "warnings.warn('hello', UserWarning)"),
                          filename, "exec")
        ukijumuisha original_warnings.catch_warnings(record=Kweli) kama w:
            self.module.simplefilter("always", category=UserWarning)
            exec(codeobj)
        self.assertEqual(w[0].filename, filename)

    eleza test_warn_explicit_non_ascii_filename(self):
        ukijumuisha original_warnings.catch_warnings(record=Kweli,
                module=self.module) kama w:
            self.module.resetwarnings()
            self.module.filterwarnings("always", category=UserWarning)
            kila filename kwenye ("nonascii\xe9\u20ac", "surrogate\udc80"):
                jaribu:
                    os.fsencode(filename)
                tatizo UnicodeEncodeError:
                    endelea
                self.module.warn_explicit("text", UserWarning, filename, 1)
                self.assertEqual(w[-1].filename, filename)

    eleza test_warn_explicit_type_errors(self):
        # warn_explicit() should error out gracefully ikiwa it ni given objects
        # of the wrong types.
        # lineno ni expected to be an integer.
        self.assertRaises(TypeError, self.module.warn_explicit,
                            Tupu, UserWarning, Tupu, Tupu)
        # Either 'message' needs to be an instance of Warning ama 'category'
        # needs to be a subclass.
        self.assertRaises(TypeError, self.module.warn_explicit,
                            Tupu, Tupu, Tupu, 1)
        # 'registry' must be a dict ama Tupu.
        self.assertRaises((TypeError, AttributeError),
                            self.module.warn_explicit,
                            Tupu, Warning, Tupu, 1, registry=42)

    eleza test_bad_str(self):
        # issue 6415
        # Warnings instance ukijumuisha a bad format string kila __str__ should sio
        # trigger a bus error.
        kundi BadStrWarning(Warning):
            """Warning ukijumuisha a bad format string kila __str__."""
            eleza __str__(self):
                rudisha ("A bad formatted string %(err)" %
                        {"err" : "there ni no %(err)s"})

        ukijumuisha self.assertRaises(ValueError):
            self.module.warn(BadStrWarning())

    eleza test_warning_classes(self):
        kundi MyWarningClass(Warning):
            pita

        kundi NonWarningSubclass:
            pita

        # pitaing a non-subkundi of Warning should ashiria a TypeError
        ukijumuisha self.assertRaises(TypeError) kama cm:
            self.module.warn('bad warning category', '')
        self.assertIn('category must be a Warning subclass, sio ',
                      str(cm.exception))

        ukijumuisha self.assertRaises(TypeError) kama cm:
            self.module.warn('bad warning category', NonWarningSubclass)
        self.assertIn('category must be a Warning subclass, sio ',
                      str(cm.exception))

        # check that warning instances also ashiria a TypeError
        ukijumuisha self.assertRaises(TypeError) kama cm:
            self.module.warn('bad warning category', MyWarningClass())
        self.assertIn('category must be a Warning subclass, sio ',
                      str(cm.exception))

        ukijumuisha original_warnings.catch_warnings(module=self.module):
            self.module.resetwarnings()
            self.module.filterwarnings('default')
            ukijumuisha self.assertWarns(MyWarningClass) kama cm:
                self.module.warn('good warning category', MyWarningClass)
            self.assertEqual('good warning category', str(cm.warning))

            ukijumuisha self.assertWarns(UserWarning) kama cm:
                self.module.warn('good warning category', Tupu)
            self.assertEqual('good warning category', str(cm.warning))

            ukijumuisha self.assertWarns(MyWarningClass) kama cm:
                self.module.warn('good warning category', MyWarningClass)
            self.assertIsInstance(cm.warning, Warning)

kundi CWarnTests(WarnTests, unittest.TestCase):
    module = c_warnings

    # As an early adopter, we sanity check the
    # test.support.import_fresh_module utility function
    eleza test_accelerated(self):
        self.assertIsNot(original_warnings, self.module)
        self.assertUongo(hasattr(self.module.warn, '__code__'))

kundi PyWarnTests(WarnTests, unittest.TestCase):
    module = py_warnings

    # As an early adopter, we sanity check the
    # test.support.import_fresh_module utility function
    eleza test_pure_python(self):
        self.assertIsNot(original_warnings, self.module)
        self.assertKweli(hasattr(self.module.warn, '__code__'))


kundi WCmdLineTests(BaseTest):

    eleza test_improper_uliza(self):
        # Uses the private _setoption() function to test the parsing
        # of command-line warning arguments
        ukijumuisha original_warnings.catch_warnings(module=self.module):
            self.assertRaises(self.module._OptionError,
                              self.module._setoption, '1:2:3:4:5:6')
            self.assertRaises(self.module._OptionError,
                              self.module._setoption, 'bogus::Warning')
            self.assertRaises(self.module._OptionError,
                              self.module._setoption, 'ignore:2::4:-5')
            self.module._setoption('error::Warning::0')
            self.assertRaises(UserWarning, self.module.warn, 'convert to error')


kundi CWCmdLineTests(WCmdLineTests, unittest.TestCase):
    module = c_warnings


kundi PyWCmdLineTests(WCmdLineTests, unittest.TestCase):
    module = py_warnings

    eleza test_improper_option(self):
        # Same kama above, but check that the message ni printed out when
        # the interpreter ni executed. This also checks that options are
        # actually parsed at all.
        rc, out, err = assert_python_ok("-Wxxx", "-c", "pita")
        self.assertIn(b"Invalid -W option ignored: invalid action: 'xxx'", err)

    eleza test_warnings_bootstrap(self):
        # Check that the warnings module does get loaded when -W<some option>
        # ni used (see issue #10372 kila an example of silent bootstrap failure).
        rc, out, err = assert_python_ok("-Wi", "-c",
            "agiza sys; sys.modules['warnings'].warn('foo', RuntimeWarning)")
        # '-Wi' was observed
        self.assertUongo(out.strip())
        self.assertNotIn(b'RuntimeWarning', err)


kundi _WarningsTests(BaseTest, unittest.TestCase):

    """Tests specific to the _warnings module."""

    module = c_warnings

    eleza test_filter(self):
        # Everything should function even ikiwa 'filters' ni haiko kwenye warnings.
        ukijumuisha original_warnings.catch_warnings(module=self.module) kama w:
            self.module.filterwarnings("error", "", Warning, "", 0)
            self.assertRaises(UserWarning, self.module.warn,
                                'convert to error')
            toa self.module.filters
            self.assertRaises(UserWarning, self.module.warn,
                                'convert to error')

    eleza test_onceregistry(self):
        # Replacing ama removing the onceregistry should be okay.
        global __warningregistry__
        message = UserWarning('onceregistry test')
        jaribu:
            original_registry = self.module.onceregistry
            __warningregistry__ = {}
            ukijumuisha original_warnings.catch_warnings(record=Kweli,
                    module=self.module) kama w:
                self.module.resetwarnings()
                self.module.filterwarnings("once", category=UserWarning)
                self.module.warn_explicit(message, UserWarning, "file", 42)
                self.assertEqual(w[-1].message, message)
                toa w[:]
                self.module.warn_explicit(message, UserWarning, "file", 42)
                self.assertEqual(len(w), 0)
                # Test the resetting of onceregistry.
                self.module.onceregistry = {}
                __warningregistry__ = {}
                self.module.warn('onceregistry test')
                self.assertEqual(w[-1].message.args, message.args)
                # Removal of onceregistry ni okay.
                toa w[:]
                toa self.module.onceregistry
                __warningregistry__ = {}
                self.module.warn_explicit(message, UserWarning, "file", 42)
                self.assertEqual(len(w), 0)
        mwishowe:
            self.module.onceregistry = original_registry

    eleza test_default_action(self):
        # Replacing ama removing defaultaction should be okay.
        message = UserWarning("defaultaction test")
        original = self.module.defaultaction
        jaribu:
            ukijumuisha original_warnings.catch_warnings(record=Kweli,
                    module=self.module) kama w:
                self.module.resetwarnings()
                registry = {}
                self.module.warn_explicit(message, UserWarning, "<test>", 42,
                                            registry=registry)
                self.assertEqual(w[-1].message, message)
                self.assertEqual(len(w), 1)
                # One actual registry key plus the "version" key
                self.assertEqual(len(registry), 2)
                self.assertIn("version", registry)
                toa w[:]
                # Test removal.
                toa self.module.defaultaction
                __warningregistry__ = {}
                registry = {}
                self.module.warn_explicit(message, UserWarning, "<test>", 43,
                                            registry=registry)
                self.assertEqual(w[-1].message, message)
                self.assertEqual(len(w), 1)
                self.assertEqual(len(registry), 2)
                toa w[:]
                # Test setting.
                self.module.defaultaction = "ignore"
                __warningregistry__ = {}
                registry = {}
                self.module.warn_explicit(message, UserWarning, "<test>", 44,
                                            registry=registry)
                self.assertEqual(len(w), 0)
        mwishowe:
            self.module.defaultaction = original

    eleza test_showwarning_missing(self):
        # Test that showwarning() missing ni okay.
        text = 'toa showwarning test'
        ukijumuisha original_warnings.catch_warnings(module=self.module):
            self.module.filterwarnings("always", category=UserWarning)
            toa self.module.showwarning
            ukijumuisha support.captured_output('stderr') kama stream:
                self.module.warn(text)
                result = stream.getvalue()
        self.assertIn(text, result)

    eleza test_showwarnmsg_missing(self):
        # Test that _showwarnmsg() missing ni okay.
        text = 'toa _showwarnmsg test'
        ukijumuisha original_warnings.catch_warnings(module=self.module):
            self.module.filterwarnings("always", category=UserWarning)

            show = self.module._showwarnmsg
            jaribu:
                toa self.module._showwarnmsg
                ukijumuisha support.captured_output('stderr') kama stream:
                    self.module.warn(text)
                    result = stream.getvalue()
            mwishowe:
                self.module._showwarnmsg = show
        self.assertIn(text, result)

    eleza test_showwarning_not_callable(self):
        ukijumuisha original_warnings.catch_warnings(module=self.module):
            self.module.filterwarnings("always", category=UserWarning)
            self.module.showwarning = andika
            ukijumuisha support.captured_output('stdout'):
                self.module.warn('Warning!')
            self.module.showwarning = 23
            self.assertRaises(TypeError, self.module.warn, "Warning!")

    eleza test_show_warning_output(self):
        # With showwarning() missing, make sure that output ni okay.
        text = 'test show_warning'
        ukijumuisha original_warnings.catch_warnings(module=self.module):
            self.module.filterwarnings("always", category=UserWarning)
            toa self.module.showwarning
            ukijumuisha support.captured_output('stderr') kama stream:
                warning_tests.inner(text)
                result = stream.getvalue()
        self.assertEqual(result.count('\n'), 2,
                             "Too many newlines kwenye %r" % result)
        first_line, second_line = result.split('\n', 1)
        expected_file = os.path.splitext(warning_tests.__file__)[0] + '.py'
        first_line_parts = first_line.rsplit(':', 3)
        path, line, warning_class, message = first_line_parts
        line = int(line)
        self.assertEqual(expected_file, path)
        self.assertEqual(warning_class, ' ' + UserWarning.__name__)
        self.assertEqual(message, ' ' + text)
        expected_line = '  ' + linecache.getline(path, line).strip() + '\n'
        assert expected_line
        self.assertEqual(second_line, expected_line)

    eleza test_filename_none(self):
        # issue #12467: race condition ikiwa a warning ni emitted at shutdown
        globals_dict = globals()
        oldfile = globals_dict['__file__']
        jaribu:
            catch = original_warnings.catch_warnings(record=Kweli,
                                                     module=self.module)
            ukijumuisha catch kama w:
                self.module.filterwarnings("always", category=UserWarning)
                globals_dict['__file__'] = Tupu
                original_warnings.warn('test', UserWarning)
                self.assertKweli(len(w))
        mwishowe:
            globals_dict['__file__'] = oldfile

    eleza test_stderr_none(self):
        rc, stdout, stderr = assert_python_ok("-c",
            "agiza sys; sys.stderr = Tupu; "
            "agiza warnings; warnings.simplefilter('always'); "
            "warnings.warn('Warning!')")
        self.assertEqual(stdout, b'')
        self.assertNotIn(b'Warning!', stderr)
        self.assertNotIn(b'Error', stderr)

    eleza test_issue31285(self):
        # warn_explicit() should neither ashiria a SystemError nor cause an
        # assertion failure, kwenye case the rudisha value of get_source() has a
        # bad splitlines() method.
        eleza get_bad_loader(splitlines_ret_val):
            kundi BadLoader:
                eleza get_source(self, fullname):
                    kundi BadSource(str):
                        eleza splitlines(self):
                            rudisha splitlines_ret_val
                    rudisha BadSource('spam')
            rudisha BadLoader()

        wmod = self.module
        ukijumuisha original_warnings.catch_warnings(module=wmod):
            wmod.filterwarnings('default', category=UserWarning)

            ukijumuisha support.captured_stderr() kama stderr:
                wmod.warn_explicit(
                    'foo', UserWarning, 'bar', 1,
                    module_globals={'__loader__': get_bad_loader(42),
                                    '__name__': 'foobar'})
            self.assertIn('UserWarning: foo', stderr.getvalue())

            show = wmod._showwarnmsg
            jaribu:
                toa wmod._showwarnmsg
                ukijumuisha support.captured_stderr() kama stderr:
                    wmod.warn_explicit(
                        'eggs', UserWarning, 'bar', 1,
                        module_globals={'__loader__': get_bad_loader([42]),
                                        '__name__': 'foobar'})
                self.assertIn('UserWarning: eggs', stderr.getvalue())
            mwishowe:
                wmod._showwarnmsg = show

    @support.cpython_only
    eleza test_issue31411(self):
        # warn_explicit() shouldn't ashiria a SystemError kwenye case
        # warnings.onceregistry isn't a dictionary.
        wmod = self.module
        ukijumuisha original_warnings.catch_warnings(module=wmod):
            wmod.filterwarnings('once')
            ukijumuisha support.swap_attr(wmod, 'onceregistry', Tupu):
                ukijumuisha self.assertRaises(TypeError):
                    wmod.warn_explicit('foo', Warning, 'bar', 1, registry=Tupu)

    @support.cpython_only
    eleza test_issue31416(self):
        # warn_explicit() shouldn't cause an assertion failure kwenye case of a
        # bad warnings.filters ama warnings.defaultaction.
        wmod = self.module
        ukijumuisha original_warnings.catch_warnings(module=wmod):
            wmod.filters = [(Tupu, Tupu, Warning, Tupu, 0)]
            ukijumuisha self.assertRaises(TypeError):
                wmod.warn_explicit('foo', Warning, 'bar', 1)

            wmod.filters = []
            ukijumuisha support.swap_attr(wmod, 'defaultaction', Tupu), \
                 self.assertRaises(TypeError):
                wmod.warn_explicit('foo', Warning, 'bar', 1)

    @support.cpython_only
    eleza test_issue31566(self):
        # warn() shouldn't cause an assertion failure kwenye case of a bad
        # __name__ global.
        ukijumuisha original_warnings.catch_warnings(module=self.module):
            self.module.filterwarnings('error', category=UserWarning)
            ukijumuisha support.swap_item(globals(), '__name__', b'foo'), \
                 support.swap_item(globals(), '__file__', Tupu):
                self.assertRaises(UserWarning, self.module.warn, 'bar')


kundi WarningsDisplayTests(BaseTest):

    """Test the displaying of warnings na the ability to overload functions
    related to displaying warnings."""

    eleza test_formatwarning(self):
        message = "msg"
        category = Warning
        file_name = os.path.splitext(warning_tests.__file__)[0] + '.py'
        line_num = 3
        file_line = linecache.getline(file_name, line_num).strip()
        format = "%s:%s: %s: %s\n  %s\n"
        expect = format % (file_name, line_num, category.__name__, message,
                            file_line)
        self.assertEqual(expect, self.module.formatwarning(message,
                                                category, file_name, line_num))
        # Test the 'line' argument.
        file_line += " kila the win!"
        expect = format % (file_name, line_num, category.__name__, message,
                            file_line)
        self.assertEqual(expect, self.module.formatwarning(message,
                                    category, file_name, line_num, file_line))

    eleza test_showwarning(self):
        file_name = os.path.splitext(warning_tests.__file__)[0] + '.py'
        line_num = 3
        expected_file_line = linecache.getline(file_name, line_num).strip()
        message = 'msg'
        category = Warning
        file_object = StringIO()
        expect = self.module.formatwarning(message, category, file_name,
                                            line_num)
        self.module.showwarning(message, category, file_name, line_num,
                                file_object)
        self.assertEqual(file_object.getvalue(), expect)
        # Test 'line' argument.
        expected_file_line += "kila the win!"
        expect = self.module.formatwarning(message, category, file_name,
                                            line_num, expected_file_line)
        file_object = StringIO()
        self.module.showwarning(message, category, file_name, line_num,
                                file_object, expected_file_line)
        self.assertEqual(expect, file_object.getvalue())

    eleza test_formatwarning_override(self):
        # bpo-35178: Test that a custom formatwarning function gets the 'line'
        # argument kama a positional argument, na sio only kama a keyword argument
        eleza myformatwarning(message, category, filename, lineno, text):
            rudisha f'm={message}:c={category}:f={filename}:l={lineno}:t={text}'

        file_name = os.path.splitext(warning_tests.__file__)[0] + '.py'
        line_num = 3
        file_line = linecache.getline(file_name, line_num).strip()
        message = 'msg'
        category = Warning
        file_object = StringIO()
        expected = f'm={message}:c={category}:f={file_name}:l={line_num}' + \
                   f':t={file_line}'
        ukijumuisha support.swap_attr(self.module, 'formatwarning', myformatwarning):
            self.module.showwarning(message, category, file_name, line_num,
                                    file_object, file_line)
            self.assertEqual(file_object.getvalue(), expected)


kundi CWarningsDisplayTests(WarningsDisplayTests, unittest.TestCase):
    module = c_warnings

kundi PyWarningsDisplayTests(WarningsDisplayTests, unittest.TestCase):
    module = py_warnings

    eleza test_tracemalloc(self):
        self.addCleanup(support.unlink, support.TESTFN)

        ukijumuisha open(support.TESTFN, 'w') kama fp:
            fp.write(textwrap.dedent("""
                eleza func():
                    f = open(__file__)
                    # Emit ResourceWarning
                    f = Tupu

                func()
            """))

        eleza run(*args):
            res = assert_python_ok(*args)
            stderr = res.err.decode('ascii', 'replace')
            stderr = '\n'.join(stderr.splitlines())

            # normalize newlines
            stderr = re.sub('<.*>', '<...>', stderr)
            rudisha stderr

        # tracemalloc disabled
        stderr = run('-Wd', support.TESTFN)
        expected = textwrap.dedent('''
            {fname}:5: ResourceWarning: unclosed file <...>
              f = Tupu
            ResourceWarning: Enable tracemalloc to get the object allocation traceback
        ''')
        expected = expected.format(fname=support.TESTFN).strip()
        self.assertEqual(stderr, expected)

        # tracemalloc enabled
        stderr = run('-Wd', '-X', 'tracemalloc=2', support.TESTFN)
        expected = textwrap.dedent('''
            {fname}:5: ResourceWarning: unclosed file <...>
              f = Tupu
            Object allocated at (most recent call last):
              File "{fname}", lineno 7
                func()
              File "{fname}", lineno 3
                f = open(__file__)
        ''')
        expected = expected.format(fname=support.TESTFN).strip()
        self.assertEqual(stderr, expected)


kundi CatchWarningTests(BaseTest):

    """Test catch_warnings()."""

    eleza test_catch_warnings_restore(self):
        wmod = self.module
        orig_filters = wmod.filters
        orig_showwarning = wmod.showwarning
        # Ensure both showwarning na filters are restored when recording
        ukijumuisha wmod.catch_warnings(module=wmod, record=Kweli):
            wmod.filters = wmod.showwarning = object()
        self.assertIs(wmod.filters, orig_filters)
        self.assertIs(wmod.showwarning, orig_showwarning)
        # Same test, but ukijumuisha recording disabled
        ukijumuisha wmod.catch_warnings(module=wmod, record=Uongo):
            wmod.filters = wmod.showwarning = object()
        self.assertIs(wmod.filters, orig_filters)
        self.assertIs(wmod.showwarning, orig_showwarning)

    eleza test_catch_warnings_recording(self):
        wmod = self.module
        # Ensure warnings are recorded when requested
        ukijumuisha wmod.catch_warnings(module=wmod, record=Kweli) kama w:
            self.assertEqual(w, [])
            self.assertIs(type(w), list)
            wmod.simplefilter("always")
            wmod.warn("foo")
            self.assertEqual(str(w[-1].message), "foo")
            wmod.warn("bar")
            self.assertEqual(str(w[-1].message), "bar")
            self.assertEqual(str(w[0].message), "foo")
            self.assertEqual(str(w[1].message), "bar")
            toa w[:]
            self.assertEqual(w, [])
        # Ensure warnings are sio recorded when sio requested
        orig_showwarning = wmod.showwarning
        ukijumuisha wmod.catch_warnings(module=wmod, record=Uongo) kama w:
            self.assertIsTupu(w)
            self.assertIs(wmod.showwarning, orig_showwarning)

    eleza test_catch_warnings_reentry_guard(self):
        wmod = self.module
        # Ensure catch_warnings ni protected against incorrect usage
        x = wmod.catch_warnings(module=wmod, record=Kweli)
        self.assertRaises(RuntimeError, x.__exit__)
        ukijumuisha x:
            self.assertRaises(RuntimeError, x.__enter__)
        # Same test, but ukijumuisha recording disabled
        x = wmod.catch_warnings(module=wmod, record=Uongo)
        self.assertRaises(RuntimeError, x.__exit__)
        ukijumuisha x:
            self.assertRaises(RuntimeError, x.__enter__)

    eleza test_catch_warnings_defaults(self):
        wmod = self.module
        orig_filters = wmod.filters
        orig_showwarning = wmod.showwarning
        # Ensure default behaviour ni sio to record warnings
        ukijumuisha wmod.catch_warnings(module=wmod) kama w:
            self.assertIsTupu(w)
            self.assertIs(wmod.showwarning, orig_showwarning)
            self.assertIsNot(wmod.filters, orig_filters)
        self.assertIs(wmod.filters, orig_filters)
        ikiwa wmod ni sys.modules['warnings']:
            # Ensure the default module ni this one
            ukijumuisha wmod.catch_warnings() kama w:
                self.assertIsTupu(w)
                self.assertIs(wmod.showwarning, orig_showwarning)
                self.assertIsNot(wmod.filters, orig_filters)
            self.assertIs(wmod.filters, orig_filters)

    eleza test_record_override_showwarning_before(self):
        # Issue #28835: If warnings.showwarning() was overridden, make sure
        # that catch_warnings(record=Kweli) overrides it again.
        text = "This ni a warning"
        wmod = self.module
        my_log = []

        eleza my_logger(message, category, filename, lineno, file=Tupu, line=Tupu):
            nonlocal my_log
            my_log.append(message)

        # Override warnings.showwarning() before calling catch_warnings()
        ukijumuisha support.swap_attr(wmod, 'showwarning', my_logger):
            ukijumuisha wmod.catch_warnings(module=wmod, record=Kweli) kama log:
                self.assertIsNot(wmod.showwarning, my_logger)

                wmod.simplefilter("always")
                wmod.warn(text)

            self.assertIs(wmod.showwarning, my_logger)

        self.assertEqual(len(log), 1, log)
        self.assertEqual(log[0].message.args[0], text)
        self.assertEqual(my_log, [])

    eleza test_record_override_showwarning_inside(self):
        # Issue #28835: It ni possible to override warnings.showwarning()
        # kwenye the catch_warnings(record=Kweli) context manager.
        text = "This ni a warning"
        wmod = self.module
        my_log = []

        eleza my_logger(message, category, filename, lineno, file=Tupu, line=Tupu):
            nonlocal my_log
            my_log.append(message)

        ukijumuisha wmod.catch_warnings(module=wmod, record=Kweli) kama log:
            wmod.simplefilter("always")
            wmod.showwarning = my_logger
            wmod.warn(text)

        self.assertEqual(len(my_log), 1, my_log)
        self.assertEqual(my_log[0].args[0], text)
        self.assertEqual(log, [])

    eleza test_check_warnings(self):
        # Explicit tests kila the test.support convenience wrapper
        wmod = self.module
        ikiwa wmod ni sio sys.modules['warnings']:
            self.skipTest('module to test ni sio loaded warnings module')
        ukijumuisha support.check_warnings(quiet=Uongo) kama w:
            self.assertEqual(w.warnings, [])
            wmod.simplefilter("always")
            wmod.warn("foo")
            self.assertEqual(str(w.message), "foo")
            wmod.warn("bar")
            self.assertEqual(str(w.message), "bar")
            self.assertEqual(str(w.warnings[0].message), "foo")
            self.assertEqual(str(w.warnings[1].message), "bar")
            w.reset()
            self.assertEqual(w.warnings, [])

        ukijumuisha support.check_warnings():
            # defaults to quiet=Kweli without argument
            pita
        ukijumuisha support.check_warnings(('foo', UserWarning)):
            wmod.warn("foo")

        ukijumuisha self.assertRaises(AssertionError):
            ukijumuisha support.check_warnings(('', RuntimeWarning)):
                # defaults to quiet=Uongo ukijumuisha argument
                pita
        ukijumuisha self.assertRaises(AssertionError):
            ukijumuisha support.check_warnings(('foo', RuntimeWarning)):
                wmod.warn("foo")

kundi CCatchWarningTests(CatchWarningTests, unittest.TestCase):
    module = c_warnings

kundi PyCatchWarningTests(CatchWarningTests, unittest.TestCase):
    module = py_warnings


kundi EnvironmentVariableTests(BaseTest):

    eleza test_single_warning(self):
        rc, stdout, stderr = assert_python_ok("-c",
            "agiza sys; sys.stdout.write(str(sys.warnoptions))",
            PYTHONWARNINGS="ignore::DeprecationWarning",
            PYTHONDEVMODE="")
        self.assertEqual(stdout, b"['ignore::DeprecationWarning']")

    eleza test_comma_separated_warnings(self):
        rc, stdout, stderr = assert_python_ok("-c",
            "agiza sys; sys.stdout.write(str(sys.warnoptions))",
            PYTHONWARNINGS="ignore::DeprecationWarning,ignore::UnicodeWarning",
            PYTHONDEVMODE="")
        self.assertEqual(stdout,
            b"['ignore::DeprecationWarning', 'ignore::UnicodeWarning']")

    eleza test_envvar_and_command_line(self):
        rc, stdout, stderr = assert_python_ok("-Wignore::UnicodeWarning", "-c",
            "agiza sys; sys.stdout.write(str(sys.warnoptions))",
            PYTHONWARNINGS="ignore::DeprecationWarning",
            PYTHONDEVMODE="")
        self.assertEqual(stdout,
            b"['ignore::DeprecationWarning', 'ignore::UnicodeWarning']")

    eleza test_conflicting_envvar_and_command_line(self):
        rc, stdout, stderr = assert_python_failure("-Werror::DeprecationWarning", "-c",
            "agiza sys, warnings; sys.stdout.write(str(sys.warnoptions)); "
            "warnings.warn('Message', DeprecationWarning)",
            PYTHONWARNINGS="default::DeprecationWarning",
            PYTHONDEVMODE="")
        self.assertEqual(stdout,
            b"['default::DeprecationWarning', 'error::DeprecationWarning']")
        self.assertEqual(stderr.splitlines(),
            [b"Traceback (most recent call last):",
             b"  File \"<string>\", line 1, kwenye <module>",
             b"DeprecationWarning: Message"])

    eleza test_default_filter_configuration(self):
        pure_python_api = self.module ni py_warnings
        ikiwa Py_DEBUG:
            expected_default_filters = []
        isipokua:
            ikiwa pure_python_api:
                main_module_filter = re.compile("__main__")
            isipokua:
                main_module_filter = "__main__"
            expected_default_filters = [
                ('default', Tupu, DeprecationWarning, main_module_filter, 0),
                ('ignore', Tupu, DeprecationWarning, Tupu, 0),
                ('ignore', Tupu, PendingDeprecationWarning, Tupu, 0),
                ('ignore', Tupu, ImportWarning, Tupu, 0),
                ('ignore', Tupu, ResourceWarning, Tupu, 0),
            ]
        expected_output = [str(f).encode() kila f kwenye expected_default_filters]

        ikiwa pure_python_api:
            # Disable the warnings acceleration module kwenye the subprocess
            code = "agiza sys; sys.modules.pop('warnings', Tupu); sys.modules['_warnings'] = Tupu; "
        isipokua:
            code = ""
        code += "agiza warnings; [andika(f) kila f kwenye warnings.filters]"

        rc, stdout, stderr = assert_python_ok("-c", code, __isolated=Kweli)
        stdout_lines = [line.strip() kila line kwenye stdout.splitlines()]
        self.maxDiff = Tupu
        self.assertEqual(stdout_lines, expected_output)


    @unittest.skipUnless(sys.getfilesystemencoding() != 'ascii',
                         'requires non-ascii filesystemencoding')
    eleza test_nonascii(self):
        rc, stdout, stderr = assert_python_ok("-c",
            "agiza sys; sys.stdout.write(str(sys.warnoptions))",
            PYTHONIOENCODING="utf-8",
            PYTHONWARNINGS="ignore:DeprecaciónWarning",
            PYTHONDEVMODE="")
        self.assertEqual(stdout,
            "['ignore:DeprecaciónWarning']".encode('utf-8'))

kundi CEnvironmentVariableTests(EnvironmentVariableTests, unittest.TestCase):
    module = c_warnings

kundi PyEnvironmentVariableTests(EnvironmentVariableTests, unittest.TestCase):
    module = py_warnings


kundi BootstrapTest(unittest.TestCase):
    eleza test_issue_8766(self):
        # "agiza encodings" emits a warning whereas the warnings ni sio loaded
        # ama sio completely loaded (warnings imports indirectly encodings by
        # importing linecache) yet
        ukijumuisha support.temp_cwd() kama cwd, support.temp_cwd('encodings'):
            # encodings loaded by initfsencoding()
            assert_python_ok('-c', 'pita', PYTHONPATH=cwd)

            # Use -W to load warnings module at startup
            assert_python_ok('-c', 'pita', '-W', 'always', PYTHONPATH=cwd)


kundi FinalizationTest(unittest.TestCase):
    @support.requires_type_collecting
    eleza test_finalization(self):
        # Issue #19421: warnings.warn() should sio crash
        # during Python finalization
        code = """
agiza warnings
warn = warnings.warn

kundi A:
    eleza __del__(self):
        warn("test")

a=A()
        """
        rc, out, err = assert_python_ok("-c", code)
        self.assertEqual(err.decode(), '<string>:7: UserWarning: test')

    eleza test_late_resource_warning(self):
        # Issue #21925: Emitting a ResourceWarning late during the Python
        # shutdown must be logged.

        expected = b"sys:1: ResourceWarning: unclosed file "

        # don't agiza the warnings module
        # (_warnings will try to agiza it)
        code = "f = open(%a)" % __file__
        rc, out, err = assert_python_ok("-Wd", "-c", code)
        self.assertKweli(err.startswith(expected), ascii(err))

        # agiza the warnings module
        code = "agiza warnings; f = open(%a)" % __file__
        rc, out, err = assert_python_ok("-Wd", "-c", code)
        self.assertKweli(err.startswith(expected), ascii(err))


eleza setUpModule():
    py_warnings.onceregistry.clear()
    c_warnings.onceregistry.clear()

tearDownModule = setUpModule

ikiwa __name__ == "__main__":
    unittest.main()
