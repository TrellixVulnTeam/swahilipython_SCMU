# Module doctest.
# Released to the public domain 16-Jan-2001, by Tim Peters (tim@python.org).
# Major enhancements na refactoring by:
#     Jim Fulton
#     Edward Loper

# Provided as-is; use at your own risk; no warranty; no promises; enjoy!

r"""Module doctest -- a framework kila running examples kwenye docstrings.

In simplest use, end each module M to be tested with:

eleza _test():
    agiza doctest
    doctest.testmod()

ikiwa __name__ == "__main__":
    _test()

Then running the module kama a script will cause the examples kwenye the
docstrings to get executed na verified:

python M.py

This won't display anything unless an example fails, kwenye which case the
failing example(s) na the cause(s) of the failure(s) are printed to stdout
(why sio stderr? because stderr ni a lame hack <0.2 wink>), na the final
line of output ni "Test failed.".

Run it ukijumuisha the -v switch instead:

python M.py -v

and a detailed report of all examples tried ni printed to stdout, along
ukijumuisha assorted summaries at the end.

You can force verbose mode by pitaing "verbose=Kweli" to testmod, ama prohibit
it by pitaing "verbose=Uongo".  In either of those cases, sys.argv ni sio
examined by testmod.

There are a variety of other ways to run doctests, including integration
ukijumuisha the unittest framework, na support kila running non-Python text
files containing doctests.  There are also many ways to override parts
of doctest's default behaviors.  See the Library Reference Manual for
details.
"""

__docformat__ = 'reStructuredText en'

__all__ = [
    # 0, Option Flags
    'register_optionflag',
    'DONT_ACCEPT_TRUE_FOR_1',
    'DONT_ACCEPT_BLANKLINE',
    'NORMALIZE_WHITESPACE',
    'ELLIPSIS',
    'SKIP',
    'IGNORE_EXCEPTION_DETAIL',
    'COMPARISON_FLAGS',
    'REPORT_UDIFF',
    'REPORT_CDIFF',
    'REPORT_NDIFF',
    'REPORT_ONLY_FIRST_FAILURE',
    'REPORTING_FLAGS',
    'FAIL_FAST',
    # 1. Utility Functions
    # 2. Example & DocTest
    'Example',
    'DocTest',
    # 3. Doctest Parser
    'DocTestParser',
    # 4. Doctest Finder
    'DocTestFinder',
    # 5. Doctest Runner
    'DocTestRunner',
    'OutputChecker',
    'DocTestFailure',
    'UnexpectedException',
    'DebugRunner',
    # 6. Test Functions
    'testmod',
    'testfile',
    'run_docstring_examples',
    # 7. Unittest Support
    'DocTestSuite',
    'DocFileSuite',
    'set_unittest_reportflags',
    # 8. Debugging Support
    'script_from_examples',
    'testsource',
    'debug_src',
    'debug',
]

agiza __future__
agiza difflib
agiza inspect
agiza linecache
agiza os
agiza pdb
agiza re
agiza sys
agiza traceback
agiza unittest
kutoka io agiza StringIO
kutoka collections agiza namedtuple

TestResults = namedtuple('TestResults', 'failed attempted')

# There are 4 basic classes:
#  - Example: a <source, want> pair, plus an intra-docstring line number.
#  - DocTest: a collection of examples, parsed kutoka a docstring, plus
#    info about where the docstring came kutoka (name, filename, lineno).
#  - DocTestFinder: extracts DocTests kutoka a given object's docstring na
#    its contained objects' docstrings.
#  - DocTestRunner: runs DocTest cases, na accumulates statistics.
#
# So the basic picture is:
#
#                             list of:
# +------+                   +---------+                   +-------+
# |object| --DocTestFinder-> | DocTest | --DocTestRunner-> |results|
# +------+                   +---------+                   +-------+
#                            | Example |
#                            |   ...   |
#                            | Example |
#                            +---------+

# Option constants.

OPTIONFLAGS_BY_NAME = {}
eleza register_optionflag(name):
    # Create a new flag unless `name` ni already known.
    rudisha OPTIONFLAGS_BY_NAME.setdefault(name, 1 << len(OPTIONFLAGS_BY_NAME))

DONT_ACCEPT_TRUE_FOR_1 = register_optionflag('DONT_ACCEPT_TRUE_FOR_1')
DONT_ACCEPT_BLANKLINE = register_optionflag('DONT_ACCEPT_BLANKLINE')
NORMALIZE_WHITESPACE = register_optionflag('NORMALIZE_WHITESPACE')
ELLIPSIS = register_optionflag('ELLIPSIS')
SKIP = register_optionflag('SKIP')
IGNORE_EXCEPTION_DETAIL = register_optionflag('IGNORE_EXCEPTION_DETAIL')

COMPARISON_FLAGS = (DONT_ACCEPT_TRUE_FOR_1 |
                    DONT_ACCEPT_BLANKLINE |
                    NORMALIZE_WHITESPACE |
                    ELLIPSIS |
                    SKIP |
                    IGNORE_EXCEPTION_DETAIL)

REPORT_UDIFF = register_optionflag('REPORT_UDIFF')
REPORT_CDIFF = register_optionflag('REPORT_CDIFF')
REPORT_NDIFF = register_optionflag('REPORT_NDIFF')
REPORT_ONLY_FIRST_FAILURE = register_optionflag('REPORT_ONLY_FIRST_FAILURE')
FAIL_FAST = register_optionflag('FAIL_FAST')

REPORTING_FLAGS = (REPORT_UDIFF |
                   REPORT_CDIFF |
                   REPORT_NDIFF |
                   REPORT_ONLY_FIRST_FAILURE |
                   FAIL_FAST)

# Special string markers kila use kwenye `want` strings:
BLANKLINE_MARKER = '<BLANKLINE>'
ELLIPSIS_MARKER = '...'

######################################################################
## Table of Contents
######################################################################
#  1. Utility Functions
#  2. Example & DocTest -- store test cases
#  3. DocTest Parser -- extracts examples kutoka strings
#  4. DocTest Finder -- extracts test cases kutoka objects
#  5. DocTest Runner -- runs test cases
#  6. Test Functions -- convenient wrappers kila testing
#  7. Unittest Support
#  8. Debugging Support
#  9. Example Usage

######################################################################
## 1. Utility Functions
######################################################################

eleza _extract_future_flags(globs):
    """
    Return the compiler-flags associated ukijumuisha the future features that
    have been imported into the given namespace (globs).
    """
    flags = 0
    kila fname kwenye __future__.all_feature_names:
        feature = globs.get(fname, Tupu)
        ikiwa feature ni getattr(__future__, fname):
            flags |= feature.compiler_flag
    rudisha flags

eleza _normalize_module(module, depth=2):
    """
    Return the module specified by `module`.  In particular:
      - If `module` ni a module, then rudisha module.
      - If `module` ni a string, then agiza na rudisha the
        module ukijumuisha that name.
      - If `module` ni Tupu, then rudisha the calling module.
        The calling module ni assumed to be the module of
        the stack frame at the given depth kwenye the call stack.
    """
    ikiwa inspect.ismodule(module):
        rudisha module
    lasivyo isinstance(module, str):
        rudisha __import__(module, globals(), locals(), ["*"])
    lasivyo module ni Tupu:
        rudisha sys.modules[sys._getframe(depth).f_globals['__name__']]
    isipokua:
        ashiria TypeError("Expected a module, string, ama Tupu")

eleza _load_testfile(filename, package, module_relative, encoding):
    ikiwa module_relative:
        package = _normalize_module(package, 3)
        filename = _module_relative_path(package, filename)
        ikiwa getattr(package, '__loader__', Tupu) ni sio Tupu:
            ikiwa hasattr(package.__loader__, 'get_data'):
                file_contents = package.__loader__.get_data(filename)
                file_contents = file_contents.decode(encoding)
                # get_data() opens files kama 'rb', so one must do the equivalent
                # conversion kama universal newlines would do.
                rudisha file_contents.replace(os.linesep, '\n'), filename
    ukijumuisha open(filename, encoding=encoding) kama f:
        rudisha f.read(), filename

eleza _indent(s, indent=4):
    """
    Add the given number of space characters to the beginning of
    every non-blank line kwenye `s`, na rudisha the result.
    """
    # This regexp matches the start of non-blank lines:
    rudisha re.sub('(?m)^(?!$)', indent*' ', s)

eleza _exception_traceback(exc_info):
    """
    Return a string containing a traceback message kila the given
    exc_info tuple (as returned by sys.exc_info()).
    """
    # Get a traceback message.
    excout = StringIO()
    exc_type, exc_val, exc_tb = exc_info
    traceback.print_exception(exc_type, exc_val, exc_tb, file=excout)
    rudisha excout.getvalue()

# Override some StringIO methods.
kundi _SpoofOut(StringIO):
    eleza getvalue(self):
        result = StringIO.getvalue(self)
        # If anything at all was written, make sure there's a trailing
        # newline.  There's no way kila the expected output to indicate
        # that a trailing newline ni missing.
        ikiwa result na sio result.endswith("\n"):
            result += "\n"
        rudisha result

    eleza truncate(self, size=Tupu):
        self.seek(size)
        StringIO.truncate(self)

# Worst-case linear-time ellipsis matching.
eleza _ellipsis_match(want, got):
    """
    Essentially the only subtle case:
    >>> _ellipsis_match('aa...aa', 'aaa')
    Uongo
    """
    ikiwa ELLIPSIS_MARKER haiko kwenye want:
        rudisha want == got

    # Find "the real" strings.
    ws = want.split(ELLIPSIS_MARKER)
    assert len(ws) >= 2

    # Deal ukijumuisha exact matches possibly needed at one ama both ends.
    startpos, endpos = 0, len(got)
    w = ws[0]
    ikiwa w:   # starts ukijumuisha exact match
        ikiwa got.startswith(w):
            startpos = len(w)
            toa ws[0]
        isipokua:
            rudisha Uongo
    w = ws[-1]
    ikiwa w:   # ends ukijumuisha exact match
        ikiwa got.endswith(w):
            endpos -= len(w)
            toa ws[-1]
        isipokua:
            rudisha Uongo

    ikiwa startpos > endpos:
        # Exact end matches required more characters than we have, kama kwenye
        # _ellipsis_match('aa...aa', 'aaa')
        rudisha Uongo

    # For the rest, we only need to find the leftmost non-overlapping
    # match kila each piece.  If there's no overall match that way alone,
    # there's no overall match period.
    kila w kwenye ws:
        # w may be '' at times, ikiwa there are consecutive ellipses, ama
        # due to an ellipsis at the start ama end of `want`.  That's OK.
        # Search kila an empty string succeeds, na doesn't change startpos.
        startpos = got.find(w, startpos, endpos)
        ikiwa startpos < 0:
            rudisha Uongo
        startpos += len(w)

    rudisha Kweli

eleza _comment_line(line):
    "Return a commented form of the given line"
    line = line.rstrip()
    ikiwa line:
        rudisha '# '+line
    isipokua:
        rudisha '#'

eleza _strip_exception_details(msg):
    # Support kila IGNORE_EXCEPTION_DETAIL.
    # Get rid of everything tatizo the exception name; kwenye particular, drop
    # the possibly dotted module path (ikiwa any) na the exception message (if
    # any).  We assume that a colon ni never part of a dotted name, ama of an
    # exception name.
    # E.g., given
    #    "foo.bar.MyError: la di da"
    # rudisha "MyError"
    # Or kila "abc.def" ama "abc.def:\n" rudisha "def".

    start, end = 0, len(msg)
    # The exception name must appear on the first line.
    i = msg.find("\n")
    ikiwa i >= 0:
        end = i
    # retain up to the first colon (ikiwa any)
    i = msg.find(':', 0, end)
    ikiwa i >= 0:
        end = i
    # retain just the exception name
    i = msg.rfind('.', 0, end)
    ikiwa i >= 0:
        start = i+1
    rudisha msg[start: end]

