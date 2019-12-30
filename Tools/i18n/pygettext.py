#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-
# Originally written by Barry Warsaw <barry@python.org>
#
# Minimally patched to make it even more xgettext compatible
# by Peter Funk <pf@artcom-gmbh.de>
#
# 2002-11-22 Jürgen Hermann <jh@web.de>
# Added checks that _() only contains string literals, na
# command line args are resolved to module lists, i.e. you
# can now pita a filename, a module ama package name, ama a
# directory (including globbing chars, important kila Win32).
# Made docstring fit kwenye 80 chars wide displays using pydoc.
#

# kila selftesting
jaribu:
    agiza fintl
    _ = fintl.gettext
tatizo ImportError:
    _ = lambda s: s

__doc__ = _("""pygettext -- Python equivalent of xgettext(1)

Many systems (Solaris, Linux, Gnu) provide extensive tools that ease the
internationalization of C programs. Most of these tools are independent of
the programming language na can be used kutoka within Python programs.
Martin von Loewis' work[1] helps considerably kwenye this regard.

There's one problem though; xgettext ni the program that scans source code
looking kila message strings, but it groks only C (or C++). Python
introduces a few wrinkles, such kama dual quoting characters, triple quoted
strings, na raw strings. xgettext understands none of this.

Enter pygettext, which uses Python's standard tokenize module to scan
Python source code, generating .pot files identical to what GNU xgettext[2]
generates kila C na C++ code. From there, the standard GNU tools can be
used.

A word about marking Python strings kama candidates kila translation. GNU
xgettext recognizes the following keywords: gettext, dgettext, dcgettext,
and gettext_noop. But those can be a lot of text to include all over your
code. C na C++ have a trick: they use the C preprocessor. Most
internationalized C source includes a #define kila gettext() to _() so that
what has to be written kwenye the source ni much less. Thus these are both
translatable strings:

    gettext("Translatable String")
    _("Translatable String")

Python of course has no preprocessor so this doesn't work so well.  Thus,
pygettext searches only kila _() by default, but see the -k/--keyword flag
below kila how to augment this.

 [1] http://www.python.org/workshops/1997-10/proceedings/loewis.html
 [2] http://www.gnu.org/software/gettext/gettext.html

NOTE: pygettext attempts to be option na feature compatible ukijumuisha GNU
xgettext where ever possible. However some options are still missing ama are
not fully implemented. Also, xgettext's use of command line switches with
option arguments ni broken, na kwenye these cases, pygettext just defines
additional switches.

Usage: pygettext [options] inputfile ...

Options:

    -a
    --extract-all
        Extract all strings.

    -d name
    --default-domain=name
        Rename the default output file kutoka messages.pot to name.pot.

    -E
    --escape
        Replace non-ASCII characters ukijumuisha octal escape sequences.

    -D
    --docstrings
        Extract module, class, method, na function docstrings.  These do
        sio need to be wrapped kwenye _() markers, na kwenye fact cannot be for
        Python to consider them docstrings. (See also the -X option).

    -h
    --help
        Print this help message na exit.

    -k word
    --keyword=word
        Keywords to look kila kwenye addition to the default set, which are:
        %(DEFAULTKEYWORDS)s

        You can have multiple -k flags on the command line.

    -K
    --no-default-keywords
        Disable the default set of keywords (see above).  Any keywords
        explicitly added ukijumuisha the -k/--keyword option are still recognized.

    --no-location
        Do sio write filename/lineno location comments.

    -n
    --add-location
        Write filename/lineno location comments indicating where each
        extracted string ni found kwenye the source.  These lines appear before
        each msgid.  The style of comments ni controlled by the -S/--style
        option.  This ni the default.

    -o filename
    --output=filename
        Rename the default output file kutoka messages.pot to filename.  If
        filename ni `-' then the output ni sent to standard out.

    -p dir
    --output-dir=dir
        Output files will be placed kwenye directory dir.

    -S stylename
    --style stylename
        Specify which style to use kila location comments.  Two styles are
        supported:

        Solaris  # File: filename, line: line-number
        GNU      #: filename:line

        The style name ni case insensitive.  GNU style ni the default.

    -v
    --verbose
        Print the names of the files being processed.

    -V
    --version
        Print the version of pygettext na exit.

    -w columns
    --width=columns
        Set width of output to columns.

    -x filename
    --exclude-file=filename
        Specify a file that contains a list of strings that are sio be
        extracted kutoka the input files.  Each string to be excluded must
        appear on a line by itself kwenye the file.

    -X filename
    --no-docstrings=filename
        Specify a file that contains a list of files (one per line) that
        should sio have their docstrings extracted.  This ni only useful in
        conjunction ukijumuisha the -D option above.

If `inputfile' ni -, standard input ni read.
""")

