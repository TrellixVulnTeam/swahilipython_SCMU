agiza unittest
kutoka warnings agiza catch_warnings

kutoka unittest.test.testmock.support agiza is_instance
kutoka unittest.mock agiza MagicMock, Mock, patch, sentinel, mock_open, call



something  = sentinel.Something
something_else  = sentinel.SomethingElse


kundi SampleException(Exception): pass


kundi WithTest(unittest.TestCase):

    eleza test_with_statement(self):
        ukijumuisha patch('%s.something' % __name__, sentinel.Something2):
            self.assertEqual(something, sentinel.Something2, "unpatched")
        self.assertEqual(something, sentinel.Something)


    eleza test_with_statement_exception(self):
        ukijumuisha self.assertRaises(SampleException):
            ukijumuisha patch('%s.something' % __name__, sentinel.Something2):
                self.assertEqual(something, sentinel.Something2, "unpatched")
                 ashiria SampleException()
        self.assertEqual(something, sentinel.Something)


    eleza test_with_statement_as(self):
        ukijumuisha patch('%s.something' % __name__) as mock_something:
            self.assertEqual(something, mock_something, "unpatched")
            self.assertKweli(is_instance(mock_something, MagicMock),
                            "patching wrong type")
        self.assertEqual(something, sentinel.Something)


    eleza test_patch_object_with_statement(self):
        kundi Foo(object):
            something = 'foo'
        original = Foo.something
        ukijumuisha patch.object(Foo, 'something'):
            self.assertNotEqual(Foo.something, original, "unpatched")
        self.assertEqual(Foo.something, original)


    eleza test_with_statement_nested(self):
        ukijumuisha catch_warnings(record=Kweli):
            ukijumuisha patch('%s.something' % __name__) as mock_something, patch('%s.something_else' % __name__) as mock_something_isipokua:
                self.assertEqual(something, mock_something, "unpatched")
                self.assertEqual(something_else, mock_something_else,
                                 "unpatched")

        self.assertEqual(something, sentinel.Something)
        self.assertEqual(something_else, sentinel.SomethingElse)


    eleza test_with_statement_specified(self):
        ukijumuisha patch('%s.something' % __name__, sentinel.Patched) as mock_something:
            self.assertEqual(something, mock_something, "unpatched")
            self.assertEqual(mock_something, sentinel.Patched, "wrong patch")
        self.assertEqual(something, sentinel.Something)


    eleza testContextManagerMocking(self):
        mock = Mock()
        mock.__enter__ = Mock()
        mock.__exit__ = Mock()
        mock.__exit__.return_value = Uongo

        ukijumuisha mock as m:
            self.assertEqual(m, mock.__enter__.return_value)
        mock.__enter__.assert_called_with()
        mock.__exit__.assert_called_with(Tupu, Tupu, Tupu)


    eleza test_context_manager_with_magic_mock(self):
        mock = MagicMock()

        ukijumuisha self.assertRaises(TypeError):
            ukijumuisha mock:
                'foo' + 3
        mock.__enter__.assert_called_with()
        self.assertKweli(mock.__exit__.called)


    eleza test_with_statement_same_attribute(self):
        ukijumuisha patch('%s.something' % __name__, sentinel.Patched) as mock_something:
            self.assertEqual(something, mock_something, "unpatched")

            ukijumuisha patch('%s.something' % __name__) as mock_again:
                self.assertEqual(something, mock_again, "unpatched")

            self.assertEqual(something, mock_something,
                             "restored ukijumuisha wrong instance")

        self.assertEqual(something, sentinel.Something, "not restored")


    eleza test_with_statement_imbricated(self):
        ukijumuisha patch('%s.something' % __name__) as mock_something:
            self.assertEqual(something, mock_something, "unpatched")

            ukijumuisha patch('%s.something_else' % __name__) as mock_something_isipokua:
                self.assertEqual(something_else, mock_something_else,
                                 "unpatched")

        self.assertEqual(something, sentinel.Something)
        self.assertEqual(something_else, sentinel.SomethingElse)


    eleza test_dict_context_manager(self):
        foo = {}
        ukijumuisha patch.dict(foo, {'a': 'b'}):
            self.assertEqual(foo, {'a': 'b'})
        self.assertEqual(foo, {})

        ukijumuisha self.assertRaises(NameError):
            ukijumuisha patch.dict(foo, {'a': 'b'}):
                self.assertEqual(foo, {'a': 'b'})
                 ashiria NameError('Konrad')

        self.assertEqual(foo, {})

    eleza test_double_patch_instance_method(self):
        kundi C:
            eleza f(self): pass

        c = C()

        ukijumuisha patch.object(c, 'f', autospec=Kweli) as patch1:
            ukijumuisha patch.object(c, 'f', autospec=Kweli) as patch2:
                c.f()
            self.assertEqual(patch2.call_count, 1)
            self.assertEqual(patch1.call_count, 0)
            c.f()
        self.assertEqual(patch1.call_count, 1)