kundi _OutputRedirectingPdb(pdb.Pdb):
    """
    A specialized version of the python debugger that redirects stdout
    to a given stream when interacting ukijumuisha the user.  Stdout ni *not*
    redirected when traced code ni executed.
    """
    eleza __init__(self, out):
        self.__out = out
        self.__debugger_used = Uongo
        # do sio play signal games kwenye the pdb
        pdb.Pdb.__init__(self, stdout=out, nosigint=Kweli)
        # still use uliza() to get user input
        self.use_rawinput = 1

    eleza set_trace(self, frame=Tupu):
        self.__debugger_used = Kweli
        ikiwa frame ni Tupu:
            frame = sys._getframe().f_back
        pdb.Pdb.set_trace(self, frame)

    eleza set_endelea(self):
        # Calling set_endelea unconditionally would koma unit test
        # coverage reporting, kama Bdb.set_endelea calls sys.settrace(Tupu).
        ikiwa self.__debugger_used:
            pdb.Pdb.set_endelea(self)

    eleza trace_dispatch(self, *args):
        # Redirect stdout to the given stream.
        save_stdout = sys.stdout
        sys.stdout = self.__out
        # Call Pdb's trace dispatch method.
        jaribu:
            rudisha pdb.Pdb.trace_dispatch(self, *args)
        mwishowe:
            sys.stdout = save_stdout

# [XX] Normalize ukijumuisha respect to os.path.pardir?
eleza _module_relative_path(module, test_path):
    ikiwa sio inpect.ismodule(module):
        ashiria TypeError('Expected a module: %r' % module)
    ikiwa test_path.startswith('/'):
        ashiria ValueError('Module-relative files may sio have absolute paths')

    # Normalize the path. On Windows, replace "/" ukijumuisha "\".
    test_path = os.path.join(*(test_path.split('/')))

    # Find the base directory kila the path.
    ikiwa hasattr(module, '__file__'):
        # A normal module/package
        basedir = os.path.split(module.__file__)[0]
    lasivyo module.__name__ == '__main__':
        # An interactive session.
        ikiwa len(sys.argv)>0 na sys.argv[0] != '':
            basedir = os.path.split(sys.argv[0])[0]
        isipokua:
            basedir = os.curdir
    isipokua:
        ikiwa hasattr(module, '__path__'):
            kila directory kwenye module.__path__:
                fullpath = os.path.join(directory, test_path)
                ikiwa os.path.exists(fullpath):
                    rudisha fullpath

        # A module w/o __file__ (this includes builtins)
        ashiria ValueError("Can't resolve paths relative to the module "
                         "%r (it has no __file__)"
                         % module.__name__)

    # Combine the base directory na the test path.
    rudisha os.path.join(basedir, test_path)

######################################################################
## 2. Example & DocTest
######################################################################
## - An "example" ni a <source, want> pair, where "source" ni a
##   fragment of source code, na "want" ni the expected output for
##   "source."  The Example kundi also includes information about
##   where the example was extracted from.
##
## - A "doctest" ni a collection of examples, typically extracted from
##   a string (such kama an object's docstring).  The DocTest kundi also
##   includes information about where the string was extracted from.

kundi Example:
    """
    A single doctest example, consisting of source code na expected
    output.  `Example` defines the following attributes:

      - source: A single Python statement, always ending ukijumuisha a newline.
        The constructor adds a newline ikiwa needed.

      - want: The expected output kutoka running the source code (either
        kutoka stdout, ama a traceback kwenye case of exception).  `want` ends
        ukijumuisha a newline unless it's empty, kwenye which case it's an empty
        string.  The constructor adds a newline ikiwa needed.

      - exc_msg: The exception message generated by the example, if
        the example ni expected to generate an exception; ama `Tupu` if
        it ni sio expected to generate an exception.  This exception
        message ni compared against the rudisha value of
        `traceback.format_exception_only()`.  `exc_msg` ends ukijumuisha a
        newline unless it's `Tupu`.  The constructor adds a newline
        ikiwa needed.

      - lineno: The line number within the DocTest string containing
        this Example where the Example begins.  This line number is
        zero-based, ukijumuisha respect to the beginning of the DocTest.

      - indent: The example's indentation kwenye the DocTest string.
        I.e., the number of space characters that precede the
        example's first prompt.

      - options: A dictionary mapping kutoka option flags to Kweli ama
        Uongo, which ni used to override default options kila this
        example.  Any option flags sio contained kwenye this dictionary
        are left at their default value (as specified by the
        DocTestRunner's optionflags).  By default, no options are set.
    """
    eleza __init__(self, source, want, exc_msg=Tupu, lineno=0, indent=0,
                 options=Tupu):
        # Normalize inputs.
        ikiwa sio source.endswith('\n'):
            source += '\n'
        ikiwa want na sio want.endswith('\n'):
            want += '\n'
        ikiwa exc_msg ni sio Tupu na sio exc_msg.endswith('\n'):
            exc_msg += '\n'
        # Store properties.
        self.source = source
        self.want = want
        self.lineno = lineno
        self.indent = indent
        ikiwa options ni Tupu: options = {}
        self.options = options
        self.exc_msg = exc_msg

    eleza __eq__(self, other):
        ikiwa type(self) ni sio type(other):
            rudisha NotImplemented

        rudisha self.source == other.source na \
               self.want == other.want na \
               self.lineno == other.lineno na \
               self.indent == other.indent na \
               self.options == other.options na \
               self.exc_msg == other.exc_msg

    eleza __hash__(self):
        rudisha hash((self.source, self.want, self.lineno, self.indent,
                     self.exc_msg))

kundi DocTest:
    """
    A collection of doctest examples that should be run kwenye a single
    namespace.  Each `DocTest` defines the following attributes:

      - examples: the list of examples.

      - globs: The namespace (aka globals) that the examples should
        be run in.

      - name: A name identifying the DocTest (typically, the name of
        the object whose docstring this DocTest was extracted from).

      - filename: The name of the file that this DocTest was extracted
        from, ama `Tupu` ikiwa the filename ni unknown.

      - lineno: The line number within filename where this DocTest
        begins, ama `Tupu` ikiwa the line number ni unavailable.  This
        line number ni zero-based, ukijumuisha respect to the beginning of
        the file.

      - docstring: The string that the examples were extracted from,
        ama `Tupu` ikiwa the string ni unavailable.
    """
    eleza __init__(self, examples, globs, name, filename, lineno, docstring):
        """
        Create a new DocTest containing the given examples.  The
        DocTest's globals are initialized ukijumuisha a copy of `globs`.
        """
        assert sio isinstance(examples, str), \
               "DocTest no longer accepts str; use DocTestParser instead"
        self.examples = examples
        self.docstring = docstring
        self.globs = globs.copy()
        self.name = name
        self.filename = filename
        self.lineno = lineno

    eleza __repr__(self):
        ikiwa len(self.examples) == 0:
            examples = 'no examples'
        lasivyo len(self.examples) == 1:
            examples = '1 example'
        isipokua:
            examples = '%d examples' % len(self.examples)
        rudisha ('<%s %s kutoka %s:%s (%s)>' %
                (self.__class__.__name__,
                 self.name, self.filename, self.lineno, examples))

    eleza __eq__(self, other):
        ikiwa type(self) ni sio type(other):
            rudisha NotImplemented

        rudisha self.examples == other.examples na \
               self.docstring == other.docstring na \
               self.globs == other.globs na \
               self.name == other.name na \
               self.filename == other.filename na \
               self.lineno == other.lineno

    eleza __hash__(self):
        rudisha hash((self.docstring, self.name, self.filename, self.lineno))

    # This lets us sort tests by name:
    eleza __lt__(self, other):
        ikiwa sio isinstance(other, DocTest):
            rudisha NotImplemented
        rudisha ((self.name, self.filename, self.lineno, id(self))
                <
                (other.name, other.filename, other.lineno, id(other)))

######################################################################
## 3. DocTestParser
######################################################################

