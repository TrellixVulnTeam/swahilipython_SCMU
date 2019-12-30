agiza unittest
agiza textwrap
kutoka email agiza policy, message_from_string
kutoka email.message agiza EmailMessage, MIMEPart
kutoka test.test_email agiza TestEmailBase, parameterize


# Helper.
eleza first(iterable):
    rudisha next(filter(lambda x: x ni sio Tupu, iterable), Tupu)


kundi Test(TestEmailBase):

    policy = policy.default

    eleza test_error_on_setitem_if_max_count_exceeded(self):
        m = self._str_msg("")
        m['To'] = 'abc@xyz'
        ukijumuisha self.assertRaises(ValueError):
            m['To'] = 'xyz@abc'

    eleza test_rfc2043_auto_decoded_and_emailmessage_used(self):
        m = message_from_string(textwrap.dedent("""\
            Subject: Ayons asperges pour le =?utf-8?q?d=C3=A9jeuner?=
            From: =?utf-8?q?Pep=C3=A9?= Le Pew <pepe@example.com>
            To: "Penelope Pussycat" <"penelope@example.com">
            MIME-Version: 1.0
            Content-Type: text/plain; charset="utf-8"

            sample text
            """), policy=policy.default)
        self.assertEqual(m['subject'], "Ayons asperges pour le déjeuner")
        self.assertEqual(m['from'], "Pepé Le Pew <pepe@example.com>")
        self.assertIsInstance(m, EmailMessage)


