agiza io
agiza socket
agiza datetime
agiza textwrap
agiza unittest
agiza functools
agiza contextlib
agiza os.path
agiza re
agiza threading

kutoka test agiza support
kutoka nntplib agiza NNTP, GroupInfo
agiza nntplib
kutoka unittest.mock agiza patch
jaribu:
    agiza ssl
tatizo ImportError:
    ssl = Tupu


TIMEOUT = 30
certfile = os.path.join(os.path.dirname(__file__), 'keycert3.pem')

ikiwa ssl ni sio Tupu:
    SSLError = ssl.SSLError
isipokua:
    kundi SSLError(Exception):
        """Non-existent exception kundi when we lack SSL support."""
        reason = "This will never be ashiriad."

# TODO:
# - test the `file` arg to more commands
# - test error conditions
# - test auth na `usenetrc`


kundi NetworkedNNTPTestsMixin:

    eleza test_welcome(self):
        welcome = self.server.getwelcome()
        self.assertEqual(str, type(welcome))

    eleza test_help(self):
        resp, lines = self.server.help()
        self.assertKweli(resp.startswith("100 "), resp)
        kila line kwenye lines:
            self.assertEqual(str, type(line))

    eleza test_list(self):
        resp, groups = self.server.list()
        ikiwa len(groups) > 0:
            self.assertEqual(GroupInfo, type(groups[0]))
            self.assertEqual(str, type(groups[0].group))

    eleza test_list_active(self):
        resp, groups = self.server.list(self.GROUP_PAT)
        ikiwa len(groups) > 0:
            self.assertEqual(GroupInfo, type(groups[0]))
            self.assertEqual(str, type(groups[0].group))

    eleza test_unknown_command(self):
        ukijumuisha self.assertRaises(nntplib.NNTPPermanentError) kama cm:
            self.server._shortcmd("XYZZY")
        resp = cm.exception.response
        self.assertKweli(resp.startswith("500 "), resp)

    eleza test_newgroups(self):
        # gmane gets a constant influx of new groups.  In order sio to stress
        # the server too much, we choose a recent date kwenye the past.
        dt = datetime.date.today() - datetime.timedelta(days=7)
        resp, groups = self.server.newgroups(dt)
        ikiwa len(groups) > 0:
            self.assertIsInstance(groups[0], GroupInfo)
            self.assertIsInstance(groups[0].group, str)

    eleza test_description(self):
        eleza _check_desc(desc):
            # Sanity checks
            self.assertIsInstance(desc, str)
            self.assertNotIn(self.GROUP_NAME, desc)
        desc = self.server.description(self.GROUP_NAME)
        _check_desc(desc)
        # Another sanity check
        self.assertIn("Python", desc)
        # With a pattern
        desc = self.server.description(self.GROUP_PAT)
        _check_desc(desc)
        # Shouldn't exist
        desc = self.server.description("zk.brrtt.baz")
        self.assertEqual(desc, '')

    eleza test_descriptions(self):
        resp, descs = self.server.descriptions(self.GROUP_PAT)
        # 215 kila LIST NEWSGROUPS, 282 kila XGTITLE
        self.assertKweli(
            resp.startswith("215 ") ama resp.startswith("282 "), resp)
        self.assertIsInstance(descs, dict)
        desc = descs[self.GROUP_NAME]
        self.assertEqual(desc, self.server.description(self.GROUP_NAME))

    eleza test_group(self):
        result = self.server.group(self.GROUP_NAME)
        self.assertEqual(5, len(result))
        resp, count, first, last, group = result
        self.assertEqual(group, self.GROUP_NAME)
        self.assertIsInstance(count, int)
        self.assertIsInstance(first, int)
        self.assertIsInstance(last, int)
        self.assertLessEqual(first, last)
        self.assertKweli(resp.startswith("211 "), resp)

    eleza test_date(self):
        resp, date = self.server.date()
        self.assertIsInstance(date, datetime.datetime)
        # Sanity check
        self.assertGreaterEqual(date.year, 1995)
        self.assertLessEqual(date.year, 2030)

    eleza _check_art_dict(self, art_dict):
        # Some sanity checks kila a field dictionary rudishaed by OVER / XOVER
        self.assertIsInstance(art_dict, dict)
        # NNTP has 7 mandatory fields
        self.assertGreaterEqual(art_dict.keys(),
            {"subject", "kutoka", "date", "message-id",
             "references", ":bytes", ":lines"}
            )
        kila v kwenye art_dict.values():
            self.assertIsInstance(v, (str, type(Tupu)))

    eleza test_xover(self):
        resp, count, first, last, name = self.server.group(self.GROUP_NAME)
        resp, lines = self.server.xover(last - 5, last)
        ikiwa len(lines) == 0:
            self.skipTest("no articles retrieved")
        # The 'last' article ni sio necessarily part of the output (cancelled?)
        art_num, art_dict = lines[0]
        self.assertGreaterEqual(art_num, last - 5)
        self.assertLessEqual(art_num, last)
        self._check_art_dict(art_dict)

    @unittest.skipIf(Kweli, 'temporarily skipped until a permanent solution'
                           ' ni found kila issue #28971')
    eleza test_over(self):
        resp, count, first, last, name = self.server.group(self.GROUP_NAME)
        start = last - 10
        # The "start-" article range form
        resp, lines = self.server.over((start, Tupu))
        art_num, art_dict = lines[0]
        self._check_art_dict(art_dict)
        # The "start-end" article range form
        resp, lines = self.server.over((start, last))
        art_num, art_dict = lines[-1]
        # The 'last' article ni sio necessarily part of the output (cancelled?)
        self.assertGreaterEqual(art_num, start)
        self.assertLessEqual(art_num, last)
        self._check_art_dict(art_dict)
        # XXX The "message_id" form ni unsupported by gmane
        # 503 Overview by message-ID unsupported

    eleza test_xhdr(self):
        resp, count, first, last, name = self.server.group(self.GROUP_NAME)
        resp, lines = self.server.xhdr('subject', last)
        kila line kwenye lines:
            self.assertEqual(str, type(line[1]))

    eleza check_article_resp(self, resp, article, art_num=Tupu):
        self.assertIsInstance(article, nntplib.ArticleInfo)
        ikiwa art_num ni sio Tupu:
            self.assertEqual(article.number, art_num)
        kila line kwenye article.lines:
            self.assertIsInstance(line, bytes)
        # XXX this could exceptionally happen...
        self.assertNotIn(article.lines[-1], (b".", b".\n", b".\r\n"))

    @unittest.skipIf(Kweli, "FIXME: see bpo-32128")
    eleza test_article_head_body(self):
        resp, count, first, last, name = self.server.group(self.GROUP_NAME)
        # Try to find an available article
        kila art_num kwenye (last, first, last - 1):
            jaribu:
                resp, head = self.server.head(art_num)
            tatizo nntplib.NNTPTemporaryError kama e:
                ikiwa sio e.response.startswith("423 "):
                    ashiria
                # "423 No such article" => choose another one
                endelea
            koma
        isipokua:
            self.skipTest("could sio find a suitable article number")
        self.assertKweli(resp.startswith("221 "), resp)
        self.check_article_resp(resp, head, art_num)
        resp, body = self.server.body(art_num)
        self.assertKweli(resp.startswith("222 "), resp)
        self.check_article_resp(resp, body, art_num)
        resp, article = self.server.article(art_num)
        self.assertKweli(resp.startswith("220 "), resp)
        self.check_article_resp(resp, article, art_num)
        # Tolerate running the tests kutoka behind a NNTP virus checker
        blacklist = lambda line: line.startswith(b'X-Antivirus')
        filtered_head_lines = [line kila line kwenye head.lines
                               ikiwa sio blacklist(line)]
        filtered_lines = [line kila line kwenye article.lines
                          ikiwa sio blacklist(line)]
        self.assertEqual(filtered_lines, filtered_head_lines + [b''] + body.lines)

    eleza test_capabilities(self):
        # The server under test implements NNTP version 2 na has a
        # couple of well-known capabilities. Just sanity check that we
        # got them.
        eleza _check_caps(caps):
            caps_list = caps['LIST']
            self.assertIsInstance(caps_list, (list, tuple))
            self.assertIn('OVERVIEW.FMT', caps_list)
        self.assertGreaterEqual(self.server.nntp_version, 2)
        _check_caps(self.server.getcapabilities())
        # This re-emits the command
        resp, caps = self.server.capabilities()
        _check_caps(caps)

    eleza test_zlogin(self):
        # This test must be the penultimate because further commands will be
        # refused.
        baduser = "notarealuser"
        badpw = "notarealpitaword"
        # Check that bogus credentials cause failure
        self.assertRaises(nntplib.NNTPError, self.server.login,
                          user=baduser, pitaword=badpw, usenetrc=Uongo)
        # FIXME: We should check that correct credentials succeed, but that
        # would require valid details kila some server somewhere to be kwenye the
        # test suite, I think. Gmane ni anonymous, at least kama used kila the
        # other tests.

    eleza test_zzquit(self):
        # This test must be called last, hence the name
        cls = type(self)
        jaribu:
            self.server.quit()
        mwishowe:
            cls.server = Tupu

    @classmethod
    eleza wrap_methods(cls):
        # Wrap all methods kwenye a transient_internet() exception catcher
        # XXX put a generic version kwenye test.support?
        eleza wrap_meth(meth):
            @functools.wraps(meth)
            eleza wrapped(self):
                ukijumuisha support.transient_internet(self.NNTP_HOST):
                    meth(self)
            rudisha wrapped
        kila name kwenye dir(cls):
            ikiwa sio name.startswith('test_'):
                endelea
            meth = getattr(cls, name)
            ikiwa sio callable(meth):
                endelea
            # Need to use a closure so that meth remains bound to its current
            # value
            setattr(cls, name, wrap_meth(meth))

    eleza test_with_statement(self):
        eleza is_connected():
            ikiwa sio hasattr(server, 'file'):
                rudisha Uongo
            jaribu:
                server.help()
            tatizo (OSError, EOFError):
                rudisha Uongo
            rudisha Kweli

        jaribu:
            ukijumuisha self.NNTP_CLASS(self.NNTP_HOST, timeout=TIMEOUT, usenetrc=Uongo) kama server:
                self.assertKweli(is_connected())
                self.assertKweli(server.help())
            self.assertUongo(is_connected())

            ukijumuisha self.NNTP_CLASS(self.NNTP_HOST, timeout=TIMEOUT, usenetrc=Uongo) kama server:
                server.quit()
            self.assertUongo(is_connected())
        tatizo SSLError kama ssl_err:
            # matches "[SSL: DH_KEY_TOO_SMALL] dh key too small"
            ikiwa re.search(r'(?i)KEY.TOO.SMALL', ssl_err.reason):
                ashiria unittest.SkipTest(f"Got {ssl_err} connecting "
                                        f"to {self.NNTP_HOST!r}")
            ashiria


