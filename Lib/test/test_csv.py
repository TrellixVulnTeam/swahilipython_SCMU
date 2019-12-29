# Copyright (C) 2001,2002 Python Software Foundation
# csv package unit tests

agiza copy
agiza sys
agiza unittest
kutoka io agiza StringIO
kutoka tempfile agiza TemporaryFile
agiza csv
agiza gc
agiza pickle
kutoka test agiza support
kutoka itertools agiza permutations
kutoka textwrap agiza dedent
kutoka collections agiza OrderedDict

kundi Test_Csv(unittest.TestCase):
    """
    Test the underlying C csv parser kwenye ways that are sio appropriate
    kutoka the high level interface. Further tests of this nature are done
    kwenye TestDialectRegistry.
    """
    eleza _test_arg_valid(self, ctor, arg):
        self.assertRaises(TypeError, ctor)
        self.assertRaises(TypeError, ctor, Tupu)
        self.assertRaises(TypeError, ctor, arg, bad_attr = 0)
        self.assertRaises(TypeError, ctor, arg, delimiter = 0)
        self.assertRaises(TypeError, ctor, arg, delimiter = 'XX')
        self.assertRaises(csv.Error, ctor, arg, 'foo')
        self.assertRaises(TypeError, ctor, arg, delimiter=Tupu)
        self.assertRaises(TypeError, ctor, arg, delimiter=1)
        self.assertRaises(TypeError, ctor, arg, quotechar=1)
        self.assertRaises(TypeError, ctor, arg, lineterminator=Tupu)
        self.assertRaises(TypeError, ctor, arg, lineterminator=1)
        self.assertRaises(TypeError, ctor, arg, quoting=Tupu)
        self.assertRaises(TypeError, ctor, arg,
                          quoting=csv.QUOTE_ALL, quotechar='')
        self.assertRaises(TypeError, ctor, arg,
                          quoting=csv.QUOTE_ALL, quotechar=Tupu)

    eleza test_reader_arg_valid(self):
        self._test_arg_valid(csv.reader, [])

    eleza test_writer_arg_valid(self):
        self._test_arg_valid(csv.writer, StringIO())

    eleza _test_default_attrs(self, ctor, *args):
        obj = ctor(*args)
        # Check defaults
        self.assertEqual(obj.dialect.delimiter, ',')
        self.assertIs(obj.dialect.doublequote, Kweli)
        self.assertEqual(obj.dialect.escapechar, Tupu)
        self.assertEqual(obj.dialect.lineterminator, "\r\n")
        self.assertEqual(obj.dialect.quotechar, '"')
        self.assertEqual(obj.dialect.quoting, csv.QUOTE_MINIMAL)
        self.assertIs(obj.dialect.skipinitialspace, Uongo)
        self.assertIs(obj.dialect.strict, Uongo)
        # Try deleting ama changing attributes (they are read-only)
        self.assertRaises(AttributeError, delattr, obj.dialect, 'delimiter')
        self.assertRaises(AttributeError, setattr, obj.dialect, 'delimiter', ':')
        self.assertRaises(AttributeError, delattr, obj.dialect, 'quoting')
        self.assertRaises(AttributeError, setattr, obj.dialect,
                          'quoting', Tupu)

    eleza test_reader_attrs(self):
        self._test_default_attrs(csv.reader, [])

    eleza test_writer_attrs(self):
        self._test_default_attrs(csv.writer, StringIO())

    eleza _test_kw_attrs(self, ctor, *args):
        # Now try with alternate options
        kwargs = dict(delimiter=':', doublequote=Uongo, escapechar='\\',
                      lineterminator='\r', quotechar='*',
                      quoting=csv.QUOTE_NONE, skipinitialspace=Kweli,
                      strict=Kweli)
        obj = ctor(*args, **kwargs)
        self.assertEqual(obj.dialect.delimiter, ':')
        self.assertIs(obj.dialect.doublequote, Uongo)
        self.assertEqual(obj.dialect.escapechar, '\\')
        self.assertEqual(obj.dialect.lineterminator, "\r")
        self.assertEqual(obj.dialect.quotechar, '*')
        self.assertEqual(obj.dialect.quoting, csv.QUOTE_NONE)
        self.assertIs(obj.dialect.skipinitialspace, Kweli)
        self.assertIs(obj.dialect.strict, Kweli)

    eleza test_reader_kw_attrs(self):
        self._test_kw_attrs(csv.reader, [])

    eleza test_writer_kw_attrs(self):
        self._test_kw_attrs(csv.writer, StringIO())

    eleza _test_dialect_attrs(self, ctor, *args):
        # Now try with dialect-derived options
        kundi dialect:
            delimiter='-'
            doublequote=Uongo
            escapechar='^'
            lineterminator='$'
            quotechar='#'
            quoting=csv.QUOTE_ALL
            skipinitialspace=Kweli
            strict=Uongo
        args = args + (dialect,)
        obj = ctor(*args)
        self.assertEqual(obj.dialect.delimiter, '-')
        self.assertIs(obj.dialect.doublequote, Uongo)
        self.assertEqual(obj.dialect.escapechar, '^')
        self.assertEqual(obj.dialect.lineterminator, "$")
        self.assertEqual(obj.dialect.quotechar, '#')
        self.assertEqual(obj.dialect.quoting, csv.QUOTE_ALL)
        self.assertIs(obj.dialect.skipinitialspace, Kweli)
        self.assertIs(obj.dialect.strict, Uongo)

    eleza test_reader_dialect_attrs(self):
        self._test_dialect_attrs(csv.reader, [])

    eleza test_writer_dialect_attrs(self):
        self._test_dialect_attrs(csv.writer, StringIO())


    eleza _write_test(self, fields, expect, **kwargs):
        with TemporaryFile("w+", newline='') kama fileobj:
            writer = csv.writer(fileobj, **kwargs)
            writer.writerow(fields)
            fileobj.seek(0)
            self.assertEqual(fileobj.read(),
                             expect + writer.dialect.lineterminator)

    eleza _write_error_test(self, exc, fields, **kwargs):
        with TemporaryFile("w+", newline='') kama fileobj:
            writer = csv.writer(fileobj, **kwargs)
            with self.assertRaises(exc):
                writer.writerow(fields)
            fileobj.seek(0)
            self.assertEqual(fileobj.read(), '')

    eleza test_write_arg_valid(self):
        self._write_error_test(csv.Error, Tupu)
        self._write_test((), '')
        self._write_test([Tupu], '""')
        self._write_error_test(csv.Error, [Tupu], quoting = csv.QUOTE_NONE)
        # Check that exceptions are pitaed up the chain
        kundi BadList:
            eleza __len__(self):
                rudisha 10;
            eleza __getitem__(self, i):
                ikiwa i > 2:
                    ashiria OSError
        self._write_error_test(OSError, BadList())
        kundi BadItem:
            eleza __str__(self):
                ashiria OSError
        self._write_error_test(OSError, [BadItem()])

    eleza test_write_bigfield(self):
        # This exercises the buffer realloc functionality
        bigstring = 'X' * 50000
        self._write_test([bigstring,bigstring], '%s,%s' % \
                         (bigstring, bigstring))

    eleza test_write_quoting(self):
        self._write_test(['a',1,'p,q'], 'a,1,"p,q"')
        self._write_error_test(csv.Error, ['a',1,'p,q'],
                               quoting = csv.QUOTE_NONE)
        self._write_test(['a',1,'p,q'], 'a,1,"p,q"',
                         quoting = csv.QUOTE_MINIMAL)
        self._write_test(['a',1,'p,q'], '"a",1,"p,q"',
                         quoting = csv.QUOTE_NONNUMERIC)
        self._write_test(['a',1,'p,q'], '"a","1","p,q"',
                         quoting = csv.QUOTE_ALL)
        self._write_test(['a\nb',1], '"a\nb","1"',
                         quoting = csv.QUOTE_ALL)

    eleza test_write_escape(self):
        self._write_test(['a',1,'p,q'], 'a,1,"p,q"',
                         escapechar='\\')
        self._write_error_test(csv.Error, ['a',1,'p,"q"'],
                               escapechar=Tupu, doublequote=Uongo)
        self._write_test(['a',1,'p,"q"'], 'a,1,"p,\\"q\\""',
                         escapechar='\\', doublequote = Uongo)
        self._write_test(['"'], '""""',
                         escapechar='\\', quoting = csv.QUOTE_MINIMAL)
        self._write_test(['"'], '\\"',
                         escapechar='\\', quoting = csv.QUOTE_MINIMAL,
                         doublequote = Uongo)
        self._write_test(['"'], '\\"',
                         escapechar='\\', quoting = csv.QUOTE_NONE)
        self._write_test(['a',1,'p,q'], 'a,1,p\\,q',
                         escapechar='\\', quoting = csv.QUOTE_NONE)

    eleza test_write_iterable(self):
        self._write_test(iter(['a', 1, 'p,q']), 'a,1,"p,q"')
        self._write_test(iter(['a', 1, Tupu]), 'a,1,')
        self._write_test(iter([]), '')
        self._write_test(iter([Tupu]), '""')
        self._write_error_test(csv.Error, iter([Tupu]), quoting=csv.QUOTE_NONE)
        self._write_test(iter([Tupu, Tupu]), ',')

    eleza test_writerows(self):
        kundi BrokenFile:
            eleza write(self, buf):
                ashiria OSError
        writer = csv.writer(BrokenFile())
        self.assertRaises(OSError, writer.writerows, [['a']])

        with TemporaryFile("w+", newline='') kama fileobj:
            writer = csv.writer(fileobj)
            self.assertRaises(TypeError, writer.writerows, Tupu)
            writer.writerows([['a', 'b'], ['c', 'd']])
            fileobj.seek(0)
            self.assertEqual(fileobj.read(), "a,b\r\nc,d\r\n")

    eleza test_writerows_with_none(self):
        with TemporaryFile("w+", newline='') kama fileobj:
            writer = csv.writer(fileobj)
            writer.writerows([['a', Tupu], [Tupu, 'd']])
            fileobj.seek(0)
            self.assertEqual(fileobj.read(), "a,\r\n,d\r\n")

        with TemporaryFile("w+", newline='') kama fileobj:
            writer = csv.writer(fileobj)
            writer.writerows([[Tupu], ['a']])
            fileobj.seek(0)
            self.assertEqual(fileobj.read(), '""\r\na\r\n')

        with TemporaryFile("w+", newline='') kama fileobj:
            writer = csv.writer(fileobj)
            writer.writerows([['a'], [Tupu]])
            fileobj.seek(0)
            self.assertEqual(fileobj.read(), 'a\r\n""\r\n')

    @support.cpython_only
    eleza test_writerows_legacy_strings(self):
        agiza _testcapi

        c = _testcapi.unicode_legacy_string('a')
        with TemporaryFile("w+", newline='') kama fileobj:
            writer = csv.writer(fileobj)
            writer.writerows([[c]])
            fileobj.seek(0)
            self.assertEqual(fileobj.read(), "a\r\n")

    eleza _read_test(self, input, expect, **kwargs):
        reader = csv.reader(input, **kwargs)
        result = list(reader)
        self.assertEqual(result, expect)

    eleza test_read_oddinputs(self):
        self._read_test([], [])
        self._read_test([''], [[]])
        self.assertRaises(csv.Error, self._read_test,
                          ['"ab"c'], Tupu, strict = 1)
        # cannot handle null bytes kila the moment
        self.assertRaises(csv.Error, self._read_test,
                          ['ab\0c'], Tupu, strict = 1)
        self._read_test(['"ab"c'], [['abc']], doublequote = 0)

        self.assertRaises(csv.Error, self._read_test,
                          [b'ab\0c'], Tupu)


    eleza test_read_eol(self):
        self._read_test(['a,b'], [['a','b']])
        self._read_test(['a,b\n'], [['a','b']])
        self._read_test(['a,b\r\n'], [['a','b']])
        self._read_test(['a,b\r'], [['a','b']])
        self.assertRaises(csv.Error, self._read_test, ['a,b\rc,d'], [])
        self.assertRaises(csv.Error, self._read_test, ['a,b\nc,d'], [])
        self.assertRaises(csv.Error, self._read_test, ['a,b\r\nc,d'], [])

    eleza test_read_eof(self):
        self._read_test(['a,"'], [['a', '']])
        self._read_test(['"a'], [['a']])
        self._read_test(['^'], [['\n']], escapechar='^')
        self.assertRaises(csv.Error, self._read_test, ['a,"'], [], strict=Kweli)
        self.assertRaises(csv.Error, self._read_test, ['"a'], [], strict=Kweli)
        self.assertRaises(csv.Error, self._read_test,
                          ['^'], [], escapechar='^', strict=Kweli)

    eleza test_read_escape(self):
        self._read_test(['a,\\b,c'], [['a', 'b', 'c']], escapechar='\\')
        self._read_test(['a,b\\,c'], [['a', 'b,c']], escapechar='\\')
        self._read_test(['a,"b\\,c"'], [['a', 'b,c']], escapechar='\\')
        self._read_test(['a,"b,\\c"'], [['a', 'b,c']], escapechar='\\')
        self._read_test(['a,"b,c\\""'], [['a', 'b,c"']], escapechar='\\')
        self._read_test(['a,"b,c"\\'], [['a', 'b,c\\']], escapechar='\\')

    eleza test_read_quoting(self):
        self._read_test(['1,",3,",5'], [['1', ',3,', '5']])
        self._read_test(['1,",3,",5'], [['1', '"', '3', '"', '5']],
                        quotechar=Tupu, escapechar='\\')
        self._read_test(['1,",3,",5'], [['1', '"', '3', '"', '5']],
                        quoting=csv.QUOTE_NONE, escapechar='\\')
        # will this fail where locale uses comma kila decimals?
        self._read_test([',3,"5",7.3, 9'], [['', 3, '5', 7.3, 9]],
                        quoting=csv.QUOTE_NONNUMERIC)
        self._read_test(['"a\nb", 7'], [['a\nb', ' 7']])
        self.assertRaises(ValueError, self._read_test,
                          ['abc,3'], [[]],
                          quoting=csv.QUOTE_NONNUMERIC)

    eleza test_read_bigfield(self):
        # This exercises the buffer realloc functionality na field size
        # limits.
        limit = csv.field_size_limit()
        jaribu:
            size = 50000
            bigstring = 'X' * size
            bigline = '%s,%s' % (bigstring, bigstring)
            self._read_test([bigline], [[bigstring, bigstring]])
            csv.field_size_limit(size)
            self._read_test([bigline], [[bigstring, bigstring]])
            self.assertEqual(csv.field_size_limit(), size)
            csv.field_size_limit(size-1)
            self.assertRaises(csv.Error, self._read_test, [bigline], [])
            self.assertRaises(TypeError, csv.field_size_limit, Tupu)
            self.assertRaises(TypeError, csv.field_size_limit, 1, Tupu)
        mwishowe:
            csv.field_size_limit(limit)

    eleza test_read_linenum(self):
        r = csv.reader(['line,1', 'line,2', 'line,3'])
        self.assertEqual(r.line_num, 0)
        next(r)
        self.assertEqual(r.line_num, 1)
        next(r)
        self.assertEqual(r.line_num, 2)
        next(r)
        self.assertEqual(r.line_num, 3)
        self.assertRaises(StopIteration, next, r)
        self.assertEqual(r.line_num, 3)

    eleza test_roundtrip_quoteed_newlines(self):
        with TemporaryFile("w+", newline='') kama fileobj:
            writer = csv.writer(fileobj)
            self.assertRaises(TypeError, writer.writerows, Tupu)
            rows = [['a\nb','b'],['c','x\r\nd']]
            writer.writerows(rows)
            fileobj.seek(0)
            kila i, row kwenye enumerate(csv.reader(fileobj)):
                self.assertEqual(row, rows[i])

    eleza test_roundtrip_escaped_unquoted_newlines(self):
        with TemporaryFile("w+", newline='') kama fileobj:
            writer = csv.writer(fileobj,quoting=csv.QUOTE_NONE,escapechar="\\")
            rows = [['a\nb','b'],['c','x\r\nd']]
            writer.writerows(rows)
            fileobj.seek(0)
            kila i, row kwenye enumerate(csv.reader(fileobj,quoting=csv.QUOTE_NONE,escapechar="\\")):
                self.assertEqual(row,rows[i])