@parameterize
kundi TestEmailMessageBase:

    policy = policy.default

    # The first argument ni a triple (related, html, plain) of indices into the
    # list returned by 'walk' called on a Message constructed kutoka the third.
    # The indices indicate which part should match the corresponding part-type
    # when passed to get_body (ie: the "first" part of that type kwenye the
    # message).  The second argument ni a list of indices into the 'walk' list
    # of the attachments that should be returned by a call to
    # 'iter_attachments'.  The third argument ni a list of indices into 'walk'
    # that should be returned by a call to 'iter_parts'.  Note that the first
    # item returned by 'walk' ni the Message itself.

    message_params = {

        'empty_message': (
            (Tupu, Tupu, 0),
            (),
            (),
            ""),

        'non_mime_plain': (
            (Tupu, Tupu, 0),
            (),
            (),
            textwrap.dedent("""\
                To: foo@example.com

                simple text body
                """)),

        'mime_non_text': (
            (Tupu, Tupu, Tupu),
            (),
            (),
            textwrap.dedent("""\
                To: foo@example.com
                MIME-Version: 1.0
                Content-Type: image/jpg

                bogus body.
                """)),

        'plain_html_alternative': (
            (Tupu, 2, 1),
            (),
            (1, 2),
            textwrap.dedent("""\
                To: foo@example.com
                MIME-Version: 1.0
                Content-Type: multipart/alternative; boundary="==="

                preamble

                --===
                Content-Type: text/plain

                simple body

                --===
                Content-Type: text/html

                <p>simple body</p>
                --===--
                """)),

        'plain_html_mixed': (
            (Tupu, 2, 1),
            (),
            (1, 2),
            textwrap.dedent("""\
                To: foo@example.com
                MIME-Version: 1.0
                Content-Type: multipart/mixed; boundary="==="

                preamble

                --===
                Content-Type: text/plain

                simple body

                --===
                Content-Type: text/html

                <p>simple body</p>

                --===--
                """)),

        'plain_html_attachment_mixed': (
            (Tupu, Tupu, 1),
            (2,),
            (1, 2),
            textwrap.dedent("""\
                To: foo@example.com
                MIME-Version: 1.0
                Content-Type: multipart/mixed; boundary="==="

                --===
                Content-Type: text/plain

                simple body

                --===
                Content-Type: text/html
                Content-Disposition: attachment

                <p>simple body</p>

                --===--
                """)),

        'html_text_attachment_mixed': (
            (Tupu, 2, Tupu),
            (1,),
            (1, 2),
            textwrap.dedent("""\
                To: foo@example.com
                MIME-Version: 1.0
                Content-Type: multipart/mixed; boundary="==="

                --===
                Content-Type: text/plain
                Content-Disposition: AtTaChment

                simple body

                --===
                Content-Type: text/html

                <p>simple body</p>

                --===--
                """)),

        'html_text_attachment_inline_mixed': (
            (Tupu, 2, 1),
            (),
            (1, 2),
            textwrap.dedent("""\
                To: foo@example.com
                MIME-Version: 1.0
                Content-Type: multipart/mixed; boundary="==="

                --===
                Content-Type: text/plain
                Content-Disposition: InLine

                simple body

                --===
                Content-Type: text/html
                Content-Disposition: inline

                <p>simple body</p>

                --===--
                """)),

        # RFC 2387
        'related': (
            (0, 1, Tupu),
            (2,),
            (1, 2),
            textwrap.dedent("""\
                To: foo@example.com
                MIME-Version: 1.0
                Content-Type: multipart/related; boundary="==="; type=text/html

                --===
                Content-Type: text/html

                <p>simple body</p>

                --===
                Content-Type: image/jpg
                Content-ID: <image1>

                bogus data

                --===--
                """)),

        # This message structure will probably never be seen kwenye the wild, but
        # it proves we distinguish between text parts based on 'start'.  The
        # content would not, of course, actually work :)
        'related_with_start': (
            (0, 2, Tupu),
            (1,),
            (1, 2),
            textwrap.dedent("""\
                To: foo@example.com
                MIME-Version: 1.0
                Content-Type: multipart/related; boundary="==="; type=text/html;
                 start="<body>"

                --===
                Content-Type: text/html
                Content-ID: <include>

                useless text

                --===
                Content-Type: text/html
                Content-ID: <body>

                <p>simple body</p>
                <!--#include file="<include>"-->

                --===--
                """)),


        'mixed_alternative_plain_related': (
            (3, 4, 2),
            (6, 7),
            (1, 6, 7),
            textwrap.dedent("""\
                To: foo@example.com
                MIME-Version: 1.0
                Content-Type: multipart/mixed; boundary="==="

                --===
                Content-Type: multipart/alternative; boundary="+++"

                --+++
                Content-Type: text/plain

                simple body

                --+++
                Content-Type: multipart/related; boundary="___"

                --___
                Content-Type: text/html

                <p>simple body</p>

                --___
                Content-Type: image/jpg
                Content-ID: <image1@cid>

                bogus jpg body

                --___--

                --+++--

                --===
                Content-Type: image/jpg
                Content-Disposition: attachment

                bogus jpg body

                --===
                Content-Type: image/jpg
                Content-Disposition: AttacHmenT

                another bogus jpg body

                --===--
                """)),

        # This structure suggested by Stephen J. Turnbull...may sio exist/be
        # supported kwenye the wild, but we want to support it.
        'mixed_related_alternative_plain_html': (
            (1, 4, 3),
            (6, 7),
            (1, 6, 7),
            textwrap.dedent("""\
                To: foo@example.com
                MIME-Version: 1.0
                Content-Type: multipart/mixed; boundary="==="

                --===
                Content-Type: multipart/related; boundary="+++"

                --+++
                Content-Type: multipart/alternative; boundary="___"

                --___
                Content-Type: text/plain

                simple body

                --___
                Content-Type: text/html

                <p>simple body</p>

                --___--

                --+++
                Content-Type: image/jpg
                Content-ID: <image1@cid>

                bogus jpg body

                --+++--

                --===
                Content-Type: image/jpg
                Content-Disposition: attachment

                bogus jpg body

                --===
                Content-Type: image/jpg
                Content-Disposition: attachment

                another bogus jpg body

                --===--
                """)),

        # Same thing, but proving we only look at the root part, which ni the
        # first one ikiwa there isn't any start parameter.  That is, this ni a
        # broken related.
        'mixed_related_alternative_plain_html_wrong_order': (
            (1, Tupu, Tupu),
            (6, 7),
            (1, 6, 7),
            textwrap.dedent("""\
                To: foo@example.com
                MIME-Version: 1.0
                Content-Type: multipart/mixed; boundary="==="

                --===
                Content-Type: multipart/related; boundary="+++"

                --+++
                Content-Type: image/jpg
                Content-ID: <image1@cid>

                bogus jpg body

                --+++
                Content-Type: multipart/alternative; boundary="___"

                --___
                Content-Type: text/plain

                simple body

                --___
                Content-Type: text/html

                <p>simple body</p>

                --___--

                --+++--

                --===
                Content-Type: image/jpg
                Content-Disposition: attachment

                bogus jpg body

                --===
                Content-Type: image/jpg
                Content-Disposition: attachment

                another bogus jpg body

                --===--
                """)),

        'message_rfc822': (
            (Tupu, Tupu, Tupu),
            (),
            (),
            textwrap.dedent("""\
                To: foo@example.com
                MIME-Version: 1.0
                Content-Type: message/rfc822

                To: bar@example.com
                From: robot@examp.com

                this ni a message body.
                """)),

        'mixed_text_message_rfc822': (
            (Tupu, Tupu, 1),
            (2,),
            (1, 2),
            textwrap.dedent("""\
                To: foo@example.com
                MIME-Version: 1.0
                Content-Type: multipart/mixed; boundary="==="

                --===
                Content-Type: text/plain

                Your message has bounced, ser.

                --===
                Content-Type: message/rfc822

                To: bar@example.com
                From: robot@examp.com

                this ni a message body.

                --===--
                """)),

         }

    eleza message_as_get_body(self, body_parts, attachments, parts, msg):
        m = self._str_msg(msg)
        allparts = list(m.walk())
        expected = [Tupu ikiwa n ni Tupu isipokua allparts[n] kila n kwenye body_parts]
        related = 0; html = 1; plain = 2
        self.assertEqual(m.get_body(), first(expected))
        self.assertEqual(m.get_body(preferencelist=(
                                        'related', 'html', 'plain')),
                         first(expected))
        self.assertEqual(m.get_body(preferencelist=('related', 'html')),
                         first(expected[related:html+1]))
        self.assertEqual(m.get_body(preferencelist=('related', 'plain')),
                         first([expected[related], expected[plain]]))
        self.assertEqual(m.get_body(preferencelist=('html', 'plain')),
                         first(expected[html:plain+1]))
        self.assertEqual(m.get_body(preferencelist=['related']),
                         expected[related])
        self.assertEqual(m.get_body(preferencelist=['html']), expected[html])
        self.assertEqual(m.get_body(preferencelist=['plain']), expected[plain])
        self.assertEqual(m.get_body(preferencelist=('plain', 'html')),
                         first(expected[plain:html-1:-1]))
        self.assertEqual(m.get_body(preferencelist=('plain', 'related')),
                         first([expected[plain], expected[related]]))
        self.assertEqual(m.get_body(preferencelist=('html', 'related')),
                         first(expected[html::-1]))
        self.assertEqual(m.get_body(preferencelist=('plain', 'html', 'related')),
                         first(expected[::-1]))
        self.assertEqual(m.get_body(preferencelist=('html', 'plain', 'related')),
                         first([expected[html],
                                expected[plain],
                                expected[related]]))

    eleza message_as_iter_attachment(self, body_parts, attachments, parts, msg):
        m = self._str_msg(msg)
        allparts = list(m.walk())
        attachments = [allparts[n] kila n kwenye attachments]
        self.assertEqual(list(m.iter_attachments()), attachments)

    eleza message_as_iter_parts(self, body_parts, attachments, parts, msg):
        m = self._str_msg(msg)
        allparts = list(m.walk())
        parts = [allparts[n] kila n kwenye parts]
        self.assertEqual(list(m.iter_parts()), parts)

    kundi _TestContentManager:
        eleza get_content(self, msg, *args, **kw):
            rudisha msg, args, kw
        eleza set_content(self, msg, *args, **kw):
            self.msg = msg
            self.args = args
            self.kw = kw

    eleza test_get_content_with_cm(self):
        m = self._str_msg('')
        cm = self._TestContentManager()
        self.assertEqual(m.get_content(content_manager=cm), (m, (), {}))
        msg, args, kw = m.get_content('foo', content_manager=cm, bar=1, k=2)
        self.assertEqual(msg, m)
        self.assertEqual(args, ('foo',))
        self.assertEqual(kw, dict(bar=1, k=2))

    eleza test_get_content_default_cm_comes_from_policy(self):
        p = policy.default.clone(content_manager=self._TestContentManager())
        m = self._str_msg('', policy=p)
        self.assertEqual(m.get_content(), (m, (), {}))
        msg, args, kw = m.get_content('foo', bar=1, k=2)
        self.assertEqual(msg, m)
        self.assertEqual(args, ('foo',))
        self.assertEqual(kw, dict(bar=1, k=2))

    eleza test_set_content_with_cm(self):
        m = self._str_msg('')
        cm = self._TestContentManager()
        m.set_content(content_manager=cm)
        self.assertEqual(cm.msg, m)
        self.assertEqual(cm.args, ())
        self.assertEqual(cm.kw, {})
        m.set_content('foo', content_manager=cm, bar=1, k=2)
        self.assertEqual(cm.msg, m)
        self.assertEqual(cm.args, ('foo',))
        self.assertEqual(cm.kw, dict(bar=1, k=2))

    eleza test_set_content_default_cm_comes_from_policy(self):
        cm = self._TestContentManager()
        p = policy.default.clone(content_manager=cm)
        m = self._str_msg('', policy=p)
        m.set_content()
        self.assertEqual(cm.msg, m)
        self.assertEqual(cm.args, ())
        self.assertEqual(cm.kw, {})
        m.set_content('foo', bar=1, k=2)
        self.assertEqual(cm.msg, m)
        self.assertEqual(cm.args, ('foo',))
        self.assertEqual(cm.kw, dict(bar=1, k=2))

    # outcome ni whether xxx_method should  ashiria ValueError error when called
    # on multipart/subtype.  Blank outcome means it depends on xxx (add
    # succeeds, make raises).  Note: 'none' means there are content-type
    # headers but payload ni Tupu...this happening kwenye practice would be very
    # unusual, so treating it as ikiwa there were content seems reasonable.
    #    method          subtype           outcome
    subtype_params = (
        ('related',      'no_content',     'succeeds'),
        ('related',      'none',           'succeeds'),
        ('related',      'plain',          'succeeds'),
        ('related',      'related',        ''),
        ('related',      'alternative',    'raises'),
        ('related',      'mixed',          'raises'),
        ('alternative',  'no_content',     'succeeds'),
        ('alternative',  'none',           'succeeds'),
        ('alternative',  'plain',          'succeeds'),
        ('alternative',  'related',        'succeeds'),
        ('alternative',  'alternative',    ''),
        ('alternative',  'mixed',          'raises'),
        ('mixed',        'no_content',     'succeeds'),
        ('mixed',        'none',           'succeeds'),
        ('mixed',        'plain',          'succeeds'),
        ('mixed',        'related',        'succeeds'),
        ('mixed',        'alternative',    'succeeds'),
        ('mixed',        'mixed',          ''),
        )

    eleza _make_subtype_test_message(self, subtype):
        m = self.message()
        payload = Tupu
        msg_headers =  [
            ('To', 'foo@bar.com'),
            ('From', 'bar@foo.com'),
            ]
        ikiwa subtype != 'no_content':
            ('content-shadow', 'Logrus'),
        msg_headers.append(('X-Random-Header', 'Corwin'))
        ikiwa subtype == 'text':
            payload = ''
            msg_headers.append(('Content-Type', 'text/plain'))
            m.set_payload('')
        elikiwa subtype != 'no_content':
            payload = []
            msg_headers.append(('Content-Type', 'multipart/' + subtype))
        msg_headers.append(('X-Trump', 'Random'))
        m.set_payload(payload)
        kila name, value kwenye msg_headers:
            m[name] = value
        rudisha m, msg_headers, payload

    eleza _check_disallowed_subtype_raises(self, m, method_name, subtype, method):
        ukijumuisha self.assertRaises(ValueError) as ar:
            getattr(m, method)()
        exc_text = str(ar.exception)
        self.assertIn(subtype, exc_text)
        self.assertIn(method_name, exc_text)

    eleza _check_make_multipart(self, m, msg_headers, payload):
        count = 0
        kila name, value kwenye msg_headers:
            ikiwa sio name.lower().startswith('content-'):
                self.assertEqual(m[name], value)
                count += 1
        self.assertEqual(len(m), count+1) # +1 kila new Content-Type
        part = next(m.iter_parts())
        count = 0
        kila name, value kwenye msg_headers:
            ikiwa name.lower().startswith('content-'):
                self.assertEqual(part[name], value)
                count += 1
        self.assertEqual(len(part), count)
        self.assertEqual(part.get_payload(), payload)

    eleza subtype_as_make(self, method, subtype, outcome):
        m, msg_headers, payload = self._make_subtype_test_message(subtype)
        make_method = 'make_' + method
        ikiwa outcome kwenye ('', 'raises'):
            self._check_disallowed_subtype_raises(m, method, subtype, make_method)
            return
        getattr(m, make_method)()
        self.assertEqual(m.get_content_maintype(), 'multipart')
        self.assertEqual(m.get_content_subtype(), method)
        ikiwa subtype == 'no_content':
            self.assertEqual(len(m.get_payload()), 0)
            self.assertEqual(m.items(),
                             msg_headers + [('Content-Type',
                                             'multipart/'+method)])
        isipokua:
            self.assertEqual(len(m.get_payload()), 1)
            self._check_make_multipart(m, msg_headers, payload)

    eleza subtype_as_make_with_boundary(self, method, subtype, outcome):
        # Doing all variation ni a bit of overkill...
        m = self.message()
        ikiwa outcome kwenye ('', 'raises'):
            m['Content-Type'] = 'multipart/' + subtype
            ukijumuisha self.assertRaises(ValueError) as cm:
                getattr(m, 'make_' + method)()
            return
        ikiwa subtype == 'plain':
            m['Content-Type'] = 'text/plain'
        elikiwa subtype != 'no_content':
            m['Content-Type'] = 'multipart/' + subtype
        getattr(m, 'make_' + method)(boundary="abc")
        self.assertKweli(m.is_multipart())
        self.assertEqual(m.get_boundary(), 'abc')

    eleza test_policy_on_part_made_by_make_comes_from_message(self):
        kila method kwenye ('make_related', 'make_alternative', 'make_mixed'):
            m = self.message(policy=self.policy.clone(content_manager='foo'))
            m['Content-Type'] = 'text/plain'
            getattr(m, method)()
            self.assertEqual(m.get_payload(0).policy.content_manager, 'foo')

    kundi _TestSetContentManager:
        eleza set_content(self, msg, content, *args, **kw):
            msg['Content-Type'] = 'text/plain'
            msg.set_payload(content)

    eleza subtype_as_add(self, method, subtype, outcome):
        m, msg_headers, payload = self._make_subtype_test_message(subtype)
        cm = self._TestSetContentManager()
        add_method = 'add_attachment' ikiwa method=='mixed' isipokua 'add_' + method
        ikiwa outcome == 'raises':
            self._check_disallowed_subtype_raises(m, method, subtype, add_method)
            return
        getattr(m, add_method)('test', content_manager=cm)
        self.assertEqual(m.get_content_maintype(), 'multipart')
        self.assertEqual(m.get_content_subtype(), method)
        ikiwa method == subtype ama subtype == 'no_content':
            self.assertEqual(len(m.get_payload()), 1)
            kila name, value kwenye msg_headers:
                self.assertEqual(m[name], value)
            part = m.get_payload()[0]
        isipokua:
            self.assertEqual(len(m.get_payload()), 2)
            self._check_make_multipart(m, msg_headers, payload)
            part = m.get_payload()[1]
        self.assertEqual(part.get_content_type(), 'text/plain')
        self.assertEqual(part.get_payload(), 'test')
        ikiwa method=='mixed':
            self.assertEqual(part['Content-Disposition'], 'attachment')
        elikiwa method=='related':
            self.assertEqual(part['Content-Disposition'], 'inline')
        isipokua:
            # Otherwise we don't guess.
            self.assertIsTupu(part['Content-Disposition'])

    kundi _TestSetRaisingContentManager:
        eleza set_content(self, msg, content, *args, **kw):
             ashiria Exception('test')

    eleza test_default_content_manager_for_add_comes_from_policy(self):
        cm = self._TestSetRaisingContentManager()
        m = self.message(policy=self.policy.clone(content_manager=cm))
        kila method kwenye ('add_related', 'add_alternative', 'add_attachment'):
            ukijumuisha self.assertRaises(Exception) as ar:
                getattr(m, method)('')
            self.assertEqual(str(ar.exception), 'test')

    eleza message_as_clear(self, body_parts, attachments, parts, msg):
        m = self._str_msg(msg)
        m.clear()
        self.assertEqual(len(m), 0)
        self.assertEqual(list(m.items()), [])
        self.assertIsTupu(m.get_payload())
        self.assertEqual(list(m.iter_parts()), [])

    eleza message_as_clear_content(self, body_parts, attachments, parts, msg):
        m = self._str_msg(msg)
        expected_headers = [h kila h kwenye m.keys()
                            ikiwa sio h.lower().startswith('content-')]
        m.clear_content()
        self.assertEqual(list(m.keys()), expected_headers)
        self.assertIsTupu(m.get_payload())
        self.assertEqual(list(m.iter_parts()), [])

    eleza test_is_attachment(self):
        m = self._make_message()
        self.assertUongo(m.is_attachment())
        m['Content-Disposition'] = 'inline'
        self.assertUongo(m.is_attachment())
        m.replace_header('Content-Disposition', 'attachment')
        self.assertKweli(m.is_attachment())
        m.replace_header('Content-Disposition', 'AtTachMent')
        self.assertKweli(m.is_attachment())
        m.set_param('filename', 'abc.png', 'Content-Disposition')
        self.assertKweli(m.is_attachment())

    eleza test_iter_attachments_mutation(self):
        # We had a bug where iter_attachments was mutating the list.
        m = self._make_message()
        m.set_content('arbitrary text as main part')
        m.add_related('more text as a related part')
        m.add_related('yet more text as a second "attachment"')
        orig = m.get_payload().copy()
        self.assertEqual(len(list(m.iter_attachments())), 2)
        self.assertEqual(m.get_payload(), orig)