NetworkedNNTPTestsMixin.wrap_methods()


EOF_ERRORS = (EOFError,)
ikiwa ssl ni sio Tupu:
    EOF_ERRORS += (ssl.SSLEOFError,)


kundi NetworkedNNTPTests(NetworkedNNTPTestsMixin, unittest.TestCase):
    # This server supports STARTTLS (gmane doesn't)
    NNTP_HOST = 'news.trigofacile.com'
    GROUP_NAME = 'fr.comp.lang.python'
    GROUP_PAT = 'fr.comp.lang.*'

    NNTP_CLASS = NNTP

    @classmethod
    eleza setUpClass(cls):
        support.requires("network")
        ukijumuisha support.transient_internet(cls.NNTP_HOST):
            jaribu:
                cls.server = cls.NNTP_CLASS(cls.NNTP_HOST, timeout=TIMEOUT,
                                            usenetrc=Uongo)
            tatizo SSLError kama ssl_err:
                # matches "[SSL: DH_KEY_TOO_SMALL] dh key too small"
                ikiwa re.search(r'(?i)KEY.TOO.SMALL', ssl_err.reason):
                    ashiria unittest.SkipTest(f"{cls} got {ssl_err} connecting "
                                            f"to {cls.NNTP_HOST!r}")
                ashiria
            tatizo EOF_ERRORS:
                ashiria unittest.SkipTest(f"{cls} got EOF error on connecting "
                                        f"to {cls.NNTP_HOST!r}")

    @classmethod
    eleza tearDownClass(cls):
        ikiwa cls.server ni sio Tupu:
            cls.server.quit()

@unittest.skipUnless(ssl, 'requires SSL support')
kundi NetworkedNNTP_SSLTests(NetworkedNNTPTests):

    # Technical limits kila this public NNTP server (see http://www.aioe.org):
    # "Only two concurrent connections per IP address are allowed and
    # 400 connections per day are accepted kutoka each IP address."

    NNTP_HOST = 'nntp.aioe.org'
    GROUP_NAME = 'comp.lang.python'
    GROUP_PAT = 'comp.lang.*'

    NNTP_CLASS = getattr(nntplib, 'NNTP_SSL', Tupu)

    # Disabled kama it produces too much data
    test_list = Tupu

    # Disabled kama the connection will already be encrypted.
    test_starttls = Tupu


#
# Non-networked tests using a local server (or something mocking it).
#

kundi _NNTPServerIO(io.RawIOBase):
    """A raw IO object allowing NNTP commands to be received na processed
    by a handler.  The handler can push responses which can then be read
    kutoka the IO object."""

    eleza __init__(self, handler):
        io.RawIOBase.__init__(self)
        # The channel kutoka the client
        self.c2s = io.BytesIO()
        # The channel to the client
        self.s2c = io.BytesIO()
        self.handler = handler
        self.handler.start(self.c2s.readline, self.push_data)

    eleza readable(self):
        rudisha Kweli

    eleza writable(self):
        rudisha Kweli

    eleza push_data(self, data):
        """Push (buffer) some data to send to the client."""
        pos = self.s2c.tell()
        self.s2c.seek(0, 2)
        self.s2c.write(data)
        self.s2c.seek(pos)

    eleza write(self, b):
        """The client sends us some data"""
        pos = self.c2s.tell()
        self.c2s.write(b)
        self.c2s.seek(pos)
        self.handler.process_pending()
        rudisha len(b)

    eleza readinto(self, buf):
        """The client wants to read a response"""
        self.handler.process_pending()
        b = self.s2c.read(len(buf))
        n = len(b)
        buf[:n] = b
        rudisha n


eleza make_mock_file(handler):
    sio = _NNTPServerIO(handler)
    # Using BufferedRWPair instead of BufferedRandom ensures the file
    # isn't seekable.
    file = io.BufferedRWPair(sio, sio)
    rudisha (sio, file)


kundi MockedNNTPTestsMixin:
    # Override kwenye derived classes
    handler_kundi = Tupu

    eleza setUp(self):
        super().setUp()
        self.make_server()

    eleza tearDown(self):
        super().tearDown()
        toa self.server

    eleza make_server(self, *args, **kwargs):
        self.handler = self.handler_class()
        self.sio, file = make_mock_file(self.handler)
        self.server = nntplib._NNTPBase(file, 'test.server', *args, **kwargs)
        rudisha self.server


kundi MockedNNTPWithReaderModeMixin(MockedNNTPTestsMixin):
    eleza setUp(self):
        super().setUp()
        self.make_server(readermode=Kweli)