kundi TestDialectRegistry(unittest.TestCase):
    eleza test_registry_badargs(self):
        self.assertRaises(TypeError, csv.list_dialects, Tupu)
        self.assertRaises(TypeError, csv.get_dialect)
        self.assertRaises(csv.Error, csv.get_dialect, Tupu)
        self.assertRaises(csv.Error, csv.get_dialect, "nonesuch")
        self.assertRaises(TypeError, csv.unregister_dialect)
        self.assertRaises(csv.Error, csv.unregister_dialect, Tupu)
        self.assertRaises(csv.Error, csv.unregister_dialect, "nonesuch")
        self.assertRaises(TypeError, csv.register_dialect, Tupu)
        self.assertRaises(TypeError, csv.register_dialect, Tupu, Tupu)
        self.assertRaises(TypeError, csv.register_dialect, "nonesuch", 0, 0)
        self.assertRaises(TypeError, csv.register_dialect, "nonesuch",
                          badargument=Tupu)
        self.assertRaises(TypeError, csv.register_dialect, "nonesuch",
                          quoting=Tupu)
        self.assertRaises(TypeError, csv.register_dialect, [])

    eleza test_registry(self):
        kundi myexceltsv(csv.excel):
            delimiter = "\t"
        name = "myexceltsv"
        expected_dialects = csv.list_dialects() + [name]
        expected_dialects.sort()
        csv.register_dialect(name, myexceltsv)
        self.addCleanup(csv.unregister_dialect, name)
        self.assertEqual(csv.get_dialect(name).delimiter, '\t')
        got_dialects = sorted(csv.list_dialects())
        self.assertEqual(expected_dialects, got_dialects)

    eleza test_register_kwargs(self):
        name = 'fedcba'
        csv.register_dialect(name, delimiter=';')
        self.addCleanup(csv.unregister_dialect, name)
        self.assertEqual(csv.get_dialect(name).delimiter, ';')
        self.assertEqual([['X', 'Y', 'Z']], list(csv.reader(['X;Y;Z'], name)))

    eleza test_incomplete_dialect(self):
        kundi myexceltsv(csv.Dialect):
            delimiter = "\t"
        self.assertRaises(csv.Error, myexceltsv)

    eleza test_space_dialect(self):
        kundi space(csv.excel):
            delimiter = " "
            quoting = csv.QUOTE_NONE
            escapechar = "\\"

        with TemporaryFile("w+") kama fileobj:
            fileobj.write("abc def\nc1ccccc1 benzene\n")
            fileobj.seek(0)
            reader = csv.reader(fileobj, dialect=space())
            self.assertEqual(next(reader), ["abc", "def"])
            self.assertEqual(next(reader), ["c1ccccc1", "benzene"])

    eleza compare_dialect_123(self, expected, *writeargs, **kwwriteargs):

        with TemporaryFile("w+", newline='', encoding="utf-8") kama fileobj:

            writer = csv.writer(fileobj, *writeargs, **kwwriteargs)
            writer.writerow([1,2,3])
            fileobj.seek(0)
            self.assertEqual(fileobj.read(), expected)

    eleza test_dialect_apply(self):
        kundi testA(csv.excel):
            delimiter = "\t"
        kundi testB(csv.excel):
            delimiter = ":"
        kundi testC(csv.excel):
            delimiter = "|"
        kundi testUni(csv.excel):
            delimiter = "\u039B"

        csv.register_dialect('testC', testC)
        jaribu:
            self.compare_dialect_123("1,2,3\r\n")
            self.compare_dialect_123("1\t2\t3\r\n", testA)
            self.compare_dialect_123("1:2:3\r\n", dialect=testB())
            self.compare_dialect_123("1|2|3\r\n", dialect='testC')
            self.compare_dialect_123("1;2;3\r\n", dialect=testA,
                                     delimiter=';')
            self.compare_dialect_123("1\u039B2\u039B3\r\n",
                                     dialect=testUni)

        mwishowe:
            csv.unregister_dialect('testC')

    eleza test_bad_dialect(self):
        # Unknown parameter
        self.assertRaises(TypeError, csv.reader, [], bad_attr = 0)
        # Bad values
        self.assertRaises(TypeError, csv.reader, [], delimiter = Tupu)
        self.assertRaises(TypeError, csv.reader, [], quoting = -1)
        self.assertRaises(TypeError, csv.reader, [], quoting = 100)

    eleza test_copy(self):
        kila name kwenye csv.list_dialects():
            dialect = csv.get_dialect(name)
            self.assertRaises(TypeError, copy.copy, dialect)

    eleza test_pickle(self):
        kila name kwenye csv.list_dialects():
            dialect = csv.get_dialect(name)
            kila proto kwenye range(pickle.HIGHEST_PROTOCOL + 1):
                self.assertRaises(TypeError, pickle.dumps, dialect, proto)

