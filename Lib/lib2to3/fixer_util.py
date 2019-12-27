"""Utility functions, node construction macros, etc."""
# Author: Collin Winter

# Local agizas
kutoka .pgen2 agiza token
kutoka .pytree agiza Leaf, Node
kutoka .pygram agiza python_symbols as syms
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
    ikiwa not isinstance(target, list):
        target = [target]
    ikiwa not isinstance(source, list):
        source.prefix = " "
        source = [source]

    rudisha Node(syms.atom,
                target + [Leaf(token.EQUAL, "=", prefix=" ")] + source)

eleza Name(name, prefix=None):
    """Return a NAME leaf"""
    rudisha Leaf(token.NAME, name, prefix=prefix)

eleza Attr(obj, attr):
    """A node tuple for obj.attr"""
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

eleza Call(func_name, args=None, prefix=None):
    """A function call"""
    node = Node(syms.power, [func_name, ArgList(args)])
    ikiwa prefix is not None:
        node.prefix = prefix
    rudisha node

eleza Newline():
    """A newline literal"""
    rudisha Leaf(token.NEWLINE, "\n")

eleza BlankLine():
    """A blank line"""
    rudisha Leaf(token.NEWLINE, "")

eleza Number(n, prefix=None):
    rudisha Leaf(token.NUMBER, n, prefix=prefix)

eleza Subscript(index_node):
    """A numeric or string subscript"""
    rudisha Node(syms.trailer, [Leaf(token.LBRACE, "["),
                               index_node,
                               Leaf(token.RBRACE, "]")])

eleza String(string, prefix=None):
    """A string leaf"""
    rudisha Leaf(token.STRING, string, prefix=prefix)

eleza ListComp(xp, fp, it, test=None):
    """A list comprehension of the form [xp for fp in it ikiwa test].

    If test is None, the "ikiwa test" part is omitted.
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
    """ Return an agiza statement in the form:
        kutoka package agiza name_leafs"""
    # XXX: May not handle dotted agizas properly (eg, package_name='foo.bar')
    #assert package_name == '.' or '.' not in package_name, "FromImport has "\
    #       "not been tested with dotted package names -- use at your own "\
    #       "peril!"

    for leaf in name_leafs:
        # Pull the leaves out of their old tree
        leaf.remove()

    children = [Leaf(token.NAME, "kutoka"),
                Leaf(token.NAME, package_name, prefix=" "),
                Leaf(token.NAME, "agiza", prefix=" "),
                Node(syms.import_as_names, name_leafs)]
    imp = Node(syms.import_kutoka, children)
    rudisha imp

eleza ImportAndCall(node, results, names):
    """Returns an agiza statement and calls a method
    of the module:

    agiza module
    module.name()"""
    obj = results["obj"].clone()
    ikiwa obj.type == syms.arglist:
        newarglist = obj.clone()
    else:
        newarglist = Node(syms.arglist, [obj.clone()])
    after = results["after"]
    ikiwa after:
        after = [n.clone() for n in after]
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
    ikiwa isinstance(node, Node) and node.children == [LParen(), RParen()]:
        rudisha True
    rudisha (isinstance(node, Node)
            and len(node.children) == 3
            and isinstance(node.children[0], Leaf)
            and isinstance(node.children[1], Node)
            and isinstance(node.children[2], Leaf)
            and node.children[0].value == "("
            and node.children[2].value == ")")

eleza is_list(node):
    """Does the node represent a list literal?"""
    rudisha (isinstance(node, Node)
            and len(node.children) > 1
            and isinstance(node.children[0], Leaf)
            and isinstance(node.children[-1], Leaf)
            and node.children[0].value == "["
            and node.children[-1].value == "]")


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
    use this to iterate over all objects in the chain. Iteration is
    terminated by getattr(x, attr) is None.

    Args:
        obj: the starting object
        attr: the name of the chaining attribute

    Yields:
        Each successive object in the chain.
    """
    next = getattr(obj, attr)
    while next:
        yield next
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
pats_built = False
eleza in_special_context(node):
    """ Returns true ikiwa node is in an environment where all that is required
        of it is being iterable (ie, it doesn't matter ikiwa it returns a list
        or an iterator).
        See test_map_nochange in test_fixers.py for some examples and tests.
        """
    global p0, p1, p2, pats_built
    ikiwa not pats_built:
        p0 = patcomp.compile_pattern(p0)
        p1 = patcomp.compile_pattern(p1)
        p2 = patcomp.compile_pattern(p2)
        pats_built = True
    patterns = [p0, p1, p2]
    for pattern, parent in zip(patterns, attr_chain(node, "parent")):
        results = {}
        ikiwa pattern.match(parent, results) and results["node"] is node:
            rudisha True
    rudisha False

