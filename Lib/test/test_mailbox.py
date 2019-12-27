agiza os
agiza sys
agiza time
agiza stat
agiza socket
agiza email
agiza email.message
agiza re
agiza io
agiza tempfile
kutoka test agiza support
agiza unittest
agiza textwrap
agiza mailbox
agiza glob


kundi TestBase:

    all_mailbox_types = (mailbox.Message, mailbox.MaildirMessage,
                         mailbox.mboxMessage, mailbox.MHMessage,
                         mailbox.BabylMessage, mailbox.MMDFMessage)

    eleza _check_sample(self, msg):
        # Inspect a mailbox.Message representation of the sample message
        self.assertIsInstance(msg, email.message.Message)
        self.assertIsInstance(msg, mailbox.Message)
        for key, value in _sample_headers.items():
            self.assertIn(value, msg.get_all(key))
        self.assertTrue(msg.is_multipart())
        self.assertEqual(len(msg.get_payload()), len(_sample_payloads))
        for i, payload in enumerate(_sample_payloads):
            part = msg.get_payload(i)
            self.assertIsInstance(part, email.message.Message)
            self.assertNotIsInstance(part, mailbox.Message)
            self.assertEqual(part.get_payload(), payload)

    eleza _delete_recursively(self, target):
        # Delete a file or delete a directory recursively
        ikiwa os.path.isdir(target):
            support.rmtree(target)
        elikiwa os.path.exists(target):
            support.unlink(target)


kundi TestMailbox(TestBase):

    maxDiff = None

    _factory = None     # Overridden by subclasses to reuse tests
    _template = 'From: foo\n\n%s\n'

    eleza setUp(self):
        self._path = support.TESTFN
        self._delete_recursively(self._path)
        self._box = self._factory(self._path)

    eleza tearDown(self):
        self._box.close()
        self._delete_recursively(self._path)

    eleza test_add(self):
        # Add copies of a sample message
        keys = []
        keys.append(self._box.add(self._template % 0))
        self.assertEqual(len(self._box), 1)
        keys.append(self._box.add(mailbox.Message(_sample_message)))
        self.assertEqual(len(self._box), 2)
        keys.append(self._box.add(email.message_kutoka_string(_sample_message)))
        self.assertEqual(len(self._box), 3)
        keys.append(self._box.add(io.BytesIO(_bytes_sample_message)))
        self.assertEqual(len(self._box), 4)
        keys.append(self._box.add(_sample_message))
        self.assertEqual(len(self._box), 5)
        keys.append(self._box.add(_bytes_sample_message))
        self.assertEqual(len(self._box), 6)
        with self.assertWarns(DeprecationWarning):
            keys.append(self._box.add(
                io.TextIOWrapper(io.BytesIO(_bytes_sample_message))))
        self.assertEqual(len(self._box), 7)
        self.assertEqual(self._box.get_string(keys[0]), self._template % 0)
        for i in (1, 2, 3, 4, 5, 6):
            self._check_sample(self._box[keys[i]])

    _nonascii_msg = textwrap.dedent("""\
            From: foo
            Subject: Falinaptár házhozszállítással. Már rendeltél?

            0
            """)

    eleza test_add_invalid_8bit_bytes_header(self):
        key = self._box.add(self._nonascii_msg.encode('latin-1'))
        self.assertEqual(len(self._box), 1)
        self.assertEqual(self._box.get_bytes(key),
            self._nonascii_msg.encode('latin-1'))

    eleza test_invalid_nonascii_header_as_string(self):
        subj = self._nonascii_msg.splitlines()[1]
        key = self._box.add(subj.encode('latin-1'))
        self.assertEqual(self._box.get_string(key),
            'Subject: =?unknown-8bit?b?RmFsaW5hcHThciBo4Xpob3pzeuFsbO104XNz'
            'YWwuIE3hciByZW5kZWx06Ww/?=\n\n')

    eleza test_add_nonascii_string_header_raises(self):
        with self.assertRaisesRegex(ValueError, "ASCII-only"):
            self._box.add(self._nonascii_msg)
        self._box.flush()
        self.assertEqual(len(self._box), 0)
        self.assertMailboxEmpty()

    eleza test_add_that_raises_leaves_mailbox_empty(self):
        eleza raiser(*args, **kw):
            raise Exception("a fake error")
        support.patch(self, email.generator.BytesGenerator, 'flatten', raiser)
        with self.assertRaises(Exception):
            self._box.add(email.message_kutoka_string("From: Alphöso"))
        self.assertEqual(len(self._box), 0)
        self._box.close()
        self.assertMailboxEmpty()

    _non_latin_bin_msg = textwrap.dedent("""\
        From: foo@bar.com
        To: báz
        Subject: Maintenant je vous présente mon collègue, le pouf célèbre
        \tJean de Baddie
        Mime-Version: 1.0
        Content-Type: text/plain; charset="utf-8"
        Content-Transfer-Encoding: 8bit

        Да, они летят.
        """).encode('utf-8')

    eleza test_add_8bit_body(self):
        key = self._box.add(self._non_latin_bin_msg)
        self.assertEqual(self._box.get_bytes(key),
                         self._non_latin_bin_msg)
        with self._box.get_file(key) as f:
            self.assertEqual(f.read(),
                             self._non_latin_bin_msg.replace(b'\n',
                                os.linesep.encode()))
        self.assertEqual(self._box[key].get_payload(),
                        "Да, они летят.\n")

    eleza test_add_binary_file(self):
        with tempfile.TemporaryFile('wb+') as f:
            f.write(_bytes_sample_message)
            f.seek(0)
            key = self._box.add(f)
        self.assertEqual(self._box.get_bytes(key).split(b'\n'),
            _bytes_sample_message.split(b'\n'))

    eleza test_add_binary_nonascii_file(self):
        with tempfile.TemporaryFile('wb+') as f:
            f.write(self._non_latin_bin_msg)
            f.seek(0)
            key = self._box.add(f)
        self.assertEqual(self._box.get_bytes(key).split(b'\n'),
            self._non_latin_bin_msg.split(b'\n'))

    eleza test_add_text_file_warns(self):
        with tempfile.TemporaryFile('w+') as f:
            f.write(_sample_message)
            f.seek(0)
            with self.assertWarns(DeprecationWarning):
                key = self._box.add(f)
        self.assertEqual(self._box.get_bytes(key).split(b'\n'),
            _bytes_sample_message.split(b'\n'))

    eleza test_add_StringIO_warns(self):
        with self.assertWarns(DeprecationWarning):
            key = self._box.add(io.StringIO(self._template % "0"))
        self.assertEqual(self._box.get_string(key), self._template % "0")

    eleza test_add_nonascii_StringIO_raises(self):
        with self.assertWarns(DeprecationWarning):
            with self.assertRaisesRegex(ValueError, "ASCII-only"):
                self._box.add(io.StringIO(self._nonascii_msg))
        self.assertEqual(len(self._box), 0)
        self._box.close()
        self.assertMailboxEmpty()

    eleza test_remove(self):
        # Remove messages using remove()
        self._test_remove_or_delitem(self._box.remove)

    eleza test_delitem(self):
        # Remove messages using __delitem__()
        self._test_remove_or_delitem(self._box.__delitem__)

    eleza _test_remove_or_delitem(self, method):
        # (Used by test_remove() and test_delitem().)
        key0 = self._box.add(self._template % 0)
        key1 = self._box.add(self._template % 1)
        self.assertEqual(len(self._box), 2)
        method(key0)
        self.assertEqual(len(self._box), 1)
        self.assertRaises(KeyError, lambda: self._box[key0])
        self.assertRaises(KeyError, lambda: method(key0))
        self.assertEqual(self._box.get_string(key1), self._template % 1)
        key2 = self._box.add(self._template % 2)
        self.assertEqual(len(self._box), 2)
        method(key2)
        self.assertEqual(len(self._box), 1)
        self.assertRaises(KeyError, lambda: self._box[key2])
        self.assertRaises(KeyError, lambda: method(key2))
        self.assertEqual(self._box.get_string(key1), self._template % 1)
        method(key1)
        self.assertEqual(len(self._box), 0)
        self.assertRaises(KeyError, lambda: self._box[key1])
        self.assertRaises(KeyError, lambda: method(key1))

    eleza test_discard(self, repetitions=10):
        # Discard messages
        key0 = self._box.add(self._template % 0)
        key1 = self._box.add(self._template % 1)
        self.assertEqual(len(self._box), 2)
        self._box.discard(key0)
        self.assertEqual(len(self._box), 1)
        self.assertRaises(KeyError, lambda: self._box[key0])
        self._box.discard(key0)
        self.assertEqual(len(self._box), 1)
        self.assertRaises(KeyError, lambda: self._box[key0])

    eleza test_get(self):
        # Retrieve messages using get()
        key0 = self._box.add(self._template % 0)
        msg = self._box.get(key0)
        self.assertEqual(msg['kutoka'], 'foo')
        self.assertEqual(msg.get_payload(), '0\n')
        self.assertIsNone(self._box.get('foo'))
        self.assertIs(self._box.get('foo', False), False)
        self._box.close()
        self._box = self._factory(self._path)
        key1 = self._box.add(self._template % 1)
        msg = self._box.get(key1)
        self.assertEqual(msg['kutoka'], 'foo')
        self.assertEqual(msg.get_payload(), '1\n')

    eleza test_getitem(self):
        # Retrieve message using __getitem__()
        key0 = self._box.add(self._template % 0)
        msg = self._box[key0]
        self.assertEqual(msg['kutoka'], 'foo')
        self.assertEqual(msg.get_payload(), '0\n')
        self.assertRaises(KeyError, lambda: self._box['foo'])
        self._box.discard(key0)
        self.assertRaises(KeyError, lambda: self._box[key0])

    eleza test_get_message(self):
        # Get Message representations of messages
        key0 = self._box.add(self._template % 0)
        key1 = self._box.add(_sample_message)
        msg0 = self._box.get_message(key0)
        self.assertIsInstance(msg0, mailbox.Message)
        self.assertEqual(msg0['kutoka'], 'foo')
        self.assertEqual(msg0.get_payload(), '0\n')
        self._check_sample(self._box.get_message(key1))

    eleza test_get_bytes(self):
        # Get bytes representations of messages
        key0 = self._box.add(self._template % 0)
        key1 = self._box.add(_sample_message)
        self.assertEqual(self._box.get_bytes(key0),
            (self._template % 0).encode('ascii'))
        self.assertEqual(self._box.get_bytes(key1), _bytes_sample_message)

    eleza test_get_string(self):
        # Get string representations of messages
        key0 = self._box.add(self._template % 0)
        key1 = self._box.add(_sample_message)
        self.assertEqual(self._box.get_string(key0), self._template % 0)
        self.assertEqual(self._box.get_string(key1).split('\n'),
                         _sample_message.split('\n'))

    eleza test_get_file(self):
        # Get file representations of messages
        key0 = self._box.add(self._template % 0)
        key1 = self._box.add(_sample_message)
        with self._box.get_file(key0) as file:
            data0 = file.read()
        with self._box.get_file(key1) as file:
            data1 = file.read()
        self.assertEqual(data0.decode('ascii').replace(os.linesep, '\n'),
                         self._template % 0)
        self.assertEqual(data1.decode('ascii').replace(os.linesep, '\n'),
                         _sample_message)

    eleza test_get_file_can_be_closed_twice(self):
        # Issue 11700
        key = self._box.add(_sample_message)
        f = self._box.get_file(key)
        f.close()
        f.close()

    eleza test_iterkeys(self):
        # Get keys using iterkeys()
        self._check_iteration(self._box.iterkeys, do_keys=True, do_values=False)

    eleza test_keys(self):
        # Get keys using keys()
        self._check_iteration(self._box.keys, do_keys=True, do_values=False)

    eleza test_itervalues(self):
        # Get values using itervalues()
        self._check_iteration(self._box.itervalues, do_keys=False,
                              do_values=True)

    eleza test_iter(self):
        # Get values using __iter__()
        self._check_iteration(self._box.__iter__, do_keys=False,
                              do_values=True)

    eleza test_values(self):
        # Get values using values()
        self._check_iteration(self._box.values, do_keys=False, do_values=True)

    eleza test_iteritems(self):
        # Get keys and values using iteritems()
        self._check_iteration(self._box.iteritems, do_keys=True,
                              do_values=True)

    eleza test_items(self):
        # Get keys and values using items()
        self._check_iteration(self._box.items, do_keys=True, do_values=True)

    eleza _check_iteration(self, method, do_keys, do_values, repetitions=10):
        for value in method():
            self.fail("Not empty")
        keys, values = [], []
        for i in range(repetitions):
            keys.append(self._box.add(self._template % i))
            values.append(self._template % i)
        ikiwa do_keys and not do_values:
            returned_keys = list(method())
        elikiwa do_values and not do_keys:
            returned_values = list(method())
        else:
            returned_keys, returned_values = [], []
            for key, value in method():
                returned_keys.append(key)
                returned_values.append(value)
        ikiwa do_keys:
            self.assertEqual(len(keys), len(returned_keys))
            self.assertEqual(set(keys), set(returned_keys))
        ikiwa do_values:
            count = 0
            for value in returned_values:
                self.assertEqual(value['kutoka'], 'foo')
                self.assertLess(int(value.get_payload()), repetitions)
                count += 1
            self.assertEqual(len(values), count)

    eleza test_contains(self):
        # Check existence of keys using __contains__()
        self.assertNotIn('foo', self._box)
        key0 = self._box.add(self._template % 0)
        self.assertIn(key0, self._box)
        self.assertNotIn('foo', self._box)
        key1 = self._box.add(self._template % 1)
        self.assertIn(key1, self._box)
        self.assertIn(key0, self._box)
        self.assertNotIn('foo', self._box)
        self._box.remove(key0)
        self.assertNotIn(key0, self._box)
        self.assertIn(key1, self._box)
        self.assertNotIn('foo', self._box)
        self._box.remove(key1)
        self.assertNotIn(key1, self._box)
        self.assertNotIn(key0, self._box)
        self.assertNotIn('foo', self._box)

    eleza test_len(self, repetitions=10):
        # Get message count
        keys = []
        for i in range(repetitions):
            self.assertEqual(len(self._box), i)
            keys.append(self._box.add(self._template % i))
            self.assertEqual(len(self._box), i + 1)
        for i in range(repetitions):
            self.assertEqual(len(self._box), repetitions - i)
            self._box.remove(keys[i])
            self.assertEqual(len(self._box), repetitions - i - 1)

    eleza test_set_item(self):
        # Modify messages using __setitem__()
        key0 = self._box.add(self._template % 'original 0')
        self.assertEqual(self._box.get_string(key0),
                         self._template % 'original 0')
        key1 = self._box.add(self._template % 'original 1')
        self.assertEqual(self._box.get_string(key1),
                         self._template % 'original 1')
        self._box[key0] = self._template % 'changed 0'
        self.assertEqual(self._box.get_string(key0),
                         self._template % 'changed 0')
        self._box[key1] = self._template % 'changed 1'
        self.assertEqual(self._box.get_string(key1),
                         self._template % 'changed 1')
        self._box[key0] = _sample_message
        self._check_sample(self._box[key0])
        self._box[key1] = self._box[key0]
        self._check_sample(self._box[key1])
        self._box[key0] = self._template % 'original 0'
        self.assertEqual(self._box.get_string(key0),
                     self._template % 'original 0')
        self._check_sample(self._box[key1])
        self.assertRaises(KeyError,
                          lambda: self._box.__setitem__('foo', 'bar'))
        self.assertRaises(KeyError, lambda: self._box['foo'])
        self.assertEqual(len(self._box), 2)

    eleza test_clear(self, iterations=10):
        # Remove all messages using clear()
        keys = []
        for i in range(iterations):
            self._box.add(self._template % i)
        for i, key in enumerate(keys):
            self.assertEqual(self._box.get_string(key), self._template % i)
        self._box.clear()
        self.assertEqual(len(self._box), 0)
        for i, key in enumerate(keys):
            self.assertRaises(KeyError, lambda: self._box.get_string(key))

    eleza test_pop(self):
        # Get and remove a message using pop()
        key0 = self._box.add(self._template % 0)
        self.assertIn(key0, self._box)
        key1 = self._box.add(self._template % 1)
        self.assertIn(key1, self._box)
        self.assertEqual(self._box.pop(key0).get_payload(), '0\n')
        self.assertNotIn(key0, self._box)
        self.assertIn(key1, self._box)
        key2 = self._box.add(self._template % 2)
        self.assertIn(key2, self._box)
        self.assertEqual(self._box.pop(key2).get_payload(), '2\n')
        self.assertNotIn(key2, self._box)
        self.assertIn(key1, self._box)
        self.assertEqual(self._box.pop(key1).get_payload(), '1\n')
        self.assertNotIn(key1, self._box)
        self.assertEqual(len(self._box), 0)

    eleza test_popitem(self, iterations=10):
        # Get and remove an arbitrary (key, message) using popitem()
        keys = []
        for i in range(10):
            keys.append(self._box.add(self._template % i))
        seen = []
        for i in range(10):
            key, msg = self._box.popitem()
            self.assertIn(key, keys)
            self.assertNotIn(key, seen)
            seen.append(key)
            self.assertEqual(int(msg.get_payload()), keys.index(key))
        self.assertEqual(len(self._box), 0)
        for key in keys:
            self.assertRaises(KeyError, lambda: self._box[key])

    eleza test_update(self):
        # Modify multiple messages using update()
        key0 = self._box.add(self._template % 'original 0')
        key1 = self._box.add(self._template % 'original 1')
        key2 = self._box.add(self._template % 'original 2')
        self._box.update({key0: self._template % 'changed 0',
                          key2: _sample_message})
        self.assertEqual(len(self._box), 3)
        self.assertEqual(self._box.get_string(key0),
                     self._template % 'changed 0')
        self.assertEqual(self._box.get_string(key1),
                     self._template % 'original 1')
        self._check_sample(self._box[key2])
        self._box.update([(key2, self._template % 'changed 2'),
                    (key1, self._template % 'changed 1'),
                    (key0, self._template % 'original 0')])
        self.assertEqual(len(self._box), 3)
        self.assertEqual(self._box.get_string(key0),
                     self._template % 'original 0')
        self.assertEqual(self._box.get_string(key1),
                     self._template % 'changed 1')
        self.assertEqual(self._box.get_string(key2),
                     self._template % 'changed 2')
        self.assertRaises(KeyError,
                          lambda: self._box.update({'foo': 'bar',
                                          key0: self._template % "changed 0"}))
        self.assertEqual(len(self._box), 3)
        self.assertEqual(self._box.get_string(key0),
                     self._template % "changed 0")
        self.assertEqual(self._box.get_string(key1),
                     self._template % "changed 1")
        self.assertEqual(self._box.get_string(key2),
                     self._template % "changed 2")

    eleza test_flush(self):
        # Write changes to disk
        self._test_flush_or_close(self._box.flush, True)

    eleza test_popitem_and_flush_twice(self):
        # See #15036.
        self._box.add(self._template % 0)
        self._box.add(self._template % 1)
        self._box.flush()

        self._box.popitem()
        self._box.flush()
        self._box.popitem()
        self._box.flush()

    eleza test_lock_unlock(self):
        # Lock and unlock the mailbox
        self.assertFalse(os.path.exists(self._get_lock_path()))
        self._box.lock()
        self.assertTrue(os.path.exists(self._get_lock_path()))
        self._box.unlock()
        self.assertFalse(os.path.exists(self._get_lock_path()))

    eleza test_close(self):
        # Close mailbox and flush changes to disk
        self._test_flush_or_close(self._box.close, False)

    eleza _test_flush_or_close(self, method, should_call_close):
        contents = [self._template % i for i in range(3)]
        self._box.add(contents[0])
        self._box.add(contents[1])
        self._box.add(contents[2])
        oldbox = self._box
        method()
        ikiwa should_call_close:
            self._box.close()
        self._box = self._factory(self._path)
        keys = self._box.keys()
        self.assertEqual(len(keys), 3)
        for key in keys:
            self.assertIn(self._box.get_string(key), contents)
        oldbox.close()

    eleza test_dump_message(self):
        # Write message representations to disk
        for input in (email.message_kutoka_string(_sample_message),
                      _sample_message, io.BytesIO(_bytes_sample_message)):
            output = io.BytesIO()
            self._box._dump_message(input, output)
            self.assertEqual(output.getvalue(),
                _bytes_sample_message.replace(b'\n', os.linesep.encode()))
        output = io.BytesIO()
        self.assertRaises(TypeError,
                          lambda: self._box._dump_message(None, output))

    eleza _get_lock_path(self):
        # Return the path of the dot lock file. May be overridden.
        rudisha self._path + '.lock'