kundi TestCsvBase(unittest.TestCase):
    eleza readerAssertEqual(self, input, expected_result):
        with TemporaryFile("w+", newline='') kama fileobj:
            fileobj.write(input)
            fileobj.seek(0)
            reader = csv.reader(fileobj, dialect = self.dialect)
            fields = list(reader)
            self.assertEqual(fields, expected_result)

    eleza writerAssertEqual(self, input, expected_result):
        with TemporaryFile("w+", newline='') kama fileobj:
            writer = csv.writer(fileobj, dialect = self.dialect)
            writer.writerows(input)
            fileobj.seek(0)
            self.assertEqual(fileobj.read(), expected_result)

kundi TestDialectExcel(TestCsvBase):
    dialect = 'excel'

    eleza test_single(self):
        self.readerAssertEqual('abc', [['abc']])

    eleza test_simple(self):
        self.readerAssertEqual('1,2,3,4,5', [['1','2','3','4','5']])

    eleza test_blankline(self):
        self.readerAssertEqual('', [])

    eleza test_empty_fields(self):
        self.readerAssertEqual(',', [['', '']])

    eleza test_singlequoted(self):
        self.readerAssertEqual('""', [['']])

    eleza test_singlequoted_left_empty(self):
        self.readerAssertEqual('"",', [['','']])

    eleza test_singlequoted_right_empty(self):
        self.readerAssertEqual(',""', [['','']])

    eleza test_single_quoted_quote(self):
        self.readerAssertEqual('""""', [['"']])

    eleza test_quoted_quotes(self):
        self.readerAssertEqual('""""""', [['""']])

    eleza test_inline_quote(self):
        self.readerAssertEqual('a""b', [['a""b']])

    eleza test_inline_quotes(self):
        self.readerAssertEqual('a"b"c', [['a"b"c']])

    eleza test_quotes_and_more(self):
        # Excel would never write a field containing '"a"b', but when
        # reading one, it will rudisha 'ab'.
        self.readerAssertEqual('"a"b', [['ab']])

    eleza test_lone_quote(self):
        self.readerAssertEqual('a"b', [['a"b']])

    eleza test_quote_and_quote(self):
        # Excel would never write a field containing '"a" "b"', but when
        # reading one, it will rudisha 'a "b"'.
        self.readerAssertEqual('"a" "b"', [['a "b"']])

    eleza test_space_and_quote(self):
        self.readerAssertEqual(' "a"', [[' "a"']])

    eleza test_quoted(self):
        self.readerAssertEqual('1,2,3,"I think, therefore I am",5,6',
                               [['1', '2', '3',
                                 'I think, therefore I am',
                                 '5', '6']])

    eleza test_quoted_quote(self):
        self.readerAssertEqual('1,2,3,"""I see,"" said the blind man","as he picked up his hammer na saw"',
                               [['1', '2', '3',
                                 '"I see," said the blind man',
                                 'as he picked up his hammer na saw']])

    eleza test_quoted_nl(self):
        input = '''\
1,2,3,"""I see,""
said the blind man","as he picked up his
hammer na saw"
9,8,7,6'''
        self.readerAssertEqual(input,
                               [['1', '2', '3',
                                   '"I see,"\nsaid the blind man',
                                   'as he picked up his\nhammer na saw'],
                                ['9','8','7','6']])

    eleza test_dubious_quote(self):
        self.readerAssertEqual('12,12,1",', [['12', '12', '1"', '']])

    eleza test_null(self):
        self.writerAssertEqual([], '')

    eleza test_single_writer(self):
        self.writerAssertEqual([['abc']], 'abc\r\n')

    eleza test_simple_writer(self):
        self.writerAssertEqual([[1, 2, 'abc', 3, 4]], '1,2,abc,3,4\r\n')

    eleza test_quotes(self):
        self.writerAssertEqual([[1, 2, 'a"bc"', 3, 4]], '1,2,"a""bc""",3,4\r\n')

    eleza test_quote_fieldsep(self):
        self.writerAssertEqual([['abc,def']], '"abc,def"\r\n')

    eleza test_newlines(self):
        self.writerAssertEqual([[1, 2, 'a\nbc', 3, 4]], '1,2,"a\nbc",3,4\r\n')