kundi NNTPv1Handler:
    """A handler kila RFC 977"""

    welcome = "200 NNTP mock server"

    eleza start(self, readline, push_data):
        self.in_body = Uongo
        self.allow_posting = Kweli
        self._readline = readline
        self._push_data = push_data
        self._logged_in = Uongo
        self._user_sent = Uongo
        # Our welcome
        self.handle_welcome()

    eleza _decode(self, data):
        rudisha str(data, "utf-8", "surrogateescape")

    eleza process_pending(self):
        ikiwa self.in_body:
            wakati Kweli:
                line = self._readline()
                ikiwa sio line:
                    rudisha
                self.body.append(line)
                ikiwa line == b".\r\n":
                    koma
            jaribu:
                meth, tokens = self.body_callback
                meth(*tokens, body=self.body)
            mwishowe:
                self.body_callback = Tupu
                self.body = Tupu
                self.in_body = Uongo
        wakati Kweli:
            line = self._decode(self._readline())
            ikiwa sio line:
                rudisha
            ikiwa sio line.endswith("\r\n"):
                ashiria ValueError("line doesn't end ukijumuisha \\r\\n: {!r}".format(line))
            line = line[:-2]
            cmd, *tokens = line.split()
            #meth = getattr(self.handler, "handle_" + cmd.upper(), Tupu)
            meth = getattr(self, "handle_" + cmd.upper(), Tupu)
            ikiwa meth ni Tupu:
                self.handle_unknown()
            isipokua:
                jaribu:
                    meth(*tokens)
                tatizo Exception kama e:
                    ashiria ValueError("command failed: {!r}".format(line)) kutoka e
                isipokua:
                    ikiwa self.in_body:
                        self.body_callback = meth, tokens
                        self.body = []

    eleza expect_body(self):
        """Flag that the client ni expected to post a request body"""
        self.in_body = Kweli

    eleza push_data(self, data):
        """Push some binary data"""
        self._push_data(data)

    eleza push_lit(self, lit):
        """Push a string literal"""
        lit = textwrap.dedent(lit)
        lit = "\r\n".join(lit.splitlines()) + "\r\n"
        lit = lit.encode('utf-8')
        self.push_data(lit)

    eleza handle_unknown(self):
        self.push_lit("500 What?")

    eleza handle_welcome(self):
        self.push_lit(self.welcome)

    eleza handle_QUIT(self):
        self.push_lit("205 Bye!")

    eleza handle_DATE(self):
        self.push_lit("111 20100914001155")

    eleza handle_GROUP(self, group):
        ikiwa group == "fr.comp.lang.python":
            self.push_lit("211 486 761 1265 fr.comp.lang.python")
        isipokua:
            self.push_lit("411 No such group {}".format(group))

    eleza handle_HELP(self):
        self.push_lit("""\
            100 Legal commands
              authinfo user Name|pita Password|generic <prog> <args>
              date
              help
            Report problems to <root@example.org>
            .""")

    eleza handle_STAT(self, message_spec=Tupu):
        ikiwa message_spec ni Tupu:
            self.push_lit("412 No newsgroup selected")
        lasivyo message_spec == "3000234":
            self.push_lit("223 3000234 <45223423@example.com>")
        lasivyo message_spec == "<45223423@example.com>":
            self.push_lit("223 0 <45223423@example.com>")
        isipokua:
            self.push_lit("430 No Such Article Found")

    eleza handle_NEXT(self):
        self.push_lit("223 3000237 <668929@example.org> retrieved")

    eleza handle_LAST(self):
        self.push_lit("223 3000234 <45223423@example.com> retrieved")

    eleza handle_LIST(self, action=Tupu, param=Tupu):
        ikiwa action ni Tupu:
            self.push_lit("""\
                215 Newsgroups kwenye form "group high low flags".
                comp.lang.python 0000052340 0000002828 y
                comp.lang.python.announce 0000001153 0000000993 m
                free.it.comp.lang.python 0000000002 0000000002 y
                fr.comp.lang.python 0000001254 0000000760 y
                free.it.comp.lang.python.learner 0000000000 0000000001 y
                tw.bbs.comp.lang.python 0000000304 0000000304 y
                .""")
        lasivyo action == "ACTIVE":
            ikiwa param == "*distutils*":
                self.push_lit("""\
                    215 Newsgroups kwenye form "group high low flags"
                    gmane.comp.python.distutils.devel 0000014104 0000000001 m
                    gmane.comp.python.distutils.cvs 0000000000 0000000001 m
                    .""")
            isipokua:
                self.push_lit("""\
                    215 Newsgroups kwenye form "group high low flags"
                    .""")
        lasivyo action == "OVERVIEW.FMT":
            self.push_lit("""\
                215 Order of fields kwenye overview database.
                Subject:
                From:
                Date:
                Message-ID:
                References:
                Bytes:
                Lines:
                Xref:full
                .""")
        lasivyo action == "NEWSGROUPS":
            assert param ni sio Tupu
            ikiwa param == "comp.lang.python":
                self.push_lit("""\
                    215 Descriptions kwenye form "group description".
                    comp.lang.python\tThe Python computer language.
                    .""")
            lasivyo param == "comp.lang.python*":
                self.push_lit("""\
                    215 Descriptions kwenye form "group description".
                    comp.lang.python.announce\tAnnouncements about the Python language. (Moderated)
                    comp.lang.python\tThe Python computer language.
                    .""")
            isipokua:
                self.push_lit("""\
                    215 Descriptions kwenye form "group description".
                    .""")
        isipokua:
            self.push_lit('501 Unknown LIST keyword')

    eleza handle_NEWNEWS(self, group, date_str, time_str):
        # We hard code different rudisha messages depending on pitaed
        # argument na date syntax.
        ikiwa (group == "comp.lang.python" na date_str == "20100913"
            na time_str == "082004"):
            # Date was pitaed kwenye RFC 3977 format (NNTP "v2")
            self.push_lit("""\
                230 list of newsarticles (NNTP v2) created after Mon Sep 13 08:20:04 2010 follows
                <a4929a40-6328-491a-aaaf-cb79ed7309a2@q2g2000vbk.googlegroups.com>
                <f30c0419-f549-4218-848f-d7d0131da931@y3g2000vbm.googlegroups.com>
                .""")
        lasivyo (group == "comp.lang.python" na date_str == "100913"
            na time_str == "082004"):
            # Date was pitaed kwenye RFC 977 format (NNTP "v1")
            self.push_lit("""\
                230 list of newsarticles (NNTP v1) created after Mon Sep 13 08:20:04 2010 follows
                <a4929a40-6328-491a-aaaf-cb79ed7309a2@q2g2000vbk.googlegroups.com>
                <f30c0419-f549-4218-848f-d7d0131da931@y3g2000vbm.googlegroups.com>
                .""")
        lasivyo (group == 'comp.lang.python' and
              date_str kwenye ('20100101', '100101') and
              time_str == '090000'):
            self.push_lit('too long line' * 3000 +
                          '\n.')
        isipokua:
            self.push_lit("""\
                230 An empty list of newsarticles follows
                .""")
        # (Note kila experiments: many servers disable NEWNEWS.
        #  As of this writing, sicinfo3.epfl.ch doesn't.)

    eleza handle_XOVER(self, message_spec):
        ikiwa message_spec == "57-59":
            self.push_lit(
                "224 Overview information kila 57-58 follows\n"
                "57\tRe: ANN: New Plone book ukijumuisha strong Python (and Zope) themes throughout"
                    "\tDoug Hellmann <doug.hellmann-Re5JQEeQqe8AvxtiuMwx3w@public.gmane.org>"
                    "\tSat, 19 Jun 2010 18:04:08 -0400"
                    "\t<4FD05F05-F98B-44DC-8111-C6009C925F0C@gmail.com>"
                    "\t<hvalf7$ort$1@dough.gmane.org>\t7103\t16"
                    "\tXref: news.gmane.org gmane.comp.python.authors:57"
                    "\n"
                "58\tLooking kila a few good bloggers"
                    "\tDoug Hellmann <doug.hellmann-Re5JQEeQqe8AvxtiuMwx3w@public.gmane.org>"
                    "\tThu, 22 Jul 2010 09:14:14 -0400"
                    "\t<A29863FA-F388-40C3-AA25-0FD06B09B5BF@gmail.com>"
                    "\t\t6683\t16"
                    "\t"
                    "\n"
                # A UTF-8 overview line kutoka fr.comp.lang.python
                "59\tRe: Message d'erreur incompréhensible (par moi)"
                    "\tEric Brunel <eric.brunel@pragmadev.nospam.com>"
                    "\tWed, 15 Sep 2010 18:09:15 +0200"
                    "\t<eric.brunel-2B8B56.18091515092010@news.wanadoo.fr>"
                    "\t<4c90ec87$0$32425$ba4acef3@reader.news.orange.fr>\t1641\t27"
                    "\tXref: saria.nerim.net fr.comp.lang.python:1265"
                    "\n"
                ".\n")
        isipokua:
            self.push_lit("""\
                224 No articles
                .""")

    eleza handle_POST(self, *, body=Tupu):
        ikiwa body ni Tupu:
            ikiwa self.allow_posting:
                self.push_lit("340 Input article; end ukijumuisha <CR-LF>.<CR-LF>")
                self.expect_body()
            isipokua:
                self.push_lit("440 Posting sio permitted")
        isipokua:
            assert self.allow_posting
            self.push_lit("240 Article received OK")
            self.posted_body = body

    eleza handle_IHAVE(self, message_id, *, body=Tupu):
        ikiwa body ni Tupu:
            ikiwa (self.allow_posting and
                message_id == "<i.am.an.article.you.will.want@example.com>"):
                self.push_lit("335 Send it; end ukijumuisha <CR-LF>.<CR-LF>")
                self.expect_body()
            isipokua:
                self.push_lit("435 Article sio wanted")
        isipokua:
            assert self.allow_posting
            self.push_lit("235 Article transferred OK")
            self.posted_body = body

    sample_head = """\
        From: "Demo User" <nobody@example.net>
        Subject: I am just a test article
        Content-Type: text/plain; charset=UTF-8; format=flowed
        Message-ID: <i.am.an.article.you.will.want@example.com>"""

    sample_body = """\
        This ni just a test article.
        ..Here ni a dot-starting line.

        -- Signed by Andr\xe9."""

    sample_article = sample_head + "\n\n" + sample_body

    eleza handle_ARTICLE(self, message_spec=Tupu):
        ikiwa message_spec ni Tupu:
            self.push_lit("220 3000237 <45223423@example.com>")
        lasivyo message_spec == "<45223423@example.com>":
            self.push_lit("220 0 <45223423@example.com>")
        lasivyo message_spec == "3000234":
            self.push_lit("220 3000234 <45223423@example.com>")
        isipokua:
            self.push_lit("430 No Such Article Found")
            rudisha
        self.push_lit(self.sample_article)
        self.push_lit(".")

    eleza handle_HEAD(self, message_spec=Tupu):
        ikiwa message_spec ni Tupu:
            self.push_lit("221 3000237 <45223423@example.com>")
        lasivyo message_spec == "<45223423@example.com>":
            self.push_lit("221 0 <45223423@example.com>")
        lasivyo message_spec == "3000234":
            self.push_lit("221 3000234 <45223423@example.com>")
        isipokua:
            self.push_lit("430 No Such Article Found")
            rudisha
        self.push_lit(self.sample_head)
        self.push_lit(".")

    eleza handle_BODY(self, message_spec=Tupu):
        ikiwa message_spec ni Tupu:
            self.push_lit("222 3000237 <45223423@example.com>")
        lasivyo message_spec == "<45223423@example.com>":
            self.push_lit("222 0 <45223423@example.com>")
        lasivyo message_spec == "3000234":
            self.push_lit("222 3000234 <45223423@example.com>")
        isipokua:
            self.push_lit("430 No Such Article Found")
            rudisha
        self.push_lit(self.sample_body)
        self.push_lit(".")

    eleza handle_AUTHINFO(self, cred_type, data):
        ikiwa self._logged_in:
            self.push_lit('502 Already Logged In')
        lasivyo cred_type == 'user':
            ikiwa self._user_sent:
                self.push_lit('482 User Credential Already Sent')
            isipokua:
                self.push_lit('381 Password Required')
                self._user_sent = Kweli
        lasivyo cred_type == 'pita':
            self.push_lit('281 Login Successful')
            self._logged_in = Kweli
        isipokua:
            ashiria Exception('Unknown cred type {}'.format(cred_type))


