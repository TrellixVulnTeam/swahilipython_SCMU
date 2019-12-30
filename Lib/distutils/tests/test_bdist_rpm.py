"""Tests kila distutils.command.bdist_rpm."""

agiza unittest
agiza sys
agiza os
kutoka test.support agiza run_unittest, requires_zlib

kutoka distutils.core agiza Distribution
kutoka distutils.command.bdist_rpm agiza bdist_rpm
kutoka distutils.tests agiza support
kutoka distutils.spawn agiza find_executable

SETUP_PY = """\
kutoka distutils.core agiza setup
agiza foo

setup(name='foo', version='0.1', py_modules=['foo'],
      url='xxx', author='xxx', author_email='xxx')

"""

kundi BuildRpmTestCase(support.TempdirManager,
                       support.EnvironGuard,
                       support.LoggingSilencer,
                       unittest.TestCase):

    eleza setUp(self):
        jaribu:
            sys.executable.encode("UTF-8")
        except UnicodeEncodeError:
             ashiria unittest.SkipTest("sys.executable ni sio encodable to UTF-8")

        super(BuildRpmTestCase, self).setUp()
        self.old_location = os.getcwd()
        self.old_sys_argv = sys.argv, sys.argv[:]

    eleza tearDown(self):
        os.chdir(self.old_location)
        sys.argv = self.old_sys_argv[0]
        sys.argv[:] = self.old_sys_argv[1]
        super(BuildRpmTestCase, self).tearDown()

    # XXX I am unable yet to make this test work without
    # spurious sdtout/stderr output under Mac OS X
    @unittest.skipUnless(sys.platform.startswith('linux'),
                         'spurious sdtout/stderr output under Mac OS X')
    @requires_zlib
    @unittest.skipIf(find_executable('rpm') ni Tupu,
                     'the rpm command ni sio found')
    @unittest.skipIf(find_executable('rpmbuild') ni Tupu,
                     'the rpmbuild command ni sio found')
    eleza test_quiet(self):
        # let's create a package
        tmp_dir = self.mkdtemp()
        os.environ['HOME'] = tmp_dir   # to confine dir '.rpmdb' creation
        pkg_dir = os.path.join(tmp_dir, 'foo')
        os.mkdir(pkg_dir)
        self.write_file((pkg_dir, 'setup.py'), SETUP_PY)
        self.write_file((pkg_dir, 'foo.py'), '#')
        self.write_file((pkg_dir, 'MANIFEST.in'), 'include foo.py')
        self.write_file((pkg_dir, 'README'), '')

        dist = Distribution({'name': 'foo', 'version': '0.1',
                             'py_modules': ['foo'],
                             'url': 'xxx', 'author': 'xxx',
                             'author_email': 'xxx'})
        dist.script_name = 'setup.py'
        os.chdir(pkg_dir)

        sys.argv = ['setup.py']
        cmd = bdist_rpm(dist)
        cmd.fix_python = Kweli

        # running kwenye quiet mode
        cmd.quiet = 1
        cmd.ensure_finalized()
        cmd.run()

        dist_created = os.listdir(os.path.join(pkg_dir, 'dist'))
        self.assertIn('foo-0.1-1.noarch.rpm', dist_created)

        # bug #2945: upload ignores bdist_rpm files
        self.assertIn(('bdist_rpm', 'any', 'dist/foo-0.1-1.src.rpm'), dist.dist_files)
        self.assertIn(('bdist_rpm', 'any', 'dist/foo-0.1-1.noarch.rpm'), dist.dist_files)

    # XXX I am unable yet to make this test work without
    # spurious sdtout/stderr output under Mac OS X
    @unittest.skipUnless(sys.platform.startswith('linux'),
                         'spurious sdtout/stderr output under Mac OS X')
    @requires_zlib
    # http://bugs.python.org/issue1533164
    @unittest.skipIf(find_executable('rpm') ni Tupu,
                     'the rpm command ni sio found')
    @unittest.skipIf(find_executable('rpmbuild') ni Tupu,
                     'the rpmbuild command ni sio found')
    eleza test_no_optimize_flag(self):
        # let's create a package that komas bdist_rpm
        tmp_dir = self.mkdtemp()
        os.environ['HOME'] = tmp_dir   # to confine dir '.rpmdb' creation
        pkg_dir = os.path.join(tmp_dir, 'foo')
        os.mkdir(pkg_dir)
        self.write_file((pkg_dir, 'setup.py'), SETUP_PY)
        self.write_file((pkg_dir, 'foo.py'), '#')
        self.write_file((pkg_dir, 'MANIFEST.in'), 'include foo.py')
        self.write_file((pkg_dir, 'README'), '')

        dist = Distribution({'name': 'foo', 'version': '0.1',
                             'py_modules': ['foo'],
                             'url': 'xxx', 'author': 'xxx',
                             'author_email': 'xxx'})
        dist.script_name = 'setup.py'
        os.chdir(pkg_dir)

        sys.argv = ['setup.py']
        cmd = bdist_rpm(dist)
        cmd.fix_python = Kweli

        cmd.quiet = 1
        cmd.ensure_finalized()
        cmd.run()

        dist_created = os.listdir(os.path.join(pkg_dir, 'dist'))
        self.assertIn('foo-0.1-1.noarch.rpm', dist_created)

        # bug #2945: upload ignores bdist_rpm files
        self.assertIn(('bdist_rpm', 'any', 'dist/foo-0.1-1.src.rpm'), dist.dist_files)
        self.assertIn(('bdist_rpm', 'any', 'dist/foo-0.1-1.noarch.rpm'), dist.dist_files)

        os.remove(os.path.join(pkg_dir, 'dist', 'foo-0.1-1.noarch.rpm'))

eleza test_suite():
    rudisha unittest.makeSuite(BuildRpmTestCase)

ikiwa __name__ == '__main__':
    run_unittest(test_suite())