kundi EscapedExcel(csv.excel):
    quoting = csv.QUOTE_NONE
    escapechar = '\\'

kundi TestEscapedExcel(TestCsvBase):
    dialect = EscapedExcel()

    eleza test_escape_fieldsep(self):
        self.writerAssertEqual([['abc,def']], 'abc\\,def\r\n')

    eleza test_read_escape_fieldsep(self):
        self.readerAssertEqual('abc\\,def\r\n', [['abc,def']])

kundi TestDialectUnix(TestCsvBase):
    dialect = 'unix'

    eleza test_simple_writer(self):
        self.writerAssertEqual([[1, 'abc def', 'abc']], '"1","abc def","abc"\n')

    eleza test_simple_reader(self):
        self.readerAssertEqual('"1","abc def","abc"\n', [['1', 'abc def', 'abc']])

kundi QuotedEscapedExcel(csv.excel):
    quoting = csv.QUOTE_NONNUMERIC
    escapechar = '\\'

kundi TestQuotedEscapedExcel(TestCsvBase):
    dialect = QuotedEscapedExcel()

    eleza test_write_escape_fieldsep(self):
        self.writerAssertEqual([['abc,def']], '"abc,def"\r\n')

    eleza test_read_escape_fieldsep(self):
        self.readerAssertEqual('"abc\\,def"\r\n', [['abc,def']])

