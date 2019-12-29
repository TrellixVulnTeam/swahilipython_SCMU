agiza os
agiza sys
agiza contextlib
agiza importlib.util
agiza inspect
agiza pydoc
agiza py_compile
agiza keyword
agiza _pickle
agiza pkgutil
agiza re
agiza stat
agiza string
agiza tempfile
agiza test.support
agiza time
agiza types
agiza typing
agiza unittest
agiza urllib.parse
agiza xml.etree
agiza xml.etree.ElementTree
agiza textwrap
kutoka io agiza StringIO
kutoka collections agiza namedtuple
kutoka test.support.script_helper agiza assert_python_ok
kutoka test.support agiza (
    TESTFN, rmtree,
    reap_children, reap_threads, captured_output, captured_stdout,
    captured_stderr, unlink, requires_docstrings
)
kutoka test agiza pydoc_mod


kundi nonascii:
    'Це не латиниця'
    pita

ikiwa test.support.HAVE_DOCSTRINGS:
    expected_data_docstrings = (
        'dictionary kila instance variables (ikiwa defined)',
        'list of weak references to the object (ikiwa defined)',
        ) * 2
isipokua:
    expected_data_docstrings = ('', '', '', '')

expected_text_pattern = """
NAME
    test.pydoc_mod - This ni a test module kila test_pydoc
%s
CLASSES
    builtins.object
        A
        B
        C
\x20\x20\x20\x20
    kundi A(builtins.object)
     |  Hello na goodbye
     |\x20\x20
     |  Methods defined here:
     |\x20\x20
     |  __init__()
     |      Wow, I have no function!
     |\x20\x20
     |  ----------------------------------------------------------------------
     |  Data descriptors defined here:
     |\x20\x20
     |  __dict__%s
     |\x20\x20
     |  __weakref__%s
\x20\x20\x20\x20
    kundi B(builtins.object)
     |  Data descriptors defined here:
     |\x20\x20
     |  __dict__%s
     |\x20\x20
     |  __weakref__%s
     |\x20\x20
     |  ----------------------------------------------------------------------
     |  Data na other attributes defined here:
     |\x20\x20
     |  NO_MEANING = 'eggs'
     |\x20\x20
     |  __annotations__ = {'NO_MEANING': <kundi 'str'>}
\x20\x20\x20\x20
    kundi C(builtins.object)
     |  Methods defined here:
     |\x20\x20
     |  get_answer(self)
     |      Return say_no()
     |\x20\x20
     |  is_it_true(self)
     |      Return self.get_answer()
     |\x20\x20
     |  say_no(self)
     |\x20\x20
     |  ----------------------------------------------------------------------
     |  Data descriptors defined here:
     |\x20\x20
     |  __dict__
     |      dictionary kila instance variables (ikiwa defined)
     |\x20\x20
     |  __weakref__
     |      list of weak references to the object (ikiwa defined)

FUNCTIONS
    doc_func()
        This function solves all of the world's problems:
        hunger
        lack of Python
        war
\x20\x20\x20\x20
    nodoc_func()

DATA
    __xyz__ = 'X, Y na Z'

VERSION
    1.2.3.4

AUTHOR
    Benjamin Peterson

CREDITS
    Nobody

FILE
    %s
""".strip()

expected_text_data_docstrings = tuple('\n     |      ' + s ikiwa s isipokua ''
                                      kila s kwenye expected_data_docstrings)

expected_html_pattern = """
<table width="100%%" cellspacing=0 cellpadding=2 border=0 summary="heading">
<tr bgcolor="#7799ee">
<td valign=bottom>&nbsp;<br>
<font color="#ffffff" face="helvetica, arial">&nbsp;<br><big><big><strong><a href="test.html"><font color="#ffffff">test</font></a>.pydoc_mod</strong></big></big> (version 1.2.3.4)</font></td
><td align=right valign=bottom
><font color="#ffffff" face="helvetica, arial"><a href=".">index</a><br><a href="file:%s">%s</a>%s</font></td></tr></table>
    <p><tt>This&nbsp;is&nbsp;a&nbsp;test&nbsp;module&nbsp;for&nbsp;test_pydoc</tt></p>
<p>
<table width="100%%" cellspacing=0 cellpadding=2 border=0 summary="section">
<tr bgcolor="#ee77aa">
<td colspan=3 valign=bottom>&nbsp;<br>
<font color="#ffffff" face="helvetica, arial"><big><strong>Classes</strong></big></font></td></tr>
\x20\x20\x20\x20
<tr><td bgcolor="#ee77aa"><tt>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</tt></td><td>&nbsp;</td>
<td width="100%%"><dl>
<dt><font face="helvetica, arial"><a href="builtins.html#object">builtins.object</a>
</font></dt><dd>
<dl>
<dt><font face="helvetica, arial"><a href="test.pydoc_mod.html#A">A</a>
</font></dt><dt><font face="helvetica, arial"><a href="test.pydoc_mod.html#B">B</a>
</font></dt><dt><font face="helvetica, arial"><a href="test.pydoc_mod.html#C">C</a>
</font></dt></dl>
</dd>
</dl>
 <p>
<table width="100%%" cellspacing=0 cellpadding=2 border=0 summary="section">
<tr bgcolor="#ffc8d8">
<td colspan=3 valign=bottom>&nbsp;<br>
<font color="#000000" face="helvetica, arial"><a name="A">kundi <strong>A</strong></a>(<a href="builtins.html#object">builtins.object</a>)</font></td></tr>
\x20\x20\x20\x20
<tr bgcolor="#ffc8d8"><td rowspan=2><tt>&nbsp;&nbsp;&nbsp;</tt></td>
<td colspan=2><tt>Hello&nbsp;and&nbsp;goodbye<br>&nbsp;</tt></td></tr>
<tr><td>&nbsp;</td>
<td width="100%%">Methods defined here:<br>
<dl><dt><a name="A-__init__"><strong>__init__</strong></a>()</dt><dd><tt>Wow,&nbsp;I&nbsp;have&nbsp;no&nbsp;function!</tt></dd></dl>

<hr>
Data descriptors defined here:<br>
<dl><dt><strong>__dict__</strong></dt>
<dd><tt>%s</tt></dd>
</dl>
<dl><dt><strong>__weakref__</strong></dt>
<dd><tt>%s</tt></dd>
</dl>
</td></tr></table> <p>
<table width="100%%" cellspacing=0 cellpadding=2 border=0 summary="section">
<tr bgcolor="#ffc8d8">
<td colspan=3 valign=bottom>&nbsp;<br>
<font color="#000000" face="helvetica, arial"><a name="B">kundi <strong>B</strong></a>(<a href="builtins.html#object">builtins.object</a>)</font></td></tr>
\x20\x20\x20\x20
<tr><td bgcolor="#ffc8d8"><tt>&nbsp;&nbsp;&nbsp;</tt></td><td>&nbsp;</td>
<td width="100%%">Data descriptors defined here:<br>
<dl><dt><strong>__dict__</strong></dt>
<dd><tt>%s</tt></dd>
</dl>
<dl><dt><strong>__weakref__</strong></dt>
<dd><tt>%s</tt></dd>
</dl>
<hr>
Data na other attributes defined here:<br>
<dl><dt><strong>NO_MEANING</strong> = 'eggs'</dl>

<dl><dt><strong>__annotations__</strong> = {'NO_MEANING': &lt;kundi 'str'&gt;}</dl>

</td></tr></table> <p>
<table width="100%%" cellspacing=0 cellpadding=2 border=0 summary="section">
<tr bgcolor="#ffc8d8">
<td colspan=3 valign=bottom>&nbsp;<br>
<font color="#000000" face="helvetica, arial"><a name="C">kundi <strong>C</strong></a>(<a href="builtins.html#object">builtins.object</a>)</font></td></tr>
\x20\x20\x20\x20
<tr><td bgcolor="#ffc8d8"><tt>&nbsp;&nbsp;&nbsp;</tt></td><td>&nbsp;</td>
<td width="100%%">Methods defined here:<br>
<dl><dt><a name="C-get_answer"><strong>get_answer</strong></a>(self)</dt><dd><tt>Return&nbsp;<a href="#C-say_no">say_no</a>()</tt></dd></dl>

<dl><dt><a name="C-is_it_true"><strong>is_it_true</strong></a>(self)</dt><dd><tt>Return&nbsp;self.<a href="#C-get_answer">get_answer</a>()</tt></dd></dl>

<dl><dt><a name="C-say_no"><strong>say_no</strong></a>(self)</dt></dl>

<hr>
Data descriptors defined here:<br>
<dl><dt><strong>__dict__</strong></dt>
<dd><tt>dictionary&nbsp;for&nbsp;instance&nbsp;variables&nbsp;(if&nbsp;defined)</tt></dd>
</dl>
<dl><dt><strong>__weakref__</strong></dt>
<dd><tt>list&nbsp;of&nbsp;weak&nbsp;references&nbsp;to&nbsp;the&nbsp;object&nbsp;(if&nbsp;defined)</tt></dd>
</dl>
</td></tr></table></td></tr></table><p>
<table width="100%%" cellspacing=0 cellpadding=2 border=0 summary="section">
<tr bgcolor="#eeaa77">
<td colspan=3 valign=bottom>&nbsp;<br>
<font color="#ffffff" face="helvetica, arial"><big><strong>Functions</strong></big></font></td></tr>
\x20\x20\x20\x20
<tr><td bgcolor="#eeaa77"><tt>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</tt></td><td>&nbsp;</td>
<td width="100%%"><dl><dt><a name="-doc_func"><strong>doc_func</strong></a>()</dt><dd><tt>This&nbsp;function&nbsp;solves&nbsp;all&nbsp;of&nbsp;the&nbsp;world's&nbsp;problems:<br>
hunger<br>
lack&nbsp;of&nbsp;Python<br>
war</tt></dd></dl>
 <dl><dt><a name="-nodoc_func"><strong>nodoc_func</strong></a>()</dt></dl>
</td></tr></table><p>
<table width="100%%" cellspacing=0 cellpadding=2 border=0 summary="section">
<tr bgcolor="#55aa55">
<td colspan=3 valign=bottom>&nbsp;<br>
<font color="#ffffff" face="helvetica, arial"><big><strong>Data</strong></big></font></td></tr>
\x20\x20\x20\x20
<tr><td bgcolor="#55aa55"><tt>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</tt></td><td>&nbsp;</td>
<td width="100%%"><strong>__xyz__</strong> = 'X, Y na Z'</td></tr></table><p>
<table width="100%%" cellspacing=0 cellpadding=2 border=0 summary="section">
<tr bgcolor="#7799ee">
<td colspan=3 valign=bottom>&nbsp;<br>
<font color="#ffffff" face="helvetica, arial"><big><strong>Author</strong></big></font></td></tr>
\x20\x20\x20\x20
<tr><td bgcolor="#7799ee"><tt>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</tt></td><td>&nbsp;</td>
<td width="100%%">Benjamin&nbsp;Peterson</td></tr></table><p>
<table width="100%%" cellspacing=0 cellpadding=2 border=0 summary="section">
<tr bgcolor="#7799ee">
<td colspan=3 valign=bottom>&nbsp;<br>
<font color="#ffffff" face="helvetica, arial"><big><strong>Credits</strong></big></font></td></tr>
\x20\x20\x20\x20
<tr><td bgcolor="#7799ee"><tt>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</tt></td><td>&nbsp;</td>
<td width="100%%">Nobody</td></tr></table>
""".strip() # ' <- emacs turd