kundi TestMailboxSuperclass(TestBase, unittest.TestCase):

    eleza test_notimplemented(self):
        # Test that all Mailbox methods raise NotImplementedException.
        box = mailbox.Mailbox('path')
        self.assertRaises(NotImplementedError, lambda: box.add(''))
        self.assertRaises(NotImplementedError, lambda: box.remove(''))
        self.assertRaises(NotImplementedError, lambda: box.__delitem__(''))
        self.assertRaises(NotImplementedError, lambda: box.discard(''))
        self.assertRaises(NotImplementedError, lambda: box.__setitem__('', ''))
        self.assertRaises(NotImplementedError, lambda: box.iterkeys())
        self.assertRaises(NotImplementedError, lambda: box.keys())
        self.assertRaises(NotImplementedError, lambda: box.itervalues().__next__())
        self.assertRaises(NotImplementedError, lambda: box.__iter__().__next__())
        self.assertRaises(NotImplementedError, lambda: box.values())
        self.assertRaises(NotImplementedError, lambda: box.iteritems().__next__())
        self.assertRaises(NotImplementedError, lambda: box.items())
        self.assertRaises(NotImplementedError, lambda: box.get(''))
        self.assertRaises(NotImplementedError, lambda: box.__getitem__(''))
        self.assertRaises(NotImplementedError, lambda: box.get_message(''))
        self.assertRaises(NotImplementedError, lambda: box.get_string(''))
        self.assertRaises(NotImplementedError, lambda: box.get_bytes(''))
        self.assertRaises(NotImplementedError, lambda: box.get_file(''))
        self.assertRaises(NotImplementedError, lambda: '' in box)
        self.assertRaises(NotImplementedError, lambda: box.__contains__(''))
        self.assertRaises(NotImplementedError, lambda: box.__len__())
        self.assertRaises(NotImplementedError, lambda: box.clear())
        self.assertRaises(NotImplementedError, lambda: box.pop(''))
        self.assertRaises(NotImplementedError, lambda: box.popitem())
        self.assertRaises(NotImplementedError, lambda: box.update((('', ''),)))
        self.assertRaises(NotImplementedError, lambda: box.flush())
        self.assertRaises(NotImplementedError, lambda: box.lock())
        self.assertRaises(NotImplementedError, lambda: box.unlock())
        self.assertRaises(NotImplementedError, lambda: box.close())