kundi TestDictFields(unittest.TestCase):
    ### "long" means the row ni longer than the number of fieldnames
    ### "short" means there are fewer elements kwenye the row than fieldnames
    eleza test_writeheader_rudisha_value(self):
        with TemporaryFile("w+", newline='') kama fileobj:
            writer = csv.DictWriter(fileobj, fieldnames = ["f1", "f2", "f3"])
            writeheader_rudisha_value = writer.writeheader()
            self.assertEqual(writeheader_rudisha_value, 10)

    eleza test_write_simple_dict(self):
        with TemporaryFile("w+", newline='') kama fileobj:
            writer = csv.DictWriter(fileobj, fieldnames = ["f1", "f2", "f3"])
            writer.writeheader()
            fileobj.seek(0)
            self.assertEqual(fileobj.readline(), "f1,f2,f3\r\n")
            writer.writerow({"f1": 10, "f3": "abc"})
            fileobj.seek(0)
            fileobj.readline() # header
            self.assertEqual(fileobj.read(), "10,,abc\r\n")

    eleza test_write_multiple_dict_rows(self):
        fileobj = StringIO()
        writer = csv.DictWriter(fileobj, fieldnames=["f1", "f2", "f3"])
        writer.writeheader()
        self.assertEqual(fileobj.getvalue(), "f1,f2,f3\r\n")
        writer.writerows([{"f1": 1, "f2": "abc", "f3": "f"},
                          {"f1": 2, "f2": 5, "f3": "xyz"}])
        self.assertEqual(fileobj.getvalue(),
                         "f1,f2,f3\r\n1,abc,f\r\n2,5,xyz\r\n")

    eleza test_write_no_fields(self):
        fileobj = StringIO()
        self.assertRaises(TypeError, csv.DictWriter, fileobj)

    eleza test_write_fields_not_in_fieldnames(self):
        with TemporaryFile("w+", newline='') kama fileobj:
            writer = csv.DictWriter(fileobj, fieldnames = ["f1", "f2", "f3"])
            # Of special note ni the non-string key (issue 19449)
            with self.assertRaises(ValueError) kama cx:
                writer.writerow({"f4": 10, "f2": "spam", 1: "abc"})
            exception = str(cx.exception)
            self.assertIn("fieldnames", exception)
            self.assertIn("'f4'", exception)
            self.assertNotIn("'f2'", exception)
            self.assertIn("1", exception)

    eleza test_typo_in_extrasaction_ashirias_error(self):
        fileobj = StringIO()
        self.assertRaises(ValueError, csv.DictWriter, fileobj, ['f1', 'f2'],
                          extrasaction="ashiriad")

    eleza test_write_field_not_in_field_names_ashiria(self):
        fileobj = StringIO()
        writer = csv.DictWriter(fileobj, ['f1', 'f2'], extrasaction="ashiria")
        dictrow = {'f0': 0, 'f1': 1, 'f2': 2, 'f3': 3}
        self.assertRaises(ValueError, csv.DictWriter.writerow, writer, dictrow)

    eleza test_write_field_not_in_field_names_ignore(self):
        fileobj = StringIO()
        writer = csv.DictWriter(fileobj, ['f1', 'f2'], extrasaction="ignore")
        dictrow = {'f0': 0, 'f1': 1, 'f2': 2, 'f3': 3}
        csv.DictWriter.writerow(writer, dictrow)
        self.assertEqual(fileobj.getvalue(), "1,2\r\n")

    eleza test_read_dict_fields(self):
        with TemporaryFile("w+") kama fileobj:
            fileobj.write("1,2,abc\r\n")
            fileobj.seek(0)
            reader = csv.DictReader(fileobj,
                                    fieldnames=["f1", "f2", "f3"])
            self.assertEqual(next(reader), {"f1": '1', "f2": '2', "f3": 'abc'})

    eleza test_read_dict_no_fieldnames(self):
        with TemporaryFile("w+") kama fileobj:
            fileobj.write("f1,f2,f3\r\n1,2,abc\r\n")
            fileobj.seek(0)
            reader = csv.DictReader(fileobj)
            self.assertEqual(next(reader), {"f1": '1', "f2": '2', "f3": 'abc'})
            self.assertEqual(reader.fieldnames, ["f1", "f2", "f3"])

    # Two test cases to make sure existing ways of implicitly setting
    # fieldnames endelea to work.  Both arise kutoka discussion kwenye issue3436.
    eleza test_read_dict_fieldnames_kutoka_file(self):
        with TemporaryFile("w+") kama fileobj:
            fileobj.write("f1,f2,f3\r\n1,2,abc\r\n")
            fileobj.seek(0)
            reader = csv.DictReader(fileobj,
                                    fieldnames=next(csv.reader(fileobj)))
            self.assertEqual(reader.fieldnames, ["f1", "f2", "f3"])
            self.assertEqual(next(reader), {"f1": '1', "f2": '2', "f3": 'abc'})

    eleza test_read_dict_fieldnames_chain(self):
        agiza itertools
        with TemporaryFile("w+") kama fileobj:
            fileobj.write("f1,f2,f3\r\n1,2,abc\r\n")
            fileobj.seek(0)
            reader = csv.DictReader(fileobj)
            first = next(reader)
            kila row kwenye itertools.chain([first], reader):
                self.assertEqual(reader.fieldnames, ["f1", "f2", "f3"])
                self.assertEqual(row, {"f1": '1', "f2": '2', "f3": 'abc'})

    eleza test_read_long(self):
        with TemporaryFile("w+") kama fileobj:
            fileobj.write("1,2,abc,4,5,6\r\n")
            fileobj.seek(0)
            reader = csv.DictReader(fileobj,
                                    fieldnames=["f1", "f2"])
            self.assertEqual(next(reader), {"f1": '1', "f2": '2',
                                             Tupu: ["abc", "4", "5", "6"]})

    eleza test_read_long_with_rest(self):
        with TemporaryFile("w+") kama fileobj:
            fileobj.write("1,2,abc,4,5,6\r\n")
            fileobj.seek(0)
            reader = csv.DictReader(fileobj,
                                    fieldnames=["f1", "f2"], restkey="_rest")
            self.assertEqual(next(reader), {"f1": '1', "f2": '2',
                                             "_rest": ["abc", "4", "5", "6"]})

    eleza test_read_long_with_rest_no_fieldnames(self):
        with TemporaryFile("w+") kama fileobj:
            fileobj.write("f1,f2\r\n1,2,abc,4,5,6\r\n")
            fileobj.seek(0)
            reader = csv.DictReader(fileobj, restkey="_rest")
            self.assertEqual(reader.fieldnames, ["f1", "f2"])
            self.assertEqual(next(reader), {"f1": '1', "f2": '2',
                                             "_rest": ["abc", "4", "5", "6"]})

    eleza test_read_short(self):
        with TemporaryFile("w+") kama fileobj:
            fileobj.write("1,2,abc,4,5,6\r\n1,2,abc\r\n")
            fileobj.seek(0)
            reader = csv.DictReader(fileobj,
                                    fieldnames="1 2 3 4 5 6".split(),
                                    restval="DEFAULT")
            self.assertEqual(next(reader), {"1": '1', "2": '2', "3": 'abc',
                                             "4": '4', "5": '5', "6": '6'})
            self.assertEqual(next(reader), {"1": '1', "2": '2', "3": 'abc',
                                             "4": 'DEFAULT', "5": 'DEFAULT',
                                             "6": 'DEFAULT'})

    eleza test_read_multi(self):
        sample = [
            '2147483648,43.0e12,17,abc,def\r\n',
            '147483648,43.0e2,17,abc,def\r\n',
            '47483648,43.0,170,abc,def\r\n'
            ]

        reader = csv.DictReader(sample,
                                fieldnames="i1 float i2 s1 s2".split())
        self.assertEqual(next(reader), {"i1": '2147483648',
                                         "float": '43.0e12',
                                         "i2": '17',
                                         "s1": 'abc',
                                         "s2": 'def'})

    eleza test_read_with_blanks(self):
        reader = csv.DictReader(["1,2,abc,4,5,6\r\n","\r\n",
                                 "1,2,abc,4,5,6\r\n"],
                                fieldnames="1 2 3 4 5 6".split())
        self.assertEqual(next(reader), {"1": '1', "2": '2', "3": 'abc',
                                         "4": '4', "5": '5', "6": '6'})
        self.assertEqual(next(reader), {"1": '1', "2": '2', "3": 'abc',
                                         "4": '4', "5": '5', "6": '6'})

    eleza test_read_semi_sep(self):
        reader = csv.DictReader(["1;2;abc;4;5;6\r\n"],
                                fieldnames="1 2 3 4 5 6".split(),
                                delimiter=';')
        self.assertEqual(next(reader), {"1": '1', "2": '2', "3": 'abc',
                                         "4": '4', "5": '5', "6": '6'})