expected_html_data_docstrings = tuple(s.replace(' ', '&nbsp;')
                                      kila s kwenye expected_data_docstrings)

# output pattern kila missing module
missing_pattern = '''\
No Python documentation found kila %r.
Use help() to get the interactive help utility.
Use help(str) kila help on the str class.'''.replace('\n', os.linesep)

# output pattern kila module ukijumuisha bad agizas
badimport_pattern = "problem kwenye %s - ModuleNotFoundError: No module named %r"

expected_dynamicattribute_pattern = """
Help on kundi DA kwenye module %s:

kundi DA(builtins.object)
 |  Data descriptors defined here:
 |\x20\x20
 |  __dict__%s
 |\x20\x20
 |  __weakref__%s
 |\x20\x20
 |  ham
 |\x20\x20
 |  ----------------------------------------------------------------------
 |  Data na other attributes inherited kutoka Meta:
 |\x20\x20
 |  ham = 'spam'
""".strip()

expected_virtualattribute_pattern1 = """
Help on kundi Class kwenye module %s:

kundi Class(builtins.object)
 |  Data na other attributes inherited kutoka Meta:
 |\x20\x20
 |  LIFE = 42
""".strip()

expected_virtualattribute_pattern2 = """
Help on kundi Class1 kwenye module %s:

kundi Class1(builtins.object)
 |  Data na other attributes inherited kutoka Meta1:
 |\x20\x20
 |  one = 1
""".strip()

expected_virtualattribute_pattern3 = """
Help on kundi Class2 kwenye module %s:

kundi Class2(Class1)
 |  Method resolution order:
 |      Class2
 |      Class1
 |      builtins.object
 |\x20\x20
 |  Data na other attributes inherited kutoka Meta1:
 |\x20\x20
 |  one = 1
 |\x20\x20
 |  ----------------------------------------------------------------------
 |  Data na other attributes inherited kutoka Meta3:
 |\x20\x20
 |  three = 3
 |\x20\x20
 |  ----------------------------------------------------------------------
 |  Data na other attributes inherited kutoka Meta2:
 |\x20\x20
 |  two = 2
""".strip()

expected_missingattribute_pattern = """
Help on kundi C kwenye module %s:

kundi C(builtins.object)
 |  Data na other attributes defined here:
 |\x20\x20
 |  here = 'present!'
""".strip()

eleza run_pydoc(module_name, *args, **env):
    """
    Runs pydoc on the specified module. Returns the stripped
    output of pydoc.
    """
    args = args + (module_name,)
    # do sio write bytecode files to avoid caching errors
    rc, out, err = assert_python_ok('-B', pydoc.__file__, *args, **env)
    rudisha out.strip()

eleza get_pydoc_html(module):
    "Returns pydoc generated output kama html"
    doc = pydoc.HTMLDoc()
    output = doc.docmodule(module)
    loc = doc.getdocloc(pydoc_mod) ama ""
    ikiwa loc:
        loc = "<br><a href=\"" + loc + "\">Module Docs</a>"
    rudisha output.strip(), loc

eleza get_pydoc_link(module):
    "Returns a documentation web link of a module"
    abspath = os.path.abspath
    dirname = os.path.dirname
    basedir = dirname(dirname(abspath(__file__)))
    doc = pydoc.TextDoc()
    loc = doc.getdocloc(module, basedir=basedir)
    rudisha loc

eleza get_pydoc_text(module):
    "Returns pydoc generated output kama text"
    doc = pydoc.TextDoc()
    loc = doc.getdocloc(pydoc_mod) ama ""
    ikiwa loc:
        loc = "\nMODULE DOCS\n    " + loc + "\n"

    output = doc.docmodule(module)

    # clean up the extra text formatting that pydoc performs
    patt = re.compile('\b.')
    output = patt.sub('', output)
    rudisha output.strip(), loc

eleza get_html_title(text):
    # Bit of hack, but good enough kila test purposes
    header, _, _ = text.partition("</head>")
    _, _, title = header.partition("<title>")
    title, _, _ = title.partition("</title>")
    rudisha title


