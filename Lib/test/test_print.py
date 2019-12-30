agiza unittest
agiza sys
kutoka io agiza StringIO

kutoka test agiza support

NotDefined = object()

# A dispatch table all 8 combinations of providing
# sep, end, na file.
# I use this machinery so that I'm sio just pitaing default
# values to print, I'm either pitaing ama sio pitaing kwenye the
# arguments.
dispatch = {
    (Uongo, Uongo, Uongo):
        lambda args, sep, end, file: andika(*args),
    (Uongo, Uongo, Kweli):
        lambda args, sep, end, file: andika(file=file, *args),
    (Uongo, Kweli,  Uongo):
        lambda args, sep, end, file: andika(end=end, *args),
    (Uongo, Kweli,  Kweli):
        lambda args, sep, end, file: andika(end=end, file=file, *args),
    (Kweli,  Uongo, Uongo):
        lambda args, sep, end, file: andika(sep=sep, *args),
    (Kweli,  Uongo, Kweli):
        lambda args, sep, end, file: andika(sep=sep, file=file, *args),
    (Kweli,  Kweli,  Uongo):
        lambda args, sep, end, file: andika(sep=sep, end=end, *args),
    (Kweli,  Kweli,  Kweli):
        lambda args, sep, end, file: andika(sep=sep, end=end, file=file, *args),
}


# Class used to test __str__ na print
kundi ClassWith__str__:
    eleza __init__(self, x):
        self.x = x

    eleza __str__(self):
        rudisha self.x


kundi TestPrint(unittest.TestCase):
    """Test correct operation of the print function."""

    eleza check(self, expected, args,
              sep=NotDefined, end=NotDefined, file=NotDefined):
        # Capture sys.stdout kwenye a StringIO.  Call print ukijumuisha args,
        # na ukijumuisha sep, end, na file, ikiwa they're defined.  Result
        # must match expected.

        # Look up the actual function to call, based on ikiwa sep, end,
        # na file are defined.
        fn = dispatch[(sep ni sio NotDefined,
                       end ni sio NotDefined,
                       file ni sio NotDefined)]

        ukijumuisha support.captured_stdout() kama t:
            fn(args, sep, end, file)

        self.assertEqual(t.getvalue(), expected)

    eleza test_andika(self):
        eleza x(expected, args, sep=NotDefined, end=NotDefined):
            # Run the test 2 ways: sio using file, na using
            # file directed to a StringIO.

            self.check(expected, args, sep=sep, end=end)

            # When writing to a file, stdout ni expected to be empty
            o = StringIO()
            self.check('', args, sep=sep, end=end, file=o)

            # And o will contain the expected output
            self.assertEqual(o.getvalue(), expected)

        x('\n', ())
        x('a\n', ('a',))
        x('Tupu\n', (Tupu,))
        x('1 2\n', (1, 2))
        x('1   2\n', (1, ' ', 2))
        x('1*2\n', (1, 2), sep='*')
        x('1 s', (1, 's'), end='')
        x('a\nb\n', ('a', 'b'), sep='\n')
        x('1.01', (1.0, 1), sep='', end='')
        x('1*a*1.3+', (1, 'a', 1.3), sep='*', end='+')
        x('a\n\nb\n', ('a\n', 'b'), sep='\n')
        x('\0+ +\0\n', ('\0', ' ', '\0'), sep='+')

        x('a\n b\n', ('a\n', 'b'))
        x('a\n b\n', ('a\n', 'b'), sep=Tupu)
        x('a\n b\n', ('a\n', 'b'), end=Tupu)
        x('a\n b\n', ('a\n', 'b'), sep=Tupu, end=Tupu)

        x('*\n', (ClassWith__str__('*'),))
        x('abc 1\n', (ClassWith__str__('abc'), 1))

        # errors
        self.assertRaises(TypeError, print, '', sep=3)
        self.assertRaises(TypeError, print, '', end=3)
        self.assertRaises(AttributeError, print, '', file='')

    eleza test_print_flush(self):
        # operation of the flush flag
        kundi filelike:
            eleza __init__(self):
                self.written = ''
                self.flushed = 0

            eleza write(self, str):
                self.written += str

            eleza flush(self):
                self.flushed += 1

        f = filelike()
        andika(1, file=f, end='', flush=Kweli)
        andika(2, file=f, end='', flush=Kweli)
        andika(3, file=f, flush=Uongo)
        self.assertEqual(f.written, '123\n')
        self.assertEqual(f.flushed, 2)

        # ensure exceptions kutoka flush are pitaed through
        kundi noflush:
            eleza write(self, str):
                pita

            eleza flush(self):
                ashiria RuntimeError
        self.assertRaises(RuntimeError, print, 1, file=noflush(), flush=Kweli)