kundi TestMaildir(TestMailbox, unittest.TestCase):

    _factory = lambda self, path, factory=None: mailbox.Maildir(path, factory)

    eleza setUp(self):
        TestMailbox.setUp(self)
        ikiwa (os.name == 'nt') or (sys.platform == 'cygwin'):
            self._box.colon = '!'

    eleza assertMailboxEmpty(self):
        self.assertEqual(os.listdir(os.path.join(self._path, 'tmp')), [])

    eleza test_add_MM(self):
        # Add a MaildirMessage instance
        msg = mailbox.MaildirMessage(self._template % 0)
        msg.set_subdir('cur')
        msg.set_info('foo')
        key = self._box.add(msg)
        self.assertTrue(os.path.exists(os.path.join(self._path, 'cur', '%s%sfoo' %
                                                 (key, self._box.colon))))

    eleza test_get_MM(self):
        # Get a MaildirMessage instance
        msg = mailbox.MaildirMessage(self._template % 0)
        msg.set_subdir('cur')
        msg.set_flags('RF')
        key = self._box.add(msg)
        msg_returned = self._box.get_message(key)
        self.assertIsInstance(msg_returned, mailbox.MaildirMessage)
        self.assertEqual(msg_returned.get_subdir(), 'cur')
        self.assertEqual(msg_returned.get_flags(), 'FR')

    eleza test_set_MM(self):
        # Set with a MaildirMessage instance
        msg0 = mailbox.MaildirMessage(self._template % 0)
        msg0.set_flags('TP')
        key = self._box.add(msg0)
        msg_returned = self._box.get_message(key)
        self.assertEqual(msg_returned.get_subdir(), 'new')
        self.assertEqual(msg_returned.get_flags(), 'PT')
        msg1 = mailbox.MaildirMessage(self._template % 1)
        self._box[key] = msg1
        msg_returned = self._box.get_message(key)
        self.assertEqual(msg_returned.get_subdir(), 'new')
        self.assertEqual(msg_returned.get_flags(), '')
        self.assertEqual(msg_returned.get_payload(), '1\n')
        msg2 = mailbox.MaildirMessage(self._template % 2)
        msg2.set_info('2,S')
        self._box[key] = msg2
        self._box[key] = self._template % 3
        msg_returned = self._box.get_message(key)
        self.assertEqual(msg_returned.get_subdir(), 'new')
        self.assertEqual(msg_returned.get_flags(), 'S')
        self.assertEqual(msg_returned.get_payload(), '3\n')

    eleza test_consistent_factory(self):
        # Add a message.
        msg = mailbox.MaildirMessage(self._template % 0)
        msg.set_subdir('cur')
        msg.set_flags('RF')
        key = self._box.add(msg)

        # Create new mailbox with
        kundi FakeMessage(mailbox.MaildirMessage):
            pass
        box = mailbox.Maildir(self._path, factory=FakeMessage)
        box.colon = self._box.colon
        msg2 = box.get_message(key)
        self.assertIsInstance(msg2, FakeMessage)

    eleza test_initialize_new(self):
        # Initialize a non-existent mailbox
        self.tearDown()
        self._box = mailbox.Maildir(self._path)
        self._check_basics()
        self._delete_recursively(self._path)
        self._box = self._factory(self._path, factory=None)
        self._check_basics()

    eleza test_initialize_existing(self):
        # Initialize an existing mailbox
        self.tearDown()
        for subdir in '', 'tmp', 'new', 'cur':
            os.mkdir(os.path.normpath(os.path.join(self._path, subdir)))
        self._box = mailbox.Maildir(self._path)
        self._check_basics()

    eleza _check_basics(self, factory=None):
        # (Used by test_open_new() and test_open_existing().)
        self.assertEqual(self._box._path, os.path.abspath(self._path))
        self.assertEqual(self._box._factory, factory)
        for subdir in '', 'tmp', 'new', 'cur':
            path = os.path.join(self._path, subdir)
            mode = os.stat(path)[stat.ST_MODE]
            self.assertTrue(stat.S_ISDIR(mode), "Not a directory: '%s'" % path)

    eleza test_list_folders(self):
        # List folders
        self._box.add_folder('one')
        self._box.add_folder('two')
        self._box.add_folder('three')
        self.assertEqual(len(self._box.list_folders()), 3)
        self.assertEqual(set(self._box.list_folders()),
                     set(('one', 'two', 'three')))

    eleza test_get_folder(self):
        # Open folders
        self._box.add_folder('foo.bar')
        folder0 = self._box.get_folder('foo.bar')
        folder0.add(self._template % 'bar')
        self.assertTrue(os.path.isdir(os.path.join(self._path, '.foo.bar')))
        folder1 = self._box.get_folder('foo.bar')
        self.assertEqual(folder1.get_string(folder1.keys()[0]),
                         self._template % 'bar')

    eleza test_add_and_remove_folders(self):
        # Delete folders
        self._box.add_folder('one')
        self._box.add_folder('two')
        self.assertEqual(len(self._box.list_folders()), 2)
        self.assertEqual(set(self._box.list_folders()), set(('one', 'two')))
        self._box.remove_folder('one')
        self.assertEqual(len(self._box.list_folders()), 1)
        self.assertEqual(set(self._box.list_folders()), set(('two',)))
        self._box.add_folder('three')
        self.assertEqual(len(self._box.list_folders()), 2)
        self.assertEqual(set(self._box.list_folders()), set(('two', 'three')))
        self._box.remove_folder('three')
        self.assertEqual(len(self._box.list_folders()), 1)
        self.assertEqual(set(self._box.list_folders()), set(('two',)))
        self._box.remove_folder('two')
        self.assertEqual(len(self._box.list_folders()), 0)
        self.assertEqual(self._box.list_folders(), [])

    eleza test_clean(self):
        # Remove old files kutoka 'tmp'
        foo_path = os.path.join(self._path, 'tmp', 'foo')
        bar_path = os.path.join(self._path, 'tmp', 'bar')
        with open(foo_path, 'w') as f:
            f.write("@")
        with open(bar_path, 'w') as f:
            f.write("@")
        self._box.clean()
        self.assertTrue(os.path.exists(foo_path))
        self.assertTrue(os.path.exists(bar_path))
        foo_stat = os.stat(foo_path)
        os.utime(foo_path, (time.time() - 129600 - 2,
                            foo_stat.st_mtime))
        self._box.clean()
        self.assertFalse(os.path.exists(foo_path))
        self.assertTrue(os.path.exists(bar_path))

    eleza test_create_tmp(self, repetitions=10):
        # Create files in tmp directory
        hostname = socket.gethostname()
        ikiwa '/' in hostname:
            hostname = hostname.replace('/', r'\057')
        ikiwa ':' in hostname:
            hostname = hostname.replace(':', r'\072')
        pid = os.getpid()
        pattern = re.compile(r"(?P<time>\d+)\.M(?P<M>\d{1,6})P(?P<P>\d+)"
                             r"Q(?P<Q>\d+)\.(?P<host>[^:/]*)")
        previous_groups = None
        for x in range(repetitions):
            tmp_file = self._box._create_tmp()
            head, tail = os.path.split(tmp_file.name)
            self.assertEqual(head, os.path.abspath(os.path.join(self._path,
                                                                "tmp")),
                             "File in wrong location: '%s'" % head)
            match = pattern.match(tail)
            self.assertIsNotNone(match, "Invalid file name: '%s'" % tail)
            groups = match.groups()
            ikiwa previous_groups is not None:
                self.assertGreaterEqual(int(groups[0]), int(previous_groups[0]),
                             "Non-monotonic seconds: '%s' before '%s'" %
                             (previous_groups[0], groups[0]))
                ikiwa int(groups[0]) == int(previous_groups[0]):
                    self.assertGreaterEqual(int(groups[1]), int(previous_groups[1]),
                                "Non-monotonic milliseconds: '%s' before '%s'" %
                                (previous_groups[1], groups[1]))
                self.assertEqual(int(groups[2]), pid,
                             "Process ID mismatch: '%s' should be '%s'" %
                             (groups[2], pid))
                self.assertEqual(int(groups[3]), int(previous_groups[3]) + 1,
                             "Non-sequential counter: '%s' before '%s'" %
                             (previous_groups[3], groups[3]))
                self.assertEqual(groups[4], hostname,
                             "Host name mismatch: '%s' should be '%s'" %
                             (groups[4], hostname))
            previous_groups = groups
            tmp_file.write(_bytes_sample_message)
            tmp_file.seek(0)
            self.assertEqual(tmp_file.read(), _bytes_sample_message)
            tmp_file.close()
        file_count = len(os.listdir(os.path.join(self._path, "tmp")))
        self.assertEqual(file_count, repetitions,
                     "Wrong file count: '%s' should be '%s'" %
                     (file_count, repetitions))

    eleza test_refresh(self):
        # Update the table of contents
        self.assertEqual(self._box._toc, {})
        key0 = self._box.add(self._template % 0)
        key1 = self._box.add(self._template % 1)
        self.assertEqual(self._box._toc, {})
        self._box._refresh()
        self.assertEqual(self._box._toc, {key0: os.path.join('new', key0),
                                          key1: os.path.join('new', key1)})
        key2 = self._box.add(self._template % 2)
        self.assertEqual(self._box._toc, {key0: os.path.join('new', key0),
                                          key1: os.path.join('new', key1)})
        self._box._refresh()
        self.assertEqual(self._box._toc, {key0: os.path.join('new', key0),
                                          key1: os.path.join('new', key1),
                                          key2: os.path.join('new', key2)})

    eleza test_refresh_after_safety_period(self):
        # Issue #13254: Call _refresh after the "file system safety
        # period" of 2 seconds has passed; _toc should still be
        # updated because this is the first call to _refresh.
        key0 = self._box.add(self._template % 0)
        key1 = self._box.add(self._template % 1)

        self._box = self._factory(self._path)
        self.assertEqual(self._box._toc, {})

        # Emulate sleeping. Instead of sleeping for 2 seconds, use the
        # skew factor to make _refresh think that the filesystem
        # safety period has passed and re-reading the _toc is only
        # required ikiwa mtimes differ.
        self._box._skewfactor = -3

        self._box._refresh()
        self.assertEqual(sorted(self._box._toc.keys()), sorted([key0, key1]))

    eleza test_lookup(self):
        # Look up message subpaths in the TOC
        self.assertRaises(KeyError, lambda: self._box._lookup('foo'))
        key0 = self._box.add(self._template % 0)
        self.assertEqual(self._box._lookup(key0), os.path.join('new', key0))
        os.remove(os.path.join(self._path, 'new', key0))
        self.assertEqual(self._box._toc, {key0: os.path.join('new', key0)})
        # Be sure that the TOC is read back kutoka disk (see issue #6896
        # about bad mtime behaviour on some systems).
        self._box.flush()
        self.assertRaises(KeyError, lambda: self._box._lookup(key0))
        self.assertEqual(self._box._toc, {})

    eleza test_lock_unlock(self):
        # Lock and unlock the mailbox. For Maildir, this does nothing.
        self._box.lock()
        self._box.unlock()

    eleza test_folder (self):
        # Test for bug #1569790: verify that folders returned by .get_folder()
        # use the same factory function.
        eleza dummy_factory (s):
            rudisha None
        box = self._factory(self._path, factory=dummy_factory)
        folder = box.add_folder('folder1')
        self.assertIs(folder._factory, dummy_factory)

        folder1_alias = box.get_folder('folder1')
        self.assertIs(folder1_alias._factory, dummy_factory)

    eleza test_directory_in_folder (self):
        # Test that mailboxes still work ikiwa there's a stray extra directory
        # in a folder.
        for i in range(10):
            self._box.add(mailbox.Message(_sample_message))

        # Create a stray directory
        os.mkdir(os.path.join(self._path, 'cur', 'stray-dir'))

        # Check that looping still works with the directory present.
        for msg in self._box:
            pass

    @unittest.skipUnless(hasattr(os, 'umask'), 'test needs os.umask()')
    eleza test_file_permissions(self):
        # Verify that message files are created without execute permissions
        msg = mailbox.MaildirMessage(self._template % 0)
        orig_umask = os.umask(0)
        try:
            key = self._box.add(msg)
        finally:
            os.umask(orig_umask)
        path = os.path.join(self._path, self._box._lookup(key))
        mode = os.stat(path).st_mode
        self.assertFalse(mode & 0o111)

    @unittest.skipUnless(hasattr(os, 'umask'), 'test needs os.umask()')
    eleza test_folder_file_perms(self):
        # From bug #3228, we want to verify that the file created inside a Maildir
        # subfolder isn't marked as executable.
        orig_umask = os.umask(0)
        try:
            subfolder = self._box.add_folder('subfolder')
        finally:
            os.umask(orig_umask)

        path = os.path.join(subfolder._path, 'maildirfolder')
        st = os.stat(path)
        perms = st.st_mode
        self.assertFalse((perms & 0o111)) # Execute bits should all be off.

    eleza test_reread(self):
        # Do an initial unconditional refresh
        self._box._refresh()

        # Put the last modified times more than two seconds into the past
        # (because mtime may have a two second granularity)
        for subdir in ('cur', 'new'):
            os.utime(os.path.join(self._box._path, subdir),
                     (time.time()-5,)*2)

        # Because mtime has a two second granularity in worst case (FAT), a
        # refresh is done unconditionally ikiwa called for within
        # two-second-plus-a-bit of the last one, just in case the mbox has
        # changed; so now we have to wait for that interval to expire.
        #
        # Because this is a test, emulate sleeping. Instead of
        # sleeping for 2 seconds, use the skew factor to make _refresh
        # think that 2 seconds have passed and re-reading the _toc is
        # only required ikiwa mtimes differ.
        self._box._skewfactor = -3

        # Re-reading causes the ._toc attribute to be assigned a new dictionary
        # object, so we'll check that the ._toc attribute isn't a different
        # object.
        orig_toc = self._box._toc
        eleza refreshed():
            rudisha self._box._toc is not orig_toc

        self._box._refresh()
        self.assertFalse(refreshed())

        # Now, write something into cur and remove it.  This changes
        # the mtime and should cause a re-read. Note that "sleep
        # emulation" is still in effect, as skewfactor is -3.
        filename = os.path.join(self._path, 'cur', 'stray-file')
        support.create_empty_file(filename)
        os.unlink(filename)
        self._box._refresh()
        self.assertTrue(refreshed())