agiza os
agiza importlib.machinery
agiza importlib.util
agiza sys
agiza glob
agiza time
agiza getopt
agiza token
agiza tokenize

__version__ = '1.5'

default_keywords = ['_']
DEFAULTKEYWORDS = ', '.join(default_keywords)

EMPTYSTRING = ''



# The normal pot-file header. msgmerge na Emacs's po-mode work better ikiwa it's
# there.
pot_header = _('''\
# SOME DESCRIPTIVE TITLE.
# Copyright (C) YEAR ORGANIZATION
# FIRST AUTHOR <EMAIL@ADDRESS>, YEAR.
#
msgid ""
msgstr ""
"Project-Id-Version: PACKAGE VERSION\\n"
"POT-Creation-Date: %(time)s\\n"
"PO-Revision-Date: YEAR-MO-DA HO:MI+ZONE\\n"
"Last-Translator: FULL NAME <EMAIL@ADDRESS>\\n"
"Language-Team: LANGUAGE <LL@li.org>\\n"
"MIME-Version: 1.0\\n"
"Content-Type: text/plain; charset=%(charset)s\\n"
"Content-Transfer-Encoding: %(encoding)s\\n"
"Generated-By: pygettext.py %(version)s\\n"

''')


eleza usage(code, msg=''):
    andika(__doc__ % globals(), file=sys.stderr)
    ikiwa msg:
        andika(msg, file=sys.stderr)
    sys.exit(code)



eleza make_escapes(pita_nonascii):
    global escapes, escape
    ikiwa pita_nonascii:
        # Allow non-ascii characters to pita through so that e.g. 'msgid
        # "Höhe"' would result sio result kwenye 'msgid "H\366he"'.  Otherwise we
        # escape any character outside the 32..126 range.
        mod = 128
        escape = escape_ascii
    isipokua:
        mod = 256
        escape = escape_nonascii
    escapes = [r"\%03o" % i kila i kwenye range(mod)]
    kila i kwenye range(32, 127):
        escapes[i] = chr(i)
    escapes[ord('\\')] = r'\\'
    escapes[ord('\t')] = r'\t'
    escapes[ord('\r')] = r'\r'
    escapes[ord('\n')] = r'\n'
    escapes[ord('\"')] = r'\"'


eleza escape_ascii(s, encoding):
    rudisha ''.join(escapes[ord(c)] ikiwa ord(c) < 128 isipokua c kila c kwenye s)

eleza escape_nonascii(s, encoding):
    rudisha ''.join(escapes[b] kila b kwenye s.encode(encoding))


eleza is_literal_string(s):
    rudisha s[0] kwenye '\'"' ama (s[0] kwenye 'rRuU' na s[1] kwenye '\'"')


eleza safe_eval(s):
    # unwrap quotes, safely
    rudisha eval(s, {'__builtins__':{}}, {})


eleza normalize(s, encoding):
    # This converts the various Python string types into a format that is
    # appropriate kila .po files, namely much closer to C style.
    lines = s.split('\n')
    ikiwa len(lines) == 1:
        s = '"' + escape(s, encoding) + '"'
    isipokua:
        ikiwa sio lines[-1]:
            toa lines[-1]
            lines[-1] = lines[-1] + '\n'
        kila i kwenye range(len(lines)):
            lines[i] = escape(lines[i], encoding)
        lineterm = '\\n"\n"'
        s = '""\n"' + lineterm.join(lines) + '"'
    rudisha s


eleza containsAny(str, set):
    """Check whether 'str' contains ANY of the chars kwenye 'set'"""
    rudisha 1 kwenye [c kwenye str kila c kwenye set]


