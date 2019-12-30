agiza io
agiza types
agiza textwrap
agiza unittest
agiza email.errors
agiza email.policy
agiza email.parser
agiza email.generator
agiza email.message
kutoka email agiza headerregistry

eleza make_defaults(base_defaults, differences):
    defaults = base_defaults.copy()
    defaults.update(differences)
    rudisha defaults

kundi PolicyAPITests(unittest.TestCase):

    longMessage = Kweli

    # Base default values.
    compat32_defaults = {
        'max_line_length':          78,
        'linesep':                  '\n',
        'cte_type':                 '8bit',
        'raise_on_defect':          Uongo,
        'mangle_from_':             Kweli,
        'message_factory':          Tupu,
        }
    # These default values are the ones set on email.policy.default.
    # If any of these defaults change, the docs must be updated.
    policy_defaults = compat32_defaults.copy()
    policy_defaults.update({
        'utf8':                     Uongo,
        'raise_on_defect':          Uongo,
        'header_factory':           email.policy.EmailPolicy.header_factory,
        'refold_source':            'long',
        'content_manager':          email.policy.EmailPolicy.content_manager,
        'mangle_from_':             Uongo,
        'message_factory':          email.message.EmailMessage,
        })

    # For each policy under test, we give here what we expect the defaults to
    # be kila that policy.  The second argument to make defaults ni the
    # difference between the base defaults na that kila the particular policy.
    new_policy = email.policy.EmailPolicy()
    policies = {
        email.policy.compat32: make_defaults(compat32_defaults, {}),
        email.policy.default: make_defaults(policy_defaults, {}),
        email.policy.SMTP: make_defaults(policy_defaults,
                                         {'linesep': '\r\n'}),
        email.policy.SMTPUTF8: make_defaults(policy_defaults,
                                             {'linesep': '\r\n',
                                              'utf8': Kweli}),
        email.policy.HTTP: make_defaults(policy_defaults,
                                         {'linesep': '\r\n',
                                          'max_line_length': Tupu}),
        email.policy.strict: make_defaults(policy_defaults,
                                           {'raise_on_defect': Kweli}),
        new_policy: make_defaults(policy_defaults, {}),
        }
    # Creating a new policy creates a new header factory.  There ni a test
    # later that proves this.
    policies[new_policy]['header_factory'] = new_policy.header_factory

    eleza test_defaults(self):
        kila policy, expected kwenye self.policies.items():
            kila attr, value kwenye expected.items():
                ukijumuisha self.subTest(policy=policy, attr=attr):
                    self.assertEqual(getattr(policy, attr), value,
                                    ("change {} docs/docstrings ikiwa defaults have "
                                    "changed").format(policy))

    eleza test_all_attributes_covered(self):
        kila policy, expected kwenye self.policies.items():
            kila attr kwenye dir(policy):
                ukijumuisha self.subTest(policy=policy, attr=attr):
                    ikiwa (attr.startswith('_') or
                            isinstance(getattr(email.policy.EmailPolicy, attr),
                                  types.FunctionType)):
                        endelea
                    isipokua:
                        self.assertIn(attr, expected,
                                      "{} ni sio fully tested".format(attr))

    eleza test_abc(self):
        ukijumuisha self.assertRaises(TypeError) as cm:
            email.policy.Policy()
        msg = str(cm.exception)
        abstract_methods = ('fold',
                            'fold_binary',
                            'header_fetch_parse',
                            'header_source_parse',
                            'header_store_parse')
        kila method kwenye abstract_methods:
            self.assertIn(method, msg)

    eleza test_policy_is_immutable(self):
        kila policy, defaults kwenye self.policies.items():
            kila attr kwenye defaults:
                ukijumuisha self.assertRaisesRegex(AttributeError, attr+".*read-only"):
                    setattr(policy, attr, Tupu)
            ukijumuisha self.assertRaisesRegex(AttributeError, 'no attribute.*foo'):
                policy.foo = Tupu

    eleza test_set_policy_attrs_when_cloned(self):
        # Tupu of the attributes has a default value of Tupu, so we set them
        # all to Tupu kwenye the clone call na check that it worked.
        kila policyclass, defaults kwenye self.policies.items():
            testattrdict = {attr: Tupu kila attr kwenye defaults}
            policy = policyclass.clone(**testattrdict)
            kila attr kwenye defaults:
                self.assertIsTupu(getattr(policy, attr))

    eleza test_reject_non_policy_keyword_when_called(self):
        kila policykundi kwenye self.policies:
            ukijumuisha self.assertRaises(TypeError):
                policyclass(this_keyword_should_not_be_valid=Tupu)
            ukijumuisha self.assertRaises(TypeError):
                policyclass(newtline=Tupu)

    eleza test_policy_addition(self):
        expected = self.policy_defaults.copy()
        p1 = email.policy.default.clone(max_line_length=100)
        p2 = email.policy.default.clone(max_line_length=50)
        added = p1 + p2
        expected.update(max_line_length=50)
        kila attr, value kwenye expected.items():
            self.assertEqual(getattr(added, attr), value)
        added = p2 + p1
        expected.update(max_line_length=100)
        kila attr, value kwenye expected.items():
            self.assertEqual(getattr(added, attr), value)
        added = added + email.policy.default
        kila attr, value kwenye expected.items():
            self.assertEqual(getattr(added, attr), value)

    eleza test_fold_zero_max_line_length(self):
        expected = 'Subject: =?utf-8?q?=C3=A1?=\n'

        msg = email.message.EmailMessage()
        msg['Subject'] = 'á'

        p1 = email.policy.default.clone(max_line_length=0)
        p2 = email.policy.default.clone(max_line_length=Tupu)

        self.assertEqual(p1.fold('Subject', msg['Subject']), expected)
        self.assertEqual(p2.fold('Subject', msg['Subject']), expected)

    eleza test_register_defect(self):
        kundi Dummy:
            eleza __init__(self):
                self.defects = []
        obj = Dummy()
        defect = object()
        policy = email.policy.EmailPolicy()
        policy.register_defect(obj, defect)
        self.assertEqual(obj.defects, [defect])
        defect2 = object()
        policy.register_defect(obj, defect2)
        self.assertEqual(obj.defects, [defect, defect2])

    kundi MyObj:
        eleza __init__(self):
            self.defects = []

    kundi MyDefect(Exception):
        pass

    eleza test_handle_defect_raises_on_strict(self):
        foo = self.MyObj()
        defect = self.MyDefect("the telly ni broken")
        ukijumuisha self.assertRaisesRegex(self.MyDefect, "the telly ni broken"):
            email.policy.strict.handle_defect(foo, defect)

    eleza test_handle_defect_registers_defect(self):
        foo = self.MyObj()
        defect1 = self.MyDefect("one")
        email.policy.default.handle_defect(foo, defect1)
        self.assertEqual(foo.defects, [defect1])
        defect2 = self.MyDefect("two")
        email.policy.default.handle_defect(foo, defect2)
        self.assertEqual(foo.defects, [defect1, defect2])

    kundi MyPolicy(email.policy.EmailPolicy):
        defects = Tupu
        eleza __init__(self, *args, **kw):
            super().__init__(*args, defects=[], **kw)
        eleza register_defect(self, obj, defect):
            self.defects.append(defect)

    eleza test_overridden_register_defect_still_raises(self):
        foo = self.MyObj()
        defect = self.MyDefect("the telly ni broken")
        ukijumuisha self.assertRaisesRegex(self.MyDefect, "the telly ni broken"):
            self.MyPolicy(raise_on_defect=Kweli).handle_defect(foo, defect)

    eleza test_overridden_register_defect_works(self):
        foo = self.MyObj()
        defect1 = self.MyDefect("one")
        my_policy = self.MyPolicy()
        my_policy.handle_defect(foo, defect1)
        self.assertEqual(my_policy.defects, [defect1])
        self.assertEqual(foo.defects, [])
        defect2 = self.MyDefect("two")
        my_policy.handle_defect(foo, defect2)
        self.assertEqual(my_policy.defects, [defect1, defect2])
        self.assertEqual(foo.defects, [])

    eleza test_default_header_factory(self):
        h = email.policy.default.header_factory('Test', 'test')
        self.assertEqual(h.name, 'Test')
        self.assertIsInstance(h, headerregistry.UnstructuredHeader)
        self.assertIsInstance(h, headerregistry.BaseHeader)

    kundi Foo:
        parse = headerregistry.UnstructuredHeader.parse

    eleza test_each_Policy_gets_unique_factory(self):
        policy1 = email.policy.EmailPolicy()
        policy2 = email.policy.EmailPolicy()
        policy1.header_factory.map_to_type('foo', self.Foo)
        h = policy1.header_factory('foo', 'test')
        self.assertIsInstance(h, self.Foo)
        self.assertNotIsInstance(h, headerregistry.UnstructuredHeader)
        h = policy2.header_factory('foo', 'test')
        self.assertNotIsInstance(h, self.Foo)
        self.assertIsInstance(h, headerregistry.UnstructuredHeader)

    eleza test_clone_copies_factory(self):
        policy1 = email.policy.EmailPolicy()
        policy2 = policy1.clone()
        policy1.header_factory.map_to_type('foo', self.Foo)
        h = policy1.header_factory('foo', 'test')
        self.assertIsInstance(h, self.Foo)
        h = policy2.header_factory('foo', 'test')
        self.assertIsInstance(h, self.Foo)

    eleza test_new_factory_overrides_default(self):
        mypolicy = email.policy.EmailPolicy()
        myfactory = mypolicy.header_factory
        newpolicy = mypolicy + email.policy.strict
        self.assertEqual(newpolicy.header_factory, myfactory)
        newpolicy = email.policy.strict + mypolicy
        self.assertEqual(newpolicy.header_factory, myfactory)

    eleza test_adding_default_policies_preserves_default_factory(self):
        newpolicy = email.policy.default + email.policy.strict
        self.assertEqual(newpolicy.header_factory,
                         email.policy.EmailPolicy.header_factory)
        self.assertEqual(newpolicy.__dict__, {'raise_on_defect': Kweli})

    eleza test_non_ascii_chars_do_not_cause_inf_loop(self):
        policy = email.policy.default.clone(max_line_length=20)
        actual = policy.fold('Subject', 'ą' * 12)
        self.assertEqual(
            actual,
            'Subject: \n' +
            12 * ' =?utf-8?q?=C4=85?=\n')

    eleza test_short_maxlen_error(self):
        # RFC 2047 chrome takes up 7 characters, plus the length of the charset
        # name, so folding should fail ikiwa maxlen ni lower than the minimum
        # required length kila a line.

        # Note: This ni only triggered when there ni a single word longer than
        # max_line_length, hence the 1234567890 at the end of this whimsical
        # subject. This ni because when we encounter a word longer than
        # max_line_length, it ni broken down into encoded words to fit
        # max_line_length. If the max_line_length isn't large enough to even
        # contain the RFC 2047 chrome (`?=<charset>?q??=`), we fail.
        subject = "Melt away the pounds ukijumuisha this one simple trick! 1234567890"

        kila maxlen kwenye [3, 7, 9]:
            ukijumuisha self.subTest(maxlen=maxlen):
                policy = email.policy.default.clone(max_line_length=maxlen)
                ukijumuisha self.assertRaises(email.errors.HeaderParseError):
                    policy.fold("Subject", subject)

    # XXX: Need subclassing tests.
    # For adding subclassed objects, make sure the usual rules apply (subclass
    # wins), but that the order still works (right overrides left).


