#
# ElementTree
# $Id: ElementInclude.py 3375 2008-02-13 08:05:08Z fredrik $
#
# limited xinclude support for element trees
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
# and will comply with the following terms and conditions:
#
# Permission to use, copy, modify, and distribute this software and
# its associated documentation for any purpose and without fee is
# hereby granted, provided that the above copyright notice appears in
# all copies, and that both that copyright notice and this permission
# notice appear in supporting documentation, and that the name of
# Secret Labs AB or the author not be used in advertising or publicity
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
# See http://www.python.org/psf/license for licensing details.

##
# Limited XInclude support for the ElementTree package.
##

agiza copy
kutoka . agiza ElementTree

XINCLUDE = "{http://www.w3.org/2001/XInclude}"

XINCLUDE_INCLUDE = XINCLUDE + "include"
XINCLUDE_FALLBACK = XINCLUDE + "fallback"

##
# Fatal include error.

kundi FatalIncludeError(SyntaxError):
    pass

##
# Default loader.  This loader reads an included resource kutoka disk.
#
# @param href Resource reference.
# @param parse Parse mode.  Either "xml" or "text".
# @param encoding Optional text encoding (UTF-8 by default for "text").
# @rudisha The expanded resource.  If the parse mode is "xml", this
#    is an ElementTree instance.  If the parse mode is "text", this
#    is a Unicode string.  If the loader fails, it can rudisha None
#    or raise an OSError exception.
# @throws OSError If the loader fails to load the resource.

eleza default_loader(href, parse, encoding=None):
    ikiwa parse == "xml":
        with open(href, 'rb') as file:
            data = ElementTree.parse(file).getroot()
    else:
        ikiwa not encoding:
            encoding = 'UTF-8'
        with open(href, 'r', encoding=encoding) as file:
            data = file.read()
    rudisha data

##
# Expand XInclude directives.
#
# @param elem Root element.
# @param loader Optional resource loader.  If omitted, it defaults
#     to {@link default_loader}.  If given, it should be a callable
#     that implements the same interface as <b>default_loader</b>.
# @throws FatalIncludeError If the function fails to include a given
#     resource, or ikiwa the tree contains malformed XInclude elements.
# @throws OSError If the function fails to load a given resource.

eleza include(elem, loader=None):
    ikiwa loader is None:
        loader = default_loader
    # look for xinclude elements
    i = 0
    while i < len(elem):
        e = elem[i]
        ikiwa e.tag == XINCLUDE_INCLUDE:
            # process xinclude directive
            href = e.get("href")
            parse = e.get("parse", "xml")
            ikiwa parse == "xml":
                node = loader(href, parse)
                ikiwa node is None:
                    raise FatalIncludeError(
                        "cannot load %r as %r" % (href, parse)
                        )
                node = copy.copy(node)
                ikiwa e.tail:
                    node.tail = (node.tail or "") + e.tail
                elem[i] = node
            elikiwa parse == "text":
                text = loader(href, parse, e.get("encoding"))
                ikiwa text is None:
                    raise FatalIncludeError(
                        "cannot load %r as %r" % (href, parse)
                        )
                ikiwa i:
                    node = elem[i-1]
                    node.tail = (node.tail or "") + text + (e.tail or "")
                else:
                    elem.text = (elem.text or "") + text + (e.tail or "")
                del elem[i]
                continue
            else:
                raise FatalIncludeError(
                    "unknown parse type in xi:include tag (%r)" % parse
                )
        elikiwa e.tag == XINCLUDE_FALLBACK:
            raise FatalIncludeError(
                "xi:fallback tag must be child of xi:include (%r)" % e.tag
                )
        else:
            include(e, loader)
        i = i + 1
