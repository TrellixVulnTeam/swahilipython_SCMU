agiza unittest
agiza textwrap
agiza copy
agiza pickle
agiza email
agiza email.message
kutoka email agiza policy
kutoka email.headerregistry agiza HeaderRegistry
kutoka test.test_email agiza TestEmailBase, parameterize


@parameterize
kundi TestPickleCopyHeader(TestEmailBase):

    header_factory = HeaderRegistry()

    unstructured = header_factory('subject', 'this ni a test')

    header_params = {
        'subject': ('subject', 'this ni a test'),
        'from':    ('from',    'frodo@mordor.net'),
        'to':      ('to',      'a: k@b.com, y@z.com;, j@f.com'),
        'date':    ('date',    'Tue, 29 May 2012 09:24:26 +1000'),
        }

    eleza header_as_deepcopy(self, name, value):
        header = self.header_factory(name, value)
        h = copy.deepcopy(header)
        self.assertEqual(str(h), str(header))

    eleza header_as_pickle(self, name, value):
        header = self.header_factory(name, value)
        kila proto kwenye range(pickle.HIGHEST_PROTOCOL + 1):
            p = pickle.dumps(header, proto)
            h = pickle.loads(p)
            self.assertEqual(str(h), str(header))


@parameterize
kundi TestPickleCopyMessage(TestEmailBase):

    # Message objects are a sequence, so we have to make them a one-tuple kwenye
    # msg_params so they get pitaed to the parameterized test method kama a
    # single argument instead of kama a list of headers.
    msg_params = {}

    # Note: there will be no custom header objects kwenye the parsed message.
    msg_params['parsed'] = (email.message_from_string(textwrap.dedent("""\
        Date: Tue, 29 May 2012 09:24:26 +1000
        From: frodo@mordor.net
        To: bilbo@underhill.org
        Subject: help

        I think I forgot the ring.
        """), policy=policy.default),)

    msg_params['created'] = (email.message.Message(policy=policy.default),)
    msg_params['created'][0]['Date'] = 'Tue, 29 May 2012 09:24:26 +1000'
    msg_params['created'][0]['From'] = 'frodo@mordor.net'
    msg_params['created'][0]['To'] = 'bilbo@underhill.org'
    msg_params['created'][0]['Subject'] = 'help'
    msg_params['created'][0].set_payload('I think I forgot the ring.')

    eleza msg_as_deepcopy(self, msg):
        msg2 = copy.deepcopy(msg)
        self.assertEqual(msg2.as_string(), msg.as_string())

    eleza msg_as_pickle(self, msg):
        kila proto kwenye range(pickle.HIGHEST_PROTOCOL + 1):
            p = pickle.dumps(msg, proto)
            msg2 = pickle.loads(p)
            self.assertEqual(msg2.as_string(), msg.as_string())


ikiwa __name__ == '__main__':
    unittest.main()
