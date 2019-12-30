"""
Test script kila doctest.
"""

kutoka test agiza support
agiza doctest
agiza functools
agiza os
agiza sys
agiza importlib
agiza unittest
agiza tempfile

# NOTE: There are some additional tests relating to interaction with
#       zipagiza kwenye the test_zipimport_support test module.

######################################################################
## Sample Objects (used by test cases)
######################################################################

eleza sample_func(v):
    """
    Blah blah

    >>> andika(sample_func(22))
    44

    Yee ha!
    """
    rudisha v+v

kundi SampleClass:
    """
    >>> andika(1)
    1

    >>> # comments get ignored.  so are empty PS1 na PS2 prompts:
    >>>
    ...

    Multiline example:
    >>> sc = SampleClass(3)
    >>> kila i kwenye range(10):
    ...     sc = sc.double()
    ...     andika(' ', sc.get(), sep='', end='')
     6 12 24 48 96 192 384 768 1536 3072
    """
    eleza __init__(self, val):
        """
        >>> andika(SampleClass(12).get())
        12
        """
        self.val = val

    eleza double(self):
        """
        >>> andika(SampleClass(12).double().get())
        24
        """
        rudisha SampleClass(self.val + self.val)

    eleza get(self):
        """
        >>> andika(SampleClass(-5).get())
        -5
        """
        rudisha self.val

    eleza a_staticmethod(v):
        """
        >>> andika(SampleClass.a_staticmethod(10))
        11
        """
        rudisha v+1
    a_staticmethod = staticmethod(a_staticmethod)

    eleza a_classmethod(cls, v):
        """
        >>> andika(SampleClass.a_classmethod(10))
        12
        >>> andika(SampleClass(0).a_classmethod(10))
        12
        """
        rudisha v+2
    a_classmethod = classmethod(a_classmethod)

    a_property = property(get, doc="""
        >>> andika(SampleClass(22).a_property)
        22
        """)

    kundi NestedClass:
        """
        >>> x = SampleClass.NestedClass(5)
        >>> y = x.square()
        >>> andika(y.get())
        25
        """
        eleza __init__(self, val=0):
            """
            >>> andika(SampleClass.NestedClass().get())
            0
            """
            self.val = val
        eleza square(self):
            rudisha SampleClass.NestedClass(self.val*self.val)
        eleza get(self):
            rudisha self.val

kundi SampleNewStyleClass(object):
    r"""
    >>> andika('1\n2\n3')
    1
    2
    3
    """
    eleza __init__(self, val):
        """
        >>> andika(SampleNewStyleClass(12).get())
        12
        """
        self.val = val

    eleza double(self):
        """
        >>> andika(SampleNewStyleClass(12).double().get())
        24
        """
        rudisha SampleNewStyleClass(self.val + self.val)

    eleza get(self):
        """
        >>> andika(SampleNewStyleClass(-5).get())
        -5
        """
        rudisha self.val

######################################################################
## Fake stdin (kila testing interactive debugging)
######################################################################

kundi _FakeInput:
    """
    A fake input stream kila pdb's interactive debugger.  Whenever a
    line ni read, print it (to simulate the user typing it), na then
    rudisha it.  The set of lines to rudisha ni specified kwenye the
    constructor; they should sio have trailing newlines.
    """
    eleza __init__(self, lines):
        self.lines = lines

    eleza readline(self):
        line = self.lines.pop(0)
        andika(line)
        rudisha line+'\n'

######################################################################
## Test Cases
######################################################################

eleza test_Example(): r"""
Unit tests kila the `Example` class.

Example ni a simple container kundi that holds:
  - `source`: A source string.
  - `want`: An expected output string.
  - `exc_msg`: An expected exception message string (or Tupu ikiwa no
    exception ni expected).
  - `lineno`: A line number (within the docstring).
  - `indent`: The example's indentation kwenye the input string.
  - `options`: An option dictionary, mapping option flags to Kweli ama
    Uongo.

These attributes are set by the constructor.  `source` na `want` are
required; the other attributes all have default values:

    >>> example = doctest.Example('andika(1)', '1\n')
    >>> (example.source, example.want, example.exc_msg,
    ...  example.lineno, example.indent, example.options)
    ('andika(1)\n', '1\n', Tupu, 0, 0, {})

The first three attributes (`source`, `want`, na `exc_msg`) may be
specified positionally; the remaining arguments should be specified as
keyword arguments:

    >>> exc_msg = 'IndexError: pop kutoka an empty list'
    >>> example = doctest.Example('[].pop()', '', exc_msg,
    ...                           lineno=5, indent=4,
    ...                           options={doctest.ELLIPSIS: Kweli})
    >>> (example.source, example.want, example.exc_msg,
    ...  example.lineno, example.indent, example.options)
    ('[].pop()\n', '', 'IndexError: pop kutoka an empty list\n', 5, 4, {8: Kweli})

The constructor normalizes the `source` string to end kwenye a newline:

    Source spans a single line: no terminating newline.
    >>> e = doctest.Example('andika(1)', '1\n')
    >>> e.source, e.want
    ('andika(1)\n', '1\n')

    >>> e = doctest.Example('andika(1)\n', '1\n')
    >>> e.source, e.want
    ('andika(1)\n', '1\n')

    Source spans multiple lines: require terminating newline.
    >>> e = doctest.Example('andika(1);\nandika(2)\n', '1\n2\n')
    >>> e.source, e.want
    ('andika(1);\nandika(2)\n', '1\n2\n')

    >>> e = doctest.Example('andika(1);\nandika(2)', '1\n2\n')
    >>> e.source, e.want
    ('andika(1);\nandika(2)\n', '1\n2\n')

    Empty source string (which should never appear kwenye real examples)
    >>> e = doctest.Example('', '')
    >>> e.source, e.want
    ('\n', '')

The constructor normalizes the `want` string to end kwenye a newline,
unless it's the empty string:

    >>> e = doctest.Example('andika(1)', '1\n')
    >>> e.source, e.want
    ('andika(1)\n', '1\n')

    >>> e = doctest.Example('andika(1)', '1')
    >>> e.source, e.want
    ('andika(1)\n', '1\n')

    >>> e = doctest.Example('print', '')
    >>> e.source, e.want
    ('print\n', '')

The constructor normalizes the `exc_msg` string to end kwenye a newline,
unless it's `Tupu`:

    Message spans one line
    >>> exc_msg = 'IndexError: pop kutoka an empty list'
    >>> e = doctest.Example('[].pop()', '', exc_msg)
    >>> e.exc_msg
    'IndexError: pop kutoka an empty list\n'

    >>> exc_msg = 'IndexError: pop kutoka an empty list\n'
    >>> e = doctest.Example('[].pop()', '', exc_msg)
    >>> e.exc_msg
    'IndexError: pop kutoka an empty list\n'

    Message spans multiple lines
    >>> exc_msg = 'ValueError: 1\n  2'
    >>> e = doctest.Example('ashiria ValueError("1\n  2")', '', exc_msg)
    >>> e.exc_msg
    'ValueError: 1\n  2\n'

    >>> exc_msg = 'ValueError: 1\n  2\n'
    >>> e = doctest.Example('ashiria ValueError("1\n  2")', '', exc_msg)
    >>> e.exc_msg
    'ValueError: 1\n  2\n'

    Empty (but non-Tupu) exception message (which should never appear
    kwenye real examples)
    >>> exc_msg = ''
    >>> e = doctest.Example('ashiria X()', '', exc_msg)
    >>> e.exc_msg
    '\n'

Compare `Example`:
    >>> example = doctest.Example('print 1', '1\n')
    >>> same_example = doctest.Example('print 1', '1\n')
    >>> other_example = doctest.Example('print 42', '42\n')
    >>> example == same_example
    Kweli
    >>> example != same_example
    Uongo
    >>> hash(example) == hash(same_example)
    Kweli
    >>> example == other_example
    Uongo
    >>> example != other_example
    Kweli
"""

eleza test_DocTest(): r"""
Unit tests kila the `DocTest` class.

DocTest ni a collection of examples, extracted kutoka a docstring, along
ukijumuisha information about where the docstring comes kutoka (a name,
filename, na line number).  The docstring ni parsed by the `DocTest`
constructor:

    >>> docstring = '''
    ...     >>> andika(12)
    ...     12
    ...
    ... Non-example text.
    ...
    ...     >>> andika('another\\example')
    ...     another
    ...     example
    ... '''
    >>> globs = {} # globals to run the test in.
    >>> parser = doctest.DocTestParser()
    >>> test = parser.get_doctest(docstring, globs, 'some_test',
    ...                           'some_file', 20)
    >>> andika(test)
    <DocTest some_test kutoka some_file:20 (2 examples)>
    >>> len(test.examples)
    2
    >>> e1, e2 = test.examples
    >>> (e1.source, e1.want, e1.lineno)
    ('andika(12)\n', '12\n', 1)
    >>> (e2.source, e2.want, e2.lineno)
    ("andika('another\\example')\n", 'another\nexample\n', 6)

Source information (name, filename, na line number) ni available as
attributes on the doctest object:

    >>> (test.name, test.filename, test.lineno)
    ('some_test', 'some_file', 20)

The line number of an example within its containing file ni found by
adding the line number of the example na the line number of its
containing test:

    >>> test.lineno + e1.lineno
    21
    >>> test.lineno + e2.lineno
    26

If the docstring contains inconsistent leading whitespace kwenye the
expected output of an example, then `DocTest` will ashiria a ValueError:

    >>> docstring = r'''
    ...       >>> andika('bad\nindentation')
    ...       bad
    ...     indentation
    ...     '''
    >>> parser.get_doctest(docstring, globs, 'some_test', 'filename', 0)
    Traceback (most recent call last):
    ValueError: line 4 of the docstring kila some_test has inconsistent leading whitespace: 'indentation'

If the docstring contains inconsistent leading whitespace on
continuation lines, then `DocTest` will ashiria a ValueError:

    >>> docstring = r'''
    ...       >>> andika(('bad indentation',
    ...     ...          2))
    ...       ('bad', 'indentation')
    ...     '''
    >>> parser.get_doctest(docstring, globs, 'some_test', 'filename', 0)
    Traceback (most recent call last):
    ValueError: line 2 of the docstring kila some_test has inconsistent leading whitespace: '...          2))'

If there's no blank space after a PS1 prompt ('>>>'), then `DocTest`
will ashiria a ValueError:

    >>> docstring = '>>>andika(1)\n1'
    >>> parser.get_doctest(docstring, globs, 'some_test', 'filename', 0)
    Traceback (most recent call last):
    ValueError: line 1 of the docstring kila some_test lacks blank after >>>: '>>>andika(1)'

If there's no blank space after a PS2 prompt ('...'), then `DocTest`
will ashiria a ValueError:

    >>> docstring = '>>> ikiwa 1:\n...andika(1)\n1'
    >>> parser.get_doctest(docstring, globs, 'some_test', 'filename', 0)
    Traceback (most recent call last):
    ValueError: line 2 of the docstring kila some_test lacks blank after ...: '...andika(1)'

Compare `DocTest`:

    >>> docstring = '''
    ...     >>> print 12
    ...     12
    ... '''
    >>> test = parser.get_doctest(docstring, globs, 'some_test',
    ...                           'some_test', 20)
    >>> same_test = parser.get_doctest(docstring, globs, 'some_test',
    ...                                'some_test', 20)
    >>> test == same_test
    Kweli
    >>> test != same_test
    Uongo
    >>> hash(test) == hash(same_test)
    Kweli
    >>> docstring = '''
    ...     >>> print 42
    ...     42
    ... '''
    >>> other_test = parser.get_doctest(docstring, globs, 'other_test',
    ...                                 'other_file', 10)
    >>> test == other_test
    Uongo
    >>> test != other_test
    Kweli

Compare `DocTestCase`:

    >>> DocTestCase = doctest.DocTestCase
    >>> test_case = DocTestCase(test)
    >>> same_test_case = DocTestCase(same_test)
    >>> other_test_case = DocTestCase(other_test)
    >>> test_case == same_test_case
    Kweli
    >>> test_case != same_test_case
    Uongo
    >>> hash(test_case) == hash(same_test_case)
    Kweli
    >>> test == other_test_case
    Uongo
    >>> test != other_test_case
    Kweli

"""

