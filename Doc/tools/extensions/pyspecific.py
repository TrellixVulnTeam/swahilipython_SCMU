# -*- coding: utf-8 -*-
"""
    pyspecific.py
    ~~~~~~~~~~~~~

    Sphinx extension ukijumuisha Python doc-specific markup.

    :copyright: 2008-2014 by Georg Brandl.
    :license: Python license.
"""

agiza re
agiza io
kutoka os agiza getenv, path
kutoka time agiza asctime
kutoka pprint agiza pformat
kutoka docutils.io agiza StringOutput
kutoka docutils.parsers.rst agiza Directive
kutoka docutils.utils agiza new_document

kutoka docutils agiza nodes, utils

kutoka sphinx agiza addnodes
kutoka sphinx.builders agiza Builder
jaribu:
    kutoka sphinx.errors agiza NoUri
tatizo ImportError:
    kutoka sphinx.environment agiza NoUri
kutoka sphinx.locale agiza translators
kutoka sphinx.util agiza status_iterator, logging
kutoka sphinx.util.nodes agiza split_explicit_title
kutoka sphinx.writers.text agiza TextWriter, TextTranslator
kutoka sphinx.writers.latex agiza LaTeXTranslator
kutoka sphinx.domains.python agiza PyModulelevel, PyClassmember

# Support kila checking kila suspicious markup

agiza suspicious


ISSUE_URI = 'https://bugs.python.org/issue%s'
SOURCE_URI = 'https://github.com/python/cpython/tree/3.8/%s'

# monkey-patch reST parser to disable alphabetic na roman enumerated lists
kutoka docutils.parsers.rst.states agiza Body
Body.enum.converters['loweralpha'] = \
    Body.enum.converters['upperalpha'] = \
    Body.enum.converters['lowerroman'] = \
    Body.enum.converters['upperroman'] = lambda x: Tupu


# Support kila marking up na linking to bugs.python.org issues

eleza issue_role(typ, rawtext, text, lineno, inliner, options={}, content=[]):
    issue = utils.unescape(text)
    text = 'bpo-' + issue
    refnode = nodes.reference(text, text, refuri=ISSUE_URI % issue)
    rudisha [refnode], []


# Support kila linking to Python source files easily

eleza source_role(typ, rawtext, text, lineno, inliner, options={}, content=[]):
    has_t, title, target = split_explicit_title(text)
    title = utils.unescape(title)
    target = utils.unescape(target)
    refnode = nodes.reference(title, title, refuri=SOURCE_URI % target)
    rudisha [refnode], []


# Support kila marking up implementation details

kundi ImplementationDetail(Directive):

    has_content = Kweli
    required_arguments = 0
    optional_arguments = 1
    final_argument_whitespace = Kweli

    # This text ni copied to templates/dummy.html
    label_text = 'CPython implementation detail:'

    eleza run(self):
        pnode = nodes.compound(classes=['impl-detail'])
        label = translators['sphinx'].gettext(self.label_text)
        content = self.content
        add_text = nodes.strong(label, label)
        ikiwa self.arguments:
            n, m = self.state.inline_text(self.arguments[0], self.lineno)
            pnode.append(nodes.paragraph('', '', *(n + m)))
        self.state.nested_parse(content, self.content_offset, pnode)
        ikiwa pnode.children na isinstance(pnode[0], nodes.paragraph):
            content = nodes.inline(pnode[0].rawsource, translatable=Kweli)
            content.source = pnode[0].source
            content.line = pnode[0].line
            content += pnode[0].children
            pnode[0].replace_self(nodes.paragraph('', '', content,
                                                  translatable=Uongo))
            pnode[0].insert(0, add_text)
            pnode[0].insert(1, nodes.Text(' '))
        isipokua:
            pnode.insert(0, nodes.paragraph('', '', add_text))
        rudisha [pnode]


# Support kila documenting platform availability

kundi Availability(Directive):

    has_content = Uongo
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = Kweli

    eleza run(self):
        availability_ref = ':ref:`Availability <availability>`: '
        pnode = nodes.paragraph(availability_ref + self.arguments[0],
                                classes=["availability"],)
        n, m = self.state.inline_text(availability_ref, self.lineno)
        pnode.extend(n + m)
        n, m = self.state.inline_text(self.arguments[0], self.lineno)
        pnode.extend(n + m)
        rudisha [pnode]


