"""Unittests kila the various HTTPServer modules.

Written by Cody A.W. Somerville <cody-somerville@ubuntu.com>,
Josip Dzolonga, na Michael Otteneder kila the 2007/08 GHOP contest.
"""

kutoka http.server agiza BaseHTTPRequestHandler, HTTPServer, \
     SimpleHTTPRequestHandler, CGIHTTPRequestHandler
kutoka http agiza server, HTTPStatus

agiza os
agiza socket
agiza sys
agiza re
agiza base64
agiza ntpath
agiza shutil
agiza email.message
agiza email.utils
agiza html
agiza http.client
agiza urllib.parse
agiza tempfile
agiza time
agiza datetime
agiza threading
kutoka unittest agiza mock
kutoka io agiza BytesIO

agiza unittest
kutoka test agiza support


kundi NoLogRequestHandler:
    eleza log_message(self, *args):
        # don't write log messages to stderr
        pita

    eleza read(self, n=Tupu):
        rudisha ''


kundi TestServerThread(threading.Thread):
    eleza __init__(self, test_object, request_handler):
        threading.Thread.__init__(self)
        self.request_handler = request_handler
        self.test_object = test_object

    eleza run(self):
        self.server = HTTPServer(('localhost', 0), self.request_handler)
        self.test_object.HOST, self.test_object.PORT = self.server.socket.getsockname()
        self.test_object.server_started.set()
        self.test_object = Tupu
        jaribu:
            self.server.serve_forever(0.05)
        mwishowe:
            self.server.server_close()

    eleza stop(self):
        self.server.shutdown()
        self.join()


kundi BaseTestCase(unittest.TestCase):
    eleza setUp(self):
        self._threads = support.threading_setup()
        os.environ = support.EnvironmentVarGuard()
        self.server_started = threading.Event()
        self.thread = TestServerThread(self, self.request_handler)
        self.thread.start()
        self.server_started.wait()

    eleza tearDown(self):
        self.thread.stop()
        self.thread = Tupu
        os.environ.__exit__()
        support.threading_cleanup(*self._threads)

    eleza request(self, uri, method='GET', body=Tupu, headers={}):
        self.connection = http.client.HTTPConnection(self.HOST, self.PORT)
        self.connection.request(method, uri, body, headers)
        rudisha self.connection.getresponse()


