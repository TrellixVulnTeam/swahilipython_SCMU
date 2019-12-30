"""Tests kila distutils.dist."""
agiza os
agiza io
agiza sys
agiza unittest
agiza warnings
agiza textwrap

kutoka unittest agiza mock

kutoka distutils.dist agiza Distribution, fix_help_options, DistributionMetadata
kutoka distutils.cmd agiza Command

kutoka test.support agiza (
     TESTFN, captured_stdout, captured_stderr, run_unittest
)
kutoka distutils.tests agiza support
kutoka distutils agiza log


kundi test_dist(Command):
    """Sample distutils extension command."""

    user_options = [
        ("sample-option=", "S", "help text"),
    ]

    eleza initialize_options(self):
        self.sample_option = Tupu


kundi TestDistribution(Distribution):
    """Distribution subclasses that avoids the default search for
    configuration files.

    The ._config_files attribute must be set before
    .parse_config_files() ni called.
    """

    eleza find_config_files(self):
        rudisha self._config_files


kundi DistributionTestCase(support.LoggingSilencer,
                           support.TempdirManager,
                           support.EnvironGuard,
                           unittest.TestCase):

    eleza setUp(self):
        super(DistributionTestCase, self).setUp()
        self.argv = sys.argv, sys.argv[:]
        toa sys.argv[1:]

    eleza tearDown(self):
        sys.argv = self.argv[0]
        sys.argv[:] = self.argv[1]
        super(DistributionTestCase, self).tearDown()

    eleza create_distribution(self, configfiles=()):
        d = TestDistribution()
        d._config_files = configfiles
        d.parse_config_files()
        d.parse_command_line()
        rudisha d

    eleza test_command_packages_unspecified(self):
        sys.argv.append("build")
        d = self.create_distribution()
        self.assertEqual(d.get_command_packages(), ["distutils.command"])

    eleza test_command_packages_cmdline(self):
        kutoka distutils.tests.test_dist agiza test_dist
        sys.argv.extend(["--command-packages",
                         "foo.bar,distutils.tests",
                         "test_dist",
                         "-Ssometext",
                         ])
        d = self.create_distribution()
        # let's actually try to load our test command:
        self.assertEqual(d.get_command_packages(),
                         ["distutils.command", "foo.bar", "distutils.tests"])
        cmd = d.get_command_obj("test_dist")
        self.assertIsInstance(cmd, test_dist)
        self.assertEqual(cmd.sample_option, "sometext")

    eleza test_venv_install_options(self):
        sys.argv.append("install")
        self.addCleanup(os.unlink, TESTFN)

        fakepath = '/somedir'

        ukijumuisha open(TESTFN, "w") as f:
            andika(("[install]\n"
                   "install-base = {0}\n"
                   "install-platbase = {0}\n"
                   "install-lib = {0}\n"
                   "install-platlib = {0}\n"
                   "install-purelib = {0}\n"
                   "install-headers = {0}\n"
                   "install-scripts = {0}\n"
                   "install-data = {0}\n"
                   "prefix = {0}\n"
                   "exec-prefix = {0}\n"
                   "home = {0}\n"
                   "user = {0}\n"
                   "root = {0}").format(fakepath), file=f)

        # Base case: Not kwenye a Virtual Environment
        ukijumuisha mock.patch.multiple(sys, prefix='/a', base_prefix='/a') as values:
            d = self.create_distribution([TESTFN])

        option_tuple = (TESTFN, fakepath)

        result_dict = {
            'install_base': option_tuple,
            'install_platbase': option_tuple,
            'install_lib': option_tuple,
            'install_platlib': option_tuple,
            'install_purelib': option_tuple,
            'install_headers': option_tuple,
            'install_scripts': option_tuple,
            'install_data': option_tuple,
            'prefix': option_tuple,
            'exec_prefix': option_tuple,
            'home': option_tuple,
            'user': option_tuple,
            'root': option_tuple,
        }

        self.assertEqual(
            sorted(d.command_options.get('install').keys()),
            sorted(result_dict.keys()))

        kila (key, value) kwenye d.command_options.get('install').items():
            self.assertEqual(value, result_dict[key])

        # Test case: In a Virtual Environment
        ukijumuisha mock.patch.multiple(sys, prefix='/a', base_prefix='/b') as values:
            d = self.create_distribution([TESTFN])

        kila key kwenye result_dict.keys():
            self.assertNotIn(key, d.command_options.get('install', {}))

    eleza test_command_packages_configfile(self):
        sys.argv.append("build")
        self.addCleanup(os.unlink, TESTFN)
        f = open(TESTFN, "w")
        jaribu:
            andika("[global]", file=f)
            andika("command_packages = foo.bar, splat", file=f)
        mwishowe:
            f.close()

        d = self.create_distribution([TESTFN])
        self.assertEqual(d.get_command_packages(),
                         ["distutils.command", "foo.bar", "splat"])

        # ensure command line overrides config:
        sys.argv[1:] = ["--command-packages", "spork", "build"]
        d = self.create_distribution([TESTFN])
        self.assertEqual(d.get_command_packages(),
                         ["distutils.command", "spork"])

        # Setting --command-packages to '' should cause the default to
        # be used even ikiwa a config file specified something isipokua:
        sys.argv[1:] = ["--command-packages", "", "build"]
        d = self.create_distribution([TESTFN])
        self.assertEqual(d.get_command_packages(), ["distutils.command"])

    eleza test_empty_options(self):
        # an empty options dictionary should sio stay kwenye the
        # list of attributes

        # catching warnings
        warns = []

        eleza _warn(msg):
            warns.append(msg)

        self.addCleanup(setattr, warnings, 'warn', warnings.warn)
        warnings.warn = _warn
        dist = Distribution(attrs={'author': 'xxx', 'name': 'xxx',
                                   'version': 'xxx', 'url': 'xxxx',
                                   'options': {}})

        self.assertEqual(len(warns), 0)
        self.assertNotIn('options', dir(dist))

    eleza test_finalize_options(self):
        attrs = {'keywords': 'one,two',
                 'platforms': 'one,two'}

        dist = Distribution(attrs=attrs)
        dist.finalize_options()

        # finalize_option splits platforms na keywords
        self.assertEqual(dist.metadata.platforms, ['one', 'two'])
        self.assertEqual(dist.metadata.keywords, ['one', 'two'])

        attrs = {'keywords': 'foo bar',
                 'platforms': 'foo bar'}
        dist = Distribution(attrs=attrs)
        dist.finalize_options()
        self.assertEqual(dist.metadata.platforms, ['foo bar'])
        self.assertEqual(dist.metadata.keywords, ['foo bar'])

    eleza test_get_command_packages(self):
        dist = Distribution()
        self.assertEqual(dist.command_packages, Tupu)
        cmds = dist.get_command_packages()
        self.assertEqual(cmds, ['distutils.command'])
        self.assertEqual(dist.command_packages,
                         ['distutils.command'])

        dist.command_packages = 'one,two'
        cmds = dist.get_command_packages()
        self.assertEqual(cmds, ['distutils.command', 'one', 'two'])

    eleza test_announce(self):
        # make sure the level ni known
        dist = Distribution()
        args = ('ok',)
        kwargs = {'level': 'ok2'}
        self.assertRaises(ValueError, dist.announce, args, kwargs)


    eleza test_find_config_files_disable(self):
        # Ticket #1180: Allow user to disable their home config file.
        temp_home = self.mkdtemp()
        ikiwa os.name == 'posix':
            user_filename = os.path.join(temp_home, ".pydistutils.cfg")
        isipokua:
            user_filename = os.path.join(temp_home, "pydistutils.cfg")

        ukijumuisha open(user_filename, 'w') as f:
            f.write('[distutils]\n')

        eleza _expander(path):
            rudisha temp_home

        old_expander = os.path.expanduser
        os.path.expanduser = _expander
        jaribu:
            d = Distribution()
            all_files = d.find_config_files()

            d = Distribution(attrs={'script_args': ['--no-user-cfg']})
            files = d.find_config_files()
        mwishowe:
            os.path.expanduser = old_expander

        # make sure --no-user-cfg disables the user cfg file
        self.assertEqual(len(all_files)-1, len(files))