# Support kila documenting audit event

kundi AuditEvent(Directive):

    has_content = Kweli
    required_arguments = 1
    optional_arguments = 2
    final_argument_whitespace = Kweli

    _label = [
        "Raises an :ref:`auditing event <auditing>` {name} ukijumuisha no arguments.",
        "Raises an :ref:`auditing event <auditing>` {name} ukijumuisha argument {args}.",
        "Raises an :ref:`auditing event <auditing>` {name} ukijumuisha arguments {args}.",
    ]

    @property
    eleza logger(self):
        cls = type(self)
        rudisha logging.getLogger(cls.__module__ + "." + cls.__name__)

    eleza run(self):
        name = self.arguments[0]
        ikiwa len(self.arguments) >= 2 na self.arguments[1]:
            args = (a.strip() kila a kwenye self.arguments[1].strip("'\"").split(","))
            args = [a kila a kwenye args ikiwa a]
        isipokua:
            args = []

        label = translators['sphinx'].gettext(self._label[min(2, len(args))])
        text = label.format(name="``{}``".format(name),
                            args=", ".join("``{}``".format(a) kila a kwenye args ikiwa a))

        env = self.state.document.settings.env
        ikiwa sio hasattr(env, 'all_audit_events'):
            env.all_audit_events = {}

        new_info = {
            'source': [],
            'args': args
        }
        info = env.all_audit_events.setdefault(name, new_info)
        ikiwa info ni sio new_info:
            ikiwa sio self._do_args_match(info['args'], new_info['args']):
                self.logger.warn(
                    "Mismatched arguments kila audit-event {}: {!r} != {!r}"
                    .format(name, info['args'], new_info['args'])
                )

        ids = []
        jaribu:
            target = self.arguments[2].strip("\"'")
        tatizo (IndexError, TypeError):
            target = Tupu
        ikiwa sio target:
            target = "audit_event_{}_{}".format(
                re.sub(r'\W', '_', name),
                len(info['source']),
            )
            ids.append(target)

        info['source'].append((env.docname, target))

        pnode = nodes.paragraph(text, classes=["audit-hook"], ids=ids)
        ikiwa self.content:
            self.state.nested_parse(self.content, self.content_offset, pnode)
        isipokua:
            n, m = self.state.inline_text(text, self.lineno)
            pnode.extend(n + m)

        rudisha [pnode]

    # This list of sets are allowable synonyms kila event argument names.
    # If two names are kwenye the same set, they are treated kama equal kila the
    # purposes of warning. This won't help ikiwa number of arguments is
    # different!
    _SYNONYMS = [
        {"file", "path", "fd"},
    ]

    eleza _do_args_match(self, args1, args2):
        ikiwa args1 == args2:
            rudisha Kweli
        ikiwa len(args1) != len(args2):
            rudisha Uongo
        kila a1, a2 kwenye zip(args1, args2):
            ikiwa a1 == a2:
                endelea
            ikiwa any(a1 kwenye s na a2 kwenye s kila s kwenye self._SYNONYMS):
                endelea
            rudisha Uongo
        rudisha Kweli


kundi audit_event_list(nodes.General, nodes.Element):
    pita


kundi AuditEventListDirective(Directive):

    eleza run(self):
        rudisha [audit_event_list('')]


# Support kila documenting decorators

kundi PyDecoratorMixin(object):
    eleza handle_signature(self, sig, signode):
        ret = super(PyDecoratorMixin, self).handle_signature(sig, signode)
        signode.insert(0, addnodes.desc_addname('@', '@'))
        rudisha ret

    eleza needs_arglist(self):
        rudisha Uongo


kundi PyDecoratorFunction(PyDecoratorMixin, PyModulelevel):
    eleza run(self):
        # a decorator function ni a function after all
        self.name = 'py:function'
        rudisha PyModulelevel.run(self)


kundi PyDecoratorMethod(PyDecoratorMixin, PyClassmember):
    eleza run(self):
        self.name = 'py:method'
        rudisha PyClassmember.run(self)


kundi PyCoroutineMixin(object):
    eleza handle_signature(self, sig, signode):
        ret = super(PyCoroutineMixin, self).handle_signature(sig, signode)
        signode.insert(0, addnodes.desc_annotation('coroutine ', 'coroutine '))
        rudisha ret