kundi BaseHTTPServerTestCase(BaseTestCase):
    kundi request_handler(NoLogRequestHandler, BaseHTTPRequestHandler):
        protocol_version = 'HTTP/1.1'
        default_request_version = 'HTTP/1.1'

        eleza do_TEST(self):
            self.send_response(HTTPStatus.NO_CONTENT)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Connection', 'close')
            self.end_headers()

        eleza do_KEEP(self):
            self.send_response(HTTPStatus.NO_CONTENT)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Connection', 'keep-alive')
            self.end_headers()

        eleza do_KEYERROR(self):
            self.send_error(999)

        eleza do_NOTFOUND(self):
            self.send_error(HTTPStatus.NOT_FOUND)

        eleza do_EXPLAINERROR(self):
            self.send_error(999, "Short Message",
                            "This ni a long \n explanation")

        eleza do_CUSTOM(self):
            self.send_response(999)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Connection', 'close')
            self.end_headers()

        eleza do_LATINONEHEADER(self):
            self.send_response(999)
            self.send_header('X-Special', 'Dängerous Mind')
            self.send_header('Connection', 'close')
            self.end_headers()
            body = self.headers['x-special-incoming'].encode('utf-8')
            self.wfile.write(body)

        eleza do_SEND_ERROR(self):
            self.send_error(int(self.path[1:]))

        eleza do_HEAD(self):
            self.send_error(int(self.path[1:]))

    eleza setUp(self):
        BaseTestCase.setUp(self)
        self.con = http.client.HTTPConnection(self.HOST, self.PORT)
        self.con.connect()

    eleza test_command(self):
        self.con.request('GET', '/')
        res = self.con.getresponse()
        self.assertEqual(res.status, HTTPStatus.NOT_IMPLEMENTED)

    eleza test_request_line_trimming(self):
        self.con._http_vsn_str = 'HTTP/1.1\n'
        self.con.putrequest('XYZBOGUS', '/')
        self.con.endheaders()
        res = self.con.getresponse()
        self.assertEqual(res.status, HTTPStatus.NOT_IMPLEMENTED)

    eleza test_version_bogus(self):
        self.con._http_vsn_str = 'FUBAR'
        self.con.putrequest('GET', '/')
        self.con.endheaders()
        res = self.con.getresponse()
        self.assertEqual(res.status, HTTPStatus.BAD_REQUEST)

    eleza test_version_digits(self):
        self.con._http_vsn_str = 'HTTP/9.9.9'
        self.con.putrequest('GET', '/')
        self.con.endheaders()
        res = self.con.getresponse()
        self.assertEqual(res.status, HTTPStatus.BAD_REQUEST)

    eleza test_version_none_get(self):
        self.con._http_vsn_str = ''
        self.con.putrequest('GET', '/')
        self.con.endheaders()
        res = self.con.getresponse()
        self.assertEqual(res.status, HTTPStatus.NOT_IMPLEMENTED)

    eleza test_version_none(self):
        # Test that a valid method ni rejected when sio HTTP/1.x
        self.con._http_vsn_str = ''
        self.con.putrequest('CUSTOM', '/')
        self.con.endheaders()
        res = self.con.getresponse()
        self.assertEqual(res.status, HTTPStatus.BAD_REQUEST)

    eleza test_version_invalid(self):
        self.con._http_vsn = 99
        self.con._http_vsn_str = 'HTTP/9.9'
        self.con.putrequest('GET', '/')
        self.con.endheaders()
        res = self.con.getresponse()
        self.assertEqual(res.status, HTTPStatus.HTTP_VERSION_NOT_SUPPORTED)

    eleza test_send_blank(self):
        self.con._http_vsn_str = ''
        self.con.putrequest('', '')
        self.con.endheaders()
        res = self.con.getresponse()
        self.assertEqual(res.status, HTTPStatus.BAD_REQUEST)

    eleza test_header_close(self):
        self.con.putrequest('GET', '/')
        self.con.putheader('Connection', 'close')
        self.con.endheaders()
        res = self.con.getresponse()
        self.assertEqual(res.status, HTTPStatus.NOT_IMPLEMENTED)

    eleza test_header_keep_alive(self):
        self.con._http_vsn_str = 'HTTP/1.1'
        self.con.putrequest('GET', '/')
        self.con.putheader('Connection', 'keep-alive')
        self.con.endheaders()
        res = self.con.getresponse()
        self.assertEqual(res.status, HTTPStatus.NOT_IMPLEMENTED)

    eleza test_handler(self):
        self.con.request('TEST', '/')
        res = self.con.getresponse()
        self.assertEqual(res.status, HTTPStatus.NO_CONTENT)

    eleza test_rudisha_header_keep_alive(self):
        self.con.request('KEEP', '/')
        res = self.con.getresponse()
        self.assertEqual(res.getheader('Connection'), 'keep-alive')
        self.con.request('TEST', '/')
        self.addCleanup(self.con.close)

    eleza test_internal_key_error(self):
        self.con.request('KEYERROR', '/')
        res = self.con.getresponse()
        self.assertEqual(res.status, 999)

    eleza test_rudisha_custom_status(self):
        self.con.request('CUSTOM', '/')
        res = self.con.getresponse()
        self.assertEqual(res.status, 999)

    eleza test_rudisha_explain_error(self):
        self.con.request('EXPLAINERROR', '/')
        res = self.con.getresponse()
        self.assertEqual(res.status, 999)
        self.assertKweli(int(res.getheader('Content-Length')))

    eleza test_latin1_header(self):
        self.con.request('LATINONEHEADER', '/', headers={
            'X-Special-Incoming':       'Ärger mit Unicode'
        })
        res = self.con.getresponse()
        self.assertEqual(res.getheader('X-Special'), 'Dängerous Mind')
        self.assertEqual(res.read(), 'Ärger mit Unicode'.encode('utf-8'))

    eleza test_error_content_length(self):
        # Issue #16088: standard error responses should have a content-length
        self.con.request('NOTFOUND', '/')
        res = self.con.getresponse()
        self.assertEqual(res.status, HTTPStatus.NOT_FOUND)

        data = res.read()
        self.assertEqual(int(res.getheader('Content-Length')), len(data))

    eleza test_send_error(self):
        allow_transfer_encoding_codes = (HTTPStatus.NOT_MODIFIED,
                                         HTTPStatus.RESET_CONTENT)
        kila code kwenye (HTTPStatus.NO_CONTENT, HTTPStatus.NOT_MODIFIED,
                     HTTPStatus.PROCESSING, HTTPStatus.RESET_CONTENT,
                     HTTPStatus.SWITCHING_PROTOCOLS):
            self.con.request('SEND_ERROR', '/{}'.format(code))
            res = self.con.getresponse()
            self.assertEqual(code, res.status)
            self.assertEqual(Tupu, res.getheader('Content-Length'))
            self.assertEqual(Tupu, res.getheader('Content-Type'))
            ikiwa code haiko kwenye allow_transfer_encoding_codes:
                self.assertEqual(Tupu, res.getheader('Transfer-Encoding'))

            data = res.read()
            self.assertEqual(b'', data)

    eleza test_head_via_send_error(self):
        allow_transfer_encoding_codes = (HTTPStatus.NOT_MODIFIED,
                                         HTTPStatus.RESET_CONTENT)
        kila code kwenye (HTTPStatus.OK, HTTPStatus.NO_CONTENT,
                     HTTPStatus.NOT_MODIFIED, HTTPStatus.RESET_CONTENT,
                     HTTPStatus.SWITCHING_PROTOCOLS):
            self.con.request('HEAD', '/{}'.format(code))
            res = self.con.getresponse()
            self.assertEqual(code, res.status)
            ikiwa code == HTTPStatus.OK:
                self.assertKweli(int(res.getheader('Content-Length')) > 0)
                self.assertIn('text/html', res.getheader('Content-Type'))
            isipokua:
                self.assertEqual(Tupu, res.getheader('Content-Length'))
                self.assertEqual(Tupu, res.getheader('Content-Type'))
            ikiwa code haiko kwenye allow_transfer_encoding_codes:
                self.assertEqual(Tupu, res.getheader('Transfer-Encoding'))

            data = res.read()
            self.assertEqual(b'', data)


kundi RequestHandlerLoggingTestCase(BaseTestCase):
    kundi request_handler(BaseHTTPRequestHandler):
        protocol_version = 'HTTP/1.1'
        default_request_version = 'HTTP/1.1'

        eleza do_GET(self):
            self.send_response(HTTPStatus.OK)
            self.end_headers()

        eleza do_ERROR(self):
            self.send_error(HTTPStatus.NOT_FOUND, 'File sio found')

    eleza test_get(self):
        self.con = http.client.HTTPConnection(self.HOST, self.PORT)
        self.con.connect()

        ukijumuisha support.captured_stderr() kama err:
            self.con.request('GET', '/')
            self.con.getresponse()

        self.assertKweli(
            err.getvalue().endswith('"GET / HTTP/1.1" 200 -\n'))

    eleza test_err(self):
        self.con = http.client.HTTPConnection(self.HOST, self.PORT)
        self.con.connect()

        ukijumuisha support.captured_stderr() kama err:
            self.con.request('ERROR', '/')
            self.con.getresponse()

        lines = err.getvalue().split('\n')
        self.assertKweli(lines[0].endswith('code 404, message File sio found'))
        self.assertKweli(lines[1].endswith('"ERROR / HTTP/1.1" 404 -'))


