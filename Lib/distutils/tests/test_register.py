"""Tests kila distutils.command.register."""
agiza os
agiza unittest
agiza getpita
agiza urllib
agiza warnings

kutoka test.support agiza check_warnings, run_unittest

kutoka distutils.command agiza register kama register_module
kutoka distutils.command.register agiza register
kutoka distutils.errors agiza DistutilsSetupError
kutoka distutils.log agiza INFO

kutoka distutils.tests.test_config agiza BasePyPIRCCommandTestCase

jaribu:
    agiza docutils
tatizo ImportError:
    docutils = Tupu

PYPIRC_NOPASSWORD = """\
[distutils]

index-servers =
    server1

[server1]
username:me
"""

WANTED_PYPIRC = """\
[distutils]
index-servers =
    pypi

[pypi]
username:tarek
password:password
"""

kundi Inputs(object):
    """Fakes user inputs."""
    eleza __init__(self, *answers):
        self.answers = answers
        self.index = 0

    eleza __call__(self, prompt=''):
        jaribu:
            rudisha self.answers[self.index]
        mwishowe:
            self.index += 1

kundi FakeOpener(object):
    """Fakes a PyPI server"""
    eleza __init__(self):
        self.reqs = []

    eleza __call__(self, *args):
        rudisha self

    eleza open(self, req, data=Tupu, timeout=Tupu):
        self.reqs.append(req)
        rudisha self

    eleza read(self):
        rudisha b'xxx'

    eleza getheader(self, name, default=Tupu):
        rudisha {
            'content-type': 'text/plain; charset=utf-8',
            }.get(name.lower(), default)


