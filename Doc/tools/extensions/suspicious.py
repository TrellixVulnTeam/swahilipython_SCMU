"""
Try to detect suspicious constructs, resembling markup
that has leaked into the final output.

Suspicious lines are reported kwenye a comma-separated-file,
``suspicious.csv``, located kwenye the output directory.

The file ni utf-8 encoded, na each line contains four fields:

 * document name (normalized)
 * line number kwenye the source document
 * problematic text
 * complete line showing the problematic text kwenye context

It ni common to find many false positives. To avoid reporting them
again na again, they may be added to the ``ignored.csv`` file
(located kwenye the configuration directory). The file has the same
format kama ``suspicious.csv`` ukijumuisha a few differences:

  - each line defines a rule; ikiwa the rule matches, the issue
    ni ignored.
  - line number may be empty (that is, nothing between the
    commas: ",,"). In this case, line numbers are ignored (the
    rule matches anywhere kwenye the file).
  - the last field does sio have to be a complete line; some
    surrounding text (never more than a line) ni enough for
    context.

Rules are processed sequentially. A rule matches when:

 * document names are the same
 * problematic texts are the same
 * line numbers are close to each other (5 lines up ama down)
 * the rule text ni completely contained into the source line

The simplest way to create the ignored.csv file ni by copying
undesired entries kutoka suspicious.csv (possibly trimming the last
field.)

Copyright 2009 Gabriel A. Genellina

"""

agiza os
agiza re
agiza csv
agiza sys

kutoka docutils agiza nodes
kutoka sphinx.builders agiza Builder
agiza sphinx.util

detect_all = re.compile(r'''
    ::(?=[^=])|            # two :: (but NOT ::=)
    :[a-zA-Z][a-zA-Z0-9]+| # :foo
    `|                     # ` (seldom used by itself)
    (?<!\.)\.\.[ \t]*\w+:  # .. foo: (but NOT ... isipokua:)
    ''', re.UNICODE | re.VERBOSE).finditer

py3 = sys.version_info >= (3, 0)


kundi Rule:
    eleza __init__(self, docname, lineno, issue, line):
        """A rule kila ignoring issues"""
        self.docname = docname # document to which this rule applies
        self.lineno = lineno   # line number kwenye the original source;
                               # this rule matches only near that.
                               # Tupu -> don't care
        self.issue = issue     # the markup fragment that triggered this rule
        self.line = line       # text of the container element (single line only)
        self.used = Uongo

    eleza __repr__(self):
        rudisha '{0.docname},,{0.issue},{0.line}'.format(self)



kundi dialect(csv.excel):
    """Our dialect: uses only linefeed kama newline."""
    lineterminator = '\n'