eleza is_probably_builtin(node):
    """
    Check that something isn't an attribute or function name etc.
    """
    prev = node.prev_sibling
    ikiwa prev is not None and prev.type == token.DOT:
        # Attribute lookup.
        rudisha False
    parent = node.parent
    ikiwa parent.type in (syms.funcdef, syms.classdef):
        rudisha False
    ikiwa parent.type == syms.expr_stmt and parent.children[0] is node:
        # Assignment.
        rudisha False
    ikiwa parent.type == syms.parameters or \
            (parent.type == syms.typedargslist and (
            (prev is not None and prev.type == token.COMMA) or
            parent.children[0] is node
            )):
        # The name of an argument.
        rudisha False
    rudisha True

eleza find_indentation(node):
    """Find the indentation of *node*."""
    while node is not None:
        ikiwa node.type == syms.suite and len(node.children) > 2:
            indent = node.children[1]
            ikiwa indent.type == token.INDENT:
                rudisha indent.value
        node = node.parent
    rudisha ""

###########################################################
### The following functions are to find bindings in a suite
###########################################################

eleza make_suite(node):
    ikiwa node.type == syms.suite:
        rudisha node
    node = node.clone()
    parent, node.parent = node.parent, None
    suite = Node(syms.suite, [node])
    suite.parent = parent
    rudisha suite

eleza find_root(node):
    """Find the top level namespace."""
    # Scamper up to the top level namespace
    while node.type != syms.file_input:
        node = node.parent
        ikiwa not node:
            raise ValueError("root found before file_input node was found.")
    rudisha node

eleza does_tree_agiza(package, name, node):
    """ Returns true ikiwa name is imported kutoka package at the
        top level of the tree which node belongs to.
        To cover the case of an agiza like 'agiza foo', use
        None for the package and 'foo' for the name. """
    binding = find_binding(name, find_root(node), package)
    rudisha bool(binding)

eleza is_agiza(node):
    """Returns true ikiwa the node is an agiza statement."""
    rudisha node.type in (syms.import_name, syms.import_kutoka)

eleza touch_agiza(package, name, node):
    """ Works like `does_tree_agiza` but adds an agiza statement
        ikiwa it was not imported. """
    eleza is_import_stmt(node):
        rudisha (node.type == syms.simple_stmt and node.children and
                is_agiza(node.children[0]))

    root = find_root(node)

    ikiwa does_tree_agiza(package, name, root):
        return

    # figure out where to insert the new agiza.  First try to find
    # the first agiza and then skip to the last one.
    insert_pos = offset = 0
    for idx, node in enumerate(root.children):
        ikiwa not is_import_stmt(node):
            continue
        for offset, node2 in enumerate(root.children[idx:]):
            ikiwa not is_import_stmt(node2):
                break
        insert_pos = idx + offset
        break

    # ikiwa there are no agizas where we can insert, find the docstring.
    # ikiwa that also fails, we stick to the beginning of the file
    ikiwa insert_pos == 0:
        for idx, node in enumerate(root.children):
            ikiwa (node.type == syms.simple_stmt and node.children and
               node.children[0].type == token.STRING):
                insert_pos = idx + 1
                break

    ikiwa package is None:
        import_ = Node(syms.import_name, [
            Leaf(token.NAME, "agiza"),
            Leaf(token.NAME, name, prefix=" ")
        ])
    else:
        import_ = FromImport(package, [Leaf(token.NAME, name, prefix=" ")])

    children = [import_, Newline()]
    root.insert_child(insert_pos, Node(syms.simple_stmt, children))