kundi PyAwaitableMixin(object):
    eleza handle_signature(self, sig, signode):
        ret = super(PyAwaitableMixin, self).handle_signature(sig, signode)
        signode.insert(0, addnodes.desc_annotation('awaitable ', 'awaitable '))
        rudisha ret


kundi PyCoroutineFunction(PyCoroutineMixin, PyModulelevel):
    eleza run(self):
        self.name = 'py:function'
        rudisha PyModulelevel.run(self)


kundi PyCoroutineMethod(PyCoroutineMixin, PyClassmember):
    eleza run(self):
        self.name = 'py:method'
        rudisha PyClassmember.run(self)


kundi PyAwaitableFunction(PyAwaitableMixin, PyClassmember):
    eleza run(self):
        self.name = 'py:function'
        rudisha PyClassmember.run(self)


kundi PyAwaitableMethod(PyAwaitableMixin, PyClassmember):
    eleza run(self):
        self.name = 'py:method'
        rudisha PyClassmember.run(self)


kundi PyAbstractMethod(PyClassmember):

    eleza handle_signature(self, sig, signode):
        ret = super(PyAbstractMethod, self).handle_signature(sig, signode)
        signode.insert(0, addnodes.desc_annotation('abstractmethod ',
                                                   'abstractmethod '))
        rudisha ret

    eleza run(self):
        self.name = 'py:method'
        rudisha PyClassmember.run(self)


# Support kila documenting version of removal kwenye deprecations

kundi DeprecatedRemoved(Directive):
    has_content = Kweli
    required_arguments = 2
    optional_arguments = 1
    final_argument_whitespace = Kweli
    option_spec = {}

    _label = 'Deprecated since version {deprecated}, will be removed kwenye version {removed}'

    eleza run(self):
        node = addnodes.versionmodified()
        node.document = self.state.document
        node['type'] = 'deprecated-removed'
        version = (self.arguments[0], self.arguments[1])
        node['version'] = version
        label = translators['sphinx'].gettext(self._label)
        text = label.format(deprecated=self.arguments[0], removed=self.arguments[1])
        ikiwa len(self.arguments) == 3:
            inodes, messages = self.state.inline_text(self.arguments[2],
                                                      self.lineno+1)
            para = nodes.paragraph(self.arguments[2], '', *inodes, translatable=Uongo)
            node.append(para)
        isipokua:
            messages = []
        ikiwa self.content:
            self.state.nested_parse(self.content, self.content_offset, node)
        ikiwa len(node):
            ikiwa isinstance(node[0], nodes.paragraph) na node[0].rawsource:
                content = nodes.inline(node[0].rawsource, translatable=Kweli)
                content.source = node[0].source
                content.line = node[0].line
                content += node[0].children
                node[0].replace_self(nodes.paragraph('', '', content, translatable=Uongo))
            node[0].insert(0, nodes.inline('', '%s: ' % text,
                                           classes=['versionmodified']))
        isipokua:
            para = nodes.paragraph('', '',
                                   nodes.inline('', '%s.' % text,
                                                classes=['versionmodified']),
                                   translatable=Uongo)
            node.append(para)
        env = self.state.document.settings.env
        env.get_domain('changeset').note_changeset(node)
        rudisha [node] + messages


# Support kila including Misc/NEWS

issue_re = re.compile('(?:[Ii]ssue #|bpo-)([0-9]+)')
whatsnew_re = re.compile(r"(?im)^what's new kwenye (.*?)\??$")


kundi MiscNews(Directive):
    has_content = Uongo
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = Uongo
    option_spec = {}

    eleza run(self):
        fname = self.arguments[0]
        source = self.state_machine.input_lines.source(
            self.lineno - self.state_machine.input_offset - 1)
        source_dir = getenv('PY_MISC_NEWS_DIR')
        ikiwa sio source_dir:
            source_dir = path.dirname(path.abspath(source))
        fpath = path.join(source_dir, fname)
        self.state.document.settings.record_dependencies.add(fpath)
        jaribu:
            ukijumuisha io.open(fpath, encoding='utf-8') kama fp:
                content = fp.read()
        tatizo Exception:
            text = 'The NEWS file ni sio available.'
            node = nodes.strong(text, text)
            rudisha [node]
        content = issue_re.sub(r'`bpo-\1 <https://bugs.python.org/issue\1>`__',
                               content)
        content = whatsnew_re.sub(r'\1', content)
        # remove first 3 lines kama they are the main heading
        lines = ['.. default-role:: obj', ''] + content.splitlines()[3:]
        self.state_machine.insert_input(lines, fname)
        rudisha []