kundi test_DocTestFinder:
    eleza basics(): r"""
Unit tests kila the `DocTestFinder` class.

DocTestFinder ni used to extract DocTests kutoka an object's docstring
and the docstrings of its contained objects.  It can be used with
modules, functions, classes, methods, staticmethods, classmethods, na
properties.

Finding Tests kwenye Functions
~~~~~~~~~~~~~~~~~~~~~~~~~~
For a function whose docstring contains examples, DocTestFinder.find()
will rudisha a single test (kila that function's docstring):

    >>> finder = doctest.DocTestFinder()

We'll simulate a __file__ attr that ends kwenye pyc:

    >>> agiza test.test_doctest
    >>> old = test.test_doctest.__file__
    >>> test.test_doctest.__file__ = 'test_doctest.pyc'

    >>> tests = finder.find(sample_func)

    >>> andika(tests)  # doctest: +ELLIPSIS
    [<DocTest sample_func kutoka ...:21 (1 example)>]

The exact name depends on how test_doctest was invoked, so allow for
leading path components.

    >>> tests[0].filename # doctest: +ELLIPSIS
    '...test_doctest.py'

    >>> test.test_doctest.__file__ = old


    >>> e = tests[0].examples[0]
    >>> (e.source, e.want, e.lineno)
    ('andika(sample_func(22))\n', '44\n', 3)

By default, tests are created kila objects ukijumuisha no docstring:

    >>> eleza no_docstring(v):
    ...     pita
    >>> finder.find(no_docstring)
    []

However, the optional argument `exclude_empty` to the DocTestFinder
constructor can be used to exclude tests kila objects ukijumuisha empty
docstrings:

    >>> eleza no_docstring(v):
    ...     pita
    >>> excl_empty_finder = doctest.DocTestFinder(exclude_empty=Kweli)
    >>> excl_empty_finder.find(no_docstring)
    []

If the function has a docstring ukijumuisha no examples, then a test ukijumuisha no
examples ni rudishaed.  (This lets `DocTestRunner` collect statistics
about which functions have no tests -- but ni that useful?  And should
an empty test also be created when there's no docstring?)

    >>> eleza no_examples(v):
    ...     ''' no doctest examples '''
    >>> finder.find(no_examples) # doctest: +ELLIPSIS
    [<DocTest no_examples kutoka ...:1 (no examples)>]

Finding Tests kwenye Classes
~~~~~~~~~~~~~~~~~~~~~~~~
For a class, DocTestFinder will create a test kila the class's
docstring, na will recursively explore its contents, including
methods, classmethods, staticmethods, properties, na nested classes.

    >>> finder = doctest.DocTestFinder()
    >>> tests = finder.find(SampleClass)
    >>> kila t kwenye tests:
    ...     andika('%2s  %s' % (len(t.examples), t.name))
     3  SampleClass
     3  SampleClass.NestedClass
     1  SampleClass.NestedClass.__init__
     1  SampleClass.__init__
     2  SampleClass.a_classmethod
     1  SampleClass.a_property
     1  SampleClass.a_staticmethod
     1  SampleClass.double
     1  SampleClass.get

New-style classes are also supported:

    >>> tests = finder.find(SampleNewStyleClass)
    >>> kila t kwenye tests:
    ...     andika('%2s  %s' % (len(t.examples), t.name))
     1  SampleNewStyleClass
     1  SampleNewStyleClass.__init__
     1  SampleNewStyleClass.double
     1  SampleNewStyleClass.get

Finding Tests kwenye Modules
~~~~~~~~~~~~~~~~~~~~~~~~
For a module, DocTestFinder will create a test kila the class's
docstring, na will recursively explore its contents, including
functions, classes, na the `__test__` dictionary, ikiwa it exists:

    >>> # A module
    >>> agiza types
    >>> m = types.ModuleType('some_module')
    >>> eleza triple(val):
    ...     '''
    ...     >>> andika(triple(11))
    ...     33
    ...     '''
    ...     rudisha val*3
    >>> m.__dict__.update({
    ...     'sample_func': sample_func,
    ...     'SampleClass': SampleClass,
    ...     '__doc__': '''
    ...         Module docstring.
    ...             >>> andika('module')
    ...             module
    ...         ''',
    ...     '__test__': {
    ...         'd': '>>> andika(6)\n6\n>>> andika(7)\n7\n',
    ...         'c': triple}})

    >>> finder = doctest.DocTestFinder()
    >>> # Use module=test.test_doctest, to prevent doctest kutoka
    >>> # ignoring the objects since they weren't defined kwenye m.
    >>> agiza test.test_doctest
    >>> tests = finder.find(m, module=test.test_doctest)
    >>> kila t kwenye tests:
    ...     andika('%2s  %s' % (len(t.examples), t.name))
     1  some_module
     3  some_module.SampleClass
     3  some_module.SampleClass.NestedClass
     1  some_module.SampleClass.NestedClass.__init__
     1  some_module.SampleClass.__init__
     2  some_module.SampleClass.a_classmethod
     1  some_module.SampleClass.a_property
     1  some_module.SampleClass.a_staticmethod
     1  some_module.SampleClass.double
     1  some_module.SampleClass.get
     1  some_module.__test__.c
     2  some_module.__test__.d
     1  some_module.sample_func

Duplicate Removal
~~~~~~~~~~~~~~~~~
If a single object ni listed twice (under different names), then tests
will only be generated kila it once:

    >>> kutoka test agiza doctest_aliases
    >>> assert doctest_aliases.TwoNames.f
    >>> assert doctest_aliases.TwoNames.g
    >>> tests = excl_empty_finder.find(doctest_aliases)
    >>> andika(len(tests))
    2
    >>> andika(tests[0].name)
    test.doctest_aliases.TwoNames

    TwoNames.f na TwoNames.g are bound to the same object.
    We can't guess which will be found kwenye doctest's traversal of
    TwoNames.__dict__ first, so we have to allow kila either.

    >>> tests[1].name.split('.')[-1] kwenye ['f', 'g']
    Kweli

Empty Tests
~~~~~~~~~~~
By default, an object ukijumuisha no doctests doesn't create any tests:

    >>> tests = doctest.DocTestFinder().find(SampleClass)
    >>> kila t kwenye tests:
    ...     andika('%2s  %s' % (len(t.examples), t.name))
     3  SampleClass
     3  SampleClass.NestedClass
     1  SampleClass.NestedClass.__init__
     1  SampleClass.__init__
     2  SampleClass.a_classmethod
     1  SampleClass.a_property
     1  SampleClass.a_staticmethod
     1  SampleClass.double
     1  SampleClass.get

By default, that excluded objects ukijumuisha no doctests.  exclude_empty=Uongo
tells it to include (empty) tests kila objects ukijumuisha no doctests.  This feature
is really to support backward compatibility kwenye what doctest.master.summarize()
displays.

    >>> tests = doctest.DocTestFinder(exclude_empty=Uongo).find(SampleClass)
    >>> kila t kwenye tests:
    ...     andika('%2s  %s' % (len(t.examples), t.name))
     3  SampleClass
     3  SampleClass.NestedClass
     1  SampleClass.NestedClass.__init__
     0  SampleClass.NestedClass.get
     0  SampleClass.NestedClass.square
     1  SampleClass.__init__
     2  SampleClass.a_classmethod
     1  SampleClass.a_property
     1  SampleClass.a_staticmethod
     1  SampleClass.double
     1  SampleClass.get

Turning off Recursion
~~~~~~~~~~~~~~~~~~~~~
DocTestFinder can be told sio to look kila tests kwenye contained objects
using the `recurse` flag:

    >>> tests = doctest.DocTestFinder(recurse=Uongo).find(SampleClass)
    >>> kila t kwenye tests:
    ...     andika('%2s  %s' % (len(t.examples), t.name))
     3  SampleClass

Line numbers
~~~~~~~~~~~~
DocTestFinder finds the line number of each example:

    >>> eleza f(x):
    ...     '''
    ...     >>> x = 12
    ...
    ...     some text
    ...
    ...     >>> # examples are sio created kila comments & bare prompts.
    ...     >>>
    ...     ...
    ...
    ...     >>> kila x kwenye range(10):
    ...     ...     andika(x, end=' ')
    ...     0 1 2 3 4 5 6 7 8 9
    ...     >>> x//2
    ...     6
    ...     '''
    >>> test = doctest.DocTestFinder().find(f)[0]
    >>> [e.lineno kila e kwenye test.examples]
    [1, 9, 12]
"""

    ikiwa int.__doc__: # simple check kila --without-doc-strings, skip ikiwa lacking
        eleza non_Python_modules(): r"""

Finding Doctests kwenye Modules Not Written kwenye Python
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
DocTestFinder can also find doctests kwenye most modules sio written kwenye Python.
We'll use builtins kama an example, since it almost certainly isn't written in
plain ol' Python na ni guaranteed to be available.

    >>> agiza builtins
    >>> tests = doctest.DocTestFinder().find(builtins)
    >>> 800 < len(tests) < 820 # approximate number of objects ukijumuisha docstrings
    Kweli
    >>> real_tests = [t kila t kwenye tests ikiwa len(t.examples) > 0]
    >>> len(real_tests) # objects that actually have doctests
    12
    >>> kila t kwenye real_tests:
    ...     andika('{}  {}'.format(len(t.examples), t.name))
    ...
    1  builtins.bin
    5  builtins.bytearray.hex
    5  builtins.bytes.hex
    3  builtins.float.as_integer_ratio
    2  builtins.float.kutokahex
    2  builtins.float.hex
    1  builtins.hex
    1  builtins.int
    3  builtins.int.as_integer_ratio
    2  builtins.int.bit_length
    5  builtins.memoryview.hex
    1  builtins.oct

Note here that 'bin', 'oct', na 'hex' are functions; 'float.as_integer_ratio',
'float.hex', na 'int.bit_length' are methods; 'float.kutokahex' ni a classmethod,
and 'int' ni a type.
"""


kundi TestDocTestFinder(unittest.TestCase):

    eleza test_empty_namespace_package(self):
        pkg_name = 'doctest_empty_pkg'
        ukijumuisha tempfile.TemporaryDirectory() kama parent_dir:
            pkg_dir = os.path.join(parent_dir, pkg_name)
            os.mkdir(pkg_dir)
            sys.path.append(parent_dir)
            jaribu:
                mod = importlib.import_module(pkg_name)
            mwishowe:
                support.forget(pkg_name)
                sys.path.pop()
            assert doctest.DocTestFinder().find(mod) == []


eleza test_DocTestParser(): r"""
Unit tests kila the `DocTestParser` class.

DocTestParser ni used to parse docstrings containing doctest examples.

The `parse` method divides a docstring into examples na intervening
text:

    >>> s = '''
    ...     >>> x, y = 2, 3  # no output expected
    ...     >>> ikiwa 1:
    ...     ...     andika(x)
    ...     ...     andika(y)
    ...     2
    ...     3
    ...
    ...     Some text.
    ...     >>> x+y
    ...     5
    ...     '''
    >>> parser = doctest.DocTestParser()
    >>> kila piece kwenye parser.parse(s):
    ...     ikiwa isinstance(piece, doctest.Example):
    ...         andika('Example:', (piece.source, piece.want, piece.lineno))
    ...     isipokua:
    ...         andika('   Text:', repr(piece))
       Text: '\n'
    Example: ('x, y = 2, 3  # no output expected\n', '', 1)
       Text: ''
    Example: ('ikiwa 1:\n    andika(x)\n    andika(y)\n', '2\n3\n', 2)
       Text: '\nSome text.\n'
    Example: ('x+y\n', '5\n', 9)
       Text: ''

The `get_examples` method rudishas just the examples:

    >>> kila piece kwenye parser.get_examples(s):
    ...     andika((piece.source, piece.want, piece.lineno))
    ('x, y = 2, 3  # no output expected\n', '', 1)
    ('ikiwa 1:\n    andika(x)\n    andika(y)\n', '2\n3\n', 2)
    ('x+y\n', '5\n', 9)

The `get_doctest` method creates a Test kutoka the examples, along ukijumuisha the
given arguments:

    >>> test = parser.get_doctest(s, {}, 'name', 'filename', lineno=5)
    >>> (test.name, test.filename, test.lineno)
    ('name', 'filename', 5)
    >>> kila piece kwenye test.examples:
    ...     andika((piece.source, piece.want, piece.lineno))
    ('x, y = 2, 3  # no output expected\n', '', 1)
    ('ikiwa 1:\n    andika(x)\n    andika(y)\n', '2\n3\n', 2)
    ('x+y\n', '5\n', 9)
"""