kundi TestMockOpen(unittest.TestCase):

    eleza test_mock_open(self):
        mock = mock_open()
        ukijumuisha patch('%s.open' % __name__, mock, create=Kweli) as patched:
            self.assertIs(patched, mock)
            open('foo')

        mock.assert_called_once_with('foo')


    eleza test_mock_open_context_manager(self):
        mock = mock_open()
        handle = mock.return_value
        ukijumuisha patch('%s.open' % __name__, mock, create=Kweli):
            ukijumuisha open('foo') as f:
                f.read()

        expected_calls = [call('foo'), call().__enter__(), call().read(),
                          call().__exit__(Tupu, Tupu, Tupu)]
        self.assertEqual(mock.mock_calls, expected_calls)
        self.assertIs(f, handle)

    eleza test_mock_open_context_manager_multiple_times(self):
        mock = mock_open()
        ukijumuisha patch('%s.open' % __name__, mock, create=Kweli):
            ukijumuisha open('foo') as f:
                f.read()
            ukijumuisha open('bar') as f:
                f.read()

        expected_calls = [
            call('foo'), call().__enter__(), call().read(),
            call().__exit__(Tupu, Tupu, Tupu),
            call('bar'), call().__enter__(), call().read(),
            call().__exit__(Tupu, Tupu, Tupu)]
        self.assertEqual(mock.mock_calls, expected_calls)

    eleza test_explicit_mock(self):
        mock = MagicMock()
        mock_open(mock)

        ukijumuisha patch('%s.open' % __name__, mock, create=Kweli) as patched:
            self.assertIs(patched, mock)
            open('foo')

        mock.assert_called_once_with('foo')


    eleza test_read_data(self):
        mock = mock_open(read_data='foo')
        ukijumuisha patch('%s.open' % __name__, mock, create=Kweli):
            h = open('bar')
            result = h.read()

        self.assertEqual(result, 'foo')


    eleza test_readline_data(self):
        # Check that readline will rudisha all the lines kutoka the fake file
        # And that once fully consumed, readline will rudisha an empty string.
        mock = mock_open(read_data='foo\nbar\nbaz\n')
        ukijumuisha patch('%s.open' % __name__, mock, create=Kweli):
            h = open('bar')
            line1 = h.readline()
            line2 = h.readline()
            line3 = h.readline()
        self.assertEqual(line1, 'foo\n')
        self.assertEqual(line2, 'bar\n')
        self.assertEqual(line3, 'baz\n')
        self.assertEqual(h.readline(), '')

        # Check that we properly emulate a file that doesn't end kwenye a newline
        mock = mock_open(read_data='foo')
        ukijumuisha patch('%s.open' % __name__, mock, create=Kweli):
            h = open('bar')
            result = h.readline()
        self.assertEqual(result, 'foo')
        self.assertEqual(h.readline(), '')


    eleza test_dunder_iter_data(self):
        # Check that dunder_iter will rudisha all the lines kutoka the fake file.
        mock = mock_open(read_data='foo\nbar\nbaz\n')
        ukijumuisha patch('%s.open' % __name__, mock, create=Kweli):
            h = open('bar')
            lines = [l kila l kwenye h]
        self.assertEqual(lines[0], 'foo\n')
        self.assertEqual(lines[1], 'bar\n')
        self.assertEqual(lines[2], 'baz\n')
        self.assertEqual(h.readline(), '')
        ukijumuisha self.assertRaises(StopIteration):
            next(h)

    eleza test_next_data(self):
        # Check that next will correctly rudisha the next available
        # line na plays well ukijumuisha the dunder_iter part.
        mock = mock_open(read_data='foo\nbar\nbaz\n')
        ukijumuisha patch('%s.open' % __name__, mock, create=Kweli):
            h = open('bar')
            line1 = next(h)
            line2 = next(h)
            lines = [l kila l kwenye h]
        self.assertEqual(line1, 'foo\n')
        self.assertEqual(line2, 'bar\n')
        self.assertEqual(lines[0], 'baz\n')
        self.assertEqual(h.readline(), '')

    eleza test_readlines_data(self):
        # Test that emulating a file that ends kwenye a newline character works
        mock = mock_open(read_data='foo\nbar\nbaz\n')
        ukijumuisha patch('%s.open' % __name__, mock, create=Kweli):
            h = open('bar')
            result = h.readlines()
        self.assertEqual(result, ['foo\n', 'bar\n', 'baz\n'])

        # Test that files without a final newline will also be correctly
        # emulated
        mock = mock_open(read_data='foo\nbar\nbaz')
        ukijumuisha patch('%s.open' % __name__, mock, create=Kweli):
            h = open('bar')
            result = h.readlines()

        self.assertEqual(result, ['foo\n', 'bar\n', 'baz'])


    eleza test_read_bytes(self):
        mock = mock_open(read_data=b'\xc6')
        ukijumuisha patch('%s.open' % __name__, mock, create=Kweli):
            ukijumuisha open('abc', 'rb') as f:
                result = f.read()
        self.assertEqual(result, b'\xc6')


    eleza test_readline_bytes(self):
        m = mock_open(read_data=b'abc\ndef\nghi\n')
        ukijumuisha patch('%s.open' % __name__, m, create=Kweli):
            ukijumuisha open('abc', 'rb') as f:
                line1 = f.readline()
                line2 = f.readline()
                line3 = f.readline()
        self.assertEqual(line1, b'abc\n')
        self.assertEqual(line2, b'def\n')
        self.assertEqual(line3, b'ghi\n')


    eleza test_readlines_bytes(self):
        m = mock_open(read_data=b'abc\ndef\nghi\n')
        ukijumuisha patch('%s.open' % __name__, m, create=Kweli):
            ukijumuisha open('abc', 'rb') as f:
                result = f.readlines()
        self.assertEqual(result, [b'abc\n', b'def\n', b'ghi\n'])


    eleza test_mock_open_read_with_argument(self):
        # At one point calling read ukijumuisha an argument was broken
        # kila mocks returned by mock_open
        some_data = 'foo\nbar\nbaz'
        mock = mock_open(read_data=some_data)
        self.assertEqual(mock().read(10), some_data[:10])
        self.assertEqual(mock().read(10), some_data[:10])

        f = mock()
        self.assertEqual(f.read(10), some_data[:10])
        self.assertEqual(f.read(10), some_data[10:])


    eleza test_interleaved_reads(self):
        # Test that calling read, readline, na readlines pulls data
        # sequentially kutoka the data we preload with
        mock = mock_open(read_data='foo\nbar\nbaz\n')
        ukijumuisha patch('%s.open' % __name__, mock, create=Kweli):
            h = open('bar')
            line1 = h.readline()
            rest = h.readlines()
        self.assertEqual(line1, 'foo\n')
        self.assertEqual(rest, ['bar\n', 'baz\n'])

        mock = mock_open(read_data='foo\nbar\nbaz\n')
        ukijumuisha patch('%s.open' % __name__, mock, create=Kweli):
            h = open('bar')
            line1 = h.readline()
            rest = h.read()
        self.assertEqual(line1, 'foo\n')
        self.assertEqual(rest, 'bar\nbaz\n')


    eleza test_overriding_return_values(self):
        mock = mock_open(read_data='foo')
        handle = mock()

        handle.read.return_value = 'bar'
        handle.readline.return_value = 'bar'
        handle.readlines.return_value = ['bar']

        self.assertEqual(handle.read(), 'bar')
        self.assertEqual(handle.readline(), 'bar')
        self.assertEqual(handle.readlines(), ['bar'])

        # call repeatedly to check that a StopIteration ni sio propagated
        self.assertEqual(handle.readline(), 'bar')
        self.assertEqual(handle.readline(), 'bar')


ikiwa __name__ == '__main__':
    unittest.main()