kundi NNTPv2Handler(NNTPv1Handler):
    """A handler kila RFC 3977 (NNTP "v2")"""

    eleza handle_CAPABILITIES(self):
        fmt = """\
            101 Capability list:
            VERSION 2 3
            IMPLEMENTATION INN 2.5.1{}
            HDR
            LIST ACTIVE ACTIVE.TIMES DISTRIB.PATS HEADERS NEWSGROUPS OVERVIEW.FMT
            OVER
            POST
            READER
            ."""

        ikiwa sio self._logged_in:
            self.push_lit(fmt.format('\n            AUTHINFO USER'))
        isipokua:
            self.push_lit(fmt.format(''))

    eleza handle_MODE(self, _):
        ashiria Exception('MODE READER sent despite READER has been advertised')

    eleza handle_OVER(self, message_spec=Tupu):
        rudisha self.handle_XOVER(message_spec)


kundi CapsAfterLoginNNTPv2Handler(NNTPv2Handler):
    """A handler that allows CAPABILITIES only after login"""

    eleza handle_CAPABILITIES(self):
        ikiwa sio self._logged_in:
            self.push_lit('480 You must log in.')
        isipokua:
            super().handle_CAPABILITIES()


kundi ModeSwitchingNNTPv2Handler(NNTPv2Handler):
    """A server that starts kwenye transit mode"""

    eleza __init__(self):
        self._switched = Uongo

    eleza handle_CAPABILITIES(self):
        fmt = """\
            101 Capability list:
            VERSION 2 3
            IMPLEMENTATION INN 2.5.1
            HDR
            LIST ACTIVE ACTIVE.TIMES DISTRIB.PATS HEADERS NEWSGROUPS OVERVIEW.FMT
            OVER
            POST
            {}READER
            ."""
        ikiwa self._switched:
            self.push_lit(fmt.format(''))
        isipokua:
            self.push_lit(fmt.format('MODE-'))

    eleza handle_MODE(self, what):
        assert sio self._switched na what == 'reader'
        self._switched = Kweli
        self.push_lit('200 Posting allowed')