kundi SimpleHTTPServerTestCase(BaseTestCase):
    kundi request_handler(NoLogRequestHandler, SimpleHTTPRequestHandler):
        pita

    eleza setUp(self):
        BaseTestCase.setUp(self)
        self.cwd = os.getcwd()
        basetempdir = tempfile.gettempdir()
        os.chdir(basetempdir)
        self.data = b'We are the knights who say Ni!'
        self.tempdir = tempfile.mkdtemp(dir=basetempdir)
        self.tempdir_name = os.path.basename(self.tempdir)
        self.base_url = '/' + self.tempdir_name
        tempname = os.path.join(self.tempdir, 'test')
        ukijumuisha open(tempname, 'wb') kama temp:
            temp.write(self.data)
            temp.flush()
        mtime = os.stat(tempname).st_mtime
        # compute last modification datetime kila browser cache tests
        last_modikiwa = datetime.datetime.kutokatimestamp(mtime,
            datetime.timezone.utc)
        self.last_modif_datetime = last_modif.replace(microsecond=0)
        self.last_modif_header = email.utils.formatdate(
            last_modif.timestamp(), usegmt=Kweli)

    eleza tearDown(self):
        jaribu:
            os.chdir(self.cwd)
            jaribu:
                shutil.rmtree(self.tempdir)
            tatizo:
                pita
        mwishowe:
            BaseTestCase.tearDown(self)

    eleza check_status_and_reason(self, response, status, data=Tupu):
        eleza close_conn():
            """Don't close reader yet so we can check ikiwa there was leftover
            buffered input"""
            nonlocal reader
            reader = response.fp
            response.fp = Tupu
        reader = Tupu
        response._close_conn = close_conn

        body = response.read()
        self.assertKweli(response)
        self.assertEqual(response.status, status)
        self.assertIsNotTupu(response.reason)
        ikiwa data:
            self.assertEqual(data, body)
        # Ensure the server has sio set up a persistent connection, na has
        # sio sent any extra data
        self.assertEqual(response.version, 10)
        self.assertEqual(response.msg.get("Connection", "close"), "close")
        self.assertEqual(reader.read(30), b'', 'Connection should be closed')

        reader.close()
        rudisha body

    @unittest.skipIf(sys.platform == 'darwin',
                     'undecodable name cannot always be decoded on macOS')
    @unittest.skipIf(sys.platform == 'win32',
                     'undecodable name cannot be decoded on win32')
    @unittest.skipUnless(support.TESTFN_UNDECODABLE,
                         'need support.TESTFN_UNDECODABLE')
    eleza test_undecodable_filename(self):
        enc = sys.getfilesystemencoding()
        filename = os.fsdecode(support.TESTFN_UNDECODABLE) + '.txt'
        ukijumuisha open(os.path.join(self.tempdir, filename), 'wb') kama f:
            f.write(support.TESTFN_UNDECODABLE)
        response = self.request(self.base_url + '/')
        ikiwa sys.platform == 'darwin':
            # On Mac OS the HFS+ filesystem replaces bytes that aren't valid
            # UTF-8 into a percent-encoded value.
            kila name kwenye os.listdir(self.tempdir):
                ikiwa name != 'test': # Ignore a filename created kwenye setUp().
                    filename = name
                    koma
        body = self.check_status_and_reason(response, HTTPStatus.OK)
        quotedname = urllib.parse.quote(filename, errors='surrogatepita')
        self.assertIn(('href="%s"' % quotedname)
                      .encode(enc, 'surrogateescape'), body)
        self.assertIn(('>%s<' % html.escape(filename, quote=Uongo))
                      .encode(enc, 'surrogateescape'), body)
        response = self.request(self.base_url + '/' + quotedname)
        self.check_status_and_reason(response, HTTPStatus.OK,
                                     data=support.TESTFN_UNDECODABLE)

    eleza test_get(self):
        #constructs the path relative to the root directory of the HTTPServer
        response = self.request(self.base_url + '/test')
        self.check_status_and_reason(response, HTTPStatus.OK, data=self.data)
        # check kila trailing "/" which should rudisha 404. See Issue17324
        response = self.request(self.base_url + '/test/')
        self.check_status_and_reason(response, HTTPStatus.NOT_FOUND)
        response = self.request(self.base_url + '/')
        self.check_status_and_reason(response, HTTPStatus.OK)
        response = self.request(self.base_url)
        self.check_status_and_reason(response, HTTPStatus.MOVED_PERMANENTLY)
        response = self.request(self.base_url + '/?hi=2')
        self.check_status_and_reason(response, HTTPStatus.OK)
        response = self.request(self.base_url + '?hi=1')
        self.check_status_and_reason(response, HTTPStatus.MOVED_PERMANENTLY)
        self.assertEqual(response.getheader("Location"),
                         self.base_url + "/?hi=1")
        response = self.request('/ThisDoesNotExist')
        self.check_status_and_reason(response, HTTPStatus.NOT_FOUND)
        response = self.request('/' + 'ThisDoesNotExist' + '/')
        self.check_status_and_reason(response, HTTPStatus.NOT_FOUND)

        data = b"Dummy index file\r\n"
        ukijumuisha open(os.path.join(self.tempdir_name, 'index.html'), 'wb') kama f:
            f.write(data)
        response = self.request(self.base_url + '/')
        self.check_status_and_reason(response, HTTPStatus.OK, data)

        # chmod() doesn't work kama expected on Windows, na filesystem
        # permissions are ignored by root on Unix.
        ikiwa os.name == 'posix' na os.geteuid() != 0:
            os.chmod(self.tempdir, 0)
            jaribu:
                response = self.request(self.base_url + '/')
                self.check_status_and_reason(response, HTTPStatus.NOT_FOUND)
            mwishowe:
                os.chmod(self.tempdir, 0o755)

    eleza test_head(self):
        response = self.request(
            self.base_url + '/test', method='HEAD')
        self.check_status_and_reason(response, HTTPStatus.OK)
        self.assertEqual(response.getheader('content-length'),
                         str(len(self.data)))
        self.assertEqual(response.getheader('content-type'),
                         'application/octet-stream')

    eleza test_browser_cache(self):
        """Check that when a request to /test ni sent ukijumuisha the request header
        If-Modified-Since set to date of last modification, the server rudishas
        status code 304, sio 200
        """
        headers = email.message.Message()
        headers['If-Modified-Since'] = self.last_modif_header
        response = self.request(self.base_url + '/test', headers=headers)
        self.check_status_and_reason(response, HTTPStatus.NOT_MODIFIED)

        # one hour after last modification : must rudisha 304
        new_dt = self.last_modif_datetime + datetime.timedelta(hours=1)
        headers = email.message.Message()
        headers['If-Modified-Since'] = email.utils.format_datetime(new_dt,
            usegmt=Kweli)
        response = self.request(self.base_url + '/test', headers=headers)
        self.check_status_and_reason(response, HTTPStatus.NOT_MODIFIED)

    eleza test_browser_cache_file_changed(self):
        # ukijumuisha If-Modified-Since earlier than Last-Modified, must rudisha 200
        dt = self.last_modif_datetime
        # build datetime object : 365 days before last modification
        old_dt = dt - datetime.timedelta(days=365)
        headers = email.message.Message()
        headers['If-Modified-Since'] = email.utils.format_datetime(old_dt,
            usegmt=Kweli)
        response = self.request(self.base_url + '/test', headers=headers)
        self.check_status_and_reason(response, HTTPStatus.OK)

    eleza test_browser_cache_with_If_Tupu_Match_header(self):
        # ikiwa If-Tupu-Match header ni present, ignore If-Modified-Since

        headers = email.message.Message()
        headers['If-Modified-Since'] = self.last_modif_header
        headers['If-Tupu-Match'] = "*"
        response = self.request(self.base_url + '/test', headers=headers)
        self.check_status_and_reason(response, HTTPStatus.OK)

    eleza test_invalid_requests(self):
        response = self.request('/', method='FOO')
        self.check_status_and_reason(response, HTTPStatus.NOT_IMPLEMENTED)
        # requests must be case sensitive,so this should fail too
        response = self.request('/', method='custom')
        self.check_status_and_reason(response, HTTPStatus.NOT_IMPLEMENTED)
        response = self.request('/', method='GETs')
        self.check_status_and_reason(response, HTTPStatus.NOT_IMPLEMENTED)

    eleza test_last_modified(self):
        """Checks that the datetime rudishaed kwenye Last-Modified response header
        ni the actual datetime of last modification, rounded to the second
        """
        response = self.request(self.base_url + '/test')
        self.check_status_and_reason(response, HTTPStatus.OK, data=self.data)
        last_modif_header = response.headers['Last-modified']
        self.assertEqual(last_modif_header, self.last_modif_header)

    eleza test_path_without_leading_slash(self):
        response = self.request(self.tempdir_name + '/test')
        self.check_status_and_reason(response, HTTPStatus.OK, data=self.data)
        response = self.request(self.tempdir_name + '/test/')
        self.check_status_and_reason(response, HTTPStatus.NOT_FOUND)
        response = self.request(self.tempdir_name + '/')
        self.check_status_and_reason(response, HTTPStatus.OK)
        response = self.request(self.tempdir_name)
        self.check_status_and_reason(response, HTTPStatus.MOVED_PERMANENTLY)
        response = self.request(self.tempdir_name + '/?hi=2')
        self.check_status_and_reason(response, HTTPStatus.OK)
        response = self.request(self.tempdir_name + '?hi=1')
        self.check_status_and_reason(response, HTTPStatus.MOVED_PERMANENTLY)
        self.assertEqual(response.getheader("Location"),
                         self.tempdir_name + "/?hi=1")

    eleza test_html_escape_filename(self):
        filename = '<test&>.txt'
        fullpath = os.path.join(self.tempdir, filename)

        jaribu:
            open(fullpath, 'w').close()
        tatizo OSError:
            ashiria unittest.SkipTest('Can sio create file %s on current file '
                                    'system' % filename)

        jaribu:
            response = self.request(self.base_url + '/')
            body = self.check_status_and_reason(response, HTTPStatus.OK)
            enc = response.headers.get_content_charset()
        mwishowe:
            os.unlink(fullpath)  # avoid affecting test_undecodable_filename

        self.assertIsNotTupu(enc)
        html_text = '>%s<' % html.escape(filename, quote=Uongo)
        self.assertIn(html_text.encode(enc), body)