kundi _TestSingleFile(TestMailbox):
    '''Common tests for single-file mailboxes'''

    eleza test_add_doesnt_rewrite(self):
        # When only adding messages, flush() should not rewrite the
        # mailbox file. See issue #9559.

        # Inode number changes ikiwa the contents are written to another
        # file which is then renamed over the original file. So we
        # must check that the inode number doesn't change.
        inode_before = os.stat(self._path).st_ino

        self._box.add(self._template % 0)
        self._box.flush()

        inode_after = os.stat(self._path).st_ino
        self.assertEqual(inode_before, inode_after)

        # Make sure the message was really added
        self._box.close()
        self._box = self._factory(self._path)
        self.assertEqual(len(self._box), 1)

    eleza test_permissions_after_flush(self):
        # See issue #5346

        # Make the mailbox world writable. It's unlikely that the new
        # mailbox file would have these permissions after flush(),
        # because umask usually prevents it.
        mode = os.stat(self._path).st_mode | 0o666
        os.chmod(self._path, mode)

        self._box.add(self._template % 0)
        i = self._box.add(self._template % 1)
        # Need to remove one message to make flush() create a new file
        self._box.remove(i)
        self._box.flush()

        self.assertEqual(os.stat(self._path).st_mode, mode)


kundi _TestMboxMMDF(_TestSingleFile):

    eleza tearDown(self):
        super().tearDown()
        self._box.close()
        self._delete_recursively(self._path)
        for lock_remnant in glob.glob(self._path + '.*'):
            support.unlink(lock_remnant)

    eleza assertMailboxEmpty(self):
        with open(self._path) as f:
            self.assertEqual(f.readlines(), [])

    eleza test_get_bytes_kutoka(self):
        # Get bytes representations of messages with _unixkutoka.
        unixkutoka = 'From foo@bar blah\n'
        key0 = self._box.add(unixkutoka + self._template % 0)
        key1 = self._box.add(unixkutoka + _sample_message)
        self.assertEqual(self._box.get_bytes(key0, kutoka_=False),
            (self._template % 0).encode('ascii'))
        self.assertEqual(self._box.get_bytes(key1, kutoka_=False),
            _bytes_sample_message)
        self.assertEqual(self._box.get_bytes(key0, kutoka_=True),
            (unixkutoka + self._template % 0).encode('ascii'))
        self.assertEqual(self._box.get_bytes(key1, kutoka_=True),
            unixkutoka.encode('ascii') + _bytes_sample_message)

    eleza test_get_string_kutoka(self):
        # Get string representations of messages with _unixkutoka.
        unixkutoka = 'From foo@bar blah\n'
        key0 = self._box.add(unixkutoka + self._template % 0)
        key1 = self._box.add(unixkutoka + _sample_message)
        self.assertEqual(self._box.get_string(key0, kutoka_=False),
                         self._template % 0)
        self.assertEqual(self._box.get_string(key1, kutoka_=False).split('\n'),
                         _sample_message.split('\n'))
        self.assertEqual(self._box.get_string(key0, kutoka_=True),
                         unixkutoka + self._template % 0)
        self.assertEqual(self._box.get_string(key1, kutoka_=True).split('\n'),
                         (unixkutoka + _sample_message).split('\n'))

    eleza test_add_kutoka_string(self):
        # Add a string starting with 'From ' to the mailbox
        key = self._box.add('From foo@bar blah\nFrom: foo\n\n0\n')
        self.assertEqual(self._box[key].get_kutoka(), 'foo@bar blah')
        self.assertEqual(self._box[key].get_payload(), '0\n')

    eleza test_add_kutoka_bytes(self):
        # Add a byte string starting with 'From ' to the mailbox
        key = self._box.add(b'From foo@bar blah\nFrom: foo\n\n0\n')
        self.assertEqual(self._box[key].get_kutoka(), 'foo@bar blah')
        self.assertEqual(self._box[key].get_payload(), '0\n')

    eleza test_add_mbox_or_mmdf_message(self):
        # Add an mboxMessage or MMDFMessage
        for class_ in (mailbox.mboxMessage, mailbox.MMDFMessage):
            msg = class_('From foo@bar blah\nFrom: foo\n\n0\n')
            key = self._box.add(msg)

    eleza test_open_close_open(self):
        # Open and inspect previously-created mailbox
        values = [self._template % i for i in range(3)]
        for value in values:
            self._box.add(value)
        self._box.close()
        mtime = os.path.getmtime(self._path)
        self._box = self._factory(self._path)
        self.assertEqual(len(self._box), 3)
        for key in self._box.iterkeys():
            self.assertIn(self._box.get_string(key), values)
        self._box.close()
        self.assertEqual(mtime, os.path.getmtime(self._path))

    eleza test_add_and_close(self):
        # Verifying that closing a mailbox doesn't change added items
        self._box.add(_sample_message)
        for i in range(3):
            self._box.add(self._template % i)
        self._box.add(_sample_message)
        self._box._file.flush()
        self._box._file.seek(0)
        contents = self._box._file.read()
        self._box.close()
        with open(self._path, 'rb') as f:
            self.assertEqual(contents, f.read())
        self._box = self._factory(self._path)

    @unittest.skipUnless(hasattr(os, 'fork'), "Test needs fork().")
    @unittest.skipUnless(hasattr(socket, 'socketpair'), "Test needs socketpair().")
    eleza test_lock_conflict(self):
        # Fork off a child process that will lock the mailbox temporarily,
        # unlock it and exit.
        c, p = socket.socketpair()
        self.addCleanup(c.close)
        self.addCleanup(p.close)

        pid = os.fork()
        ikiwa pid == 0:
            # child
            try:
                # lock the mailbox, and signal the parent it can proceed
                self._box.lock()
                c.send(b'c')

                # wait until the parent is done, and unlock the mailbox
                c.recv(1)
                self._box.unlock()
            finally:
                os._exit(0)

        # In the parent, wait until the child signals it locked the mailbox.
        p.recv(1)
        try:
            self.assertRaises(mailbox.ExternalClashError,
                              self._box.lock)
        finally:
            # Signal the child it can now release the lock and exit.
            p.send(b'p')
            # Wait for child to exit.  Locking should now succeed.
            exited_pid, status = os.waitpid(pid, 0)

        self._box.lock()
        self._box.unlock()

    eleza test_relock(self):
        # Test case for bug #1575506: the mailbox kundi was locking the
        # wrong file object in its flush() method.
        msg = "Subject: sub\n\nbody\n"
        key1 = self._box.add(msg)
        self._box.flush()
        self._box.close()

        self._box = self._factory(self._path)
        self._box.lock()
        key2 = self._box.add(msg)
        self._box.flush()
        self.assertTrue(self._box._locked)
        self._box.close()


kundi TestMbox(_TestMboxMMDF, unittest.TestCase):

    _factory = lambda self, path, factory=None: mailbox.mbox(path, factory)

    @unittest.skipUnless(hasattr(os, 'umask'), 'test needs os.umask()')
    eleza test_file_perms(self):
        # From bug #3228, we want to verify that the mailbox file isn't executable,
        # even ikiwa the umask is set to something that would leave executable bits set.
        # We only run this test on platforms that support umask.
        try:
            old_umask = os.umask(0o077)
            self._box.close()
            os.unlink(self._path)
            self._box = mailbox.mbox(self._path, create=True)
            self._box.add('')
            self._box.close()
        finally:
            os.umask(old_umask)

        st = os.stat(self._path)
        perms = st.st_mode
        self.assertFalse((perms & 0o111)) # Execute bits should all be off.

    eleza test_terminating_newline(self):
        message = email.message.Message()
        message['From'] = 'john@example.com'
        message.set_payload('No newline at the end')
        i = self._box.add(message)

        # A newline should have been appended to the payload
        message = self._box.get(i)
        self.assertEqual(message.get_payload(), 'No newline at the end\n')

    eleza test_message_separator(self):
        # Check there's always a single blank line after each message
        self._box.add('From: foo\n\n0')  # No newline at the end
        with open(self._path) as f:
            data = f.read()
            self.assertEqual(data[-3:], '0\n\n')

        self._box.add('From: foo\n\n0\n')  # Newline at the end
        with open(self._path) as f:
            data = f.read()
            self.assertEqual(data[-3:], '0\n\n')


kundi TestMMDF(_TestMboxMMDF, unittest.TestCase):

    _factory = lambda self, path, factory=None: mailbox.MMDF(path, factory)