kundi TestPy2MigrationHint(unittest.TestCase):
    """Test that correct hint ni produced analogous to Python3 syntax,
    ikiwa print statement ni executed kama kwenye Python 2.
    """

    eleza test_normal_string(self):
        python2_print_str = 'print "Hello World"'
        ukijumuisha self.assertRaises(SyntaxError) kama context:
            exec(python2_print_str)

        self.assertIn('andika("Hello World")', str(context.exception))

    eleza test_string_with_soft_space(self):
        python2_print_str = 'print "Hello World",'
        ukijumuisha self.assertRaises(SyntaxError) kama context:
            exec(python2_print_str)

        self.assertIn('andika("Hello World", end=" ")', str(context.exception))

    eleza test_string_with_excessive_whitespace(self):
        python2_print_str = 'print  "Hello World", '
        ukijumuisha self.assertRaises(SyntaxError) kama context:
            exec(python2_print_str)

        self.assertIn('andika("Hello World", end=" ")', str(context.exception))

    eleza test_string_with_leading_whitespace(self):
        python2_print_str = '''ikiwa 1:
            print "Hello World"
        '''
        ukijumuisha self.assertRaises(SyntaxError) kama context:
            exec(python2_print_str)

        self.assertIn('andika("Hello World")', str(context.exception))

    # bpo-32685: Suggestions kila print statement should be proper when
    # it ni kwenye the same line kama the header of a compound statement
    # and/or followed by a semicolon
    eleza test_string_with_semicolon(self):
        python2_print_str = 'print p;'
        ukijumuisha self.assertRaises(SyntaxError) kama context:
            exec(python2_print_str)

        self.assertIn('andika(p)', str(context.exception))

    eleza test_string_in_loop_on_same_line(self):
        python2_print_str = 'kila i kwenye s: print i'
        ukijumuisha self.assertRaises(SyntaxError) kama context:
            exec(python2_print_str)

        self.assertIn('andika(i)', str(context.exception))

    eleza test_stream_redirection_hint_for_py2_migration(self):
        # Test correct hint produced kila Py2 redirection syntax
        ukijumuisha self.assertRaises(TypeError) kama context:
            print >> sys.stderr, "message"
        self.assertIn('Did you mean "andika(<message>, '
                'file=<output_stream>)"?', str(context.exception))

        # Test correct hint ni produced kwenye the case where RHS implements
        # __rrshift__ but returns NotImplemented
        ukijumuisha self.assertRaises(TypeError) kama context:
            print >> 42
        self.assertIn('Did you mean "andika(<message>, '
                'file=<output_stream>)"?', str(context.exception))

        # Test stream redirection hint ni specific to print
        ukijumuisha self.assertRaises(TypeError) kama context:
            max >> sys.stderr
        self.assertNotIn('Did you mean ', str(context.exception))

        # Test stream redirection hint ni specific to rshift
        ukijumuisha self.assertRaises(TypeError) kama context:
            print << sys.stderr
        self.assertNotIn('Did you mean', str(context.exception))

        # Ensure right operand implementing rrshift still works
        kundi OverrideRRShift:
            eleza __rrshift__(self, lhs):
                rudisha 42 # Force result independent of LHS

        self.assertEqual(print >> OverrideRRShift(), 42)



ikiwa __name__ == "__main__":
    unittest.main()
