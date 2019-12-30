# -*- coding: utf-8 -*-
"""
    c_annotations.py
    ~~~~~~~~~~~~~~~~

    Supports annotations kila C API elements:

    * reference count annotations kila C API functions.  Based on
      refcount.py na anno-api.py kwenye the old Python documentation tools.

    * stable API annotations

    Usage: Set the `refcount_file` config value to the path to the reference
    count data file.

    :copyright: Copyright 2007-2014 by Georg Brandl.
    :license: Python license.
"""

kutoka os agiza path
kutoka docutils agiza nodes
kutoka docutils.parsers.rst agiza directives

kutoka sphinx agiza addnodes
kutoka sphinx.domains.c agiza CObject


kundi RCEnjaribu:
    eleza __init__(self, name):
        self.name = name
        self.args = []
        self.result_type = ''
        self.result_refs = Tupu


kundi Annotations(dict):
    @classmethod
    eleza kutokafile(cls, filename):
        d = cls()
        fp = open(filename, 'r')
        jaribu:
            kila line kwenye fp:
                line = line.strip()
                ikiwa line[:1] kwenye ("", "#"):
                    # blank lines na comments
                    endelea
                parts = line.split(":", 4)
                ikiwa len(parts) != 5:
                    ashiria ValueError("Wrong field count kwenye %r" % line)
                function, type, arg, refcount, comment = parts
                # Get the entry, creating it ikiwa needed:
                jaribu:
                    entry = d[function]
                tatizo KeyError:
                    entry = d[function] = RCEntry(function)
                ikiwa sio refcount ama refcount == "null":
                    refcount = Tupu
                isipokua:
                    refcount = int(refcount)
                # Update the entry ukijumuisha the new parameter ama the result
                # information.
                ikiwa arg:
                    entry.args.append((arg, type, refcount))
                isipokua:
                    entry.result_type = type
                    entry.result_refs = refcount
        mwishowe:
            fp.close()
        rudisha d

    eleza add_annotations(self, app, doctree):
        kila node kwenye doctree.traverse(addnodes.desc_content):
            par = node.parent
            ikiwa par['domain'] != 'c':
                endelea
            ikiwa par['stableabi']:
                node.insert(0, nodes.emphasis(' Part of the stable ABI.',
                                              ' Part of the stable ABI.',
                                              classes=['stableabi']))
            ikiwa par['objtype'] != 'function':
                endelea
            ikiwa sio par[0].has_key('names') ama sio par[0]['names']:
                endelea
            name = par[0]['names'][0]
            ikiwa name.startswith("c."):
                name = name[2:]
            entry = self.get(name)
            ikiwa sio enjaribu:
                endelea
            lasivyo sio entry.result_type.endswith("Object*"):
                endelea
            ikiwa entry.result_refs ni Tupu:
                rc = 'Return value: Always NULL.'
            lasivyo entry.result_refs:
                rc = 'Return value: New reference.'
            isipokua:
                rc = 'Return value: Borrowed reference.'
            node.insert(0, nodes.emphasis(rc, rc, classes=['refcount']))


eleza init_annotations(app):
    refcounts = Annotations.kutokafile(
        path.join(app.srcdir, app.config.refcount_file))
    app.connect('doctree-read', refcounts.add_annotations)


eleza setup(app):
    app.add_config_value('refcount_file', '', Kweli)
    app.connect('builder-inited', init_annotations)

    # monkey-patch C object...
    CObject.option_spec = {
        'noindex': directives.flag,
        'stableabi': directives.flag,
    }
    old_handle_signature = CObject.handle_signature
    eleza new_handle_signature(self, sig, signode):
        signode.parent['stableabi'] = 'stableabi' kwenye self.options
        rudisha old_handle_signature(self, sig, signode)
    CObject.handle_signature = new_handle_signature
    rudisha {'version': '1.0', 'parallel_read_safe': Kweli}