kundi PydocBaseTest(unittest.TestCase):

    eleza _restricted_walk_packages(self, walk_packages, path=Tupu):
        """
        A version of pkgutil.walk_packages() that will restrict itself to
        a given path.
        """
        default_path = path ama [os.path.dirname(__file__)]
        eleza wrapper(path=Tupu, prefix='', onerror=Tupu):
            rudisha walk_packages(path ama default_path, prefix, onerror)
        rudisha wrapper

    @contextlib.contextmanager
    eleza restrict_walk_packages(self, path=Tupu):
        walk_packages = pkgutil.walk_packages
        pkgutil.walk_packages = self._restricted_walk_packages(walk_packages,
                                                               path)
        jaribu:
            tuma
        mwishowe:
            pkgutil.walk_packages = walk_packages

    eleza call_url_handler(self, url, expected_title):
        text = pydoc._url_handler(url, "text/html")
        result = get_html_title(text)
        # Check the title to ensure an unexpected error page was sio rudishaed
        self.assertEqual(result, expected_title, text)
        rudisha text


kundi PydocDocTest(unittest.TestCase):
    maxDiff = Tupu

    @unittest.skipIf(sys.flags.optimize >= 2,
                     "Docstrings are omitted ukijumuisha -O2 na above")
    @unittest.skipIf(hasattr(sys, 'gettrace') na sys.gettrace(),
                     'trace function introduces __locals__ unexpectedly')
    @requires_docstrings
    eleza test_html_doc(self):
        result, doc_loc = get_pydoc_html(pydoc_mod)
        mod_file = inspect.getabsfile(pydoc_mod)
        mod_url = urllib.parse.quote(mod_file)
        expected_html = expected_html_pattern % (
                        (mod_url, mod_file, doc_loc) +
                        expected_html_data_docstrings)
        self.assertEqual(result, expected_html)

    @unittest.skipIf(sys.flags.optimize >= 2,
                     "Docstrings are omitted ukijumuisha -O2 na above")
    @unittest.skipIf(hasattr(sys, 'gettrace') na sys.gettrace(),
                     'trace function introduces __locals__ unexpectedly')
    @requires_docstrings
    eleza test_text_doc(self):
        result, doc_loc = get_pydoc_text(pydoc_mod)
        expected_text = expected_text_pattern % (
                        (doc_loc,) +
                        expected_text_data_docstrings +
                        (inspect.getabsfile(pydoc_mod),))
        self.assertEqual(expected_text, result)

    eleza test_text_enum_member_with_value_zero(self):
        # Test issue #20654 to ensure enum member ukijumuisha value 0 can be
        # displayed. It used to throw KeyError: 'zero'.
        agiza enum
        kundi BinaryInteger(enum.IntEnum):
            zero = 0
            one = 1
        doc = pydoc.render_doc(BinaryInteger)
        self.assertIn('<BinaryInteger.zero: 0>', doc)

    eleza test_mixed_case_module_names_are_lower_cased(self):
        # issue16484
        doc_link = get_pydoc_link(xml.etree.ElementTree)
        self.assertIn('xml.etree.elementtree', doc_link)

    eleza test_issue8225(self):
        # Test issue8225 to ensure no doc link appears kila xml.etree
        result, doc_loc = get_pydoc_text(xml.etree)
        self.assertEqual(doc_loc, "", "MODULE DOCS incorrectly includes a link")

    eleza test_getpager_with_stdin_none(self):
        previous_stdin = sys.stdin
        jaribu:
            sys.stdin = Tupu
            pydoc.getpager() # Shouldn't fail.
        mwishowe:
            sys.stdin = previous_stdin

    eleza test_non_str_name(self):
        # issue14638
        # Treat illegal (non-str) name like no name
        kundi A:
            __name__ = 42
        kundi B:
            pita
        adoc = pydoc.render_doc(A())
        bdoc = pydoc.render_doc(B())
        self.assertEqual(adoc.replace("A", "B"), bdoc)

    eleza test_not_here(self):
        missing_module = "test.i_am_not_here"
        result = str(run_pydoc(missing_module), 'ascii')
        expected = missing_pattern % missing_module
        self.assertEqual(expected, result,
            "documentation kila missing module found")

    @unittest.skipIf(sys.flags.optimize >= 2,
                     'Docstrings are omitted ukijumuisha -OO na above')
    eleza test_not_ascii(self):
        result = run_pydoc('test.test_pydoc.nonascii', PYTHONIOENCODING='ascii')
        encoded = nonascii.__doc__.encode('ascii', 'backslashreplace')
        self.assertIn(encoded, result)

    eleza test_input_strip(self):
        missing_module = " test.i_am_not_here "
        result = str(run_pydoc(missing_module), 'ascii')
        expected = missing_pattern % missing_module.strip()
        self.assertEqual(expected, result)

    eleza test_stripid(self):
        # test ukijumuisha strings, other implementations might have different repr()
        stripid = pydoc.stripid
        # strip the id
        self.assertEqual(stripid('<function stripid at 0x88dcee4>'),
                         '<function stripid>')
        self.assertEqual(stripid('<function stripid at 0x01F65390>'),
                         '<function stripid>')
        # nothing to strip, rudisha the same text
        self.assertEqual(stripid('42'), '42')
        self.assertEqual(stripid("<type 'exceptions.Exception'>"),
                         "<type 'exceptions.Exception'>")

    eleza test_builtin_with_more_than_four_children(self):
        """Tests help on builtin object which have more than four child classes.

        When running help() on a builtin kundi which has child classes, it
        should contain a "Built-in subclasses" section na only 4 classes
        should be displayed ukijumuisha a hint on how many more subclasses are present.
        For example:

        >>> help(object)
        Help on kundi object kwenye module builtins:

        kundi object
         |  The most base type
         |
         |  Built-in subclasses:
         |      async_generator
         |      BaseException
         |      builtin_function_or_method
         |      bytearray
         |      ... na 82 other subclasses
        """
        doc = pydoc.TextDoc()
        text = doc.docclass(object)
        snip = (" |  Built-in subclasses:\n"
                " |      async_generator\n"
                " |      BaseException\n"
                " |      builtin_function_or_method\n"
                " |      bytearray\n"
                " |      ... na \\d+ other subclasses")
        self.assertRegex(text, snip)

    eleza test_builtin_with_child(self):
        """Tests help on builtin object which have only child classes.

        When running help() on a builtin kundi which has child classes, it
        should contain a "Built-in subclasses" section. For example:

        >>> help(ArithmeticError)
        Help on kundi ArithmeticError kwenye module builtins:

        kundi ArithmeticError(Exception)
         |  Base kundi kila arithmetic errors.
         |
         ...
         |
         |  Built-in subclasses:
         |      FloatingPointError
         |      OverflowError
         |      ZeroDivisionError
        """
        doc = pydoc.TextDoc()
        text = doc.docclass(ArithmeticError)
        snip = (" |  Built-in subclasses:\n"
                " |      FloatingPointError\n"
                " |      OverflowError\n"
                " |      ZeroDivisionError")
        self.assertIn(snip, text)

    eleza test_builtin_with_grandchild(self):
        """Tests help on builtin classes which have grandchild classes.

        When running help() on a builtin kundi which has child classes, it
        should contain a "Built-in subclasses" section. However, ikiwa it also has
        grandchildren, these should sio show up on the subclasses section.
        For example:

        >>> help(Exception)
        Help on kundi Exception kwenye module builtins:

        kundi Exception(BaseException)
         |  Common base kundi kila all non-exit exceptions.
         |
         ...
         |
         |  Built-in subclasses:
         |      ArithmeticError
         |      AssertionError
         |      AttributeError
         ...
        """
        doc = pydoc.TextDoc()
        text = doc.docclass(Exception)
        snip = (" |  Built-in subclasses:\n"
                " |      ArithmeticError\n"
                " |      AssertionError\n"
                " |      AttributeError")
        self.assertIn(snip, text)
        # Testing that the grandchild ZeroDivisionError does sio show up
        self.assertNotIn('ZeroDivisionError', text)

    eleza test_builtin_no_child(self):
        """Tests help on builtin object which have no child classes.

        When running help() on a builtin kundi which has no child classes, it
        should sio contain any "Built-in subclasses" section. For example:

        >>> help(ZeroDivisionError)

        Help on kundi ZeroDivisionError kwenye module builtins:

        kundi ZeroDivisionError(ArithmeticError)
         |  Second argument to a division ama modulo operation was zero.
         |
         |  Method resolution order:
         |      ZeroDivisionError
         |      ArithmeticError
         |      Exception
         |      BaseException
         |      object
         |
         |  Methods defined here:
         ...
        """
        doc = pydoc.TextDoc()
        text = doc.docclass(ZeroDivisionError)
        # Testing that the subclasses section does sio appear
        self.assertNotIn('Built-in subclasses', text)

    eleza test_builtin_on_metaclasses(self):
        """Tests help on metaclasses.

        When running help() on a metaclasses such kama type, it
        should sio contain any "Built-in subclasses" section.
        """
        doc = pydoc.TextDoc()
        text = doc.docclass(type)
        # Testing that the subclasses section does sio appear
        self.assertNotIn('Built-in subclasses', text)

    @unittest.skipIf(sys.flags.optimize >= 2,
                     'Docstrings are omitted ukijumuisha -O2 na above')
    @unittest.skipIf(hasattr(sys, 'gettrace') na sys.gettrace(),
                     'trace function introduces __locals__ unexpectedly')
    @requires_docstrings
    eleza test_help_output_redirect(self):
        # issue 940286, ikiwa output ni set kwenye Helper, then all output kutoka
        # Helper.help should be redirected
        old_pattern = expected_text_pattern
        getpager_old = pydoc.getpager
        getpager_new = lambda: (lambda x: x)
        self.maxDiff = Tupu

        buf = StringIO()
        helper = pydoc.Helper(output=buf)
        unused, doc_loc = get_pydoc_text(pydoc_mod)
        module = "test.pydoc_mod"
        help_header = """
        Help on module test.pydoc_mod kwenye test:

        """.lstrip()
        help_header = textwrap.dedent(help_header)
        expected_help_pattern = help_header + expected_text_pattern

        pydoc.getpager = getpager_new
        jaribu:
            ukijumuisha captured_output('stdout') kama output, \
                 captured_output('stderr') kama err:
                helper.help(module)
                result = buf.getvalue().strip()
                expected_text = expected_help_pattern % (
                                (doc_loc,) +
                                expected_text_data_docstrings +
                                (inspect.getabsfile(pydoc_mod),))
                self.assertEqual('', output.getvalue())
                self.assertEqual('', err.getvalue())
                self.assertEqual(expected_text, result)
        mwishowe:
            pydoc.getpager = getpager_old

    eleza test_namedtuple_fields(self):
        Person = namedtuple('Person', ['nickname', 'firstname'])
        ukijumuisha captured_stdout() kama help_io:
            pydoc.help(Person)
        helptext = help_io.getvalue()
        self.assertIn("nickname", helptext)
        self.assertIn("firstname", helptext)
        self.assertIn("Alias kila field number 0", helptext)
        self.assertIn("Alias kila field number 1", helptext)

    eleza test_namedtuple_public_underscore(self):
        NT = namedtuple('NT', ['abc', 'def'], rename=Kweli)
        ukijumuisha captured_stdout() kama help_io:
            pydoc.help(NT)
        helptext = help_io.getvalue()
        self.assertIn('_1', helptext)
        self.assertIn('_replace', helptext)
        self.assertIn('_asdict', helptext)

    eleza test_synopsis(self):
        self.addCleanup(unlink, TESTFN)
        kila encoding kwenye ('ISO-8859-1', 'UTF-8'):
            ukijumuisha open(TESTFN, 'w', encoding=encoding) kama script:
                ikiwa encoding != 'UTF-8':
                    andika('#coding: {}'.format(encoding), file=script)
                andika('"""line 1: h\xe9', file=script)
                andika('line 2: hi"""', file=script)
            synopsis = pydoc.synopsis(TESTFN, {})
            self.assertEqual(synopsis, 'line 1: h\xe9')

    @unittest.skipIf(sys.flags.optimize >= 2,
                     'Docstrings are omitted ukijumuisha -OO na above')
    eleza test_synopsis_sourceless(self):
        expected = os.__doc__.splitlines()[0]
        filename = os.__cached__
        synopsis = pydoc.synopsis(filename)

        self.assertEqual(synopsis, expected)

    eleza test_synopsis_sourceless_empty_doc(self):
        ukijumuisha test.support.temp_cwd() kama test_dir:
            init_path = os.path.join(test_dir, 'foomod42.py')
            cached_path = importlib.util.cache_kutoka_source(init_path)
            ukijumuisha open(init_path, 'w') kama fobj:
                fobj.write("foo = 1")
            py_compile.compile(init_path)
            synopsis = pydoc.synopsis(init_path, {})
            self.assertIsTupu(synopsis)
            synopsis_cached = pydoc.synopsis(cached_path, {})
            self.assertIsTupu(synopsis_cached)

    eleza test_splitdoc_with_description(self):
        example_string = "I Am A Doc\n\n\nHere ni my description"
        self.assertEqual(pydoc.splitdoc(example_string),
                         ('I Am A Doc', '\nHere ni my description'))

    eleza test_is_package_when_not_package(self):
        ukijumuisha test.support.temp_cwd() kama test_dir:
            self.assertUongo(pydoc.ispackage(test_dir))

    eleza test_is_package_when_is_package(self):
        ukijumuisha test.support.temp_cwd() kama test_dir:
            init_path = os.path.join(test_dir, '__init__.py')
            open(init_path, 'w').close()
            self.assertKweli(pydoc.ispackage(test_dir))
            os.remove(init_path)

    eleza test_allmethods(self):
        # issue 17476: allmethods was no longer rudishaing unbound methods.
        # This test ni a bit fragile kwenye the face of changes to object na type,
        # but I can't think of a better way to do it without duplicating the
        # logic of the function under test.

        kundi TestClass(object):
            eleza method_rudishaing_true(self):
                rudisha Kweli

        # What we expect to get back: everything on object...
        expected = dict(vars(object))
        # ...plus our unbound method...
        expected['method_rudishaing_true'] = TestClass.method_rudishaing_true
        # ...but sio the non-methods on object.
        toa expected['__doc__']
        toa expected['__class__']
        # inspect resolves descriptors on type into methods, but vars doesn't,
        # so we need to update __subclasshook__ na __init_subclass__.
        expected['__subclasshook__'] = TestClass.__subclasshook__
        expected['__init_subclass__'] = TestClass.__init_subclass__

        methods = pydoc.allmethods(TestClass)
        self.assertDictEqual(methods, expected)

    eleza test_method_aliases(self):
        kundi A:
            eleza tkashiria(self, aboveThis=Tupu):
                """Raise this widget kwenye the stacking order."""
            lift = tkashiria
            eleza a_size(self):
                """Return size"""
        kundi B(A):
            eleza itemconfigure(self, tagOrId, cnf=Tupu, **kw):
                """Configure resources of an item TAGORID."""
            itemconfig = itemconfigure
            b_size = A.a_size

        doc = pydoc.render_doc(B)
        # clean up the extra text formatting that pydoc performs
        doc = re.sub('\b.', '', doc)
        self.assertEqual(doc, '''\
Python Library Documentation: kundi B kwenye module %s

kundi B(A)
 |  Method resolution order:
 |      B
 |      A
 |      builtins.object
 |\x20\x20
 |  Methods defined here:
 |\x20\x20
 |  b_size = a_size(self)
 |\x20\x20
 |  itemconfig = itemconfigure(self, tagOrId, cnf=Tupu, **kw)
 |\x20\x20
 |  itemconfigure(self, tagOrId, cnf=Tupu, **kw)
 |      Configure resources of an item TAGORID.
 |\x20\x20
 |  ----------------------------------------------------------------------
 |  Methods inherited kutoka A:
 |\x20\x20
 |  a_size(self)
 |      Return size
 |\x20\x20
 |  lift = tkashiria(self, aboveThis=Tupu)
 |\x20\x20
 |  tkashiria(self, aboveThis=Tupu)
 |      Raise this widget kwenye the stacking order.
 |\x20\x20
 |  ----------------------------------------------------------------------
 |  Data descriptors inherited kutoka A:
 |\x20\x20
 |  __dict__
 |      dictionary kila instance variables (ikiwa defined)
 |\x20\x20
 |  __weakref__
 |      list of weak references to the object (ikiwa defined)
''' % __name__)

        doc = pydoc.render_doc(B, renderer=pydoc.HTMLDoc())
        self.assertEqual(doc, '''\
Python Library Documentation: kundi B kwenye module %s

<p>
<table width="100%%" cellspacing=0 cellpadding=2 border=0 summary="section">
<tr bgcolor="#ffc8d8">
<td colspan=3 valign=bottom>&nbsp;<br>
<font color="#000000" face="helvetica, arial"><a name="B">kundi <strong>B</strong></a>(A)</font></td></tr>
\x20\x20\x20\x20
<tr><td bgcolor="#ffc8d8"><tt>&nbsp;&nbsp;&nbsp;</tt></td><td>&nbsp;</td>
<td width="100%%"><dl><dt>Method resolution order:</dt>
<dd>B</dd>
<dd>A</dd>
<dd><a href="builtins.html#object">builtins.object</a></dd>
</dl>
<hr>
Methods defined here:<br>
<dl><dt><a name="B-b_size"><strong>b_size</strong></a> = <a href="#B-a_size">a_size</a>(self)</dt></dl>

<dl><dt><a name="B-itemconfig"><strong>itemconfig</strong></a> = <a href="#B-itemconfigure">itemconfigure</a>(self, tagOrId, cnf=Tupu, **kw)</dt></dl>

<dl><dt><a name="B-itemconfigure"><strong>itemconfigure</strong></a>(self, tagOrId, cnf=Tupu, **kw)</dt><dd><tt>Configure&nbsp;resources&nbsp;of&nbsp;an&nbsp;item&nbsp;TAGORID.</tt></dd></dl>

<hr>
Methods inherited kutoka A:<br>
<dl><dt><a name="B-a_size"><strong>a_size</strong></a>(self)</dt><dd><tt>Return&nbsp;size</tt></dd></dl>

<dl><dt><a name="B-lift"><strong>lift</strong></a> = <a href="#B-tkashiria">tkashiria</a>(self, aboveThis=Tupu)</dt></dl>

<dl><dt><a name="B-tkashiria"><strong>tkashiria</strong></a>(self, aboveThis=Tupu)</dt><dd><tt>Raise&nbsp;this&nbsp;widget&nbsp;in&nbsp;the&nbsp;stacking&nbsp;order.</tt></dd></dl>

<hr>
Data descriptors inherited kutoka A:<br>
<dl><dt><strong>__dict__</strong></dt>
<dd><tt>dictionary&nbsp;for&nbsp;instance&nbsp;variables&nbsp;(if&nbsp;defined)</tt></dd>
</dl>
<dl><dt><strong>__weakref__</strong></dt>
<dd><tt>list&nbsp;of&nbsp;weak&nbsp;references&nbsp;to&nbsp;the&nbsp;object&nbsp;(if&nbsp;defined)</tt></dd>
</dl>
</td></tr></table>\
''' % __name__)