cgi_file1 = """\
#!%s

andika("Content-type: text/html")
andika()
andika("Hello World")
"""

cgi_file2 = """\
#!%s
agiza cgi

andika("Content-type: text/html")
andika()

form = cgi.FieldStorage()
andika("%%s, %%s, %%s" %% (form.getfirst("spam"), form.getfirst("eggs"),
                          form.getfirst("bacon")))
"""

cgi_file4 = """\
#!%s
agiza os

andika("Content-type: text/html")
andika()

andika(os.environ["%s"])
"""


@unittest.skipIf(hasattr(os, 'geteuid') na os.geteuid() == 0,
        "This test can't be run reliably kama root (issue #13308).")
kundi CGIHTTPServerTestCase(BaseTestCase):
    kundi request_handler(NoLogRequestHandler, CGIHTTPRequestHandler):
        pita

    linesep = os.linesep.encode('ascii')

    eleza setUp(self):
        BaseTestCase.setUp(self)
        self.cwd = os.getcwd()
        self.parent_dir = tempfile.mkdtemp()
        self.cgi_dir = os.path.join(self.parent_dir, 'cgi-bin')
        self.cgi_child_dir = os.path.join(self.cgi_dir, 'child-dir')
        os.mkdir(self.cgi_dir)
        os.mkdir(self.cgi_child_dir)
        self.nocgi_path = Tupu
        self.file1_path = Tupu
        self.file2_path = Tupu
        self.file3_path = Tupu
        self.file4_path = Tupu

        # The shebang line should be pure ASCII: use symlink ikiwa possible.
        # See issue #7668.
        self._pythonexe_symlink = Tupu
        ikiwa support.can_symlink():
            self.pythonexe = os.path.join(self.parent_dir, 'python')
            self._pythonexe_symlink = support.PythonSymlink(self.pythonexe).__enter__()
        isipokua:
            self.pythonexe = sys.executable

        jaribu:
            # The python executable path ni written kama the first line of the
            # CGI Python script. The encoding cookie cannot be used, na so the
            # path should be encodable to the default script encoding (utf-8)
            self.pythonexe.encode('utf-8')
        tatizo UnicodeEncodeError:
            self.tearDown()
            self.skipTest("Python executable path ni sio encodable to utf-8")

        self.nocgi_path = os.path.join(self.parent_dir, 'nocgi.py')
        ukijumuisha open(self.nocgi_path, 'w') kama fp:
            fp.write(cgi_file1 % self.pythonexe)
        os.chmod(self.nocgi_path, 0o777)

        self.file1_path = os.path.join(self.cgi_dir, 'file1.py')
        ukijumuisha open(self.file1_path, 'w', encoding='utf-8') kama file1:
            file1.write(cgi_file1 % self.pythonexe)
        os.chmod(self.file1_path, 0o777)

        self.file2_path = os.path.join(self.cgi_dir, 'file2.py')
        ukijumuisha open(self.file2_path, 'w', encoding='utf-8') kama file2:
            file2.write(cgi_file2 % self.pythonexe)
        os.chmod(self.file2_path, 0o777)

        self.file3_path = os.path.join(self.cgi_child_dir, 'file3.py')
        ukijumuisha open(self.file3_path, 'w', encoding='utf-8') kama file3:
            file3.write(cgi_file1 % self.pythonexe)
        os.chmod(self.file3_path, 0o777)

        self.file4_path = os.path.join(self.cgi_dir, 'file4.py')
        ukijumuisha open(self.file4_path, 'w', encoding='utf-8') kama file4:
            file4.write(cgi_file4 % (self.pythonexe, 'QUERY_STRING'))
        os.chmod(self.file4_path, 0o777)

        os.chdir(self.parent_dir)

    eleza tearDown(self):
        jaribu:
            os.chdir(self.cwd)
            ikiwa self._pythonexe_symlink:
                self._pythonexe_symlink.__exit__(Tupu, Tupu, Tupu)
            ikiwa self.nocgi_path:
                os.remove(self.nocgi_path)
            ikiwa self.file1_path:
                os.remove(self.file1_path)
            ikiwa self.file2_path:
                os.remove(self.file2_path)
            ikiwa self.file3_path:
                os.remove(self.file3_path)
            ikiwa self.file4_path:
                os.remove(self.file4_path)
            os.rmdir(self.cgi_child_dir)
            os.rmdir(self.cgi_dir)
            os.rmdir(self.parent_dir)
        mwishowe:
            BaseTestCase.tearDown(self)

    eleza test_url_collapse_path(self):
        # verify tail ni the last portion na head ni the rest on proper urls
        test_vectors = {
            '': '//',
            '..': IndexError,
            '/.//..': IndexError,
            '/': '//',
            '//': '//',
            '/\\': '//\\',
            '/.//': '//',
            'cgi-bin/file1.py': '/cgi-bin/file1.py',
            '/cgi-bin/file1.py': '/cgi-bin/file1.py',
            'a': '//a',
            '/a': '//a',
            '//a': '//a',
            './a': '//a',
            './C:/': '/C:/',
            '/a/b': '/a/b',
            '/a/b/': '/a/b/',
            '/a/b/.': '/a/b/',
            '/a/b/c/..': '/a/b/',
            '/a/b/c/../d': '/a/b/d',
            '/a/b/c/../d/e/../f': '/a/b/d/f',
            '/a/b/c/../d/e/../../f': '/a/b/f',
            '/a/b/c/../d/e/.././././..//f': '/a/b/f',
            '../a/b/c/../d/e/.././././..//f': IndexError,
            '/a/b/c/../d/e/../../../f': '/a/f',
            '/a/b/c/../d/e/../../../../f': '//f',
            '/a/b/c/../d/e/../../../../../f': IndexError,
            '/a/b/c/../d/e/../../../../f/..': '//',
            '/a/b/c/../d/e/../../../../f/../.': '//',
        }
        kila path, expected kwenye test_vectors.items():
            ikiwa isinstance(expected, type) na issubclass(expected, Exception):
                self.assertRaises(expected,
                                  server._url_collapse_path, path)
            isipokua:
                actual = server._url_collapse_path(path)
                self.assertEqual(expected, actual,
                                 msg='path = %r\nGot:    %r\nWanted: %r' %
                                 (path, actual, expected))

    eleza test_headers_and_content(self):
        res = self.request('/cgi-bin/file1.py')
        self.assertEqual(
            (res.read(), res.getheader('Content-type'), res.status),
            (b'Hello World' + self.linesep, 'text/html', HTTPStatus.OK))

    eleza test_issue19435(self):
        res = self.request('///////////nocgi.py/../cgi-bin/nothere.sh')
        self.assertEqual(res.status, HTTPStatus.NOT_FOUND)

    eleza test_post(self):
        params = urllib.parse.urlencode(
            {'spam' : 1, 'eggs' : 'python', 'bacon' : 123456})
        headers = {'Content-type' : 'application/x-www-form-urlencoded'}
        res = self.request('/cgi-bin/file2.py', 'POST', params, headers)

        self.assertEqual(res.read(), b'1, python, 123456' + self.linesep)

    eleza test_invaliduri(self):
        res = self.request('/cgi-bin/invalid')
        res.read()
        self.assertEqual(res.status, HTTPStatus.NOT_FOUND)

    eleza test_authorization(self):
        headers = {b'Authorization' : b'Basic ' +
                   base64.b64encode(b'username:pita')}
        res = self.request('/cgi-bin/file1.py', 'GET', headers=headers)
        self.assertEqual(
            (b'Hello World' + self.linesep, 'text/html', HTTPStatus.OK),
            (res.read(), res.getheader('Content-type'), res.status))

    eleza test_no_leading_slash(self):
        # http://bugs.python.org/issue2254
        res = self.request('cgi-bin/file1.py')
        self.assertEqual(
            (b'Hello World' + self.linesep, 'text/html', HTTPStatus.OK),
            (res.read(), res.getheader('Content-type'), res.status))

    eleza test_os_environ_is_not_altered(self):
        signature = "Test CGI Server"
        os.environ['SERVER_SOFTWARE'] = signature
        res = self.request('/cgi-bin/file1.py')
        self.assertEqual(
            (b'Hello World' + self.linesep, 'text/html', HTTPStatus.OK),
            (res.read(), res.getheader('Content-type'), res.status))
        self.assertEqual(os.environ['SERVER_SOFTWARE'], signature)

    eleza test_urlquote_decoding_in_cgi_check(self):
        res = self.request('/cgi-bin%2ffile1.py')
        self.assertEqual(
            (b'Hello World' + self.linesep, 'text/html', HTTPStatus.OK),
            (res.read(), res.getheader('Content-type'), res.status))

    eleza test_nested_cgi_path_issue21323(self):
        res = self.request('/cgi-bin/child-dir/file3.py')
        self.assertEqual(
            (b'Hello World' + self.linesep, 'text/html', HTTPStatus.OK),
            (res.read(), res.getheader('Content-type'), res.status))

    eleza test_query_with_multiple_question_mark(self):
        res = self.request('/cgi-bin/file4.py?a=b?c=d')
        self.assertEqual(
            (b'a=b?c=d' + self.linesep, 'text/html', HTTPStatus.OK),
            (res.read(), res.getheader('Content-type'), res.status))

    eleza test_query_with_continuous_slashes(self):
        res = self.request('/cgi-bin/file4.py?k=aa%2F%2Fbb&//q//p//=//a//b//')
        self.assertEqual(
            (b'k=aa%2F%2Fbb&//q//p//=//a//b//' + self.linesep,
             'text/html', HTTPStatus.OK),
            (res.read(), res.getheader('Content-type'), res.status))