kundi TestArrayWrites(unittest.TestCase):
    eleza test_int_write(self):
        agiza array
        contents = [(20-i) kila i kwenye range(20)]
        a = array.array('i', contents)

        with TemporaryFile("w+", newline='') kama fileobj:
            writer = csv.writer(fileobj, dialect="excel")
            writer.writerow(a)
            expected = ",".join([str(i) kila i kwenye a])+"\r\n"
            fileobj.seek(0)
            self.assertEqual(fileobj.read(), expected)

    eleza test_double_write(self):
        agiza array
        contents = [(20-i)*0.1 kila i kwenye range(20)]
        a = array.array('d', contents)
        with TemporaryFile("w+", newline='') kama fileobj:
            writer = csv.writer(fileobj, dialect="excel")
            writer.writerow(a)
            expected = ",".join([str(i) kila i kwenye a])+"\r\n"
            fileobj.seek(0)
            self.assertEqual(fileobj.read(), expected)

    eleza test_float_write(self):
        agiza array
        contents = [(20-i)*0.1 kila i kwenye range(20)]
        a = array.array('f', contents)
        with TemporaryFile("w+", newline='') kama fileobj:
            writer = csv.writer(fileobj, dialect="excel")
            writer.writerow(a)
            expected = ",".join([str(i) kila i kwenye a])+"\r\n"
            fileobj.seek(0)
            self.assertEqual(fileobj.read(), expected)

    eleza test_char_write(self):
        agiza array, string
        a = array.array('u', string.ascii_letters)

        with TemporaryFile("w+", newline='') kama fileobj:
            writer = csv.writer(fileobj, dialect="excel")
            writer.writerow(a)
            expected = ",".join(a)+"\r\n"
            fileobj.seek(0)
            self.assertEqual(fileobj.read(), expected)

kundi TestDialectValidity(unittest.TestCase):
    eleza test_quoting(self):
        kundi mydialect(csv.Dialect):
            delimiter = ";"
            escapechar = '\\'
            doublequote = Uongo
            skipinitialspace = Kweli
            lineterminator = '\r\n'
            quoting = csv.QUOTE_NONE
        d = mydialect()
        self.assertEqual(d.quoting, csv.QUOTE_NONE)

        mydialect.quoting = Tupu
        self.assertRaises(csv.Error, mydialect)

        mydialect.doublequote = Kweli
        mydialect.quoting = csv.QUOTE_ALL
        mydialect.quotechar = '"'
        d = mydialect()
        self.assertEqual(d.quoting, csv.QUOTE_ALL)
        self.assertEqual(d.quotechar, '"')
        self.assertKweli(d.doublequote)

        mydialect.quotechar = "''"
        with self.assertRaises(csv.Error) kama cm:
            mydialect()
        self.assertEqual(str(cm.exception),
                         '"quotechar" must be a 1-character string')

        mydialect.quotechar = 4
        with self.assertRaises(csv.Error) kama cm:
            mydialect()
        self.assertEqual(str(cm.exception),
                         '"quotechar" must be string, sio int')

    eleza test_delimiter(self):
        kundi mydialect(csv.Dialect):
            delimiter = ";"
            escapechar = '\\'
            doublequote = Uongo
            skipinitialspace = Kweli
            lineterminator = '\r\n'
            quoting = csv.QUOTE_NONE
        d = mydialect()
        self.assertEqual(d.delimiter, ";")

        mydialect.delimiter = ":::"
        with self.assertRaises(csv.Error) kama cm:
            mydialect()
        self.assertEqual(str(cm.exception),
                         '"delimiter" must be a 1-character string')

        mydialect.delimiter = ""
        with self.assertRaises(csv.Error) kama cm:
            mydialect()
        self.assertEqual(str(cm.exception),
                         '"delimiter" must be a 1-character string')

        mydialect.delimiter = b","
        with self.assertRaises(csv.Error) kama cm:
            mydialect()
        self.assertEqual(str(cm.exception),
                         '"delimiter" must be string, sio bytes')

        mydialect.delimiter = 4
        with self.assertRaises(csv.Error) kama cm:
            mydialect()
        self.assertEqual(str(cm.exception),
                         '"delimiter" must be string, sio int')

    eleza test_lineterminator(self):
        kundi mydialect(csv.Dialect):
            delimiter = ";"
            escapechar = '\\'
            doublequote = Uongo
            skipinitialspace = Kweli
            lineterminator = '\r\n'
            quoting = csv.QUOTE_NONE
        d = mydialect()
        self.assertEqual(d.lineterminator, '\r\n')

        mydialect.lineterminator = ":::"
        d = mydialect()
        self.assertEqual(d.lineterminator, ":::")

        mydialect.lineterminator = 4
        with self.assertRaises(csv.Error) kama cm:
            mydialect()
        self.assertEqual(str(cm.exception),
                         '"lineterminator" must be a string')

    eleza test_invalid_chars(self):
        eleza create_invalid(field_name, value):
            kundi mydialect(csv.Dialect):
                pita
            setattr(mydialect, field_name, value)
            d = mydialect()

        kila field_name kwenye ("delimiter", "escapechar", "quotechar"):
            with self.subTest(field_name=field_name):
                self.assertRaises(csv.Error, create_invalid, field_name, "")
                self.assertRaises(csv.Error, create_invalid, field_name, "abc")
                self.assertRaises(csv.Error, create_invalid, field_name, b'x')
                self.assertRaises(csv.Error, create_invalid, field_name, 5)