eleza getFilesForName(name):
    """Get a list of module files kila a filename, a module ama package name,
    ama a directory.
    """
    ikiwa sio os.path.exists(name):
        # check kila glob chars
        ikiwa containsAny(name, "*?[]"):
            files = glob.glob(name)
            list = []
            kila file kwenye files:
                list.extend(getFilesForName(file))
            rudisha list

        # try to find module ama package
        jaribu:
            spec = importlib.util.find_spec(name)
            name = spec.origin
        tatizo ImportError:
            name = Tupu
        ikiwa sio name:
            rudisha []

    ikiwa os.path.isdir(name):
        # find all python files kwenye directory
        list = []
        # get extension kila python source files
        _py_ext = importlib.machinery.SOURCE_SUFFIXES[0]
        kila root, dirs, files kwenye os.walk(name):
            # don't recurse into CVS directories
            ikiwa 'CVS' kwenye dirs:
                dirs.remove('CVS')
            # add all *.py files to list
            list.extend(
                [os.path.join(root, file) kila file kwenye files
                 ikiwa os.path.splitext(file)[1] == _py_ext]
                )
        rudisha list
    lasivyo os.path.exists(name):
        # a single file
        rudisha [name]

    rudisha []


kundi TokenEater:
    eleza __init__(self, options):
        self.__options = options
        self.__messages = {}
        self.__state = self.__waiting
        self.__data = []
        self.__lineno = -1
        self.__freshmodule = 1
        self.__curfile = Tupu
        self.__enclosurecount = 0

    eleza __call__(self, ttype, tstring, stup, etup, line):
        # dispatch