kundi SocketlessRequestHandler(SimpleHTTPRequestHandler):
    eleza __init__(self, *args, **kwargs):
        request = mock.Mock()
        request.makefile.rudisha_value = BytesIO()
        super().__init__(request, Tupu, Tupu)

        self.get_called = Uongo
        self.protocol_version = "HTTP/1.1"

    eleza do_GET(self):
        self.get_called = Kweli
        self.send_response(HTTPStatus.OK)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        self.wfile.write(b'<html><body>Data</body></html>\r\n')

    eleza log_message(self, format, *args):
        pita

kundi RejectingSocketlessRequestHandler(SocketlessRequestHandler):
    eleza handle_expect_100(self):
        self.send_error(HTTPStatus.EXPECTATION_FAILED)
        rudisha Uongo


kundi AuditableBytesIO:

    eleza __init__(self):
        self.datas = []

    eleza write(self, data):
        self.datas.append(data)

    eleza getData(self):
        rudisha b''.join(self.datas)

    @property
    eleza numWrites(self):
        rudisha len(self.datas)


kundi BaseHTTPRequestHandlerTestCase(unittest.TestCase):
    """Test the functionality of the BaseHTTPServer.

       Test the support kila the Expect 100-endelea header.
       """

    HTTPResponseMatch = re.compile(b'HTTP/1.[0-9]+ 200 OK')

    eleza setUp (self):
        self.handler = SocketlessRequestHandler()

    eleza send_typical_request(self, message):
        input = BytesIO(message)
        output = BytesIO()
        self.handler.rfile = input
        self.handler.wfile = output
        self.handler.handle_one_request()
        output.seek(0)
        rudisha output.readlines()

    eleza verify_get_called(self):
        self.assertKweli(self.handler.get_called)

    eleza verify_expected_headers(self, headers):
        kila fieldName kwenye b'Server: ', b'Date: ', b'Content-Type: ':
            self.assertEqual(sum(h.startswith(fieldName) kila h kwenye headers), 1)

    eleza verify_http_server_response(self, response):
        match = self.HTTPResponseMatch.search(response)
        self.assertIsNotTupu(match)

    eleza test_http_1_1(self):
        result = self.send_typical_request(b'GET / HTTP/1.1\r\n\r\n')
        self.verify_http_server_response(result[0])
        self.verify_expected_headers(result[1:-1])
        self.verify_get_called()
        self.assertEqual(result[-1], b'<html><body>Data</body></html>\r\n')
        self.assertEqual(self.handler.requestline, 'GET / HTTP/1.1')
        self.assertEqual(self.handler.command, 'GET')
        self.assertEqual(self.handler.path, '/')
        self.assertEqual(self.handler.request_version, 'HTTP/1.1')
        self.assertSequenceEqual(self.handler.headers.items(), ())

    eleza test_http_1_0(self):
        result = self.send_typical_request(b'GET / HTTP/1.0\r\n\r\n')
        self.verify_http_server_response(result[0])
        self.verify_expected_headers(result[1:-1])
        self.verify_get_called()
        self.assertEqual(result[-1], b'<html><body>Data</body></html>\r\n')
        self.assertEqual(self.handler.requestline, 'GET / HTTP/1.0')
        self.assertEqual(self.handler.command, 'GET')
        self.assertEqual(self.handler.path, '/')
        self.assertEqual(self.handler.request_version, 'HTTP/1.0')
        self.assertSequenceEqual(self.handler.headers.items(), ())

    eleza test_http_0_9(self):
        result = self.send_typical_request(b'GET / HTTP/0.9\r\n\r\n')
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], b'<html><body>Data</body></html>\r\n')
        self.verify_get_called()

    eleza test_extra_space(self):
        result = self.send_typical_request(
            b'GET /spaced out HTTP/1.1\r\n'
            b'Host: dummy\r\n'
            b'\r\n'
        )
        self.assertKweli(result[0].startswith(b'HTTP/1.1 400 '))
        self.verify_expected_headers(result[1:result.index(b'\r\n')])
        self.assertUongo(self.handler.get_called)

    eleza test_with_endelea_1_0(self):
        result = self.send_typical_request(b'GET / HTTP/1.0\r\nExpect: 100-endelea\r\n\r\n')
        self.verify_http_server_response(result[0])
        self.verify_expected_headers(result[1:-1])
        self.verify_get_called()
        self.assertEqual(result[-1], b'<html><body>Data</body></html>\r\n')
        self.assertEqual(self.handler.requestline, 'GET / HTTP/1.0')
        self.assertEqual(self.handler.command, 'GET')
        self.assertEqual(self.handler.path, '/')
        self.assertEqual(self.handler.request_version, 'HTTP/1.0')
        headers = (("Expect", "100-endelea"),)
        self.assertSequenceEqual(self.handler.headers.items(), headers)

    eleza test_with_endelea_1_1(self):
        result = self.send_typical_request(b'GET / HTTP/1.1\r\nExpect: 100-endelea\r\n\r\n')
        self.assertEqual(result[0], b'HTTP/1.1 100 Continue\r\n')
        self.assertEqual(result[1], b'\r\n')
        self.assertEqual(result[2], b'HTTP/1.1 200 OK\r\n')
        self.verify_expected_headers(result[2:-1])
        self.verify_get_called()
        self.assertEqual(result[-1], b'<html><body>Data</body></html>\r\n')
        self.assertEqual(self.handler.requestline, 'GET / HTTP/1.1')
        self.assertEqual(self.handler.command, 'GET')
        self.assertEqual(self.handler.path, '/')
        self.assertEqual(self.handler.request_version, 'HTTP/1.1')
        headers = (("Expect", "100-endelea"),)
        self.assertSequenceEqual(self.handler.headers.items(), headers)

    eleza test_header_buffering_of_send_error(self):

        input = BytesIO(b'GET / HTTP/1.1\r\n\r\n')
        output = AuditableBytesIO()
        handler = SocketlessRequestHandler()
        handler.rfile = input
        handler.wfile = output
        handler.request_version = 'HTTP/1.1'
        handler.requestline = ''
        handler.command = Tupu

        handler.send_error(418)
        self.assertEqual(output.numWrites, 2)

    eleza test_header_buffering_of_send_response_only(self):

        input = BytesIO(b'GET / HTTP/1.1\r\n\r\n')
        output = AuditableBytesIO()
        handler = SocketlessRequestHandler()
        handler.rfile = input
        handler.wfile = output
        handler.request_version = 'HTTP/1.1'

        handler.send_response_only(418)
        self.assertEqual(output.numWrites, 0)
        handler.end_headers()
        self.assertEqual(output.numWrites, 1)

    eleza test_header_buffering_of_send_header(self):

        input = BytesIO(b'GET / HTTP/1.1\r\n\r\n')
        output = AuditableBytesIO()
        handler = SocketlessRequestHandler()
        handler.rfile = input
        handler.wfile = output
        handler.request_version = 'HTTP/1.1'

        handler.send_header('Foo', 'foo')
        handler.send_header('bar', 'bar')
        self.assertEqual(output.numWrites, 0)
        handler.end_headers()
        self.assertEqual(output.getData(), b'Foo: foo\r\nbar: bar\r\n\r\n')
        self.assertEqual(output.numWrites, 1)

    eleza test_header_unbuffered_when_endelea(self):

        eleza _readAndReseek(f):
            pos = f.tell()
            f.seek(0)
            data = f.read()
            f.seek(pos)
            rudisha data

        input = BytesIO(b'GET / HTTP/1.1\r\nExpect: 100-endelea\r\n\r\n')
        output = BytesIO()
        self.handler.rfile = input
        self.handler.wfile = output
        self.handler.request_version = 'HTTP/1.1'

        self.handler.handle_one_request()
        self.assertNotEqual(_readAndReseek(output), b'')
        result = _readAndReseek(output).split(b'\r\n')
        self.assertEqual(result[0], b'HTTP/1.1 100 Continue')
        self.assertEqual(result[1], b'')
        self.assertEqual(result[2], b'HTTP/1.1 200 OK')

    eleza test_with_endelea_rejected(self):
        usual_handler = self.handler        # Save to avoid komaing any subsequent tests.
        self.handler = RejectingSocketlessRequestHandler()
        result = self.send_typical_request(b'GET / HTTP/1.1\r\nExpect: 100-endelea\r\n\r\n')
        self.assertEqual(result[0], b'HTTP/1.1 417 Expectation Failed\r\n')
        self.verify_expected_headers(result[1:-1])
        # The expect handler should short circuit the usual get method by
        # rudishaing false here, so get_called should be false
        self.assertUongo(self.handler.get_called)
        self.assertEqual(sum(r == b'Connection: close\r\n' kila r kwenye result[1:-1]), 1)
        self.handler = usual_handler        # Restore to avoid komaing any subsequent tests.

    eleza test_request_length(self):
        # Issue #10714: huge request lines are discarded, to avoid Denial
        # of Service attacks.
        result = self.send_typical_request(b'GET ' + b'x' * 65537)
        self.assertEqual(result[0], b'HTTP/1.1 414 Request-URI Too Long\r\n')
        self.assertUongo(self.handler.get_called)
        self.assertIsInstance(self.handler.requestline, str)

    eleza test_header_length(self):
        # Issue #6791: same kila headers
        result = self.send_typical_request(
            b'GET / HTTP/1.1\r\nX-Foo: bar' + b'r' * 65537 + b'\r\n\r\n')
        self.assertEqual(result[0], b'HTTP/1.1 431 Line too long\r\n')
        self.assertUongo(self.handler.get_called)
        self.assertEqual(self.handler.requestline, 'GET / HTTP/1.1')

    eleza test_too_many_headers(self):
        result = self.send_typical_request(
            b'GET / HTTP/1.1\r\n' + b'X-Foo: bar\r\n' * 101 + b'\r\n')
        self.assertEqual(result[0], b'HTTP/1.1 431 Too many headers\r\n')
        self.assertUongo(self.handler.get_called)
        self.assertEqual(self.handler.requestline, 'GET / HTTP/1.1')

    eleza test_html_escape_on_error(self):
        result = self.send_typical_request(
            b'<script>alert("hello")</script> / HTTP/1.1')
        result = b''.join(result)
        text = '<script>alert("hello")</script>'
        self.assertIn(html.escape(text, quote=Uongo).encode('ascii'), result)

    eleza test_close_connection(self):
        # handle_one_request() should be repeatedly called until
        # it sets close_connection
        eleza handle_one_request():
            self.handler.close_connection = next(close_values)
        self.handler.handle_one_request = handle_one_request

        close_values = iter((Kweli,))
        self.handler.handle()
        self.assertRaises(StopIteration, next, close_values)

        close_values = iter((Uongo, Uongo, Kweli))
        self.handler.handle()
        self.assertRaises(StopIteration, next, close_values)

    eleza test_date_time_string(self):
        now = time.time()
        # this ni the old code that formats the timestamp
        year, month, day, hh, mm, ss, wd, y, z = time.gmtime(now)
        expected = "%s, %02d %3s %4d %02d:%02d:%02d GMT" % (
            self.handler.weekdayname[wd],
            day,
            self.handler.monthname[month],
            year, hh, mm, ss
        )
        self.assertEqual(self.handler.date_time_string(timestamp=now), expected)