kundi DocTestParser:
    """
    A kundi used to parse strings containing doctest examples.
    """
    # This regular expression ni used to find doctest examples kwenye a
    # string.  It defines three groups: `source` ni the source code
    # (including leading indentation na prompts); `indent` ni the
    # indentation of the first (PS1) line of the source code; na
    # `want` ni the expected output (including leading indentation).
    _EXAMPLE_RE = re.compile(r'''
        # Source consists of a PS1 line followed by zero ama more PS2 lines.
        (?P<source>
            (?:^(?P<indent> [ ]*) >>>    .*)    # PS1 line
            (?:\n           [ ]*  \.\.\. .*)*)  # PS2 lines
        \n?
        # Want consists of any non-blank lines that do sio start ukijumuisha PS1.
        (?P<want> (?:(?![ ]*$)    # Not a blank line
                     (?![ ]*>>>)  # Not a line starting ukijumuisha PS1
                     .+$\n?       # But any other line
                  )*)
        ''', re.MULTILINE | re.VERBOSE)

    # A regular expression kila handling `want` strings that contain
    # expected exceptions.  It divides `want` into three pieces:
    #    - the traceback header line (`hdr`)
    #    - the traceback stack (`stack`)
    #    - the exception message (`msg`), kama generated by
    #      traceback.format_exception_only()
    # `msg` may have multiple lines.  We assume/require that the
    # exception message ni the first non-indented line starting ukijumuisha a word
    # character following the traceback header line.
    _EXCEPTION_RE = re.compile(r"""
        # Grab the traceback header.  Different versions of Python have
        # said different things on the first traceback line.
        ^(?P<hdr> Traceback\ \(
            (?: most\ recent\ call\ last
            |   innermost\ last
            ) \) :
        )
        \s* $                # toss trailing whitespace on the header.
        (?P<stack> .*?)      # don't blink: absorb stuff until...
        ^ (?P<msg> \w+ .*)   #     a line *starts* ukijumuisha alphanum.
        """, re.VERBOSE | re.MULTILINE | re.DOTALL)

    # A callable returning a true value iff its argument ni a blank line
    # ama contains a single comment.
    _IS_BLANK_OR_COMMENT = re.compile(r'^[ ]*(#.*)?$').match

    eleza parse(self, string, name='<string>'):
        """
        Divide the given string into examples na intervening text,
        na rudisha them kama a list of alternating Examples na strings.
        Line numbers kila the Examples are 0-based.  The optional
        argument `name` ni a name identifying this string, na ni only
        used kila error messages.
        """
        string = string.expandtabs()
        # If all lines begin ukijumuisha the same indentation, then strip it.
        min_indent = self._min_indent(string)
        ikiwa min_indent > 0:
            string = '\n'.join([l[min_indent:] kila l kwenye string.split('\n')])

        output = []
        charno, lineno = 0, 0
        # Find all doctest examples kwenye the string:
        kila m kwenye self._EXAMPLE_RE.finditer(string):
            # Add the pre-example text to `output`.
            output.append(string[charno:m.start()])
            # Update lineno (lines before this example)
            lineno += string.count('\n', charno, m.start())
            # Extract info kutoka the regexp match.
            (source, options, want, exc_msg) = \
                     self._parse_example(m, name, lineno)
            # Create an Example, na add it to the list.
            ikiwa sio self._IS_BLANK_OR_COMMENT(source):
                output.append( Example(source, want, exc_msg,
                                    lineno=lineno,
                                    indent=min_indent+len(m.group('indent')),
                                    options=options) )
            # Update lineno (lines inside this example)
            lineno += string.count('\n', m.start(), m.end())
            # Update charno.
            charno = m.end()
        # Add any remaining post-example text to `output`.
        output.append(string[charno:])
        rudisha output

    eleza get_doctest(self, string, globs, name, filename, lineno):
        """
        Extract all doctest examples kutoka the given string, na
        collect them into a `DocTest` object.

        `globs`, `name`, `filename`, na `lineno` are attributes for
        the new `DocTest` object.  See the documentation kila `DocTest`
        kila more information.
        """
        rudisha DocTest(self.get_examples(string, name), globs,
                       name, filename, lineno, string)

    eleza get_examples(self, string, name='<string>'):
        """
        Extract all doctest examples kutoka the given string, na rudisha
        them kama a list of `Example` objects.  Line numbers are
        0-based, because it's most common kwenye doctests that nothing
        interesting appears on the same line kama opening triple-quote,
        na so the first interesting line ni called \"line 1\" then.

        The optional argument `name` ni a name identifying this
        string, na ni only used kila error messages.
        """
        rudisha [x kila x kwenye self.parse(string, name)
                ikiwa isinstance(x, Example)]

    eleza _parse_example(self, m, name, lineno):
        """
        Given a regular expression match kutoka `_EXAMPLE_RE` (`m`),
        rudisha a pair `(source, want)`, where `source` ni the matched
        example's source code (ukijumuisha prompts na indentation stripped);
        na `want` ni the example's expected output (ukijumuisha indentation
        stripped).

        `name` ni the string's name, na `lineno` ni the line number
        where the example starts; both are used kila error messages.
        """
        # Get the example's indentation level.
        indent = len(m.group('indent'))

        # Divide source into lines; check that they're properly
        # indented; na then strip their indentation & prompts.
        source_lines = m.group('source').split('\n')
        self._check_prompt_blank(source_lines, indent, name, lineno)
        self._check_prefix(source_lines[1:], ' '*indent + '.', name, lineno)
        source = '\n'.join([sl[indent+4:] kila sl kwenye source_lines])

        # Divide want into lines; check that it's properly indented; na
        # then strip the indentation.  Spaces before the last newline should
        # be preserved, so plain rstrip() isn't good enough.
        want = m.group('want')
        want_lines = want.split('\n')
        ikiwa len(want_lines) > 1 na re.match(r' *$', want_lines[-1]):
            toa want_lines[-1]  # forget final newline & spaces after it
        self._check_prefix(want_lines, ' '*indent, name,
                           lineno + len(source_lines))
        want = '\n'.join([wl[indent:] kila wl kwenye want_lines])

        # If `want` contains a traceback message, then extract it.
        m = self._EXCEPTION_RE.match(want)
        ikiwa m:
            exc_msg = m.group('msg')
        isipokua:
            exc_msg = Tupu

        # Extract options kutoka the source.
        options = self._find_options(source, name, lineno)

        rudisha source, options, want, exc_msg

    # This regular expression looks kila option directives kwenye the
    # source code of an example.  Option directives are comments
    # starting ukijumuisha "doctest:".  Warning: this may give false
    # positives kila string-literals that contain the string
    # "#doctest:".  Eliminating these false positives would require
    # actually parsing the string; but we limit them by ignoring any
    # line containing "#doctest:" that ni *followed* by a quote mark.
    _OPTION_DIRECTIVE_RE = re.compile(r'#\s*doctest:\s*([^\n\'"]*)$',
                                      re.MULTILINE)

    eleza _find_options(self, source, name, lineno):
        """
        Return a dictionary containing option overrides extracted from
        option directives kwenye the given source string.

        `name` ni the string's name, na `lineno` ni the line number
        where the example starts; both are used kila error messages.
        """
        options = {}
        # (note: ukijumuisha the current regexp, this will match at most once:)
        kila m kwenye self._OPTION_DIRECTIVE_RE.finditer(source):
            option_strings = m.group(1).replace(',', ' ').split()
            kila option kwenye option_strings:
                ikiwa (option[0] haiko kwenye '+-' ama
                    option[1:] haiko kwenye OPTIONFLAGS_BY_NAME):
                    ashiria ValueError('line %r of the doctest kila %s '
                                     'has an invalid option: %r' %
                                     (lineno+1, name, option))
                flag = OPTIONFLAGS_BY_NAME[option[1:]]
                options[flag] = (option[0] == '+')
        ikiwa options na self._IS_BLANK_OR_COMMENT(source):
            ashiria ValueError('line %r of the doctest kila %s has an option '
                             'directive on a line ukijumuisha no example: %r' %
                             (lineno, name, source))
        rudisha options

    # This regular expression finds the indentation of every non-blank
    # line kwenye a string.
    _INDENT_RE = re.compile(r'^([ ]*)(?=\S)', re.MULTILINE)

    eleza _min_indent(self, s):
        "Return the minimum indentation of any non-blank line kwenye `s`"
        indents = [len(indent) kila indent kwenye self._INDENT_RE.findall(s)]
        ikiwa len(indents) > 0:
            rudisha min(indents)
        isipokua:
            rudisha 0

    eleza _check_prompt_blank(self, lines, indent, name, lineno):
        """
        Given the lines of a source string (including prompts na
        leading indentation), check to make sure that every prompt is
        followed by a space character.  If any line ni sio followed by
        a space character, then ashiria ValueError.
        """
        kila i, line kwenye enumerate(lines):
            ikiwa len(line) >= indent+4 na line[indent+3] != ' ':
                ashiria ValueError('line %r of the docstring kila %s '
                                 'lacks blank after %s: %r' %
                                 (lineno+i+1, name,
                                  line[indent:indent+3], line))

    eleza _check_prefix(self, lines, prefix, name, lineno):
        """
        Check that every line kwenye the given list starts ukijumuisha the given
        prefix; ikiwa any line does not, then ashiria a ValueError.
        """
        kila i, line kwenye enumerate(lines):
            ikiwa line na sio line.startswith(prefix):
                ashiria ValueError('line %r of the docstring kila %s has '
                                 'inconsistent leading whitespace: %r' %
                                 (lineno+i+1, name, line))


######################################################################
## 4. DocTest Finder
######################################################################

kundi DocTestFinder:
    """
    A kundi used to extract the DocTests that are relevant to a given
    object, kutoka its docstring na the docstrings of its contained
    objects.  Doctests can currently be extracted kutoka the following
    object types: modules, functions, classes, methods, staticmethods,
    classmethods, na properties.
    """

    eleza __init__(self, verbose=Uongo, parser=DocTestParser(),
                 recurse=Kweli, exclude_empty=Kweli):
        """
        Create a new doctest finder.

        The optional argument `parser` specifies a kundi ama
        function that should be used to create new DocTest objects (or
        objects that implement the same interface kama DocTest).  The
        signature kila this factory function should match the signature
        of the DocTest constructor.

        If the optional argument `recurse` ni false, then `find` will
        only examine the given object, na sio any contained objects.

        If the optional argument `exclude_empty` ni false, then `find`
        will include tests kila objects ukijumuisha empty docstrings.
        """
        self._parser = parser
        self._verbose = verbose
        self._recurse = recurse
        self._exclude_empty = exclude_empty

    eleza find(self, obj, name=Tupu, module=Tupu, globs=Tupu, extraglobs=Tupu):
        """
        Return a list of the DocTests that are defined by the given
        object's docstring, ama by any of its contained objects'
        docstrings.

        The optional parameter `module` ni the module that contains
        the given object.  If the module ni sio specified ama ni Tupu, then
        the test finder will attempt to automatically determine the
        correct module.  The object's module ni used:

            - As a default namespace, ikiwa `globs` ni sio specified.
            - To prevent the DocTestFinder kutoka extracting DocTests
              kutoka objects that are imported kutoka other modules.
            - To find the name of the file containing the object.
            - To help find the line number of the object within its
              file.

        Contained objects whose module does sio match `module` are ignored.

        If `module` ni Uongo, no attempt to find the module will be made.
        This ni obscure, of use mostly kwenye tests:  ikiwa `module` ni Uongo, ama
        ni Tupu but cansio be found automatically, then all objects are
        considered to belong to the (non-existent) module, so all contained
        objects will (recursively) be searched kila doctests.

        The globals kila each DocTest ni formed by combining `globs`
        na `extraglobs` (bindings kwenye `extraglobs` override bindings
        kwenye `globs`).  A new copy of the globals dictionary ni created
        kila each DocTest.  If `globs` ni sio specified, then it
        defaults to the module's `__dict__`, ikiwa specified, ama {}
        otherwise.  If `extraglobs` ni sio specified, then it defaults
        to {}.

        """
        # If name was sio specified, then extract it kutoka the object.
        ikiwa name ni Tupu:
            name = getattr(obj, '__name__', Tupu)
            ikiwa name ni Tupu:
                ashiria ValueError("DocTestFinder.find: name must be given "
                        "when obj.__name__ doesn't exist: %r" %
                                 (type(obj),))

        # Find the module that contains the given object (ikiwa obj is
        # a module, then module=obj.).  Note: this may fail, kwenye which
        # case module will be Tupu.
        ikiwa module ni Uongo:
            module = Tupu
        lasivyo module ni Tupu:
            module = inspect.getmodule(obj)

        # Read the module's source code.  This ni used by
        # DocTestFinder._find_lineno to find the line number kila a
        # given object's docstring.
        jaribu:
            file = inspect.getsourcefile(obj)
        tatizo TypeError:
            source_lines = Tupu
        isipokua:
            ikiwa sio file:
                # Check to see ikiwa it's one of our special internal "files"
                # (see __patched_linecache_getlines).
                file = inspect.getfile(obj)
                ikiwa sio file[0]+file[-2:] == '<]>': file = Tupu
            ikiwa file ni Tupu:
                source_lines = Tupu
            isipokua:
                ikiwa module ni sio Tupu:
                    # Supply the module globals kwenye case the module was
                    # originally loaded via a PEP 302 loader na
                    # file ni sio a valid filesystem path
                    source_lines = linecache.getlines(file, module.__dict__)
                isipokua:
                    # No access to a loader, so assume it's a normal
                    # filesystem path
                    source_lines = linecache.getlines(file)
                ikiwa sio source_lines:
                    source_lines = Tupu

        # Initialize globals, na merge kwenye extraglobs.
        ikiwa globs ni Tupu:
            ikiwa module ni Tupu:
                globs = {}
            isipokua:
                globs = module.__dict__.copy()
        isipokua:
            globs = globs.copy()
        ikiwa extraglobs ni sio Tupu:
            globs.update(extraglobs)
        ikiwa '__name__' haiko kwenye globs:
            globs['__name__'] = '__main__'  # provide a default module name

        # Recursively explore `obj`, extracting DocTests.
        tests = []
        self._find(tests, obj, name, module, source_lines, globs, {})
        # Sort the tests by alpha order of names, kila consistency kwenye
        # verbose-mode output.  This was a feature of doctest kwenye Pythons
        # <= 2.3 that got lost by accident kwenye 2.4.  It was repaired kwenye
        # 2.4.4 na 2.5.
        tests.sort()
        rudisha tests

    eleza _from_module(self, module, object):
        """
        Return true ikiwa the given object ni defined kwenye the given
        module.
        """
        ikiwa module ni Tupu:
            rudisha Kweli
        lasivyo inspect.getmodule(object) ni sio Tupu:
            rudisha module ni inspect.getmodule(object)
        lasivyo inspect.isfunction(object):
            rudisha module.__dict__ ni object.__globals__
        lasivyo inspect.ismethoddescriptor(object):
            ikiwa hasattr(object, '__objclass__'):
                obj_mod = object.__objclass__.__module__
            lasivyo hasattr(object, '__module__'):
                obj_mod = object.__module__
            isipokua:
                rudisha Kweli # [XX] no easy way to tell otherwise
            rudisha module.__name__ == obj_mod
        lasivyo inspect.isclass(object):
            rudisha module.__name__ == object.__module__
        lasivyo hasattr(object, '__module__'):
            rudisha module.__name__ == object.__module__
        lasivyo isinstance(object, property):
            rudisha Kweli # [XX] no way sio be sure.
        isipokua:
            ashiria ValueError("object must be a kundi ama function")

    eleza _find(self, tests, obj, name, module, source_lines, globs, seen):
        """
        Find tests kila the given object na any contained objects, na
        add them to `tests`.
        """
        ikiwa self._verbose:
            andika('Finding tests kwenye %s' % name)

        # If we've already processed this object, then ignore it.
        ikiwa id(obj) kwenye seen:
            rudisha
        seen[id(obj)] = 1

        # Find a test kila this object, na add it to the list of tests.
        test = self._get_test(obj, name, module, globs, source_lines)
        ikiwa test ni sio Tupu:
            tests.append(test)

        # Look kila tests kwenye a module's contained objects.
        ikiwa inspect.ismodule(obj) na self._recurse:
            kila valname, val kwenye obj.__dict__.items():
                valname = '%s.%s' % (name, valname)
                # Recurse to functions & classes.
                ikiwa ((inspect.isroutine(inspect.unwrap(val))
                     ama inspect.isclass(val)) na
                    self._from_module(module, val)):
                    self._find(tests, val, valname, module, source_lines,
                               globs, seen)

        # Look kila tests kwenye a module's __test__ dictionary.
        ikiwa inspect.ismodule(obj) na self._recurse:
            kila valname, val kwenye getattr(obj, '__test__', {}).items():
                ikiwa sio isinstance(valname, str):
                    ashiria ValueError("DocTestFinder.find: __test__ keys "
                                     "must be strings: %r" %
                                     (type(valname),))
                ikiwa sio (inspect.isroutine(val) ama inspect.isclass(val) ama
                        inspect.ismodule(val) ama isinstance(val, str)):
                    ashiria ValueError("DocTestFinder.find: __test__ values "
                                     "must be strings, functions, methods, "
                                     "classes, ama modules: %r" %
                                     (type(val),))
                valname = '%s.__test__.%s' % (name, valname)
                self._find(tests, val, valname, module, source_lines,
                           globs, seen)

        # Look kila tests kwenye a class's contained objects.
        ikiwa inspect.isclass(obj) na self._recurse:
            kila valname, val kwenye obj.__dict__.items():
                # Special handling kila staticmethod/classmethod.
                ikiwa isinstance(val, staticmethod):
                    val = getattr(obj, valname)
                ikiwa isinstance(val, classmethod):
                    val = getattr(obj, valname).__func__

                # Recurse to methods, properties, na nested classes.
                ikiwa ((inspect.isroutine(val) ama inspect.isclass(val) ama
                      isinstance(val, property)) na
                      self._from_module(module, val)):
                    valname = '%s.%s' % (name, valname)
                    self._find(tests, val, valname, module, source_lines,
                               globs, seen)

    eleza _get_test(self, obj, name, module, globs, source_lines):
        """
        Return a DocTest kila the given object, ikiwa it defines a docstring;
        otherwise, rudisha Tupu.
        """
        # Extract the object's docstring.  If it doesn't have one,
        # then rudisha Tupu (no test kila this object).
        ikiwa isinstance(obj, str):
            docstring = obj
        isipokua:
            jaribu:
                ikiwa obj.__doc__ ni Tupu:
                    docstring = ''
                isipokua:
                    docstring = obj.__doc__
                    ikiwa sio isinstance(docstring, str):
                        docstring = str(docstring)
            tatizo (TypeError, AttributeError):
                docstring = ''

        # Find the docstring's location kwenye the file.
        lineno = self._find_lineno(obj, source_lines)

        # Don't bother ikiwa the docstring ni empty.
        ikiwa self._exclude_empty na sio docstring:
            rudisha Tupu

        # Return a DocTest kila this object.
        ikiwa module ni Tupu:
            filename = Tupu
        isipokua:
            filename = getattr(module, '__file__', module.__name__)
            ikiwa filename[-4:] == ".pyc":
                filename = filename[:-1]
        rudisha self._parser.get_doctest(docstring, globs, name,
                                        filename, lineno)

    eleza _find_lineno(self, obj, source_lines):
        """
        Return a line number of the given object's docstring.  Note:
        this method assumes that the object has a docstring.
        """
        lineno = Tupu

        # Find the line number kila modules.
        ikiwa inspect.ismodule(obj):
            lineno = 0

        # Find the line number kila classes.
        # Note: this could be fooled ikiwa a kundi ni defined multiple
        # times kwenye a single file.
        ikiwa inspect.isclass(obj):
            ikiwa source_lines ni Tupu:
                rudisha Tupu
            pat = re.compile(r'^\s*class\s*%s\b' %
                             getattr(obj, '__name__', '-'))
            kila i, line kwenye enumerate(source_lines):
                ikiwa pat.match(line):
                    lineno = i
                    koma

        # Find the line number kila functions & methods.
        ikiwa inspect.ismethod(obj): obj = obj.__func__
        ikiwa inspect.isfunction(obj): obj = obj.__code__
        ikiwa inspect.istraceback(obj): obj = obj.tb_frame
        ikiwa inspect.isframe(obj): obj = obj.f_code
        ikiwa inspect.iscode(obj):
            lineno = getattr(obj, 'co_firstlineno', Tupu)-1

        # Find the line number where the docstring starts.  Assume
        # that it's the first line that begins ukijumuisha a quote mark.
        # Note: this could be fooled by a multiline function
        # signature, where a continuation line begins ukijumuisha a quote
        # mark.
        ikiwa lineno ni sio Tupu:
            ikiwa source_lines ni Tupu:
                rudisha lineno+1
            pat = re.compile(r'(^|.*:)\s*\w*("|\')')
            kila lineno kwenye range(lineno, len(source_lines)):
                ikiwa pat.match(source_lines[lineno]):
                    rudisha lineno

        # We couldn't find the line number.
        rudisha Tupu

