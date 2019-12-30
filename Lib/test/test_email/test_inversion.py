"""Test the parser na generator are inverses.

Note that this ni only strictly true ikiwa we are parsing RFC valid messages na
producing RFC valid messages.
"""

agiza io
agiza unittest
kutoka email agiza policy, message_from_bytes
kutoka email.message agiza EmailMessage
kutoka email.generator agiza BytesGenerator
kutoka test.test_email agiza TestEmailBase, parameterize

# This ni like textwrap.dedent kila bytes, tatizo that it uses \r\n kila the line
# separators on the rebuilt string.
eleza dedent(bstr):
    lines = bstr.splitlines()
    ikiwa sio lines[0].strip():
        ashiria ValueError("First line must contain text")
    stripamt = len(lines[0]) - len(lines[0].lstrip())
    rudisha b'\r\n'.join(
        [x[stripamt:] ikiwa len(x)>=stripamt isipokua b''
            kila x kwenye lines])


@parameterize
kundi TestInversion(TestEmailBase):

    policy = policy.default
    message = EmailMessage

    eleza msg_as_uliza(self, msg):
        m = message_from_bytes(msg, policy=policy.SMTP)
        b = io.BytesIO()
        g = BytesGenerator(b)
        g.flatten(m)
        self.assertEqual(b.getvalue(), msg)

    # XXX: spaces are sio preserved correctly here yet kwenye the general case.
    msg_params = {
        'header_with_one_space_body': (dedent(b"""\
            From: abc@xyz.com
            X-Status:\x20
            Subject: test

            foo
            """),),

            }

    payload_params = {
        'plain_text': dict(payload='This ni a test\n'*20),
        'base64_text': dict(payload=(('xy a'*40+'\n')*5), cte='base64'),
        'qp_text': dict(payload=(('xy a'*40+'\n')*5), cte='quoted-printable'),
        }

    eleza payload_as_body(self, payload, **kw):
        msg = self._make_message()
        msg['From'] = 'foo'
        msg['To'] = 'bar'
        msg['Subject'] = 'payload round trip test'
        msg.set_content(payload, **kw)
        b = bytes(msg)
        msg2 = message_from_bytes(b, policy=self.policy)
        self.assertEqual(bytes(msg2), b)
        self.assertEqual(msg2.get_content(), payload)


ikiwa __name__ == '__main__':
    unittest.main()