kundi TestMH(TestMailbox, unittest.TestCase):

    _factory = lambda self, path, factory=None: mailbox.MH(path, factory)

    eleza assertMailboxEmpty(self):
        self.assertEqual(os.listdir(self._path), ['.mh_sequences'])

    eleza test_list_folders(self):
        # List folders
        self._box.add_folder('one')
        self._box.add_folder('two')
        self._box.add_folder('three')
        self.assertEqual(len(self._box.list_folders()), 3)
        self.assertEqual(set(self._box.list_folders()),
                     set(('one', 'two', 'three')))

    eleza test_get_folder(self):
        # Open folders
        eleza dummy_factory (s):
            rudisha None
        self._box = self._factory(self._path, dummy_factory)

        new_folder = self._box.add_folder('foo.bar')
        folder0 = self._box.get_folder('foo.bar')
        folder0.add(self._template % 'bar')
        self.assertTrue(os.path.isdir(os.path.join(self._path, 'foo.bar')))
        folder1 = self._box.get_folder('foo.bar')
        self.assertEqual(folder1.get_string(folder1.keys()[0]),
                         self._template % 'bar')

        # Test for bug #1569790: verify that folders returned by .get_folder()
        # use the same factory function.
        self.assertIs(new_folder._factory, self._box._factory)
        self.assertIs(folder0._factory, self._box._factory)

    eleza test_add_and_remove_folders(self):
        # Delete folders
        self._box.add_folder('one')
        self._box.add_folder('two')
        self.assertEqual(len(self._box.list_folders()), 2)
        self.assertEqual(set(self._box.list_folders()), set(('one', 'two')))
        self._box.remove_folder('one')
        self.assertEqual(len(self._box.list_folders()), 1)
        self.assertEqual(set(self._box.list_folders()), set(('two',)))
        self._box.add_folder('three')
        self.assertEqual(len(self._box.list_folders()), 2)
        self.assertEqual(set(self._box.list_folders()), set(('two', 'three')))
        self._box.remove_folder('three')
        self.assertEqual(len(self._box.list_folders()), 1)
        self.assertEqual(set(self._box.list_folders()), set(('two',)))
        self._box.remove_folder('two')
        self.assertEqual(len(self._box.list_folders()), 0)
        self.assertEqual(self._box.list_folders(), [])

    eleza test_sequences(self):
        # Get and set sequences
        self.assertEqual(self._box.get_sequences(), {})
        msg0 = mailbox.MHMessage(self._template % 0)
        msg0.add_sequence('foo')
        key0 = self._box.add(msg0)
        self.assertEqual(self._box.get_sequences(), {'foo':[key0]})
        msg1 = mailbox.MHMessage(self._template % 1)
        msg1.set_sequences(['bar', 'replied', 'foo'])
        key1 = self._box.add(msg1)
        self.assertEqual(self._box.get_sequences(),
                     {'foo':[key0, key1], 'bar':[key1], 'replied':[key1]})
        msg0.set_sequences(['flagged'])
        self._box[key0] = msg0
        self.assertEqual(self._box.get_sequences(),
                     {'foo':[key1], 'bar':[key1], 'replied':[key1],
                      'flagged':[key0]})
        self._box.remove(key1)
        self.assertEqual(self._box.get_sequences(), {'flagged':[key0]})

    eleza test_issue2625(self):
        msg0 = mailbox.MHMessage(self._template % 0)
        msg0.add_sequence('foo')
        key0 = self._box.add(msg0)
        refmsg0 = self._box.get_message(key0)

    eleza test_issue7627(self):
        msg0 = mailbox.MHMessage(self._template % 0)
        key0 = self._box.add(msg0)
        self._box.lock()
        self._box.remove(key0)
        self._box.unlock()

    eleza test_pack(self):
        # Pack the contents of the mailbox
        msg0 = mailbox.MHMessage(self._template % 0)
        msg1 = mailbox.MHMessage(self._template % 1)
        msg2 = mailbox.MHMessage(self._template % 2)
        msg3 = mailbox.MHMessage(self._template % 3)
        msg0.set_sequences(['foo', 'unseen'])
        msg1.set_sequences(['foo'])
        msg2.set_sequences(['foo', 'flagged'])
        msg3.set_sequences(['foo', 'bar', 'replied'])
        key0 = self._box.add(msg0)
        key1 = self._box.add(msg1)
        key2 = self._box.add(msg2)
        key3 = self._box.add(msg3)
        self.assertEqual(self._box.get_sequences(),
                     {'foo':[key0,key1,key2,key3], 'unseen':[key0],
                      'flagged':[key2], 'bar':[key3], 'replied':[key3]})
        self._box.remove(key2)
        self.assertEqual(self._box.get_sequences(),
                     {'foo':[key0,key1,key3], 'unseen':[key0], 'bar':[key3],
                      'replied':[key3]})
        self._box.pack()
        self.assertEqual(self._box.keys(), [1, 2, 3])
        key0 = key0
        key1 = key0 + 1
        key2 = key1 + 1
        self.assertEqual(self._box.get_sequences(),
                     {'foo':[1, 2, 3], 'unseen':[1], 'bar':[3], 'replied':[3]})

        # Test case for packing while holding the mailbox locked.
        key0 = self._box.add(msg1)
        key1 = self._box.add(msg1)
        key2 = self._box.add(msg1)
        key3 = self._box.add(msg1)

        self._box.remove(key0)
        self._box.remove(key2)
        self._box.lock()
        self._box.pack()
        self._box.unlock()
        self.assertEqual(self._box.get_sequences(),
                     {'foo':[1, 2, 3, 4, 5],
                      'unseen':[1], 'bar':[3], 'replied':[3]})

    eleza _get_lock_path(self):
        rudisha os.path.join(self._path, '.mh_sequences.lock')


kundi TestBabyl(_TestSingleFile, unittest.TestCase):

    _factory = lambda self, path, factory=None: mailbox.Babyl(path, factory)

    eleza assertMailboxEmpty(self):
        with open(self._path) as f:
            self.assertEqual(f.readlines(), [])

    eleza tearDown(self):
        super().tearDown()
        self._box.close()
        self._delete_recursively(self._path)
        for lock_remnant in glob.glob(self._path + '.*'):
            support.unlink(lock_remnant)

    eleza test_labels(self):
        # Get labels kutoka the mailbox
        self.assertEqual(self._box.get_labels(), [])
        msg0 = mailbox.BabylMessage(self._template % 0)
        msg0.add_label('foo')
        key0 = self._box.add(msg0)
        self.assertEqual(self._box.get_labels(), ['foo'])
        msg1 = mailbox.BabylMessage(self._template % 1)
        msg1.set_labels(['bar', 'answered', 'foo'])
        key1 = self._box.add(msg1)
        self.assertEqual(set(self._box.get_labels()), set(['foo', 'bar']))
        msg0.set_labels(['blah', 'filed'])
        self._box[key0] = msg0
        self.assertEqual(set(self._box.get_labels()),
                     set(['foo', 'bar', 'blah']))
        self._box.remove(key1)
        self.assertEqual(set(self._box.get_labels()), set(['blah']))


kundi FakeFileLikeObject:

    eleza __init__(self):
        self.closed = False

    eleza close(self):
        self.closed = True


kundi FakeMailBox(mailbox.Mailbox):

    eleza __init__(self):
        mailbox.Mailbox.__init__(self, '', lambda file: None)
        self.files = [FakeFileLikeObject() for i in range(10)]

    eleza get_file(self, key):
        rudisha self.files[key]


kundi TestFakeMailBox(unittest.TestCase):

    eleza test_closing_fd(self):
        box = FakeMailBox()
        for i in range(10):
            self.assertFalse(box.files[i].closed)
        for i in range(10):
            box[i]
        for i in range(10):
            self.assertTrue(box.files[i].closed)


kundi TestMessage(TestBase, unittest.TestCase):

    _factory = mailbox.Message      # Overridden by subclasses to reuse tests

    eleza setUp(self):
        self._path = support.TESTFN

    eleza tearDown(self):
        self._delete_recursively(self._path)

    eleza test_initialize_with_eMM(self):
        # Initialize based on email.message.Message instance
        eMM = email.message_kutoka_string(_sample_message)
        msg = self._factory(eMM)
        self._post_initialize_hook(msg)
        self._check_sample(msg)

    eleza test_initialize_with_string(self):
        # Initialize based on string
        msg = self._factory(_sample_message)
        self._post_initialize_hook(msg)
        self._check_sample(msg)

    eleza test_initialize_with_file(self):
        # Initialize based on contents of file
        with open(self._path, 'w+') as f:
            f.write(_sample_message)
            f.seek(0)
            msg = self._factory(f)
            self._post_initialize_hook(msg)
            self._check_sample(msg)

    eleza test_initialize_with_binary_file(self):
        # Initialize based on contents of binary file
        with open(self._path, 'wb+') as f:
            f.write(_bytes_sample_message)
            f.seek(0)
            msg = self._factory(f)
            self._post_initialize_hook(msg)
            self._check_sample(msg)

    eleza test_initialize_with_nothing(self):
        # Initialize without arguments
        msg = self._factory()
        self._post_initialize_hook(msg)
        self.assertIsInstance(msg, email.message.Message)
        self.assertIsInstance(msg, mailbox.Message)
        self.assertIsInstance(msg, self._factory)
        self.assertEqual(msg.keys(), [])
        self.assertFalse(msg.is_multipart())
        self.assertIsNone(msg.get_payload())

    eleza test_initialize_incorrectly(self):
        # Initialize with invalid argument
        self.assertRaises(TypeError, lambda: self._factory(object()))

    eleza test_all_eMM_attribues_exist(self):
        # Issue 12537
        eMM = email.message_kutoka_string(_sample_message)
        msg = self._factory(_sample_message)
        for attr in eMM.__dict__:
            self.assertIn(attr, msg.__dict__,
                '{} attribute does not exist'.format(attr))

    eleza test_become_message(self):
        # Take on the state of another message
        eMM = email.message_kutoka_string(_sample_message)
        msg = self._factory()
        msg._become_message(eMM)
        self._check_sample(msg)

    eleza test_explain_to(self):
        # Copy self's format-specific data to other message formats.
        # This test is superficial; better ones are in TestMessageConversion.
        msg = self._factory()
        for class_ in self.all_mailbox_types:
            other_msg = class_()
            msg._explain_to(other_msg)
        other_msg = email.message.Message()
        self.assertRaises(TypeError, lambda: msg._explain_to(other_msg))

    eleza _post_initialize_hook(self, msg):
        # Overridden by subclasses to check extra things after initialization
        pass


kundi TestMaildirMessage(TestMessage, unittest.TestCase):

    _factory = mailbox.MaildirMessage

    eleza _post_initialize_hook(self, msg):
        self.assertEqual(msg._subdir, 'new')
        self.assertEqual(msg._info, '')

    eleza test_subdir(self):
        # Use get_subdir() and set_subdir()
        msg = mailbox.MaildirMessage(_sample_message)
        self.assertEqual(msg.get_subdir(), 'new')
        msg.set_subdir('cur')
        self.assertEqual(msg.get_subdir(), 'cur')
        msg.set_subdir('new')
        self.assertEqual(msg.get_subdir(), 'new')
        self.assertRaises(ValueError, lambda: msg.set_subdir('tmp'))
        self.assertEqual(msg.get_subdir(), 'new')
        msg.set_subdir('new')
        self.assertEqual(msg.get_subdir(), 'new')
        self._check_sample(msg)

    eleza test_flags(self):
        # Use get_flags(), set_flags(), add_flag(), remove_flag()
        msg = mailbox.MaildirMessage(_sample_message)
        self.assertEqual(msg.get_flags(), '')
        self.assertEqual(msg.get_subdir(), 'new')
        msg.set_flags('F')
        self.assertEqual(msg.get_subdir(), 'new')
        self.assertEqual(msg.get_flags(), 'F')
        msg.set_flags('SDTP')
        self.assertEqual(msg.get_flags(), 'DPST')
        msg.add_flag('FT')
        self.assertEqual(msg.get_flags(), 'DFPST')
        msg.remove_flag('TDRP')
        self.assertEqual(msg.get_flags(), 'FS')
        self.assertEqual(msg.get_subdir(), 'new')
        self._check_sample(msg)

    eleza test_date(self):
        # Use get_date() and set_date()
        msg = mailbox.MaildirMessage(_sample_message)
        self.assertLess(abs(msg.get_date() - time.time()), 60)
        msg.set_date(0.0)
        self.assertEqual(msg.get_date(), 0.0)

    eleza test_info(self):
        # Use get_info() and set_info()
        msg = mailbox.MaildirMessage(_sample_message)
        self.assertEqual(msg.get_info(), '')
        msg.set_info('1,foo=bar')
        self.assertEqual(msg.get_info(), '1,foo=bar')
        self.assertRaises(TypeError, lambda: msg.set_info(None))
        self._check_sample(msg)

    eleza test_info_and_flags(self):
        # Test interaction of info and flag methods
        msg = mailbox.MaildirMessage(_sample_message)
        self.assertEqual(msg.get_info(), '')
        msg.set_flags('SF')
        self.assertEqual(msg.get_flags(), 'FS')
        self.assertEqual(msg.get_info(), '2,FS')
        msg.set_info('1,')
        self.assertEqual(msg.get_flags(), '')
        self.assertEqual(msg.get_info(), '1,')
        msg.remove_flag('RPT')
        self.assertEqual(msg.get_flags(), '')
        self.assertEqual(msg.get_info(), '1,')
        msg.add_flag('D')
        self.assertEqual(msg.get_flags(), 'D')
        self.assertEqual(msg.get_info(), '2,D')
        self._check_sample(msg)