######################################################################
## 5. DocTest Runner
######################################################################

kundi DocTestRunner:
    """
    A kundi used to run DocTest test cases, na accumulate statistics.
    The `run` method ni used to process a single DocTest case.  It
    returns a tuple `(f, t)`, where `t` ni the number of test cases
    tried, na `f` ni the number of test cases that failed.

        >>> tests = DocTestFinder().find(_TestClass)
        >>> runner = DocTestRunner(verbose=Uongo)
        >>> tests.sort(key = lambda test: test.name)
        >>> kila test kwenye tests:
        ...     andika(test.name, '->', runner.run(test))
        _TestClass -> TestResults(failed=0, attempted=2)
        _TestClass.__init__ -> TestResults(failed=0, attempted=2)
        _TestClass.get -> TestResults(failed=0, attempted=2)
        _TestClass.square -> TestResults(failed=0, attempted=1)

    The `summarize` method prints a summary of all the test cases that
    have been run by the runner, na returns an aggregated `(f, t)`
    tuple:

        >>> runner.summarize(verbose=1)
        4 items pitaed all tests:
           2 tests kwenye _TestClass
           2 tests kwenye _TestClass.__init__
           2 tests kwenye _TestClass.get
           1 tests kwenye _TestClass.square
        7 tests kwenye 4 items.
        7 pitaed na 0 failed.
        Test pitaed.
        TestResults(failed=0, attempted=7)

    The aggregated number of tried examples na failed examples is
    also available via the `tries` na `failures` attributes:

        >>> runner.tries
        7
        >>> runner.failures
        0

    The comparison between expected outputs na actual outputs ni done
    by an `OutputChecker`.  This comparison may be customized ukijumuisha a
    number of option flags; see the documentation kila `testmod` for
    more information.  If the option flags are insufficient, then the
    comparison may also be customized by pitaing a subkundi of
    `OutputChecker` to the constructor.

    The test runner's display output can be controlled kwenye two ways.
    First, an output function (`out) can be pitaed to
    `TestRunner.run`; this function will be called ukijumuisha strings that
    should be displayed.  It defaults to `sys.stdout.write`.  If
    capturing the output ni sio sufficient, then the display output
    can be also customized by subclassing DocTestRunner, na
    overriding the methods `report_start`, `report_success`,
    `report_unexpected_exception`, na `report_failure`.
    """
    # This divider string ni used to separate failure messages, na to
    # separate sections of the summary.
    DIVIDER = "*" * 70

    eleza __init__(self, checker=Tupu, verbose=Tupu, optionflags=0):
        """
        Create a new test runner.

        Optional keyword arg `checker` ni the `OutputChecker` that
        should be used to compare the expected outputs na actual
        outputs of doctest examples.

        Optional keyword arg 'verbose' prints lots of stuff ikiwa true,
        only failures ikiwa false; by default, it's true iff '-v' ni kwenye
        sys.argv.

        Optional argument `optionflags` can be used to control how the
        test runner compares expected output to actual output, na how
        it displays failures.  See the documentation kila `testmod` for
        more information.
        """
        self._checker = checker ama OutputChecker()
        ikiwa verbose ni Tupu:
            verbose = '-v' kwenye sys.argv
        self._verbose = verbose
        self.optionflags = optionflags
        self.original_optionflags = optionflags

        # Keep track of the examples we've run.
        self.tries = 0
        self.failures = 0
        self._name2ft = {}

        # Create a fake output target kila capturing doctest output.
        self._fakeout = _SpoofOut()

    #/////////////////////////////////////////////////////////////////
    # Reporting methods
    #/////////////////////////////////////////////////////////////////

    eleza report_start(self, out, test, example):
        """
        Report that the test runner ni about to process the given
        example.  (Only displays a message ikiwa verbose=Kweli)
        """
        ikiwa self._verbose:
            ikiwa example.want:
                out('Trying:\n' + _indent(example.source) +
                    'Expecting:\n' + _indent(example.want))
            isipokua:
                out('Trying:\n' + _indent(example.source) +
                    'Expecting nothing\n')

    eleza report_success(self, out, test, example, got):
        """
        Report that the given example ran successfully.  (Only
        displays a message ikiwa verbose=Kweli)
        """
        ikiwa self._verbose:
            out("ok\n")

    eleza report_failure(self, out, test, example, got):
        """
        Report that the given example failed.
        """
        out(self._failure_header(test, example) +
            self._checker.output_difference(example, got, self.optionflags))

    eleza report_unexpected_exception(self, out, test, example, exc_info):
        """
        Report that the given example raised an unexpected exception.
        """
        out(self._failure_header(test, example) +
            'Exception raised:\n' + _indent(_exception_traceback(exc_info)))

    eleza _failure_header(self, test, example):
        out = [self.DIVIDER]
        ikiwa test.filename:
            ikiwa test.lineno ni sio Tupu na example.lineno ni sio Tupu:
                lineno = test.lineno + example.lineno + 1
            isipokua:
                lineno = '?'
            out.append('File "%s", line %s, kwenye %s' %
                       (test.filename, lineno, test.name))
        isipokua:
            out.append('Line %s, kwenye %s' % (example.lineno+1, test.name))
        out.append('Failed example:')
        source = example.source
        out.append(_indent(source))
        rudisha '\n'.join(out)

    #/////////////////////////////////////////////////////////////////
    # DocTest Running
    #/////////////////////////////////////////////////////////////////

    eleza __run(self, test, compileflags, out):
        """
        Run the examples kwenye `test`.  Write the outcome of each example
        ukijumuisha one of the `DocTestRunner.report_*` methods, using the
        writer function `out`.  `compileflags` ni the set of compiler
        flags that should be used to execute examples.  Return a tuple
        `(f, t)`, where `t` ni the number of examples tried, na `f`
        ni the number of examples that failed.  The examples are run
        kwenye the namespace `test.globs`.
        """
        # Keep track of the number of failures na tries.
        failures = tries = 0

        # Save the option flags (since option directives can be used
        # to modify them).
        original_optionflags = self.optionflags

        SUCCESS, FAILURE, BOOM = range(3) # `outcome` state

        check = self._checker.check_output

        # Process each example.
        kila examplenum, example kwenye enumerate(test.examples):

            # If REPORT_ONLY_FIRST_FAILURE ni set, then suppress
            # reporting after the first failure.
            quiet = (self.optionflags & REPORT_ONLY_FIRST_FAILURE na
                     failures > 0)

            # Merge kwenye the example's options.
            self.optionflags = original_optionflags
            ikiwa example.options:
                kila (optionflag, val) kwenye example.options.items():
                    ikiwa val:
                        self.optionflags |= optionflag
                    isipokua:
                        self.optionflags &= ~optionflag

            # If 'SKIP' ni set, then skip this example.
            ikiwa self.optionflags & SKIP:
                endelea

            # Record that we started this example.
            tries += 1
            ikiwa sio quiet:
                self.report_start(out, test, example)

            # Use a special filename kila compile(), so we can retrieve
            # the source code during interactive debugging (see
            # __patched_linecache_getlines).
            filename = '<doctest %s[%d]>' % (test.name, examplenum)

            # Run the example kwenye the given context (globs), na record
            # any exception that gets raised.  (But don't intercept
            # keyboard interrupts.)
            jaribu:
                # Don't blink!  This ni where the user's code gets run.
                exec(compile(example.source, filename, "single",
                             compileflags, 1), test.globs)
                self.debugger.set_endelea() # ==== Example Finished ====
                exception = Tupu
            tatizo KeyboardInterrupt:
                raise
            tatizo:
                exception = sys.exc_info()
                self.debugger.set_endelea() # ==== Example Finished ====

            got = self._fakeout.getvalue()  # the actual output
            self._fakeout.truncate(0)
            outcome = FAILURE   # guilty until proved innocent ama insane

            # If the example executed without raising any exceptions,
            # verify its output.
            ikiwa exception ni Tupu:
                ikiwa check(example.want, got, self.optionflags):
                    outcome = SUCCESS

            # The example raised an exception:  check ikiwa it was expected.
            isipokua:
                exc_msg = traceback.format_exception_only(*exception[:2])[-1]
                ikiwa sio quiet:
                    got += _exception_traceback(exception)

                # If `example.exc_msg` ni Tupu, then we weren't expecting
                # an exception.
                ikiwa example.exc_msg ni Tupu:
                    outcome = BOOM

                # We expected an exception:  see whether it matches.
                lasivyo check(example.exc_msg, exc_msg, self.optionflags):
                    outcome = SUCCESS

                # Another chance ikiwa they didn't care about the detail.
                lasivyo self.optionflags & IGNORE_EXCEPTION_DETAIL:
                    ikiwa check(_strip_exception_details(example.exc_msg),
                             _strip_exception_details(exc_msg),
                             self.optionflags):
                        outcome = SUCCESS

            # Report the outcome.
            ikiwa outcome ni SUCCESS:
                ikiwa sio quiet:
                    self.report_success(out, test, example, got)
            lasivyo outcome ni FAILURE:
                ikiwa sio quiet:
                    self.report_failure(out, test, example, got)
                failures += 1
            lasivyo outcome ni BOOM:
                ikiwa sio quiet:
                    self.report_unexpected_exception(out, test, example,
                                                     exception)
                failures += 1
            isipokua:
                assert Uongo, ("unknown outcome", outcome)

            ikiwa failures na self.optionflags & FAIL_FAST:
                koma

        # Restore the option flags (in case they were modified)
        self.optionflags = original_optionflags

        # Record na rudisha the number of failures na tries.
        self.__record_outcome(test, failures, tries)
        rudisha TestResults(failures, tries)

    eleza __record_outcome(self, test, f, t):
        """
        Record the fact that the given DocTest (`test`) generated `f`
        failures out of `t` tried examples.
        """
        f2, t2 = self._name2ft.get(test.name, (0,0))
        self._name2ft[test.name] = (f+f2, t+t2)
        self.failures += f
        self.tries += t

    __LINECACHE_FILENAME_RE = re.compile(r'<doctest '
                                         r'(?P<name>.+)'
                                         r'\[(?P<examplenum>\d+)\]>$')
    eleza __patched_linecache_getlines(self, filename, module_globals=Tupu):
        m = self.__LINECACHE_FILENAME_RE.match(filename)
        ikiwa m na m.group('name') == self.test.name:
            example = self.test.examples[int(m.group('examplenum'))]
            rudisha example.source.splitlines(keepends=Kweli)
        isipokua:
            rudisha self.save_linecache_getlines(filename, module_globals)

    eleza run(self, test, compileflags=Tupu, out=Tupu, clear_globs=Kweli):
        """
        Run the examples kwenye `test`, na display the results using the
        writer function `out`.

        The examples are run kwenye the namespace `test.globs`.  If
        `clear_globs` ni true (the default), then this namespace will
        be cleared after the test runs, to help ukijumuisha garbage
        collection.  If you would like to examine the namespace after
        the test completes, then use `clear_globs=Uongo`.

        `compileflags` gives the set of flags that should be used by
        the Python compiler when running the examples.  If sio
        specified, then it will default to the set of future-import
        flags that apply to `globs`.

        The output of each example ni checked using
        `DocTestRunner.check_output`, na the results are formatted by
        the `DocTestRunner.report_*` methods.
        """
        self.test = test

        ikiwa compileflags ni Tupu:
            compileflags = _extract_future_flags(test.globs)

        save_stdout = sys.stdout
        ikiwa out ni Tupu:
            encoding = save_stdout.encoding
            ikiwa encoding ni Tupu ama encoding.lower() == 'utf-8':
                out = save_stdout.write
            isipokua:
                # Use backslashreplace error handling on write
                eleza out(s):
                    s = str(s.encode(encoding, 'backslashreplace'), encoding)
                    save_stdout.write(s)
        sys.stdout = self._fakeout

        # Patch pdb.set_trace to restore sys.stdout during interactive
        # debugging (so it's sio still redirected to self._fakeout).
        # Note that the interactive output will go to *our*
        # save_stdout, even ikiwa that's sio the real sys.stdout; this
        # allows us to write test cases kila the set_trace behavior.
        save_trace = sys.gettrace()
        save_set_trace = pdb.set_trace
        self.debugger = _OutputRedirectingPdb(save_stdout)
        self.debugger.reset()
        pdb.set_trace = self.debugger.set_trace

        # Patch linecache.getlines, so we can see the example's source
        # when we're inside the debugger.
        self.save_linecache_getlines = linecache.getlines
        linecache.getlines = self.__patched_linecache_getlines

        # Make sure sys.displayhook just prints the value to stdout
        save_displayhook = sys.displayhook
        sys.displayhook = sys.__displayhook__

        jaribu:
            rudisha self.__run(test, compileflags, out)
        mwishowe:
            sys.stdout = save_stdout
            pdb.set_trace = save_set_trace
            sys.settrace(save_trace)
            linecache.getlines = self.save_linecache_getlines
            sys.displayhook = save_displayhook
            ikiwa clear_globs:
                test.globs.clear()
                agiza builtins
                builtins._ = Tupu

    #/////////////////////////////////////////////////////////////////
    # Summarization
    #/////////////////////////////////////////////////////////////////
    eleza summarize(self, verbose=Tupu):
        """
        Print a summary of all the test cases that have been run by
        this DocTestRunner, na rudisha a tuple `(f, t)`, where `f` is
        the total number of failed examples, na `t` ni the total
        number of tried examples.

        The optional `verbose` argument controls how detailed the
        summary is.  If the verbosity ni sio specified, then the
        DocTestRunner's verbosity ni used.
        """
        ikiwa verbose ni Tupu:
            verbose = self._verbose
        notests = []
        pitaed = []
        failed = []
        totalt = totalf = 0
        kila x kwenye self._name2ft.items():
            name, (f, t) = x
            assert f <= t
            totalt += t
            totalf += f
            ikiwa t == 0:
                notests.append(name)
            lasivyo f == 0:
                pitaed.append( (name, t) )
            isipokua:
                failed.append(x)
        ikiwa verbose:
            ikiwa notests:
                andika(len(notests), "items had no tests:")
                notests.sort()
                kila thing kwenye notests:
                    andika("   ", thing)
            ikiwa pitaed:
                andika(len(pitaed), "items pitaed all tests:")
                pitaed.sort()
                kila thing, count kwenye pitaed:
                    andika(" %3d tests kwenye %s" % (count, thing))
        ikiwa failed:
            andika(self.DIVIDER)
            andika(len(failed), "items had failures:")
            failed.sort()
            kila thing, (f, t) kwenye failed:
                andika(" %3d of %3d kwenye %s" % (f, t, thing))
        ikiwa verbose:
            andika(totalt, "tests in", len(self._name2ft), "items.")
            andika(totalt - totalf, "pitaed and", totalf, "failed.")
        ikiwa totalf:
            andika("***Test Failed***", totalf, "failures.")
        lasivyo verbose:
            andika("Test pitaed.")
        rudisha TestResults(totalf, totalt)

    #/////////////////////////////////////////////////////////////////
    # Backward compatibility cruft to maintain doctest.master.
    #/////////////////////////////////////////////////////////////////
    eleza merge(self, other):
        d = self._name2ft
        kila name, (f, t) kwenye other._name2ft.items():
            ikiwa name kwenye d:
                # Don't andika here by default, since doing
                #     so komas some of the buildbots
                #andika("*** DocTestRunner.merge: '" + name + "' kwenye both" \
                #    " testers; summing outcomes.")
                f2, t2 = d[name]
                f = f + f2
                t = t + t2
            d[name] = f, t