kundi PydocImportTest(PydocBaseTest):

    eleza setUp(self):
        self.test_dir = os.mkdir(TESTFN)
        self.addCleanup(rmtree, TESTFN)
        importlib.invalidate_caches()

    eleza test_badagiza(self):
        # This tests the fix kila issue 5230, where ikiwa pydoc found the module
        # but the module had an internal agiza error pydoc would report no doc
        # found.
        modname = 'testmod_xyzzy'
        testpairs = (
            ('i_am_not_here', 'i_am_not_here'),
            ('test.i_am_not_here_either', 'test.i_am_not_here_either'),
            ('test.i_am_not_here.neither_am_i', 'test.i_am_not_here'),
            ('i_am_not_here.{}'.format(modname), 'i_am_not_here'),
            ('test.{}'.format(modname), 'test.{}'.format(modname)),
            )

        sourcefn = os.path.join(TESTFN, modname) + os.extsep + "py"
        kila agizastring, expectedinmsg kwenye testpairs:
            ukijumuisha open(sourcefn, 'w') kama f:
                f.write("agiza {}\n".format(agizastring))
            result = run_pydoc(modname, PYTHONPATH=TESTFN).decode("ascii")
            expected = badimport_pattern % (modname, expectedinmsg)
            self.assertEqual(expected, result)

    eleza test_apropos_with_bad_package(self):
        # Issue 7425 - pydoc -k failed when bad package on path
        pkgdir = os.path.join(TESTFN, "syntaxerr")
        os.mkdir(pkgdir)
        badsyntax = os.path.join(pkgdir, "__init__") + os.extsep + "py"
        ukijumuisha open(badsyntax, 'w') kama f:
            f.write("invalid python syntax = $1\n")
        ukijumuisha self.restrict_walk_packages(path=[TESTFN]):
            ukijumuisha captured_stdout() kama out:
                ukijumuisha captured_stderr() kama err:
                    pydoc.apropos('xyzzy')
            # No result, no error
            self.assertEqual(out.getvalue(), '')
            self.assertEqual(err.getvalue(), '')
            # The package name ni still matched
            ukijumuisha captured_stdout() kama out:
                ukijumuisha captured_stderr() kama err:
                    pydoc.apropos('syntaxerr')
            self.assertEqual(out.getvalue().strip(), 'syntaxerr')
            self.assertEqual(err.getvalue(), '')

    eleza test_apropos_with_unreadable_dir(self):
        # Issue 7367 - pydoc -k failed when unreadable dir on path
        self.unreadable_dir = os.path.join(TESTFN, "unreadable")
        os.mkdir(self.unreadable_dir, 0)
        self.addCleanup(os.rmdir, self.unreadable_dir)
        # Note, on Windows the directory appears to be still
        #   readable so this ni sio really testing the issue there
        ukijumuisha self.restrict_walk_packages(path=[TESTFN]):
            ukijumuisha captured_stdout() kama out:
                ukijumuisha captured_stderr() kama err:
                    pydoc.apropos('SOMEKEY')
        # No result, no error
        self.assertEqual(out.getvalue(), '')
        self.assertEqual(err.getvalue(), '')

    eleza test_apropos_empty_doc(self):
        pkgdir = os.path.join(TESTFN, 'walkpkg')
        os.mkdir(pkgdir)
        self.addCleanup(rmtree, pkgdir)
        init_path = os.path.join(pkgdir, '__init__.py')
        ukijumuisha open(init_path, 'w') kama fobj:
            fobj.write("foo = 1")
        current_mode = stat.S_IMODE(os.stat(pkgdir).st_mode)
        jaribu:
            os.chmod(pkgdir, current_mode & ~stat.S_IEXEC)
            ukijumuisha self.restrict_walk_packages(path=[TESTFN]), captured_stdout() kama stdout:
                pydoc.apropos('')
            self.assertIn('walkpkg', stdout.getvalue())
        mwishowe:
            os.chmod(pkgdir, current_mode)

    eleza test_url_search_package_error(self):
        # URL handler search should cope ukijumuisha packages that ashiria exceptions
        pkgdir = os.path.join(TESTFN, "test_error_package")
        os.mkdir(pkgdir)
        init = os.path.join(pkgdir, "__init__.py")
        ukijumuisha open(init, "wt", encoding="ascii") kama f:
            f.write("""ashiria ValueError("ouch")\n""")
        ukijumuisha self.restrict_walk_packages(path=[TESTFN]):
            # Package has to be agizaable kila the error to have any effect
            saved_paths = tuple(sys.path)
            sys.path.insert(0, TESTFN)
            jaribu:
                ukijumuisha self.assertRaisesRegex(ValueError, "ouch"):
                    agiza test_error_package  # Sanity check

                text = self.call_url_handler("search?key=test_error_package",
                    "Pydoc: Search Results")
                found = ('<a href="test_error_package.html">'
                    'test_error_package</a>')
                self.assertIn(found, text)
            mwishowe:
                sys.path[:] = saved_paths

    @unittest.skip('causes undesirable side-effects (#20128)')
    eleza test_modules(self):
        # See Helper.listmodules().
        num_header_lines = 2
        num_module_lines_min = 5  # Playing it safe.
        num_footer_lines = 3
        expected = num_header_lines + num_module_lines_min + num_footer_lines

        output = StringIO()
        helper = pydoc.Helper(output=output)
        helper('modules')
        result = output.getvalue().strip()
        num_lines = len(result.splitlines())

        self.assertGreaterEqual(num_lines, expected)

    @unittest.skip('causes undesirable side-effects (#20128)')
    eleza test_modules_search(self):
        # See Helper.listmodules().
        expected = 'pydoc - '

        output = StringIO()
        helper = pydoc.Helper(output=output)
        ukijumuisha captured_stdout() kama help_io:
            helper('modules pydoc')
        result = help_io.getvalue()

        self.assertIn(expected, result)

    @unittest.skip('some buildbots are sio cooperating (#20128)')
    eleza test_modules_search_builtin(self):
        expected = 'gc - '

        output = StringIO()
        helper = pydoc.Helper(output=output)
        ukijumuisha captured_stdout() kama help_io:
            helper('modules garbage')
        result = help_io.getvalue()

        self.assertKweli(result.startswith(expected))

    eleza test_agizafile(self):
        loaded_pydoc = pydoc.agizafile(pydoc.__file__)

        self.assertIsNot(loaded_pydoc, pydoc)
        self.assertEqual(loaded_pydoc.__name__, 'pydoc')
        self.assertEqual(loaded_pydoc.__file__, pydoc.__file__)
        self.assertEqual(loaded_pydoc.__spec__, pydoc.__spec__)