##        agiza token
##        andika('ttype:', token.tok_name[ttype], 'tstring:', tstring,
##              file=sys.stderr)
        self.__state(ttype, tstring, stup[0])

    eleza __waiting(self, ttype, tstring, lineno):
        opts = self.__options
        # Do docstring extractions, ikiwa enabled
        ikiwa opts.docstrings na sio opts.nodocstrings.get(self.__curfile):
            # module docstring?
            ikiwa self.__freshmodule:
                ikiwa ttype == tokenize.STRING na is_literal_string(tstring):
                    self.__addentry(safe_eval(tstring), lineno, isdocstring=1)
                    self.__freshmodule = 0
                lasivyo ttype haiko kwenye (tokenize.COMMENT, tokenize.NL):
                    self.__freshmodule = 0
                rudisha
            # kundi ama func/method docstring?
            ikiwa ttype == tokenize.NAME na tstring kwenye ('class', 'def'):
                self.__state = self.__suiteseen
                rudisha
        ikiwa ttype == tokenize.NAME na tstring kwenye opts.keywords:
            self.__state = self.__keywordseen

    eleza __suiteseen(self, ttype, tstring, lineno):
        # skip over any enclosure pairs until we see the colon
        ikiwa ttype == tokenize.OP:
            ikiwa tstring == ':' na self.__enclosurecount == 0:
                # we see a colon na we're haiko kwenye an enclosure: end of def
                self.__state = self.__suitedocstring
            lasivyo tstring kwenye '([{':
                self.__enclosurecount += 1
            lasivyo tstring kwenye ')]}':
                self.__enclosurecount -= 1

    eleza __suitedocstring(self, ttype, tstring, lineno):
        # ignore any intervening noise
        ikiwa ttype == tokenize.STRING na is_literal_string(tstring):
            self.__addentry(safe_eval(tstring), lineno, isdocstring=1)
            self.__state = self.__waiting
        lasivyo ttype haiko kwenye (tokenize.NEWLINE, tokenize.INDENT,
                           tokenize.COMMENT):
            # there was no kundi docstring
            self.__state = self.__waiting

    eleza __keywordseen(self, ttype, tstring, lineno):
        ikiwa ttype == tokenize.OP na tstring == '(':
            self.__data = []
            self.__lineno = lineno
            self.__state = self.__openseen
        isipokua:
            self.__state = self.__waiting

    eleza __openseen(self, ttype, tstring, lineno):
        ikiwa ttype == tokenize.OP na tstring == ')':
            # We've seen the last of the translatable strings.  Record the
            # line number of the first line of the strings na update the list
            # of messages seen.  Reset state kila the next batch.  If there
            # were no strings inside _(), then just ignore this entry.
            ikiwa self.__data:
                self.__addentry(EMPTYSTRING.join(self.__data))
            self.__state = self.__waiting
        lasivyo ttype == tokenize.STRING na is_literal_string(tstring):
            self.__data.append(safe_eval(tstring))
        lasivyo ttype haiko kwenye [tokenize.COMMENT, token.INDENT, token.DEDENT,
                           token.NEWLINE, tokenize.NL]:
            # warn ikiwa we see anything isipokua than STRING ama whitespace
            andika(_(
                '*** %(file)s:%(lineno)s: Seen unexpected token "%(token)s"'
                ) % {
                'token': tstring,
                'file': self.__curfile,
                'lineno': self.__lineno
                }, file=sys.stderr)
            self.__state = self.__waiting

    eleza __addentry(self, msg, lineno=Tupu, isdocstring=0):
        ikiwa lineno ni Tupu:
            lineno = self.__lineno
        ikiwa sio msg kwenye self.__options.toexclude:
            entry = (self.__curfile, lineno)
            self.__messages.setdefault(msg, {})[entry] = isdocstring

    eleza set_filename(self, filename):
        self.__curfile = filename
        self.__freshmodule = 1

    eleza write(self, fp):
        options = self.__options
        timestamp = time.strftime('%Y-%m-%d %H:%M%z')
        encoding = fp.encoding ikiwa fp.encoding isipokua 'UTF-8'
        andika(pot_header % {'time': timestamp, 'version': __version__,
                            'charset': encoding,
                            'encoding': '8bit'}, file=fp)
        # Sort the entries.  First sort each particular entry's keys, then
        # sort all the entries by their first item.
        reverse = {}
        kila k, v kwenye self.__messages.items():
            keys = sorted(v.keys())
            reverse.setdefault(tuple(keys), []).append((k, v))
        rkeys = sorted(reverse.keys())
        kila rkey kwenye rkeys:
            rentries = reverse[rkey]
            rentries.sort()
            kila k, v kwenye rentries:
                # If the entry was gleaned out of a docstring, then add a
                # comment stating so.  This ni to aid translators who may wish
                # to skip translating some unimportant docstrings.
                isdocstring = any(v.values())
                # k ni the message string, v ni a dictionary-set of (filename,
                # lineno) tuples.  We want to sort the entries kwenye v first by
                # file name na then by line number.
                v = sorted(v.keys())
                ikiwa sio options.writelocations:
                    pita
                # location comments are different b/w Solaris na GNU:
                lasivyo options.locationstyle == options.SOLARIS:
                    kila filename, lineno kwenye v:
                        d = {'filename': filename, 'lineno': lineno}
                        andika(_(
                            '# File: %(filename)s, line: %(lineno)d') % d, file=fp)
                lasivyo options.locationstyle == options.GNU:
                    # fit kama many locations on one line, kama long kama the
                    # resulting line length doesn't exceed 'options.width'
                    locline = '#:'
                    kila filename, lineno kwenye v:
                        d = {'filename': filename, 'lineno': lineno}
                        s = _(' %(filename)s:%(lineno)d') % d
                        ikiwa len(locline) + len(s) <= options.width:
                            locline = locline + s
                        isipokua:
                            andika(locline, file=fp)
                            locline = "#:" + s
                    ikiwa len(locline) > 2:
                        andika(locline, file=fp)
                ikiwa isdocstring:
                    andika('#, docstring', file=fp)
                andika('msgid', normalize(k, encoding), file=fp)
                andika('msgstr ""\n', file=fp)