kundi OutputChecker:
    """
    A kundi used to check the whether the actual output kutoka a doctest
    example matches the expected output.  `OutputChecker` defines two
    methods: `check_output`, which compares a given pair of outputs,
    na returns true ikiwa they match; na `output_difference`, which
    returns a string describing the differences between two outputs.
    """
    eleza _toAscii(self, s):
        """
        Convert string to hex-escaped ASCII string.
        """
        rudisha str(s.encode('ASCII', 'backslashreplace'), "ASCII")

    eleza check_output(self, want, got, optionflags):
        """
        Return Kweli iff the actual output kutoka an example (`got`)
        matches the expected output (`want`).  These strings are
        always considered to match ikiwa they are identical; but
        depending on what option flags the test runner ni using,
        several non-exact match types are also possible.  See the
        documentation kila `TestRunner` kila more information about
        option flags.
        """

        # If `want` contains hex-escaped character such kama "\u1234",
        # then `want` ni a string of six characters(e.g. [\,u,1,2,3,4]).
        # On the other hand, `got` could be another sequence of
        # characters such kama [\u1234], so `want` na `got` should
        # be folded to hex-escaped ASCII string to compare.
        got = self._toAscii(got)
        want = self._toAscii(want)

        # Handle the common case first, kila efficiency:
        # ikiwa they're string-identical, always rudisha true.
        ikiwa got == want:
            rudisha Kweli

        # The values Kweli na Uongo replaced 1 na 0 kama the rudisha
        # value kila boolean comparisons kwenye Python 2.3.
        ikiwa sio (optionflags & DONT_ACCEPT_TRUE_FOR_1):
            ikiwa (got,want) == ("Kweli\n", "1\n"):
                rudisha Kweli
            ikiwa (got,want) == ("Uongo\n", "0\n"):
                rudisha Kweli

        # <BLANKLINE> can be used kama a special sequence to signify a
        # blank line, unless the DONT_ACCEPT_BLANKLINE flag ni used.
        ikiwa sio (optionflags & DONT_ACCEPT_BLANKLINE):
            # Replace <BLANKLINE> kwenye want ukijumuisha a blank line.
            want = re.sub(r'(?m)^%s\s*?$' % re.escape(BLANKLINE_MARKER),
                          '', want)
            # If a line kwenye got contains only spaces, then remove the
            # spaces.
            got = re.sub(r'(?m)^[^\S\n]+$', '', got)
            ikiwa got == want:
                rudisha Kweli

        # This flag causes doctest to ignore any differences kwenye the
        # contents of whitespace strings.  Note that this can be used
        # kwenye conjunction ukijumuisha the ELLIPSIS flag.
        ikiwa optionflags & NORMALIZE_WHITESPACE:
            got = ' '.join(got.split())
            want = ' '.join(want.split())
            ikiwa got == want:
                rudisha Kweli

        # The ELLIPSIS flag says to let the sequence "..." kwenye `want`
        # match any substring kwenye `got`.
        ikiwa optionflags & ELLIPSIS:
            ikiwa _ellipsis_match(want, got):
                rudisha Kweli

        # We didn't find any match; rudisha false.
        rudisha Uongo

    # Should we do a fancy diff?
    eleza _do_a_fancy_diff(self, want, got, optionflags):
        # Not unless they asked kila a fancy diff.
        ikiwa sio optionflags & (REPORT_UDIFF |
                              REPORT_CDIFF |
                              REPORT_NDIFF):
            rudisha Uongo

        # If expected output uses ellipsis, a meaningful fancy diff is
        # too hard ... ama maybe not.  In two real-life failures Tim saw,
        # a diff was a major help anyway, so this ni commented out.
        # [todo] _ellipsis_match() knows which pieces do na don't match,
        # na could be the basis kila a kick-ass diff kwenye this case.
        ##ikiwa optionflags & ELLIPSIS na ELLIPSIS_MARKER kwenye want:
        ##    rudisha Uongo

        # ndiff does intraline difference marking, so can be useful even
        # kila 1-line differences.
        ikiwa optionflags & REPORT_NDIFF:
            rudisha Kweli

        # The other diff types need at least a few lines to be helpful.
        rudisha want.count('\n') > 2 na got.count('\n') > 2

    eleza output_difference(self, example, got, optionflags):
        """
        Return a string describing the differences between the
        expected output kila a given example (`example`) na the actual
        output (`got`).  `optionflags` ni the set of option flags used
        to compare `want` na `got`.
        """
        want = example.want
        # If <BLANKLINE>s are being used, then replace blank lines
        # ukijumuisha <BLANKLINE> kwenye the actual output string.
        ikiwa sio (optionflags & DONT_ACCEPT_BLANKLINE):
            got = re.sub('(?m)^[ ]*(?=\n)', BLANKLINE_MARKER, got)

        # Check ikiwa we should use diff.
        ikiwa self._do_a_fancy_diff(want, got, optionflags):
            # Split want & got into lines.
            want_lines = want.splitlines(keepends=Kweli)
            got_lines = got.splitlines(keepends=Kweli)
            # Use difflib to find their differences.
            ikiwa optionflags & REPORT_UDIFF:
                diff = difflib.unified_diff(want_lines, got_lines, n=2)
                diff = list(diff)[2:] # strip the diff header
                kind = 'unified diff ukijumuisha -expected +actual'
            lasivyo optionflags & REPORT_CDIFF:
                diff = difflib.context_diff(want_lines, got_lines, n=2)
                diff = list(diff)[2:] # strip the diff header
                kind = 'context diff ukijumuisha expected followed by actual'
            lasivyo optionflags & REPORT_NDIFF:
                engine = difflib.Differ(charjunk=difflib.IS_CHARACTER_JUNK)
                diff = list(engine.compare(want_lines, got_lines))
                kind = 'ndiff ukijumuisha -expected +actual'
            isipokua:
                assert 0, 'Bad diff option'
            rudisha 'Differences (%s):\n' % kind + _indent(''.join(diff))

        # If we're sio using diff, then simply list the expected
        # output followed by the actual output.
        ikiwa want na got:
            rudisha 'Expected:\n%sGot:\n%s' % (_indent(want), _indent(got))
        lasivyo want:
            rudisha 'Expected:\n%sGot nothing\n' % _indent(want)
        lasivyo got:
            rudisha 'Expected nothing\nGot:\n%s' % _indent(got)
        isipokua:
            rudisha 'Expected nothing\nGot nothing\n'

