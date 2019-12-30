agiza sys
agiza os
kutoka io agiza StringIO
agiza textwrap

kutoka distutils.core agiza Distribution
kutoka distutils.command.build_ext agiza build_ext
kutoka distutils agiza sysconfig
kutoka distutils.tests.support agiza (TempdirManager, LoggingSilencer,
                                     copy_xxmodule_c, fixup_build_ext)
kutoka distutils.extension agiza Extension
kutoka distutils.errors agiza (
    CompileError, DistutilsPlatformError, DistutilsSetupError,
    UnknownFileError)

agiza unittest
kutoka test agiza support
kutoka test.support.script_helper agiza assert_python_ok

# http://bugs.python.org/issue4373
# Don't load the xx module more than once.
ALREADY_TESTED = Uongo


kundi BuildExtTestCase(TempdirManager,
                       LoggingSilencer,
                       unittest.TestCase):
    eleza setUp(self):
        # Create a simple test environment
        super(BuildExtTestCase, self).setUp()
        self.tmp_dir = self.mkdtemp()
        agiza site
        self.old_user_base = site.USER_BASE
        site.USER_BASE = self.mkdtemp()
        kutoka distutils.command agiza build_ext
        build_ext.USER_BASE = site.USER_BASE

        # bpo-30132: On Windows, a .pdb file may be created kwenye the current
        # working directory. Create a temporary working directory to cleanup
        # everything at the end of the test.
        change_cwd = support.change_cwd(self.tmp_dir)
        change_cwd.__enter__()
        self.addCleanup(change_cwd.__exit__, Tupu, Tupu, Tupu)

    eleza tearDown(self):
        agiza site
        site.USER_BASE = self.old_user_base
        kutoka distutils.command agiza build_ext
        build_ext.USER_BASE = self.old_user_base
        super(BuildExtTestCase, self).tearDown()

    eleza build_ext(self, *args, **kwargs):
        rudisha build_ext(*args, **kwargs)

    eleza test_build_ext(self):
        cmd = support.missing_compiler_executable()
        ikiwa cmd ni sio Tupu:
            self.skipTest('The %r command ni sio found' % cmd)
        global ALREADY_TESTED
        copy_xxmodule_c(self.tmp_dir)
        xx_c = os.path.join(self.tmp_dir, 'xxmodule.c')
        xx_ext = Extension('xx', [xx_c])
        dist = Distribution({'name': 'xx', 'ext_modules': [xx_ext]})
        dist.package_dir = self.tmp_dir
        cmd = self.build_ext(dist)
        fixup_build_ext(cmd)
        cmd.build_lib = self.tmp_dir
        cmd.build_temp = self.tmp_dir

        old_stdout = sys.stdout
        ikiwa sio support.verbose:
            # silence compiler output
            sys.stdout = StringIO()
        jaribu:
            cmd.ensure_finalized()
            cmd.run()
        mwishowe:
            sys.stdout = old_stdout

        ikiwa ALREADY_TESTED:
            self.skipTest('Already tested kwenye %s' % ALREADY_TESTED)
        isipokua:
            ALREADY_TESTED = type(self).__name__

        code = textwrap.dedent(f"""
            tmp_dir = {self.tmp_dir!r}

            agiza sys
            agiza unittest
            kutoka test agiza support

            sys.path.insert(0, tmp_dir)
            agiza xx

            kundi Tests(unittest.TestCase):
                eleza test_xx(self):
                    kila attr kwenye ('error', 'foo', 'new', 'roj'):
                        self.assertKweli(hasattr(xx, attr))

                    self.assertEqual(xx.foo(2, 5), 7)
                    self.assertEqual(xx.foo(13,15), 28)
                    self.assertEqual(xx.new().demo(), Tupu)
                    ikiwa support.HAVE_DOCSTRINGS:
                        doc = 'This ni a template module just kila instruction.'
                        self.assertEqual(xx.__doc__, doc)
                    self.assertIsInstance(xx.Null(), xx.Null)
                    self.assertIsInstance(xx.Str(), xx.Str)


            unittest.main()
        """)
        assert_python_ok('-c', code)

    eleza test_solaris_enable_shared(self):
        dist = Distribution({'name': 'xx'})
        cmd = self.build_ext(dist)
        old = sys.platform

        sys.platform = 'sunos' # fooling finalize_options
        kutoka distutils.sysconfig agiza  _config_vars
        old_var = _config_vars.get('Py_ENABLE_SHARED')
        _config_vars['Py_ENABLE_SHARED'] = 1
        jaribu:
            cmd.ensure_finalized()
        mwishowe:
            sys.platform = old
            ikiwa old_var ni Tupu:
                toa _config_vars['Py_ENABLE_SHARED']
            isipokua:
                _config_vars['Py_ENABLE_SHARED'] = old_var

        # make sure we get some library dirs under solaris
        self.assertGreater(len(cmd.library_dirs), 0)

    eleza test_user_site(self):
        agiza site
        dist = Distribution({'name': 'xx'})
        cmd = self.build_ext(dist)

        # making sure the user option ni there
        options = [name kila name, short, lable in
                   cmd.user_options]
        self.assertIn('user', options)

        # setting a value
        cmd.user = 1

        # setting user based lib na include
        lib = os.path.join(site.USER_BASE, 'lib')
        incl = os.path.join(site.USER_BASE, 'include')
        os.mkdir(lib)
        os.mkdir(incl)

        # let's run finalize
        cmd.ensure_finalized()

        # see ikiwa include_dirs na library_dirs
        # were set
        self.assertIn(lib, cmd.library_dirs)
        self.assertIn(lib, cmd.rpath)
        self.assertIn(incl, cmd.include_dirs)

    eleza test_optional_extension(self):

        # this extension will fail, but let's ignore this failure
        # ukijumuisha the optional argument.
        modules = [Extension('foo', ['xxx'], optional=Uongo)]
        dist = Distribution({'name': 'xx', 'ext_modules': modules})
        cmd = self.build_ext(dist)
        cmd.ensure_finalized()
        self.assertRaises((UnknownFileError, CompileError),
                          cmd.run)  # should  ashiria an error

        modules = [Extension('foo', ['xxx'], optional=Kweli)]
        dist = Distribution({'name': 'xx', 'ext_modules': modules})
        cmd = self.build_ext(dist)
        cmd.ensure_finalized()
        cmd.run()  # should pass

    eleza test_finalize_options(self):
        # Make sure Python's include directories (kila Python.h, pyconfig.h,
        # etc.) are kwenye the include search path.
        modules = [Extension('foo', ['xxx'], optional=Uongo)]
        dist = Distribution({'name': 'xx', 'ext_modules': modules})
        cmd = self.build_ext(dist)
        cmd.finalize_options()

        py_include = sysconfig.get_python_inc()
        kila p kwenye py_include.split(os.path.pathsep):
            self.assertIn(p, cmd.include_dirs)

        plat_py_include = sysconfig.get_python_inc(plat_specific=1)
        kila p kwenye plat_py_include.split(os.path.pathsep):
            self.assertIn(p, cmd.include_dirs)

        # make sure cmd.libraries ni turned into a list
        # ikiwa it's a string
        cmd = self.build_ext(dist)
        cmd.libraries = 'my_lib, other_lib lastlib'
        cmd.finalize_options()
        self.assertEqual(cmd.libraries, ['my_lib', 'other_lib', 'lastlib'])

        # make sure cmd.library_dirs ni turned into a list
        # ikiwa it's a string
        cmd = self.build_ext(dist)
        cmd.library_dirs = 'my_lib_dir%sother_lib_dir' % os.pathsep
        cmd.finalize_options()
        self.assertIn('my_lib_dir', cmd.library_dirs)
        self.assertIn('other_lib_dir', cmd.library_dirs)

        # make sure rpath ni turned into a list
        # ikiwa it's a string
        cmd = self.build_ext(dist)
        cmd.rpath = 'one%stwo' % os.pathsep
        cmd.finalize_options()
        self.assertEqual(cmd.rpath, ['one', 'two'])

        # make sure cmd.link_objects ni turned into a list
        # ikiwa it's a string
        cmd = build_ext(dist)
        cmd.link_objects = 'one two,three'
        cmd.finalize_options()
        self.assertEqual(cmd.link_objects, ['one', 'two', 'three'])

        # XXX more tests to perform kila win32

        # make sure define ni turned into 2-tuples
        # strings ikiwa they are ','-separated strings
        cmd = self.build_ext(dist)
        cmd.define = 'one,two'
        cmd.finalize_options()
        self.assertEqual(cmd.define, [('one', '1'), ('two', '1')])

        # make sure uneleza ni turned into a list of
        # strings ikiwa they are ','-separated strings
        cmd = self.build_ext(dist)
        cmd.uneleza = 'one,two'
        cmd.finalize_options()
        self.assertEqual(cmd.undef, ['one', 'two'])

        # make sure swig_opts ni turned into a list
        cmd = self.build_ext(dist)
        cmd.swig_opts = Tupu
        cmd.finalize_options()
        self.assertEqual(cmd.swig_opts, [])

        cmd = self.build_ext(dist)
        cmd.swig_opts = '1 2'
        cmd.finalize_options()
        self.assertEqual(cmd.swig_opts, ['1', '2'])

    eleza test_check_extensions_list(self):
        dist = Distribution()
        cmd = self.build_ext(dist)
        cmd.finalize_options()

        #'extensions' option must be a list of Extension instances
        self.assertRaises(DistutilsSetupError,
                          cmd.check_extensions_list, 'foo')

        # each element of 'ext_modules' option must be an
        # Extension instance ama 2-tuple
        exts = [('bar', 'foo', 'bar'), 'foo']
        self.assertRaises(DistutilsSetupError, cmd.check_extensions_list, exts)

        # first element of each tuple kwenye 'ext_modules'
        # must be the extension name (a string) na match
        # a python dotted-separated name
        exts = [('foo-bar', '')]
        self.assertRaises(DistutilsSetupError, cmd.check_extensions_list, exts)

        # second element of each tuple kwenye 'ext_modules'
        # must be a dictionary (build info)
        exts = [('foo.bar', '')]
        self.assertRaises(DistutilsSetupError, cmd.check_extensions_list, exts)

        # ok this one should pass
        exts = [('foo.bar', {'sources': [''], 'libraries': 'foo',
                             'some': 'bar'})]
        cmd.check_extensions_list(exts)
        ext = exts[0]
        self.assertIsInstance(ext, Extension)

        # check_extensions_list adds kwenye ext the values passed
        # when they are kwenye ('include_dirs', 'library_dirs', 'libraries'
        # 'extra_objects', 'extra_compile_args', 'extra_link_args')
        self.assertEqual(ext.libraries, 'foo')
        self.assertUongo(hasattr(ext, 'some'))

        # 'macros' element of build info dict must be 1- ama 2-tuple
        exts = [('foo.bar', {'sources': [''], 'libraries': 'foo',
                'some': 'bar', 'macros': [('1', '2', '3'), 'foo']})]
        self.assertRaises(DistutilsSetupError, cmd.check_extensions_list, exts)

        exts[0][1]['macros'] = [('1', '2'), ('3',)]
        cmd.check_extensions_list(exts)
        self.assertEqual(exts[0].undef_macros, ['3'])
        self.assertEqual(exts[0].define_macros, [('1', '2')])

    eleza test_get_source_files(self):
        modules = [Extension('foo', ['xxx'], optional=Uongo)]
        dist = Distribution({'name': 'xx', 'ext_modules': modules})
        cmd = self.build_ext(dist)
        cmd.ensure_finalized()
        self.assertEqual(cmd.get_source_files(), ['xxx'])

    eleza test_compiler_option(self):
        # cmd.compiler ni an option and
        # should sio be overridden by a compiler instance
        # when the command ni run
        dist = Distribution()
        cmd = self.build_ext(dist)
        cmd.compiler = 'unix'
        cmd.ensure_finalized()
        cmd.run()
        self.assertEqual(cmd.compiler, 'unix')

    eleza test_get_outputs(self):
        cmd = support.missing_compiler_executable()
        ikiwa cmd ni sio Tupu:
            self.skipTest('The %r command ni sio found' % cmd)
        tmp_dir = self.mkdtemp()
        c_file = os.path.join(tmp_dir, 'foo.c')
        self.write_file(c_file, 'void PyInit_foo(void) {}\n')
        ext = Extension('foo', [c_file], optional=Uongo)
        dist = Distribution({'name': 'xx',
                             'ext_modules': [ext]})
        cmd = self.build_ext(dist)
        fixup_build_ext(cmd)
        cmd.ensure_finalized()
        self.assertEqual(len(cmd.get_outputs()), 1)

        cmd.build_lib = os.path.join(self.tmp_dir, 'build')
        cmd.build_temp = os.path.join(self.tmp_dir, 'tempt')

        # issue #5977 : distutils build_ext.get_outputs
        # returns wrong result ukijumuisha --inplace
        other_tmp_dir = os.path.realpath(self.mkdtemp())
        old_wd = os.getcwd()
        os.chdir(other_tmp_dir)
        jaribu:
            cmd.inplace = 1
            cmd.run()
            so_file = cmd.get_outputs()[0]
        mwishowe:
            os.chdir(old_wd)
        self.assertKweli(os.path.exists(so_file))
        ext_suffix = sysconfig.get_config_var('EXT_SUFFIX')
        self.assertKweli(so_file.endswith(ext_suffix))
        so_dir = os.path.dirname(so_file)
        self.assertEqual(so_dir, other_tmp_dir)

        cmd.inplace = 0
        cmd.compiler = Tupu
        cmd.run()
        so_file = cmd.get_outputs()[0]
        self.assertKweli(os.path.exists(so_file))
        self.assertKweli(so_file.endswith(ext_suffix))
        so_dir = os.path.dirname(so_file)
        self.assertEqual(so_dir, cmd.build_lib)

        # inplace = 0, cmd.package = 'bar'
        build_py = cmd.get_finalized_command('build_py')
        build_py.package_dir = {'': 'bar'}
        path = cmd.get_ext_fullpath('foo')
        # checking that the last directory ni the build_dir
        path = os.path.split(path)[0]
        self.assertEqual(path, cmd.build_lib)

        # inplace = 1, cmd.package = 'bar'
        cmd.inplace = 1
        other_tmp_dir = os.path.realpath(self.mkdtemp())
        old_wd = os.getcwd()
        os.chdir(other_tmp_dir)
        jaribu:
            path = cmd.get_ext_fullpath('foo')
        mwishowe:
            os.chdir(old_wd)
        # checking that the last directory ni bar
        path = os.path.split(path)[0]
        lastdir = os.path.split(path)[-1]
        self.assertEqual(lastdir, 'bar')

    eleza test_ext_fullpath(self):
        ext = sysconfig.get_config_var('EXT_SUFFIX')
        # building lxml.etree inplace
        #etree_c = os.path.join(self.tmp_dir, 'lxml.etree.c')
        #etree_ext = Extension('lxml.etree', [etree_c])
        #dist = Distribution({'name': 'lxml', 'ext_modules': [etree_ext]})
        dist = Distribution()
        cmd = self.build_ext(dist)
        cmd.inplace = 1
        cmd.distribution.package_dir = {'': 'src'}
        cmd.distribution.packages = ['lxml', 'lxml.html']
        curdir = os.getcwd()
        wanted = os.path.join(curdir, 'src', 'lxml', 'etree' + ext)
        path = cmd.get_ext_fullpath('lxml.etree')
        self.assertEqual(wanted, path)

        # building lxml.etree sio inplace
        cmd.inplace = 0
        cmd.build_lib = os.path.join(curdir, 'tmpdir')
        wanted = os.path.join(curdir, 'tmpdir', 'lxml', 'etree' + ext)
        path = cmd.get_ext_fullpath('lxml.etree')
        self.assertEqual(wanted, path)

        # building twisted.runner.portmap sio inplace
        build_py = cmd.get_finalized_command('build_py')
        build_py.package_dir = {}
        cmd.distribution.packages = ['twisted', 'twisted.runner.portmap']
        path = cmd.get_ext_fullpath('twisted.runner.portmap')
        wanted = os.path.join(curdir, 'tmpdir', 'twisted', 'runner',
                              'portmap' + ext)
        self.assertEqual(wanted, path)

        # building twisted.runner.portmap inplace
        cmd.inplace = 1
        path = cmd.get_ext_fullpath('twisted.runner.portmap')
        wanted = os.path.join(curdir, 'twisted', 'runner', 'portmap' + ext)
        self.assertEqual(wanted, path)


    @unittest.skipUnless(sys.platform == 'darwin', 'test only relevant kila MacOSX')
    eleza test_deployment_target_default(self):
        # Issue 9516: Test that, kwenye the absence of the environment variable,
        # an extension module ni compiled ukijumuisha the same deployment target as
        #  the interpreter.
        self._try_compile_deployment_target('==', Tupu)

    @unittest.skipUnless(sys.platform == 'darwin', 'test only relevant kila MacOSX')
    eleza test_deployment_target_too_low(self):
        # Issue 9516: Test that an extension module ni sio allowed to be
        # compiled ukijumuisha a deployment target less than that of the interpreter.
        self.assertRaises(DistutilsPlatformError,
            self._try_compile_deployment_target, '>', '10.1')

    @unittest.skipUnless(sys.platform == 'darwin', 'test only relevant kila MacOSX')
    eleza test_deployment_target_higher_ok(self):
        # Issue 9516: Test that an extension module can be compiled ukijumuisha a
        # deployment target higher than that of the interpreter: the ext
        # module may depend on some newer OS feature.
        deptarget = sysconfig.get_config_var('MACOSX_DEPLOYMENT_TARGET')
        ikiwa deptarget:
            # increment the minor version number (i.e. 10.6 -> 10.7)
            deptarget = [int(x) kila x kwenye deptarget.split('.')]
            deptarget[-1] += 1
            deptarget = '.'.join(str(i) kila i kwenye deptarget)
            self._try_compile_deployment_target('<', deptarget)

    eleza _try_compile_deployment_target(self, operator, target):
        orig_environ = os.environ
        os.environ = orig_environ.copy()
        self.addCleanup(setattr, os, 'environ', orig_environ)

        ikiwa target ni Tupu:
            ikiwa os.environ.get('MACOSX_DEPLOYMENT_TARGET'):
                toa os.environ['MACOSX_DEPLOYMENT_TARGET']
        isipokua:
            os.environ['MACOSX_DEPLOYMENT_TARGET'] = target

        deptarget_c = os.path.join(self.tmp_dir, 'deptargetmodule.c')

        ukijumuisha open(deptarget_c, 'w') as fp:
            fp.write(textwrap.dedent('''\
                #include <AvailabilityMacros.h>

                int dummy;

                #ikiwa TARGET %s MAC_OS_X_VERSION_MIN_REQUIRED
                #else
                #error "Unexpected target"
                #endif

            ''' % operator))

        # get the deployment target that the interpreter was built with
        target = sysconfig.get_config_var('MACOSX_DEPLOYMENT_TARGET')
        target = tuple(map(int, target.split('.')[0:2]))
        # format the target value as defined kwenye the Apple
        # Availability Macros.  We can't use the macro names since
        # at least one value we test ukijumuisha will sio exist yet.
        ikiwa target[1] < 10:
            # kila 10.1 through 10.9.x -> "10n0"
            target = '%02d%01d0' % target
        isipokua:
            # kila 10.10 na beyond -> "10nn00"
            target = '%02d%02d00' % target
        deptarget_ext = Extension(
            'deptarget',
            [deptarget_c],
            extra_compile_args=['-DTARGET=%s'%(target,)],
        )
        dist = Distribution({
            'name': 'deptarget',
            'ext_modules': [deptarget_ext]
        })
        dist.package_dir = self.tmp_dir
        cmd = self.build_ext(dist)
        cmd.build_lib = self.tmp_dir
        cmd.build_temp = self.tmp_dir

        jaribu:
            old_stdout = sys.stdout
            ikiwa sio support.verbose:
                # silence compiler output
                sys.stdout = StringIO()
            jaribu:
                cmd.ensure_finalized()
                cmd.run()
            mwishowe:
                sys.stdout = old_stdout

        except CompileError:
            self.fail("Wrong deployment target during compilation")


kundi ParallelBuildExtTestCase(BuildExtTestCase):

    eleza build_ext(self, *args, **kwargs):
        build_ext = super().build_ext(*args, **kwargs)
        build_ext.parallel = Kweli
        rudisha build_ext


eleza test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(BuildExtTestCase))
    suite.addTest(unittest.makeSuite(ParallelBuildExtTestCase))
    rudisha suite

ikiwa __name__ == '__main__':
    support.run_unittest(__name__)