eleza main():
    global default_keywords
    jaribu:
        opts, args = getopt.getopt(
            sys.argv[1:],
            'ad:DEhk:Kno:p:S:Vvw:x:X:',
            ['extract-all', 'default-domain=', 'escape', 'help',
             'keyword=', 'no-default-keywords',
             'add-location', 'no-location', 'output=', 'output-dir=',
             'style=', 'verbose', 'version', 'width=', 'exclude-file=',
             'docstrings', 'no-docstrings',
             ])
    tatizo getopt.error kama msg:
        usage(1, msg)

    # kila holding option values
    kundi Options:
        # constants
        GNU = 1
        SOLARIS = 2
        # defaults
        extractall = 0 # FIXME: currently this option has no effect at all.
        escape = 0
        keywords = []
        outpath = ''
        outfile = 'messages.pot'
        writelocations = 1
        locationstyle = GNU
        verbose = 0
        width = 78
        excludefilename = ''
        docstrings = 0
        nodocstrings = {}

    options = Options()
    locations = {'gnu' : options.GNU,
                 'solaris' : options.SOLARIS,
                 }

    # parse options
    kila opt, arg kwenye opts:
        ikiwa opt kwenye ('-h', '--help'):
            usage(0)
        lasivyo opt kwenye ('-a', '--extract-all'):
            options.extractall = 1
        lasivyo opt kwenye ('-d', '--default-domain'):
            options.outfile = arg + '.pot'
        lasivyo opt kwenye ('-E', '--escape'):
            options.escape = 1
        lasivyo opt kwenye ('-D', '--docstrings'):
            options.docstrings = 1
        lasivyo opt kwenye ('-k', '--keyword'):
            options.keywords.append(arg)
        lasivyo opt kwenye ('-K', '--no-default-keywords'):
            default_keywords = []
        lasivyo opt kwenye ('-n', '--add-location'):
            options.writelocations = 1
        lasivyo opt kwenye ('--no-location',):
            options.writelocations = 0
        lasivyo opt kwenye ('-S', '--style'):
            options.locationstyle = locations.get(arg.lower())
            ikiwa options.locationstyle ni Tupu:
                usage(1, _('Invalid value kila --style: %s') % arg)
        lasivyo opt kwenye ('-o', '--output'):
            options.outfile = arg
        lasivyo opt kwenye ('-p', '--output-dir'):
            options.outpath = arg
        lasivyo opt kwenye ('-v', '--verbose'):
            options.verbose = 1
        lasivyo opt kwenye ('-V', '--version'):
            andika(_('pygettext.py (xgettext kila Python) %s') % __version__)
            sys.exit(0)
        lasivyo opt kwenye ('-w', '--width'):
            jaribu:
                options.width = int(arg)
            tatizo ValueError:
                usage(1, _('--width argument must be an integer: %s') % arg)
        lasivyo opt kwenye ('-x', '--exclude-file'):
            options.excludefilename = arg
        lasivyo opt kwenye ('-X', '--no-docstrings'):
            fp = open(arg)
            jaribu:
                wakati 1:
                    line = fp.readline()
                    ikiwa sio line:
                        koma
                    options.nodocstrings[line[:-1]] = 1
            mwishowe:
                fp.close()

    # calculate escapes
    make_escapes(sio options.escape)

    # calculate all keywords
    options.keywords.extend(default_keywords)

    # initialize list of strings to exclude
    ikiwa options.excludefilename:
        jaribu:
            ukijumuisha open(options.excludefilename) kama fp:
                options.toexclude = fp.readlines()
        tatizo IOError:
            andika(_(
                "Can't read --exclude-file: %s") % options.excludefilename, file=sys.stderr)
            sys.exit(1)
    isipokua:
        options.toexclude = []

    # resolve args to module lists
    expanded = []
    kila arg kwenye args:
        ikiwa arg == '-':
            expanded.append(arg)
        isipokua:
            expanded.extend(getFilesForName(arg))
    args = expanded

    # slurp through all the files
    eater = TokenEater(options)
    kila filename kwenye args:
        ikiwa filename == '-':
            ikiwa options.verbose:
                andika(_('Reading standard input'))
            fp = sys.stdin.buffer
            closep = 0
        isipokua:
            ikiwa options.verbose:
                andika(_('Working on %s') % filename)
            fp = open(filename, 'rb')
            closep = 1
        jaribu:
            eater.set_filename(filename)
            jaribu:
                tokens = tokenize.tokenize(fp.readline)
                kila _token kwenye tokens:
                    eater(*_token)
            tatizo tokenize.TokenError kama e:
                andika('%s: %s, line %d, column %d' % (
                    e.args[0], filename, e.args[1][0], e.args[1][1]),
                    file=sys.stderr)
        mwishowe:
            ikiwa closep:
                fp.close()

    # write the output
    ikiwa options.outfile == '-':
        fp = sys.stdout
        closep = 0
    isipokua:
        ikiwa options.outpath:
            options.outfile = os.path.join(options.outpath, options.outfile)
        fp = open(options.outfile, 'w')
        closep = 1
    jaribu:
        eater.write(fp)
    mwishowe:
        ikiwa closep:
            fp.close()


ikiwa __name__ == '__main__':
    main()
    # some more test strings
    # this one creates a warning
    _('*** Seen unexpected token "%(token)s"') % {'token': 'test'}
    _('more' 'than' 'one' 'string')