kundi TestSniffer(unittest.TestCase):
    sample1 = """\
Harry's, Arlington Heights, IL, 2/1/03, Kimi Hayes
Shark City, Glendale Heights, IL, 12/28/02, Prezence
Tommy's Place, Blue Island, IL, 12/28/02, Blue Sunday/White Crow
Stonecutters Seafood na Chop House, Lemont, IL, 12/19/02, Week Back
"""
    sample2 = """\
'Harry''s':'Arlington Heights':'IL':'2/1/03':'Kimi Hayes'
'Shark City':'Glendale Heights':'IL':'12/28/02':'Prezence'
'Tommy''s Place':'Blue Island':'IL':'12/28/02':'Blue Sunday/White Crow'
'Stonecutters ''Seafood'' na Chop House':'Lemont':'IL':'12/19/02':'Week Back'
"""
    header1 = '''\
"venue","city","state","date","performers"
'''
    sample3 = '''\
05/05/03?05/05/03?05/05/03?05/05/03?05/05/03?05/05/03
05/05/03?05/05/03?05/05/03?05/05/03?05/05/03?05/05/03
05/05/03?05/05/03?05/05/03?05/05/03?05/05/03?05/05/03
'''

    sample4 = '''\
2147483648;43.0e12;17;abc;def
147483648;43.0e2;17;abc;def
47483648;43.0;170;abc;def
'''

    sample5 = "aaa\tbbb\r\nAAA\t\r\nBBB\t\r\n"
    sample6 = "a|b|c\r\nd|e|f\r\n"
    sample7 = "'a'|'b'|'c'\r\n'd'|e|f\r\n"

# Issue 18155: Use a delimiter that ni a special char to regex:

    header2 = '''\
"venue"+"city"+"state"+"date"+"performers"
'''
    sample8 = """\
Harry's+ Arlington Heights+ IL+ 2/1/03+ Kimi Hayes
Shark City+ Glendale Heights+ IL+ 12/28/02+ Prezence
Tommy's Place+ Blue Island+ IL+ 12/28/02+ Blue Sunday/White Crow
Stonecutters Seafood na Chop House+ Lemont+ IL+ 12/19/02+ Week Back
"""
    sample9 = """\
'Harry''s'+ Arlington Heights'+ 'IL'+ '2/1/03'+ 'Kimi Hayes'
'Shark City'+ Glendale Heights'+' IL'+ '12/28/02'+ 'Prezence'
'Tommy''s Place'+ Blue Island'+ 'IL'+ '12/28/02'+ 'Blue Sunday/White Crow'
'Stonecutters ''Seafood'' na Chop House'+ 'Lemont'+ 'IL'+ '12/19/02'+ 'Week Back'
"""

    eleza test_has_header(self):
        sniffer = csv.Sniffer()
        self.assertIs(sniffer.has_header(self.sample1), Uongo)
        self.assertIs(sniffer.has_header(self.header1 + self.sample1), Kweli)

    eleza test_has_header_regex_special_delimiter(self):
        sniffer = csv.Sniffer()
        self.assertIs(sniffer.has_header(self.sample8), Uongo)
        self.assertIs(sniffer.has_header(self.header2 + self.sample8), Kweli)

    eleza test_guess_quote_and_delimiter(self):
        sniffer = csv.Sniffer()
        kila header kwenye (";'123;4';", "'123;4';", ";'123;4'", "'123;4'"):
            with self.subTest(header):
                dialect = sniffer.sniff(header, ",;")
                self.assertEqual(dialect.delimiter, ';')
                self.assertEqual(dialect.quotechar, "'")
                self.assertIs(dialect.doublequote, Uongo)
                self.assertIs(dialect.skipinitialspace, Uongo)

    eleza test_sniff(self):
        sniffer = csv.Sniffer()
        dialect = sniffer.sniff(self.sample1)
        self.assertEqual(dialect.delimiter, ",")
        self.assertEqual(dialect.quotechar, '"')
        self.assertIs(dialect.skipinitialspace, Kweli)

        dialect = sniffer.sniff(self.sample2)
        self.assertEqual(dialect.delimiter, ":")
        self.assertEqual(dialect.quotechar, "'")
        self.assertIs(dialect.skipinitialspace, Uongo)

    eleza test_delimiters(self):
        sniffer = csv.Sniffer()
        dialect = sniffer.sniff(self.sample3)
        # given that all three lines kwenye sample3 are equal,
        # I think that any character could have been 'guessed' kama the
        # delimiter, depending on dictionary order
        self.assertIn(dialect.delimiter, self.sample3)
        dialect = sniffer.sniff(self.sample3, delimiters="?,")
        self.assertEqual(dialect.delimiter, "?")
        dialect = sniffer.sniff(self.sample3, delimiters="/,")
        self.assertEqual(dialect.delimiter, "/")
        dialect = sniffer.sniff(self.sample4)
        self.assertEqual(dialect.delimiter, ";")
        dialect = sniffer.sniff(self.sample5)
        self.assertEqual(dialect.delimiter, "\t")
        dialect = sniffer.sniff(self.sample6)
        self.assertEqual(dialect.delimiter, "|")
        dialect = sniffer.sniff(self.sample7)
        self.assertEqual(dialect.delimiter, "|")
        self.assertEqual(dialect.quotechar, "'")
        dialect = sniffer.sniff(self.sample8)
        self.assertEqual(dialect.delimiter, '+')
        dialect = sniffer.sniff(self.sample9)
        self.assertEqual(dialect.delimiter, '+')
        self.assertEqual(dialect.quotechar, "'")

    eleza test_doublequote(self):
        sniffer = csv.Sniffer()
        dialect = sniffer.sniff(self.header1)
        self.assertUongo(dialect.doublequote)
        dialect = sniffer.sniff(self.header2)
        self.assertUongo(dialect.doublequote)
        dialect = sniffer.sniff(self.sample2)
        self.assertKweli(dialect.doublequote)
        dialect = sniffer.sniff(self.sample8)
        self.assertUongo(dialect.doublequote)
        dialect = sniffer.sniff(self.sample9)
        self.assertKweli(dialect.doublequote)

