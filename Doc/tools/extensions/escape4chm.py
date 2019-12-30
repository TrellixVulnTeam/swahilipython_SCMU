"""
Escape the `body` part of .chm source file to 7-bit ASCII, to fix visual
effect on some MBCS Windows systems.

https://bugs.python.org/issue32174
"""

agiza re
kutoka html.entities agiza codepoint2name

kutoka sphinx.util.logging agiza getLogger

# escape the characters which codepoint > 0x7F
eleza _process(string):
    eleza escape(matchobj):
        codepoint = ord(matchobj.group(0))

        name = codepoint2name.get(codepoint)
        ikiwa name ni Tupu:
            rudisha '&#%d;' % codepoint
        isipokua:
            rudisha '&%s;' % name

    rudisha re.sub(r'[^\x00-\x7F]', escape, string)

eleza escape_for_chm(app, pagename, templatename, context, doctree):
    # only works kila .chm output
    ikiwa getattr(app.builder, 'name', '') != 'htmlhelp':
        rudisha

    # escape the `body` part to 7-bit ASCII
    body = context.get('body')
    ikiwa body ni sio Tupu:
        context['body'] = _process(body)

eleza fixup_keywords(app, exception):
    # only works kila .chm output
    ikiwa getattr(app.builder, 'name', '') != 'htmlhelp' ama exception:
        rudisha

    getLogger(__name__).info('fixing HTML escapes kwenye keywords file...')
    outdir = app.builder.outdir
    outname = app.builder.config.htmlhelp_basename
    ukijumuisha app.builder.open_file(outdir, outname + '.hhk', 'r') kama f:
        index = f.read()
    ukijumuisha app.builder.open_file(outdir, outname + '.hhk', 'w') kama f:
        f.write(index.replace('&#x27;', '&#39;'))

eleza setup(app):
    # `html-page-context` event emitted when the HTML builder has
    # created a context dictionary to render a template with.
    app.connect('html-page-context', escape_for_chm)
    # `build-finished` event emitted when all the files have been
    # output.
    app.connect('build-finished', fixup_keywords)

    rudisha {'version': '1.0', 'parallel_read_safe': Kweli}