kundi DocTestFailure(Exception):
    """A DocTest example has failed kwenye debugging mode.

    The exception instance has variables:

    - test: the DocTest object being run

    - example: the Example object that failed

    - got: the actual output
    """
    eleza __init__(self, test, example, got):
        self.test = test
        self.example = example
        self.got = got

    eleza __str__(self):
        rudisha str(self.test)

kundi UnexpectedException(Exception):
    """A DocTest example has encountered an unexpected exception

    The exception instance has variables:

    - test: the DocTest object being run

    - example: the Example object that failed

    - exc_info: the exception info
    """
    eleza __init__(self, test, example, exc_info):
        self.test = test
        self.example = example
        self.exc_info = exc_info

    eleza __str__(self):
        rudisha str(self.test)

kundi DebugRunner(DocTestRunner):
    r"""Run doc tests but ashiria an exception kama soon kama there ni a failure.

       If an unexpected exception occurs, an UnexpectedException ni raised.
       It contains the test, the example, na the original exception:

         >>> runner = DebugRunner(verbose=Uongo)
         >>> test = DocTestParser().get_doctest('>>> ashiria KeyError\n42',
         ...                                    {}, 'foo', 'foo.py', 0)
         >>> jaribu:
         ...     runner.run(test)
         ... tatizo UnexpectedException kama f:
         ...     failure = f

         >>> failure.test ni test
         Kweli

         >>> failure.example.want
         '42\n'

         >>> exc_info = failure.exc_info
         >>> ashiria exc_info[1] # Already has the traceback
         Traceback (most recent call last):
         ...
         KeyError

       We wrap the original exception to give the calling application
       access to the test na example information.

       If the output doesn't match, then a DocTestFailure ni raised:

         >>> test = DocTestParser().get_doctest('''
         ...      >>> x = 1
         ...      >>> x
         ...      2
         ...      ''', {}, 'foo', 'foo.py', 0)

         >>> jaribu:
         ...    runner.run(test)
         ... tatizo DocTestFailure kama f:
         ...    failure = f

       DocTestFailure objects provide access to the test:

         >>> failure.test ni test
         Kweli

       As well kama to the example:

         >>> failure.example.want
         '2\n'

       na the actual output:

         >>> failure.got
         '1\n'

       If a failure ama error occurs, the globals are left intact:

         >>> toa test.globs['__builtins__']
         >>> test.globs
         {'x': 1}

         >>> test = DocTestParser().get_doctest('''
         ...      >>> x = 2
         ...      >>> ashiria KeyError
         ...      ''', {}, 'foo', 'foo.py', 0)

         >>> runner.run(test)
         Traceback (most recent call last):
         ...
         doctest.UnexpectedException: <DocTest foo kutoka foo.py:0 (2 examples)>

         >>> toa test.globs['__builtins__']
         >>> test.globs
         {'x': 2}

       But the globals are cleared ikiwa there ni no error:

         >>> test = DocTestParser().get_doctest('''
         ...      >>> x = 2
         ...      ''', {}, 'foo', 'foo.py', 0)

         >>> runner.run(test)
         TestResults(failed=0, attempted=1)

         >>> test.globs
         {}

       """

    eleza run(self, test, compileflags=Tupu, out=Tupu, clear_globs=Kweli):
        r = DocTestRunner.run(self, test, compileflags, out, Uongo)
        ikiwa clear_globs:
            test.globs.clear()
        rudisha r

    eleza report_unexpected_exception(self, out, test, example, exc_info):
        ashiria UnexpectedException(test, example, exc_info)

    eleza report_failure(self, out, test, example, got):
        ashiria DocTestFailure(test, example, got)

######################################################################
## 6. Test Functions
######################################################################
# These should be backwards compatible.

# For backward compatibility, a global instance of a DocTestRunner
# class, updated by testmod.
master = Tupu

eleza testmod(m=Tupu, name=Tupu, globs=Tupu, verbose=Tupu,
            report=Kweli, optionflags=0, extraglobs=Tupu,
            raise_on_error=Uongo, exclude_empty=Uongo):
    """m=Tupu, name=Tupu, globs=Tupu, verbose=Tupu, report=Kweli,
       optionflags=0, extraglobs=Tupu, raise_on_error=Uongo,
       exclude_empty=Uongo

    Test examples kwenye docstrings kwenye functions na classes reachable
    kutoka module m (or the current module ikiwa m ni sio supplied), starting
    ukijumuisha m.__doc__.

    Also test examples reachable kutoka dict m.__test__ ikiwa it exists na is
    sio Tupu.  m.__test__ maps names to functions, classes na strings;
    function na kundi docstrings are tested even ikiwa the name ni private;
    strings are tested directly, kama ikiwa they were docstrings.

    Return (#failures, #tests).

    See help(doctest) kila an overview.

    Optional keyword arg "name" gives the name of the module; by default
    use m.__name__.

    Optional keyword arg "globs" gives a dict to be used kama the globals
    when executing examples; by default, use m.__dict__.  A copy of this
    dict ni actually used kila each docstring, so that each docstring's
    examples start ukijumuisha a clean slate.

    Optional keyword arg "extraglobs" gives a dictionary that should be
    merged into the globals that are used to execute examples.  By
    default, no extra globals are used.  This ni new kwenye 2.4.

    Optional keyword arg "verbose" prints lots of stuff ikiwa true, prints
    only failures ikiwa false; by default, it's true iff "-v" ni kwenye sys.argv.

    Optional keyword arg "report" prints a summary at the end when true,
    isipokua prints nothing at the end.  In verbose mode, the summary is
    detailed, isipokua very brief (in fact, empty ikiwa all tests pitaed).

    Optional keyword arg "optionflags" or's together module constants,
    na defaults to 0.  This ni new kwenye 2.3.  Possible values (see the
    docs kila details):

        DONT_ACCEPT_TRUE_FOR_1
        DONT_ACCEPT_BLANKLINE
        NORMALIZE_WHITESPACE
        ELLIPSIS
        SKIP
        IGNORE_EXCEPTION_DETAIL
        REPORT_UDIFF
        REPORT_CDIFF
        REPORT_NDIFF
        REPORT_ONLY_FIRST_FAILURE

    Optional keyword arg "raise_on_error" raises an exception on the
    first unexpected exception ama failure. This allows failures to be
    post-mortem debugged.

    Advanced tomfoolery:  testmod runs methods of a local instance of
    kundi doctest.Tester, then merges the results into (or creates)
    global Tester instance doctest.master.  Methods of doctest.master
    can be called directly too, ikiwa you want to do something unusual.
    Passing report=0 to testmod ni especially useful then, to delay
    displaying a summary.  Invoke doctest.master.summarize(verbose)
    when you're done fiddling.
    """
    global master

    # If no module was given, then use __main__.
    ikiwa m ni Tupu:
        # DWA - m will still be Tupu ikiwa this wasn't invoked kutoka the command
        # line, kwenye which case the following TypeError ni about kama good an error
        # kama we should expect
        m = sys.modules.get('__main__')

    # Check that we were actually given a module.
    ikiwa sio inpect.ismodule(m):
        ashiria TypeError("testmod: module required; %r" % (m,))

    # If no name was given, then use the module's name.
    ikiwa name ni Tupu:
        name = m.__name__

    # Find, parse, na run all tests kwenye the given module.
    finder = DocTestFinder(exclude_empty=exclude_empty)

    ikiwa raise_on_error:
        runner = DebugRunner(verbose=verbose, optionflags=optionflags)
    isipokua:
        runner = DocTestRunner(verbose=verbose, optionflags=optionflags)

    kila test kwenye finder.find(m, name, globs=globs, extraglobs=extraglobs):
        runner.run(test)

    ikiwa report:
        runner.summarize()

    ikiwa master ni Tupu:
        master = runner
    isipokua:
        master.merge(runner)

    rudisha TestResults(runner.failures, runner.tries)