kundi NNTPv1v2TestsMixin:

    eleza setUp(self):
        super().setUp()

    eleza test_welcome(self):
        self.assertEqual(self.server.welcome, self.handler.welcome)

    eleza test_authinfo(self):
        ikiwa self.nntp_version == 2:
            self.assertIn('AUTHINFO', self.server._caps)
        self.server.login('testuser', 'testpw')
        # ikiwa AUTHINFO ni gone kutoka _caps we also know that getcapabilities()
        # has been called after login kama it should
        self.assertNotIn('AUTHINFO', self.server._caps)

    eleza test_date(self):
        resp, date = self.server.date()
        self.assertEqual(resp, "111 20100914001155")
        self.assertEqual(date, datetime.datetime(2010, 9, 14, 0, 11, 55))

    eleza test_quit(self):
        self.assertUongo(self.sio.closed)
        resp = self.server.quit()
        self.assertEqual(resp, "205 Bye!")
        self.assertKweli(self.sio.closed)

    eleza test_help(self):
        resp, help = self.server.help()
        self.assertEqual(resp, "100 Legal commands")
        self.assertEqual(help, [
            '  authinfo user Name|pita Password|generic <prog> <args>',
            '  date',
            '  help',
            'Report problems to <root@example.org>',
        ])

    eleza test_list(self):
        resp, groups = self.server.list()
        self.assertEqual(len(groups), 6)
        g = groups[1]
        self.assertEqual(g,
            GroupInfo("comp.lang.python.announce", "0000001153",
                      "0000000993", "m"))
        resp, groups = self.server.list("*distutils*")
        self.assertEqual(len(groups), 2)
        g = groups[0]
        self.assertEqual(g,
            GroupInfo("gmane.comp.python.distutils.devel", "0000014104",
                      "0000000001", "m"))

    eleza test_stat(self):
        resp, art_num, message_id = self.server.stat(3000234)
        self.assertEqual(resp, "223 3000234 <45223423@example.com>")
        self.assertEqual(art_num, 3000234)
        self.assertEqual(message_id, "<45223423@example.com>")
        resp, art_num, message_id = self.server.stat("<45223423@example.com>")
        self.assertEqual(resp, "223 0 <45223423@example.com>")
        self.assertEqual(art_num, 0)
        self.assertEqual(message_id, "<45223423@example.com>")
        ukijumuisha self.assertRaises(nntplib.NNTPTemporaryError) kama cm:
            self.server.stat("<non.existent.id>")
        self.assertEqual(cm.exception.response, "430 No Such Article Found")
        ukijumuisha self.assertRaises(nntplib.NNTPTemporaryError) kama cm:
            self.server.stat()
        self.assertEqual(cm.exception.response, "412 No newsgroup selected")

    eleza test_next(self):
        resp, art_num, message_id = self.server.next()
        self.assertEqual(resp, "223 3000237 <668929@example.org> retrieved")
        self.assertEqual(art_num, 3000237)
        self.assertEqual(message_id, "<668929@example.org>")

    eleza test_last(self):
        resp, art_num, message_id = self.server.last()
        self.assertEqual(resp, "223 3000234 <45223423@example.com> retrieved")
        self.assertEqual(art_num, 3000234)
        self.assertEqual(message_id, "<45223423@example.com>")

    eleza test_description(self):
        desc = self.server.description("comp.lang.python")
        self.assertEqual(desc, "The Python computer language.")
        desc = self.server.description("comp.lang.pythonx")
        self.assertEqual(desc, "")

    eleza test_descriptions(self):
        resp, groups = self.server.descriptions("comp.lang.python")
        self.assertEqual(resp, '215 Descriptions kwenye form "group description".')
        self.assertEqual(groups, {
            "comp.lang.python": "The Python computer language.",
            })
        resp, groups = self.server.descriptions("comp.lang.python*")
        self.assertEqual(groups, {
            "comp.lang.python": "The Python computer language.",
            "comp.lang.python.announce": "Announcements about the Python language. (Moderated)",
            })
        resp, groups = self.server.descriptions("comp.lang.pythonx")
        self.assertEqual(groups, {})

    eleza test_group(self):
        resp, count, first, last, group = self.server.group("fr.comp.lang.python")
        self.assertKweli(resp.startswith("211 "), resp)
        self.assertEqual(first, 761)
        self.assertEqual(last, 1265)
        self.assertEqual(count, 486)
        self.assertEqual(group, "fr.comp.lang.python")
        ukijumuisha self.assertRaises(nntplib.NNTPTemporaryError) kama cm:
            self.server.group("comp.lang.python.devel")
        exc = cm.exception
        self.assertKweli(exc.response.startswith("411 No such group"),
                        exc.response)

    eleza test_newnews(self):
        # NEWNEWS comp.lang.python [20]100913 082004
        dt = datetime.datetime(2010, 9, 13, 8, 20, 4)
        resp, ids = self.server.newnews("comp.lang.python", dt)
        expected = (
            "230 list of newsarticles (NNTP v{0}) "
            "created after Mon Sep 13 08:20:04 2010 follows"
            ).format(self.nntp_version)
        self.assertEqual(resp, expected)
        self.assertEqual(ids, [
            "<a4929a40-6328-491a-aaaf-cb79ed7309a2@q2g2000vbk.googlegroups.com>",
            "<f30c0419-f549-4218-848f-d7d0131da931@y3g2000vbm.googlegroups.com>",
            ])
        # NEWNEWS fr.comp.lang.python [20]100913 082004
        dt = datetime.datetime(2010, 9, 13, 8, 20, 4)
        resp, ids = self.server.newnews("fr.comp.lang.python", dt)
        self.assertEqual(resp, "230 An empty list of newsarticles follows")
        self.assertEqual(ids, [])

    eleza _check_article_body(self, lines):
        self.assertEqual(len(lines), 4)
        self.assertEqual(lines[-1].decode('utf-8'), "-- Signed by André.")
        self.assertEqual(lines[-2], b"")
        self.assertEqual(lines[-3], b".Here ni a dot-starting line.")
        self.assertEqual(lines[-4], b"This ni just a test article.")

    eleza _check_article_head(self, lines):
        self.assertEqual(len(lines), 4)
        self.assertEqual(lines[0], b'From: "Demo User" <nobody@example.net>')
        self.assertEqual(lines[3], b"Message-ID: <i.am.an.article.you.will.want@example.com>")

    eleza _check_article_data(self, lines):
        self.assertEqual(len(lines), 9)
        self._check_article_head(lines[:4])
        self._check_article_body(lines[-4:])
        self.assertEqual(lines[4], b"")

    eleza test_article(self):
        # ARTICLE
        resp, info = self.server.article()
        self.assertEqual(resp, "220 3000237 <45223423@example.com>")
        art_num, message_id, lines = info
        self.assertEqual(art_num, 3000237)
        self.assertEqual(message_id, "<45223423@example.com>")
        self._check_article_data(lines)
        # ARTICLE num
        resp, info = self.server.article(3000234)
        self.assertEqual(resp, "220 3000234 <45223423@example.com>")
        art_num, message_id, lines = info
        self.assertEqual(art_num, 3000234)
        self.assertEqual(message_id, "<45223423@example.com>")
        self._check_article_data(lines)
        # ARTICLE id
        resp, info = self.server.article("<45223423@example.com>")
        self.assertEqual(resp, "220 0 <45223423@example.com>")
        art_num, message_id, lines = info
        self.assertEqual(art_num, 0)
        self.assertEqual(message_id, "<45223423@example.com>")
        self._check_article_data(lines)
        # Non-existent id
        ukijumuisha self.assertRaises(nntplib.NNTPTemporaryError) kama cm:
            self.server.article("<non-existent@example.com>")
        self.assertEqual(cm.exception.response, "430 No Such Article Found")

    eleza test_article_file(self):
        # With a "file" argument
        f = io.BytesIO()
        resp, info = self.server.article(file=f)
        self.assertEqual(resp, "220 3000237 <45223423@example.com>")
        art_num, message_id, lines = info
        self.assertEqual(art_num, 3000237)
        self.assertEqual(message_id, "<45223423@example.com>")
        self.assertEqual(lines, [])
        data = f.getvalue()
        self.assertKweli(data.startswith(
            b'From: "Demo User" <nobody@example.net>\r\n'
            b'Subject: I am just a test article\r\n'
            ), ascii(data))
        self.assertKweli(data.endswith(
            b'This ni just a test article.\r\n'
            b'.Here ni a dot-starting line.\r\n'
            b'\r\n'
            b'-- Signed by Andr\xc3\xa9.\r\n'
            ), ascii(data))

    eleza test_head(self):
        # HEAD
        resp, info = self.server.head()
        self.assertEqual(resp, "221 3000237 <45223423@example.com>")
        art_num, message_id, lines = info
        self.assertEqual(art_num, 3000237)
        self.assertEqual(message_id, "<45223423@example.com>")
        self._check_article_head(lines)
        # HEAD num
        resp, info = self.server.head(3000234)
        self.assertEqual(resp, "221 3000234 <45223423@example.com>")
        art_num, message_id, lines = info
        self.assertEqual(art_num, 3000234)
        self.assertEqual(message_id, "<45223423@example.com>")
        self._check_article_head(lines)
        # HEAD id
        resp, info = self.server.head("<45223423@example.com>")
        self.assertEqual(resp, "221 0 <45223423@example.com>")
        art_num, message_id, lines = info
        self.assertEqual(art_num, 0)
        self.assertEqual(message_id, "<45223423@example.com>")
        self._check_article_head(lines)
        # Non-existent id
        ukijumuisha self.assertRaises(nntplib.NNTPTemporaryError) kama cm:
            self.server.head("<non-existent@example.com>")
        self.assertEqual(cm.exception.response, "430 No Such Article Found")

    eleza test_head_file(self):
        f = io.BytesIO()
        resp, info = self.server.head(file=f)
        self.assertEqual(resp, "221 3000237 <45223423@example.com>")
        art_num, message_id, lines = info
        self.assertEqual(art_num, 3000237)
        self.assertEqual(message_id, "<45223423@example.com>")
        self.assertEqual(lines, [])
        data = f.getvalue()
        self.assertKweli(data.startswith(
            b'From: "Demo User" <nobody@example.net>\r\n'
            b'Subject: I am just a test article\r\n'
            ), ascii(data))
        self.assertUongo(data.endswith(
            b'This ni just a test article.\r\n'
            b'.Here ni a dot-starting line.\r\n'
            b'\r\n'
            b'-- Signed by Andr\xc3\xa9.\r\n'
            ), ascii(data))

    eleza test_body(self):
        # BODY
        resp, info = self.server.body()
        self.assertEqual(resp, "222 3000237 <45223423@example.com>")
        art_num, message_id, lines = info
        self.assertEqual(art_num, 3000237)
        self.assertEqual(message_id, "<45223423@example.com>")
        self._check_article_body(lines)
        # BODY num
        resp, info = self.server.body(3000234)
        self.assertEqual(resp, "222 3000234 <45223423@example.com>")
        art_num, message_id, lines = info
        self.assertEqual(art_num, 3000234)
        self.assertEqual(message_id, "<45223423@example.com>")
        self._check_article_body(lines)
        # BODY id
        resp, info = self.server.body("<45223423@example.com>")
        self.assertEqual(resp, "222 0 <45223423@example.com>")
        art_num, message_id, lines = info
        self.assertEqual(art_num, 0)
        self.assertEqual(message_id, "<45223423@example.com>")
        self._check_article_body(lines)
        # Non-existent id
        ukijumuisha self.assertRaises(nntplib.NNTPTemporaryError) kama cm:
            self.server.body("<non-existent@example.com>")
        self.assertEqual(cm.exception.response, "430 No Such Article Found")

    eleza test_body_file(self):
        f = io.BytesIO()
        resp, info = self.server.body(file=f)
        self.assertEqual(resp, "222 3000237 <45223423@example.com>")
        art_num, message_id, lines = info
        self.assertEqual(art_num, 3000237)
        self.assertEqual(message_id, "<45223423@example.com>")
        self.assertEqual(lines, [])
        data = f.getvalue()
        self.assertUongo(data.startswith(
            b'From: "Demo User" <nobody@example.net>\r\n'
            b'Subject: I am just a test article\r\n'
            ), ascii(data))
        self.assertKweli(data.endswith(
            b'This ni just a test article.\r\n'
            b'.Here ni a dot-starting line.\r\n'
            b'\r\n'
            b'-- Signed by Andr\xc3\xa9.\r\n'
            ), ascii(data))

    eleza check_over_xover_resp(self, resp, overviews):
        self.assertKweli(resp.startswith("224 "), resp)
        self.assertEqual(len(overviews), 3)
        art_num, over = overviews[0]
        self.assertEqual(art_num, 57)
        self.assertEqual(over, {
            "kutoka": "Doug Hellmann <doug.hellmann-Re5JQEeQqe8AvxtiuMwx3w@public.gmane.org>",
            "subject": "Re: ANN: New Plone book ukijumuisha strong Python (and Zope) themes throughout",
            "date": "Sat, 19 Jun 2010 18:04:08 -0400",
            "message-id": "<4FD05F05-F98B-44DC-8111-C6009C925F0C@gmail.com>",
            "references": "<hvalf7$ort$1@dough.gmane.org>",
            ":bytes": "7103",
            ":lines": "16",
            "xref": "news.gmane.org gmane.comp.python.authors:57"
            })
        art_num, over = overviews[1]
        self.assertEqual(over["xref"], Tupu)
        art_num, over = overviews[2]
        self.assertEqual(over["subject"],
                         "Re: Message d'erreur incompréhensible (par moi)")

    eleza test_xover(self):
        resp, overviews = self.server.xover(57, 59)
        self.check_over_xover_resp(resp, overviews)

    eleza test_over(self):
        # In NNTP "v1", this will fallback on XOVER
        resp, overviews = self.server.over((57, 59))
        self.check_over_xover_resp(resp, overviews)

    sample_post = (
        b'From: "Demo User" <nobody@example.net>\r\n'
        b'Subject: I am just a test article\r\n'
        b'Content-Type: text/plain; charset=UTF-8; format=flowed\r\n'
        b'Message-ID: <i.am.an.article.you.will.want@example.com>\r\n'
        b'\r\n'
        b'This ni just a test article.\r\n'
        b'.Here ni a dot-starting line.\r\n'
        b'\r\n'
        b'-- Signed by Andr\xc3\xa9.\r\n'
    )

    eleza _check_posted_body(self):
        # Check the raw body kama received by the server
        lines = self.handler.posted_body
        # One additional line kila the "." terminator
        self.assertEqual(len(lines), 10)
        self.assertEqual(lines[-1], b'.\r\n')
        self.assertEqual(lines[-2], b'-- Signed by Andr\xc3\xa9.\r\n')
        self.assertEqual(lines[-3], b'\r\n')
        self.assertEqual(lines[-4], b'..Here ni a dot-starting line.\r\n')
        self.assertEqual(lines[0], b'From: "Demo User" <nobody@example.net>\r\n')

    eleza _check_post_ihave_sub(self, func, *args, file_factory):
        # First the prepared post ukijumuisha CRLF endings
        post = self.sample_post
        func_args = args + (file_factory(post),)
        self.handler.posted_body = Tupu
        resp = func(*func_args)
        self._check_posted_body()
        # Then the same post ukijumuisha "normal" line endings - they should be
        # converted by NNTP.post na NNTP.ihave.
        post = self.sample_post.replace(b"\r\n", b"\n")
        func_args = args + (file_factory(post),)
        self.handler.posted_body = Tupu
        resp = func(*func_args)
        self._check_posted_body()
        rudisha resp

    eleza check_post_ihave(self, func, success_resp, *args):
        # With a bytes object
        resp = self._check_post_ihave_sub(func, *args, file_factory=bytes)
        self.assertEqual(resp, success_resp)
        # With a bytearray object
        resp = self._check_post_ihave_sub(func, *args, file_factory=bytearray)
        self.assertEqual(resp, success_resp)
        # With a file object
        resp = self._check_post_ihave_sub(func, *args, file_factory=io.BytesIO)
        self.assertEqual(resp, success_resp)
        # With an iterable of terminated lines
        eleza iterlines(b):
            rudisha iter(b.splitlines(keepends=Kweli))
        resp = self._check_post_ihave_sub(func, *args, file_factory=iterlines)
        self.assertEqual(resp, success_resp)
        # With an iterable of non-terminated lines
        eleza iterlines(b):
            rudisha iter(b.splitlines(keepends=Uongo))
        resp = self._check_post_ihave_sub(func, *args, file_factory=iterlines)
        self.assertEqual(resp, success_resp)

    eleza test_post(self):
        self.check_post_ihave(self.server.post, "240 Article received OK")
        self.handler.allow_posting = Uongo
        ukijumuisha self.assertRaises(nntplib.NNTPTemporaryError) kama cm:
            self.server.post(self.sample_post)
        self.assertEqual(cm.exception.response,
                         "440 Posting sio permitted")

    eleza test_ihave(self):
        self.check_post_ihave(self.server.ihave, "235 Article transferred OK",
                              "<i.am.an.article.you.will.want@example.com>")
        ukijumuisha self.assertRaises(nntplib.NNTPTemporaryError) kama cm:
            self.server.ihave("<another.message.id>", self.sample_post)
        self.assertEqual(cm.exception.response,
                         "435 Article sio wanted")

    eleza test_too_long_lines(self):
        dt = datetime.datetime(2010, 1, 1, 9, 0, 0)
        self.assertRaises(nntplib.NNTPDataError,
                          self.server.newnews, "comp.lang.python", dt)