kundi _TestMboxMMDFMessage:

    _factory = mailbox._mboxMMDFMessage

    eleza _post_initialize_hook(self, msg):
        self._check_kutoka(msg)

    eleza test_initialize_with_unixkutoka(self):
        # Initialize with a message that already has a _unixkutoka attribute
        msg = mailbox.Message(_sample_message)
        msg.set_unixkutoka('From foo@bar blah')
        msg = mailbox.mboxMessage(msg)
        self.assertEqual(msg.get_kutoka(), 'foo@bar blah', msg.get_kutoka())

    eleza test_kutoka(self):
        # Get and set "From " line
        msg = mailbox.mboxMessage(_sample_message)
        self._check_kutoka(msg)
        msg.set_kutoka('foo bar')
        self.assertEqual(msg.get_kutoka(), 'foo bar')
        msg.set_kutoka('foo@bar', True)
        self._check_kutoka(msg, 'foo@bar')
        msg.set_kutoka('blah@temp', time.localtime())
        self._check_kutoka(msg, 'blah@temp')

    eleza test_flags(self):
        # Use get_flags(), set_flags(), add_flag(), remove_flag()
        msg = mailbox.mboxMessage(_sample_message)
        self.assertEqual(msg.get_flags(), '')
        msg.set_flags('F')
        self.assertEqual(msg.get_flags(), 'F')
        msg.set_flags('XODR')
        self.assertEqual(msg.get_flags(), 'RODX')
        msg.add_flag('FA')
        self.assertEqual(msg.get_flags(), 'RODFAX')
        msg.remove_flag('FDXA')
        self.assertEqual(msg.get_flags(), 'RO')
        self._check_sample(msg)

    eleza _check_kutoka(self, msg, sender=None):
        # Check contents of "From " line
        ikiwa sender is None:
            sender = "MAILER-DAEMON"
        self.assertIsNotNone(re.match(
                sender + r" \w{3} \w{3} [\d ]\d [\d ]\d:\d{2}:\d{2} \d{4}",
                msg.get_kutoka()))


kundi TestMboxMessage(_TestMboxMMDFMessage, TestMessage):

    _factory = mailbox.mboxMessage


kundi TestMHMessage(TestMessage, unittest.TestCase):

    _factory = mailbox.MHMessage

    eleza _post_initialize_hook(self, msg):
        self.assertEqual(msg._sequences, [])

    eleza test_sequences(self):
        # Get, set, join, and leave sequences
        msg = mailbox.MHMessage(_sample_message)
        self.assertEqual(msg.get_sequences(), [])
        msg.set_sequences(['foobar'])
        self.assertEqual(msg.get_sequences(), ['foobar'])
        msg.set_sequences([])
        self.assertEqual(msg.get_sequences(), [])
        msg.add_sequence('unseen')
        self.assertEqual(msg.get_sequences(), ['unseen'])
        msg.add_sequence('flagged')
        self.assertEqual(msg.get_sequences(), ['unseen', 'flagged'])
        msg.add_sequence('flagged')
        self.assertEqual(msg.get_sequences(), ['unseen', 'flagged'])
        msg.remove_sequence('unseen')
        self.assertEqual(msg.get_sequences(), ['flagged'])
        msg.add_sequence('foobar')
        self.assertEqual(msg.get_sequences(), ['flagged', 'foobar'])
        msg.remove_sequence('replied')
        self.assertEqual(msg.get_sequences(), ['flagged', 'foobar'])
        msg.set_sequences(['foobar', 'replied'])
        self.assertEqual(msg.get_sequences(), ['foobar', 'replied'])


kundi TestBabylMessage(TestMessage, unittest.TestCase):

    _factory = mailbox.BabylMessage

    eleza _post_initialize_hook(self, msg):
        self.assertEqual(msg._labels, [])

    eleza test_labels(self):
        # Get, set, join, and leave labels
        msg = mailbox.BabylMessage(_sample_message)
        self.assertEqual(msg.get_labels(), [])
        msg.set_labels(['foobar'])
        self.assertEqual(msg.get_labels(), ['foobar'])
        msg.set_labels([])
        self.assertEqual(msg.get_labels(), [])
        msg.add_label('filed')
        self.assertEqual(msg.get_labels(), ['filed'])
        msg.add_label('resent')
        self.assertEqual(msg.get_labels(), ['filed', 'resent'])
        msg.add_label('resent')
        self.assertEqual(msg.get_labels(), ['filed', 'resent'])
        msg.remove_label('filed')
        self.assertEqual(msg.get_labels(), ['resent'])
        msg.add_label('foobar')
        self.assertEqual(msg.get_labels(), ['resent', 'foobar'])
        msg.remove_label('unseen')
        self.assertEqual(msg.get_labels(), ['resent', 'foobar'])
        msg.set_labels(['foobar', 'answered'])
        self.assertEqual(msg.get_labels(), ['foobar', 'answered'])

    eleza test_visible(self):
        # Get, set, and update visible headers
        msg = mailbox.BabylMessage(_sample_message)
        visible = msg.get_visible()
        self.assertEqual(visible.keys(), [])
        self.assertIsNone(visible.get_payload())
        visible['User-Agent'] = 'FooBar 1.0'
        visible['X-Whatever'] = 'Blah'
        self.assertEqual(msg.get_visible().keys(), [])
        msg.set_visible(visible)
        visible = msg.get_visible()
        self.assertEqual(visible.keys(), ['User-Agent', 'X-Whatever'])
        self.assertEqual(visible['User-Agent'], 'FooBar 1.0')
        self.assertEqual(visible['X-Whatever'], 'Blah')
        self.assertIsNone(visible.get_payload())
        msg.update_visible()
        self.assertEqual(visible.keys(), ['User-Agent', 'X-Whatever'])
        self.assertIsNone(visible.get_payload())
        visible = msg.get_visible()
        self.assertEqual(visible.keys(), ['User-Agent', 'Date', 'From', 'To',
                                          'Subject'])
        for header in ('User-Agent', 'Date', 'From', 'To', 'Subject'):
            self.assertEqual(visible[header], msg[header])


kundi TestMMDFMessage(_TestMboxMMDFMessage, TestMessage):

    _factory = mailbox.MMDFMessage


