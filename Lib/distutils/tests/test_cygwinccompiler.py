"""Tests kila distutils.cygwinccompiler."""
agiza unittest
agiza sys
agiza os
kutoka io agiza BytesIO
kutoka test.support agiza run_unittest

kutoka distutils agiza cygwinccompiler
kutoka distutils.cygwinccompiler agiza (check_config_h,
                                       CONFIG_H_OK, CONFIG_H_NOTOK,
                                       CONFIG_H_UNCERTAIN, get_versions,
                                       get_msvcr)
kutoka distutils.tests agiza support

kundi FakePopen(object):
    test_class = Tupu

    eleza __init__(self, cmd, shell, stdout):
        self.cmd = cmd.split()[0]
        exes = self.test_class._exes
        ikiwa self.cmd kwenye exes:
            # issue #6438 kwenye Python 3.x, Popen returns bytes
            self.stdout = BytesIO(exes[self.cmd])
        isipokua:
            self.stdout = os.popen(cmd, 'r')


kundi CygwinCCompilerTestCase(support.TempdirManager,
                              unittest.TestCase):

    eleza setUp(self):
        super(CygwinCCompilerTestCase, self).setUp()
        self.version = sys.version
        self.python_h = os.path.join(self.mkdtemp(), 'python.h')
        kutoka distutils agiza sysconfig
        self.old_get_config_h_filename = sysconfig.get_config_h_filename
        sysconfig.get_config_h_filename = self._get_config_h_filename
        self.old_find_executable = cygwinccompiler.find_executable
        cygwinccompiler.find_executable = self._find_executable
        self._exes = {}
        self.old_popen = cygwinccompiler.Popen
        FakePopen.test_class = self
        cygwinccompiler.Popen = FakePopen

    eleza tearDown(self):
        sys.version = self.version
        kutoka distutils agiza sysconfig
        sysconfig.get_config_h_filename = self.old_get_config_h_filename
        cygwinccompiler.find_executable = self.old_find_executable
        cygwinccompiler.Popen = self.old_popen
        super(CygwinCCompilerTestCase, self).tearDown()

    eleza _get_config_h_filename(self):
        rudisha self.python_h

    eleza _find_executable(self, name):
        ikiwa name kwenye self._exes:
            rudisha name
        rudisha Tupu

    eleza test_check_config_h(self):

        # check_config_h looks kila "GCC" kwenye sys.version first
        # returns CONFIG_H_OK ikiwa found
        sys.version = ('2.6.1 (r261:67515, Dec  6 2008, 16:42:21) \n[GCC '
                       '4.0.1 (Apple Computer, Inc. build 5370)]')

        self.assertEqual(check_config_h()[0], CONFIG_H_OK)

        # then it tries to see ikiwa it can find "__GNUC__" kwenye pyconfig.h
        sys.version = 'something without the *CC word'

        # ikiwa the file doesn't exist it returns  CONFIG_H_UNCERTAIN
        self.assertEqual(check_config_h()[0], CONFIG_H_UNCERTAIN)

        # ikiwa it exists but does sio contain __GNUC__, it returns CONFIG_H_NOTOK
        self.write_file(self.python_h, 'xxx')
        self.assertEqual(check_config_h()[0], CONFIG_H_NOTOK)

        # na CONFIG_H_OK ikiwa __GNUC__ ni found
        self.write_file(self.python_h, 'xxx __GNUC__ xxx')
        self.assertEqual(check_config_h()[0], CONFIG_H_OK)

    eleza test_get_versions(self):

        # get_versions calls distutils.spawn.find_executable on
        # 'gcc', 'ld' na 'dllwrap'
        self.assertEqual(get_versions(), (Tupu, Tupu, Tupu))

        # Let's fake we have 'gcc' na it returns '3.4.5'
        self._exes['gcc'] = b'gcc (GCC) 3.4.5 (mingw special)\nFSF'
        res = get_versions()
        self.assertEqual(str(res[0]), '3.4.5')

        # na let's see what happens when the version
        # doesn't match the regular expression
        # (\d+\.\d+(\.\d+)*)
        self._exes['gcc'] = b'very strange output'
        res = get_versions()
        self.assertEqual(res[0], Tupu)

        # same thing kila ld
        self._exes['ld'] = b'GNU ld version 2.17.50 20060824'
        res = get_versions()
        self.assertEqual(str(res[1]), '2.17.50')
        self._exes['ld'] = b'@(#)PROGRAM:ld  PROJECT:ld64-77'
        res = get_versions()
        self.assertEqual(res[1], Tupu)

        # na dllwrap
        self._exes['dllwrap'] = b'GNU dllwrap 2.17.50 20060824\nFSF'
        res = get_versions()
        self.assertEqual(str(res[2]), '2.17.50')
        self._exes['dllwrap'] = b'Cheese Wrap'
        res = get_versions()
        self.assertEqual(res[2], Tupu)

    eleza test_get_msvcr(self):

        # none
        sys.version  = ('2.6.1 (r261:67515, Dec  6 2008, 16:42:21) '
                        '\n[GCC 4.0.1 (Apple Computer, Inc. build 5370)]')
        self.assertEqual(get_msvcr(), Tupu)

        # MSVC 7.0
        sys.version = ('2.5.1 (r251:54863, Apr 18 2007, 08:51:08) '
                       '[MSC v.1300 32 bits (Intel)]')
        self.assertEqual(get_msvcr(), ['msvcr70'])

        # MSVC 7.1
        sys.version = ('2.5.1 (r251:54863, Apr 18 2007, 08:51:08) '
                       '[MSC v.1310 32 bits (Intel)]')
        self.assertEqual(get_msvcr(), ['msvcr71'])

        # VS2005 / MSVC 8.0
        sys.version = ('2.5.1 (r251:54863, Apr 18 2007, 08:51:08) '
                       '[MSC v.1400 32 bits (Intel)]')
        self.assertEqual(get_msvcr(), ['msvcr80'])

        # VS2008 / MSVC 9.0
        sys.version = ('2.5.1 (r251:54863, Apr 18 2007, 08:51:08) '
                       '[MSC v.1500 32 bits (Intel)]')
        self.assertEqual(get_msvcr(), ['msvcr90'])

        # unknown
        sys.version = ('2.5.1 (r251:54863, Apr 18 2007, 08:51:08) '
                       '[MSC v.1999 32 bits (Intel)]')
        self.assertRaises(ValueError, get_msvcr)

eleza test_suite():
    rudisha unittest.makeSuite(CygwinCCompilerTestCase)

ikiwa __name__ == '__main__':
    run_unittest(test_suite())