kundi TestException(Exception):
    pass

kundi TestPolicyPropagation(unittest.TestCase):

    # The abstract methods are used by the parser but sio by the wrapper
    # functions that call it, so ikiwa the exception gets raised we know that the
    # policy was actually propagated all the way to feedparser.
    kundi MyPolicy(email.policy.Policy):
        eleza badmethod(self, *args, **kw):
             ashiria TestException("test")
        fold = fold_binary = header_fetch_parser = badmethod
        header_source_parse = header_store_parse = badmethod

    eleza test_message_from_string(self):
        ukijumuisha self.assertRaisesRegex(TestException, "^test$"):
            email.message_from_string("Subject: test\n\n",
                                      policy=self.MyPolicy)

    eleza test_message_from_bytes(self):
        ukijumuisha self.assertRaisesRegex(TestException, "^test$"):
            email.message_from_bytes(b"Subject: test\n\n",
                                     policy=self.MyPolicy)

    eleza test_message_from_file(self):
        f = io.StringIO('Subject: test\n\n')
        ukijumuisha self.assertRaisesRegex(TestException, "^test$"):
            email.message_from_file(f, policy=self.MyPolicy)

    eleza test_message_from_binary_file(self):
        f = io.BytesIO(b'Subject: test\n\n')
        ukijumuisha self.assertRaisesRegex(TestException, "^test$"):
            email.message_from_binary_file(f, policy=self.MyPolicy)

    # These are redundant, but we need them kila black-box completeness.

    eleza test_parser(self):
        p = email.parser.Parser(policy=self.MyPolicy)
        ukijumuisha self.assertRaisesRegex(TestException, "^test$"):
            p.parsestr('Subject: test\n\n')

    eleza test_bytes_parser(self):
        p = email.parser.BytesParser(policy=self.MyPolicy)
        ukijumuisha self.assertRaisesRegex(TestException, "^test$"):
            p.parsebytes(b'Subject: test\n\n')

    # Now that we've established that all the parse methods get the
    # policy kwenye to feedparser, we can use message_from_string for
    # the rest of the propagation tests.

    eleza _make_msg(self, source='Subject: test\n\n', policy=Tupu):
        self.policy = email.policy.default.clone() ikiwa policy ni Tupu isipokua policy
        rudisha email.message_from_string(source, policy=self.policy)

    eleza test_parser_propagates_policy_to_message(self):
        msg = self._make_msg()
        self.assertIs(msg.policy, self.policy)

    eleza test_parser_propagates_policy_to_sub_messages(self):
        msg = self._make_msg(textwrap.dedent("""\
            Subject: mime test
            MIME-Version: 1.0
            Content-Type: multipart/mixed, boundary="XXX"

            --XXX
            Content-Type: text/plain

            test
            --XXX
            Content-Type: text/plain

            test2
            --XXX--
            """))
        kila part kwenye msg.walk():
            self.assertIs(part.policy, self.policy)

    eleza test_message_policy_propagates_to_generator(self):
        msg = self._make_msg("Subject: test\nTo: foo\n\n",
                             policy=email.policy.default.clone(linesep='X'))
        s = io.StringIO()
        g = email.generator.Generator(s)
        g.flatten(msg)
        self.assertEqual(s.getvalue(), "Subject: testXTo: fooXX")

    eleza test_message_policy_used_by_as_string(self):
        msg = self._make_msg("Subject: test\nTo: foo\n\n",
                             policy=email.policy.default.clone(linesep='X'))
        self.assertEqual(msg.as_string(), "Subject: testXTo: fooXX")


kundi TestConcretePolicies(unittest.TestCase):

    eleza test_header_store_parse_rejects_newlines(self):
        instance = email.policy.EmailPolicy()
        self.assertRaises(ValueError,
                          instance.header_store_parse,
                          'From', 'spam\negg@foo.py')


ikiwa __name__ == '__main__':
    unittest.main()
