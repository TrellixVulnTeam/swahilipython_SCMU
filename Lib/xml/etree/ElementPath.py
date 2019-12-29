#
# ElementTree
# $Id: ElementPath.py 3375 2008-02-13 08:05:08Z fredrik $
#
# limited xpath support kila element trees
#
# history:
# 2003-05-23 fl   created
# 2003-05-28 fl   added support kila // etc
# 2003-08-27 fl   fixed parsing of periods kwenye element names
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
# Implementation module kila XPath support.  There's usually no reason
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

eleza xpath_tokenizer(pattern, namespaces=Tupu):
    default_namespace = namespaces.get('') ikiwa namespaces isipokua Tupu
    parsing_attribute = Uongo
    kila token kwenye xpath_tokenizer_re.findall(pattern):
        ttype, tag = token
        ikiwa tag na tag[0] != "{":
            ikiwa ":" kwenye tag:
                prefix, uri = tag.split(":", 1)
                jaribu:
                    ikiwa sio namespaces:
                        ashiria KeyError
                    tuma ttype, "{%s}%s" % (namespaces[prefix], uri)
                tatizo KeyError:
                    ashiria SyntaxError("prefix %r sio found kwenye prefix map" % prefix) kutoka Tupu
            lasivyo default_namespace na sio parsing_attribute:
                tuma ttype, "{%s}%s" % (default_namespace, tag)
            isipokua:
                tuma token
            parsing_attribute = Uongo
        isipokua:
            tuma token
            parsing_attribute = ttype == '@'


eleza get_parent_map(context):
    parent_map = context.parent_map
    ikiwa parent_map ni Tupu:
        context.parent_map = parent_map = {}
        kila p kwenye context.root.iter():
            kila e kwenye p:
                parent_map[e] = p
    rudisha parent_map


eleza _is_wildcard_tag(tag):
    rudisha tag[:3] == '{*}' ama tag[-2:] == '}*'


eleza _prepare_tag(tag):
    _isinstance, _str = isinstance, str
    ikiwa tag == '{*}*':
        # Same kama '*', but no comments ama processing instructions.
        # It can be a surprise that '*' includes those, but there ni no
        # justification kila '{*}*' doing the same.
        eleza select(context, result):
            kila elem kwenye result:
                ikiwa _isinstance(elem.tag, _str):
                    tuma elem
    lasivyo tag == '{}*':
        # Any tag that ni haiko kwenye a namespace.
        eleza select(context, result):
            kila elem kwenye result:
                el_tag = elem.tag
                ikiwa _isinstance(el_tag, _str) na el_tag[0] != '{':
                    tuma elem
    lasivyo tag[:3] == '{*}':
        # The tag kwenye any (or no) namespace.
        suffix = tag[2:]  # '}name'
        no_ns = slice(-len(suffix), Tupu)
        tag = tag[3:]
        eleza select(context, result):
            kila elem kwenye result:
                el_tag = elem.tag
                ikiwa el_tag == tag ama _isinstance(el_tag, _str) na el_tag[no_ns] == suffix:
                    tuma elem
    lasivyo tag[-2:] == '}*':
        # Any tag kwenye the given namespace.
        ns = tag[:-1]
        ns_only = slice(Tupu, len(ns))
        eleza select(context, result):
            kila elem kwenye result:
                el_tag = elem.tag
                ikiwa _isinstance(el_tag, _str) na el_tag[ns_only] == ns:
                    tuma elem
    isipokua:
        ashiria RuntimeError(f"internal parser error, got {tag}")
    rudisha select


eleza prepare_child(next, token):
    tag = token[1]
    ikiwa _is_wildcard_tag(tag):
        select_tag = _prepare_tag(tag)
        eleza select(context, result):
            eleza select_child(result):
                kila elem kwenye result:
                    tuma kutoka elem
            rudisha select_tag(context, select_child(result))
    isipokua:
        ikiwa tag[:2] == '{}':
            tag = tag[2:]  # '{}tag' == 'tag'
        eleza select(context, result):
            kila elem kwenye result:
                kila e kwenye elem:
                    ikiwa e.tag == tag:
                        tuma e
    rudisha select

eleza prepare_star(next, token):
    eleza select(context, result):
        kila elem kwenye result:
            tuma kutoka elem
    rudisha select

eleza prepare_self(next, token):
    eleza select(context, result):
        tuma kutoka result
    rudisha select

eleza prepare_descendant(next, token):
    jaribu:
        token = next()
    tatizo StopIteration:
        rudisha
    ikiwa token[0] == "*":
        tag = "*"
    lasivyo sio token[0]:
        tag = token[1]
    isipokua:
        ashiria SyntaxError("invalid descendant")

    ikiwa _is_wildcard_tag(tag):
        select_tag = _prepare_tag(tag)
        eleza select(context, result):
            eleza select_child(result):
                kila elem kwenye result:
                    kila e kwenye elem.iter():
                        ikiwa e ni sio elem:
                            tuma e
            rudisha select_tag(context, select_child(result))
    isipokua:
        ikiwa tag[:2] == '{}':
            tag = tag[2:]  # '{}tag' == 'tag'
        eleza select(context, result):
            kila elem kwenye result:
                kila e kwenye elem.iter(tag):
                    ikiwa e ni sio elem:
                        tuma e
    rudisha select