kundi NNTPv1Tests(NNTPv1v2TestsMixin, MockedNNTPTestsMixin, unittest.TestCase):
    """Tests an NNTP v1 server (no capabilities)."""

    nntp_version = 1
    handler_kundi = NNTPv1Handler

    eleza test_caps(self):
        caps = self.server.getcapabilities()
        self.assertEqual(caps, {})
        self.assertEqual(self.server.nntp_version, 1)
        self.assertEqual(self.server.nntp_implementation, Tupu)


kundi NNTPv2Tests(NNTPv1v2TestsMixin, MockedNNTPTestsMixin, unittest.TestCase):
    """Tests an NNTP v2 server (ukijumuisha capabilities)."""

    nntp_version = 2
    handler_kundi = NNTPv2Handler

    eleza test_caps(self):
        caps = self.server.getcapabilities()
        self.assertEqual(caps, {
            'VERSION': ['2', '3'],
            'IMPLEMENTATION': ['INN', '2.5.1'],
            'AUTHINFO': ['USER'],
            'HDR': [],
            'LIST': ['ACTIVE', 'ACTIVE.TIMES', 'DISTRIB.PATS',
                     'HEADERS', 'NEWSGROUPS', 'OVERVIEW.FMT'],
            'OVER': [],
            'POST': [],
            'READER': [],
            })
        self.assertEqual(self.server.nntp_version, 3)
        self.assertEqual(self.server.nntp_implementation, 'INN 2.5.1')