kundi test_DocTestRunner:
    eleza basics(): r"""
Unit tests kila the `DocTestRunner` class.

DocTestRunner ni used to run DocTest test cases, na to accumulate
statistics.  Here's a simple DocTest case we can use:

    >>> eleza f(x):
    ...     '''
    ...     >>> x = 12
    ...     >>> andika(x)
    ...     12
    ...     >>> x//2
    ...     6
    ...     '''
    >>> test = doctest.DocTestFinder().find(f)[0]

The main DocTestRunner interface ni the `run` method, which runs a
given DocTest case kwenye a given namespace (globs).  It rudishas a tuple
`(f,t)`, where `f` ni the number of failed tests na `t` ni the number
of tried tests.

    >>> doctest.DocTestRunner(verbose=Uongo).run(test)
    TestResults(failed=0, attempted=3)

If any example produces incorrect output, then the test runner reports
the failure na proceeds to the next example:

    >>> eleza f(x):
    ...     '''
    ...     >>> x = 12
    ...     >>> andika(x)
    ...     14
    ...     >>> x//2
    ...     6
    ...     '''
    >>> test = doctest.DocTestFinder().find(f)[0]
    >>> doctest.DocTestRunner(verbose=Kweli).run(test)
    ... # doctest: +ELLIPSIS
    Trying:
        x = 12
    Expecting nothing
    ok
    Trying:
        andika(x)
    Expecting:
        14
    **********************************************************************
    File ..., line 4, kwenye f
    Failed example:
        andika(x)
    Expected:
        14
    Got:
        12
    Trying:
        x//2
    Expecting:
        6
    ok
    TestResults(failed=1, attempted=3)
"""
    eleza verbose_flag(): r"""
The `verbose` flag makes the test runner generate more detailed
output:

    >>> eleza f(x):
    ...     '''
    ...     >>> x = 12
    ...     >>> andika(x)
    ...     12
    ...     >>> x//2
    ...     6
    ...     '''
    >>> test = doctest.DocTestFinder().find(f)[0]

    >>> doctest.DocTestRunner(verbose=Kweli).run(test)
    Trying:
        x = 12
    Expecting nothing
    ok
    Trying:
        andika(x)
    Expecting:
        12
    ok
    Trying:
        x//2
    Expecting:
        6
    ok
    TestResults(failed=0, attempted=3)

If the `verbose` flag ni unspecified, then the output will be verbose
iff `-v` appears kwenye sys.argv:

    >>> # Save the real sys.argv list.
    >>> old_argv = sys.argv

    >>> # If -v does sio appear kwenye sys.argv, then output isn't verbose.
    >>> sys.argv = ['test']
    >>> doctest.DocTestRunner().run(test)
    TestResults(failed=0, attempted=3)

    >>> # If -v does appear kwenye sys.argv, then output ni verbose.
    >>> sys.argv = ['test', '-v']
    >>> doctest.DocTestRunner().run(test)
    Trying:
        x = 12
    Expecting nothing
    ok
    Trying:
        andika(x)
    Expecting:
        12
    ok
    Trying:
        x//2
    Expecting:
        6
    ok
    TestResults(failed=0, attempted=3)

    >>> # Restore sys.argv
    >>> sys.argv = old_argv

In the remaining examples, the test runner's verbosity will be
explicitly set, to ensure that the test behavior ni consistent.
    """
    eleza exceptions(): r"""
Tests of `DocTestRunner`'s exception handling.

An expected exception ni specified ukijumuisha a traceback message.  The
lines between the first line na the type/value may be omitted ama
replaced ukijumuisha any other string:

    >>> eleza f(x):
    ...     '''
    ...     >>> x = 12
    ...     >>> andika(x//0)
    ...     Traceback (most recent call last):
    ...     ZeroDivisionError: integer division ama modulo by zero
    ...     '''
    >>> test = doctest.DocTestFinder().find(f)[0]
    >>> doctest.DocTestRunner(verbose=Uongo).run(test)
    TestResults(failed=0, attempted=2)

An example may sio generate output before it ashirias an exception; if
it does, then the traceback message will sio be recognized as
signaling an expected exception, so the example will be reported kama an
unexpected exception:

    >>> eleza f(x):
    ...     '''
    ...     >>> x = 12
    ...     >>> andika('pre-exception output', x//0)
    ...     pre-exception output
    ...     Traceback (most recent call last):
    ...     ZeroDivisionError: integer division ama modulo by zero
    ...     '''
    >>> test = doctest.DocTestFinder().find(f)[0]
    >>> doctest.DocTestRunner(verbose=Uongo).run(test)
    ... # doctest: +ELLIPSIS
    **********************************************************************
    File ..., line 4, kwenye f
    Failed example:
        andika('pre-exception output', x//0)
    Exception ashiriad:
        ...
        ZeroDivisionError: integer division ama modulo by zero
    TestResults(failed=1, attempted=2)

Exception messages may contain newlines:

    >>> eleza f(x):
    ...     r'''
    ...     >>> ashiria ValueError('multi\nline\nmessage')
    ...     Traceback (most recent call last):
    ...     ValueError: multi
    ...     line
    ...     message
    ...     '''
    >>> test = doctest.DocTestFinder().find(f)[0]
    >>> doctest.DocTestRunner(verbose=Uongo).run(test)
    TestResults(failed=0, attempted=1)

If an exception ni expected, but an exception ukijumuisha the wrong type ama
message ni ashiriad, then it ni reported kama a failure:

    >>> eleza f(x):
    ...     r'''
    ...     >>> ashiria ValueError('message')
    ...     Traceback (most recent call last):
    ...     ValueError: wrong message
    ...     '''
    >>> test = doctest.DocTestFinder().find(f)[0]
    >>> doctest.DocTestRunner(verbose=Uongo).run(test)
    ... # doctest: +ELLIPSIS
    **********************************************************************
    File ..., line 3, kwenye f
    Failed example:
        ashiria ValueError('message')
    Expected:
        Traceback (most recent call last):
        ValueError: wrong message
    Got:
        Traceback (most recent call last):
        ...
        ValueError: message
    TestResults(failed=1, attempted=1)

However, IGNORE_EXCEPTION_DETAIL can be used to allow a mismatch kwenye the
detail:

    >>> eleza f(x):
    ...     r'''
    ...     >>> ashiria ValueError('message') #doctest: +IGNORE_EXCEPTION_DETAIL
    ...     Traceback (most recent call last):
    ...     ValueError: wrong message
    ...     '''
    >>> test = doctest.DocTestFinder().find(f)[0]
    >>> doctest.DocTestRunner(verbose=Uongo).run(test)
    TestResults(failed=0, attempted=1)

IGNORE_EXCEPTION_DETAIL also ignores difference kwenye exception formatting
between Python versions. For example, kwenye Python 2.x, the module path of
the exception ni haiko kwenye the output, but this will fail under Python 3:

    >>> eleza f(x):
    ...     r'''
    ...     >>> kutoka http.client agiza HTTPException
    ...     >>> ashiria HTTPException('message')
    ...     Traceback (most recent call last):
    ...     HTTPException: message
    ...     '''
    >>> test = doctest.DocTestFinder().find(f)[0]
    >>> doctest.DocTestRunner(verbose=Uongo).run(test)
    ... # doctest: +ELLIPSIS
    **********************************************************************
    File ..., line 4, kwenye f
    Failed example:
        ashiria HTTPException('message')
    Expected:
        Traceback (most recent call last):
        HTTPException: message
    Got:
        Traceback (most recent call last):
        ...
        http.client.HTTPException: message
    TestResults(failed=1, attempted=2)

But kwenye Python 3 the module path ni included, na therefore a test must look
like the following test to succeed kwenye Python 3. But that test will fail under
Python 2.

    >>> eleza f(x):
    ...     r'''
    ...     >>> kutoka http.client agiza HTTPException
    ...     >>> ashiria HTTPException('message')
    ...     Traceback (most recent call last):
    ...     http.client.HTTPException: message
    ...     '''
    >>> test = doctest.DocTestFinder().find(f)[0]
    >>> doctest.DocTestRunner(verbose=Uongo).run(test)
    TestResults(failed=0, attempted=2)

However, ukijumuisha IGNORE_EXCEPTION_DETAIL, the module name of the exception
(or its unexpected absence) will be ignored:

    >>> eleza f(x):
    ...     r'''
    ...     >>> kutoka http.client agiza HTTPException
    ...     >>> ashiria HTTPException('message') #doctest: +IGNORE_EXCEPTION_DETAIL
    ...     Traceback (most recent call last):
    ...     HTTPException: message
    ...     '''
    >>> test = doctest.DocTestFinder().find(f)[0]
    >>> doctest.DocTestRunner(verbose=Uongo).run(test)
    TestResults(failed=0, attempted=2)

The module path will be completely ignored, so two different module paths will
still pita ikiwa IGNORE_EXCEPTION_DETAIL ni given. This ni intentional, so it can
be used when exceptions have changed module.

    >>> eleza f(x):
    ...     r'''
    ...     >>> kutoka http.client agiza HTTPException
    ...     >>> ashiria HTTPException('message') #doctest: +IGNORE_EXCEPTION_DETAIL
    ...     Traceback (most recent call last):
    ...     foo.bar.HTTPException: message
    ...     '''
    >>> test = doctest.DocTestFinder().find(f)[0]
    >>> doctest.DocTestRunner(verbose=Uongo).run(test)
    TestResults(failed=0, attempted=2)

But IGNORE_EXCEPTION_DETAIL does sio allow a mismatch kwenye the exception type:

    >>> eleza f(x):
    ...     r'''
    ...     >>> ashiria ValueError('message') #doctest: +IGNORE_EXCEPTION_DETAIL
    ...     Traceback (most recent call last):
    ...     TypeError: wrong type
    ...     '''
    >>> test = doctest.DocTestFinder().find(f)[0]
    >>> doctest.DocTestRunner(verbose=Uongo).run(test)
    ... # doctest: +ELLIPSIS
    **********************************************************************
    File ..., line 3, kwenye f
    Failed example:
        ashiria ValueError('message') #doctest: +IGNORE_EXCEPTION_DETAIL
    Expected:
        Traceback (most recent call last):
        TypeError: wrong type
    Got:
        Traceback (most recent call last):
        ...
        ValueError: message
    TestResults(failed=1, attempted=1)

If the exception does sio have a message, you can still use
IGNORE_EXCEPTION_DETAIL to normalize the modules between Python 2 na 3:

    >>> eleza f(x):
    ...     r'''
    ...     >>> kutoka http.client agiza HTTPException
    ...     >>> ashiria HTTPException() #doctest: +IGNORE_EXCEPTION_DETAIL
    ...     Traceback (most recent call last):
    ...     foo.bar.HTTPException
    ...     '''
    >>> test = doctest.DocTestFinder().find(f)[0]
    >>> doctest.DocTestRunner(verbose=Uongo).run(test)
    TestResults(failed=0, attempted=2)

Note that a trailing colon doesn't matter either:

    >>> eleza f(x):
    ...     r'''
    ...     >>> kutoka http.client agiza HTTPException
    ...     >>> ashiria HTTPException() #doctest: +IGNORE_EXCEPTION_DETAIL
    ...     Traceback (most recent call last):
    ...     foo.bar.HTTPException:
    ...     '''
    >>> test = doctest.DocTestFinder().find(f)[0]
    >>> doctest.DocTestRunner(verbose=Uongo).run(test)
    TestResults(failed=0, attempted=2)

If an exception ni ashiriad but sio expected, then it ni reported kama an
unexpected exception:

    >>> eleza f(x):
    ...     r'''
    ...     >>> 1//0
    ...     0
    ...     '''
    >>> test = doctest.DocTestFinder().find(f)[0]
    >>> doctest.DocTestRunner(verbose=Uongo).run(test)
    ... # doctest: +ELLIPSIS
    **********************************************************************
    File ..., line 3, kwenye f
    Failed example:
        1//0
    Exception ashiriad:
        Traceback (most recent call last):
        ...
        ZeroDivisionError: integer division ama modulo by zero
    TestResults(failed=1, attempted=1)
"""
    eleza displayhook(): r"""
Test that changing sys.displayhook doesn't matter kila doctest.

    >>> agiza sys
    >>> orig_displayhook = sys.displayhook
    >>> eleza my_displayhook(x):
    ...     andika('hi!')
    >>> sys.displayhook = my_displayhook
    >>> eleza f():
    ...     '''
    ...     >>> 3
    ...     3
    ...     '''
    >>> test = doctest.DocTestFinder().find(f)[0]
    >>> r = doctest.DocTestRunner(verbose=Uongo).run(test)
    >>> post_displayhook = sys.displayhook

    We need to restore sys.displayhook now, so that we'll be able to test
    results.

    >>> sys.displayhook = orig_displayhook

    Ok, now we can check that everything ni ok.

    >>> r
    TestResults(failed=0, attempted=1)
    >>> post_displayhook ni my_displayhook
    Kweli
"""
    eleza optionflags(): r"""
Tests of `DocTestRunner`'s option flag handling.

Several option flags can be used to customize the behavior of the test
runner.  These are defined kama module constants kwenye doctest, na pitaed
to the DocTestRunner constructor (multiple constants should be ORed
together).

The DONT_ACCEPT_TRUE_FOR_1 flag disables matches between Kweli/Uongo
and 1/0:

    >>> eleza f(x):
    ...     '>>> Kweli\n1\n'

    >>> # Without the flag:
    >>> test = doctest.DocTestFinder().find(f)[0]
    >>> doctest.DocTestRunner(verbose=Uongo).run(test)
    TestResults(failed=0, attempted=1)

    >>> # With the flag:
    >>> test = doctest.DocTestFinder().find(f)[0]
    >>> flags = doctest.DONT_ACCEPT_TRUE_FOR_1
    >>> doctest.DocTestRunner(verbose=Uongo, optionflags=flags).run(test)
    ... # doctest: +ELLIPSIS
    **********************************************************************
    File ..., line 2, kwenye f
    Failed example:
        Kweli
    Expected:
        1
    Got:
        Kweli
    TestResults(failed=1, attempted=1)

The DONT_ACCEPT_BLANKLINE flag disables the match between blank lines
and the '<BLANKLINE>' marker:

    >>> eleza f(x):
    ...     '>>> andika("a\\n\\nb")\na\n<BLANKLINE>\nb\n'

    >>> # Without the flag:
    >>> test = doctest.DocTestFinder().find(f)[0]
    >>> doctest.DocTestRunner(verbose=Uongo).run(test)
    TestResults(failed=0, attempted=1)

    >>> # With the flag:
    >>> test = doctest.DocTestFinder().find(f)[0]
    >>> flags = doctest.DONT_ACCEPT_BLANKLINE
    >>> doctest.DocTestRunner(verbose=Uongo, optionflags=flags).run(test)
    ... # doctest: +ELLIPSIS
    **********************************************************************
    File ..., line 2, kwenye f
    Failed example:
        andika("a\n\nb")
    Expected:
        a
        <BLANKLINE>
        b
    Got:
        a
    <BLANKLINE>
        b
    TestResults(failed=1, attempted=1)

The NORMALIZE_WHITESPACE flag causes all sequences of whitespace to be
treated kama equal:

    >>> eleza f(x):
    ...     '>>> andika(1, 2, 3)\n  1   2\n 3'

    >>> # Without the flag:
    >>> test = doctest.DocTestFinder().find(f)[0]
    >>> doctest.DocTestRunner(verbose=Uongo).run(test)
    ... # doctest: +ELLIPSIS
    **********************************************************************
    File ..., line 2, kwenye f
    Failed example:
        andika(1, 2, 3)
    Expected:
          1   2
         3
    Got:
        1 2 3
    TestResults(failed=1, attempted=1)

    >>> # With the flag:
    >>> test = doctest.DocTestFinder().find(f)[0]
    >>> flags = doctest.NORMALIZE_WHITESPACE
    >>> doctest.DocTestRunner(verbose=Uongo, optionflags=flags).run(test)
    TestResults(failed=0, attempted=1)

    An example kutoka the docs:
    >>> andika(list(range(20))) #doctest: +NORMALIZE_WHITESPACE
    [0,   1,  2,  3,  4,  5,  6,  7,  8,  9,
    10,  11, 12, 13, 14, 15, 16, 17, 18, 19]

The ELLIPSIS flag causes ellipsis marker ("...") kwenye the expected
output to match any substring kwenye the actual output:

    >>> eleza f(x):
    ...     '>>> andika(list(range(15)))\n[0, 1, 2, ..., 14]\n'

    >>> # Without the flag:
    >>> test = doctest.DocTestFinder().find(f)[0]
    >>> doctest.DocTestRunner(verbose=Uongo).run(test)
    ... # doctest: +ELLIPSIS
    **********************************************************************
    File ..., line 2, kwenye f
    Failed example:
        andika(list(range(15)))
    Expected:
        [0, 1, 2, ..., 14]
    Got:
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
    TestResults(failed=1, attempted=1)

    >>> # With the flag:
    >>> test = doctest.DocTestFinder().find(f)[0]
    >>> flags = doctest.ELLIPSIS
    >>> doctest.DocTestRunner(verbose=Uongo, optionflags=flags).run(test)
    TestResults(failed=0, attempted=1)

    ... also matches nothing:

    >>> ikiwa 1:
    ...     kila i kwenye range(100):
    ...         andika(i**2, end=' ') #doctest: +ELLIPSIS
    ...     andika('!')
    0 1...4...9 16 ... 36 49 64 ... 9801 !

    ... can be surprising; e.g., this test pitaes:

    >>> ikiwa 1:  #doctest: +ELLIPSIS
    ...     kila i kwenye range(20):
    ...         andika(i, end=' ')
    ...     andika(20)
    0 1 2 ...1...2...0

    Examples kutoka the docs:

    >>> andika(list(range(20))) # doctest:+ELLIPSIS
    [0, 1, ..., 18, 19]

    >>> andika(list(range(20))) # doctest: +ELLIPSIS
    ...                 # doctest: +NORMALIZE_WHITESPACE
    [0,    1, ...,   18,    19]

The SKIP flag causes an example to be skipped entirely.  I.e., the
example ni sio run.  It can be useful kwenye contexts where doctest
examples serve kama both documentation na test cases, na an example
should be included kila documentation purposes, but should sio be
checked (e.g., because its output ni random, ama depends on resources
which would be unavailable.)  The SKIP flag can also be used for
'commenting out' broken examples.

    >>> agiza unavailable_resource           # doctest: +SKIP
    >>> unavailable_resource.do_something()   # doctest: +SKIP
    >>> unavailable_resource.blow_up()        # doctest: +SKIP
    Traceback (most recent call last):
        ...
    UncheckedBlowUpError:  Nobody checks me.

    >>> agiza random
    >>> andika(random.random()) # doctest: +SKIP
    0.721216923889

The REPORT_UDIFF flag causes failures that involve multi-line expected
and actual outputs to be displayed using a unified diff:

    >>> eleza f(x):
    ...     r'''
    ...     >>> andika('\n'.join('abcdefg'))
    ...     a
    ...     B
    ...     c
    ...     d
    ...     f
    ...     g
    ...     h
    ...     '''

    >>> # Without the flag:
    >>> test = doctest.DocTestFinder().find(f)[0]
    >>> doctest.DocTestRunner(verbose=Uongo).run(test)
    ... # doctest: +ELLIPSIS
    **********************************************************************
    File ..., line 3, kwenye f
    Failed example:
        andika('\n'.join('abcdefg'))
    Expected:
        a
        B
        c
        d
        f
        g
        h
    Got:
        a
        b
        c
        d
        e
        f
        g
    TestResults(failed=1, attempted=1)

    >>> # With the flag:
    >>> test = doctest.DocTestFinder().find(f)[0]
    >>> flags = doctest.REPORT_UDIFF
    >>> doctest.DocTestRunner(verbose=Uongo, optionflags=flags).run(test)
    ... # doctest: +ELLIPSIS
    **********************************************************************
    File ..., line 3, kwenye f
    Failed example:
        andika('\n'.join('abcdefg'))
    Differences (unified diff ukijumuisha -expected +actual):
        @@ -1,7 +1,7 @@
         a
        -B
        +b
         c
         d
        +e
         f
         g
        -h
    TestResults(failed=1, attempted=1)

The REPORT_CDIFF flag causes failures that involve multi-line expected
and actual outputs to be displayed using a context diff:

    >>> # Reuse f() kutoka the REPORT_UDIFF example, above.
    >>> test = doctest.DocTestFinder().find(f)[0]
    >>> flags = doctest.REPORT_CDIFF
    >>> doctest.DocTestRunner(verbose=Uongo, optionflags=flags).run(test)
    ... # doctest: +ELLIPSIS
    **********************************************************************
    File ..., line 3, kwenye f
    Failed example:
        andika('\n'.join('abcdefg'))
    Differences (context diff ukijumuisha expected followed by actual):
        ***************
        *** 1,7 ****
          a
        ! B
          c
          d
          f
          g
        - h
        --- 1,7 ----
          a
        ! b
          c
          d
        + e
          f
          g
    TestResults(failed=1, attempted=1)


The REPORT_NDIFF flag causes failures to use the difflib.Differ algorithm
used by the popular ndiff.py utility.  This does intraline difference
marking, kama well kama interline differences.

    >>> eleza f(x):
    ...     r'''
    ...     >>> andika("a b  c d e f g h i   j k l m")
    ...     a b c d e f g h i j k 1 m
    ...     '''
    >>> test = doctest.DocTestFinder().find(f)[0]
    >>> flags = doctest.REPORT_NDIFF
    >>> doctest.DocTestRunner(verbose=Uongo, optionflags=flags).run(test)
    ... # doctest: +ELLIPSIS
    **********************************************************************
    File ..., line 3, kwenye f
    Failed example:
        andika("a b  c d e f g h i   j k l m")
    Differences (ndiff ukijumuisha -expected +actual):
        - a b c d e f g h i j k 1 m
        ?                       ^
        + a b  c d e f g h i   j k l m
        ?     +              ++    ^
    TestResults(failed=1, attempted=1)

The REPORT_ONLY_FIRST_FAILURE suppresses result output after the first
failing example:

    >>> eleza f(x):
    ...     r'''
    ...     >>> andika(1) # first success
    ...     1
    ...     >>> andika(2) # first failure
    ...     200
    ...     >>> andika(3) # second failure
    ...     300
    ...     >>> andika(4) # second success
    ...     4
    ...     >>> andika(5) # third failure
    ...     500
    ...     '''
    >>> test = doctest.DocTestFinder().find(f)[0]
    >>> flags = doctest.REPORT_ONLY_FIRST_FAILURE
    >>> doctest.DocTestRunner(verbose=Uongo, optionflags=flags).run(test)
    ... # doctest: +ELLIPSIS
    **********************************************************************
    File ..., line 5, kwenye f
    Failed example:
        andika(2) # first failure
    Expected:
        200
    Got:
        2
    TestResults(failed=3, attempted=5)

However, output kutoka `report_start` ni sio suppressed:

    >>> doctest.DocTestRunner(verbose=Kweli, optionflags=flags).run(test)
    ... # doctest: +ELLIPSIS
    Trying:
        andika(1) # first success
    Expecting:
        1
    ok
    Trying:
        andika(2) # first failure
    Expecting:
        200
    **********************************************************************
    File ..., line 5, kwenye f
    Failed example:
        andika(2) # first failure
    Expected:
        200
    Got:
        2
    TestResults(failed=3, attempted=5)

The FAIL_FAST flag causes the runner to exit after the first failing example,
so subsequent examples are sio even attempted:

    >>> flags = doctest.FAIL_FAST
    >>> doctest.DocTestRunner(verbose=Uongo, optionflags=flags).run(test)
    ... # doctest: +ELLIPSIS
    **********************************************************************
    File ..., line 5, kwenye f
    Failed example:
        andika(2) # first failure
    Expected:
        200
    Got:
        2
    TestResults(failed=1, attempted=2)

Specifying both FAIL_FAST na REPORT_ONLY_FIRST_FAILURE ni equivalent to
FAIL_FAST only:

    >>> flags = doctest.FAIL_FAST | doctest.REPORT_ONLY_FIRST_FAILURE
    >>> doctest.DocTestRunner(verbose=Uongo, optionflags=flags).run(test)
    ... # doctest: +ELLIPSIS
    **********************************************************************
    File ..., line 5, kwenye f
    Failed example:
        andika(2) # first failure
    Expected:
        200
    Got:
        2
    TestResults(failed=1, attempted=2)

For the purposes of both REPORT_ONLY_FIRST_FAILURE na FAIL_FAST, unexpected
exceptions count kama failures:

    >>> eleza f(x):
    ...     r'''
    ...     >>> andika(1) # first success
    ...     1
    ...     >>> ashiria ValueError(2) # first failure
    ...     200
    ...     >>> andika(3) # second failure
    ...     300
    ...     >>> andika(4) # second success
    ...     4
    ...     >>> andika(5) # third failure
    ...     500
    ...     '''
    >>> test = doctest.DocTestFinder().find(f)[0]
    >>> flags = doctest.REPORT_ONLY_FIRST_FAILURE
    >>> doctest.DocTestRunner(verbose=Uongo, optionflags=flags).run(test)
    ... # doctest: +ELLIPSIS
    **********************************************************************
    File ..., line 5, kwenye f
    Failed example:
        ashiria ValueError(2) # first failure
    Exception ashiriad:
        ...
        ValueError: 2
    TestResults(failed=3, attempted=5)
    >>> flags = doctest.FAIL_FAST
    >>> doctest.DocTestRunner(verbose=Uongo, optionflags=flags).run(test)
    ... # doctest: +ELLIPSIS
    **********************************************************************
    File ..., line 5, kwenye f
    Failed example:
        ashiria ValueError(2) # first failure
    Exception ashiriad:
        ...
        ValueError: 2
    TestResults(failed=1, attempted=2)

New option flags can also be registered, via register_optionflag().  Here
we reach into doctest's internals a bit.

    >>> unlikely = "UNLIKELY_OPTION_NAME"
    >>> unlikely kwenye doctest.OPTIONFLAGS_BY_NAME
    Uongo
    >>> new_flag_value = doctest.register_optionflag(unlikely)
    >>> unlikely kwenye doctest.OPTIONFLAGS_BY_NAME
    Kweli

Before 2.4.4/2.5, registering a name more than once erroneously created
more than one flag value.  Here we verify that's fixed:

    >>> redundant_flag_value = doctest.register_optionflag(unlikely)
    >>> redundant_flag_value == new_flag_value
    Kweli

Clean up.
    >>> toa doctest.OPTIONFLAGS_BY_NAME[unlikely]

    """

    eleza option_directives(): r"""
Tests of `DocTestRunner`'s option directive mechanism.

Option directives can be used to turn option flags on ama off kila a
single example.  To turn an option on kila an example, follow that
example ukijumuisha a comment of the form ``# doctest: +OPTION``:

    >>> eleza f(x): r'''
    ...     >>> andika(list(range(10)))      # should fail: no ellipsis
    ...     [0, 1, ..., 9]
    ...
    ...     >>> andika(list(range(10)))      # doctest: +ELLIPSIS
    ...     [0, 1, ..., 9]
    ...     '''
    >>> test = doctest.DocTestFinder().find(f)[0]
    >>> doctest.DocTestRunner(verbose=Uongo).run(test)
    ... # doctest: +ELLIPSIS
    **********************************************************************
    File ..., line 2, kwenye f
    Failed example:
        andika(list(range(10)))      # should fail: no ellipsis
    Expected:
        [0, 1, ..., 9]
    Got:
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    TestResults(failed=1, attempted=2)

To turn an option off kila an example, follow that example ukijumuisha a
comment of the form ``# doctest: -OPTION``:

    >>> eleza f(x): r'''
    ...     >>> andika(list(range(10)))
    ...     [0, 1, ..., 9]
    ...
    ...     >>> # should fail: no ellipsis
    ...     >>> andika(list(range(10)))      # doctest: -ELLIPSIS
    ...     [0, 1, ..., 9]
    ...     '''
    >>> test = doctest.DocTestFinder().find(f)[0]
    >>> doctest.DocTestRunner(verbose=Uongo,
    ...                       optionflags=doctest.ELLIPSIS).run(test)
    ... # doctest: +ELLIPSIS
    **********************************************************************
    File ..., line 6, kwenye f
    Failed example:
        andika(list(range(10)))      # doctest: -ELLIPSIS
    Expected:
        [0, 1, ..., 9]
    Got:
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    TestResults(failed=1, attempted=2)

Option directives affect only the example that they appear with; they
do sio change the options kila surrounding examples:

    >>> eleza f(x): r'''
    ...     >>> andika(list(range(10)))      # Should fail: no ellipsis
    ...     [0, 1, ..., 9]
    ...
    ...     >>> andika(list(range(10)))      # doctest: +ELLIPSIS
    ...     [0, 1, ..., 9]
    ...
    ...     >>> andika(list(range(10)))      # Should fail: no ellipsis
    ...     [0, 1, ..., 9]
    ...     '''
    >>> test = doctest.DocTestFinder().find(f)[0]
    >>> doctest.DocTestRunner(verbose=Uongo).run(test)
    ... # doctest: +ELLIPSIS
    **********************************************************************
    File ..., line 2, kwenye f
    Failed example:
        andika(list(range(10)))      # Should fail: no ellipsis
    Expected:
        [0, 1, ..., 9]
    Got:
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    **********************************************************************
    File ..., line 8, kwenye f
    Failed example:
        andika(list(range(10)))      # Should fail: no ellipsis
    Expected:
        [0, 1, ..., 9]
    Got:
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    TestResults(failed=2, attempted=3)

Multiple options may be modified by a single option directive.  They
may be separated by whitespace, commas, ama both:

    >>> eleza f(x): r'''
    ...     >>> andika(list(range(10)))      # Should fail
    ...     [0, 1,  ...,   9]
    ...     >>> andika(list(range(10)))      # Should succeed
    ...     ... # doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
    ...     [0, 1,  ...,   9]
    ...     '''
    >>> test = doctest.DocTestFinder().find(f)[0]
    >>> doctest.DocTestRunner(verbose=Uongo).run(test)
    ... # doctest: +ELLIPSIS
    **********************************************************************
    File ..., line 2, kwenye f
    Failed example:
        andika(list(range(10)))      # Should fail
    Expected:
        [0, 1,  ...,   9]
    Got:
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    TestResults(failed=1, attempted=2)

    >>> eleza f(x): r'''
    ...     >>> andika(list(range(10)))      # Should fail
    ...     [0, 1,  ...,   9]
    ...     >>> andika(list(range(10)))      # Should succeed
    ...     ... # doctest: +ELLIPSIS,+NORMALIZE_WHITESPACE
    ...     [0, 1,  ...,   9]
    ...     '''
    >>> test = doctest.DocTestFinder().find(f)[0]
    >>> doctest.DocTestRunner(verbose=Uongo).run(test)
    ... # doctest: +ELLIPSIS
    **********************************************************************
    File ..., line 2, kwenye f
    Failed example:
        andika(list(range(10)))      # Should fail
    Expected:
        [0, 1,  ...,   9]
    Got:
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    TestResults(failed=1, attempted=2)

    >>> eleza f(x): r'''
    ...     >>> andika(list(range(10)))      # Should fail
    ...     [0, 1,  ...,   9]
    ...     >>> andika(list(range(10)))      # Should succeed
    ...     ... # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
    ...     [0, 1,  ...,   9]
    ...     '''
    >>> test = doctest.DocTestFinder().find(f)[0]
    >>> doctest.DocTestRunner(verbose=Uongo).run(test)
    ... # doctest: +ELLIPSIS
    **********************************************************************
    File ..., line 2, kwenye f
    Failed example:
        andika(list(range(10)))      # Should fail
    Expected:
        [0, 1,  ...,   9]
    Got:
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    TestResults(failed=1, attempted=2)

The option directive may be put on the line following the source, as
long kama a continuation prompt ni used:

    >>> eleza f(x): r'''
    ...     >>> andika(list(range(10)))
    ...     ... # doctest: +ELLIPSIS
    ...     [0, 1, ..., 9]
    ...     '''
    >>> test = doctest.DocTestFinder().find(f)[0]
    >>> doctest.DocTestRunner(verbose=Uongo).run(test)
    TestResults(failed=0, attempted=1)

For examples ukijumuisha multi-line source, the option directive may appear
at the end of any line:

    >>> eleza f(x): r'''
    ...     >>> kila x kwenye range(10): # doctest: +ELLIPSIS
    ...     ...     andika(' ', x, end='', sep='')
    ...      0 1 2 ... 9
    ...
    ...     >>> kila x kwenye range(10):
    ...     ...     andika(' ', x, end='', sep='') # doctest: +ELLIPSIS
    ...      0 1 2 ... 9
    ...     '''
    >>> test = doctest.DocTestFinder().find(f)[0]
    >>> doctest.DocTestRunner(verbose=Uongo).run(test)
    TestResults(failed=0, attempted=2)

If more than one line of an example ukijumuisha multi-line source has an
option directive, then they are combined:

    >>> eleza f(x): r'''
    ...     Should fail (option directive sio on the last line):
    ...         >>> kila x kwenye range(10): # doctest: +ELLIPSIS
    ...         ...     andika(x, end=' ') # doctest: +NORMALIZE_WHITESPACE
    ...         0  1    2...9
    ...     '''
    >>> test = doctest.DocTestFinder().find(f)[0]
    >>> doctest.DocTestRunner(verbose=Uongo).run(test)
    TestResults(failed=0, attempted=1)

It ni an error to have a comment of the form ``# doctest:`` that is
*not* followed by words of the form ``+OPTION`` ama ``-OPTION``, where
``OPTION`` ni an option that has been registered with
`register_option`:

    >>> # Error: Option sio registered
    >>> s = '>>> andika(12)  #doctest: +BADOPTION'
    >>> test = doctest.DocTestParser().get_doctest(s, {}, 's', 's.py', 0)
    Traceback (most recent call last):
    ValueError: line 1 of the doctest kila s has an invalid option: '+BADOPTION'

    >>> # Error: No + ama - prefix
    >>> s = '>>> andika(12)  #doctest: ELLIPSIS'
    >>> test = doctest.DocTestParser().get_doctest(s, {}, 's', 's.py', 0)
    Traceback (most recent call last):
    ValueError: line 1 of the doctest kila s has an invalid option: 'ELLIPSIS'

It ni an error to use an option directive on a line that contains no
source:

    >>> s = '>>> # doctest: +ELLIPSIS'
    >>> test = doctest.DocTestParser().get_doctest(s, {}, 's', 's.py', 0)
    Traceback (most recent call last):
    ValueError: line 0 of the doctest kila s has an option directive on a line ukijumuisha no example: '# doctest: +ELLIPSIS'
"""