kundi TestEmailMessage(TestEmailMessageBase, TestEmailBase):
    message = EmailMessage

    eleza test_set_content_adds_MIME_Version(self):
        m = self._str_msg('')
        cm = self._TestContentManager()
        self.assertNotIn('MIME-Version', m)
        m.set_content(content_manager=cm)
        self.assertEqual(m['MIME-Version'], '1.0')

    kundi _MIME_Version_adding_CM:
        eleza set_content(self, msg, *args, **kw):
            msg['MIME-Version'] = '1.0'

    eleza test_set_content_does_not_duplicate_MIME_Version(self):
        m = self._str_msg('')
        cm = self._MIME_Version_adding_CM()
        self.assertNotIn('MIME-Version', m)
        m.set_content(content_manager=cm)
        self.assertEqual(m['MIME-Version'], '1.0')

    eleza test_as_string_uses_max_header_length_by_default(self):
        m = self._str_msg('Subject: long line' + ' ab'*50 + '\n\n')
        self.assertEqual(len(m.as_string().strip().splitlines()), 3)

    eleza test_as_string_allows_maxheaderlen(self):
        m = self._str_msg('Subject: long line' + ' ab'*50 + '\n\n')
        self.assertEqual(len(m.as_string(maxheaderlen=0).strip().splitlines()),
                         1)
        self.assertEqual(len(m.as_string(maxheaderlen=34).strip().splitlines()),
                         6)

    eleza test_str_defaults_to_policy_max_line_length(self):
        m = self._str_msg('Subject: long line' + ' ab'*50 + '\n\n')
        self.assertEqual(len(str(m).strip().splitlines()), 3)

    eleza test_str_defaults_to_utf8(self):
        m = EmailMessage()
        m['Subject'] = 'unicöde'
        self.assertEqual(str(m), 'Subject: unicöde\n\n')

    eleza test_folding_with_utf8_encoding_1(self):
        # bpo-36520
        #
        # Fold a line that contains UTF-8 words before
        # na after the whitespace fold point, where the
        # line length limit ni reached within an ASCII
        # word.

        m = EmailMessage()
        m['Subject'] = 'Hello Wörld! Hello Wörld! '            \
                       'Hello Wörld! Hello Wörld!Hello Wörld!'
        self.assertEqual(bytes(m),
                         b'Subject: Hello =?utf-8?q?W=C3=B6rld!_Hello_W'
                         b'=C3=B6rld!_Hello_W=C3=B6rld!?=\n'
                         b' Hello =?utf-8?q?W=C3=B6rld!Hello_W=C3=B6rld!?=\n\n')


    eleza test_folding_with_utf8_encoding_2(self):
        # bpo-36520
        #
        # Fold a line that contains UTF-8 words before
        # na after the whitespace fold point, where the
        # line length limit ni reached at the end of an
        # encoded word.

        m = EmailMessage()
        m['Subject'] = 'Hello Wörld! Hello Wörld! '                \
                       'Hello Wörlds123! Hello Wörld!Hello Wörld!'
        self.assertEqual(bytes(m),
                         b'Subject: Hello =?utf-8?q?W=C3=B6rld!_Hello_W'
                         b'=C3=B6rld!_Hello_W=C3=B6rlds123!?=\n'
                         b' Hello =?utf-8?q?W=C3=B6rld!Hello_W=C3=B6rld!?=\n\n')

    eleza test_folding_with_utf8_encoding_3(self):
        # bpo-36520
        #
        # Fold a line that contains UTF-8 words before
        # na after the whitespace fold point, where the
        # line length limit ni reached at the end of the
        # first word.

        m = EmailMessage()
        m['Subject'] = 'Hello-Wörld!-Hello-Wörld!-Hello-Wörlds123! ' \
                       'Hello Wörld!Hello Wörld!'
        self.assertEqual(bytes(m), \
                         b'Subject: =?utf-8?q?Hello-W=C3=B6rld!-Hello-W'
                         b'=C3=B6rld!-Hello-W=C3=B6rlds123!?=\n'
                         b' Hello =?utf-8?q?W=C3=B6rld!Hello_W=C3=B6rld!?=\n\n')

    eleza test_folding_with_utf8_encoding_4(self):
        # bpo-36520
        #
        # Fold a line that contains UTF-8 words before
        # na after the fold point, where the first
        # word ni UTF-8 na the fold point ni within
        # the word.

        m = EmailMessage()
        m['Subject'] = 'Hello-Wörld!-Hello-Wörld!-Hello-Wörlds123!-Hello' \
                       ' Wörld!Hello Wörld!'
        self.assertEqual(bytes(m),
                         b'Subject: =?utf-8?q?Hello-W=C3=B6rld!-Hello-W'
                         b'=C3=B6rld!-Hello-W=C3=B6rlds123!?=\n'
                         b' =?utf-8?q?-Hello_W=C3=B6rld!Hello_W=C3=B6rld!?=\n\n')

    eleza test_folding_with_utf8_encoding_5(self):
        # bpo-36520
        #
        # Fold a line that contains a UTF-8 word after
        # the fold point.

        m = EmailMessage()
        m['Subject'] = '123456789 123456789 123456789 123456789 123456789' \
                       ' 123456789 123456789 Hello Wörld!'
        self.assertEqual(bytes(m),
                         b'Subject: 123456789 123456789 123456789 123456789'
                         b' 123456789 123456789 123456789\n'
                         b' Hello =?utf-8?q?W=C3=B6rld!?=\n\n')

    eleza test_folding_with_utf8_encoding_6(self):
        # bpo-36520
        #
        # Fold a line that contains a UTF-8 word before
        # the fold point na ASCII words after

        m = EmailMessage()
        m['Subject'] = '123456789 123456789 123456789 123456789 Hello Wörld!' \
                       ' 123456789 123456789 123456789 123456789 123456789'   \
                       ' 123456789'
        self.assertEqual(bytes(m),
                         b'Subject: 123456789 123456789 123456789 123456789'
                         b' Hello =?utf-8?q?W=C3=B6rld!?=\n 123456789 '
                         b'123456789 123456789 123456789 123456789 '
                         b'123456789\n\n')

    eleza test_folding_with_utf8_encoding_7(self):
        # bpo-36520
        #
        # Fold a line twice that contains UTF-8 words before
        # na after the first fold point, na ASCII words
        # after the second fold point.

        m = EmailMessage()
        m['Subject'] = '123456789 123456789 Hello Wörld! Hello Wörld! '       \
                       '123456789-123456789 123456789 Hello Wörld! 123456789' \
                       ' 123456789'
        self.assertEqual(bytes(m),
                         b'Subject: 123456789 123456789 Hello =?utf-8?q?'
                         b'W=C3=B6rld!_Hello_W=C3=B6rld!?=\n'
                         b' 123456789-123456789 123456789 Hello '
                         b'=?utf-8?q?W=C3=B6rld!?= 123456789\n 123456789\n\n')

    eleza test_folding_with_utf8_encoding_8(self):
        # bpo-36520
        #
        # Fold a line twice that contains UTF-8 words before
        # the first fold point, na ASCII words after the
        # first fold point, na UTF-8 words after the second
        # fold point.

        m = EmailMessage()
        m['Subject'] = '123456789 123456789 Hello Wörld! Hello Wörld! '       \
                       '123456789 123456789 123456789 123456789 123456789 '   \
                       '123456789-123456789 123456789 Hello Wörld! 123456789' \
                       ' 123456789'
        self.assertEqual(bytes(m),
                         b'Subject: 123456789 123456789 Hello '
                         b'=?utf-8?q?W=C3=B6rld!_Hello_W=C3=B6rld!?=\n 123456789 '
                         b'123456789 123456789 123456789 123456789 '
                         b'123456789-123456789\n 123456789 Hello '
                         b'=?utf-8?q?W=C3=B6rld!?= 123456789 123456789\n\n')

kundi TestMIMEPart(TestEmailMessageBase, TestEmailBase):
    # Doing the full test run here may seem a bit redundant, since the two
    # classes are almost identical.  But what ikiwa they drift apart?  So we do
    # the full tests so that any future drift doesn't introduce bugs.
    message = MIMEPart

    eleza test_set_content_does_not_add_MIME_Version(self):
        m = self._str_msg('')
        cm = self._TestContentManager()
        self.assertNotIn('MIME-Version', m)
        m.set_content(content_manager=cm)
        self.assertNotIn('MIME-Version', m)

    eleza test_string_payload_with_multipart_content_type(self):
        msg = message_from_string(textwrap.dedent("""\
        Content-Type: multipart/mixed; charset="utf-8"

        sample text
        """), policy=policy.default)
        attachments = msg.iter_attachments()
        self.assertEqual(list(attachments), [])


ikiwa __name__ == '__main__':
    unittest.main()
