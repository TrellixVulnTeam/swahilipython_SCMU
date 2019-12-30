agiza os
agiza platform
agiza subprocess
agiza sys
agiza unittest
kutoka unittest agiza mock

kutoka test agiza support


kundi PlatformTest(unittest.TestCase):
    eleza clear_caches(self):
        platform._platform_cache.clear()
        platform._sys_version_cache.clear()
        platform._uname_cache = Tupu

    eleza test_architecture(self):
        res = platform.architecture()

    @support.skip_unless_symlink
    eleza test_architecture_via_symlink(self): # issue3762
        ukijumuisha support.PythonSymlink() kama py:
            cmd = "-c", "agiza platform; andika(platform.architecture())"
            self.assertEqual(py.call_real(*cmd), py.call_link(*cmd))

    eleza test_platform(self):
        kila aliased kwenye (Uongo, Kweli):
            kila terse kwenye (Uongo, Kweli):
                res = platform.platform(aliased, terse)

    eleza test_system(self):
        res = platform.system()

    eleza test_node(self):
        res = platform.node()

    eleza test_release(self):
        res = platform.release()

    eleza test_version(self):
        res = platform.version()

    eleza test_machine(self):
        res = platform.machine()

    eleza test_processor(self):
        res = platform.processor()

    eleza setUp(self):
        self.save_version = sys.version
        self.save_git = sys._git
        self.save_platform = sys.platform

    eleza tearDown(self):
        sys.version = self.save_version
        sys._git = self.save_git
        sys.platform = self.save_platform

    eleza test_sys_version(self):
        # Old test.
        kila input, output kwenye (
            ('2.4.3 (#1, Jun 21 2006, 13:54:21) \n[GCC 3.3.4 (pre 3.3.5 20040809)]',
             ('CPython', '2.4.3', '', '', '1', 'Jun 21 2006 13:54:21', 'GCC 3.3.4 (pre 3.3.5 20040809)')),
            ('IronPython 1.0.60816 on .NET 2.0.50727.42',
             ('IronPython', '1.0.60816', '', '', '', '', '.NET 2.0.50727.42')),
            ('IronPython 1.0 (1.0.61005.1977) on .NET 2.0.50727.42',
             ('IronPython', '1.0.0', '', '', '', '', '.NET 2.0.50727.42')),
            ('2.4.3 (truncation, date, t) \n[GCC]',
             ('CPython', '2.4.3', '', '', 'truncation', 'date t', 'GCC')),
            ('2.4.3 (truncation, date, ) \n[GCC]',
             ('CPython', '2.4.3', '', '', 'truncation', 'date', 'GCC')),
            ('2.4.3 (truncation, date,) \n[GCC]',
             ('CPython', '2.4.3', '', '', 'truncation', 'date', 'GCC')),
            ('2.4.3 (truncation, date) \n[GCC]',
             ('CPython', '2.4.3', '', '', 'truncation', 'date', 'GCC')),
            ('2.4.3 (truncation, d) \n[GCC]',
             ('CPython', '2.4.3', '', '', 'truncation', 'd', 'GCC')),
            ('2.4.3 (truncation, ) \n[GCC]',
             ('CPython', '2.4.3', '', '', 'truncation', '', 'GCC')),
            ('2.4.3 (truncation,) \n[GCC]',
             ('CPython', '2.4.3', '', '', 'truncation', '', 'GCC')),
            ('2.4.3 (truncation) \n[GCC]',
             ('CPython', '2.4.3', '', '', 'truncation', '', 'GCC')),
            ):
            # branch na revision are sio "parsed", but fetched
            # kutoka sys._git.  Ignore them
            (name, version, branch, revision, buildno, builddate, compiler) \
                   = platform._sys_version(input)
            self.assertEqual(
                (name, version, '', '', buildno, builddate, compiler), output)

        # Tests kila python_implementation(), python_version(), python_branch(),
        # python_revision(), python_build(), na python_compiler().
        sys_versions = {
            ("2.6.1 (r261:67515, Dec  6 2008, 15:26:00) \n[GCC 4.0.1 (Apple Computer, Inc. build 5370)]",
             ('CPython', 'tags/r261', '67515'), self.save_platform)
            :
                ("CPython", "2.6.1", "tags/r261", "67515",
                 ('r261:67515', 'Dec  6 2008 15:26:00'),
                 'GCC 4.0.1 (Apple Computer, Inc. build 5370)'),

            ("IronPython 2.0 (2.0.0.0) on .NET 2.0.50727.3053", Tupu, "cli")
            :
                ("IronPython", "2.0.0", "", "", ("", ""),
                 ".NET 2.0.50727.3053"),

            ("2.6.1 (IronPython 2.6.1 (2.6.10920.0) on .NET 2.0.50727.1433)", Tupu, "cli")
            :
                ("IronPython", "2.6.1", "", "", ("", ""),
                 ".NET 2.0.50727.1433"),

            ("2.7.4 (IronPython 2.7.4 (2.7.0.40) on Mono 4.0.30319.1 (32-bit))", Tupu, "cli")
            :
                ("IronPython", "2.7.4", "", "", ("", ""),
                 "Mono 4.0.30319.1 (32-bit)"),

            ("2.5 (trunk:6107, Mar 26 2009, 13:02:18) \n[Java HotSpot(TM) Client VM (\"Apple Computer, Inc.\")]",
            ('Jython', 'trunk', '6107'), "java1.5.0_16")
            :
                ("Jython", "2.5.0", "trunk", "6107",
                 ('trunk:6107', 'Mar 26 2009'), "java1.5.0_16"),

            ("2.5.2 (63378, Mar 26 2009, 18:03:29)\n[PyPy 1.0.0]",
             ('PyPy', 'trunk', '63378'), self.save_platform)
            :
                ("PyPy", "2.5.2", "trunk", "63378", ('63378', 'Mar 26 2009'),
                 "")
            }
        kila (version_tag, scm, sys_platform), info kwenye \
                sys_versions.items():
            sys.version = version_tag
            ikiwa scm ni Tupu:
                ikiwa hasattr(sys, "_git"):
                    toa sys._git
            isipokua:
                sys._git = scm
            ikiwa sys_platform ni sio Tupu:
                sys.platform = sys_platform
            self.assertEqual(platform.python_implementation(), info[0])
            self.assertEqual(platform.python_version(), info[1])
            self.assertEqual(platform.python_branch(), info[2])
            self.assertEqual(platform.python_revision(), info[3])
            self.assertEqual(platform.python_build(), info[4])
            self.assertEqual(platform.python_compiler(), info[5])

    eleza test_system_alias(self):
        res = platform.system_alias(
            platform.system(),
            platform.release(),
            platform.version(),
        )

    eleza test_uname(self):
        res = platform.uname()
        self.assertKweli(any(res))
        self.assertEqual(res[0], res.system)
        self.assertEqual(res[1], res.node)
        self.assertEqual(res[2], res.release)
        self.assertEqual(res[3], res.version)
        self.assertEqual(res[4], res.machine)
        self.assertEqual(res[5], res.processor)

    @unittest.skipUnless(sys.platform.startswith('win'), "windows only test")
    eleza test_uname_win32_ARCHITEW6432(self):
        # Issue 7860: make sure we get architecture kutoka the correct variable
        # on 64 bit Windows: ikiwa PROCESSOR_ARCHITEW6432 exists we should be
        # using it, per
        # http://blogs.msdn.com/david.wang/archive/2006/03/26/HOWTO-Detect-Process-Bitness.aspx
        jaribu:
            ukijumuisha support.EnvironmentVarGuard() kama environ:
                ikiwa 'PROCESSOR_ARCHITEW6432' kwenye environ:
                    toa environ['PROCESSOR_ARCHITEW6432']
                environ['PROCESSOR_ARCHITECTURE'] = 'foo'
                platform._uname_cache = Tupu
                system, node, release, version, machine, processor = platform.uname()
                self.assertEqual(machine, 'foo')
                environ['PROCESSOR_ARCHITEW6432'] = 'bar'
                platform._uname_cache = Tupu
                system, node, release, version, machine, processor = platform.uname()
                self.assertEqual(machine, 'bar')
        mwishowe:
            platform._uname_cache = Tupu

    eleza test_java_ver(self):
        res = platform.java_ver()
        ikiwa sys.platform == 'java':
            self.assertKweli(all(res))

    eleza test_win32_ver(self):
        res = platform.win32_ver()

    eleza test_mac_ver(self):
        res = platform.mac_ver()

        ikiwa platform.uname().system == 'Darwin':
            # We are on a macOS system, check that the right version
            # information ni returned
            output = subprocess.check_output(['sw_vers'], text=Kweli)
            kila line kwenye output.splitlines():
                ikiwa line.startswith('ProductVersion:'):
                    real_ver = line.strip().split()[-1]
                    koma
            isipokua:
                self.fail(f"failed to parse sw_vers output: {output!r}")

            result_list = res[0].split('.')
            expect_list = real_ver.split('.')
            len_diff = len(result_list) - len(expect_list)
            # On Snow Leopard, sw_vers reports 10.6.0 kama 10.6
            ikiwa len_diff > 0:
                expect_list.extend(['0'] * len_diff)
            self.assertEqual(result_list, expect_list)

            # res[1] claims to contain
            # (version, dev_stage, non_release_version)
            # That information ni no longer available
            self.assertEqual(res[1], ('', '', ''))

            ikiwa sys.byteorder == 'little':
                self.assertIn(res[2], ('i386', 'x86_64'))
            isipokua:
                self.assertEqual(res[2], 'PowerPC')


    @unittest.skipUnless(sys.platform == 'darwin', "OSX only test")
    eleza test_mac_ver_with_fork(self):
        # Issue7895: platform.mac_ver() crashes when using fork without exec
        #
        # This test checks that the fix kila that issue works.
        #
        pid = os.fork()
        ikiwa pid == 0:
            # child
            info = platform.mac_ver()
            os._exit(0)

        isipokua:
            # parent
            cpid, sts = os.waitpid(pid, 0)
            self.assertEqual(cpid, pid)
            self.assertEqual(sts, 0)

    eleza test_libc_ver(self):
        # check that libc_ver(executable) doesn't ashiria an exception
        ikiwa os.path.isdir(sys.executable) na \
           os.path.exists(sys.executable+'.exe'):
            # Cygwin horror
            executable = sys.executable + '.exe'
        lasivyo sys.platform == "win32" na sio os.path.exists(sys.executable):
            # App symlink appears to sio exist, but we want the
            # real executable here anyway
            agiza _winapi
            executable = _winapi.GetModuleFileName(0)
        isipokua:
            executable = sys.executable
        platform.libc_ver(executable)

        filename = support.TESTFN
        self.addCleanup(support.unlink, filename)

        ukijumuisha mock.patch('os.confstr', create=Kweli, return_value='mock 1.0'):
            # test os.confstr() code path
            self.assertEqual(platform.libc_ver(), ('mock', '1.0'))

            # test the different regular expressions
            kila data, expected kwenye (
                (b'__libc_init', ('libc', '')),
                (b'GLIBC_2.9', ('glibc', '2.9')),
                (b'libc.so.1.2.5', ('libc', '1.2.5')),
                (b'libc_pthread.so.1.2.5', ('libc', '1.2.5_pthread')),
                (b'', ('', '')),
            ):
                ukijumuisha open(filename, 'wb') kama fp:
                    fp.write(b'[xxx%sxxx]' % data)
                    fp.flush()

                # os.confstr() must sio be used ikiwa executable ni set
                self.assertEqual(platform.libc_ver(executable=filename),
                                 expected)

        # binary containing multiple versions: get the most recent,
        # make sure that 1.9 ni seen kama older than 1.23.4
        chunksize = 16384
        ukijumuisha open(filename, 'wb') kama f:
            # test match at chunk boundary
            f.write(b'x'*(chunksize - 10))
            f.write(b'GLIBC_1.23.4\0GLIBC_1.9\0GLIBC_1.21\0')
        self.assertEqual(platform.libc_ver(filename, chunksize=chunksize),
                         ('glibc', '1.23.4'))

    @support.cpython_only
    eleza test__comparable_version(self):
        kutoka platform agiza _comparable_version kama V
        self.assertEqual(V('1.2.3'), V('1.2.3'))
        self.assertLess(V('1.2.3'), V('1.2.10'))
        self.assertEqual(V('1.2.3.4'), V('1_2-3+4'))
        self.assertLess(V('1.2spam'), V('1.2dev'))
        self.assertLess(V('1.2dev'), V('1.2alpha'))
        self.assertLess(V('1.2dev'), V('1.2a'))
        self.assertLess(V('1.2alpha'), V('1.2beta'))
        self.assertLess(V('1.2a'), V('1.2b'))
        self.assertLess(V('1.2beta'), V('1.2c'))
        self.assertLess(V('1.2b'), V('1.2c'))
        self.assertLess(V('1.2c'), V('1.2RC'))
        self.assertLess(V('1.2c'), V('1.2rc'))
        self.assertLess(V('1.2RC'), V('1.2.0'))
        self.assertLess(V('1.2rc'), V('1.2.0'))
        self.assertLess(V('1.2.0'), V('1.2pl'))
        self.assertLess(V('1.2.0'), V('1.2p'))

        self.assertLess(V('1.5.1'), V('1.5.2b2'))
        self.assertLess(V('3.10a'), V('161'))
        self.assertEqual(V('8.02'), V('8.02'))
        self.assertLess(V('3.4j'), V('1996.07.12'))
        self.assertLess(V('3.1.1.6'), V('3.2.pl0'))
        self.assertLess(V('2g6'), V('11g'))
        self.assertLess(V('0.9'), V('2.2'))
        self.assertLess(V('1.2'), V('1.2.1'))
        self.assertLess(V('1.1'), V('1.2.2'))
        self.assertLess(V('1.1'), V('1.2'))
        self.assertLess(V('1.2.1'), V('1.2.2'))
        self.assertLess(V('1.2'), V('1.2.2'))
        self.assertLess(V('0.4'), V('0.4.0'))
        self.assertLess(V('1.13++'), V('5.5.kw'))
        self.assertLess(V('0.960923'), V('2.2beta29'))


    eleza test_macos(self):
        self.addCleanup(self.clear_caches)

        uname = ('Darwin', 'hostname', '17.7.0',
                 ('Darwin Kernel Version 17.7.0: '
                  'Thu Jun 21 22:53:14 PDT 2018; '
                  'root:xnu-4570.71.2~1/RELEASE_X86_64'),
                 'x86_64', 'i386')
        arch = ('64bit', '')
        ukijumuisha mock.patch.object(platform, 'uname', return_value=uname), \
             mock.patch.object(platform, 'architecture', return_value=arch):
            kila mac_ver, expected_terse, expected kwenye [
                # darwin: mac_ver() returns empty strings
                (('', '', ''),
                 'Darwin-17.7.0',
                 'Darwin-17.7.0-x86_64-i386-64bit'),
                # macOS: mac_ver() returns macOS version
                (('10.13.6', ('', '', ''), 'x86_64'),
                 'macOS-10.13.6',
                 'macOS-10.13.6-x86_64-i386-64bit'),
            ]:
                ukijumuisha mock.patch.object(platform, 'mac_ver',
                                       return_value=mac_ver):
                    self.clear_caches()
                    self.assertEqual(platform.platform(terse=1), expected_terse)
                    self.assertEqual(platform.platform(), expected)


ikiwa __name__ == '__main__':
    unittest.main()