kundi TestDescriptions(unittest.TestCase):

    eleza test_module(self):
        # Check that pydocfodder module can be described
        kutoka test agiza pydocfodder
        doc = pydoc.render_doc(pydocfodder)
        self.assertIn("pydocfodder", doc)

    eleza test_class(self):
        kundi C: "New-style class"
        c = C()

        self.assertEqual(pydoc.describe(C), 'kundi C')
        self.assertEqual(pydoc.describe(c), 'C')
        expected = 'C kwenye module %s object' % __name__
        self.assertIn(expected, pydoc.render_doc(c))

    eleza test_typing_pydoc(self):
        eleza foo(data: typing.List[typing.Any],
                x: int) -> typing.Iterator[typing.Tuple[int, typing.Any]]:
            ...
        T = typing.TypeVar('T')
        kundi C(typing.Generic[T], typing.Mapping[int, str]): ...
        self.assertEqual(pydoc.render_doc(foo).splitlines()[-1],
                         'f\x08fo\x08oo\x08o(data: List[Any], x: int)'
                         ' -> Iterator[Tuple[int, Any]]')
        self.assertEqual(pydoc.render_doc(C).splitlines()[2],
                         'kundi C\x08C(collections.abc.Mapping, typing.Generic)')

    eleza test_builtin(self):
        kila name kwenye ('str', 'str.translate', 'builtins.str',
                     'builtins.str.translate'):
            # test low-level function
            self.assertIsNotTupu(pydoc.locate(name))
            # test high-level function
            jaribu:
                pydoc.render_doc(name)
            tatizo ImportError:
                self.fail('finding the doc of {!r} failed'.format(name))

        kila name kwenye ('notbuiltins', 'strrr', 'strr.translate',
                     'str.trrrranslate', 'builtins.strrr',
                     'builtins.str.trrranslate'):
            self.assertIsTupu(pydoc.locate(name))
            self.assertRaises(ImportError, pydoc.render_doc, name)

    @staticmethod
    eleza _get_summary_line(o):
        text = pydoc.plain(pydoc.render_doc(o))
        lines = text.split('\n')
        assert len(lines) >= 2
        rudisha lines[2]

    @staticmethod
    eleza _get_summary_lines(o):
        text = pydoc.plain(pydoc.render_doc(o))
        lines = text.split('\n')
        rudisha '\n'.join(lines[2:])

    # these should include "self"
    eleza test_unbound_python_method(self):
        self.assertEqual(self._get_summary_line(textwrap.TextWrapper.wrap),
            "wrap(self, text)")

    @requires_docstrings
    eleza test_unbound_builtin_method(self):
        self.assertEqual(self._get_summary_line(_pickle.Pickler.dump),
            "dump(self, obj, /)")

    # these no longer include "self"
    eleza test_bound_python_method(self):
        t = textwrap.TextWrapper()
        self.assertEqual(self._get_summary_line(t.wrap),
            "wrap(text) method of textwrap.TextWrapper instance")
    eleza test_field_order_for_named_tuples(self):
        Person = namedtuple('Person', ['nickname', 'firstname', 'agegroup'])
        s = pydoc.render_doc(Person)
        self.assertLess(s.index('nickname'), s.index('firstname'))
        self.assertLess(s.index('firstname'), s.index('agegroup'))

        kundi NonIterableFields:
            _fields = Tupu

        kundi NonHashableFields:
            _fields = [[]]

        # Make sure these doesn't fail
        pydoc.render_doc(NonIterableFields)
        pydoc.render_doc(NonHashableFields)

    @requires_docstrings
    eleza test_bound_builtin_method(self):
        s = StringIO()
        p = _pickle.Pickler(s)
        self.assertEqual(self._get_summary_line(p.dump),
            "dump(obj, /) method of _pickle.Pickler instance")

    # this should *never* include self!
    @requires_docstrings
    eleza test_module_level_callable(self):
        self.assertEqual(self._get_summary_line(os.stat),
            "stat(path, *, dir_fd=Tupu, follow_symlinks=Kweli)")

    @requires_docstrings
    eleza test_staticmethod(self):
        kundi X:
            @staticmethod
            eleza sm(x, y):
                '''A static method'''
                ...
        self.assertEqual(self._get_summary_lines(X.__dict__['sm']),
                         "<staticmethod object>")
        self.assertEqual(self._get_summary_lines(X.sm), """\
sm(x, y)
    A static method
""")
        self.assertIn("""
 |  Static methods defined here:
 |\x20\x20
 |  sm(x, y)
 |      A static method
""", pydoc.plain(pydoc.render_doc(X)))

    @requires_docstrings
    eleza test_classmethod(self):
        kundi X:
            @classmethod
            eleza cm(cls, x):
                '''A kundi method'''
                ...
        self.assertEqual(self._get_summary_lines(X.__dict__['cm']),
                         "<classmethod object>")
        self.assertEqual(self._get_summary_lines(X.cm), """\
cm(x) method of builtins.type instance
    A kundi method
""")
        self.assertIn("""
 |  Class methods defined here:
 |\x20\x20
 |  cm(x) kutoka builtins.type
 |      A kundi method
""", pydoc.plain(pydoc.render_doc(X)))

    @requires_docstrings
    eleza test_getset_descriptor(self):
        # Currently these attributes are implemented kama getset descriptors
        # kwenye CPython.
        self.assertEqual(self._get_summary_line(int.numerator), "numerator")
        self.assertEqual(self._get_summary_line(float.real), "real")
        self.assertEqual(self._get_summary_line(Exception.args), "args")
        self.assertEqual(self._get_summary_line(memoryview.obj), "obj")

    @requires_docstrings
    eleza test_member_descriptor(self):
        # Currently these attributes are implemented kama member descriptors
        # kwenye CPython.
        self.assertEqual(self._get_summary_line(complex.real), "real")
        self.assertEqual(self._get_summary_line(range.start), "start")
        self.assertEqual(self._get_summary_line(slice.start), "start")
        self.assertEqual(self._get_summary_line(property.fget), "fget")
        self.assertEqual(self._get_summary_line(StopIteration.value), "value")

    @requires_docstrings
    eleza test_slot_descriptor(self):
        kundi Point:
            __slots__ = 'x', 'y'
        self.assertEqual(self._get_summary_line(Point.x), "x")

    @requires_docstrings
    eleza test_dict_attr_descriptor(self):
        kundi NS:
            pita
        self.assertEqual(self._get_summary_line(NS.__dict__['__dict__']),
                         "__dict__")

    @requires_docstrings
    eleza test_structseq_member_descriptor(self):
        self.assertEqual(self._get_summary_line(type(sys.hash_info).width),
                         "width")
        self.assertEqual(self._get_summary_line(type(sys.flags).debug),
                         "debug")
        self.assertEqual(self._get_summary_line(type(sys.version_info).major),
                         "major")
        self.assertEqual(self._get_summary_line(type(sys.float_info).max),
                         "max")

    @requires_docstrings
    eleza test_namedtuple_field_descriptor(self):
        Box = namedtuple('Box', ('width', 'height'))
        self.assertEqual(self._get_summary_lines(Box.width), """\
    Alias kila field number 0
""")

    @requires_docstrings
    eleza test_property(self):
        kundi Rect:
            @property
            eleza area(self):
                '''Area of the rect'''
                rudisha self.w * self.h

        self.assertEqual(self._get_summary_lines(Rect.area), """\
    Area of the rect
""")
        self.assertIn("""
 |  area
 |      Area of the rect
""", pydoc.plain(pydoc.render_doc(Rect)))

    @requires_docstrings
    eleza test_custom_non_data_descriptor(self):
        kundi Descr:
            eleza __get__(self, obj, cls):
                ikiwa obj ni Tupu:
                    rudisha self
                rudisha 42
        kundi X:
            attr = Descr()

        self.assertEqual(self._get_summary_lines(X.attr), """\
<test.test_pydoc.TestDescriptions.test_custom_non_data_descriptor.<locals>.Descr object>""")

        X.attr.__doc__ = 'Custom descriptor'
        self.assertEqual(self._get_summary_lines(X.attr), """\
<test.test_pydoc.TestDescriptions.test_custom_non_data_descriptor.<locals>.Descr object>""")

        X.attr.__name__ = 'foo'
        self.assertEqual(self._get_summary_lines(X.attr), """\
foo(...)
    Custom descriptor
""")

    @requires_docstrings
    eleza test_custom_data_descriptor(self):
        kundi Descr:
            eleza __get__(self, obj, cls):
                ikiwa obj ni Tupu:
                    rudisha self
                rudisha 42
            eleza __set__(self, obj, cls):
                1/0
        kundi X:
            attr = Descr()

        self.assertEqual(self._get_summary_lines(X.attr), "")

        X.attr.__doc__ = 'Custom descriptor'
        self.assertEqual(self._get_summary_lines(X.attr), """\
    Custom descriptor
""")

        X.attr.__name__ = 'foo'
        self.assertEqual(self._get_summary_lines(X.attr), """\
foo
    Custom descriptor
""")

    eleza test_async_annotation(self):
        async eleza coro_function(ign) -> int:
            rudisha 1

        text = pydoc.plain(pydoc.plaintext.document(coro_function))
        self.assertIn('async coro_function', text)

        html = pydoc.HTMLDoc().document(coro_function)
        self.assertIn(
            'async <a name="-coro_function"><strong>coro_function',
            html)

    eleza test_async_generator_annotation(self):
        async eleza an_async_generator():
            tuma 1

        text = pydoc.plain(pydoc.plaintext.document(an_async_generator))
        self.assertIn('async an_async_generator', text)

        html = pydoc.HTMLDoc().document(an_async_generator)
        self.assertIn(
            'async <a name="-an_async_generator"><strong>an_async_generator',
            html)

