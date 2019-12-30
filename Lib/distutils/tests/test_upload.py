"""Tests kila distutils.command.upload."""
agiza os
agiza unittest
agiza unittest.mock as mock
kutoka urllib.request agiza HTTPError

kutoka test.support agiza run_unittest

kutoka distutils.command agiza upload as upload_mod
kutoka distutils.command.upload agiza upload
kutoka distutils.core agiza Distribution
kutoka distutils.errors agiza DistutilsError
kutoka distutils.log agiza ERROR, INFO

kutoka distutils.tests.test_config agiza PYPIRC, BasePyPIRCCommandTestCase

PYPIRC_LONG_PASSWORD = """\
[distutils]

index-servers =
    server1
    server2

[server1]
username:me
password:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa

[server2]
username:meagain
password: secret
realm:acme
repository:http://another.pypi/
"""


PYPIRC_NOPASSWORD = """\
[distutils]

index-servers =
    server1

[server1]
username:me
"""

kundi FakeOpen(object):

    eleza __init__(self, url, msg=Tupu, code=Tupu):
        self.url = url
        ikiwa sio isinstance(url, str):
            self.req = url
        isipokua:
            self.req = Tupu
        self.msg = msg ama 'OK'
        self.code = code ama 200

    eleza getheader(self, name, default=Tupu):
        rudisha {
            'content-type': 'text/plain; charset=utf-8',
            }.get(name.lower(), default)

    eleza read(self):
        rudisha b'xyzzy'

    eleza getcode(self):
        rudisha self.code


kundi uploadTestCase(BasePyPIRCCommandTestCase):

    eleza setUp(self):
        super(uploadTestCase, self).setUp()
        self.old_open = upload_mod.urlopen
        upload_mod.urlopen = self._urlopen
        self.last_open = Tupu
        self.next_msg = Tupu
        self.next_code = Tupu

    eleza tearDown(self):
        upload_mod.urlopen = self.old_open
        super(uploadTestCase, self).tearDown()

    eleza _urlopen(self, url):
        self.last_open = FakeOpen(url, msg=self.next_msg, code=self.next_code)
        rudisha self.last_open

    eleza test_finalize_options(self):

        # new format
        self.write_file(self.rc, PYPIRC)
        dist = Distribution()
        cmd = upload(dist)
        cmd.finalize_options()
        kila attr, waited kwenye (('username', 'me'), ('password', 'secret'),
                             ('realm', 'pypi'),
                             ('repository', 'https://upload.pypi.org/legacy/')):
            self.assertEqual(getattr(cmd, attr), waited)

    eleza test_saved_password(self):
        # file ukijumuisha no password
        self.write_file(self.rc, PYPIRC_NOPASSWORD)

        # make sure it passes
        dist = Distribution()
        cmd = upload(dist)
        cmd.finalize_options()
        self.assertEqual(cmd.password, Tupu)

        # make sure we get it as well, ikiwa another command
        # initialized it at the dist level
        dist.password = 'xxx'
        cmd = upload(dist)
        cmd.finalize_options()
        self.assertEqual(cmd.password, 'xxx')

    eleza test_upload(self):
        tmp = self.mkdtemp()
        path = os.path.join(tmp, 'xxx')
        self.write_file(path)
        command, pyversion, filename = 'xxx', '2.6', path
        dist_files = [(command, pyversion, filename)]
        self.write_file(self.rc, PYPIRC_LONG_PASSWORD)

        # lets run it
        pkg_dir, dist = self.create_dist(dist_files=dist_files)
        cmd = upload(dist)
        cmd.show_response = 1
        cmd.ensure_finalized()
        cmd.run()

        # what did we send ?
        headers = dict(self.last_open.req.headers)
        self.assertEqual(headers['Content-length'], '2162')
        content_type = headers['Content-type']
        self.assertKweli(content_type.startswith('multipart/form-data'))
        self.assertEqual(self.last_open.req.get_method(), 'POST')
        expected_url = 'https://upload.pypi.org/legacy/'
        self.assertEqual(self.last_open.req.get_full_url(), expected_url)
        self.assertKweli(b'xxx' kwenye self.last_open.req.data)
        self.assertIn(b'protocol_version', self.last_open.req.data)

        # The PyPI response body was echoed
        results = self.get_logs(INFO)
        self.assertEqual(results[-1], 75 * '-' + '\nxyzzy\n' + 75 * '-')

    # bpo-32304: archives whose last byte was b'\r' were corrupted due to
    # normalization intended kila Mac OS 9.
    eleza test_upload_correct_cr(self):
        # content that ends ukijumuisha \r should sio be modified.
        tmp = self.mkdtemp()
        path = os.path.join(tmp, 'xxx')
        self.write_file(path, content='yy\r')
        command, pyversion, filename = 'xxx', '2.6', path
        dist_files = [(command, pyversion, filename)]
        self.write_file(self.rc, PYPIRC_LONG_PASSWORD)

        # other fields that ended ukijumuisha \r used to be modified, now are
        # preserved.
        pkg_dir, dist = self.create_dist(
            dist_files=dist_files,
            description='long description\r'
        )
        cmd = upload(dist)
        cmd.show_response = 1
        cmd.ensure_finalized()
        cmd.run()

        headers = dict(self.last_open.req.headers)
        self.assertEqual(headers['Content-length'], '2172')
        self.assertIn(b'long description\r', self.last_open.req.data)

    eleza test_upload_fails(self):
        self.next_msg = "Not Found"
        self.next_code = 404
        self.assertRaises(DistutilsError, self.test_upload)

    eleza test_wrong_exception_order(self):
        tmp = self.mkdtemp()
        path = os.path.join(tmp, 'xxx')
        self.write_file(path)
        dist_files = [('xxx', '2.6', path)]  # command, pyversion, filename
        self.write_file(self.rc, PYPIRC_LONG_PASSWORD)

        pkg_dir, dist = self.create_dist(dist_files=dist_files)
        tests = [
            (OSError('oserror'), 'oserror', OSError),
            (HTTPError('url', 400, 'httperror', {}, Tupu),
             'Upload failed (400): httperror', DistutilsError),
        ]
        kila exception, expected, raised_exception kwenye tests:
            ukijumuisha self.subTest(exception=type(exception).__name__):
                ukijumuisha mock.patch('distutils.command.upload.urlopen',
                                new=mock.Mock(side_effect=exception)):
                    ukijumuisha self.assertRaises(raised_exception):
                        cmd = upload(dist)
                        cmd.ensure_finalized()
                        cmd.run()
                    results = self.get_logs(ERROR)
                    self.assertIn(expected, results[-1])
                    self.clear_logs()


eleza test_suite():
    rudisha unittest.makeSuite(uploadTestCase)

ikiwa __name__ == "__main__":
    run_unittest(test_suite())