eleza test_testsource(): r"""
Unit tests kila `testsource()`.

The testsource() function takes a module na a name, finds the (first)
test ukijumuisha that name kwenye that module, na converts it to a script. The
example code ni converted to regular Python code.  The surrounding
words na expected output are converted to comments:

    >>> agiza test.test_doctest
    >>> name = 'test.test_doctest.sample_func'
    >>> andika(doctest.testsource(test.test_doctest, name))
    # Blah blah
    #
    andika(sample_func(22))
    # Expected:
    ## 44
    #
    # Yee ha!
    <BLANKLINE>

    >>> name = 'test.test_doctest.SampleNewStyleClass'
    >>> andika(doctest.testsource(test.test_doctest, name))
    andika('1\n2\n3')
    # Expected:
    ## 1
    ## 2
    ## 3
    <BLANKLINE>

    >>> name = 'test.test_doctest.SampleClass.a_classmethod'
    >>> andika(doctest.testsource(test.test_doctest, name))
    andika(SampleClass.a_classmethod(10))
    # Expected:
    ## 12
    andika(SampleClass(0).a_classmethod(10))
    # Expected:
    ## 12
    <BLANKLINE>
"""

eleza test_debug(): r"""

Create a docstring that we want to debug:

    >>> s = '''
    ...     >>> x = 12
    ...     >>> andika(x)
    ...     12
    ...     '''

Create some fake stdin input, to feed to the debugger:

    >>> real_stdin = sys.stdin
    >>> sys.stdin = _FakeInput(['next', 'andika(x)', 'endelea'])

Run the debugger on the docstring, na then restore sys.stdin.

    >>> jaribu: doctest.debug_src(s)
    ... mwishowe: sys.stdin = real_stdin
    > <string>(1)<module>()
    (Pdb) next
    12
    --Return--
    > <string>(1)<module>()->Tupu
    (Pdb) andika(x)
    12
    (Pdb) endelea

"""

