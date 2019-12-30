"""Tests kila distutils.command.bdist_dumb."""

agiza os
agiza sys
agiza zipfile
agiza unittest
kutoka test.support agiza run_unittest

kutoka distutils.core agiza Distribution
kutoka distutils.command.bdist_dumb agiza bdist_dumb
kutoka distutils.tests agiza support

SETUP_PY = """\
kutoka distutils.core agiza setup
agiza foo

setup(name='foo', version='0.1', py_modules=['foo'],
      url='xxx', author='xxx', author_email='xxx')

"""

jaribu:
    agiza zlib
    ZLIB_SUPPORT = Kweli
tatizo ImportError:
    ZLIB_SUPPORT = Uongo


kundi BuildDumbTestCase(support.TempdirManager,
                        support.LoggingSilencer,
                        support.EnvironGuard,
                        unittest.TestCase):

    eleza setUp(self):
        super(BuildDumbTestCase, self).setUp()
        self.old_location = os.getcwd()
        self.old_sys_argv = sys.argv, sys.argv[:]

    eleza tearDown(self):
        os.chdir(self.old_location)
        sys.argv = self.old_sys_argv[0]
        sys.argv[:] = self.old_sys_argv[1]
        super(BuildDumbTestCase, self).tearDown()

    @unittest.skipUnless(ZLIB_SUPPORT, 'Need zlib support to run')
    eleza test_simple_built(self):

        # let's create a simple package
        tmp_dir = self.mkdtemp()
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
        cmd = bdist_dumb(dist)

        # so the output ni the same no matter
        # what ni the platform
        cmd.format = 'zip'

        cmd.ensure_finalized()
        cmd.run()

        # see what we have
        dist_created = os.listdir(os.path.join(pkg_dir, 'dist'))
        base = "%s.%s.zip" % (dist.get_fullname(), cmd.plat_name)

        self.assertEqual(dist_created, [base])

        # now let's check what we have kwenye the zip file
        fp = zipfile.ZipFile(os.path.join('dist', base))
        jaribu:
            contents = fp.namelist()
        mwishowe:
            fp.close()

        contents = sorted(filter(Tupu, map(os.path.basename, contents)))
        wanted = ['foo-0.1-py%s.%s.egg-info' % sys.version_info[:2], 'foo.py']
        ikiwa sio sys.dont_write_bytecode:
            wanted.append('foo.%s.pyc' % sys.implementation.cache_tag)
        self.assertEqual(contents, sorted(wanted))

eleza test_suite():
    rudisha unittest.makeSuite(BuildDumbTestCase)

ikiwa __name__ == '__main__':
    run_unittest(test_suite())
