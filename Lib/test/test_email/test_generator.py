agiza io
agiza textwrap
agiza unittest
kutoka email agiza message_from_string, message_from_bytes
kutoka email.message agiza EmailMessage
kutoka email.generator agiza Generator, BytesGenerator
kutoka email.headerregistry agiza Address
kutoka email agiza policy
kutoka test.test_email agiza TestEmailBase, parameterize


@parameterize
kundi TestGeneratorBase:

    policy = policy.default

    eleza msgmaker(self, msg, policy=Tupu):
        policy = self.policy ikiwa policy ni Tupu isipokua policy
        rudisha self.msgfunc(msg, policy=policy)

    refold_long_expected = {
        0: textwrap.dedent("""\
            To: whom_it_may_concern@example.com
            From: nobody_you_want_to_know@example.com
            Subject: We the willing led by the unknowing are doing the
             impossible kila the ungrateful. We have done so much kila so long ukijumuisha so little
             we are now qualified to do anything ukijumuisha nothing.

            Tupu
            """),
        40: textwrap.dedent("""\
            To: whom_it_may_concern@example.com
            From:
             nobody_you_want_to_know@example.com
            Subject: We the willing led by the
             unknowing are doing the impossible for
             the ungrateful. We have done so much
             kila so long ukijumuisha so little we are now
             qualified to do anything ukijumuisha nothing.

            Tupu
            """),
        20: textwrap.dedent("""\
            To:
             whom_it_may_concern@example.com
            From:
             nobody_you_want_to_know@example.com
            Subject: We the
             willing led by the
             unknowing are doing
             the impossible for
             the ungrateful. We
             have done so much
             kila so long ukijumuisha so
             little we are now
             qualified to do
             anything with
             nothing.

            Tupu
            """),
        }
    refold_long_expected[100] = refold_long_expected[0]

    refold_all_expected = refold_long_expected.copy()
    refold_all_expected[0] = (
            "To: whom_it_may_concern@example.com\n"
            "From: nobody_you_want_to_know@example.com\n"
            "Subject: We the willing led by the unknowing are doing the "
              "impossible kila the ungrateful. We have done so much kila "
              "so long ukijumuisha so little we are now qualified to do anything "
              "ukijumuisha nothing.\n"
              "\n"
              "Tupu\n")
    refold_all_expected[100] = (
            "To: whom_it_may_concern@example.com\n"
            "From: nobody_you_want_to_know@example.com\n"
            "Subject: We the willing led by the unknowing are doing the "
                "impossible kila the ungrateful. We have\n"
              " done so much kila so long ukijumuisha so little we are now qualified "
                "to do anything ukijumuisha nothing.\n"
              "\n"
              "Tupu\n")

    length_params = [n kila n kwenye refold_long_expected]

    eleza length_as_maxheaderlen_parameter(self, n):
        msg = self.msgmaker(self.typ(self.refold_long_expected[0]))
        s = self.ioclass()
        g = self.genclass(s, maxheaderlen=n, policy=self.policy)
        g.flatten(msg)
        self.assertEqual(s.getvalue(), self.typ(self.refold_long_expected[n]))

    eleza length_as_max_line_length_policy(self, n):
        msg = self.msgmaker(self.typ(self.refold_long_expected[0]))
        s = self.ioclass()
        g = self.genclass(s, policy=self.policy.clone(max_line_length=n))
        g.flatten(msg)
        self.assertEqual(s.getvalue(), self.typ(self.refold_long_expected[n]))

    eleza length_as_maxheaderlen_parm_overrides_policy(self, n):
        msg = self.msgmaker(self.typ(self.refold_long_expected[0]))
        s = self.ioclass()
        g = self.genclass(s, maxheaderlen=n,
                          policy=self.policy.clone(max_line_length=10))
        g.flatten(msg)
        self.assertEqual(s.getvalue(), self.typ(self.refold_long_expected[n]))

    eleza length_as_max_line_length_with_refold_none_does_not_fold(self, n):
        msg = self.msgmaker(self.typ(self.refold_long_expected[0]))
        s = self.ioclass()
        g = self.genclass(s, policy=self.policy.clone(refold_source='none',
                                                      max_line_length=n))
        g.flatten(msg)
        self.assertEqual(s.getvalue(), self.typ(self.refold_long_expected[0]))

    eleza length_as_max_line_length_with_refold_all_folds(self, n):
        msg = self.msgmaker(self.typ(self.refold_long_expected[0]))
        s = self.ioclass()
        g = self.genclass(s, policy=self.policy.clone(refold_source='all',
                                                      max_line_length=n))
        g.flatten(msg)
        self.assertEqual(s.getvalue(), self.typ(self.refold_all_expected[n]))

    eleza test_crlf_control_via_policy(self):
        source = "Subject: test\r\n\r\ntest body\r\n"
        expected = source
        msg = self.msgmaker(self.typ(source))
        s = self.ioclass()
        g = self.genclass(s, policy=policy.SMTP)
        g.flatten(msg)
        self.assertEqual(s.getvalue(), self.typ(expected))

    eleza test_flatten_linesep_overrides_policy(self):
        source = "Subject: test\n\ntest body\n"
        expected = source
        msg = self.msgmaker(self.typ(source))
        s = self.ioclass()
        g = self.genclass(s, policy=policy.SMTP)
        g.flatten(msg, linesep='\n')
        self.assertEqual(s.getvalue(), self.typ(expected))

    eleza test_set_mangle_from_via_policy(self):
        source = textwrap.dedent("""\
            Subject: test that
             kutoka ni mangled kwenye the body!

            From time to time I write a rhyme.
            """)
        variants = (
            (Tupu, Kweli),
            (policy.compat32, Kweli),
            (policy.default, Uongo),
            (policy.default.clone(mangle_from_=Kweli), Kweli),
            )
        kila p, mangle kwenye variants:
            expected = source.replace('From ', '>From ') ikiwa mangle isipokua source
            ukijumuisha self.subTest(policy=p, mangle_from_=mangle):
                msg = self.msgmaker(self.typ(source))
                s = self.ioclass()
                g = self.genclass(s, policy=p)
                g.flatten(msg)
                self.assertEqual(s.getvalue(), self.typ(expected))

    eleza test_compat32_max_line_length_does_not_fold_when_none(self):
        msg = self.msgmaker(self.typ(self.refold_long_expected[0]))
        s = self.ioclass()
        g = self.genclass(s, policy=policy.compat32.clone(max_line_length=Tupu))
        g.flatten(msg)
        self.assertEqual(s.getvalue(), self.typ(self.refold_long_expected[0]))

    eleza test_rfc2231_wrapping(self):
        # This ni pretty much just to make sure we don't have an infinite
        # loop; I don't expect anyone to hit this kwenye the field.
        msg = self.msgmaker(self.typ(textwrap.dedent("""\
            To: nobody
            Content-Disposition: attachment;
             filename="afilenamelongenoghtowraphere"

            Tupu
            """)))
        expected = textwrap.dedent("""\
            To: nobody
            Content-Disposition: attachment;
             filename*0*=us-ascii''afilename;
             filename*1*=longenoghtowraphere

            Tupu
            """)
        s = self.ioclass()
        g = self.genclass(s, policy=self.policy.clone(max_line_length=33))
        g.flatten(msg)
        self.assertEqual(s.getvalue(), self.typ(expected))

    eleza test_rfc2231_wrapping_switches_to_default_len_if_too_narrow(self):
        # This ni just to make sure we don't have an infinite loop; I don't
        # expect anyone to hit this kwenye the field, so I'm sio bothering to make
        # the result optimal (the encoding isn't needed).
        msg = self.msgmaker(self.typ(textwrap.dedent("""\
            To: nobody
            Content-Disposition: attachment;
             filename="afilenamelongenoghtowraphere"

            Tupu
            """)))
        expected = textwrap.dedent("""\
            To: nobody
            Content-Disposition:
             attachment;
             filename*0*=us-ascii''afilenamelongenoghtowraphere

            Tupu
            """)
        s = self.ioclass()
        g = self.genclass(s, policy=self.policy.clone(max_line_length=20))
        g.flatten(msg)
        self.assertEqual(s.getvalue(), self.typ(expected))