kundi NUL:
    eleza write(s, *args):
        pita
    writelines = write

@unittest.skipUnless(hasattr(sys, "gettotalrefcount"),
                     'requires sys.gettotalrefcount()')
kundi TestLeaks(unittest.TestCase):
    eleza test_create_read(self):
        delta = 0
        lastrc = sys.gettotalrefcount()
        kila i kwenye range(20):
            gc.collect()
            self.assertEqual(gc.garbage, [])
            rc = sys.gettotalrefcount()
            csv.reader(["a,b,c\r\n"])
            csv.reader(["a,b,c\r\n"])
            csv.reader(["a,b,c\r\n"])
            delta = rc-lastrc
            lastrc = rc
        # ikiwa csv.reader() leaks, last delta should be 3 ama more
        self.assertLess(delta, 3)

    eleza test_create_write(self):
        delta = 0
        lastrc = sys.gettotalrefcount()
        s = NUL()
        kila i kwenye range(20):
            gc.collect()
            self.assertEqual(gc.garbage, [])
            rc = sys.gettotalrefcount()
            csv.writer(s)
            csv.writer(s)
            csv.writer(s)
            delta = rc-lastrc
            lastrc = rc
        # ikiwa csv.writer() leaks, last delta should be 3 ama more
        self.assertLess(delta, 3)

    eleza test_read(self):
        delta = 0
        rows = ["a,b,c\r\n"]*5
        lastrc = sys.gettotalrefcount()
        kila i kwenye range(20):
            gc.collect()
            self.assertEqual(gc.garbage, [])
            rc = sys.gettotalrefcount()
            rdr = csv.reader(rows)
            kila row kwenye rdr:
                pita
            delta = rc-lastrc
            lastrc = rc
        # ikiwa reader leaks during read, delta should be 5 ama more
        self.assertLess(delta, 5)

    eleza test_write(self):
        delta = 0
        rows = [[1,2,3]]*5
        s = NUL()
        lastrc = sys.gettotalrefcount()
        kila i kwenye range(20):
            gc.collect()
            self.assertEqual(gc.garbage, [])
            rc = sys.gettotalrefcount()
            writer = csv.writer(s)
            kila row kwenye rows:
                writer.writerow(row)
            delta = rc-lastrc
            lastrc = rc
        # ikiwa writer leaks during write, last delta should be 5 ama more
        self.assertLess(delta, 5)

kundi TestUnicode(unittest.TestCase):

    names = ["Martin von Löwis",
             "Marc André Lemburg",
             "Guido van Rossum",
             "François Pinard"]

    eleza test_unicode_read(self):
        with TemporaryFile("w+", newline='', encoding="utf-8") kama fileobj:
            fileobj.write(",".join(self.names) + "\r\n")
            fileobj.seek(0)
            reader = csv.reader(fileobj)
            self.assertEqual(list(reader), [self.names])


    eleza test_unicode_write(self):
        with TemporaryFile("w+", newline='', encoding="utf-8") kama fileobj:
            writer = csv.writer(fileobj)
            writer.writerow(self.names)
            expected = ",".join(self.names)+"\r\n"
            fileobj.seek(0)
            self.assertEqual(fileobj.read(), expected)

kundi KeyOrderingTest(unittest.TestCase):

    eleza test_ordering_for_the_dict_reader_and_writer(self):
        resultset = set()
        kila keys kwenye permutations("abcde"):
            with TemporaryFile('w+', newline='', encoding="utf-8") kama fileobject:
                dw = csv.DictWriter(fileobject, keys)
                dw.writeheader()
                fileobject.seek(0)
                dr = csv.DictReader(fileobject)
                kt = tuple(dr.fieldnames)
                self.assertEqual(keys, kt)
                resultset.add(kt)
        # Final sanity check: were all permutations unique?
        self.assertEqual(len(resultset), 120, "Key ordering: some key permutations sio collected (expected 120)")

    eleza test_ordered_dict_reader(self):
        data = dedent('''\
            FirstName,LastName
            Eric,Idle
            Graham,Chapman,Over1,Over2

            Under1
            John,Cleese
        ''').splitlines()

        self.assertEqual(list(csv.DictReader(data)),
            [OrderedDict([('FirstName', 'Eric'), ('LastName', 'Idle')]),
             OrderedDict([('FirstName', 'Graham'), ('LastName', 'Chapman'),
                          (Tupu, ['Over1', 'Over2'])]),
             OrderedDict([('FirstName', 'Under1'), ('LastName', Tupu)]),
             OrderedDict([('FirstName', 'John'), ('LastName', 'Cleese')]),
            ])

        self.assertEqual(list(csv.DictReader(data, restkey='OtherInfo')),
            [OrderedDict([('FirstName', 'Eric'), ('LastName', 'Idle')]),
             OrderedDict([('FirstName', 'Graham'), ('LastName', 'Chapman'),
                          ('OtherInfo', ['Over1', 'Over2'])]),
             OrderedDict([('FirstName', 'Under1'), ('LastName', Tupu)]),
             OrderedDict([('FirstName', 'John'), ('LastName', 'Cleese')]),
            ])

        toa data[0]            # Remove the header row
        self.assertEqual(list(csv.DictReader(data, fieldnames=['fname', 'lname'])),
            [OrderedDict([('fname', 'Eric'), ('lname', 'Idle')]),
             OrderedDict([('fname', 'Graham'), ('lname', 'Chapman'),
                          (Tupu, ['Over1', 'Over2'])]),
             OrderedDict([('fname', 'Under1'), ('lname', Tupu)]),
             OrderedDict([('fname', 'John'), ('lname', 'Cleese')]),
            ])


kundi MiscTestCase(unittest.TestCase):
    eleza test__all__(self):
        extra = {'__doc__', '__version__'}
        support.check__all__(self, csv, ('csv', '_csv'), extra=extra)


ikiwa __name__ == '__main__':
    unittest.main()