# Support kila building "topic help" kila pydoc

pydoc_topic_labels = [
    'assert', 'assignment', 'async', 'atom-identifiers', 'atom-literals',
    'attribute-access', 'attribute-references', 'augassign', 'await',
    'binary', 'bitwise', 'bltin-code-objects', 'bltin-ellipsis-object',
    'bltin-null-object', 'bltin-type-objects', 'booleans',
    'koma', 'callable-types', 'calls', 'class', 'comparisons', 'compound',
    'context-managers', 'endelea', 'conversions', 'customization', 'debugger',
    'del', 'dict', 'dynamic-features', 'else', 'exceptions', 'execmodel',
    'exprlists', 'floating', 'for', 'formatstrings', 'function', 'global',
    'id-classes', 'identifiers', 'if', 'imaginary', 'agiza', 'in', 'integers',
    'lambda', 'lists', 'naming', 'nonlocal', 'numbers', 'numeric-types',
    'objects', 'operator-summary', 'pita', 'power', 'raise', 'return',
    'sequence-types', 'shifting', 'slicings', 'specialattrs', 'specialnames',
    'string-methods', 'strings', 'subscriptions', 'truth', 'try', 'types',
    'typesfunctions', 'typesmapping', 'typesmethods', 'typesmodules',
    'typesseq', 'typesseq-mutable', 'unary', 'while', 'with', 'yield'
]


kundi PydocTopicsBuilder(Builder):
    name = 'pydoc-topics'

    default_translator_class = TextTranslator

    eleza init(self):
        self.topics = {}
        self.secnumbers = {}

    eleza get_outdated_docs(self):
        rudisha 'all pydoc topics'

    eleza get_target_uri(self, docname, typ=Tupu):
        rudisha ''  # no URIs

    eleza write(self, *ignored):
        writer = TextWriter(self)
        kila label kwenye status_iterator(pydoc_topic_labels,
                                     'building topics... ',
                                     length=len(pydoc_topic_labels)):
            ikiwa label haiko kwenye self.env.domaindata['std']['labels']:
                self.env.logger.warn('label %r haiko kwenye documentation' % label)
                endelea
            docname, labelid, sectname = self.env.domaindata['std']['labels'][label]
            doctree = self.env.get_and_resolve_doctree(docname, self)
            document = new_document('<section node>')
            document.append(doctree.ids[labelid])
            destination = StringOutput(encoding='utf-8')
            writer.write(document, destination)
            self.topics[label] = writer.output

    eleza finish(self):
        f = open(path.join(self.outdir, 'topics.py'), 'wb')
        jaribu:
            f.write('# -*- coding: utf-8 -*-\n'.encode('utf-8'))
            f.write(('# Autogenerated by Sphinx on %s\n' % asctime()).encode('utf-8'))
            f.write(('topics = ' + pformat(self.topics) + '\n').encode('utf-8'))
        mwishowe:
            f.close()


# Support kila documenting Opcodes

opcode_sig_re = re.compile(r'(\w+(?:\+\d)?)(?:\s*\((.*)\))?')


eleza parse_opcode_signature(env, sig, signode):
    """Transform an opcode signature into RST nodes."""
    m = opcode_sig_re.match(sig)
    ikiwa m ni Tupu:
        ashiria ValueError
    opname, arglist = m.groups()
    signode += addnodes.desc_name(opname, opname)
    ikiwa arglist ni sio Tupu:
        paramlist = addnodes.desc_parameterlist()
        signode += paramlist
        paramlist += addnodes.desc_parameter(arglist, arglist)
    rudisha opname.strip()


# Support kila documenting pdb commands

pdbcmd_sig_re = re.compile(r'([a-z()!]+)\s*(.*)')