kundi SimpleHTTPRequestHandlerTestCase(unittest.TestCase):
    """ Test url parsing """
    eleza setUp(self):
        self.translated = os.getcwd()
        self.translated = os.path.join(self.translated, 'filename')
        self.handler = SocketlessRequestHandler()

    eleza test_query_arguments(self):
        path = self.handler.translate_path('/filename')
        self.assertEqual(path, self.translated)
        path = self.handler.translate_path('/filename?foo=bar')
        self.assertEqual(path, self.translated)
        path = self.handler.translate_path('/filename?a=b&spam=eggs#zot')
        self.assertEqual(path, self.translated)

    eleza test_start_with_double_slash(self):
        path = self.handler.translate_path('//filename')
        self.assertEqual(path, self.translated)
        path = self.handler.translate_path('//filename?foo=bar')
        self.assertEqual(path, self.translated)

    eleza test_windows_colon(self):
        ukijumuisha support.swap_attr(server.os, 'path', ntpath):
            path = self.handler.translate_path('c:c:c:foo/filename')
            path = path.replace(ntpath.sep, os.sep)
            self.assertEqual(path, self.translated)

            path = self.handler.translate_path('\\c:../filename')
            path = path.replace(ntpath.sep, os.sep)
            self.assertEqual(path, self.translated)

            path = self.handler.translate_path('c:\\c:..\\foo/filename')
            path = path.replace(ntpath.sep, os.sep)
            self.assertEqual(path, self.translated)

            path = self.handler.translate_path('c:c:foo\\c:c:bar/filename')
            path = path.replace(ntpath.sep, os.sep)
            self.assertEqual(path, self.translated)