eleza prepare_parent(next, token):
    eleza select(context, result):
        # FIXME: ashiria error ikiwa .. ni applied at toplevel?
        parent_map = get_parent_map(context)
        result_map = {}
        kila elem kwenye result:
            ikiwa elem kwenye parent_map:
                parent = parent_map[elem]
                ikiwa parent haiko kwenye result_map:
                    result_map[parent] = Tupu
                    tuma parent
    rudisha select

eleza prepare_predicate(next, token):
    # FIXME: replace ukijumuisha real parser!!! refs:
    # http://effbot.org/zone/simple-iterator-parser.htm
    # http://javascript.crockford.com/tdop/tdop.html
    signature = []
    predicate = []
    wakati 1:
        jaribu:
            token = next()
        tatizo StopIteration:
            rudisha
        ikiwa token[0] == "]":
            koma
        ikiwa token == ('', ''):
            # ignore whitespace
            endelea
        ikiwa token[0] na token[0][:1] kwenye "'\"":
            token = "'", token[0][1:-1]
        signature.append(token[0] ama "-")
        predicate.append(token[1])
    signature = "".join(signature)
    # use signature to determine predicate type
    ikiwa signature == "@-":
        # [@attribute] predicate
        key = predicate[1]
        eleza select(context, result):
            kila elem kwenye result:
                ikiwa elem.get(key) ni sio Tupu:
                    tuma elem
        rudisha select
    ikiwa signature == "@-='":
        # [@attribute='value']
        key = predicate[1]
        value = predicate[-1]
        eleza select(context, result):
            kila elem kwenye result:
                ikiwa elem.get(key) == value:
                    tuma elem
        rudisha select
    ikiwa signature == "-" na sio re.match(r"\-?\d+$", predicate[0]):
        # [tag]
        tag = predicate[0]
        eleza select(context, result):
            kila elem kwenye result:
                ikiwa elem.find(tag) ni sio Tupu:
                    tuma elem
        rudisha select
    ikiwa signature == ".='" ama (signature == "-='" na sio re.match(r"\-?\d+$", predicate[0])):
        # [.='value'] ama [tag='value']
        tag = predicate[0]
        value = predicate[-1]
        ikiwa tag:
            eleza select(context, result):
                kila elem kwenye result:
                    kila e kwenye elem.findall(tag):
                        ikiwa "".join(e.itertext()) == value:
                            tuma elem
                            koma
        isipokua:
            eleza select(context, result):
                kila elem kwenye result:
                    ikiwa "".join(elem.itertext()) == value:
                        tuma elem
        rudisha select
    ikiwa signature == "-" ama signature == "-()" ama signature == "-()-":
        # [index] ama [last()] ama [last()-index]
        ikiwa signature == "-":
            # [index]
            index = int(predicate[0]) - 1
            ikiwa index < 0:
                ashiria SyntaxError("XPath position >= 1 expected")
        isipokua:
            ikiwa predicate[0] != "last":
                ashiria SyntaxError("unsupported function")
            ikiwa signature == "-()-":
                jaribu:
                    index = int(predicate[2]) - 1
                tatizo ValueError:
                    ashiria SyntaxError("unsupported expression")
                ikiwa index > -2:
                    ashiria SyntaxError("XPath offset kutoka last() must be negative")
            isipokua:
                index = -1
        eleza select(context, result):
            parent_map = get_parent_map(context)
            kila elem kwenye result:
                jaribu:
                    parent = parent_map[elem]
                    # FIXME: what ikiwa the selector ni "*" ?
                    elems = list(parent.findall(elem.tag))
                    ikiwa elems[index] ni elem:
                        tuma elem
                tatizo (IndexError, KeyError):
                    pita
        rudisha select
    ashiria SyntaxError("invalid predicate")

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
    parent_map = Tupu
    eleza __init__(self, root):
        self.root = root

# --------------------------------------------------------------------

##
# Generate all matching objects.

eleza iterfind(elem, path, namespaces=Tupu):
    # compile selector pattern
    ikiwa path[-1:] == "/":
        path = path + "*" # implicit all (FIXME: keep this?)

    cache_key = (path,)
    ikiwa namespaces:
        cache_key += tuple(sorted(namespaces.items()))

    jaribu:
        selector = _cache[cache_key]
    tatizo KeyError:
        ikiwa len(_cache) > 100:
            _cache.clear()
        ikiwa path[:1] == "/":
            ashiria SyntaxError("cannot use absolute path on element")
        next = iter(xpath_tokenizer(path, namespaces)).__next__
        jaribu:
            token = next()
        tatizo StopIteration:
            rudisha
        selector = []
        wakati 1:
            jaribu:
                selector.append(ops[token[0]](next, token))
            tatizo StopIteration:
                ashiria SyntaxError("invalid path") kutoka Tupu
            jaribu:
                token = next()
                ikiwa token[0] == "/":
                    token = next()
            tatizo StopIteration:
                koma
        _cache[cache_key] = selector
    # execute selector pattern
    result = [elem]
    context = _SelectorContext(elem)
    kila select kwenye selector:
        result = select(context, result)
    rudisha result

##
# Find first matching object.

eleza find(elem, path, namespaces=Tupu):
    rudisha next(iterfind(elem, path, namespaces), Tupu)

##
# Find all matching objects.

eleza findall(elem, path, namespaces=Tupu):
    rudisha list(iterfind(elem, path, namespaces))

##
# Find text kila first matching object.

eleza findtext(elem, path, default=Tupu, namespaces=Tupu):
    jaribu:
        elem = next(iterfind(elem, path, namespaces))
        rudisha elem.text ama ""
    tatizo StopIteration:
        rudisha default