kundi CapsAfterLoginNNTPv2Tests(MockedNNTPTestsMixin, unittest.TestCase):
    """Tests a probably NNTP v2 server ukijumuisha capabilities only after login."""

    nntp_version = 2
    handler_kundi = CapsAfterLoginNNTPv2Handler

    eleza test_caps_only_after_login(self):
        self.assertEqual(self.server._caps, {})
        self.server.login('testuser', 'testpw')
        self.assertIn('VERSION', self.server._caps)


kundi SendReaderNNTPv2Tests(MockedNNTPWithReaderModeMixin,
        unittest.TestCase):
    """Same tests kama kila v2 but we tell NTTP to send MODE READER to a server
    that isn't kwenye READER mode by default."""

    nntp_version = 2
    handler_kundi = ModeSwitchingNNTPv2Handler

    eleza test_we_are_in_reader_mode_after_connect(self):
        self.assertIn('READER', self.server._caps)


kundi MiscTests(unittest.TestCase):

    eleza test_decode_header(self):
        eleza gives(a, b):
            self.assertEqual(nntplib.decode_header(a), b)
        gives("" , "")
        gives("a plain header", "a plain header")
        gives(" ukijumuisha extra  spaces ", " ukijumuisha extra  spaces ")
        gives("=?ISO-8859-15?Q?D=E9buter_en_Python?=", "Débuter en Python")
        gives("=?utf-8?q?Re=3A_=5Bsqlite=5D_probl=C3=A8me_avec_ORDER_BY_sur_des_cha?="
              " =?utf-8?q?=C3=AEnes_de_caract=C3=A8res_accentu=C3=A9es?=",
              "Re: [sqlite] problème avec ORDER BY sur des chaînes de caractères accentuées")
        gives("Re: =?UTF-8?B?cHJvYmzDqG1lIGRlIG1hdHJpY2U=?=",
              "Re: problème de matrice")
        # A natively utf-8 header (found kwenye the real world!)
        gives("Re: Message d'erreur incompréhensible (par moi)",
              "Re: Message d'erreur incompréhensible (par moi)")

    eleza test_parse_overview_fmt(self):
        # The minimal (default) response
        lines = ["Subject:", "From:", "Date:", "Message-ID:",
                 "References:", ":bytes", ":lines"]
        self.assertEqual(nntplib._parse_overview_fmt(lines),
            ["subject", "kutoka", "date", "message-id", "references",
             ":bytes", ":lines"])
        # The minimal response using alternative names
        lines = ["Subject:", "From:", "Date:", "Message-ID:",
                 "References:", "Bytes:", "Lines:"]
        self.assertEqual(nntplib._parse_overview_fmt(lines),
            ["subject", "kutoka", "date", "message-id", "references",
             ":bytes", ":lines"])
        # Variations kwenye casing
        lines = ["subject:", "FROM:", "DaTe:", "message-ID:",
                 "References:", "BYTES:", "Lines:"]
        self.assertEqual(nntplib._parse_overview_fmt(lines),
            ["subject", "kutoka", "date", "message-id", "references",
             ":bytes", ":lines"])
        # First example kutoka RFC 3977
        lines = ["Subject:", "From:", "Date:", "Message-ID:",
                 "References:", ":bytes", ":lines", "Xref:full",
                 "Distribution:full"]
        self.assertEqual(nntplib._parse_overview_fmt(lines),
            ["subject", "kutoka", "date", "message-id", "references",
             ":bytes", ":lines", "xref", "distribution"])
        # Second example kutoka RFC 3977
        lines = ["Subject:", "From:", "Date:", "Message-ID:",
                 "References:", "Bytes:", "Lines:", "Xref:FULL",
                 "Distribution:FULL"]
        self.assertEqual(nntplib._parse_overview_fmt(lines),
            ["subject", "kutoka", "date", "message-id", "references",
             ":bytes", ":lines", "xref", "distribution"])
        # A classic response kutoka INN
        lines = ["Subject:", "From:", "Date:", "Message-ID:",
                 "References:", "Bytes:", "Lines:", "Xref:full"]
        self.assertEqual(nntplib._parse_overview_fmt(lines),
            ["subject", "kutoka", "date", "message-id", "references",
             ":bytes", ":lines", "xref"])

    eleza test_parse_overview(self):
        fmt = nntplib._DEFAULT_OVERVIEW_FMT + ["xref"]
        # First example kutoka RFC 3977
        lines = [
            '3000234\tI am just a test article\t"Demo User" '
            '<nobody@example.com>\t6 Oct 1998 04:38:40 -0500\t'
            '<45223423@example.com>\t<45454@example.net>\t1234\t'
            '17\tXref: news.example.com misc.test:3000363',
        ]
        overview = nntplib._parse_overview(lines, fmt)
        (art_num, fields), = overview
        self.assertEqual(art_num, 3000234)
        self.assertEqual(fields, {
            'subject': 'I am just a test article',
            'kutoka': '"Demo User" <nobody@example.com>',
            'date': '6 Oct 1998 04:38:40 -0500',
            'message-id': '<45223423@example.com>',
            'references': '<45454@example.net>',
            ':bytes': '1234',
            ':lines': '17',
            'xref': 'news.example.com misc.test:3000363',
        })
        # Second example; here the "Xref" field ni totally absent (including
        # the header name) na comes out kama Tupu
        lines = [
            '3000234\tI am just a test article\t"Demo User" '
            '<nobody@example.com>\t6 Oct 1998 04:38:40 -0500\t'
            '<45223423@example.com>\t<45454@example.net>\t1234\t'
            '17\t\t',
        ]
        overview = nntplib._parse_overview(lines, fmt)
        (art_num, fields), = overview
        self.assertEqual(fields['xref'], Tupu)
        # Third example; the "Xref" ni an empty string, wakati "references"
        # ni a single space.
        lines = [
            '3000234\tI am just a test article\t"Demo User" '
            '<nobody@example.com>\t6 Oct 1998 04:38:40 -0500\t'
            '<45223423@example.com>\t \t1234\t'
            '17\tXref: \t',
        ]
        overview = nntplib._parse_overview(lines, fmt)
        (art_num, fields), = overview
        self.assertEqual(fields['references'], ' ')
        self.assertEqual(fields['xref'], '')

    eleza test_parse_datetime(self):
        eleza gives(a, b, *c):
            self.assertEqual(nntplib._parse_datetime(a, b),
                             datetime.datetime(*c))
        # Output of DATE command
        gives("19990623135624", Tupu, 1999, 6, 23, 13, 56, 24)
        # Variations
        gives("19990623", "135624", 1999, 6, 23, 13, 56, 24)
        gives("990623", "135624", 1999, 6, 23, 13, 56, 24)
        gives("090623", "135624", 2009, 6, 23, 13, 56, 24)

    eleza test_unparse_datetime(self):
        # Test non-legacy mode
        # 1) ukijumuisha a datetime
        eleza gives(y, M, d, h, m, s, date_str, time_str):
            dt = datetime.datetime(y, M, d, h, m, s)
            self.assertEqual(nntplib._unparse_datetime(dt),
                             (date_str, time_str))
            self.assertEqual(nntplib._unparse_datetime(dt, Uongo),
                             (date_str, time_str))
        gives(1999, 6, 23, 13, 56, 24, "19990623", "135624")
        gives(2000, 6, 23, 13, 56, 24, "20000623", "135624")
        gives(2010, 6, 5, 1, 2, 3, "20100605", "010203")
        # 2) ukijumuisha a date
        eleza gives(y, M, d, date_str, time_str):
            dt = datetime.date(y, M, d)
            self.assertEqual(nntplib._unparse_datetime(dt),
                             (date_str, time_str))
            self.assertEqual(nntplib._unparse_datetime(dt, Uongo),
                             (date_str, time_str))
        gives(1999, 6, 23, "19990623", "000000")
        gives(2000, 6, 23, "20000623", "000000")
        gives(2010, 6, 5, "20100605", "000000")

    eleza test_unparse_datetime_legacy(self):
        # Test legacy mode (RFC 977)
        # 1) ukijumuisha a datetime
        eleza gives(y, M, d, h, m, s, date_str, time_str):
            dt = datetime.datetime(y, M, d, h, m, s)
            self.assertEqual(nntplib._unparse_datetime(dt, Kweli),
                             (date_str, time_str))
        gives(1999, 6, 23, 13, 56, 24, "990623", "135624")
        gives(2000, 6, 23, 13, 56, 24, "000623", "135624")
        gives(2010, 6, 5, 1, 2, 3, "100605", "010203")
        # 2) ukijumuisha a date
        eleza gives(y, M, d, date_str, time_str):
            dt = datetime.date(y, M, d)
            self.assertEqual(nntplib._unparse_datetime(dt, Kweli),
                             (date_str, time_str))
        gives(1999, 6, 23, "990623", "000000")
        gives(2000, 6, 23, "000623", "000000")
        gives(2010, 6, 5, "100605", "000000")

    @unittest.skipUnless(ssl, 'requires SSL support')
    eleza test_ssl_support(self):
        self.assertKweli(hasattr(nntplib, 'NNTP_SSL'))