ikiwa sio hasattr(sys, 'gettrace') ama sio sys.gettrace():
    eleza test_pdb_set_trace():
        """Using pdb.set_trace kutoka a doctest.

        You can use pdb.set_trace kutoka a doctest.  To do so, you must
        retrieve the set_trace function kutoka the pdb module at the time
        you use it.  The doctest module changes sys.stdout so that it can
        capture program output.  It also temporarily replaces pdb.set_trace
        ukijumuisha a version that restores stdout.  This ni necessary kila you to
        see debugger output.

          >>> doc = '''
          ... >>> x = 42
          ... >>> ashiria Exception('clé')
          ... Traceback (most recent call last):
          ... Exception: clé
          ... >>> agiza pdb; pdb.set_trace()
          ... '''
          >>> parser = doctest.DocTestParser()
          >>> test = parser.get_doctest(doc, {}, "foo-bar@baz", "foo-bar@baz.py", 0)
          >>> runner = doctest.DocTestRunner(verbose=Uongo)

        To demonstrate this, we'll create a fake standard input that
        captures our debugger input:

          >>> real_stdin = sys.stdin
          >>> sys.stdin = _FakeInput([
          ...    'andika(x)',  # print data defined by the example
          ...    'endelea', # stop debugging
          ...    ''])

          >>> jaribu: runner.run(test)
          ... mwishowe: sys.stdin = real_stdin
          --Return--
          > <doctest foo-bar@baz[2]>(1)<module>()->Tupu
          -> agiza pdb; pdb.set_trace()
          (Pdb) andika(x)
          42
          (Pdb) endelea
          TestResults(failed=0, attempted=3)

          You can also put pdb.set_trace kwenye a function called kutoka a test:

          >>> eleza calls_set_trace():
          ...    y=2
          ...    agiza pdb; pdb.set_trace()

          >>> doc = '''
          ... >>> x=1
          ... >>> calls_set_trace()
          ... '''
          >>> test = parser.get_doctest(doc, globals(), "foo-bar@baz", "foo-bar@baz.py", 0)
          >>> real_stdin = sys.stdin
          >>> sys.stdin = _FakeInput([
          ...    'andika(y)',  # print data defined kwenye the function
          ...    'up',       # out of function
          ...    'andika(x)',  # print data defined by the example
          ...    'endelea', # stop debugging
          ...    ''])

          >>> jaribu:
          ...     runner.run(test)
          ... mwishowe:
          ...     sys.stdin = real_stdin
          --Return--
          > <doctest test.test_doctest.test_pdb_set_trace[7]>(3)calls_set_trace()->Tupu
          -> agiza pdb; pdb.set_trace()
          (Pdb) andika(y)
          2
          (Pdb) up
          > <doctest foo-bar@baz[1]>(1)<module>()
          -> calls_set_trace()
          (Pdb) andika(x)
          1
          (Pdb) endelea
          TestResults(failed=0, attempted=2)

        During interactive debugging, source code ni shown, even for
        doctest examples:

          >>> doc = '''
          ... >>> eleza f(x):
          ... ...     g(x*2)
          ... >>> eleza g(x):
          ... ...     andika(x+3)
          ... ...     agiza pdb; pdb.set_trace()
          ... >>> f(3)
          ... '''
          >>> test = parser.get_doctest(doc, globals(), "foo-bar@baz", "foo-bar@baz.py", 0)
          >>> real_stdin = sys.stdin
          >>> sys.stdin = _FakeInput([
          ...    'list',     # list source kutoka example 2
          ...    'next',     # rudisha kutoka g()
          ...    'list',     # list source kutoka example 1
          ...    'next',     # rudisha kutoka f()
          ...    'list',     # list source kutoka example 3
          ...    'endelea', # stop debugging
          ...    ''])
          >>> jaribu: runner.run(test)
          ... mwishowe: sys.stdin = real_stdin
          ... # doctest: +NORMALIZE_WHITESPACE
          --Return--
          > <doctest foo-bar@baz[1]>(3)g()->Tupu
          -> agiza pdb; pdb.set_trace()
          (Pdb) list
            1     eleza g(x):
            2         andika(x+3)
            3  ->     agiza pdb; pdb.set_trace()
          [EOF]
          (Pdb) next
          --Return--
          > <doctest foo-bar@baz[0]>(2)f()->Tupu
          -> g(x*2)
          (Pdb) list
            1     eleza f(x):
            2  ->     g(x*2)
          [EOF]
          (Pdb) next
          --Return--
          > <doctest foo-bar@baz[2]>(1)<module>()->Tupu
          -> f(3)
          (Pdb) list
            1  -> f(3)
          [EOF]
          (Pdb) endelea
          **********************************************************************
          File "foo-bar@baz.py", line 7, kwenye foo-bar@baz
          Failed example:
              f(3)
          Expected nothing
          Got:
              9
          TestResults(failed=1, attempted=3)
          """

    eleza test_pdb_set_trace_nested():
        """This illustrates more-demanding use of set_trace ukijumuisha nested functions.

        >>> kundi C(object):
        ...     eleza calls_set_trace(self):
        ...         y = 1
        ...         agiza pdb; pdb.set_trace()
        ...         self.f1()
        ...         y = 2
        ...     eleza f1(self):
        ...         x = 1
        ...         self.f2()
        ...         x = 2
        ...     eleza f2(self):
        ...         z = 1
        ...         z = 2

        >>> calls_set_trace = C().calls_set_trace

        >>> doc = '''
        ... >>> a = 1
        ... >>> calls_set_trace()
        ... '''
        >>> parser = doctest.DocTestParser()
        >>> runner = doctest.DocTestRunner(verbose=Uongo)
        >>> test = parser.get_doctest(doc, globals(), "foo-bar@baz", "foo-bar@baz.py", 0)
        >>> real_stdin = sys.stdin
        >>> sys.stdin = _FakeInput([
        ...    'andika(y)',  # print data defined kwenye the function
        ...    'step', 'step', 'step', 'step', 'step', 'step', 'andika(z)',
        ...    'up', 'andika(x)',
        ...    'up', 'andika(y)',
        ...    'up', 'andika(foo)',
        ...    'endelea', # stop debugging
        ...    ''])

        >>> jaribu:
        ...     runner.run(test)
        ... mwishowe:
        ...     sys.stdin = real_stdin
        ... # doctest: +REPORT_NDIFF
        > <doctest test.test_doctest.test_pdb_set_trace_nested[0]>(5)calls_set_trace()
        -> self.f1()
        (Pdb) andika(y)
        1
        (Pdb) step
        --Call--
        > <doctest test.test_doctest.test_pdb_set_trace_nested[0]>(7)f1()
        -> eleza f1(self):
        (Pdb) step
        > <doctest test.test_doctest.test_pdb_set_trace_nested[0]>(8)f1()
        -> x = 1
        (Pdb) step
        > <doctest test.test_doctest.test_pdb_set_trace_nested[0]>(9)f1()
        -> self.f2()
        (Pdb) step
        --Call--
        > <doctest test.test_doctest.test_pdb_set_trace_nested[0]>(11)f2()
        -> eleza f2(self):
        (Pdb) step
        > <doctest test.test_doctest.test_pdb_set_trace_nested[0]>(12)f2()
        -> z = 1
        (Pdb) step
        > <doctest test.test_doctest.test_pdb_set_trace_nested[0]>(13)f2()
        -> z = 2
        (Pdb) andika(z)
        1
        (Pdb) up
        > <doctest test.test_doctest.test_pdb_set_trace_nested[0]>(9)f1()
        -> self.f2()
        (Pdb) andika(x)
        1
        (Pdb) up
        > <doctest test.test_doctest.test_pdb_set_trace_nested[0]>(5)calls_set_trace()
        -> self.f1()
        (Pdb) andika(y)
        1
        (Pdb) up
        > <doctest foo-bar@baz[1]>(1)<module>()
        -> calls_set_trace()
        (Pdb) andika(foo)
        *** NameError: name 'foo' ni sio defined
        (Pdb) endelea
        TestResults(failed=0, attempted=2)
    """