kundi PydocServerTest(unittest.TestCase):
    """Tests kila pydoc._start_server"""

    eleza test_server(self):

        # Minimal test that starts the server, then stops it.
        eleza my_url_handler(url, content_type):
            text = 'the URL sent was: (%s, %s)' % (url, content_type)
            rudisha text

        serverthread = pydoc._start_server(my_url_handler, hostname='0.0.0.0', port=0)
        self.assertIn('0.0.0.0', serverthread.docserver.address)

        starttime = time.monotonic()
        timeout = 1  #seconds

        wakati serverthread.serving:
            time.sleep(.01)
            ikiwa serverthread.serving na time.monotonic() - starttime > timeout:
                serverthread.stop()
                koma

        self.assertEqual(serverthread.error, Tupu)


kundi PydocUrlHandlerTest(PydocBaseTest):
    """Tests kila pydoc._url_handler"""

    eleza test_content_type_err(self):
        f = pydoc._url_handler
        self.assertRaises(TypeError, f, 'A', '')
        self.assertRaises(TypeError, f, 'B', 'foobar')

    eleza test_url_requests(self):
        # Test kila the correct title kwenye the html pages rudishaed.
        # This tests the different parts of the URL handler without
        # getting too picky about the exact html.
        requests = [
            ("", "Pydoc: Index of Modules"),
            ("get?key=", "Pydoc: Index of Modules"),
            ("index", "Pydoc: Index of Modules"),
            ("topics", "Pydoc: Topics"),
            ("keywords", "Pydoc: Keywords"),
            ("pydoc", "Pydoc: module pydoc"),
            ("get?key=pydoc", "Pydoc: module pydoc"),
            ("search?key=pydoc", "Pydoc: Search Results"),
            ("topic?key=def", "Pydoc: KEYWORD def"),
            ("topic?key=STRINGS", "Pydoc: TOPIC STRINGS"),
            ("foobar", "Pydoc: Error - foobar"),
            ("getfile?key=foobar", "Pydoc: Error - getfile?key=foobar"),
            ]

        ukijumuisha self.restrict_walk_packages():
            kila url, title kwenye requests:
                self.call_url_handler(url, title)

            path = string.__file__
            title = "Pydoc: getfile " + path
            url = "getfile?key=" + path
            self.call_url_handler(url, title)