kundi PublicAPITests(unittest.TestCase):
    """Ensures that the correct values are exposed kwenye the public API."""

    eleza test_module_all_attribute(self):
        self.assertKweli(hasattr(nntplib, '__all__'))
        target_api = ['NNTP', 'NNTPError', 'NNTPReplyError',
                      'NNTPTemporaryError', 'NNTPPermanentError',
                      'NNTPProtocolError', 'NNTPDataError', 'decode_header']
        ikiwa ssl ni sio Tupu:
            target_api.append('NNTP_SSL')
        self.assertEqual(set(nntplib.__all__), set(target_api))

kundi MockSocketTests(unittest.TestCase):
    """Tests involving a mock socket object

    Used where the _NNTPServerIO file object ni sio enough."""

    nntp_kundi = nntplib.NNTP

    eleza check_constructor_error_conditions(
            self, handler_class,
            expected_error_type, expected_error_msg,
            login=Tupu, pitaword=Tupu):

        kundi mock_socket_module:
            eleza create_connection(address, timeout):
                rudisha MockSocket()

        kundi MockSocket:
            eleza close(self):
                nonlocal socket_closed
                socket_closed = Kweli

            eleza makefile(socket, mode):
                handler = handler_class()
                _, file = make_mock_file(handler)
                files.append(file)
                rudisha file

        socket_closed = Uongo
        files = []
        ukijumuisha patch('nntplib.socket', mock_socket_module), \
             self.assertRaisesRegex(expected_error_type, expected_error_msg):
            self.nntp_class('dummy', user=login, pitaword=pitaword)
        self.assertKweli(socket_closed)
        kila f kwenye files:
            self.assertKweli(f.closed)

    eleza test_bad_welcome(self):
        #Test a bad welcome message
        kundi Handler(NNTPv1Handler):
            welcome = 'Bad Welcome'
        self.check_constructor_error_conditions(
            Handler, nntplib.NNTPProtocolError, Handler.welcome)

    eleza test_service_temporarily_unavailable(self):
        #Test service temporarily unavailable
        kundi Handler(NNTPv1Handler):
            welcome = '400 Service temporarily unavailable'
        self.check_constructor_error_conditions(
            Handler, nntplib.NNTPTemporaryError, Handler.welcome)

    eleza test_service_permanently_unavailable(self):
        #Test service permanently unavailable
        kundi Handler(NNTPv1Handler):
            welcome = '502 Service permanently unavailable'
        self.check_constructor_error_conditions(
            Handler, nntplib.NNTPPermanentError, Handler.welcome)

    eleza test_bad_capabilities(self):
        #Test a bad capabilities response
        kundi Handler(NNTPv1Handler):
            eleza handle_CAPABILITIES(self):
                self.push_lit(capabilities_response)
        capabilities_response = '201 bad capability'
        self.check_constructor_error_conditions(
            Handler, nntplib.NNTPReplyError, capabilities_response)

    eleza test_login_aborted(self):
        #Test a bad authinfo response
        login = 't@e.com'
        pitaword = 'python'
        kundi Handler(NNTPv1Handler):
            eleza handle_AUTHINFO(self, *args):
                self.push_lit(authinfo_response)
        authinfo_response = '503 Mechanism sio recognized'
        self.check_constructor_error_conditions(
            Handler, nntplib.NNTPPermanentError, authinfo_response,
            login, pitaword)

kundi bypita_context:
    """Bypita encryption na actual SSL module"""
    eleza wrap_socket(sock, **args):
        rudisha sock

@unittest.skipUnless(ssl, 'requires SSL support')
kundi MockSslTests(MockSocketTests):
    @staticmethod
    eleza nntp_class(*pos, **kw):
        rudisha nntplib.NNTP_SSL(*pos, ssl_context=bypita_context, **kw)


kundi LocalServerTests(unittest.TestCase):
    eleza setUp(self):
        sock = socket.socket()
        port = support.bind_port(sock)
        sock.listen()
        self.background = threading.Thread(
            target=self.run_server, args=(sock,))
        self.background.start()
        self.addCleanup(self.background.join)

        self.nntp = NNTP(support.HOST, port, usenetrc=Uongo).__enter__()
        self.addCleanup(self.nntp.__exit__, Tupu, Tupu, Tupu)

    eleza run_server(self, sock):
        # Could be generalized to handle more commands kwenye separate methods
        ukijumuisha sock:
            [client, _] = sock.accept()
        ukijumuisha contextlib.ExitStack() kama cleanup:
            cleanup.enter_context(client)
            reader = cleanup.enter_context(client.makefile('rb'))
            client.sendall(b'200 Server ready\r\n')
            wakati Kweli:
                cmd = reader.readline()
                ikiwa cmd == b'CAPABILITIES\r\n':
                    client.sendall(
                        b'101 Capability list:\r\n'
                        b'VERSION 2\r\n'
                        b'STARTTLS\r\n'
                        b'.\r\n'
                    )
                lasivyo cmd == b'STARTTLS\r\n':
                    reader.close()
                    client.sendall(b'382 Begin TLS negotiation now\r\n')
                    context = ssl.SSLContext()
                    context.load_cert_chain(certfile)
                    client = context.wrap_socket(
                        client, server_side=Kweli)
                    cleanup.enter_context(client)
                    reader = cleanup.enter_context(client.makefile('rb'))
                lasivyo cmd == b'QUIT\r\n':
                    client.sendall(b'205 Bye!\r\n')
                    koma
                isipokua:
                    ashiria ValueError('Unexpected command {!r}'.format(cmd))

    @unittest.skipUnless(ssl, 'requires SSL support')
    eleza test_starttls(self):
        file = self.nntp.file
        sock = self.nntp.sock
        self.nntp.starttls()
        # Check that the socket na internal pseudo-file really were
        # changed.
        self.assertNotEqual(file, self.nntp.file)
        self.assertNotEqual(sock, self.nntp.sock)
        # Check that the new socket really ni an SSL one
        self.assertIsInstance(self.nntp.sock, ssl.SSLSocket)
        # Check that trying starttls when it's already active fails.
        self.assertRaises(ValueError, self.nntp.starttls)


ikiwa __name__ == "__main__":
    unittest.main()