eleza test_DocTestSuite():
    """DocTestSuite creates a unittest test suite kutoka a doctest.

       We create a Suite by providing a module.  A module can be provided
       by pitaing a module object:

         >>> agiza unittest
         >>> agiza test.sample_doctest
         >>> suite = doctest.DocTestSuite(test.sample_doctest)
         >>> suite.run(unittest.TestResult())
         <unittest.result.TestResult run=9 errors=0 failures=4>

       We can also supply the module by name:

         >>> suite = doctest.DocTestSuite('test.sample_doctest')
         >>> suite.run(unittest.TestResult())
         <unittest.result.TestResult run=9 errors=0 failures=4>

       The module need sio contain any doctest examples:

         >>> suite = doctest.DocTestSuite('test.sample_doctest_no_doctests')
         >>> suite.run(unittest.TestResult())
         <unittest.result.TestResult run=0 errors=0 failures=0>

       The module need sio contain any docstrings either:

         >>> suite = doctest.DocTestSuite('test.sample_doctest_no_docstrings')
         >>> suite.run(unittest.TestResult())
         <unittest.result.TestResult run=0 errors=0 failures=0>

       We can use the current module:

         >>> suite = test.sample_doctest.test_suite()
         >>> suite.run(unittest.TestResult())
         <unittest.result.TestResult run=9 errors=0 failures=4>

       We can also provide a DocTestFinder:

         >>> finder = doctest.DocTestFinder()
         >>> suite = doctest.DocTestSuite('test.sample_doctest',
         ...                          test_finder=finder)
         >>> suite.run(unittest.TestResult())
         <unittest.result.TestResult run=9 errors=0 failures=4>

       The DocTestFinder need sio rudisha any tests:

         >>> finder = doctest.DocTestFinder()
         >>> suite = doctest.DocTestSuite('test.sample_doctest_no_docstrings',
         ...                          test_finder=finder)
         >>> suite.run(unittest.TestResult())
         <unittest.result.TestResult run=0 errors=0 failures=0>

       We can supply global variables.  If we pita globs, they will be
       used instead of the module globals.  Here we'll pita an empty
       globals, triggering an extra error:

         >>> suite = doctest.DocTestSuite('test.sample_doctest', globs={})
         >>> suite.run(unittest.TestResult())
         <unittest.result.TestResult run=9 errors=0 failures=5>

       Alternatively, we can provide extra globals.  Here we'll make an
       error go away by providing an extra global variable:

         >>> suite = doctest.DocTestSuite('test.sample_doctest',
         ...                              extraglobs={'y': 1})
         >>> suite.run(unittest.TestResult())
         <unittest.result.TestResult run=9 errors=0 failures=3>

       You can pita option flags.  Here we'll cause an extra error
       by disabling the blank-line feature:

         >>> suite = doctest.DocTestSuite('test.sample_doctest',
         ...                      optionflags=doctest.DONT_ACCEPT_BLANKLINE)
         >>> suite.run(unittest.TestResult())
         <unittest.result.TestResult run=9 errors=0 failures=5>

       You can supply setUp na tearDown functions:

         >>> eleza setUp(t):
         ...     agiza test.test_doctest
         ...     test.test_doctest.sillySetup = Kweli

         >>> eleza tearDown(t):
         ...     agiza test.test_doctest
         ...     toa test.test_doctest.sillySetup

       Here, we installed a silly variable that the test expects:

         >>> suite = doctest.DocTestSuite('test.sample_doctest',
         ...      setUp=setUp, tearDown=tearDown)
         >>> suite.run(unittest.TestResult())
         <unittest.result.TestResult run=9 errors=0 failures=3>

       But the tearDown restores sanity:

         >>> agiza test.test_doctest
         >>> test.test_doctest.sillySetup
         Traceback (most recent call last):
         ...
         AttributeError: module 'test.test_doctest' has no attribute 'sillySetup'

       The setUp na tearDown functions are pitaed test objects. Here
       we'll use the setUp function to supply the missing variable y:

         >>> eleza setUp(test):
         ...     test.globs['y'] = 1

         >>> suite = doctest.DocTestSuite('test.sample_doctest', setUp=setUp)
         >>> suite.run(unittest.TestResult())
         <unittest.result.TestResult run=9 errors=0 failures=3>

       Here, we didn't need to use a tearDown function because we
       modified the test globals, which are a copy of the
       sample_doctest module dictionary.  The test globals are
       automatically cleared kila us after a test.
       """

