#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Check kila stylistic na formal issues kwenye .rst na .py
# files included kwenye the documentation.
#
# 01/2009, Georg Brandl

# TODO: - wrong versions kwenye versionadded/changed
#       - wrong markup after versionchanged directive

agiza os
agiza re
agiza sys
agiza getopt
kutoka os.path agiza join, splitext, abspath, exists
kutoka collections agiza defaultdict

directives = [
    # standard docutils ones
    'admonition', 'attention', 'caution', 'class', 'compound', 'container',
    'contents', 'csv-table', 'danger', 'date', 'default-role', 'epigraph',
    'error', 'figure', 'footer', 'header', 'highlights', 'hint', 'image',
    'agizaant', 'include', 'line-block', 'list-table', 'meta', 'note',
    'parsed-literal', 'pull-quote', 'raw', 'replace',
    'restructuredtext-test-directive', 'role', 'rubric', 'sectnum', 'sidebar',
    'table', 'target-notes', 'tip', 'title', 'topic', 'unicode', 'warning',
    # Sphinx na Python docs custom ones
    'acks', 'attribute', 'autoattribute', 'autoclass', 'autodata',
    'autoexception', 'autofunction', 'automethod', 'automodule',
    'availability', 'centered', 'cfunction', 'class', 'classmethod', 'cmacro',
    'cmdoption', 'cmember', 'code-block', 'confval', 'cssclass', 'ctype',
    'currentmodule', 'cvar', 'data', 'decorator', 'decoratormethod',
    'deprecated-removed', 'deprecated(?!-removed)', 'describe', 'directive',
    'doctest', 'envvar', 'event', 'exception', 'function', 'glossary',
    'highlight', 'highlightlang', 'impl-detail', 'index', 'literalinclude',
    'method', 'miscnews', 'module', 'moduleauthor', 'opcode', 'pdbcommand',
    'productionlist', 'program', 'role', 'sectionauthor', 'seealso',
    'sourcecode', 'staticmethod', 'tabularcolumns', 'testcode', 'testoutput',
    'testsetup', 'toctree', 'todo', 'todolist', 'versionadded',
    'versionchanged'
]

all_directives = '(' + '|'.join(directives) + ')'
seems_directive_re = re.compile(r'(?<!\.)\.\. %s([^a-z:]|:(?!:))' % all_directives)
default_role_re = re.compile(r'(^| )`\w([^`]*?\w)?`($| )')
leaked_markup_re = re.compile(r'[a-z]::\s|`|\.\.\s*\w+:')


checkers = {}

checker_props = {'severity': 1, 'falsepositives': Uongo}


eleza checker(*suffixes, **kwds):
    """Decorator to register a function kama a checker."""
    eleza deco(func):
        kila suffix kwenye suffixes:
            checkers.setdefault(suffix, []).append(func)
        kila prop kwenye checker_props:
            setattr(func, prop, kwds.get(prop, checker_props[prop]))
        rudisha func
    rudisha deco


@checker('.py', severity=4)
eleza check_syntax(fn, lines):
    """Check Python examples kila valid syntax."""
    code = ''.join(lines)
    ikiwa '\r' kwenye code:
        ikiwa os.name != 'nt':
            tuma 0, '\\r kwenye code file'
        code = code.replace('\r', '')
    jaribu:
        compile(code, fn, 'exec')
    tatizo SyntaxError kama err:
        tuma err.lineno, 'not compilable: %s' % err


@checker('.rst', severity=2)
eleza check_suspicious_constructs(fn, lines):
    """Check kila suspicious reST constructs."""
    inprod = Uongo
    kila lno, line kwenye enumerate(lines):
        ikiwa seems_directive_re.search(line):
            tuma lno+1, 'comment seems to be intended kama a directive'
        ikiwa '.. productionlist::' kwenye line:
            inprod = Kweli
        lasivyo sio inprod na default_role_re.search(line):
            tuma lno+1, 'default role used'
        lasivyo inprod na sio line.strip():
            inprod = Uongo