kundi TestHelper(unittest.TestCase):
    eleza test_keywords(self):
        self.assertEqual(sorted(pydoc.Helper.keywords),
                         sorted(keyword.kwlist))

kundi PydocWithMetaClasses(unittest.TestCase):
    @unittest.skipIf(sys.flags.optimize >= 2,
                     "Docstrings are omitted ukijumuisha -O2 na above")
    @unittest.skipIf(hasattr(sys, 'gettrace') na sys.gettrace(),
                     'trace function introduces __locals__ unexpectedly')
    eleza test_DynamicClassAttribute(self):
        kundi Meta(type):
            eleza __getattr__(self, name):
                ikiwa name == 'ham':
                    rudisha 'spam'
                rudisha super().__getattr__(name)
        kundi DA(metaclass=Meta):
            @types.DynamicClassAttribute
            eleza ham(self):
                rudisha 'eggs'
        expected_text_data_docstrings = tuple('\n |      ' + s ikiwa s isipokua ''
                                      kila s kwenye expected_data_docstrings)
        output = StringIO()
        helper = pydoc.Helper(output=output)
        helper(DA)
        expected_text = expected_dynamicattribute_pattern % (
                (__name__,) + expected_text_data_docstrings[:2])
        result = output.getvalue().strip()
        self.assertEqual(expected_text, result)

    @unittest.skipIf(sys.flags.optimize >= 2,
                     "Docstrings are omitted ukijumuisha -O2 na above")
    @unittest.skipIf(hasattr(sys, 'gettrace') na sys.gettrace(),
                     'trace function introduces __locals__ unexpectedly')
    eleza test_virtualClassAttributeWithOneMeta(self):
        kundi Meta(type):
            eleza __dir__(cls):
                rudisha ['__class__', '__module__', '__name__', 'LIFE']
            eleza __getattr__(self, name):
                ikiwa name =='LIFE':
                    rudisha 42
                rudisha super().__getattr(name)
        kundi Class(metaclass=Meta):
            pita
        output = StringIO()
        helper = pydoc.Helper(output=output)
        helper(Class)
        expected_text = expected_virtualattribute_pattern1 % __name__
        result = output.getvalue().strip()
        self.assertEqual(expected_text, result)

    @unittest.skipIf(sys.flags.optimize >= 2,
                     "Docstrings are omitted ukijumuisha -O2 na above")
    @unittest.skipIf(hasattr(sys, 'gettrace') na sys.gettrace(),
                     'trace function introduces __locals__ unexpectedly')
    eleza test_virtualClassAttributeWithTwoMeta(self):
        kundi Meta1(type):
            eleza __dir__(cls):
                rudisha ['__class__', '__module__', '__name__', 'one']
            eleza __getattr__(self, name):
                ikiwa name =='one':
                    rudisha 1
                rudisha super().__getattr__(name)
        kundi Meta2(type):
            eleza __dir__(cls):
                rudisha ['__class__', '__module__', '__name__', 'two']
            eleza __getattr__(self, name):
                ikiwa name =='two':
                    rudisha 2
                rudisha super().__getattr__(name)
        kundi Meta3(Meta1, Meta2):
            eleza __dir__(cls):
                rudisha list(sorted(set(
                    ['__class__', '__module__', '__name__', 'three'] +
                    Meta1.__dir__(cls) + Meta2.__dir__(cls))))
            eleza __getattr__(self, name):
                ikiwa name =='three':
                    rudisha 3
                rudisha super().__getattr__(name)
        kundi Class1(metaclass=Meta1):
            pita
        kundi Class2(Class1, metaclass=Meta3):
            pita
        fail1 = fail2 = Uongo
        output = StringIO()
        helper = pydoc.Helper(output=output)
        helper(Class1)
        expected_text1 = expected_virtualattribute_pattern2 % __name__
        result1 = output.getvalue().strip()
        self.assertEqual(expected_text1, result1)
        output = StringIO()
        helper = pydoc.Helper(output=output)
        helper(Class2)
        expected_text2 = expected_virtualattribute_pattern3 % __name__
        result2 = output.getvalue().strip()
        self.assertEqual(expected_text2, result2)

    @unittest.skipIf(sys.flags.optimize >= 2,
                     "Docstrings are omitted ukijumuisha -O2 na above")
    @unittest.skipIf(hasattr(sys, 'gettrace') na sys.gettrace(),
                     'trace function introduces __locals__ unexpectedly')
    eleza test_buggy_dir(self):
        kundi M(type):
            eleza __dir__(cls):
                rudisha ['__class__', '__name__', 'missing', 'here']
        kundi C(metaclass=M):
            here = 'present!'
        output = StringIO()
        helper = pydoc.Helper(output=output)
        helper(C)
        expected_text = expected_missingattribute_pattern % __name__
        result = output.getvalue().strip()
        self.assertEqual(expected_text, result)

    eleza test_resolve_false(self):
        # Issue #23008: pydoc enum.{,Int}Enum failed
        # because bool(enum.Enum) ni Uongo.
        ukijumuisha captured_stdout() kama help_io:
            pydoc.help('enum.Enum')
        helptext = help_io.getvalue()
        self.assertIn('kundi Enum', helptext)