# later...
# pdbargs_tokens_re = re.compile(r'''[a-zA-Z]+  |  # identifiers
#                                   [.,:]+     |  # punctuation
#                                   [\[\]()]   |  # parens
#                                   \s+           # whitespace
#                                   ''', re.X)


eleza parse_pdb_command(env, sig, signode):
    """Transform a pdb command signature into RST nodes."""
    m = pdbcmd_sig_re.match(sig)
    ikiwa m ni Tupu:
        ashiria ValueError
    name, args = m.groups()
    fullname = name.replace('(', '').replace(')', '')
    signode += addnodes.desc_name(name, name)
    ikiwa args:
        signode += addnodes.desc_addname(' '+args, ' '+args)
    rudisha fullname


eleza process_audit_events(app, doctree, kutokadocname):
    kila node kwenye doctree.traverse(audit_event_list):
        koma
    isipokua:
        rudisha

    env = app.builder.env

    table = nodes.table(cols=3)
    group = nodes.tgroup(
        '',
        nodes.colspec(colwidth=30),
        nodes.colspec(colwidth=55),
        nodes.colspec(colwidth=15),
        cols=3,
    )
    head = nodes.thead()
    body = nodes.tbody()

    table += group
    group += head
    group += body

    row = nodes.row()
    row += nodes.entry('', nodes.paragraph('', nodes.Text('Audit event')))
    row += nodes.entry('', nodes.paragraph('', nodes.Text('Arguments')))
    row += nodes.entry('', nodes.paragraph('', nodes.Text('References')))
    head += row

    kila name kwenye sorted(getattr(env, "all_audit_events", ())):
        audit_event = env.all_audit_events[name]

        row = nodes.row()
        node = nodes.paragraph('', nodes.Text(name))
        row += nodes.entry('', node)

        node = nodes.paragraph()
        kila i, a kwenye enumerate(audit_event['args']):
            ikiwa i:
                node += nodes.Text(", ")
            node += nodes.literal(a, nodes.Text(a))
        row += nodes.entry('', node)

        node = nodes.paragraph()
        backlinks = enumerate(sorted(set(audit_event['source'])), start=1)
        kila i, (doc, label) kwenye backlinks:
            ikiwa isinstance(label, str):
                ref = nodes.reference("", nodes.Text("[{}]".format(i)), internal=Kweli)
                jaribu:
                    ref['refuri'] = "{}#{}".format(
                        app.builder.get_relative_uri(kutokadocname, doc),
                        label,
                    )
                tatizo NoUri:
                    endelea
                node += ref
        row += nodes.entry('', node)

        body += row

    kila node kwenye doctree.traverse(audit_event_list):
        node.replace_self(table)


eleza setup(app):
    app.add_role('issue', issue_role)
    app.add_role('source', source_role)
    app.add_directive('impl-detail', ImplementationDetail)
    app.add_directive('availability', Availability)
    app.add_directive('audit-event', AuditEvent)
    app.add_directive('audit-event-table', AuditEventListDirective)
    app.add_directive('deprecated-removed', DeprecatedRemoved)
    app.add_builder(PydocTopicsBuilder)
    app.add_builder(suspicious.CheckSuspiciousMarkupBuilder)
    app.add_object_type('opcode', 'opcode', '%s (opcode)', parse_opcode_signature)
    app.add_object_type('pdbcommand', 'pdbcmd', '%s (pdb command)', parse_pdb_command)
    app.add_object_type('2to3fixer', '2to3fixer', '%s (2to3 fixer)')
    app.add_directive_to_domain('py', 'decorator', PyDecoratorFunction)
    app.add_directive_to_domain('py', 'decoratormethod', PyDecoratorMethod)
    app.add_directive_to_domain('py', 'coroutinefunction', PyCoroutineFunction)
    app.add_directive_to_domain('py', 'coroutinemethod', PyCoroutineMethod)
    app.add_directive_to_domain('py', 'awaitablefunction', PyAwaitableFunction)
    app.add_directive_to_domain('py', 'awaitablemethod', PyAwaitableMethod)
    app.add_directive_to_domain('py', 'abstractmethod', PyAbstractMethod)
    app.add_directive('miscnews', MiscNews)
    app.connect('doctree-resolved', process_audit_events)
    rudisha {'version': '1.0', 'parallel_read_safe': Kweli}