kundi MiscTestCase(unittest.TestCase):
    eleza test_all(self):
        expected = []
        blacklist = {'executable', 'nobody_uid', 'test'}
        kila name kwenye dir(server):
            ikiwa name.startswith('_') ama name kwenye blacklist:
                endelea
            module_object = getattr(server, name)
            ikiwa getattr(module_object, '__module__', Tupu) == 'http.server':
                expected.append(name)
        self.assertCountEqual(server.__all__, expected)


kundi ScriptTestCase(unittest.TestCase):

    eleza mock_server_class(self):
        rudisha mock.MagicMock(
            rudisha_value=mock.MagicMock(
                __enter__=mock.MagicMock(
                    rudisha_value=mock.MagicMock(
                        socket=mock.MagicMock(
                            getsockname=lambda: ('', 0),
                        ),
                    ),
                ),
            ),
        )

    @mock.patch('builtins.print')
    eleza test_server_test_unspec(self, _):
        mock_server = self.mock_server_class()
        server.test(ServerClass=mock_server, bind=Tupu)
        self.assertIn(
            mock_server.address_family,
            (socket.AF_INET6, socket.AF_INET),
        )

    @mock.patch('builtins.print')
    eleza test_server_test_localhost(self, _):
        mock_server = self.mock_server_class()
        server.test(ServerClass=mock_server, bind="localhost")
        self.assertIn(
            mock_server.address_family,
            (socket.AF_INET6, socket.AF_INET),
        )

    ipv6_addrs = (
        "::",
        "2001:0db8:85a3:0000:0000:8a2e:0370:7334",
        "::1",
    )

    ipv4_addrs = (
        "0.0.0.0",
        "8.8.8.8",
        "127.0.0.1",
    )

    @mock.patch('builtins.print')
    eleza test_server_test_ipv6(self, _):
        kila bind kwenye self.ipv6_addrs:
            mock_server = self.mock_server_class()
            server.test(ServerClass=mock_server, bind=bind)
            self.assertEqual(mock_server.address_family, socket.AF_INET6)

    @mock.patch('builtins.print')
    eleza test_server_test_ipv4(self, _):
        kila bind kwenye self.ipv4_addrs:
            mock_server = self.mock_server_class()
            server.test(ServerClass=mock_server, bind=bind)
            self.assertEqual(mock_server.address_family, socket.AF_INET)


eleza test_main(verbose=Tupu):
    cwd = os.getcwd()
    jaribu:
        support.run_unittest(
            RequestHandlerLoggingTestCase,
            BaseHTTPRequestHandlerTestCase,
            BaseHTTPServerTestCase,
            SimpleHTTPServerTestCase,
            CGIHTTPServerTestCase,
            SimpleHTTPRequestHandlerTestCase,
            MiscTestCase,
            ScriptTestCase
        )
    mwishowe:
        os.chdir(cwd)

ikiwa __name__ == '__main__':
    test_main()