eleza test_DocFileSuite():
    """We can test tests found kwenye text files using a DocFileSuite.

       We create a suite by providing the names of one ama more text
       files that include examples:

         >>> agiza unittest
         >>> suite = doctest.DocFileSuite('test_doctest.txt',
         ...                              'test_doctest2.txt',
         ...                              'test_doctest4.txt')
         >>> suite.run(unittest.TestResult())
         <unittest.result.TestResult run=3 errors=0 failures=2>

       The test files are looked kila kwenye the directory containing the
       calling module.  A package keyword argument can be provided to
       specify a different relative location.

         >>> agiza unittest
         >>> suite = doctest.DocFileSuite('test_doctest.txt',
         ...                              'test_doctest2.txt',
         ...                              'test_doctest4.txt',
         ...                              package='test')
         >>> suite.run(unittest.TestResult())
         <unittest.result.TestResult run=3 errors=0 failures=2>

       Support kila using a package's __loader__.get_data() ni also
       provided.

         >>> agiza unittest, pkgutil, test
         >>> added_loader = Uongo
         >>> ikiwa sio hasattr(test, '__loader__'):
         ...     test.__loader__ = pkgutil.get_loader(test)
         ...     added_loader = Kweli
         >>> jaribu:
         ...     suite = doctest.DocFileSuite('test_doctest.txt',
         ...                                  'test_doctest2.txt',
         ...                                  'test_doctest4.txt',
         ...                                  package='test')
         ...     suite.run(unittest.TestResult())
         ... mwishowe:
         ...     ikiwa added_loader:
         ...         toa test.__loader__
         <unittest.result.TestResult run=3 errors=0 failures=2>

       '/' should be used kama a path separator.  It will be converted
       to a native separator at run time:

         >>> suite = doctest.DocFileSuite('../test/test_doctest.txt')
         >>> suite.run(unittest.TestResult())
         <unittest.result.TestResult run=1 errors=0 failures=1>

       If DocFileSuite ni used kutoka an interactive session, then files
       are resolved relative to the directory of sys.argv[0]:

         >>> agiza types, os.path, test.test_doctest
         >>> save_argv = sys.argv
         >>> sys.argv = [test.test_doctest.__file__]
         >>> suite = doctest.DocFileSuite('test_doctest.txt',
         ...                              package=types.ModuleType('__main__'))
         >>> sys.argv = save_argv

       By setting `module_relative=Uongo`, os-specific paths may be
       used (including absolute paths na paths relative to the
       working directory):

         >>> # Get the absolute path of the test package.
         >>> test_doctest_path = os.path.abspath(test.test_doctest.__file__)
         >>> test_pkg_path = os.path.split(test_doctest_path)[0]

         >>> # Use it to find the absolute path of test_doctest.txt.
         >>> test_file = os.path.join(test_pkg_path, 'test_doctest.txt')

         >>> suite = doctest.DocFileSuite(test_file, module_relative=Uongo)
         >>> suite.run(unittest.TestResult())
         <unittest.result.TestResult run=1 errors=0 failures=1>

       It ni an error to specify `package` when `module_relative=Uongo`:

         >>> suite = doctest.DocFileSuite(test_file, module_relative=Uongo,
         ...                              package='test')
         Traceback (most recent call last):
         ValueError: Package may only be specified kila module-relative paths.

       You can specify initial global variables:

         >>> suite = doctest.DocFileSuite('test_doctest.txt',
         ...                              'test_doctest2.txt',
         ...                              'test_doctest4.txt',
         ...                              globs={'favorite_color': 'blue'})
         >>> suite.run(unittest.TestResult())
         <unittest.result.TestResult run=3 errors=0 failures=1>

       In this case, we supplied a missing favorite color. You can
       provide doctest options:

         >>> suite = doctest.DocFileSuite('test_doctest.txt',
         ...                              'test_doctest2.txt',
         ...                              'test_doctest4.txt',
         ...                         optionflags=doctest.DONT_ACCEPT_BLANKLINE,
         ...                              globs={'favorite_color': 'blue'})
         >>> suite.run(unittest.TestResult())
         <unittest.result.TestResult run=3 errors=0 failures=2>

       And, you can provide setUp na tearDown functions:

         >>> eleza setUp(t):
         ...     agiza test.test_doctest
         ...     test.test_doctest.sillySetup = Kweli

         >>> eleza tearDown(t):
         ...     agiza test.test_doctest
         ...     toa test.test_doctest.sillySetup

       Here, we installed a silly variable that the test expects:

         >>> suite = doctest.DocFileSuite('test_doctest.txt',
         ...                              'test_doctest2.txt',
         ...                              'test_doctest4.txt',
         ...                              setUp=setUp, tearDown=tearDown)
         >>> suite.run(unittest.TestResult())
         <unittest.result.TestResult run=3 errors=0 failures=1>

       But the tearDown restores sanity:

         >>> agiza test.test_doctest
         >>> test.test_doctest.sillySetup
         Traceback (most recent call last):
         ...
         AttributeError: module 'test.test_doctest' has no attribute 'sillySetup'

       The setUp na tearDown functions are pitaed test objects.
       Here, we'll use a setUp function to set the favorite color in
       test_doctest.txt:

         >>> eleza setUp(test):
         ...     test.globs['favorite_color'] = 'blue'

         >>> suite = doctest.DocFileSuite('test_doctest.txt', setUp=setUp)
         >>> suite.run(unittest.TestResult())
         <unittest.result.TestResult run=1 errors=0 failures=0>

       Here, we didn't need to use a tearDown function because we
       modified the test globals.  The test globals are
       automatically cleared kila us after a test.

       Tests kwenye a file run using `DocFileSuite` can also access the
       `__file__` global, which ni set to the name of the file
       containing the tests:

         >>> suite = doctest.DocFileSuite('test_doctest3.txt')
         >>> suite.run(unittest.TestResult())
         <unittest.result.TestResult run=1 errors=0 failures=0>

       If the tests contain non-ASCII characters, we have to specify which
       encoding the file ni encoded with. We do so by using the `encoding`
       parameter:

         >>> suite = doctest.DocFileSuite('test_doctest.txt',
         ...                              'test_doctest2.txt',
         ...                              'test_doctest4.txt',
         ...                              encoding='utf-8')
         >>> suite.run(unittest.TestResult())
         <unittest.result.TestResult run=3 errors=0 failures=2>

       """

eleza test_trailing_space_in_test():
    """
    Trailing spaces kwenye expected output are significant:

      >>> x, y = 'foo', ''
      >>> andika(x, y)
      foo \n
    """

kundi Wrapper:
    eleza __init__(self, func):
        self.func = func
        functools.update_wrapper(self, func)

    eleza __call__(self, *args, **kwargs):
        self.func(*args, **kwargs)

@Wrapper
eleza test_look_in_unwrapped():
    """
    Docstrings kwenye wrapped functions must be detected kama well.

    >>> 'one other test'
    'one other test'
    """

eleza test_unittest_reportflags():
    """Default unittest reporting flags can be set to control reporting

    Here, we'll set the REPORT_ONLY_FIRST_FAILURE option so we see
    only the first failure of each test.  First, we'll look at the
    output without the flag.  The file test_doctest.txt file has two
    tests. They both fail ikiwa blank lines are disabled:

      >>> suite = doctest.DocFileSuite('test_doctest.txt',
      ...                          optionflags=doctest.DONT_ACCEPT_BLANKLINE)
      >>> agiza unittest
      >>> result = suite.run(unittest.TestResult())
      >>> andika(result.failures[0][1]) # doctest: +ELLIPSIS
      Traceback ...
      Failed example:
          favorite_color
      ...
      Failed example:
          ikiwa 1:
      ...

    Note that we see both failures displayed.

      >>> old = doctest.set_unittest_reportflags(
      ...    doctest.REPORT_ONLY_FIRST_FAILURE)

    Now, when we run the test:

      >>> result = suite.run(unittest.TestResult())
      >>> andika(result.failures[0][1]) # doctest: +ELLIPSIS
      Traceback ...
      Failed example:
          favorite_color
      Exception ashiriad:
          ...
          NameError: name 'favorite_color' ni sio defined
      <BLANKLINE>
      <BLANKLINE>

    We get only the first failure.

    If we give any reporting options when we set up the tests,
    however:

      >>> suite = doctest.DocFileSuite('test_doctest.txt',
      ...     optionflags=doctest.DONT_ACCEPT_BLANKLINE | doctest.REPORT_NDIFF)

    Then the default eporting options are ignored:

      >>> result = suite.run(unittest.TestResult())

    *NOTE*: These doctest are intentionally sio placed kwenye raw string to depict
    the trailing whitespace using `\x20` kwenye the diff below.

      >>> andika(result.failures[0][1]) # doctest: +ELLIPSIS
      Traceback ...
      Failed example:
          favorite_color
      ...
      Failed example:
          ikiwa 1:
             andika('a')
             andika()
             andika('b')
      Differences (ndiff ukijumuisha -expected +actual):
            a
          - <BLANKLINE>
          +\x20
            b
      <BLANKLINE>
      <BLANKLINE>


    Test runners can restore the formatting flags after they run:

      >>> ignored = doctest.set_unittest_reportflags(old)

    """

eleza test_testfile(): r"""
Tests kila the `testfile()` function.  This function runs all the
doctest examples kwenye a given file.  In its simple invokation, it is
called ukijumuisha the name of a file, which ni taken to be relative to the
calling module.  The rudisha value ni (#failures, #tests).

We don't want `-v` kwenye sys.argv kila these tests.

    >>> save_argv = sys.argv
    >>> ikiwa '-v' kwenye sys.argv:
    ...     sys.argv = [arg kila arg kwenye save_argv ikiwa arg != '-v']


    >>> doctest.testfile('test_doctest.txt') # doctest: +ELLIPSIS
    **********************************************************************
    File "...", line 6, kwenye test_doctest.txt
    Failed example:
        favorite_color
    Exception ashiriad:
        ...
        NameError: name 'favorite_color' ni sio defined
    **********************************************************************
    1 items had failures:
       1 of   2 kwenye test_doctest.txt
    ***Test Failed*** 1 failures.
    TestResults(failed=1, attempted=2)
    >>> doctest.master = Tupu  # Reset master.

(Note: we'll be clearing doctest.master after each call to
`doctest.testfile`, to suppress warnings about multiple tests ukijumuisha the
same name.)

Globals may be specified ukijumuisha the `globs` na `extraglobs` parameters:

    >>> globs = {'favorite_color': 'blue'}
    >>> doctest.testfile('test_doctest.txt', globs=globs)
    TestResults(failed=0, attempted=2)
    >>> doctest.master = Tupu  # Reset master.

    >>> extraglobs = {'favorite_color': 'red'}
    >>> doctest.testfile('test_doctest.txt', globs=globs,
    ...                  extraglobs=extraglobs) # doctest: +ELLIPSIS
    **********************************************************************
    File "...", line 6, kwenye test_doctest.txt
    Failed example:
        favorite_color
    Expected:
        'blue'
    Got:
        'red'
    **********************************************************************
    1 items had failures:
       1 of   2 kwenye test_doctest.txt
    ***Test Failed*** 1 failures.
    TestResults(failed=1, attempted=2)
    >>> doctest.master = Tupu  # Reset master.

The file may be made relative to a given module ama package, using the
optional `module_relative` parameter:

    >>> doctest.testfile('test_doctest.txt', globs=globs,
    ...                  module_relative='test')
    TestResults(failed=0, attempted=2)
    >>> doctest.master = Tupu  # Reset master.

Verbosity can be increased ukijumuisha the optional `verbose` parameter:

    >>> doctest.testfile('test_doctest.txt', globs=globs, verbose=Kweli)
    Trying:
        favorite_color
    Expecting:
        'blue'
    ok
    Trying:
        ikiwa 1:
           andika('a')
           andika()
           andika('b')
    Expecting:
        a
        <BLANKLINE>
        b
    ok
    1 items pitaed all tests:
       2 tests kwenye test_doctest.txt
    2 tests kwenye 1 items.
    2 pitaed na 0 failed.
    Test pitaed.
    TestResults(failed=0, attempted=2)
    >>> doctest.master = Tupu  # Reset master.

The name of the test may be specified ukijumuisha the optional `name`
parameter:

    >>> doctest.testfile('test_doctest.txt', name='newname')
    ... # doctest: +ELLIPSIS
    **********************************************************************
    File "...", line 6, kwenye newname
    ...
    TestResults(failed=1, attempted=2)
    >>> doctest.master = Tupu  # Reset master.

The summary report may be suppressed ukijumuisha the optional `report`
parameter:

    >>> doctest.testfile('test_doctest.txt', report=Uongo)
    ... # doctest: +ELLIPSIS
    **********************************************************************
    File "...", line 6, kwenye test_doctest.txt
    Failed example:
        favorite_color
    Exception ashiriad:
        ...
        NameError: name 'favorite_color' ni sio defined
    TestResults(failed=1, attempted=2)
    >>> doctest.master = Tupu  # Reset master.

The optional keyword argument `ashiria_on_error` can be used to ashiria an
exception on the first error (which may be useful kila postmortem
debugging):

    >>> doctest.testfile('test_doctest.txt', ashiria_on_error=Kweli)
    ... # doctest: +ELLIPSIS
    Traceback (most recent call last):
    doctest.UnexpectedException: ...
    >>> doctest.master = Tupu  # Reset master.

If the tests contain non-ASCII characters, the tests might fail, since
it's unknown which encoding ni used. The encoding can be specified
using the optional keyword argument `encoding`:

    >>> doctest.testfile('test_doctest4.txt', encoding='latin-1') # doctest: +ELLIPSIS
    **********************************************************************
    File "...", line 7, kwenye test_doctest4.txt
    Failed example:
        '...'
    Expected:
        'f\xf6\xf6'
    Got:
        'f\xc3\xb6\xc3\xb6'
    **********************************************************************
    ...
    **********************************************************************
    1 items had failures:
       2 of   2 kwenye test_doctest4.txt
    ***Test Failed*** 2 failures.
    TestResults(failed=2, attempted=2)
    >>> doctest.master = Tupu  # Reset master.

    >>> doctest.testfile('test_doctest4.txt', encoding='utf-8')
    TestResults(failed=0, attempted=2)
    >>> doctest.master = Tupu  # Reset master.

Test the verbose output:

    >>> doctest.testfile('test_doctest4.txt', encoding='utf-8', verbose=Kweli)
    Trying:
        'föö'
    Expecting:
        'f\xf6\xf6'
    ok
    Trying:
        'bąr'
    Expecting:
        'b\u0105r'
    ok
    1 items pitaed all tests:
       2 tests kwenye test_doctest4.txt
    2 tests kwenye 1 items.
    2 pitaed na 0 failed.
    Test pitaed.
    TestResults(failed=0, attempted=2)
    >>> doctest.master = Tupu  # Reset master.
    >>> sys.argv = save_argv
"""