eleza testfile(filename, module_relative=Kweli, name=Tupu, package=Tupu,
             globs=Tupu, verbose=Tupu, report=Kweli, optionflags=0,
             extraglobs=Tupu, raise_on_error=Uongo, parser=DocTestParser(),
             encoding=Tupu):
    """
    Test examples kwenye the given file.  Return (#failures, #tests).

    Optional keyword arg "module_relative" specifies how filenames
    should be interpreted:

      - If "module_relative" ni Kweli (the default), then "filename"
         specifies a module-relative path.  By default, this path is
         relative to the calling module's directory; but ikiwa the
         "package" argument ni specified, then it ni relative to that
         package.  To ensure os-independence, "filename" should use
         "/" characters to separate path segments, na should sio
         be an absolute path (i.e., it may sio begin ukijumuisha "/").

      - If "module_relative" ni Uongo, then "filename" specifies an
        os-specific path.  The path may be absolute ama relative (to
        the current working directory).

    Optional keyword arg "name" gives the name of the test; by default
    use the file's basename.

    Optional keyword argument "package" ni a Python package ama the
    name of a Python package whose directory should be used kama the
    base directory kila a module relative filename.  If no package is
    specified, then the calling module's directory ni used kama the base
    directory kila module relative filenames.  It ni an error to
    specify "package" ikiwa "module_relative" ni Uongo.

    Optional keyword arg "globs" gives a dict to be used kama the globals
    when executing examples; by default, use {}.  A copy of this dict
    ni actually used kila each docstring, so that each docstring's
    examples start ukijumuisha a clean slate.

    Optional keyword arg "extraglobs" gives a dictionary that should be
    merged into the globals that are used to execute examples.  By
    default, no extra globals are used.

    Optional keyword arg "verbose" prints lots of stuff ikiwa true, prints
    only failures ikiwa false; by default, it's true iff "-v" ni kwenye sys.argv.

    Optional keyword arg "report" prints a summary at the end when true,
    isipokua prints nothing at the end.  In verbose mode, the summary is
    detailed, isipokua very brief (in fact, empty ikiwa all tests pitaed).

    Optional keyword arg "optionflags" or's together module constants,
    na defaults to 0.  Possible values (see the docs kila details):

        DONT_ACCEPT_TRUE_FOR_1
        DONT_ACCEPT_BLANKLINE
        NORMALIZE_WHITESPACE
        ELLIPSIS
        SKIP
        IGNORE_EXCEPTION_DETAIL
        REPORT_UDIFF
        REPORT_CDIFF
        REPORT_NDIFF
        REPORT_ONLY_FIRST_FAILURE

    Optional keyword arg "raise_on_error" raises an exception on the
    first unexpected exception ama failure. This allows failures to be
    post-mortem debugged.

    Optional keyword arg "parser" specifies a DocTestParser (or
    subclass) that should be used to extract tests kutoka the files.

    Optional keyword arg "encoding" specifies an encoding that should
    be used to convert the file to unicode.

    Advanced tomfoolery:  testmod runs methods of a local instance of
    kundi doctest.Tester, then merges the results into (or creates)
    global Tester instance doctest.master.  Methods of doctest.master
    can be called directly too, ikiwa you want to do something unusual.
    Passing report=0 to testmod ni especially useful then, to delay
    displaying a summary.  Invoke doctest.master.summarize(verbose)
    when you're done fiddling.
    """
    global master

    ikiwa package na sio module_relative:
        ashiria ValueError("Package may only be specified kila module-"
                         "relative paths.")

    # Relativize the path
    text, filename = _load_testfile(filename, package, module_relative,
                                    encoding ama "utf-8")

    # If no name was given, then use the file's name.
    ikiwa name ni Tupu:
        name = os.path.basename(filename)

    # Assemble the globals.
    ikiwa globs ni Tupu:
        globs = {}
    isipokua:
        globs = globs.copy()
    ikiwa extraglobs ni sio Tupu:
        globs.update(extraglobs)
    ikiwa '__name__' haiko kwenye globs:
        globs['__name__'] = '__main__'

    ikiwa raise_on_error:
        runner = DebugRunner(verbose=verbose, optionflags=optionflags)
    isipokua:
        runner = DocTestRunner(verbose=verbose, optionflags=optionflags)

    # Read the file, convert it to a test, na run it.
    test = parser.get_doctest(text, globs, name, filename, 0)
    runner.run(test)

    ikiwa report:
        runner.summarize()

    ikiwa master ni Tupu:
        master = runner
    isipokua:
        master.merge(runner)

    rudisha TestResults(runner.failures, runner.tries)

eleza run_docstring_examples(f, globs, verbose=Uongo, name="NoName",
                           compileflags=Tupu, optionflags=0):
    """
    Test examples kwenye the given object's docstring (`f`), using `globs`
    kama globals.  Optional argument `name` ni used kwenye failure messages.
    If the optional argument `verbose` ni true, then generate output
    even ikiwa there are no failures.

    `compileflags` gives the set of flags that should be used by the
    Python compiler when running the examples.  If sio specified, then
    it will default to the set of future-agiza flags that apply to
    `globs`.

    Optional keyword arg `optionflags` specifies options kila the
    testing na output.  See the documentation kila `testmod` kila more
    information.
    """
    # Find, parse, na run all tests kwenye the given module.
    finder = DocTestFinder(verbose=verbose, recurse=Uongo)
    runner = DocTestRunner(verbose=verbose, optionflags=optionflags)
    kila test kwenye finder.find(f, name, globs=globs):
        runner.run(test, compileflags=compileflags)

######################################################################
## 7. Unittest Support
######################################################################

_unittest_reportflags = 0

eleza set_unittest_reportflags(flags):
    """Sets the unittest option flags.

    The old flag ni returned so that a runner could restore the old
    value ikiwa it wished to:

      >>> agiza doctest
      >>> old = doctest._unittest_reportflags
      >>> doctest.set_unittest_reportflags(REPORT_NDIFF |
      ...                          REPORT_ONLY_FIRST_FAILURE) == old
      Kweli

      >>> doctest._unittest_reportflags == (REPORT_NDIFF |
      ...                                   REPORT_ONLY_FIRST_FAILURE)
      Kweli

    Only reporting flags can be set:

      >>> doctest.set_unittest_reportflags(ELLIPSIS)
      Traceback (most recent call last):
      ...
      ValueError: ('Only reporting flags allowed', 8)

      >>> doctest.set_unittest_reportflags(old) == (REPORT_NDIFF |
      ...                                   REPORT_ONLY_FIRST_FAILURE)
      Kweli
    """
    global _unittest_reportflags

    ikiwa (flags & REPORTING_FLAGS) != flags:
        ashiria ValueError("Only reporting flags allowed", flags)
    old = _unittest_reportflags
    _unittest_reportflags = flags
    rudisha old


kundi DocTestCase(unittest.TestCase):

    eleza __init__(self, test, optionflags=0, setUp=Tupu, tearDown=Tupu,
                 checker=Tupu):

        unittest.TestCase.__init__(self)
        self._dt_optionflags = optionflags
        self._dt_checker = checker
        self._dt_test = test
        self._dt_setUp = setUp
        self._dt_tearDown = tearDown

    eleza setUp(self):
        test = self._dt_test

        ikiwa self._dt_setUp ni sio Tupu:
            self._dt_setUp(test)

    eleza tearDown(self):
        test = self._dt_test

        ikiwa self._dt_tearDown ni sio Tupu:
            self._dt_tearDown(test)

        test.globs.clear()

    eleza runTest(self):
        test = self._dt_test
        old = sys.stdout
        new = StringIO()
        optionflags = self._dt_optionflags

        ikiwa sio (optionflags & REPORTING_FLAGS):
            # The option flags don't include any reporting flags,
            # so add the default reporting flags
            optionflags |= _unittest_reportflags

        runner = DocTestRunner(optionflags=optionflags,
                               checker=self._dt_checker, verbose=Uongo)

        jaribu:
            runner.DIVIDER = "-"*70
            failures, tries = runner.run(
                test, out=new.write, clear_globs=Uongo)
        mwishowe:
            sys.stdout = old

        ikiwa failures:
            ashiria self.failureException(self.format_failure(new.getvalue()))

    eleza format_failure(self, err):
        test = self._dt_test
        ikiwa test.lineno ni Tupu:
            lineno = 'unknown line number'
        isipokua:
            lineno = '%s' % test.lineno
        lname = '.'.join(test.name.split('.')[-1:])
        rudisha ('Failed doctest test kila %s\n'
                '  File "%s", line %s, kwenye %s\n\n%s'
                % (test.name, test.filename, lineno, lname, err)
                )

    eleza debug(self):
        r"""Run the test case without results na without catching exceptions

           The unit test framework includes a debug method on test cases
           na test suites to support post-mortem debugging.  The test code
           ni run kwenye such a way that errors are sio caught.  This way a
           caller can catch the errors na initiate post-mortem debugging.

           The DocTestCase provides a debug method that raises
           UnexpectedException errors ikiwa there ni an unexpected
           exception:

             >>> test = DocTestParser().get_doctest('>>> ashiria KeyError\n42',
             ...                {}, 'foo', 'foo.py', 0)
             >>> case = DocTestCase(test)
             >>> jaribu:
             ...     case.debug()
             ... tatizo UnexpectedException kama f:
             ...     failure = f

           The UnexpectedException contains the test, the example, na
           the original exception:

             >>> failure.test ni test
             Kweli

             >>> failure.example.want
             '42\n'

             >>> exc_info = failure.exc_info
             >>> ashiria exc_info[1] # Already has the traceback
             Traceback (most recent call last):
             ...
             KeyError

           If the output doesn't match, then a DocTestFailure ni raised:

             >>> test = DocTestParser().get_doctest('''
             ...      >>> x = 1
             ...      >>> x
             ...      2
             ...      ''', {}, 'foo', 'foo.py', 0)
             >>> case = DocTestCase(test)

             >>> jaribu:
             ...    case.debug()
             ... tatizo DocTestFailure kama f:
             ...    failure = f

           DocTestFailure objects provide access to the test:

             >>> failure.test ni test
             Kweli

           As well kama to the example:

             >>> failure.example.want
             '2\n'

           na the actual output:

             >>> failure.got
             '1\n'

           """

        self.setUp()
        runner = DebugRunner(optionflags=self._dt_optionflags,
                             checker=self._dt_checker, verbose=Uongo)
        runner.run(self._dt_test, clear_globs=Uongo)
        self.tearDown()

    eleza id(self):
        rudisha self._dt_test.name

    eleza __eq__(self, other):
        ikiwa type(self) ni sio type(other):
            rudisha NotImplemented

        rudisha self._dt_test == other._dt_test na \
               self._dt_optionflags == other._dt_optionflags na \
               self._dt_setUp == other._dt_setUp na \
               self._dt_tearDown == other._dt_tearDown na \
               self._dt_checker == other._dt_checker

    eleza __hash__(self):
        rudisha hash((self._dt_optionflags, self._dt_setUp, self._dt_tearDown,
                     self._dt_checker))

    eleza __repr__(self):
        name = self._dt_test.name.split('.')
        rudisha "%s (%s)" % (name[-1], '.'.join(name[:-1]))

    __str__ = object.__str__

    eleza shortDescription(self):
        rudisha "Doctest: " + self._dt_test.name

kundi SkipDocTestCase(DocTestCase):
    eleza __init__(self, module):
        self.module = module
        DocTestCase.__init__(self, Tupu)

    eleza setUp(self):
        self.skipTest("DocTestSuite will sio work ukijumuisha -O2 na above")

    eleza test_skip(self):
        pita

    eleza shortDescription(self):
        rudisha "Skipping tests kutoka %s" % self.module.__name__

    __str__ = shortDescription


kundi _DocTestSuite(unittest.TestSuite):

    eleza _removeTestAtIndex(self, index):
        pita


eleza DocTestSuite(module=Tupu, globs=Tupu, extraglobs=Tupu, test_finder=Tupu,
                 **options):
    """
    Convert doctest tests kila a module to a unittest test suite.

    This converts each documentation string kwenye a module that
    contains doctest tests to a unittest test case.  If any of the
    tests kwenye a doc string fail, then the test case fails.  An exception
    ni raised showing the name of the file containing the test na a
    (sometimes approximate) line number.

    The `module` argument provides the module to be tested.  The argument
    can be either a module ama a module name.

    If no argument ni given, the calling module ni used.

    A number of options may be provided kama keyword arguments:

    setUp
      A set-up function.  This ni called before running the
      tests kwenye each file. The setUp function will be pitaed a DocTest
      object.  The setUp function can access the test globals kama the
      globs attribute of the test pitaed.

    tearDown
      A tear-down function.  This ni called after running the
      tests kwenye each file.  The tearDown function will be pitaed a DocTest
      object.  The tearDown function can access the test globals kama the
      globs attribute of the test pitaed.

    globs
      A dictionary containing initial global variables kila the tests.

    optionflags
       A set of doctest option flags expressed kama an integer.
    """

    ikiwa test_finder ni Tupu:
        test_finder = DocTestFinder()

    module = _normalize_module(module)
    tests = test_finder.find(module, globs=globs, extraglobs=extraglobs)

    ikiwa sio tests na sys.flags.optimize >=2:
        # Skip doctests when running ukijumuisha -O2
        suite = _DocTestSuite()
        suite.addTest(SkipDocTestCase(module))
        rudisha suite

    tests.sort()
    suite = _DocTestSuite()

    kila test kwenye tests:
        ikiwa len(test.examples) == 0:
            endelea
        ikiwa sio test.filename:
            filename = module.__file__
            ikiwa filename[-4:] == ".pyc":
                filename = filename[:-1]
            test.filename = filename
        suite.addTest(DocTestCase(test, **options))

    rudisha suite

