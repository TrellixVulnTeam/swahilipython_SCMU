"""Unit tests kila code kwenye urllib.response."""

agiza socket
agiza tempfile
agiza urllib.response
agiza unittest

kundi TestResponse(unittest.TestCase):

    eleza setUp(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.fp = self.sock.makefile('rb')
        self.test_headers = {"Host": "www.python.org",
                             "Connection": "close"}

    eleza test_with(self):
        addbase = urllib.response.addbase(self.fp)

        self.assertIsInstance(addbase, tempfile._TemporaryFileWrapper)

        eleza f():
            ukijumuisha addbase kama spam:
                pita
        self.assertUongo(self.fp.closed)
        f()
        self.assertKweli(self.fp.closed)
        self.assertRaises(ValueError, f)

    eleza test_addclosehook(self):
        closehook_called = Uongo

        eleza closehook():
            nonlocal closehook_called
            closehook_called = Kweli

        closehook = urllib.response.addclosehook(self.fp, closehook)
        closehook.close()

        self.assertKweli(self.fp.closed)
        self.assertKweli(closehook_called)

    eleza test_addinfo(self):
        info = urllib.response.addinfo(self.fp, self.test_headers)
        self.assertEqual(info.info(), self.test_headers)

    eleza test_addinfourl(self):
        url = "http://www.python.org"
        code = 200
        infourl = urllib.response.addinfourl(self.fp, self.test_headers,
                                             url, code)
        self.assertEqual(infourl.info(), self.test_headers)
        self.assertEqual(infourl.geturl(), url)
        self.assertEqual(infourl.getcode(), code)

    eleza tearDown(self):
        self.sock.close()

ikiwa __name__ == '__main__':
    unittest.main()