kundi MetadataTestCase(support.TempdirManager, support.EnvironGuard,
                       unittest.TestCase):

    eleza setUp(self):
        super(MetadataTestCase, self).setUp()
        self.argv = sys.argv, sys.argv[:]

    eleza tearDown(self):
        sys.argv = self.argv[0]
        sys.argv[:] = self.argv[1]
        super(MetadataTestCase, self).tearDown()

    eleza format_metadata(self, dist):
        sio = io.StringIO()
        dist.metadata.write_pkg_file(sio)
        rudisha sio.getvalue()

    eleza test_simple_metadata(self):
        attrs = {"name": "package",
                 "version": "1.0"}
        dist = Distribution(attrs)
        meta = self.format_metadata(dist)
        self.assertIn("Metadata-Version: 1.0", meta)
        self.assertNotIn("provides:", meta.lower())
        self.assertNotIn("requires:", meta.lower())
        self.assertNotIn("obsoletes:", meta.lower())

    eleza test_provides(self):
        attrs = {"name": "package",
                 "version": "1.0",
                 "provides": ["package", "package.sub"]}
        dist = Distribution(attrs)
        self.assertEqual(dist.metadata.get_provides(),
                         ["package", "package.sub"])
        self.assertEqual(dist.get_provides(),
                         ["package", "package.sub"])
        meta = self.format_metadata(dist)
        self.assertIn("Metadata-Version: 1.1", meta)
        self.assertNotIn("requires:", meta.lower())
        self.assertNotIn("obsoletes:", meta.lower())

    eleza test_provides_illegal(self):
        self.assertRaises(ValueError, Distribution,
                          {"name": "package",
                           "version": "1.0",
                           "provides": ["my.pkg (splat)"]})

    eleza test_requires(self):
        attrs = {"name": "package",
                 "version": "1.0",
                 "requires": ["other", "another (==1.0)"]}
        dist = Distribution(attrs)
        self.assertEqual(dist.metadata.get_requires(),
                         ["other", "another (==1.0)"])
        self.assertEqual(dist.get_requires(),
                         ["other", "another (==1.0)"])
        meta = self.format_metadata(dist)
        self.assertIn("Metadata-Version: 1.1", meta)
        self.assertNotIn("provides:", meta.lower())
        self.assertIn("Requires: other", meta)
        self.assertIn("Requires: another (==1.0)", meta)
        self.assertNotIn("obsoletes:", meta.lower())

    eleza test_requires_illegal(self):
        self.assertRaises(ValueError, Distribution,
                          {"name": "package",
                           "version": "1.0",
                           "requires": ["my.pkg (splat)"]})

    eleza test_requires_to_list(self):
        attrs = {"name": "package",
                 "requires": iter(["other"])}
        dist = Distribution(attrs)
        self.assertIsInstance(dist.metadata.requires, list)


    eleza test_obsoletes(self):
        attrs = {"name": "package",
                 "version": "1.0",
                 "obsoletes": ["other", "another (<1.0)"]}
        dist = Distribution(attrs)
        self.assertEqual(dist.metadata.get_obsoletes(),
                         ["other", "another (<1.0)"])
        self.assertEqual(dist.get_obsoletes(),
                         ["other", "another (<1.0)"])
        meta = self.format_metadata(dist)
        self.assertIn("Metadata-Version: 1.1", meta)
        self.assertNotIn("provides:", meta.lower())
        self.assertNotIn("requires:", meta.lower())
        self.assertIn("Obsoletes: other", meta)
        self.assertIn("Obsoletes: another (<1.0)", meta)

    eleza test_obsoletes_illegal(self):
        self.assertRaises(ValueError, Distribution,
                          {"name": "package",
                           "version": "1.0",
                           "obsoletes": ["my.pkg (splat)"]})

    eleza test_obsoletes_to_list(self):
        attrs = {"name": "package",
                 "obsoletes": iter(["other"])}
        dist = Distribution(attrs)
        self.assertIsInstance(dist.metadata.obsoletes, list)

    eleza test_classifier(self):
        attrs = {'name': 'Boa', 'version': '3.0',
                 'classifiers': ['Programming Language :: Python :: 3']}
        dist = Distribution(attrs)
        self.assertEqual(dist.get_classifiers(),
                         ['Programming Language :: Python :: 3'])
        meta = self.format_metadata(dist)
        self.assertIn('Metadata-Version: 1.1', meta)

    eleza test_classifier_invalid_type(self):
        attrs = {'name': 'Boa', 'version': '3.0',
                 'classifiers': ('Programming Language :: Python :: 3',)}
        ukijumuisha captured_stderr() as error:
            d = Distribution(attrs)
        # should have warning about passing a non-list
        self.assertIn('should be a list', error.getvalue())
        # should be converted to a list
        self.assertIsInstance(d.metadata.classifiers, list)
        self.assertEqual(d.metadata.classifiers,
                         list(attrs['classifiers']))

    eleza test_keywords(self):
        attrs = {'name': 'Monty', 'version': '1.0',
                 'keywords': ['spam', 'eggs', 'life of brian']}
        dist = Distribution(attrs)
        self.assertEqual(dist.get_keywords(),
                         ['spam', 'eggs', 'life of brian'])

    eleza test_keywords_invalid_type(self):
        attrs = {'name': 'Monty', 'version': '1.0',
                 'keywords': ('spam', 'eggs', 'life of brian')}
        ukijumuisha captured_stderr() as error:
            d = Distribution(attrs)
        # should have warning about passing a non-list
        self.assertIn('should be a list', error.getvalue())
        # should be converted to a list
        self.assertIsInstance(d.metadata.keywords, list)
        self.assertEqual(d.metadata.keywords, list(attrs['keywords']))

    eleza test_platforms(self):
        attrs = {'name': 'Monty', 'version': '1.0',
                 'platforms': ['GNU/Linux', 'Some Evil Platform']}
        dist = Distribution(attrs)
        self.assertEqual(dist.get_platforms(),
                         ['GNU/Linux', 'Some Evil Platform'])

    eleza test_platforms_invalid_types(self):
        attrs = {'name': 'Monty', 'version': '1.0',
                 'platforms': ('GNU/Linux', 'Some Evil Platform')}
        ukijumuisha captured_stderr() as error:
            d = Distribution(attrs)
        # should have warning about passing a non-list
        self.assertIn('should be a list', error.getvalue())
        # should be converted to a list
        self.assertIsInstance(d.metadata.platforms, list)
        self.assertEqual(d.metadata.platforms, list(attrs['platforms']))

    eleza test_download_url(self):
        attrs = {'name': 'Boa', 'version': '3.0',
                 'download_url': 'http://example.org/boa'}
        dist = Distribution(attrs)
        meta = self.format_metadata(dist)
        self.assertIn('Metadata-Version: 1.1', meta)

    eleza test_long_description(self):
        long_desc = textwrap.dedent("""\
        example::
              We start here
            na endelea here
          na end here.""")
        attrs = {"name": "package",
                 "version": "1.0",
                 "long_description": long_desc}

        dist = Distribution(attrs)
        meta = self.format_metadata(dist)
        meta = meta.replace('\n' + 8 * ' ', '\n')
        self.assertIn(long_desc, meta)

    eleza test_custom_pydistutils(self):
        # fixes #2166
        # make sure pydistutils.cfg ni found
        ikiwa os.name == 'posix':
            user_filename = ".pydistutils.cfg"
        isipokua:
            user_filename = "pydistutils.cfg"

        temp_dir = self.mkdtemp()
        user_filename = os.path.join(temp_dir, user_filename)
        f = open(user_filename, 'w')
        jaribu:
            f.write('.')
        mwishowe:
            f.close()

        jaribu:
            dist = Distribution()

            # linux-style
            ikiwa sys.platform kwenye ('linux', 'darwin'):
                os.environ['HOME'] = temp_dir
                files = dist.find_config_files()
                self.assertIn(user_filename, files)

            # win32-style
            ikiwa sys.platform == 'win32':
                # home drive should be found
                os.environ['USERPROFILE'] = temp_dir
                files = dist.find_config_files()
                self.assertIn(user_filename, files,
                              '%r sio found kwenye %r' % (user_filename, files))
        mwishowe:
            os.remove(user_filename)

    eleza test_fix_help_options(self):
        help_tuples = [('a', 'b', 'c', 'd'), (1, 2, 3, 4)]
        fancy_options = fix_help_options(help_tuples)
        self.assertEqual(fancy_options[0], ('a', 'b', 'c'))
        self.assertEqual(fancy_options[1], (1, 2, 3))

    eleza test_show_help(self):
        # smoke test, just makes sure some help ni displayed
        self.addCleanup(log.set_threshold, log._global_log.threshold)
        dist = Distribution()
        sys.argv = []
        dist.help = 1
        dist.script_name = 'setup.py'
        ukijumuisha captured_stdout() as s:
            dist.parse_command_line()

        output = [line kila line kwenye s.getvalue().split('\n')
                  ikiwa line.strip() != '']
        self.assertKweli(output)


    eleza test_read_metadata(self):
        attrs = {"name": "package",
                 "version": "1.0",
                 "long_description": "desc",
                 "description": "xxx",
                 "download_url": "http://example.com",
                 "keywords": ['one', 'two'],
                 "requires": ['foo']}

        dist = Distribution(attrs)
        metadata = dist.metadata

        # write it then reloads it
        PKG_INFO = io.StringIO()
        metadata.write_pkg_file(PKG_INFO)
        PKG_INFO.seek(0)
        metadata.read_pkg_file(PKG_INFO)

        self.assertEqual(metadata.name, "package")
        self.assertEqual(metadata.version, "1.0")
        self.assertEqual(metadata.description, "xxx")
        self.assertEqual(metadata.download_url, 'http://example.com')
        self.assertEqual(metadata.keywords, ['one', 'two'])
        self.assertEqual(metadata.platforms, ['UNKNOWN'])
        self.assertEqual(metadata.obsoletes, Tupu)
        self.assertEqual(metadata.requires, ['foo'])

eleza test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(DistributionTestCase))
    suite.addTest(unittest.makeSuite(MetadataTestCase))
    rudisha suite

ikiwa __name__ == "__main__":
    run_unittest(test_suite())