kundi TestMessageConversion(TestBase, unittest.TestCase):

    eleza test_plain_to_x(self):
        # Convert Message to all formats
        for class_ in self.all_mailbox_types:
            msg_plain = mailbox.Message(_sample_message)
            msg = class_(msg_plain)
            self._check_sample(msg)

    eleza test_x_to_plain(self):
        # Convert all formats to Message
        for class_ in self.all_mailbox_types:
            msg = class_(_sample_message)
            msg_plain = mailbox.Message(msg)
            self._check_sample(msg_plain)

    eleza test_x_kutoka_bytes(self):
        # Convert all formats to Message
        for class_ in self.all_mailbox_types:
            msg = class_(_bytes_sample_message)
            self._check_sample(msg)

    eleza test_x_to_invalid(self):
        # Convert all formats to an invalid format
        for class_ in self.all_mailbox_types:
            self.assertRaises(TypeError, lambda: class_(False))

    eleza test_type_specific_attributes_removed_on_conversion(self):
        reference = {class_: class_(_sample_message).__dict__
                        for class_ in self.all_mailbox_types}
        for class1 in self.all_mailbox_types:
            for class2 in self.all_mailbox_types:
                ikiwa class1 is class2:
                    continue
                source = class1(_sample_message)
                target = class2(source)
                type_specific = [a for a in reference[class1]
                                   ikiwa a not in reference[class2]]
                for attr in type_specific:
                    self.assertNotIn(attr, target.__dict__,
                        "while converting {} to {}".format(class1, class2))

    eleza test_maildir_to_maildir(self):
        # Convert MaildirMessage to MaildirMessage
        msg_maildir = mailbox.MaildirMessage(_sample_message)
        msg_maildir.set_flags('DFPRST')
        msg_maildir.set_subdir('cur')
        date = msg_maildir.get_date()
        msg = mailbox.MaildirMessage(msg_maildir)
        self._check_sample(msg)
        self.assertEqual(msg.get_flags(), 'DFPRST')
        self.assertEqual(msg.get_subdir(), 'cur')
        self.assertEqual(msg.get_date(), date)

    eleza test_maildir_to_mboxmmdf(self):
        # Convert MaildirMessage to mboxmessage and MMDFMessage
        pairs = (('D', ''), ('F', 'F'), ('P', ''), ('R', 'A'), ('S', 'R'),
                 ('T', 'D'), ('DFPRST', 'RDFA'))
        for class_ in (mailbox.mboxMessage, mailbox.MMDFMessage):
            msg_maildir = mailbox.MaildirMessage(_sample_message)
            msg_maildir.set_date(0.0)
            for setting, result in pairs:
                msg_maildir.set_flags(setting)
                msg = class_(msg_maildir)
                self.assertEqual(msg.get_flags(), result)
                self.assertEqual(msg.get_kutoka(), 'MAILER-DAEMON %s' %
                             time.asctime(time.gmtime(0.0)))
            msg_maildir.set_subdir('cur')
            self.assertEqual(class_(msg_maildir).get_flags(), 'RODFA')

    eleza test_maildir_to_mh(self):
        # Convert MaildirMessage to MHMessage
        msg_maildir = mailbox.MaildirMessage(_sample_message)
        pairs = (('D', ['unseen']), ('F', ['unseen', 'flagged']),
                 ('P', ['unseen']), ('R', ['unseen', 'replied']), ('S', []),
                 ('T', ['unseen']), ('DFPRST', ['replied', 'flagged']))
        for setting, result in pairs:
            msg_maildir.set_flags(setting)
            self.assertEqual(mailbox.MHMessage(msg_maildir).get_sequences(),
                             result)

    eleza test_maildir_to_babyl(self):
        # Convert MaildirMessage to Babyl
        msg_maildir = mailbox.MaildirMessage(_sample_message)
        pairs = (('D', ['unseen']), ('F', ['unseen']),
                 ('P', ['unseen', 'forwarded']), ('R', ['unseen', 'answered']),
                 ('S', []), ('T', ['unseen', 'deleted']),
                 ('DFPRST', ['deleted', 'answered', 'forwarded']))
        for setting, result in pairs:
            msg_maildir.set_flags(setting)
            self.assertEqual(mailbox.BabylMessage(msg_maildir).get_labels(),
                             result)

    eleza test_mboxmmdf_to_maildir(self):
        # Convert mboxMessage and MMDFMessage to MaildirMessage
        for class_ in (mailbox.mboxMessage, mailbox.MMDFMessage):
            msg_mboxMMDF = class_(_sample_message)
            msg_mboxMMDF.set_kutoka('foo@bar', time.gmtime(0.0))
            pairs = (('R', 'S'), ('O', ''), ('D', 'T'), ('F', 'F'), ('A', 'R'),
                     ('RODFA', 'FRST'))
            for setting, result in pairs:
                msg_mboxMMDF.set_flags(setting)
                msg = mailbox.MaildirMessage(msg_mboxMMDF)
                self.assertEqual(msg.get_flags(), result)
                self.assertEqual(msg.get_date(), 0.0)
            msg_mboxMMDF.set_flags('O')
            self.assertEqual(mailbox.MaildirMessage(msg_mboxMMDF).get_subdir(),
                             'cur')

    eleza test_mboxmmdf_to_mboxmmdf(self):
        # Convert mboxMessage and MMDFMessage to mboxMessage and MMDFMessage
        for class_ in (mailbox.mboxMessage, mailbox.MMDFMessage):
            msg_mboxMMDF = class_(_sample_message)
            msg_mboxMMDF.set_flags('RODFA')
            msg_mboxMMDF.set_kutoka('foo@bar')
            for class2_ in (mailbox.mboxMessage, mailbox.MMDFMessage):
                msg2 = class2_(msg_mboxMMDF)
                self.assertEqual(msg2.get_flags(), 'RODFA')
                self.assertEqual(msg2.get_kutoka(), 'foo@bar')

    eleza test_mboxmmdf_to_mh(self):
        # Convert mboxMessage and MMDFMessage to MHMessage
        for class_ in (mailbox.mboxMessage, mailbox.MMDFMessage):
            msg_mboxMMDF = class_(_sample_message)
            pairs = (('R', []), ('O', ['unseen']), ('D', ['unseen']),
                     ('F', ['unseen', 'flagged']),
                     ('A', ['unseen', 'replied']),
                     ('RODFA', ['replied', 'flagged']))
            for setting, result in pairs:
                msg_mboxMMDF.set_flags(setting)
                self.assertEqual(mailbox.MHMessage(msg_mboxMMDF).get_sequences(),
                                 result)

    eleza test_mboxmmdf_to_babyl(self):
        # Convert mboxMessage and MMDFMessage to BabylMessage
        for class_ in (mailbox.mboxMessage, mailbox.MMDFMessage):
            msg = class_(_sample_message)
            pairs = (('R', []), ('O', ['unseen']),
                     ('D', ['unseen', 'deleted']), ('F', ['unseen']),
                     ('A', ['unseen', 'answered']),
                     ('RODFA', ['deleted', 'answered']))
            for setting, result in pairs:
                msg.set_flags(setting)
                self.assertEqual(mailbox.BabylMessage(msg).get_labels(), result)

    eleza test_mh_to_maildir(self):
        # Convert MHMessage to MaildirMessage
        pairs = (('unseen', ''), ('replied', 'RS'), ('flagged', 'FS'))
        for setting, result in pairs:
            msg = mailbox.MHMessage(_sample_message)
            msg.add_sequence(setting)
            self.assertEqual(mailbox.MaildirMessage(msg).get_flags(), result)
            self.assertEqual(mailbox.MaildirMessage(msg).get_subdir(), 'cur')
        msg = mailbox.MHMessage(_sample_message)
        msg.add_sequence('unseen')
        msg.add_sequence('replied')
        msg.add_sequence('flagged')
        self.assertEqual(mailbox.MaildirMessage(msg).get_flags(), 'FR')
        self.assertEqual(mailbox.MaildirMessage(msg).get_subdir(), 'cur')

    eleza test_mh_to_mboxmmdf(self):
        # Convert MHMessage to mboxMessage and MMDFMessage
        pairs = (('unseen', 'O'), ('replied', 'ROA'), ('flagged', 'ROF'))
        for setting, result in pairs:
            msg = mailbox.MHMessage(_sample_message)
            msg.add_sequence(setting)
            for class_ in (mailbox.mboxMessage, mailbox.MMDFMessage):
                self.assertEqual(class_(msg).get_flags(), result)
        msg = mailbox.MHMessage(_sample_message)
        msg.add_sequence('unseen')
        msg.add_sequence('replied')
        msg.add_sequence('flagged')
        for class_ in (mailbox.mboxMessage, mailbox.MMDFMessage):
            self.assertEqual(class_(msg).get_flags(), 'OFA')

    eleza test_mh_to_mh(self):
        # Convert MHMessage to MHMessage
        msg = mailbox.MHMessage(_sample_message)
        msg.add_sequence('unseen')
        msg.add_sequence('replied')
        msg.add_sequence('flagged')
        self.assertEqual(mailbox.MHMessage(msg).get_sequences(),
                         ['unseen', 'replied', 'flagged'])

    eleza test_mh_to_babyl(self):
        # Convert MHMessage to BabylMessage
        pairs = (('unseen', ['unseen']), ('replied', ['answered']),
                 ('flagged', []))
        for setting, result in pairs:
            msg = mailbox.MHMessage(_sample_message)
            msg.add_sequence(setting)
            self.assertEqual(mailbox.BabylMessage(msg).get_labels(), result)
        msg = mailbox.MHMessage(_sample_message)
        msg.add_sequence('unseen')
        msg.add_sequence('replied')
        msg.add_sequence('flagged')
        self.assertEqual(mailbox.BabylMessage(msg).get_labels(),
                         ['unseen', 'answered'])

    eleza test_babyl_to_maildir(self):
        # Convert BabylMessage to MaildirMessage
        pairs = (('unseen', ''), ('deleted', 'ST'), ('filed', 'S'),
                 ('answered', 'RS'), ('forwarded', 'PS'), ('edited', 'S'),
                 ('resent', 'PS'))
        for setting, result in pairs:
            msg = mailbox.BabylMessage(_sample_message)
            msg.add_label(setting)
            self.assertEqual(mailbox.MaildirMessage(msg).get_flags(), result)
            self.assertEqual(mailbox.MaildirMessage(msg).get_subdir(), 'cur')
        msg = mailbox.BabylMessage(_sample_message)
        for label in ('unseen', 'deleted', 'filed', 'answered', 'forwarded',
                      'edited', 'resent'):
            msg.add_label(label)
        self.assertEqual(mailbox.MaildirMessage(msg).get_flags(), 'PRT')
        self.assertEqual(mailbox.MaildirMessage(msg).get_subdir(), 'cur')

    eleza test_babyl_to_mboxmmdf(self):
        # Convert BabylMessage to mboxMessage and MMDFMessage
        pairs = (('unseen', 'O'), ('deleted', 'ROD'), ('filed', 'RO'),
                 ('answered', 'ROA'), ('forwarded', 'RO'), ('edited', 'RO'),
                 ('resent', 'RO'))
        for setting, result in pairs:
            for class_ in (mailbox.mboxMessage, mailbox.MMDFMessage):
                msg = mailbox.BabylMessage(_sample_message)
                msg.add_label(setting)
                self.assertEqual(class_(msg).get_flags(), result)
        msg = mailbox.BabylMessage(_sample_message)
        for label in ('unseen', 'deleted', 'filed', 'answered', 'forwarded',
                      'edited', 'resent'):
            msg.add_label(label)
        for class_ in (mailbox.mboxMessage, mailbox.MMDFMessage):
            self.assertEqual(class_(msg).get_flags(), 'ODA')

    eleza test_babyl_to_mh(self):
        # Convert BabylMessage to MHMessage
        pairs = (('unseen', ['unseen']), ('deleted', []), ('filed', []),
                 ('answered', ['replied']), ('forwarded', []), ('edited', []),
                 ('resent', []))
        for setting, result in pairs:
            msg = mailbox.BabylMessage(_sample_message)
            msg.add_label(setting)
            self.assertEqual(mailbox.MHMessage(msg).get_sequences(), result)
        msg = mailbox.BabylMessage(_sample_message)
        for label in ('unseen', 'deleted', 'filed', 'answered', 'forwarded',
                      'edited', 'resent'):
            msg.add_label(label)
        self.assertEqual(mailbox.MHMessage(msg).get_sequences(),
                         ['unseen', 'replied'])

    eleza test_babyl_to_babyl(self):
        # Convert BabylMessage to BabylMessage
        msg = mailbox.BabylMessage(_sample_message)
        msg.update_visible()
        for label in ('unseen', 'deleted', 'filed', 'answered', 'forwarded',
                      'edited', 'resent'):
            msg.add_label(label)
        msg2 = mailbox.BabylMessage(msg)
        self.assertEqual(msg2.get_labels(), ['unseen', 'deleted', 'filed',
                                             'answered', 'forwarded', 'edited',
                                             'resent'])
        self.assertEqual(msg.get_visible().keys(), msg2.get_visible().keys())
        for key in msg.get_visible().keys():
            self.assertEqual(msg.get_visible()[key], msg2.get_visible()[key])


kundi TestProxyFileBase(TestBase):

    eleza _test_read(self, proxy):
        # Read by byte
        proxy.seek(0)
        self.assertEqual(proxy.read(), b'bar')
        proxy.seek(1)
        self.assertEqual(proxy.read(), b'ar')
        proxy.seek(0)
        self.assertEqual(proxy.read(2), b'ba')
        proxy.seek(1)
        self.assertEqual(proxy.read(-1), b'ar')
        proxy.seek(2)
        self.assertEqual(proxy.read(1000), b'r')

    eleza _test_readline(self, proxy):
        # Read by line
        linesep = os.linesep.encode()
        proxy.seek(0)
        self.assertEqual(proxy.readline(), b'foo' + linesep)
        self.assertEqual(proxy.readline(), b'bar' + linesep)
        self.assertEqual(proxy.readline(), b'fred' + linesep)
        self.assertEqual(proxy.readline(), b'bob')
        proxy.seek(2)
        self.assertEqual(proxy.readline(), b'o' + linesep)
        proxy.seek(6 + 2 * len(os.linesep))
        self.assertEqual(proxy.readline(), b'fred' + linesep)
        proxy.seek(6 + 2 * len(os.linesep))
        self.assertEqual(proxy.readline(2), b'fr')
        self.assertEqual(proxy.readline(-10), b'ed' + linesep)

    eleza _test_readlines(self, proxy):
        # Read multiple lines
        linesep = os.linesep.encode()
        proxy.seek(0)
        self.assertEqual(proxy.readlines(), [b'foo' + linesep,
                                           b'bar' + linesep,
                                           b'fred' + linesep, b'bob'])
        proxy.seek(0)
        self.assertEqual(proxy.readlines(2), [b'foo' + linesep])
        proxy.seek(3 + len(linesep))
        self.assertEqual(proxy.readlines(4 + len(linesep)),
                     [b'bar' + linesep, b'fred' + linesep])
        proxy.seek(3)
        self.assertEqual(proxy.readlines(1000), [linesep, b'bar' + linesep,
                                               b'fred' + linesep, b'bob'])

    eleza _test_iteration(self, proxy):
        # Iterate by line
        linesep = os.linesep.encode()
        proxy.seek(0)
        iterator = iter(proxy)
        self.assertEqual(next(iterator), b'foo' + linesep)
        self.assertEqual(next(iterator), b'bar' + linesep)
        self.assertEqual(next(iterator), b'fred' + linesep)
        self.assertEqual(next(iterator), b'bob')
        self.assertRaises(StopIteration, next, iterator)

    eleza _test_seek_and_tell(self, proxy):
        # Seek and use tell to check position
        linesep = os.linesep.encode()
        proxy.seek(3)
        self.assertEqual(proxy.tell(), 3)
        self.assertEqual(proxy.read(len(linesep)), linesep)
        proxy.seek(2, 1)
        self.assertEqual(proxy.read(1 + len(linesep)), b'r' + linesep)
        proxy.seek(-3 - len(linesep), 2)
        self.assertEqual(proxy.read(3), b'bar')
        proxy.seek(2, 0)
        self.assertEqual(proxy.read(), b'o' + linesep + b'bar' + linesep)
        proxy.seek(100)
        self.assertFalse(proxy.read())

    eleza _test_close(self, proxy):
        # Close a file
        self.assertFalse(proxy.closed)
        proxy.close()
        self.assertTrue(proxy.closed)
        # Issue 11700 subsequent closes should be a no-op.
        proxy.close()
        self.assertTrue(proxy.closed)


