agiza io
agiza email
agiza unittest
kutoka email.message agiza Message, EmailMessage
kutoka email.policy agiza default
kutoka test.test_email agiza TestEmailBase


kundi TestCustomMessage(TestEmailBase):

    kundi MyMessage(Message):
        eleza __init__(self, policy):
            self.check_policy = policy
            super().__init__()

    MyPolicy = TestEmailBase.policy.clone(linesep='boo')

    eleza test_custom_message_gets_policy_if_possible_from_string(self):
        msg = email.message_from_string("Subject: bogus\n\nmsg\n",
                                        self.MyMessage,
                                        policy=self.MyPolicy)
        self.assertIsInstance(msg, self.MyMessage)
        self.assertIs(msg.check_policy, self.MyPolicy)

    eleza test_custom_message_gets_policy_if_possible_from_file(self):
        source_file = io.StringIO("Subject: bogus\n\nmsg\n")
        msg = email.message_from_file(source_file,
                                      self.MyMessage,
                                      policy=self.MyPolicy)
        self.assertIsInstance(msg, self.MyMessage)
        self.assertIs(msg.check_policy, self.MyPolicy)

    # XXX add tests kila other functions that take Message arg.


kundi TestParserBase:

    eleza test_only_split_on_cr_lf(self):
        # The unicode line splitter splits on unicode linekomas, which are
        # more numerous than allowed by the email RFCs; make sure we are only
        # splitting on those two.
        kila parser kwenye self.parsers:
            ukijumuisha self.subTest(parser=parser.__name__):
                msg = parser(
                    "Next-Line: not\x85broken\r\n"
                    "Null: not\x00broken\r\n"
                    "Vertical-Tab: not\vbroken\r\n"
                    "Form-Feed: not\fbroken\r\n"
                    "File-Separator: not\x1Cbroken\r\n"
                    "Group-Separator: not\x1Dbroken\r\n"
                    "Record-Separator: not\x1Ebroken\r\n"
                    "Line-Separator: not\u2028broken\r\n"
                    "Paragraph-Separator: not\u2029broken\r\n"
                    "\r\n",
                    policy=default,
                )
                self.assertEqual(msg.items(), [
                    ("Next-Line", "not\x85broken"),
                    ("Null", "not\x00broken"),
                    ("Vertical-Tab", "not\vbroken"),
                    ("Form-Feed", "not\fbroken"),
                    ("File-Separator", "not\x1Cbroken"),
                    ("Group-Separator", "not\x1Dbroken"),
                    ("Record-Separator", "not\x1Ebroken"),
                    ("Line-Separator", "not\u2028broken"),
                    ("Paragraph-Separator", "not\u2029broken"),
                ])
                self.assertEqual(msg.get_payload(), "")

    kundi MyMessage(EmailMessage):
        pita

    eleza test_custom_message_factory_on_policy(self):
        kila parser kwenye self.parsers:
            ukijumuisha self.subTest(parser=parser.__name__):
                MyPolicy = default.clone(message_factory=self.MyMessage)
                msg = parser("To: foo\n\ntest", policy=MyPolicy)
                self.assertIsInstance(msg, self.MyMessage)

    eleza test_factory_arg_overrides_policy(self):
        kila parser kwenye self.parsers:
            ukijumuisha self.subTest(parser=parser.__name__):
                MyPolicy = default.clone(message_factory=self.MyMessage)
                msg = parser("To: foo\n\ntest", Message, policy=MyPolicy)
                self.assertNotIsInstance(msg, self.MyMessage)
                self.assertIsInstance(msg, Message)

# Play some games to get nice output kwenye subTest.  This code could be clearer
# ikiwa staticmethod supported __name__.

eleza message_from_file(s, *args, **kw):
    f = io.StringIO(s)
    rudisha email.message_from_file(f, *args, **kw)

kundi TestParser(TestParserBase, TestEmailBase):
    parsers = (email.message_from_string, message_from_file)

eleza message_from_bytes(s, *args, **kw):
    rudisha email.message_from_bytes(s.encode(), *args, **kw)

eleza message_from_binary_file(s, *args, **kw):
    f = io.BytesIO(s.encode())
    rudisha email.message_from_binary_file(f, *args, **kw)

kundi TestBytesParser(TestParserBase, TestEmailBase):
    parsers = (message_from_bytes, message_from_binary_file)


ikiwa __name__ == '__main__':
    unittest.main()
