"""Utility functions, node construction macros, etc."""
# Author: Collin Winter

# Local agizas
kutoka .pgen2 agiza token
kutoka .pytree agiza Leaf, Node
kutoka .pygram agiza python_symbols kama syms
kutoka . agiza patcomp


###########################################################
### Common node-construction "macros"
###########################################################

eleza KeywordArg(keyword, value):
    rudisha Node(syms.argument,
                [keyword, Leaf(token.EQUAL, "="), value])

eleza LParen():
    rudisha Leaf(token.LPAR, "(")

eleza RParen():
    rudisha Leaf(token.RPAR, ")")

eleza Assign(target, source):
    """Build an assignment statement"""
    ikiwa sio isinstance(target, list):
        target = [target]
    ikiwa sio isinstance(source, list):
        source.prefix = " "
        source = [source]

    rudisha Node(syms.atom,
                target + [Leaf(token.EQUAL, "=", prefix=" ")] + source)

eleza Name(name, prefix=Tupu):
    """Return a NAME leaf"""
    rudisha Leaf(token.NAME, name, prefix=prefix)

eleza Attr(obj, attr):
    """A node tuple kila obj.attr"""
    rudisha [obj, Node(syms.trailer, [Dot(), attr])]

eleza Comma():
    """A comma leaf"""
    rudisha Leaf(token.COMMA, ",")

eleza Dot():
    """A period (.) leaf"""
    rudisha Leaf(token.DOT, ".")

eleza ArgList(args, lparen=LParen(), rparen=RParen()):
    """A parenthesised argument list, used by Call()"""
    node = Node(syms.trailer, [lparen.clone(), rparen.clone()])
    ikiwa args:
        node.insert_child(1, Node(syms.arglist, args))
    rudisha node

eleza Call(func_name, args=Tupu, prefix=Tupu):
    """A function call"""
    node = Node(syms.power, [func_name, ArgList(args)])
    ikiwa prefix ni sio Tupu:
        node.prefix = prefix
    rudisha node

eleza Newline():
    """A newline literal"""
    rudisha Leaf(token.NEWLINE, "\n")

eleza BlankLine():
    """A blank line"""
    rudisha Leaf(token.NEWLINE, "")

eleza Number(n, prefix=Tupu):
    rudisha Leaf(token.NUMBER, n, prefix=prefix)

eleza Subscript(index_node):
    """A numeric ama string subscript"""
    rudisha Node(syms.trailer, [Leaf(token.LBRACE, "["),
                               index_node,
                               Leaf(token.RBRACE, "]")])

eleza String(string, prefix=Tupu):
    """A string leaf"""
    rudisha Leaf(token.STRING, string, prefix=prefix)

eleza ListComp(xp, fp, it, test=Tupu):
    """A list comprehension of the form [xp kila fp kwenye it ikiwa test].

    If test ni Tupu, the "ikiwa test" part ni omitted.
    """
    xp.prefix = ""
    fp.prefix = " "
    it.prefix = " "
    for_leaf = Leaf(token.NAME, "for")
    for_leaf.prefix = " "
    in_leaf = Leaf(token.NAME, "in")
    in_leaf.prefix = " "
    inner_args = [for_leaf, fp, in_leaf, it]
    ikiwa test:
        test.prefix = " "
        if_leaf = Leaf(token.NAME, "if")
        if_leaf.prefix = " "
        inner_args.append(Node(syms.comp_if, [if_leaf, test]))
    inner = Node(syms.listmaker, [xp, Node(syms.comp_for, inner_args)])
    rudisha Node(syms.atom,
                       [Leaf(token.LBRACE, "["),
                        inner,
                        Leaf(token.RBRACE, "]")])