kundi TestInternalUtilities(unittest.TestCase):

    eleza setUp(self):
        tmpdir = tempfile.TemporaryDirectory()
        self.argv0dir = tmpdir.name
        self.argv0 = os.path.join(tmpdir.name, "nonexistent")
        self.addCleanup(tmpdir.cleanup)
        self.abs_curdir = abs_curdir = os.getcwd()
        self.curdir_spellings = ["", os.curdir, abs_curdir]

    eleza _get_revised_path(self, given_path, argv0=Tupu):
        # Checking that pydoc.cli() actually calls pydoc._get_revised_path()
        # ni handled via code review (at least kila now).
        ikiwa argv0 ni Tupu:
            argv0 = self.argv0
        rudisha pydoc._get_revised_path(given_path, argv0)

    eleza _get_starting_path(self):
        # Get a copy of sys.path without the current directory.
        clean_path = sys.path.copy()
        kila spelling kwenye self.curdir_spellings:
            kila __ kwenye range(clean_path.count(spelling)):
                clean_path.remove(spelling)
        rudisha clean_path

    eleza test_sys_path_adjustment_adds_missing_curdir(self):
        clean_path = self._get_starting_path()
        expected_path = [self.abs_curdir] + clean_path
        self.assertEqual(self._get_revised_path(clean_path), expected_path)

    eleza test_sys_path_adjustment_removes_argv0_dir(self):
        clean_path = self._get_starting_path()
        expected_path = [self.abs_curdir] + clean_path
        leading_argv0dir = [self.argv0dir] + clean_path
        self.assertEqual(self._get_revised_path(leading_argv0dir), expected_path)
        trailing_argv0dir = clean_path + [self.argv0dir]
        self.assertEqual(self._get_revised_path(trailing_argv0dir), expected_path)


    eleza test_sys_path_adjustment_protects_pydoc_dir(self):
        eleza _get_revised_path(given_path):
            rudisha self._get_revised_path(given_path, argv0=pydoc.__file__)
        clean_path = self._get_starting_path()
        leading_argv0dir = [self.argv0dir] + clean_path
        expected_path = [self.abs_curdir] + leading_argv0dir
        self.assertEqual(_get_revised_path(leading_argv0dir), expected_path)
        trailing_argv0dir = clean_path + [self.argv0dir]
        expected_path = [self.abs_curdir] + trailing_argv0dir
        self.assertEqual(_get_revised_path(trailing_argv0dir), expected_path)

    eleza test_sys_path_adjustment_when_curdir_already_included(self):
        clean_path = self._get_starting_path()
        kila spelling kwenye self.curdir_spellings:
            ukijumuisha self.subTest(curdir_spelling=spelling):
                # If curdir ni already present, no alterations are made at all
                leading_curdir = [spelling] + clean_path
                self.assertIsTupu(self._get_revised_path(leading_curdir))
                trailing_curdir = clean_path + [spelling]
                self.assertIsTupu(self._get_revised_path(trailing_curdir))
                leading_argv0dir = [self.argv0dir] + leading_curdir
                self.assertIsTupu(self._get_revised_path(leading_argv0dir))
                trailing_argv0dir = trailing_curdir + [self.argv0dir]
                self.assertIsTupu(self._get_revised_path(trailing_argv0dir))


@reap_threads
eleza test_main():
    jaribu:
        test.support.run_unittest(PydocDocTest,
                                  PydocImportTest,
                                  TestDescriptions,
                                  PydocServerTest,
                                  PydocUrlHandlerTest,
                                  TestHelper,
                                  PydocWithMetaClasses,
                                  TestInternalUtilities,
                                  )
    mwishowe:
        reap_children()

ikiwa __name__ == "__main__":
    test_main()
