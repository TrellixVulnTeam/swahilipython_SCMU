#
# ElementTree
# $Id: ElementPath.py 3375 2008-02-13 08:05:08Z fredrik $
#
# limited xpath support for element trees
#
# history:
# 2003-05-23 fl   created
# 2003-05-28 fl   added support for // etc
# 2003-08-27 fl   fixed parsing of periods in element names
# 2007-09-10 fl   new selection engine
# 2007-09-12 fl   fixed parent selector
# 2007-09-13 fl   added iterfind; changed findall to rudisha a list
# 2007-11-30 fl   added namespaces support
# 2009-10-30 fl   added child element value filter
#
# Copyright (c) 2003-2009 by Fredrik Lundh.  All rights reserved.
#
# fredrik@pythonware.com
# http://www.pythonware.com
#
# --------------------------------------------------------------------
# The ElementTree toolkit is
#
# Copyright (c) 1999-2009 by Fredrik Lundh
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
# Implementation module for XPath support.  There's usually no reason
# to agiza this module directly; the <b>ElementTree</b> does this for
# you, ikiwa needed.
##

agiza re

xpath_tokenizer_re = re.compile(
    r"("
    r"'[^']*'|\"[^\"]*\"|"
    r"::|"
    r"//?|"
    r"\.\.|"
    r"\(\)|"
    r"[/.*:\[\]\(\)@=])|"
    r"((?:\{[^}]+\})?[^/\[\]\(\)@=\s]+)|"
    r"\s+"
    )

eleza xpath_tokenizer(pattern, namespaces=None):
    default_namespace = namespaces.get('') ikiwa namespaces else None
    parsing_attribute = False
    for token in xpath_tokenizer_re.findall(pattern):
        ttype, tag = token
        ikiwa tag and tag[0] != "{":
            ikiwa ":" in tag:
                prefix, uri = tag.split(":", 1)
                try:
                    ikiwa not namespaces:
                        raise KeyError
                    yield ttype, "{%s}%s" % (namespaces[prefix], uri)
                except KeyError:
                    raise SyntaxError("prefix %r not found in prefix map" % prefix) kutoka None
            elikiwa default_namespace and not parsing_attribute:
                yield ttype, "{%s}%s" % (default_namespace, tag)
            else:
                yield token
            parsing_attribute = False
        else:
            yield token
            parsing_attribute = ttype == '@'


eleza get_parent_map(context):
    parent_map = context.parent_map
    ikiwa parent_map is None:
        context.parent_map = parent_map = {}
        for p in context.root.iter():
            for e in p:
                parent_map[e] = p
    rudisha parent_map


eleza _is_wildcard_tag(tag):
    rudisha tag[:3] == '{*}' or tag[-2:] == '}*'


eleza _prepare_tag(tag):
    _isinstance, _str = isinstance, str
    ikiwa tag == '{*}*':
        # Same as '*', but no comments or processing instructions.
        # It can be a surprise that '*' includes those, but there is no
        # justification for '{*}*' doing the same.
        eleza select(context, result):
            for elem in result:
                ikiwa _isinstance(elem.tag, _str):
                    yield elem
    elikiwa tag == '{}*':
        # Any tag that is not in a namespace.
        eleza select(context, result):
            for elem in result:
                el_tag = elem.tag
                ikiwa _isinstance(el_tag, _str) and el_tag[0] != '{':
                    yield elem
    elikiwa tag[:3] == '{*}':
        # The tag in any (or no) namespace.
        suffix = tag[2:]  # '}name'
        no_ns = slice(-len(suffix), None)
        tag = tag[3:]
        eleza select(context, result):
            for elem in result:
                el_tag = elem.tag
                ikiwa el_tag == tag or _isinstance(el_tag, _str) and el_tag[no_ns] == suffix:
                    yield elem
    elikiwa tag[-2:] == '}*':
        # Any tag in the given namespace.
        ns = tag[:-1]
        ns_only = slice(None, len(ns))
        eleza select(context, result):
            for elem in result:
                el_tag = elem.tag
                ikiwa _isinstance(el_tag, _str) and el_tag[ns_only] == ns:
                    yield elem
    else:
        raise RuntimeError(f"internal parser error, got {tag}")
    rudisha select


eleza prepare_child(next, token):
    tag = token[1]
    ikiwa _is_wildcard_tag(tag):
        select_tag = _prepare_tag(tag)
        eleza select(context, result):
            eleza select_child(result):
                for elem in result:
                    yield kutoka elem
            rudisha select_tag(context, select_child(result))
    else:
        ikiwa tag[:2] == '{}':
            tag = tag[2:]  # '{}tag' == 'tag'
        eleza select(context, result):
            for elem in result:
                for e in elem:
                    ikiwa e.tag == tag:
                        yield e
    rudisha select

eleza prepare_star(next, token):
    eleza select(context, result):
        for elem in result:
            yield kutoka elem
    rudisha select

eleza prepare_self(next, token):
    eleza select(context, result):
        yield kutoka result
    rudisha select

eleza prepare_descendant(next, token):
    try:
        token = next()
    except StopIteration:
        return
    ikiwa token[0] == "*":
        tag = "*"
    elikiwa not token[0]:
        tag = token[1]
    else:
        raise SyntaxError("invalid descendant")

    ikiwa _is_wildcard_tag(tag):
        select_tag = _prepare_tag(tag)
        eleza select(context, result):
            eleza select_child(result):
                for elem in result:
                    for e in elem.iter():
                        ikiwa e is not elem:
                            yield e
            rudisha select_tag(context, select_child(result))
    else:
        ikiwa tag[:2] == '{}':
            tag = tag[2:]  # '{}tag' == 'tag'
        eleza select(context, result):
            for elem in result:
                for e in elem.iter(tag):
                    ikiwa e is not elem:
                        yield e
    rudisha select