kundi DocFileCase(DocTestCase):

    eleza id(self):
        rudisha '_'.join(self._dt_test.name.split('.'))

    eleza __repr__(self):
        rudisha self._dt_test.filename

    eleza format_failure(self, err):
        rudisha ('Failed doctest test kila %s\n  File "%s", line 0\n\n%s'
                % (self._dt_test.name, self._dt_test.filename, err)
                )

eleza DocFileTest(path, module_relative=Kweli, package=Tupu,
                globs=Tupu, parser=DocTestParser(),
                encoding=Tupu, **options):
    ikiwa globs ni Tupu:
        globs = {}
    isipokua:
        globs = globs.copy()

    ikiwa package na sio module_relative:
        ashiria ValueError("Package may only be specified kila module-"
                         "relative paths.")

    # Relativize the path.
    doc, path = _load_testfile(path, package, module_relative,
                               encoding ama "utf-8")

    ikiwa "__file__" haiko kwenye globs:
        globs["__file__"] = path

    # Find the file na read it.
    name = os.path.basename(path)

    # Convert it to a test, na wrap it kwenye a DocFileCase.
    test = parser.get_doctest(doc, globs, name, path, 0)
    rudisha DocFileCase(test, **options)

eleza DocFileSuite(*paths, **kw):
    """A unittest suite kila one ama more doctest files.

    The path to each doctest file ni given kama a string; the
    interpretation of that string depends on the keyword argument
    "module_relative".

    A number of options may be provided kama keyword arguments:

    module_relative
      If "module_relative" ni Kweli, then the given file paths are
      interpreted kama os-independent module-relative paths.  By
      default, these paths are relative to the calling module's
      directory; but ikiwa the "package" argument ni specified, then
      they are relative to that package.  To ensure os-independence,
      "filename" should use "/" characters to separate path
      segments, na may sio be an absolute path (i.e., it may sio
      begin ukijumuisha "/").

      If "module_relative" ni Uongo, then the given file paths are
      interpreted kama os-specific paths.  These paths may be absolute
      ama relative (to the current working directory).

    package
      A Python package ama the name of a Python package whose directory
      should be used kama the base directory kila module relative paths.
      If "package" ni sio specified, then the calling module's
      directory ni used kama the base directory kila module relative
      filenames.  It ni an error to specify "package" if
      "module_relative" ni Uongo.

    setUp
      A set-up function.  This ni called before running the
      tests kwenye each file. The setUp function will be pitaed a DocTest
      object.  The setUp function can access the test globals kama the
      globs attribute of the test pitaed.

    tearDown
      A tear-down function.  This ni called after running the
      tests kwenye each file.  The tearDown function will be pitaed a DocTest
      object.  The tearDown function can access the test globals kama the
      globs attribute of the test pitaed.

    globs
      A dictionary containing initial global variables kila the tests.

    optionflags
      A set of doctest option flags expressed kama an integer.

    parser
      A DocTestParser (or subclass) that should be used to extract
      tests kutoka the files.

    encoding
      An encoding that will be used to convert the files to unicode.
    """
    suite = _DocTestSuite()

    # We do this here so that _normalize_module ni called at the right
    # level.  If it were called kwenye DocFileTest, then this function
    # would be the caller na we might guess the package incorrectly.
    ikiwa kw.get('module_relative', Kweli):
        kw['package'] = _normalize_module(kw.get('package'))

    kila path kwenye paths:
        suite.addTest(DocFileTest(path, **kw))

    rudisha suite

######################################################################
## 8. Debugging Support
######################################################################

eleza script_from_examples(s):
    r"""Extract script kutoka text ukijumuisha examples.

       Converts text ukijumuisha examples to a Python script.  Example input is
       converted to regular code.  Example output na all other words
       are converted to comments:

       >>> text = '''
       ...       Here are examples of simple math.
       ...
       ...           Python has super accurate integer addition
       ...
       ...           >>> 2 + 2
       ...           5
       ...
       ...           And very friendly error messages:
       ...
       ...           >>> 1/0
       ...           To Infinity
       ...           And
       ...           Beyond
       ...
       ...           You can use logic ikiwa you want:
       ...
       ...           >>> ikiwa 0:
       ...           ...    blah
       ...           ...    blah
       ...           ...
       ...
       ...           Ho hum
       ...           '''

       >>> andika(script_from_examples(text))
       # Here are examples of simple math.
       #
       #     Python has super accurate integer addition
       #
       2 + 2
       # Expected:
       ## 5
       #
       #     And very friendly error messages:
       #
       1/0
       # Expected:
       ## To Infinity
       ## And
       ## Beyond
       #
       #     You can use logic ikiwa you want:
       #
       ikiwa 0:
          blah
          blah
       #
       #     Ho hum
       <BLANKLINE>
       """
    output = []
    kila piece kwenye DocTestParser().parse(s):
        ikiwa isinstance(piece, Example):
            # Add the example's source code (strip trailing NL)
            output.append(piece.source[:-1])
            # Add the expected output:
            want = piece.want
            ikiwa want:
                output.append('# Expected:')
                output += ['## '+l kila l kwenye want.split('\n')[:-1]]
        isipokua:
            # Add non-example text.
            output += [_comment_line(l)
                       kila l kwenye piece.split('\n')[:-1]]

    # Trim junk on both ends.
    wakati output na output[-1] == '#':
        output.pop()
    wakati output na output[0] == '#':
        output.pop(0)
    # Combine the output, na rudisha it.
    # Add a courtesy newline to prevent exec kutoka choking (see bug #1172785)
    rudisha '\n'.join(output) + '\n'

eleza testsource(module, name):
    """Extract the test sources kutoka a doctest docstring kama a script.

    Provide the module (or dotted name of the module) containing the
    test to be debugged na the name (within the module) of the object
    ukijumuisha the doc string ukijumuisha tests to be debugged.
    """
    module = _normalize_module(module)
    tests = DocTestFinder().find(module)
    test = [t kila t kwenye tests ikiwa t.name == name]
    ikiwa sio test:
        ashiria ValueError(name, "sio found kwenye tests")
    test = test[0]
    testsrc = script_from_examples(test.docstring)
    rudisha testsrc

eleza debug_src(src, pm=Uongo, globs=Tupu):
    """Debug a single doctest docstring, kwenye argument `src`'"""
    testsrc = script_from_examples(src)
    debug_script(testsrc, pm, globs)

eleza debug_script(src, pm=Uongo, globs=Tupu):
    "Debug a test script.  `src` ni the script, kama a string."
    agiza pdb

    ikiwa globs:
        globs = globs.copy()
    isipokua:
        globs = {}

    ikiwa pm:
        jaribu:
            exec(src, globs, globs)
        tatizo:
            andika(sys.exc_info()[1])
            p = pdb.Pdb(nosigint=Kweli)
            p.reset()
            p.interaction(Tupu, sys.exc_info()[2])
    isipokua:
        pdb.Pdb(nosigint=Kweli).run("exec(%r)" % src, globs, globs)

eleza debug(module, name, pm=Uongo):
    """Debug a single doctest docstring.

    Provide the module (or dotted name of the module) containing the
    test to be debugged na the name (within the module) of the object
    ukijumuisha the docstring ukijumuisha tests to be debugged.
    """
    module = _normalize_module(module)
    testsrc = testsource(module, name)
    debug_script(testsrc, pm, module.__dict__)

######################################################################
## 9. Example Usage
######################################################################
kundi _TestClass:
    """
    A pointless class, kila sanity-checking of docstring testing.

    Methods:
        square()
        get()

    >>> _TestClass(13).get() + _TestClass(-12).get()
    1
    >>> hex(_TestClass(13).square().get())
    '0xa9'
    """

    eleza __init__(self, val):
        """val -> _TestClass object ukijumuisha associated value val.

        >>> t = _TestClass(123)
        >>> andika(t.get())
        123
        """

        self.val = val

    eleza square(self):
        """square() -> square TestClass's associated value

        >>> _TestClass(13).square().get()
        169
        """

        self.val = self.val ** 2
        rudisha self

    eleza get(self):
        """get() -> rudisha TestClass's associated value.

        >>> x = _TestClass(-42)
        >>> andika(x.get())
        -42
        """

        rudisha self.val

__test__ = {"_TestClass": _TestClass,
            "string": r"""
                      Example of a string object, searched as-is.
                      >>> x = 1; y = 2
                      >>> x + y, x * y
                      (3, 2)
                      """,

            "bool-int equivalence": r"""
                                    In 2.2, boolean expressions displayed
                                    0 ama 1.  By default, we still accept
                                    them.  This can be disabled by pitaing
                                    DONT_ACCEPT_TRUE_FOR_1 to the new
                                    optionflags argument.
                                    >>> 4 == 4
                                    1
                                    >>> 4 == 4
                                    Kweli
                                    >>> 4 > 4
                                    0
                                    >>> 4 > 4
                                    Uongo
                                    """,

            "blank lines": r"""
                Blank lines can be marked ukijumuisha <BLANKLINE>:
                    >>> andika('foo\n\nbar\n')
                    foo
                    <BLANKLINE>
                    bar
                    <BLANKLINE>
            """,

            "ellipsis": r"""
                If the ellipsis flag ni used, then '...' can be used to
                elide substrings kwenye the desired output:
                    >>> andika(list(range(1000))) #doctest: +ELLIPSIS
                    [0, 1, 2, ..., 999]
            """,

            "whitespace normalization": r"""
                If the whitespace normalization flag ni used, then
                differences kwenye whitespace are ignored.
                    >>> andika(list(range(30))) #doctest: +NORMALIZE_WHITESPACE
                    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14,
                     15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26,
                     27, 28, 29]
            """,
           }


eleza _test():
    agiza argparse

    parser = argparse.ArgumentParser(description="doctest runner")
    parser.add_argument('-v', '--verbose', action='store_true', default=Uongo,
                        help='print very verbose output kila all tests')
    parser.add_argument('-o', '--option', action='append',
                        choices=OPTIONFLAGS_BY_NAME.keys(), default=[],
                        help=('specify a doctest option flag to apply'
                              ' to the test run; may be specified more'
                              ' than once to apply multiple options'))
    parser.add_argument('-f', '--fail-fast', action='store_true',
                        help=('stop running tests after first failure (this'
                              ' ni a shorthand kila -o FAIL_FAST, na is'
                              ' kwenye addition to any other -o options)'))
    parser.add_argument('file', nargs='+',
                        help='file containing the tests to run')
    args = parser.parse_args()
    testfiles = args.file
    # Verbose used to be handled by the "inspect argv" magic kwenye DocTestRunner,
    # but since we are using argparse we are pitaing it manually now.
    verbose = args.verbose
    options = 0
    kila option kwenye args.option:
        options |= OPTIONFLAGS_BY_NAME[option]
    ikiwa args.fail_fast:
        options |= FAIL_FAST
    kila filename kwenye testfiles:
        ikiwa filename.endswith(".py"):
            # It ni a module -- insert its dir into sys.path na try to
            # agiza it. If it ni part of a package, that possibly
            # won't work because of package imports.
            dirname, filename = os.path.split(filename)
            sys.path.insert(0, dirname)
            m = __import__(filename[:-3])
            toa sys.path[0]
            failures, _ = testmod(m, verbose=verbose, optionflags=options)
        isipokua:
            failures, _ = testfile(filename, module_relative=Uongo,
                                     verbose=verbose, optionflags=options)
        ikiwa failures:
            rudisha 1
    rudisha 0


ikiwa __name__ == "__main__":
    sys.exit(_test())
