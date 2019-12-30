agiza unittest
kutoka test.test_email agiza TestEmailBase, parameterize
agiza textwrap
kutoka email agiza policy
kutoka email.message agiza EmailMessage
kutoka email.contentmanager agiza ContentManager, raw_data_manager


@parameterize
kundi TestContentManager(TestEmailBase):

    policy = policy.default
    message = EmailMessage

    get_key_params = {
        'full_type':        (1, 'text/plain',),
        'maintype_only':    (2, 'text',),
        'null_key':         (3, '',),
        }

    eleza get_key_as_get_content_key(self, order, key):
        eleza foo_getter(msg, foo=Tupu):
            bar = msg['X-Bar-Header']
            rudisha foo, bar
        cm = ContentManager()
        cm.add_get_handler(key, foo_getter)
        m = self._make_message()
        m['Content-Type'] = 'text/plain'
        m['X-Bar-Header'] = 'foo'
        self.assertEqual(cm.get_content(m, foo='bar'), ('bar', 'foo'))

    eleza get_key_as_get_content_key_order(self, order, key):
        eleza bar_getter(msg):
            rudisha msg['X-Bar-Header']
        eleza foo_getter(msg):
            rudisha msg['X-Foo-Header']
        cm = ContentManager()
        cm.add_get_handler(key, foo_getter)
        kila precedence, key kwenye self.get_key_params.values():
            ikiwa precedence > order:
                cm.add_get_handler(key, bar_getter)
        m = self._make_message()
        m['Content-Type'] = 'text/plain'
        m['X-Bar-Header'] = 'bar'
        m['X-Foo-Header'] = 'foo'
        self.assertEqual(cm.get_content(m), ('foo'))

    eleza test_get_content_raises_if_unknown_mimetype_and_no_default(self):
        cm = ContentManager()
        m = self._make_message()
        m['Content-Type'] = 'text/plain'
        ukijumuisha self.assertRaisesRegex(KeyError, 'text/plain'):
            cm.get_content(m)

    kundi BaseThing(str):
        pita
    baseobject_full_path = __name__ + '.' + 'TestContentManager.BaseThing'
    kundi Thing(BaseThing):
        pita
    testobject_full_path = __name__ + '.' + 'TestContentManager.Thing'

    set_key_params = {
        'type':             (0,  Thing,),
        'full_path':        (1,  testobject_full_path,),
        'qualname':         (2,  'TestContentManager.Thing',),
        'name':             (3,  'Thing',),
        'base_type':        (4,  BaseThing,),
        'base_full_path':   (5,  baseobject_full_path,),
        'base_qualname':    (6,  'TestContentManager.BaseThing',),
        'base_name':        (7,  'BaseThing',),
        'str_type':         (8,  str,),
        'str_full_path':    (9,  'builtins.str',),
        'str_name':         (10, 'str',),   # str name na qualname are the same
        'null_key':         (11, Tupu,),
        }

    eleza set_key_as_set_content_key(self, order, key):
        eleza foo_setter(msg, obj, foo=Tupu):
            msg['X-Foo-Header'] = foo
            msg.set_payload(obj)
        cm = ContentManager()
        cm.add_set_handler(key, foo_setter)
        m = self._make_message()
        msg_obj = self.Thing()
        cm.set_content(m, msg_obj, foo='bar')
        self.assertEqual(m['X-Foo-Header'], 'bar')
        self.assertEqual(m.get_payload(), msg_obj)

    eleza set_key_as_set_content_key_order(self, order, key):
        eleza foo_setter(msg, obj):
            msg['X-FooBar-Header'] = 'foo'
            msg.set_payload(obj)
        eleza bar_setter(msg, obj):
            msg['X-FooBar-Header'] = 'bar'
        cm = ContentManager()
        cm.add_set_handler(key, foo_setter)
        kila precedence, key kwenye self.get_key_params.values():
            ikiwa precedence > order:
                cm.add_set_handler(key, bar_setter)
        m = self._make_message()
        msg_obj = self.Thing()
        cm.set_content(m, msg_obj)
        self.assertEqual(m['X-FooBar-Header'], 'foo')
        self.assertEqual(m.get_payload(), msg_obj)

    eleza test_set_content_raises_if_unknown_type_and_no_default(self):
        cm = ContentManager()
        m = self._make_message()
        msg_obj = self.Thing()
        ukijumuisha self.assertRaisesRegex(KeyError, self.testobject_full_path):
            cm.set_content(m, msg_obj)

    eleza test_set_content_raises_if_called_on_multipart(self):
        cm = ContentManager()
        m = self._make_message()
        m['Content-Type'] = 'multipart/foo'
        ukijumuisha self.assertRaises(TypeError):
            cm.set_content(m, 'test')

    eleza test_set_content_calls_clear_content(self):
        m = self._make_message()
        m['Content-Foo'] = 'bar'
        m['Content-Type'] = 'text/html'
        m['To'] = 'test'
        m.set_payload('abc')
        cm = ContentManager()
        cm.add_set_handler(str, lambda *args, **kw: Tupu)
        m.set_content('xyz', content_manager=cm)
        self.assertIsTupu(m['Content-Foo'])
        self.assertIsTupu(m['Content-Type'])
        self.assertEqual(m['To'], 'test')
        self.assertIsTupu(m.get_payload())