@checker('.py', '.rst')
eleza check_whitespace(fn, lines):
    """Check kila whitespace na line length issues."""
    kila lno, line kwenye enumerate(lines):
        ikiwa '\r' kwenye line:
            tuma lno+1, '\\r kwenye line'
        ikiwa '\t' kwenye line:
            tuma lno+1, 'OMG TABS!!!1'
        ikiwa line[:-1].rstrip(' \t') != line[:-1]:
            tuma lno+1, 'trailing whitespace'


@checker('.rst', severity=0)
eleza check_line_length(fn, lines):
    """Check kila line length; this checker ni sio run by default."""
    kila lno, line kwenye enumerate(lines):
        ikiwa len(line) > 81:
            # don't complain about tables, links na function signatures
            ikiwa line.lstrip()[0] haiko kwenye '+|' na \
               'http://' haiko kwenye line na \
               sio line.lstrip().startswith(('.. function',
                                             '.. method',
                                             '.. cfunction')):
                tuma lno+1, "line too long"


@checker('.html', severity=2, falsepositives=Kweli)
eleza check_leaked_markup(fn, lines):
    """Check HTML files kila leaked reST markup; this only works if
    the HTML files have been built.
    """
    kila lno, line kwenye enumerate(lines):
        ikiwa leaked_markup_re.search(line):
            tuma lno+1, 'possibly leaked markup: %r' % line


eleza main(argv):
    usage = '''\
Usage: %s [-v] [-f] [-s sev] [-i path]* [path]

Options:  -v       verbose (print all checked file names)
          -f       enable checkers that tuma many false positives
          -s sev   only show problems ukijumuisha severity >= sev
          -i path  ignore subdir ama file path
''' % argv[0]
    jaribu:
        gopts, args = getopt.getopt(argv[1:], 'vfs:i:')
    tatizo getopt.GetoptError:
        andika(usage)
        rudisha 2

    verbose = Uongo
    severity = 1
    ignore = []
    falsepos = Uongo
    kila opt, val kwenye gopts:
        ikiwa opt == '-v':
            verbose = Kweli
        lasivyo opt == '-f':
            falsepos = Kweli
        lasivyo opt == '-s':
            severity = int(val)
        lasivyo opt == '-i':
            ignore.append(abspath(val))

    ikiwa len(args) == 0:
        path = '.'
    lasivyo len(args) == 1:
        path = args[0]
    isipokua:
        andika(usage)
        rudisha 2

    ikiwa sio exists(path):
        andika('Error: path %s does sio exist' % path)
        rudisha 2

    count = defaultdict(int)

    kila root, dirs, files kwenye os.walk(path):
        # ignore subdirs kwenye ignore list
        ikiwa abspath(root) kwenye ignore:
            toa dirs[:]
            endelea

        kila fn kwenye files:
            fn = join(root, fn)
            ikiwa fn[:2] == './':
                fn = fn[2:]

            # ignore files kwenye ignore list
            ikiwa abspath(fn) kwenye ignore:
                endelea

            ext = splitext(fn)[1]
            checkerlist = checkers.get(ext, Tupu)
            ikiwa sio checkerlist:
                endelea

            ikiwa verbose:
                andika('Checking %s...' % fn)

            jaribu:
                ukijumuisha open(fn, 'r', encoding='utf-8') kama f:
                    lines = list(f)
            tatizo (IOError, OSError) kama err:
                andika('%s: cannot open: %s' % (fn, err))
                count[4] += 1
                endelea

            kila checker kwenye checkerlist:
                ikiwa checker.falsepositives na sio falsepos:
                    endelea
                csev = checker.severity
                ikiwa csev >= severity:
                    kila lno, msg kwenye checker(fn, lines):
                        andika('[%d] %s:%d: %s' % (csev, fn, lno, msg))
                        count[csev] += 1
    ikiwa verbose:
        andika()
    ikiwa sio count:
        ikiwa severity > 1:
            andika('No problems ukijumuisha severity >= %d found.' % severity)
        isipokua:
            andika('No problems found.')
    isipokua:
        kila severity kwenye sorted(count):
            number = count[severity]
            andika('%d problem%s ukijumuisha severity %d found.' %
                  (number, number > 1 na 's' ama '', severity))
    rudisha int(bool(count))


ikiwa __name__ == '__main__':
    sys.exit(main(sys.argv))