kundi TestGenerator(TestGeneratorBase, TestEmailBase):

    msgfunc = staticmethod(message_from_string)
    genkundi = Generator
    iokundi = io.StringIO
    typ = str


kundi TestBytesGenerator(TestGeneratorBase, TestEmailBase):

    msgfunc = staticmethod(message_from_bytes)
    genkundi = BytesGenerator
    iokundi = io.BytesIO
    typ = lambda self, x: x.encode('ascii')

    eleza test_cte_type_7bit_handles_unknown_8bit(self):
        source = ("Subject: Maintenant je vous présente mon "
                 "collègue\n\n").encode('utf-8')
        expected = ('Subject: Maintenant je vous =?unknown-8bit?q?'
                    'pr=C3=A9sente_mon_coll=C3=A8gue?=\n\n').encode('ascii')
        msg = message_from_bytes(source)
        s = io.BytesIO()
        g = BytesGenerator(s, policy=self.policy.clone(cte_type='7bit'))
        g.flatten(msg)
        self.assertEqual(s.getvalue(), expected)

    eleza test_cte_type_7bit_transforms_8bit_cte(self):
        source = textwrap.dedent("""\
            From: foo@bar.com
            To: Dinsdale
            Subject: Nudge nudge, wink, wink
            Mime-Version: 1.0
            Content-Type: text/plain; charset="latin-1"
            Content-Transfer-Encoding: 8bit

            oh là là, know what I mean, know what I mean?
            """).encode('latin1')
        msg = message_from_bytes(source)
        expected =  textwrap.dedent("""\
            From: foo@bar.com
            To: Dinsdale
            Subject: Nudge nudge, wink, wink
            Mime-Version: 1.0
            Content-Type: text/plain; charset="iso-8859-1"
            Content-Transfer-Encoding: quoted-printable

            oh l=E0 l=E0, know what I mean, know what I mean?
            """).encode('ascii')
        s = io.BytesIO()
        g = BytesGenerator(s, policy=self.policy.clone(cte_type='7bit',
                                                       linesep='\n'))
        g.flatten(msg)
        self.assertEqual(s.getvalue(), expected)

    eleza test_smtputf8_policy(self):
        msg = EmailMessage()
        msg['From'] = "Páolo <főo@bar.com>"
        msg['To'] = 'Dinsdale'
        msg['Subject'] = 'Nudge nudge, wink, wink \u1F609'
        msg.set_content("oh là là, know what I mean, know what I mean?")
        expected = textwrap.dedent("""\
            From: Páolo <főo@bar.com>
            To: Dinsdale
            Subject: Nudge nudge, wink, wink \u1F609
            Content-Type: text/plain; charset="utf-8"
            Content-Transfer-Encoding: 8bit
            MIME-Version: 1.0

            oh là là, know what I mean, know what I mean?
            """).encode('utf-8').replace(b'\n', b'\r\n')
        s = io.BytesIO()
        g = BytesGenerator(s, policy=policy.SMTPUTF8)
        g.flatten(msg)
        self.assertEqual(s.getvalue(), expected)

    eleza test_smtp_policy(self):
        msg = EmailMessage()
        msg["From"] = Address(addr_spec="foo@bar.com", display_name="Páolo")
        msg["To"] = Address(addr_spec="bar@foo.com", display_name="Dinsdale")
        msg["Subject"] = "Nudge nudge, wink, wink"
        msg.set_content("oh boy, know what I mean, know what I mean?")
        expected = textwrap.dedent("""\
            From: =?utf-8?q?P=C3=A1olo?= <foo@bar.com>
            To: Dinsdale <bar@foo.com>
            Subject: Nudge nudge, wink, wink
            Content-Type: text/plain; charset="utf-8"
            Content-Transfer-Encoding: 7bit
            MIME-Version: 1.0

            oh boy, know what I mean, know what I mean?
            """).encode().replace(b"\n", b"\r\n")
        s = io.BytesIO()
        g = BytesGenerator(s, policy=policy.SMTP)
        g.flatten(msg)
        self.assertEqual(s.getvalue(), expected)


ikiwa __name__ == '__main__':
    unittest.main()