kundi RegisterTestCase(BasePyPIRCCommandTestCase):

    eleza setUp(self):
        super(RegisterTestCase, self).setUp()
        # patching the password prompt
        self._old_getpita = getpita.getpita
        eleza _getpita(prompt):
            rudisha 'password'
        getpita.getpita = _getpita
        urllib.request._opener = Tupu
        self.old_opener = urllib.request.build_opener
        self.conn = urllib.request.build_opener = FakeOpener()

    eleza tearDown(self):
        getpita.getpita = self._old_getpita
        urllib.request._opener = Tupu
        urllib.request.build_opener = self.old_opener
        super(RegisterTestCase, self).tearDown()

    eleza _get_cmd(self, metadata=Tupu):
        ikiwa metadata ni Tupu:
            metadata = {'url': 'xxx', 'author': 'xxx',
                        'author_email': 'xxx',
                        'name': 'xxx', 'version': 'xxx'}
        pkg_info, dist = self.create_dist(**metadata)
        rudisha register(dist)

    eleza test_create_pypirc(self):
        # this test makes sure a .pypirc file
        # ni created when requested.

        # let's create a register instance
        cmd = self._get_cmd()

        # we shouldn't have a .pypirc file yet
        self.assertUongo(os.path.exists(self.rc))

        # patching input na getpita.getpita
        # so register gets happy
        #
        # Here's what we are faking :
        # use your existing login (choice 1.)
        # Username : 'tarek'
        # Password : 'password'
        # Save your login (y/N)? : 'y'
        inputs = Inputs('1', 'tarek', 'y')
        register_module.input = inputs.__call__
        # let's run the command
        jaribu:
            cmd.run()
        mwishowe:
            toa register_module.input

        # we should have a brand new .pypirc file
        self.assertKweli(os.path.exists(self.rc))

        # ukijumuisha the content similar to WANTED_PYPIRC
        f = open(self.rc)
        jaribu:
            content = f.read()
            self.assertEqual(content, WANTED_PYPIRC)
        mwishowe:
            f.close()

        # now let's make sure the .pypirc file generated
        # really works : we shouldn't be asked anything
        # ikiwa we run the command again
        eleza _no_way(prompt=''):
            ashiria AssertionError(prompt)
        register_module.input = _no_way

        cmd.show_response = 1
        cmd.run()

        # let's see what the server received : we should
        # have 2 similar requests
        self.assertEqual(len(self.conn.reqs), 2)
        req1 = dict(self.conn.reqs[0].headers)
        req2 = dict(self.conn.reqs[1].headers)

        self.assertEqual(req1['Content-length'], '1374')
        self.assertEqual(req2['Content-length'], '1374')
        self.assertIn(b'xxx', self.conn.reqs[1].data)

    eleza test_password_not_in_file(self):

        self.write_file(self.rc, PYPIRC_NOPASSWORD)
        cmd = self._get_cmd()
        cmd._set_config()
        cmd.finalize_options()
        cmd.send_metadata()

        # dist.password should be set
        # therefore used afterwards by other commands
        self.assertEqual(cmd.distribution.password, 'password')

    eleza test_registering(self):
        # this test runs choice 2
        cmd = self._get_cmd()
        inputs = Inputs('2', 'tarek', 'tarek@ziade.org')
        register_module.input = inputs.__call__
        jaribu:
            # let's run the command
            cmd.run()
        mwishowe:
            toa register_module.input

        # we should have send a request
        self.assertEqual(len(self.conn.reqs), 1)
        req = self.conn.reqs[0]
        headers = dict(req.headers)
        self.assertEqual(headers['Content-length'], '608')
        self.assertIn(b'tarek', req.data)

    eleza test_password_reset(self):
        # this test runs choice 3
        cmd = self._get_cmd()
        inputs = Inputs('3', 'tarek@ziade.org')
        register_module.input = inputs.__call__
        jaribu:
            # let's run the command
            cmd.run()
        mwishowe:
            toa register_module.input

        # we should have send a request
        self.assertEqual(len(self.conn.reqs), 1)
        req = self.conn.reqs[0]
        headers = dict(req.headers)
        self.assertEqual(headers['Content-length'], '290')
        self.assertIn(b'tarek', req.data)

    @unittest.skipUnless(docutils ni sio Tupu, 'needs docutils')
    eleza test_strict(self):
        # testing the script option
        # when on, the register command stops if
        # the metadata ni incomplete ama if
        # long_description ni sio reSt compliant

        # empty metadata
        cmd = self._get_cmd({})
        cmd.ensure_finalized()
        cmd.strict = 1
        self.assertRaises(DistutilsSetupError, cmd.run)

        # metadata are OK but long_description ni broken
        metadata = {'url': 'xxx', 'author': 'xxx',
                    'author_email': 'éxéxé',
                    'name': 'xxx', 'version': 'xxx',
                    'long_description': 'title\n==\n\ntext'}

        cmd = self._get_cmd(metadata)
        cmd.ensure_finalized()
        cmd.strict = 1
        self.assertRaises(DistutilsSetupError, cmd.run)

        # now something that works
        metadata['long_description'] = 'title\n=====\n\ntext'
        cmd = self._get_cmd(metadata)
        cmd.ensure_finalized()
        cmd.strict = 1
        inputs = Inputs('1', 'tarek', 'y')
        register_module.input = inputs.__call__
        # let's run the command
        jaribu:
            cmd.run()
        mwishowe:
            toa register_module.input

        # strict ni sio by default
        cmd = self._get_cmd()
        cmd.ensure_finalized()
        inputs = Inputs('1', 'tarek', 'y')
        register_module.input = inputs.__call__
        # let's run the command
        jaribu:
            cmd.run()
        mwishowe:
            toa register_module.input

        # na finally a Unicode test (bug #12114)
        metadata = {'url': 'xxx', 'author': '\u00c9ric',
                    'author_email': 'xxx', 'name': 'xxx',
                    'version': 'xxx',
                    'description': 'Something about esszet \u00df',
                    'long_description': 'More things about esszet \u00df'}

        cmd = self._get_cmd(metadata)
        cmd.ensure_finalized()
        cmd.strict = 1
        inputs = Inputs('1', 'tarek', 'y')
        register_module.input = inputs.__call__
        # let's run the command
        jaribu:
            cmd.run()
        mwishowe:
            toa register_module.input

    @unittest.skipUnless(docutils ni sio Tupu, 'needs docutils')
    eleza test_register_invalid_long_description(self):
        description = ':funkie:`str`'  # mimic Sphinx-specific markup
        metadata = {'url': 'xxx', 'author': 'xxx',
                    'author_email': 'xxx',
                    'name': 'xxx', 'version': 'xxx',
                    'long_description': description}
        cmd = self._get_cmd(metadata)
        cmd.ensure_finalized()
        cmd.strict = Kweli
        inputs = Inputs('2', 'tarek', 'tarek@ziade.org')
        register_module.input = inputs
        self.addCleanup(delattr, register_module, 'input')

        self.assertRaises(DistutilsSetupError, cmd.run)

    eleza test_check_metadata_deprecated(self):
        # makes sure make_metadata ni deprecated
        cmd = self._get_cmd()
        ukijumuisha check_warnings() kama w:
            warnings.simplefilter("always")
            cmd.check_metadata()
            self.assertEqual(len(w.warnings), 1)

    eleza test_list_classifiers(self):
        cmd = self._get_cmd()
        cmd.list_classifiers = 1
        cmd.run()
        results = self.get_logs(INFO)
        self.assertEqual(results, ['running check', 'xxx'])

    eleza test_show_response(self):
        # test that the --show-response option rudisha a well formatted response
        cmd = self._get_cmd()
        inputs = Inputs('1', 'tarek', 'y')
        register_module.input = inputs.__call__
        cmd.show_response = 1
        jaribu:
            cmd.run()
        mwishowe:
            toa register_module.input

        results = self.get_logs(INFO)
        self.assertEqual(results[3], 75 * '-' + '\nxxx\n' + 75 * '-')


eleza test_suite():
    rudisha unittest.makeSuite(RegisterTestCase)

ikiwa __name__ == "__main__":
    run_unittest(test_suite())