kundi TestProxyFile(TestProxyFileBase, unittest.TestCase):

    eleza setUp(self):
        self._path = support.TESTFN
        self._file = open(self._path, 'wb+')

    eleza tearDown(self):
        self._file.close()
        self._delete_recursively(self._path)

    eleza test_initialize(self):
        # Initialize and check position
        self._file.write(b'foo')
        pos = self._file.tell()
        proxy0 = mailbox._ProxyFile(self._file)
        self.assertEqual(proxy0.tell(), pos)
        self.assertEqual(self._file.tell(), pos)
        proxy1 = mailbox._ProxyFile(self._file, 0)
        self.assertEqual(proxy1.tell(), 0)
        self.assertEqual(self._file.tell(), pos)

    eleza test_read(self):
        self._file.write(b'bar')
        self._test_read(mailbox._ProxyFile(self._file))

    eleza test_readline(self):
        self._file.write(bytes('foo%sbar%sfred%sbob' % (os.linesep, os.linesep,
                                                  os.linesep), 'ascii'))
        self._test_readline(mailbox._ProxyFile(self._file))

    eleza test_readlines(self):
        self._file.write(bytes('foo%sbar%sfred%sbob' % (os.linesep, os.linesep,
                                                  os.linesep), 'ascii'))
        self._test_readlines(mailbox._ProxyFile(self._file))

    eleza test_iteration(self):
        self._file.write(bytes('foo%sbar%sfred%sbob' % (os.linesep, os.linesep,
                                                  os.linesep), 'ascii'))
        self._test_iteration(mailbox._ProxyFile(self._file))

    eleza test_seek_and_tell(self):
        self._file.write(bytes('foo%sbar%s' % (os.linesep, os.linesep), 'ascii'))
        self._test_seek_and_tell(mailbox._ProxyFile(self._file))

    eleza test_close(self):
        self._file.write(bytes('foo%sbar%s' % (os.linesep, os.linesep), 'ascii'))
        self._test_close(mailbox._ProxyFile(self._file))


kundi TestPartialFile(TestProxyFileBase, unittest.TestCase):

    eleza setUp(self):
        self._path = support.TESTFN
        self._file = open(self._path, 'wb+')

    eleza tearDown(self):
        self._file.close()
        self._delete_recursively(self._path)

    eleza test_initialize(self):
        # Initialize and check position
        self._file.write(bytes('foo' + os.linesep + 'bar', 'ascii'))
        pos = self._file.tell()
        proxy = mailbox._PartialFile(self._file, 2, 5)
        self.assertEqual(proxy.tell(), 0)
        self.assertEqual(self._file.tell(), pos)

    eleza test_read(self):
        self._file.write(bytes('***bar***', 'ascii'))
        self._test_read(mailbox._PartialFile(self._file, 3, 6))

    eleza test_readline(self):
        self._file.write(bytes('!!!!!foo%sbar%sfred%sbob!!!!!' %
                         (os.linesep, os.linesep, os.linesep), 'ascii'))
        self._test_readline(mailbox._PartialFile(self._file, 5,
                                                 18 + 3 * len(os.linesep)))

    eleza test_readlines(self):
        self._file.write(bytes('foo%sbar%sfred%sbob?????' %
                         (os.linesep, os.linesep, os.linesep), 'ascii'))
        self._test_readlines(mailbox._PartialFile(self._file, 0,
                                                  13 + 3 * len(os.linesep)))

    eleza test_iteration(self):
        self._file.write(bytes('____foo%sbar%sfred%sbob####' %
                         (os.linesep, os.linesep, os.linesep), 'ascii'))
        self._test_iteration(mailbox._PartialFile(self._file, 4,
                                                  17 + 3 * len(os.linesep)))

    eleza test_seek_and_tell(self):
        self._file.write(bytes('(((foo%sbar%s$$$' % (os.linesep, os.linesep), 'ascii'))
        self._test_seek_and_tell(mailbox._PartialFile(self._file, 3,
                                                      9 + 2 * len(os.linesep)))

    eleza test_close(self):
        self._file.write(bytes('&foo%sbar%s^' % (os.linesep, os.linesep), 'ascii'))
        self._test_close(mailbox._PartialFile(self._file, 1,
                                              6 + 3 * len(os.linesep)))


## Start: tests kutoka the original module (for backward compatibility).

FROM_ = "From some.body@dummy.domain  Sat Jul 24 13:43:35 2004\n"
DUMMY_MESSAGE = """\
From: some.body@dummy.domain
To: me@my.domain
Subject: Simple Test

This is a dummy message.
"""

kundi MaildirTestCase(unittest.TestCase):

    eleza setUp(self):
        # create a new maildir mailbox to work with:
        self._dir = support.TESTFN
        ikiwa os.path.isdir(self._dir):
            support.rmtree(self._dir)
        elikiwa os.path.isfile(self._dir):
            support.unlink(self._dir)
        os.mkdir(self._dir)
        os.mkdir(os.path.join(self._dir, "cur"))
        os.mkdir(os.path.join(self._dir, "tmp"))
        os.mkdir(os.path.join(self._dir, "new"))
        self._counter = 1
        self._msgfiles = []

    eleza tearDown(self):
        list(map(os.unlink, self._msgfiles))
        support.rmdir(os.path.join(self._dir, "cur"))
        support.rmdir(os.path.join(self._dir, "tmp"))
        support.rmdir(os.path.join(self._dir, "new"))
        support.rmdir(self._dir)

    eleza createMessage(self, dir, mbox=False):
        t = int(time.time() % 1000000)
        pid = self._counter
        self._counter += 1
        filename = ".".join((str(t), str(pid), "myhostname", "mydomain"))
        tmpname = os.path.join(self._dir, "tmp", filename)
        newname = os.path.join(self._dir, dir, filename)
        with open(tmpname, "w") as fp:
            self._msgfiles.append(tmpname)
            ikiwa mbox:
                fp.write(FROM_)
            fp.write(DUMMY_MESSAGE)
        try:
            os.link(tmpname, newname)
        except (AttributeError, PermissionError):
            with open(newname, "w") as fp:
                fp.write(DUMMY_MESSAGE)
        self._msgfiles.append(newname)
        rudisha tmpname

    eleza test_empty_maildir(self):
        """Test an empty maildir mailbox"""
        # Test for regression on bug #117490:
        # Make sure the boxes attribute actually gets set.
        self.mbox = mailbox.Maildir(support.TESTFN)
        #self.assertTrue(hasattr(self.mbox, "boxes"))
        #self.assertEqual(len(self.mbox.boxes), 0)
        self.assertIsNone(self.mbox.next())
        self.assertIsNone(self.mbox.next())

    eleza test_nonempty_maildir_cur(self):
        self.createMessage("cur")
        self.mbox = mailbox.Maildir(support.TESTFN)
        #self.assertEqual(len(self.mbox.boxes), 1)
        self.assertIsNotNone(self.mbox.next())
        self.assertIsNone(self.mbox.next())
        self.assertIsNone(self.mbox.next())

    eleza test_nonempty_maildir_new(self):
        self.createMessage("new")
        self.mbox = mailbox.Maildir(support.TESTFN)
        #self.assertEqual(len(self.mbox.boxes), 1)
        self.assertIsNotNone(self.mbox.next())
        self.assertIsNone(self.mbox.next())
        self.assertIsNone(self.mbox.next())

    eleza test_nonempty_maildir_both(self):
        self.createMessage("cur")
        self.createMessage("new")
        self.mbox = mailbox.Maildir(support.TESTFN)
        #self.assertEqual(len(self.mbox.boxes), 2)
        self.assertIsNotNone(self.mbox.next())
        self.assertIsNotNone(self.mbox.next())
        self.assertIsNone(self.mbox.next())
        self.assertIsNone(self.mbox.next())

## End: tests kutoka the original module (for backward compatibility).


_sample_message = """\
Return-Path: <gkj@gregorykjohnson.com>
X-Original-To: gkj+person@localhost
Delivered-To: gkj+person@localhost
Received: kutoka localhost (localhost [127.0.0.1])
        by andy.gregorykjohnson.com (Postfix) with ESMTP id 356ED9DD17
        for <gkj+person@localhost>; Wed, 13 Jul 2005 17:23:16 -0400 (EDT)
Delivered-To: gkj@sundance.gregorykjohnson.com
Received: kutoka localhost [127.0.0.1]
        by localhost with POP3 (fetchmail-6.2.5)
        for gkj+person@localhost (single-drop); Wed, 13 Jul 2005 17:23:16 -0400 (EDT)
Received: kutoka andy.gregorykjohnson.com (andy.gregorykjohnson.com [64.32.235.228])
        by sundance.gregorykjohnson.com (Postfix) with ESMTP id 5B056316746
        for <gkj@gregorykjohnson.com>; Wed, 13 Jul 2005 17:23:11 -0400 (EDT)
Received: by andy.gregorykjohnson.com (Postfix, kutoka userid 1000)
        id 490CD9DD17; Wed, 13 Jul 2005 17:23:11 -0400 (EDT)
Date: Wed, 13 Jul 2005 17:23:11 -0400
From: "Gregory K. Johnson" <gkj@gregorykjohnson.com>
To: gkj@gregorykjohnson.com
Subject: Sample message
Message-ID: <20050713212311.GC4701@andy.gregorykjohnson.com>
Mime-Version: 1.0
Content-Type: multipart/mixed; boundary="NMuMz9nt05w80d4+"
Content-Disposition: inline
User-Agent: Mutt/1.5.9i


--NMuMz9nt05w80d4+
Content-Type: text/plain; charset=us-ascii
Content-Disposition: inline

This is a sample message.

--
Gregory K. Johnson

--NMuMz9nt05w80d4+
Content-Type: application/octet-stream
Content-Disposition: attachment; filename="text.gz"
Content-Transfer-Encoding: base64

H4sICM2D1UIAA3RleHQAC8nILFYAokSFktSKEoW0zJxUPa7wzJIMhZLyfIWczLzUYj0uAHTs
3FYlAAAA

--NMuMz9nt05w80d4+--
"""

_bytes_sample_message = _sample_message.encode('ascii')

_sample_headers = {
    "Return-Path":"<gkj@gregorykjohnson.com>",
    "X-Original-To":"gkj+person@localhost",
    "Delivered-To":"gkj+person@localhost",
    "Received":"""kutoka localhost (localhost [127.0.0.1])
        by andy.gregorykjohnson.com (Postfix) with ESMTP id 356ED9DD17
        for <gkj+person@localhost>; Wed, 13 Jul 2005 17:23:16 -0400 (EDT)""",
    "Delivered-To":"gkj@sundance.gregorykjohnson.com",
    "Received":"""kutoka localhost [127.0.0.1]
        by localhost with POP3 (fetchmail-6.2.5)
        for gkj+person@localhost (single-drop); Wed, 13 Jul 2005 17:23:16 -0400 (EDT)""",
    "Received":"""kutoka andy.gregorykjohnson.com (andy.gregorykjohnson.com [64.32.235.228])
        by sundance.gregorykjohnson.com (Postfix) with ESMTP id 5B056316746
        for <gkj@gregorykjohnson.com>; Wed, 13 Jul 2005 17:23:11 -0400 (EDT)""",
    "Received":"""by andy.gregorykjohnson.com (Postfix, kutoka userid 1000)
        id 490CD9DD17; Wed, 13 Jul 2005 17:23:11 -0400 (EDT)""",
    "Date":"Wed, 13 Jul 2005 17:23:11 -0400",
    "From":""""Gregory K. Johnson" <gkj@gregorykjohnson.com>""",
    "To":"gkj@gregorykjohnson.com",
    "Subject":"Sample message",
    "Mime-Version":"1.0",
    "Content-Type":"""multipart/mixed; boundary="NMuMz9nt05w80d4+\"""",
    "Content-Disposition":"inline",
    "User-Agent": "Mutt/1.5.9i" }

_sample_payloads = ("""This is a sample message.

--
Gregory K. Johnson
""",
"""H4sICM2D1UIAA3RleHQAC8nILFYAokSFktSKEoW0zJxUPa7wzJIMhZLyfIWczLzUYj0uAHTs
3FYlAAAA
""")


kundi MiscTestCase(unittest.TestCase):
    eleza test__all__(self):
        blacklist = {"linesep", "fcntl"}
        support.check__all__(self, mailbox, blacklist=blacklist)


eleza test_main():
    tests = (TestMailboxSuperclass, TestMaildir, TestMbox, TestMMDF, TestMH,
             TestBabyl, TestMessage, TestMaildirMessage, TestMboxMessage,
             TestMHMessage, TestBabylMessage, TestMMDFMessage,
             TestMessageConversion, TestProxyFile, TestPartialFile,
             MaildirTestCase, TestFakeMailBox, MiscTestCase)
    support.run_unittest(*tests)
    support.reap_children()


ikiwa __name__ == '__main__':
    test_main()