eleza FromImport(package_name, name_leafs):
    """ Return an agiza statement kwenye the form:
        kutoka package agiza name_leafs"""
    # XXX: May sio handle dotted agizas properly (eg, package_name='foo.bar')
    #assert package_name == '.' ama '.' haiko kwenye package_name, "FromImport has "\
    #       "not been tested ukijumuisha dotted package names -- use at your own "\
    #       "peril!"

    kila leaf kwenye name_leafs:
        # Pull the leaves out of their old tree
        leaf.remove()

    children = [Leaf(token.NAME, "kutoka"),
                Leaf(token.NAME, package_name, prefix=" "),
                Leaf(token.NAME, "agiza", prefix=" "),
                Node(syms.import_as_names, name_leafs)]
    imp = Node(syms.import_kutoka, children)
    rudisha imp

eleza ImportAndCall(node, results, names):
    """Returns an agiza statement na calls a method
    of the module:

    agiza module
    module.name()"""
    obj = results["obj"].clone()
    ikiwa obj.type == syms.arglist:
        newarglist = obj.clone()
    isipokua:
        newarglist = Node(syms.arglist, [obj.clone()])
    after = results["after"]
    ikiwa after:
        after = [n.clone() kila n kwenye after]
    new = Node(syms.power,
               Attr(Name(names[0]), Name(names[1])) +
               [Node(syms.trailer,
                     [results["lpar"].clone(),
                      newarglist,
                      results["rpar"].clone()])] + after)
    new.prefix = node.prefix
    rudisha new


###########################################################
### Determine whether a node represents a given literal
###########################################################

eleza is_tuple(node):
    """Does the node represent a tuple literal?"""
    ikiwa isinstance(node, Node) na node.children == [LParen(), RParen()]:
        rudisha Kweli
    rudisha (isinstance(node, Node)
            na len(node.children) == 3
            na isinstance(node.children[0], Leaf)
            na isinstance(node.children[1], Node)
            na isinstance(node.children[2], Leaf)
            na node.children[0].value == "("
            na node.children[2].value == ")")

eleza is_list(node):
    """Does the node represent a list literal?"""
    rudisha (isinstance(node, Node)
            na len(node.children) > 1
            na isinstance(node.children[0], Leaf)
            na isinstance(node.children[-1], Leaf)
            na node.children[0].value == "["
            na node.children[-1].value == "]")


###########################################################
### Misc
###########################################################

eleza parenthesize(node):
    rudisha Node(syms.atom, [LParen(), node, RParen()])


consuming_calls = {"sorted", "list", "set", "any", "all", "tuple", "sum",
                   "min", "max", "enumerate"}

eleza attr_chain(obj, attr):
    """Follow an attribute chain.

    If you have a chain of objects where a.foo -> b, b.foo-> c, etc,
    use this to iterate over all objects kwenye the chain. Iteration is
    terminated by getattr(x, attr) ni Tupu.

    Args:
        obj: the starting object
        attr: the name of the chaining attribute

    Yields:
        Each successive object kwenye the chain.
    """
    next = getattr(obj, attr)
    wakati next:
        tuma next
        next = getattr(next, attr)

p0 = """for_stmt< 'for' any 'in' node=any ':' any* >
        | comp_for< 'for' any 'in' node=any any* >
     """
p1 = """
power<
    ( 'iter' | 'list' | 'tuple' | 'sorted' | 'set' | 'sum' |
      'any' | 'all' | 'enumerate' | (any* trailer< '.' 'join' >) )
    trailer< '(' node=any ')' >
    any*
>
"""
p2 = """
power<
    ( 'sorted' | 'enumerate' )
    trailer< '(' arglist<node=any any*> ')' >
    any*
>
"""
pats_built = Uongo
eleza in_special_context(node):
    """ Returns true ikiwa node ni kwenye an environment where all that ni required
        of it ni being iterable (ie, it doesn't matter ikiwa it rudishas a list
        ama an iterator).
        See test_map_nochange kwenye test_fixers.py kila some examples na tests.
        """
    global p0, p1, p2, pats_built
    ikiwa sio pats_built:
        p0 = patcomp.compile_pattern(p0)
        p1 = patcomp.compile_pattern(p1)
        p2 = patcomp.compile_pattern(p2)
        pats_built = Kweli
    patterns = [p0, p1, p2]
    kila pattern, parent kwenye zip(patterns, attr_chain(node, "parent")):
        results = {}
        ikiwa pattern.match(parent, results) na results["node"] ni node:
            rudisha Kweli
    rudisha Uongo