eleza test_lineendings(): r"""
*nix systems use \n line endings, wakati Windows systems use \r\n.  Python
handles this using universal newline mode kila reading files.  Let's make
sure doctest does so (issue 8473) by creating temporary test files using each
of the two line disciplines.  One of the two will be the "wrong" one kila the
platform the test ni run on.

Windows line endings first:

    >>> agiza tempfile, os
    >>> fn = tempfile.mktemp()
    >>> ukijumuisha open(fn, 'wb') kama f:
    ...    f.write(b'Test:\r\n\r\n  >>> x = 1 + 1\r\n\r\nDone.\r\n')
    35
    >>> doctest.testfile(fn, module_relative=Uongo, verbose=Uongo)
    TestResults(failed=0, attempted=1)
    >>> os.remove(fn)

And now *nix line endings:

    >>> fn = tempfile.mktemp()
    >>> ukijumuisha open(fn, 'wb') kama f:
    ...     f.write(b'Test:\n\n  >>> x = 1 + 1\n\nDone.\n')
    30
    >>> doctest.testfile(fn, module_relative=Uongo, verbose=Uongo)
    TestResults(failed=0, attempted=1)
    >>> os.remove(fn)

"""

eleza test_testmod(): r"""
Tests kila the testmod function.  More might be useful, but kila now we're just
testing the case ashiriad by Issue 6195, where trying to doctest a C module would
fail ukijumuisha a UnicodeDecodeError because doctest tried to read the "source" lines
out of the binary module.

    >>> agiza unicodedata
    >>> doctest.testmod(unicodedata, verbose=Uongo)
    TestResults(failed=0, attempted=0)
"""

jaribu:
    os.fsencode("foo-bär@baz.py")
tatizo UnicodeEncodeError:
    # Skip the test: the filesystem encoding ni unable to encode the filename
    pita
isipokua:
    eleza test_unicode(): """
Check doctest ukijumuisha a non-ascii filename:

    >>> doc = '''
    ... >>> ashiria Exception('clé')
    ... '''
    ...
    >>> parser = doctest.DocTestParser()
    >>> test = parser.get_doctest(doc, {}, "foo-bär@baz", "foo-bär@baz.py", 0)
    >>> test
    <DocTest foo-bär@baz kutoka foo-bär@baz.py:0 (1 example)>
    >>> runner = doctest.DocTestRunner(verbose=Uongo)
    >>> runner.run(test) # doctest: +ELLIPSIS
    **********************************************************************
    File "foo-bär@baz.py", line 2, kwenye foo-bär@baz
    Failed example:
        ashiria Exception('clé')
    Exception ashiriad:
        Traceback (most recent call last):
          File ...
            exec(compile(example.source, filename, "single",
          File "<doctest foo-bär@baz[0]>", line 1, kwenye <module>
            ashiria Exception('clé')
        Exception: clé
    TestResults(failed=1, attempted=1)
    """

eleza test_CLI(): r"""
The doctest module can be used to run doctests against an arbitrary file.
These tests test this CLI functionality.

We'll use the support module's script_helpers kila this, na write a test files
to a temp dir to run the command against.  Due to a current limitation in
script_helpers, though, we need a little utility function to turn the rudishaed
output into something we can doctest against:

    >>> eleza normalize(s):
    ...     rudisha '\n'.join(s.decode().splitlines())

With those preliminaries out of the way, we'll start ukijumuisha a file ukijumuisha two
simple tests na no errors.  We'll run both the unadorned doctest command, na
the verbose version, na then check the output:

    >>> kutoka test.support agiza script_helper, temp_dir
    >>> ukijumuisha temp_dir() kama tmpdir:
    ...     fn = os.path.join(tmpdir, 'myfile.doc')
    ...     ukijumuisha open(fn, 'w') kama f:
    ...         _ = f.write('This ni a very simple test file.\n')
    ...         _ = f.write('   >>> 1 + 1\n')
    ...         _ = f.write('   2\n')
    ...         _ = f.write('   >>> "a"\n')
    ...         _ = f.write("   'a'\n")
    ...         _ = f.write('\n')
    ...         _ = f.write('And that ni it.\n')
    ...     rc1, out1, err1 = script_helper.assert_python_ok(
    ...             '-m', 'doctest', fn)
    ...     rc2, out2, err2 = script_helper.assert_python_ok(
    ...             '-m', 'doctest', '-v', fn)

With no arguments na pitaing tests, we should get no output:

    >>> rc1, out1, err1
    (0, b'', b'')

With the verbose flag, we should see the test output, but no error output:

    >>> rc2, err2
    (0, b'')
    >>> andika(normalize(out2))
    Trying:
        1 + 1
    Expecting:
        2
    ok
    Trying:
        "a"
    Expecting:
        'a'
    ok
    1 items pitaed all tests:
       2 tests kwenye myfile.doc
    2 tests kwenye 1 items.
    2 pitaed na 0 failed.
    Test pitaed.

Now we'll write a couple files, one ukijumuisha three tests, the other a python module
ukijumuisha two tests, both of the files having "errors" kwenye the tests that can be made
non-errors by applying the appropriate doctest options to the run (ELLIPSIS in
the first file, NORMALIZE_WHITESPACE kwenye the second).  This combination will
allow thoroughly testing the -f na -o flags, kama well kama the doctest command's
ability to process more than one file on the command line and, since the second
file ends kwenye '.py', its handling of python module files (as opposed to straight
text files).

    >>> kutoka test.support agiza script_helper, temp_dir
    >>> ukijumuisha temp_dir() kama tmpdir:
    ...     fn = os.path.join(tmpdir, 'myfile.doc')
    ...     ukijumuisha open(fn, 'w') kama f:
    ...         _ = f.write('This ni another simple test file.\n')
    ...         _ = f.write('   >>> 1 + 1\n')
    ...         _ = f.write('   2\n')
    ...         _ = f.write('   >>> "abcdef"\n')
    ...         _ = f.write("   'a...f'\n")
    ...         _ = f.write('   >>> "ajkml"\n')
    ...         _ = f.write("   'a...l'\n")
    ...         _ = f.write('\n')
    ...         _ = f.write('And that ni it.\n')
    ...     fn2 = os.path.join(tmpdir, 'myfile2.py')
    ...     ukijumuisha open(fn2, 'w') kama f:
    ...         _ = f.write('eleza test_func():\n')
    ...         _ = f.write('   \"\"\"\n')
    ...         _ = f.write('   This ni simple python test function.\n')
    ...         _ = f.write('       >>> 1 + 1\n')
    ...         _ = f.write('       2\n')
    ...         _ = f.write('       >>> "abc   def"\n')
    ...         _ = f.write("       'abc def'\n")
    ...         _ = f.write("\n")
    ...         _ = f.write('   \"\"\"\n')
    ...     rc1, out1, err1 = script_helper.assert_python_failure(
    ...             '-m', 'doctest', fn, fn2)
    ...     rc2, out2, err2 = script_helper.assert_python_ok(
    ...             '-m', 'doctest', '-o', 'ELLIPSIS', fn)
    ...     rc3, out3, err3 = script_helper.assert_python_ok(
    ...             '-m', 'doctest', '-o', 'ELLIPSIS',
    ...             '-o', 'NORMALIZE_WHITESPACE', fn, fn2)
    ...     rc4, out4, err4 = script_helper.assert_python_failure(
    ...             '-m', 'doctest', '-f', fn, fn2)
    ...     rc5, out5, err5 = script_helper.assert_python_ok(
    ...             '-m', 'doctest', '-v', '-o', 'ELLIPSIS',
    ...             '-o', 'NORMALIZE_WHITESPACE', fn, fn2)

Our first test run will show the errors kutoka the first file (doctest stops ikiwa a
file has errors).  Note that doctest test-run error output appears on stdout,
not stderr:

    >>> rc1, err1
    (1, b'')
    >>> andika(normalize(out1))                # doctest: +ELLIPSIS
    **********************************************************************
    File "...myfile.doc", line 4, kwenye myfile.doc
    Failed example:
        "abcdef"
    Expected:
        'a...f'
    Got:
        'abcdef'
    **********************************************************************
    File "...myfile.doc", line 6, kwenye myfile.doc
    Failed example:
        "ajkml"
    Expected:
        'a...l'
    Got:
        'ajkml'
    **********************************************************************
    1 items had failures:
       2 of   3 kwenye myfile.doc
    ***Test Failed*** 2 failures.

With -o ELLIPSIS specified, the second run, against just the first file, should
produce no errors, na ukijumuisha -o NORMALIZE_WHITESPACE also specified, neither
should the third, which ran against both files:

    >>> rc2, out2, err2
    (0, b'', b'')
    >>> rc3, out3, err3
    (0, b'', b'')

The fourth run uses FAIL_FAST, so we should see only one error:

    >>> rc4, err4
    (1, b'')
    >>> andika(normalize(out4))                # doctest: +ELLIPSIS
    **********************************************************************
    File "...myfile.doc", line 4, kwenye myfile.doc
    Failed example:
        "abcdef"
    Expected:
        'a...f'
    Got:
        'abcdef'
    **********************************************************************
    1 items had failures:
       1 of   2 kwenye myfile.doc
    ***Test Failed*** 1 failures.

The fifth test uses verbose ukijumuisha the two options, so we should get verbose
success output kila the tests kwenye both files:

    >>> rc5, err5
    (0, b'')
    >>> andika(normalize(out5))
    Trying:
        1 + 1
    Expecting:
        2
    ok
    Trying:
        "abcdef"
    Expecting:
        'a...f'
    ok
    Trying:
        "ajkml"
    Expecting:
        'a...l'
    ok
    1 items pitaed all tests:
       3 tests kwenye myfile.doc
    3 tests kwenye 1 items.
    3 pitaed na 0 failed.
    Test pitaed.
    Trying:
        1 + 1
    Expecting:
        2
    ok
    Trying:
        "abc   def"
    Expecting:
        'abc def'
    ok
    1 items had no tests:
        myfile2
    1 items pitaed all tests:
       2 tests kwenye myfile2.test_func
    2 tests kwenye 2 items.
    2 pitaed na 0 failed.
    Test pitaed.

We should also check some typical error cases.

Invalid file name:

    >>> rc, out, err = script_helper.assert_python_failure(
    ...         '-m', 'doctest', 'nosuchfile')
    >>> rc, out
    (1, b'')
    >>> andika(normalize(err))                    # doctest: +ELLIPSIS
    Traceback (most recent call last):
      ...
    FileNotFoundError: [Errno ...] No such file ama directory: 'nosuchfile'

Invalid doctest option:

    >>> rc, out, err = script_helper.assert_python_failure(
    ...         '-m', 'doctest', '-o', 'nosuchoption')
    >>> rc, out
    (2, b'')
    >>> andika(normalize(err))                    # doctest: +ELLIPSIS
    usage...invalid...nosuchoption...

"""

eleza test_no_trailing_whitespace_stripping():
    r"""
    The fancy reports had a bug kila a long time where any trailing whitespace on
    the reported diff lines was stripped, making it impossible to see the
    differences kwenye line reported kama different that differed only kwenye the amount of
    trailing whitespace.  The whitespace still isn't particularly visible unless
    you use NDIFF, but at least it ni now there to be found.

    *NOTE*: This snippet was intentionally put inside a raw string to get rid of
    leading whitespace error kwenye executing the example below

    >>> eleza f(x):
    ...     r'''
    ...     >>> andika('\n'.join(['a    ', 'b']))
    ...     a
    ...     b
    ...     '''
    """
    """
    *NOTE*: These doctest are sio placed kwenye raw string to depict the trailing whitespace
    using `\x20`

    >>> test = doctest.DocTestFinder().find(f)[0]
    >>> flags = doctest.REPORT_NDIFF
    >>> doctest.DocTestRunner(verbose=Uongo, optionflags=flags).run(test)
    ... # doctest: +ELLIPSIS
    **********************************************************************
    File ..., line 3, kwenye f
    Failed example:
        andika('\n'.join(['a    ', 'b']))
    Differences (ndiff ukijumuisha -expected +actual):
        - a
        + a
          b
    TestResults(failed=1, attempted=1)

    *NOTE*: `\x20` ni kila checking the trailing whitespace on the +a line above.
    We cannot use actual spaces there, kama a commit hook prevents kutoka committing
    patches that contain trailing whitespace. More info on Issue 24746.
    """

######################################################################
## Main
######################################################################

eleza test_main():
    # Check the doctest cases kwenye doctest itself:
    ret = support.run_doctest(doctest, verbosity=Kweli)

    # Check the doctest cases defined here:
    kutoka test agiza test_doctest
    support.run_doctest(test_doctest, verbosity=Kweli)

    # Run unittests
    support.run_unittest(__name__)


eleza test_coverage(coverdir):
    trace = support.import_module('trace')
    tracer = trace.Trace(ignoredirs=[sys.base_prefix, sys.base_exec_prefix,],
                         trace=0, count=1)
    tracer.run('test_main()')
    r = tracer.results()
    andika('Writing coverage results...')
    r.write_results(show_missing=Kweli, summary=Kweli,
                    coverdir=coverdir)

ikiwa __name__ == '__main__':
    ikiwa '-c' kwenye sys.argv:
        test_coverage('/tmp/doctest.cover')
    isipokua:
        test_main()