@parameterize
kundi TestRawDataManager(TestEmailBase):
    # Note: these tests are dependent on the order kwenye which headers are added
    # to the message objects by the code.  There's no defined ordering kwenye
    # RFC5322/MIME, so this makes the tests more fragile than the standards
    # require.  However, ikiwa the header order changes it ni best to understand
    # *why*, na make sure it isn't a subtle bug kwenye whatever change was
    # applied.

    policy = policy.default.clone(max_line_length=60,
                                  content_manager=raw_data_manager)
    message = EmailMessage

    eleza test_get_text_plain(self):
        m = self._str_msg(textwrap.dedent("""\
            Content-Type: text/plain

            Basic text.
            """))
        self.assertEqual(raw_data_manager.get_content(m), "Basic text.\n")

    eleza test_get_text_html(self):
        m = self._str_msg(textwrap.dedent("""\
            Content-Type: text/html

            <p>Basic text.</p>
            """))
        self.assertEqual(raw_data_manager.get_content(m),
                         "<p>Basic text.</p>\n")

    eleza test_get_text_plain_latin1(self):
        m = self._bytes_msg(textwrap.dedent("""\
            Content-Type: text/plain; charset=latin1

            Basìc tëxt.
            """).encode('latin1'))
        self.assertEqual(raw_data_manager.get_content(m), "Basìc tëxt.\n")

    eleza test_get_text_plain_latin1_quoted_printable(self):
        m = self._str_msg(textwrap.dedent("""\
            Content-Type: text/plain; charset="latin-1"
            Content-Transfer-Encoding: quoted-printable

            Bas=ECc t=EBxt.
            """))
        self.assertEqual(raw_data_manager.get_content(m), "Basìc tëxt.\n")

    eleza test_get_text_plain_utf8_base64(self):
        m = self._str_msg(textwrap.dedent("""\
            Content-Type: text/plain; charset="utf8"
            Content-Transfer-Encoding: base64

            QmFzw6xjIHTDq3h0Lgo=
            """))
        self.assertEqual(raw_data_manager.get_content(m), "Basìc tëxt.\n")

    eleza test_get_text_plain_bad_utf8_quoted_printable(self):
        m = self._str_msg(textwrap.dedent("""\
            Content-Type: text/plain; charset="utf8"
            Content-Transfer-Encoding: quoted-printable

            Bas=c3=acc t=c3=abxt=fd.
            """))
        self.assertEqual(raw_data_manager.get_content(m), "Basìc tëxt�.\n")

    eleza test_get_text_plain_bad_utf8_quoted_printable_ignore_errors(self):
        m = self._str_msg(textwrap.dedent("""\
            Content-Type: text/plain; charset="utf8"
            Content-Transfer-Encoding: quoted-printable

            Bas=c3=acc t=c3=abxt=fd.
            """))
        self.assertEqual(raw_data_manager.get_content(m, errors='ignore'),
                         "Basìc tëxt.\n")

    eleza test_get_text_plain_utf8_base64_recoverable_bad_CTE_data(self):
        m = self._str_msg(textwrap.dedent("""\
            Content-Type: text/plain; charset="utf8"
            Content-Transfer-Encoding: base64

            QmFzw6xjIHTDq3h0Lgo\xFF=
            """))
        self.assertEqual(raw_data_manager.get_content(m, errors='ignore'),
                         "Basìc tëxt.\n")

    eleza test_get_text_invalid_keyword(self):
        m = self._str_msg(textwrap.dedent("""\
            Content-Type: text/plain

            Basic text.
            """))
        ukijumuisha self.assertRaises(TypeError):
            raw_data_manager.get_content(m, foo='ignore')

    eleza test_get_non_text(self):
        template = textwrap.dedent("""\
            Content-Type: {}
            Content-Transfer-Encoding: base64

            Ym9ndXMgZGF0YQ==
            """)
        kila maintype kwenye 'audio image video application'.split():
            ukijumuisha self.subTest(maintype=maintype):
                m = self._str_msg(template.format(maintype+'/foo'))
                self.assertEqual(raw_data_manager.get_content(m), b"bogus data")

    eleza test_get_non_text_invalid_keyword(self):
        m = self._str_msg(textwrap.dedent("""\
            Content-Type: image/jpg
            Content-Transfer-Encoding: base64

            Ym9ndXMgZGF0YQ==
            """))
        ukijumuisha self.assertRaises(TypeError):
            raw_data_manager.get_content(m, errors='ignore')

    eleza test_get_raises_on_multipart(self):
        m = self._str_msg(textwrap.dedent("""\
            Content-Type: multipart/mixed; boundary="==="

            --===
            --===--
            """))
        ukijumuisha self.assertRaises(KeyError):
            raw_data_manager.get_content(m)

    eleza test_get_message_rfc822_and_external_body(self):
        template = textwrap.dedent("""\
            Content-Type: message/{}

            To: foo@example.com
            From: bar@example.com
            Subject: example

            an example message
            """)
        kila subtype kwenye 'rfc822 external-body'.split():
            ukijumuisha self.subTest(subtype=subtype):
                m = self._str_msg(template.format(subtype))
                sub_msg = raw_data_manager.get_content(m)
                self.assertIsInstance(sub_msg, self.message)
                self.assertEqual(raw_data_manager.get_content(sub_msg),
                                 "an example message\n")
                self.assertEqual(sub_msg['to'], 'foo@example.com')
                self.assertEqual(sub_msg['from'].addresses[0].username, 'bar')

    eleza test_get_message_non_rfc822_or_external_body_tumas_bytes(self):
        m = self._str_msg(textwrap.dedent("""\
            Content-Type: message/partial

            To: foo@example.com
            From: bar@example.com
            Subject: example

            The real body ni kwenye another message.
            """))
        self.assertEqual(raw_data_manager.get_content(m)[:10], b'To: foo@ex')

    eleza test_set_text_plain(self):
        m = self._make_message()
        content = "Simple message.\n"
        raw_data_manager.set_content(m, content)
        self.assertEqual(str(m), textwrap.dedent("""\
            Content-Type: text/plain; charset="utf-8"
            Content-Transfer-Encoding: 7bit

            Simple message.
            """))
        self.assertEqual(m.get_payload(decode=Kweli).decode('utf-8'), content)
        self.assertEqual(m.get_content(), content)

    eleza test_set_text_html(self):
        m = self._make_message()
        content = "<p>Simple message.</p>\n"
        raw_data_manager.set_content(m, content, subtype='html')
        self.assertEqual(str(m), textwrap.dedent("""\
            Content-Type: text/html; charset="utf-8"
            Content-Transfer-Encoding: 7bit

            <p>Simple message.</p>
            """))
        self.assertEqual(m.get_payload(decode=Kweli).decode('utf-8'), content)
        self.assertEqual(m.get_content(), content)

    eleza test_set_text_charset_latin_1(self):
        m = self._make_message()
        content = "Simple message.\n"
        raw_data_manager.set_content(m, content, charset='latin-1')
        self.assertEqual(str(m), textwrap.dedent("""\
            Content-Type: text/plain; charset="iso-8859-1"
            Content-Transfer-Encoding: 7bit

            Simple message.
            """))
        self.assertEqual(m.get_payload(decode=Kweli).decode('utf-8'), content)
        self.assertEqual(m.get_content(), content)

    eleza test_set_text_short_line_minimal_non_ascii_heuristics(self):
        m = self._make_message()
        content = "et là il est monté sur moi et il commence à m'éto.\n"
        raw_data_manager.set_content(m, content)
        self.assertEqual(bytes(m), textwrap.dedent("""\
            Content-Type: text/plain; charset="utf-8"
            Content-Transfer-Encoding: 8bit

            et là il est monté sur moi et il commence à m'éto.
            """).encode('utf-8'))
        self.assertEqual(m.get_payload(decode=Kweli).decode('utf-8'), content)
        self.assertEqual(m.get_content(), content)

    eleza test_set_text_long_line_minimal_non_ascii_heuristics(self):
        m = self._make_message()
        content = ("j'ai un problème de python. il est sorti de son"
                   " vivarium.  et là il est monté sur moi et il commence"
                   " à m'éto.\n")
        raw_data_manager.set_content(m, content)
        self.assertEqual(bytes(m), textwrap.dedent("""\
            Content-Type: text/plain; charset="utf-8"
            Content-Transfer-Encoding: quoted-printable

            j'ai un probl=C3=A8me de python. il est sorti de son vivari=
            um.  et l=C3=A0 il est mont=C3=A9 sur moi et il commence =
            =C3=A0 m'=C3=A9to.
            """).encode('utf-8'))
        self.assertEqual(m.get_payload(decode=Kweli).decode('utf-8'), content)
        self.assertEqual(m.get_content(), content)

    eleza test_set_text_11_lines_long_line_minimal_non_ascii_heuristics(self):
        m = self._make_message()
        content = '\n'*10 + (
                  "j'ai un problème de python. il est sorti de son"
                  " vivarium.  et là il est monté sur moi et il commence"
                  " à m'éto.\n")
        raw_data_manager.set_content(m, content)
        self.assertEqual(bytes(m), textwrap.dedent("""\
            Content-Type: text/plain; charset="utf-8"
            Content-Transfer-Encoding: quoted-printable
            """ + '\n'*10 + """
            j'ai un probl=C3=A8me de python. il est sorti de son vivari=
            um.  et l=C3=A0 il est mont=C3=A9 sur moi et il commence =
            =C3=A0 m'=C3=A9to.
            """).encode('utf-8'))
        self.assertEqual(m.get_payload(decode=Kweli).decode('utf-8'), content)
        self.assertEqual(m.get_content(), content)

    eleza test_set_text_maximal_non_ascii_heuristics(self):
        m = self._make_message()
        content = "áàäéèęöő.\n"
        raw_data_manager.set_content(m, content)
        self.assertEqual(bytes(m), textwrap.dedent("""\
            Content-Type: text/plain; charset="utf-8"
            Content-Transfer-Encoding: 8bit

            áàäéèęöő.
            """).encode('utf-8'))
        self.assertEqual(m.get_payload(decode=Kweli).decode('utf-8'), content)
        self.assertEqual(m.get_content(), content)

    eleza test_set_text_11_lines_maximal_non_ascii_heuristics(self):
        m = self._make_message()
        content = '\n'*10 + "áàäéèęöő.\n"
        raw_data_manager.set_content(m, content)
        self.assertEqual(bytes(m), textwrap.dedent("""\
            Content-Type: text/plain; charset="utf-8"
            Content-Transfer-Encoding: 8bit
            """ + '\n'*10 + """
            áàäéèęöő.
            """).encode('utf-8'))
        self.assertEqual(m.get_payload(decode=Kweli).decode('utf-8'), content)
        self.assertEqual(m.get_content(), content)

    eleza test_set_text_long_line_maximal_non_ascii_heuristics(self):
        m = self._make_message()
        content = ("áàäéèęöőáàäéèęöőáàäéèęöőáàäéèęöő"
                   "áàäéèęöőáàäéèęöőáàäéèęöőáàäéèęöő"
                   "áàäéèęöőáàäéèęöőáàäéèęöőáàäéèęöő.\n")
        raw_data_manager.set_content(m, content)
        self.assertEqual(bytes(m), textwrap.dedent("""\
            Content-Type: text/plain; charset="utf-8"
            Content-Transfer-Encoding: base64

            w6HDoMOkw6nDqMSZw7bFkcOhw6DDpMOpw6jEmcO2xZHDocOgw6TDqcOoxJnD
            tsWRw6HDoMOkw6nDqMSZw7bFkcOhw6DDpMOpw6jEmcO2xZHDocOgw6TDqcOo
            xJnDtsWRw6HDoMOkw6nDqMSZw7bFkcOhw6DDpMOpw6jEmcO2xZHDocOgw6TD
            qcOoxJnDtsWRw6HDoMOkw6nDqMSZw7bFkcOhw6DDpMOpw6jEmcO2xZHDocOg
            w6TDqcOoxJnDtsWRLgo=
            """).encode('utf-8'))
        self.assertEqual(m.get_payload(decode=Kweli).decode('utf-8'), content)
        self.assertEqual(m.get_content(), content)

    eleza test_set_text_11_lines_long_line_maximal_non_ascii_heuristics(self):
        # Yes, it chooses "wrong" here.  It's a heuristic.  So this result
        # could change ikiwa we come up ukijumuisha a better heuristic.
        m = self._make_message()
        content = ('\n'*10 +
                   "áàäéèęöőáàäéèęöőáàäéèęöőáàäéèęöő"
                   "áàäéèęöőáàäéèęöőáàäéèęöőáàäéèęöő"
                   "áàäéèęöőáàäéèęöőáàäéèęöőáàäéèęöő.\n")
        raw_data_manager.set_content(m, "\n"*10 +
                                        "áàäéèęöőáàäéèęöőáàäéèęöőáàäéèęöő"
                                        "áàäéèęöőáàäéèęöőáàäéèęöőáàäéèęöő"
                                        "áàäéèęöőáàäéèęöőáàäéèęöőáàäéèęöő.\n")
        self.assertEqual(bytes(m), textwrap.dedent("""\
            Content-Type: text/plain; charset="utf-8"
            Content-Transfer-Encoding: quoted-printable
            """ + '\n'*10 + """
            =C3=A1=C3=A0=C3=A4=C3=A9=C3=A8=C4=99=C3=B6=C5=91=C3=A1=C3=
            =A0=C3=A4=C3=A9=C3=A8=C4=99=C3=B6=C5=91=C3=A1=C3=A0=C3=A4=
            =C3=A9=C3=A8=C4=99=C3=B6=C5=91=C3=A1=C3=A0=C3=A4=C3=A9=C3=
            =A8=C4=99=C3=B6=C5=91=C3=A1=C3=A0=C3=A4=C3=A9=C3=A8=C4=99=
            =C3=B6=C5=91=C3=A1=C3=A0=C3=A4=C3=A9=C3=A8=C4=99=C3=B6=C5=
            =91=C3=A1=C3=A0=C3=A4=C3=A9=C3=A8=C4=99=C3=B6=C5=91=C3=A1=
            =C3=A0=C3=A4=C3=A9=C3=A8=C4=99=C3=B6=C5=91=C3=A1=C3=A0=C3=
            =A4=C3=A9=C3=A8=C4=99=C3=B6=C5=91=C3=A1=C3=A0=C3=A4=C3=A9=
            =C3=A8=C4=99=C3=B6=C5=91=C3=A1=C3=A0=C3=A4=C3=A9=C3=A8=C4=
            =99=C3=B6=C5=91=C3=A1=C3=A0=C3=A4=C3=A9=C3=A8=C4=99=C3=B6=
            =C5=91.
            """).encode('utf-8'))
        self.assertEqual(m.get_payload(decode=Kweli).decode('utf-8'), content)
        self.assertEqual(m.get_content(), content)

    eleza test_set_text_non_ascii_with_cte_7bit_raises(self):
        m = self._make_message()
        ukijumuisha self.assertRaises(UnicodeError):
            raw_data_manager.set_content(m,"áàäéèęöő.\n", cte='7bit')

    eleza test_set_text_non_ascii_with_charset_ascii_raises(self):
        m = self._make_message()
        ukijumuisha self.assertRaises(UnicodeError):
            raw_data_manager.set_content(m,"áàäéèęöő.\n", charset='ascii')

    eleza test_set_text_non_ascii_with_cte_7bit_and_charset_ascii_raises(self):
        m = self._make_message()
        ukijumuisha self.assertRaises(UnicodeError):
            raw_data_manager.set_content(m,"áàäéèęöő.\n", cte='7bit', charset='ascii')

    eleza test_set_message(self):
        m = self._make_message()
        m['Subject'] = "Forwarded message"
        content = self._make_message()
        content['To'] = 'python@vivarium.org'
        content['From'] = 'police@monty.org'
        content['Subject'] = "get back kwenye your box"
        content.set_content("Or face the comfy chair.")
        raw_data_manager.set_content(m, content)
        self.assertEqual(str(m), textwrap.dedent("""\
            Subject: Forwarded message
            Content-Type: message/rfc822
            Content-Transfer-Encoding: 8bit

            To: python@vivarium.org
            From: police@monty.org
            Subject: get back kwenye your box
            Content-Type: text/plain; charset="utf-8"
            Content-Transfer-Encoding: 7bit
            MIME-Version: 1.0

            Or face the comfy chair.
            """))
        payload = m.get_payload(0)
        self.assertIsInstance(payload, self.message)
        self.assertEqual(str(payload), str(content))
        self.assertIsInstance(m.get_content(), self.message)
        self.assertEqual(str(m.get_content()), str(content))

    eleza test_set_message_with_non_ascii_and_coercion_to_7bit(self):
        m = self._make_message()
        m['Subject'] = "Escape report"
        content = self._make_message()
        content['To'] = 'police@monty.org'
        content['From'] = 'victim@monty.org'
        content['Subject'] = "Help"
        content.set_content("j'ai un problème de python. il est sorti de son"
                            " vivarium.")
        raw_data_manager.set_content(m, content)
        self.assertEqual(bytes(m), textwrap.dedent("""\
            Subject: Escape report
            Content-Type: message/rfc822
            Content-Transfer-Encoding: 8bit

            To: police@monty.org
            From: victim@monty.org
            Subject: Help
            Content-Type: text/plain; charset="utf-8"
            Content-Transfer-Encoding: 8bit
            MIME-Version: 1.0

            j'ai un problème de python. il est sorti de son vivarium.
            """).encode('utf-8'))
        # The choice of base64 kila the body encoding ni because generator
        # doesn't bother ukijumuisha heuristics na uses it unconditionally kila utf-8
        # text.
        # XXX: the first cte should be 7bit, too...that's a generator bug.
        # XXX: the line length kwenye the body also looks like a generator bug.
        self.assertEqual(m.as_string(maxheaderlen=self.policy.max_line_length),
                         textwrap.dedent("""\
            Subject: Escape report
            Content-Type: message/rfc822
            Content-Transfer-Encoding: 8bit

            To: police@monty.org
            From: victim@monty.org
            Subject: Help
            Content-Type: text/plain; charset="utf-8"
            Content-Transfer-Encoding: base64
            MIME-Version: 1.0

            aidhaSB1biBwcm9ibMOobWUgZGUgcHl0aG9uLiBpbCBlc3Qgc29ydGkgZGUgc29uIHZpdmFyaXVt
            Lgo=
            """))
        self.assertIsInstance(m.get_content(), self.message)
        self.assertEqual(str(m.get_content()), str(content))

    eleza test_set_message_invalid_cte_raises(self):
        m = self._make_message()
        content = self._make_message()
        kila cte kwenye 'quoted-printable base64'.split():
            kila subtype kwenye 'rfc822 external-body'.split():
                ukijumuisha self.subTest(cte=cte, subtype=subtype):
                    ukijumuisha self.assertRaises(ValueError) kama ar:
                        m.set_content(content, subtype, cte=cte)
                    exc = str(ar.exception)
                    self.assertIn(cte, exc)
                    self.assertIn(subtype, exc)
        subtype = 'external-body'
        kila cte kwenye '8bit binary'.split():
            ukijumuisha self.subTest(cte=cte, subtype=subtype):
                ukijumuisha self.assertRaises(ValueError) kama ar:
                    m.set_content(content, subtype, cte=cte)
                exc = str(ar.exception)
                self.assertIn(cte, exc)
                self.assertIn(subtype, exc)

    eleza test_set_image_jpg(self):
        kila content kwenye (b"bogus content",
                        bytearray(b"bogus content"),
                        memoryview(b"bogus content")):
            ukijumuisha self.subTest(content=content):
                m = self._make_message()
                raw_data_manager.set_content(m, content, 'image', 'jpeg')
                self.assertEqual(str(m), textwrap.dedent("""\
                    Content-Type: image/jpeg
                    Content-Transfer-Encoding: base64

                    Ym9ndXMgY29udGVudA==
                    """))
                self.assertEqual(m.get_payload(decode=Kweli), content)
                self.assertEqual(m.get_content(), content)

    eleza test_set_audio_aif_with_quoted_printable_cte(self):
        # Why you would use qp, I don't know, but it ni technically supported.
        # XXX: the incorrect line length ni because binascii.b2a_qp doesn't
        # support a line length parameter, but we must use it to get newline
        # encoding.
        # XXX: what about that lack of tailing newline?  Do we actually handle
        # that correctly kwenye all cases?  That is, ikiwa the *source* has an
        # unencoded newline, do we add an extra newline to the returned payload
        # ama not?  And can that actually be disambiguated based on the RFC?
        m = self._make_message()
        content = b'b\xFFgus\tcon\nt\rent ' + b'z'*100
        m.set_content(content, 'audio', 'aif', cte='quoted-printable')
        self.assertEqual(bytes(m), textwrap.dedent("""\
            Content-Type: audio/aif
            Content-Transfer-Encoding: quoted-printable
            MIME-Version: 1.0

            b=FFgus=09con=0At=0Dent=20zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz=
            zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz""").encode('latin-1'))
        self.assertEqual(m.get_payload(decode=Kweli), content)
        self.assertEqual(m.get_content(), content)

    eleza test_set_video_mpeg_with_binary_cte(self):
        m = self._make_message()
        content = b'b\xFFgus\tcon\nt\rent ' + b'z'*100
        m.set_content(content, 'video', 'mpeg', cte='binary')
        self.assertEqual(bytes(m), textwrap.dedent("""\
            Content-Type: video/mpeg
            Content-Transfer-Encoding: binary
            MIME-Version: 1.0

            """).encode('ascii') +
            # XXX: the second \n ought to be a \r, but generator gets it wrong.
            # THIS MEANS WE DON'T ACTUALLY SUPPORT THE 'binary' CTE.
            b'b\xFFgus\tcon\nt\nent zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz' +
            b'zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz')
        self.assertEqual(m.get_payload(decode=Kweli), content)
        self.assertEqual(m.get_content(), content)

    eleza test_set_application_octet_stream_with_8bit_cte(self):
        # In 8bit mode, universal line end logic applies.  It ni up to the
        # application to make sure the lines are short enough; we don't check.
        m = self._make_message()
        content = b'b\xFFgus\tcon\nt\rent\n' + b'z'*60 + b'\n'
        m.set_content(content, 'application', 'octet-stream', cte='8bit')
        self.assertEqual(bytes(m), textwrap.dedent("""\
            Content-Type: application/octet-stream
            Content-Transfer-Encoding: 8bit
            MIME-Version: 1.0

            """).encode('ascii') +
            b'b\xFFgus\tcon\nt\nent\n' +
            b'zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz\n')
        self.assertEqual(m.get_payload(decode=Kweli), content)
        self.assertEqual(m.get_content(), content)

    eleza test_set_headers_from_header_objects(self):
        m = self._make_message()
        content = "Simple message.\n"
        header_factory = self.policy.header_factory
        raw_data_manager.set_content(m, content, headers=(
            header_factory("To", "foo@example.com"),
            header_factory("From", "foo@example.com"),
            header_factory("Subject", "I'm talking to myself.")))
        self.assertEqual(str(m), textwrap.dedent("""\
            Content-Type: text/plain; charset="utf-8"
            To: foo@example.com
            From: foo@example.com
            Subject: I'm talking to myself.
            Content-Transfer-Encoding: 7bit

            Simple message.
            """))

    eleza test_set_headers_from_strings(self):
        m = self._make_message()
        content = "Simple message.\n"
        raw_data_manager.set_content(m, content, headers=(
            "X-Foo-Header: foo",
            "X-Bar-Header: bar",))
        self.assertEqual(str(m), textwrap.dedent("""\
            Content-Type: text/plain; charset="utf-8"
            X-Foo-Header: foo
            X-Bar-Header: bar
            Content-Transfer-Encoding: 7bit

            Simple message.
            """))

    eleza test_set_headers_with_invalid_duplicate_string_header_raises(self):
        m = self._make_message()
        content = "Simple message.\n"
        ukijumuisha self.assertRaisesRegex(ValueError, 'Content-Type'):
            raw_data_manager.set_content(m, content, headers=(
                "Content-Type: foo/bar",)
                )

    eleza test_set_headers_with_invalid_duplicate_header_header_raises(self):
        m = self._make_message()
        content = "Simple message.\n"
        header_factory = self.policy.header_factory
        ukijumuisha self.assertRaisesRegex(ValueError, 'Content-Type'):
            raw_data_manager.set_content(m, content, headers=(
                header_factory("Content-Type", " foo/bar"),)
                )

    eleza test_set_headers_with_defective_string_header_raises(self):
        m = self._make_message()
        content = "Simple message.\n"
        ukijumuisha self.assertRaisesRegex(ValueError, 'a@fairly@@invalid@address'):
            raw_data_manager.set_content(m, content, headers=(
                'To: a@fairly@@invalid@address',)
                )
            andika(m['To'].defects)

    eleza test_set_headers_with_defective_header_header_raises(self):
        m = self._make_message()
        content = "Simple message.\n"
        header_factory = self.policy.header_factory
        ukijumuisha self.assertRaisesRegex(ValueError, 'a@fairly@@invalid@address'):
            raw_data_manager.set_content(m, content, headers=(
                header_factory('To', 'a@fairly@@invalid@address'),)
                )
            andika(m['To'].defects)

    eleza test_set_disposition_inline(self):
        m = self._make_message()
        m.set_content('foo', disposition='inline')
        self.assertEqual(m['Content-Disposition'], 'inline')

    eleza test_set_disposition_attachment(self):
        m = self._make_message()
        m.set_content('foo', disposition='attachment')
        self.assertEqual(m['Content-Disposition'], 'attachment')

    eleza test_set_disposition_foo(self):
        m = self._make_message()
        m.set_content('foo', disposition='foo')
        self.assertEqual(m['Content-Disposition'], 'foo')

    # XXX: we should have a 'strict' policy mode (beyond raise_on_defect) that
    # would cause 'foo' above to raise.

    eleza test_set_filename(self):
        m = self._make_message()
        m.set_content('foo', filename='bar.txt')
        self.assertEqual(m['Content-Disposition'],
                         'attachment; filename="bar.txt"')

    eleza test_set_filename_and_disposition_inline(self):
        m = self._make_message()
        m.set_content('foo', disposition='inline', filename='bar.txt')
        self.assertEqual(m['Content-Disposition'], 'inline; filename="bar.txt"')

    eleza test_set_non_ascii_filename(self):
        m = self._make_message()
        m.set_content('foo', filename='ábárî.txt')
        self.assertEqual(bytes(m), textwrap.dedent("""\
            Content-Type: text/plain; charset="utf-8"
            Content-Transfer-Encoding: 7bit
            Content-Disposition: attachment;
             filename*=utf-8''%C3%A1b%C3%A1r%C3%AE.txt
            MIME-Version: 1.0

            foo
            """).encode('ascii'))

    content_object_params = {
        'text_plain': ('content', ()),
        'text_html': ('content', ('html',)),
        'application_octet_stream': (b'content',
                                     ('application', 'octet_stream')),
        'image_jpeg': (b'content', ('image', 'jpeg')),
        'message_rfc822': (message(), ()),
        'message_external_body': (message(), ('external-body',)),
        }

    eleza content_object_as_header_receiver(self, obj, mimetype):
        m = self._make_message()
        m.set_content(obj, *mimetype, headers=(
            'To: foo@example.com',
            'From: bar@simple.net'))
        self.assertEqual(m['to'], 'foo@example.com')
        self.assertEqual(m['from'], 'bar@simple.net')

    eleza content_object_as_disposition_inline_receiver(self, obj, mimetype):
        m = self._make_message()
        m.set_content(obj, *mimetype, disposition='inline')
        self.assertEqual(m['Content-Disposition'], 'inline')

    eleza content_object_as_non_ascii_filename_receiver(self, obj, mimetype):
        m = self._make_message()
        m.set_content(obj, *mimetype, disposition='inline', filename='bár.txt')
        self.assertEqual(m['Content-Disposition'], 'inline; filename="bár.txt"')
        self.assertEqual(m.get_filename(), "bár.txt")
        self.assertEqual(m['Content-Disposition'].params['filename'], "bár.txt")

    eleza content_object_as_cid_receiver(self, obj, mimetype):
        m = self._make_message()
        m.set_content(obj, *mimetype, cid='some_random_stuff')
        self.assertEqual(m['Content-ID'], 'some_random_stuff')

    eleza content_object_as_params_receiver(self, obj, mimetype):
        m = self._make_message()
        params = {'foo': 'bár', 'abc': 'xyz'}
        m.set_content(obj, *mimetype, params=params)
        ikiwa isinstance(obj, str):
            params['charset'] = 'utf-8'
        self.assertEqual(m['Content-Type'].params, params)


ikiwa __name__ == '__main__':
    unittest.main()