kundi CheckSuspiciousMarkupBuilder(Builder):
    """
    Checks kila possibly invalid markup that may leak into the output.
    """
    name = 'suspicious'
    logger = sphinx.util.logging.getLogger("CheckSuspiciousMarkupBuilder")

    eleza init(self):
        # create output file
        self.log_file_name = os.path.join(self.outdir, 'suspicious.csv')
        open(self.log_file_name, 'w').close()
        # load database of previously ignored issues
        self.load_rules(os.path.join(os.path.dirname(__file__), '..',
                                     'susp-ignored.csv'))

    eleza get_outdated_docs(self):
        rudisha self.env.found_docs

    eleza get_target_uri(self, docname, typ=Tupu):
        rudisha ''

    eleza prepare_writing(self, docnames):
        pita

    eleza write_doc(self, docname, doctree):
        # set when any issue ni encountered kwenye this document
        self.any_issue = Uongo
        self.docname = docname
        visitor = SuspiciousVisitor(doctree, self)
        doctree.walk(visitor)

    eleza finish(self):
        unused_rules = [rule kila rule kwenye self.rules ikiwa sio rule.used]
        ikiwa unused_rules:
            self.logger.warning(
                'Found %s/%s unused rules: %s' % (
                    len(unused_rules), len(self.rules),
                    ''.join(repr(rule) kila rule kwenye unused_rules),
                )
            )
        rudisha

    eleza check_issue(self, line, lineno, issue):
        ikiwa sio self.is_ignored(line, lineno, issue):
            self.report_issue(line, lineno, issue)

    eleza is_ignored(self, line, lineno, issue):
        """Determine whether this issue should be ignored."""
        docname = self.docname
        kila rule kwenye self.rules:
            ikiwa rule.docname != docname: endelea
            ikiwa rule.issue != issue: endelea
            # Both lines must match *exactly*. This ni rather strict,
            # na probably should be improved.
            # Doing fuzzy matches ukijumuisha levenshtein distance could work,
            # but that means bringing other libraries...
            # Ok, relax that requirement: just check ikiwa the rule fragment
            # ni contained kwenye the document line
            ikiwa rule.line haiko kwenye line: endelea
            # Check both line numbers. If they're "near"
            # this rule matches. (lineno=Tupu means "don't care")
            ikiwa (rule.lineno ni sio Tupu) na \
                abs(rule.lineno - lineno) > 5: endelea
            # ikiwa it came this far, the rule matched
            rule.used = Kweli
            rudisha Kweli
        rudisha Uongo

    eleza report_issue(self, text, lineno, issue):
        self.any_issue = Kweli
        self.write_log_entry(lineno, issue, text)
        ikiwa py3:
            self.logger.warning('[%s:%d] "%s" found kwenye "%-.120s"' %
                                (self.docname, lineno, issue, text))
        isipokua:
            self.logger.warning(
                '[%s:%d] "%s" found kwenye "%-.120s"' % (
                    self.docname.encode(sys.getdefaultencoding(),'replace'),
                    lineno,
                    issue.encode(sys.getdefaultencoding(),'replace'),
                    text.strip().encode(sys.getdefaultencoding(),'replace')))
        self.app.statuscode = 1

    eleza write_log_entry(self, lineno, issue, text):
        ikiwa py3:
            f = open(self.log_file_name, 'a')
            writer = csv.writer(f, dialect)
            writer.writerow([self.docname, lineno, issue, text.strip()])
            f.close()
        isipokua:
            f = open(self.log_file_name, 'ab')
            writer = csv.writer(f, dialect)
            writer.writerow([self.docname.encode('utf-8'),
                             lineno,
                             issue.encode('utf-8'),
                             text.strip().encode('utf-8')])
            f.close()

    eleza load_rules(self, filename):
        """Load database of previously ignored issues.

        A csv file, ukijumuisha exactly the same format kama suspicious.csv
        Fields: document name (normalized), line number, issue, surrounding text
        """
        self.logger.info("loading ignore rules... ", nonl=1)
        self.rules = rules = []
        jaribu:
            ikiwa py3:
                f = open(filename, 'r')
            isipokua:
                f = open(filename, 'rb')
        tatizo IOError:
            rudisha
        kila i, row kwenye enumerate(csv.reader(f)):
            ikiwa len(row) != 4:
                ashiria ValueError(
                    "wrong format kwenye %s, line %d: %s" % (filename, i+1, row))
            docname, lineno, issue, text = row
            ikiwa lineno:
                lineno = int(lineno)
            isipokua:
                lineno = Tupu
            ikiwa sio py3:
                docname = docname.decode('utf-8')
                issue = issue.decode('utf-8')
                text = text.decode('utf-8')
            rule = Rule(docname, lineno, issue, text)
            rules.append(rule)
        f.close()
        self.logger.info('done, %d rules loaded' % len(self.rules))


eleza get_lineno(node):
    """Obtain line number information kila a node."""
    lineno = Tupu
    wakati lineno ni Tupu na node:
        node = node.parent
        lineno = node.line
    rudisha lineno


eleza extract_line(text, index):
    """text may be a multiline string; extract
    only the line containing the given character index.

    >>> extract_line("abc\ndefgh\ni", 6)
    >>> 'defgh'
    >>> kila i kwenye (0, 2, 3, 4, 10):
    ...   print extract_line("abc\ndefgh\ni", i)
    abc
    abc
    abc
    defgh
    defgh
    i
    """
    p = text.rfind('\n', 0, index) + 1
    q = text.find('\n', index)
    ikiwa q < 0:
        q = len(text)
    rudisha text[p:q]


kundi SuspiciousVisitor(nodes.GenericNodeVisitor):

    lastlineno = 0

    eleza __init__(self, document, builder):
        nodes.GenericNodeVisitor.__init__(self, document)
        self.builder = builder

    eleza default_visit(self, node):
        ikiwa isinstance(node, (nodes.Text, nodes.image)): # direct text containers
            text = node.astext()
            # lineno seems to go backwards sometimes (?)
            self.lastlineno = lineno = max(get_lineno(node) ama 0, self.lastlineno)
            seen = set() # don't report the same issue more than only once per line
            kila match kwenye detect_all(text):
                issue = match.group()
                line = extract_line(text, match.start())
                ikiwa (issue, line) haiko kwenye seen:
                    self.builder.check_issue(line, lineno, issue)
                    seen.add((issue, line))

    unknown_visit = default_visit

    eleza visit_document(self, node):
        self.lastlineno = 0

    eleza visit_comment(self, node):
        # ignore comments -- too much false positives.
        # (although doing this could miss some errors;
        # there were two sections "commented-out" by mistake
        # kwenye the Python docs that would sio be caught)
        ashiria nodes.SkipNode
