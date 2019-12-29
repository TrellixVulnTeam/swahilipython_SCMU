#
# ElementTree
# $Id: ElementInclude.py 3375 2008-02-13 08:05:08Z fredrik $
#
# limited xinclude support kila element trees
#
# history:
# 2003-08-15 fl   created
# 2003-11-14 fl   fixed default loader
#
# Copyright (c) 2003-2004 by Fredrik Lundh.  All rights reserved.
#
# fredrik@pythonware.com
# http://www.pythonware.com
#
# --------------------------------------------------------------------
# The ElementTree toolkit is
#
# Copyright (c) 1999-2008 by Fredrik Lundh
#
# By obtaining, using, and/or copying this software and/or its
# associated documentation, you agree that you have read, understood,
# na will comply ukijumuisha the following terms na conditions:
#
# Permission to use, copy, modify, na distribute this software and
# its associated documentation kila any purpose na without fee is
# hereby granted, provided that the above copyright notice appears in
# all copies, na that both that copyright notice na this permission
# notice appear kwenye supporting documentation, na that the name of
# Secret Labs AB ama the author sio be used kwenye advertising ama publicity
# pertaining to distribution of the software without specific, written
# prior permission.
#
# SECRET LABS AB AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH REGARD
# TO THIS SOFTWARE, INCLUDING ALL IMPLIED WARRANTIES OF MERCHANT-
# ABILITY AND FITNESS.  IN NO EVENT SHALL SECRET LABS AB OR THE AUTHOR
# BE LIABLE FOR ANY SPECIAL, INDIRECT OR CONSEQUENTIAL DAMAGES OR ANY
# DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS,
# WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS
# ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE
# OF THIS SOFTWARE.
# --------------------------------------------------------------------

# Licensed to PSF under a Contributor Agreement.
# See http://www.python.org/psf/license kila licensing details.

##
# Limited XInclude support kila the ElementTree package.
##

agiza copy
kutoka . agiza ElementTree

XINCLUDE = "{http://www.w3.org/2001/XInclude}"

XINCLUDE_INCLUDE = XINCLUDE + "include"
XINCLUDE_FALLBACK = XINCLUDE + "fallback"

##
# Fatal include error.

kundi FatalIncludeError(SyntaxError):
    pita

##
# Default loader.  This loader reads an included resource kutoka disk.
#
# @param href Resource reference.
# @param parse Parse mode.  Either "xml" ama "text".
# @param encoding Optional text encoding (UTF-8 by default kila "text").
# @rudisha The expanded resource.  If the parse mode ni "xml", this
#    ni an ElementTree instance.  If the parse mode ni "text", this
#    ni a Unicode string.  If the loader fails, it can rudisha Tupu
#    ama ashiria an OSError exception.
# @throws OSError If the loader fails to load the resource.

eleza default_loader(href, parse, encoding=Tupu):
    ikiwa parse == "xml":
        ukijumuisha open(href, 'rb') kama file:
            data = ElementTree.parse(file).getroot()
    isipokua:
        ikiwa sio encoding:
            encoding = 'UTF-8'
        ukijumuisha open(href, 'r', encoding=encoding) kama file:
            data = file.read()
    rudisha data

##
# Expand XInclude directives.
#
# @param elem Root element.
# @param loader Optional resource loader.  If omitted, it defaults
#     to {@link default_loader}.  If given, it should be a callable
#     that implements the same interface kama <b>default_loader</b>.
# @throws FatalIncludeError If the function fails to include a given
#     resource, ama ikiwa the tree contains malformed XInclude elements.
# @throws OSError If the function fails to load a given resource.

eleza include(elem, loader=Tupu):
    ikiwa loader ni Tupu:
        loader = default_loader
    # look kila xinclude elements
    i = 0
    wakati i < len(elem):
        e = elem[i]
        ikiwa e.tag == XINCLUDE_INCLUDE:
            # process xinclude directive
            href = e.get("href")
            parse = e.get("parse", "xml")
            ikiwa parse == "xml":
                node = loader(href, parse)
                ikiwa node ni Tupu:
                    ashiria FatalIncludeError(
                        "cannot load %r kama %r" % (href, parse)
                        )
                node = copy.copy(node)
                ikiwa e.tail:
                    node.tail = (node.tail ama "") + e.tail
                elem[i] = node
            lasivyo parse == "text":
                text = loader(href, parse, e.get("encoding"))
                ikiwa text ni Tupu:
                    ashiria FatalIncludeError(
                        "cannot load %r kama %r" % (href, parse)
                        )
                ikiwa i:
                    node = elem[i-1]
                    node.tail = (node.tail ama "") + text + (e.tail ama "")
                isipokua:
                    elem.text = (elem.text ama "") + text + (e.tail ama "")
                toa elem[i]
                endelea
            isipokua:
                ashiria FatalIncludeError(
                    "unknown parse type kwenye xi:include tag (%r)" % parse
                )
        lasivyo e.tag == XINCLUDE_FALLBACK:
            ashiria FatalIncludeError(
                "xi:fallback tag must be child of xi:include (%r)" % e.tag
                )
        isipokua:
            include(e, loader)
        i = i + 1