_def_syms = {syms.classdef, syms.funcdef}
eleza find_binding(name, node, package=None):
    """ Returns the node which binds variable name, otherwise None.
        If optional argument package is supplied, only agizas will
        be returned.
        See test cases for examples."""
    for child in node.children:
        ret = None
        ikiwa child.type == syms.for_stmt:
            ikiwa _find(name, child.children[1]):
                rudisha child
            n = find_binding(name, make_suite(child.children[-1]), package)
            ikiwa n: ret = n
        elikiwa child.type in (syms.if_stmt, syms.while_stmt):
            n = find_binding(name, make_suite(child.children[-1]), package)
            ikiwa n: ret = n
        elikiwa child.type == syms.try_stmt:
            n = find_binding(name, make_suite(child.children[2]), package)
            ikiwa n:
                ret = n
            else:
                for i, kid in enumerate(child.children[3:]):
                    ikiwa kid.type == token.COLON and kid.value == ":":
                        # i+3 is the colon, i+4 is the suite
                        n = find_binding(name, make_suite(child.children[i+4]), package)
                        ikiwa n: ret = n
        elikiwa child.type in _def_syms and child.children[1].value == name:
            ret = child
        elikiwa _is_import_binding(child, name, package):
            ret = child
        elikiwa child.type == syms.simple_stmt:
            ret = find_binding(name, child, package)
        elikiwa child.type == syms.expr_stmt:
            ikiwa _find(name, child.children[0]):
                ret = child

        ikiwa ret:
            ikiwa not package:
                rudisha ret
            ikiwa is_agiza(ret):
                rudisha ret
    rudisha None

_block_syms = {syms.funcdef, syms.classdef, syms.trailer}
eleza _find(name, node):
    nodes = [node]
    while nodes:
        node = nodes.pop()
        ikiwa node.type > 256 and node.type not in _block_syms:
            nodes.extend(node.children)
        elikiwa node.type == token.NAME and node.value == name:
            rudisha node
    rudisha None

eleza _is_import_binding(node, name, package=None):
    """ Will reuturn node ikiwa node will agiza name, or node
        will agiza * kutoka package.  None is returned otherwise.
        See test cases for examples. """

    ikiwa node.type == syms.import_name and not package:
        imp = node.children[1]
        ikiwa imp.type == syms.dotted_as_names:
            for child in imp.children:
                ikiwa child.type == syms.dotted_as_name:
                    ikiwa child.children[2].value == name:
                        rudisha node
                elikiwa child.type == token.NAME and child.value == name:
                    rudisha node
        elikiwa imp.type == syms.dotted_as_name:
            last = imp.children[-1]
            ikiwa last.type == token.NAME and last.value == name:
                rudisha node
        elikiwa imp.type == token.NAME and imp.value == name:
            rudisha node
    elikiwa node.type == syms.import_kutoka:
        # str(...) is used to make life easier here, because
        # kutoka a.b agiza parses to ['agiza', ['a', '.', 'b'], ...]
        ikiwa package and str(node.children[1]).strip() != package:
            rudisha None
        n = node.children[3]
        ikiwa package and _find("as", n):
            # See test_kutoka_import_as for explanation
            rudisha None
        elikiwa n.type == syms.import_as_names and _find(name, n):
            rudisha node
        elikiwa n.type == syms.import_as_name:
            child = n.children[2]
            ikiwa child.type == token.NAME and child.value == name:
                rudisha node
        elikiwa n.type == token.NAME and n.value == name:
            rudisha node
        elikiwa package and n.type == token.STAR:
            rudisha node
    rudisha None