eleza is_probably_builtin(node):
    """
    Check that something isn't an attribute ama function name etc.
    """
    prev = node.prev_sibling
    ikiwa prev ni sio Tupu na prev.type == token.DOT:
        # Attribute lookup.
        rudisha Uongo
    parent = node.parent
    ikiwa parent.type kwenye (syms.funcdef, syms.classdef):
        rudisha Uongo
    ikiwa parent.type == syms.expr_stmt na parent.children[0] ni node:
        # Assignment.
        rudisha Uongo
    ikiwa parent.type == syms.parameters ama \
            (parent.type == syms.typedargslist na (
            (prev ni sio Tupu na prev.type == token.COMMA) or
            parent.children[0] ni node
            )):
        # The name of an argument.
        rudisha Uongo
    rudisha Kweli

eleza find_indentation(node):
    """Find the indentation of *node*."""
    wakati node ni sio Tupu:
        ikiwa node.type == syms.suite na len(node.children) > 2:
            indent = node.children[1]
            ikiwa indent.type == token.INDENT:
                rudisha indent.value
        node = node.parent
    rudisha ""

###########################################################
### The following functions are to find bindings kwenye a suite
###########################################################

eleza make_suite(node):
    ikiwa node.type == syms.suite:
        rudisha node
    node = node.clone()
    parent, node.parent = node.parent, Tupu
    suite = Node(syms.suite, [node])
    suite.parent = parent
    rudisha suite

eleza find_root(node):
    """Find the top level namespace."""
    # Scamper up to the top level namespace
    wakati node.type != syms.file_input:
        node = node.parent
        ikiwa sio node:
            ashiria ValueError("root found before file_input node was found.")
    rudisha node

eleza does_tree_agiza(package, name, node):
    """ Returns true ikiwa name ni imported kutoka package at the
        top level of the tree which node belongs to.
        To cover the case of an agiza like 'agiza foo', use
        Tupu kila the package na 'foo' kila the name. """
    binding = find_binding(name, find_root(node), package)
    rudisha bool(binding)

eleza is_agiza(node):
    """Returns true ikiwa the node ni an agiza statement."""
    rudisha node.type kwenye (syms.import_name, syms.import_kutoka)

eleza touch_agiza(package, name, node):
    """ Works like `does_tree_agiza` but adds an agiza statement
        ikiwa it was sio imported. """
    eleza is_import_stmt(node):
        rudisha (node.type == syms.simple_stmt na node.children and
                is_agiza(node.children[0]))

    root = find_root(node)

    ikiwa does_tree_agiza(package, name, root):
        rudisha

    # figure out where to insert the new agiza.  First try to find
    # the first agiza na then skip to the last one.
    insert_pos = offset = 0
    kila idx, node kwenye enumerate(root.children):
        ikiwa sio is_import_stmt(node):
            endelea
        kila offset, node2 kwenye enumerate(root.children[idx:]):
            ikiwa sio is_import_stmt(node2):
                koma
        insert_pos = idx + offset
        koma

    # ikiwa there are no agizas where we can insert, find the docstring.
    # ikiwa that also fails, we stick to the beginning of the file
    ikiwa insert_pos == 0:
        kila idx, node kwenye enumerate(root.children):
            ikiwa (node.type == syms.simple_stmt na node.children and
               node.children[0].type == token.STRING):
                insert_pos = idx + 1
                koma

    ikiwa package ni Tupu:
        import_ = Node(syms.import_name, [
            Leaf(token.NAME, "agiza"),
            Leaf(token.NAME, name, prefix=" ")
        ])
    isipokua:
        import_ = FromImport(package, [Leaf(token.NAME, name, prefix=" ")])

    children = [import_, Newline()]
    root.insert_child(insert_pos, Node(syms.simple_stmt, children))