eleza prepare_parent(next, token):
    eleza select(context, result):
        # FIXME: raise error ikiwa .. is applied at toplevel?
        parent_map = get_parent_map(context)
        result_map = {}
        for elem in result:
            ikiwa elem in parent_map:
                parent = parent_map[elem]
                ikiwa parent not in result_map:
                    result_map[parent] = None
                    yield parent
    rudisha select

eleza prepare_predicate(next, token):
    # FIXME: replace with real parser!!! refs:
    # http://effbot.org/zone/simple-iterator-parser.htm
    # http://javascript.crockford.com/tdop/tdop.html
    signature = []
    predicate = []
    while 1:
        try:
            token = next()
        except StopIteration:
            return
        ikiwa token[0] == "]":
            break
        ikiwa token == ('', ''):
            # ignore whitespace
            continue
        ikiwa token[0] and token[0][:1] in "'\"":
            token = "'", token[0][1:-1]
        signature.append(token[0] or "-")
        predicate.append(token[1])
    signature = "".join(signature)
    # use signature to determine predicate type
    ikiwa signature == "@-":
        # [@attribute] predicate
        key = predicate[1]
        eleza select(context, result):
            for elem in result:
                ikiwa elem.get(key) is not None:
                    yield elem
        rudisha select
    ikiwa signature == "@-='":
        # [@attribute='value']
        key = predicate[1]
        value = predicate[-1]
        eleza select(context, result):
            for elem in result:
                ikiwa elem.get(key) == value:
                    yield elem
        rudisha select
    ikiwa signature == "-" and not re.match(r"\-?\d+$", predicate[0]):
        # [tag]
        tag = predicate[0]
        eleza select(context, result):
            for elem in result:
                ikiwa elem.find(tag) is not None:
                    yield elem
        rudisha select
    ikiwa signature == ".='" or (signature == "-='" and not re.match(r"\-?\d+$", predicate[0])):
        # [.='value'] or [tag='value']
        tag = predicate[0]
        value = predicate[-1]
        ikiwa tag:
            eleza select(context, result):
                for elem in result:
                    for e in elem.findall(tag):
                        ikiwa "".join(e.itertext()) == value:
                            yield elem
                            break
        else:
            eleza select(context, result):
                for elem in result:
                    ikiwa "".join(elem.itertext()) == value:
                        yield elem
        rudisha select
    ikiwa signature == "-" or signature == "-()" or signature == "-()-":
        # [index] or [last()] or [last()-index]
        ikiwa signature == "-":
            # [index]
            index = int(predicate[0]) - 1
            ikiwa index < 0:
                raise SyntaxError("XPath position >= 1 expected")
        else:
            ikiwa predicate[0] != "last":
                raise SyntaxError("unsupported function")
            ikiwa signature == "-()-":
                try:
                    index = int(predicate[2]) - 1
                except ValueError:
                    raise SyntaxError("unsupported expression")
                ikiwa index > -2:
                    raise SyntaxError("XPath offset kutoka last() must be negative")
            else:
                index = -1
        eleza select(context, result):
            parent_map = get_parent_map(context)
            for elem in result:
                try:
                    parent = parent_map[elem]
                    # FIXME: what ikiwa the selector is "*" ?
                    elems = list(parent.findall(elem.tag))
                    ikiwa elems[index] is elem:
                        yield elem
                except (IndexError, KeyError):
                    pass
        rudisha select
    raise SyntaxError("invalid predicate")

ops = {
    "": prepare_child,
    "*": prepare_star,
    ".": prepare_self,
    "..": prepare_parent,
    "//": prepare_descendant,
    "[": prepare_predicate,
    }

_cache = {}

kundi _SelectorContext:
    parent_map = None
    eleza __init__(self, root):
        self.root = root

# --------------------------------------------------------------------

##
# Generate all matching objects.

eleza iterfind(elem, path, namespaces=None):
    # compile selector pattern
    ikiwa path[-1:] == "/":
        path = path + "*" # implicit all (FIXME: keep this?)

    cache_key = (path,)
    ikiwa namespaces:
        cache_key += tuple(sorted(namespaces.items()))

    try:
        selector = _cache[cache_key]
    except KeyError:
        ikiwa len(_cache) > 100:
            _cache.clear()
        ikiwa path[:1] == "/":
            raise SyntaxError("cannot use absolute path on element")
        next = iter(xpath_tokenizer(path, namespaces)).__next__
        try:
            token = next()
        except StopIteration:
            return
        selector = []
        while 1:
            try:
                selector.append(ops[token[0]](next, token))
            except StopIteration:
                raise SyntaxError("invalid path") kutoka None
            try:
                token = next()
                ikiwa token[0] == "/":
                    token = next()
            except StopIteration:
                break
        _cache[cache_key] = selector
    # execute selector pattern
    result = [elem]
    context = _SelectorContext(elem)
    for select in selector:
        result = select(context, result)
    rudisha result

##
# Find first matching object.

eleza find(elem, path, namespaces=None):
    rudisha next(iterfind(elem, path, namespaces), None)

##
# Find all matching objects.

eleza findall(elem, path, namespaces=None):
    rudisha list(iterfind(elem, path, namespaces))

##
# Find text for first matching object.

eleza findtext(elem, path, default=None, namespaces=None):
    try:
        elem = next(iterfind(elem, path, namespaces))
        rudisha elem.text or ""
    except StopIteration:
        rudisha default