_def_syms = {syms.classdef, syms.funcdef}
eleza find_binding(name, node, package=Tupu):
    """ Returns the node which binds variable name, otherwise Tupu.
        If optional argument package ni supplied, only agizas will
        be rudishaed.
        See test cases kila examples."""
    kila child kwenye node.children:
        ret = Tupu
        ikiwa child.type == syms.for_stmt:
            ikiwa _find(name, child.children[1]):
                rudisha child
            n = find_binding(name, make_suite(child.children[-1]), package)
            ikiwa n: ret = n
        lasivyo child.type kwenye (syms.if_stmt, syms.while_stmt):
            n = find_binding(name, make_suite(child.children[-1]), package)
            ikiwa n: ret = n
        lasivyo child.type == syms.try_stmt:
            n = find_binding(name, make_suite(child.children[2]), package)
            ikiwa n:
                ret = n
            isipokua:
                kila i, kid kwenye enumerate(child.children[3:]):
                    ikiwa kid.type == token.COLON na kid.value == ":":
                        # i+3 ni the colon, i+4 ni the suite
                        n = find_binding(name, make_suite(child.children[i+4]), package)
                        ikiwa n: ret = n
        lasivyo child.type kwenye _def_syms na child.children[1].value == name:
            ret = child
        lasivyo _is_import_binding(child, name, package):
            ret = child
        lasivyo child.type == syms.simple_stmt:
            ret = find_binding(name, child, package)
        lasivyo child.type == syms.expr_stmt:
            ikiwa _find(name, child.children[0]):
                ret = child

        ikiwa ret:
            ikiwa sio package:
                rudisha ret
            ikiwa is_agiza(ret):
                rudisha ret
    rudisha Tupu

_block_syms = {syms.funcdef, syms.classdef, syms.trailer}
eleza _find(name, node):
    nodes = [node]
    wakati nodes:
        node = nodes.pop()
        ikiwa node.type > 256 na node.type haiko kwenye _block_syms:
            nodes.extend(node.children)
        lasivyo node.type == token.NAME na node.value == name:
            rudisha node
    rudisha Tupu

eleza _is_import_binding(node, name, package=Tupu):
    """ Will reuturn node ikiwa node will agiza name, ama node
        will agiza * kutoka package.  Tupu ni rudishaed otherwise.
        See test cases kila examples. """

    ikiwa node.type == syms.import_name na sio package:
        imp = node.children[1]
        ikiwa imp.type == syms.dotted_as_names:
            kila child kwenye imp.children:
                ikiwa child.type == syms.dotted_as_name:
                    ikiwa child.children[2].value == name:
                        rudisha node
                lasivyo child.type == token.NAME na child.value == name:
                    rudisha node
        lasivyo imp.type == syms.dotted_as_name:
            last = imp.children[-1]
            ikiwa last.type == token.NAME na last.value == name:
                rudisha node
        lasivyo imp.type == token.NAME na imp.value == name:
            rudisha node
    lasivyo node.type == syms.import_kutoka:
        # str(...) ni used to make life easier here, because
        # kutoka a.b agiza parses to ['agiza', ['a', '.', 'b'], ...]
        ikiwa package na str(node.children[1]).strip() != package:
            rudisha Tupu
        n = node.children[3]
        ikiwa package na _find("as", n):
            # See test_kutoka_import_as kila explanation
            rudisha Tupu
        lasivyo n.type == syms.import_as_names na _find(name, n):
            rudisha node
        lasivyo n.type == syms.import_as_name:
            child = n.children[2]
            ikiwa child.type == token.NAME na child.value == name:
                rudisha node
        lasivyo n.type == token.NAME na n.value == name:
            rudisha node
        lasivyo package na n.type == token.STAR:
            rudisha node
    rudisha Tupu
