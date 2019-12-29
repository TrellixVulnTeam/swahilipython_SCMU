"""Fixer kila __metaclass__ = X -> (metaclass=X) methods.

   The various forms of classef (inherits nothing, inherits once, inherits
   many) don't parse the same kwenye the CST so we look at ALL classes for
   a __metaclass__ na ikiwa we find one normalize the inherits to all be
   an arglist.

   For one-liner classes ('kundi X: pita') there ni no indent/dedent so
   we normalize those into having a suite.

   Moving the __metaclass__ into the classeleza can also cause the class
   body to be empty so there ni some special casing kila that kama well.

   This fixer also tries very hard to keep original indenting na spacing
   kwenye all those corner cases.

"""
# Author: Jack Diederich

# Local agizas
kutoka .. agiza fixer_base
kutoka ..pygram agiza token
kutoka ..fixer_util agiza syms, Node, Leaf


eleza has_metaclass(parent):
    """ we have to check the cls_node without changing it.
        There are two possibilities:
          1)  clseleza => suite => simple_stmt => expr_stmt => Leaf('__meta')
          2)  clseleza => simple_stmt => expr_stmt => Leaf('__meta')
    """
    kila node kwenye parent.children:
        ikiwa node.type == syms.suite:
            rudisha has_metaclass(node)
        lasivyo node.type == syms.simple_stmt na node.children:
            expr_node = node.children[0]
            ikiwa expr_node.type == syms.expr_stmt na expr_node.children:
                left_side = expr_node.children[0]
                ikiwa isinstance(left_side, Leaf) na \
                        left_side.value == '__metaclass__':
                    rudisha Kweli
    rudisha Uongo


eleza fixup_parse_tree(cls_node):
    """ one-line classes don't get a suite kwenye the parse tree so we add
        one to normalize the tree
    """
    kila node kwenye cls_node.children:
        ikiwa node.type == syms.suite:
            # already kwenye the preferred format, do nothing
            rudisha

    # !%@#! oneliners have no suite node, we have to fake one up
    kila i, node kwenye enumerate(cls_node.children):
        ikiwa node.type == token.COLON:
            koma
    isipokua:
        ashiria ValueError("No kundi suite na no ':'!")

    # move everything into a suite node
    suite = Node(syms.suite, [])
    wakati cls_node.children[i+1:]:
        move_node = cls_node.children[i+1]
        suite.append_child(move_node.clone())
        move_node.remove()
    cls_node.append_child(suite)
    node = suite


eleza fixup_simple_stmt(parent, i, stmt_node):
    """ ikiwa there ni a semi-colon all the parts count kama part of the same
        simple_stmt.  We just want the __metaclass__ part so we move
        everything after the semi-colon into its own simple_stmt node
    """
    kila semi_ind, node kwenye enumerate(stmt_node.children):
        ikiwa node.type == token.SEMI: # *sigh*
            koma
    isipokua:
        rudisha

    node.remove() # kill the semicolon
    new_expr = Node(syms.expr_stmt, [])
    new_stmt = Node(syms.simple_stmt, [new_expr])
    wakati stmt_node.children[semi_ind:]:
        move_node = stmt_node.children[semi_ind]
        new_expr.append_child(move_node.clone())
        move_node.remove()
    parent.insert_child(i, new_stmt)
    new_leaf1 = new_stmt.children[0].children[0]
    old_leaf1 = stmt_node.children[0].children[0]
    new_leaf1.prefix = old_leaf1.prefix


eleza remove_trailing_newline(node):
    ikiwa node.children na node.children[-1].type == token.NEWLINE:
        node.children[-1].remove()


eleza find_metas(cls_node):
    # find the suite node (Mmm, sweet nodes)
    kila node kwenye cls_node.children:
        ikiwa node.type == syms.suite:
            koma
    isipokua:
        ashiria ValueError("No kundi suite!")

    # look kila simple_stmt[ expr_stmt[ Leaf('__metaclass__') ] ]
    kila i, simple_node kwenye list(enumerate(node.children)):
        ikiwa simple_node.type == syms.simple_stmt na simple_node.children:
            expr_node = simple_node.children[0]
            ikiwa expr_node.type == syms.expr_stmt na expr_node.children:
                # Check ikiwa the expr_node ni a simple assignment.
                left_node = expr_node.children[0]
                ikiwa isinstance(left_node, Leaf) na \
                        left_node.value == '__metaclass__':
                    # We found an assignment to __metaclass__.
                    fixup_simple_stmt(node, i, simple_node)
                    remove_trailing_newline(simple_node)
                    tuma (node, i, simple_node)


eleza fixup_indent(suite):
    """ If an INDENT ni followed by a thing ukijumuisha a prefix then nuke the prefix
        Otherwise we get kwenye trouble when removing __metaclass__ at suite start
    """
    kids = suite.children[::-1]
    # find the first indent
    wakati kids:
        node = kids.pop()
        ikiwa node.type == token.INDENT:
            koma

    # find the first Leaf
    wakati kids:
        node = kids.pop()
        ikiwa isinstance(node, Leaf) na node.type != token.DEDENT:
            ikiwa node.prefix:
                node.prefix = ''
            rudisha
        isipokua:
            kids.extend(node.children[::-1])


kundi FixMetaclass(fixer_base.BaseFix):
    BM_compatible = Kweli

    PATTERN = """
    classdef<any*>
    """

    eleza transform(self, node, results):
        ikiwa sio has_metaclass(node):
            rudisha

        fixup_parse_tree(node)

        # find metaclasses, keep the last one
        last_metakundi = Tupu
        kila suite, i, stmt kwenye find_metas(node):
            last_metakundi = stmt
            stmt.remove()

        text_type = node.children[0].type # always Leaf(nnn, 'class')

        # figure out what kind of classeleza we have
        ikiwa len(node.children) == 7:
            # Node(classdef, ['class', 'name', '(', arglist, ')', ':', suite])
            #                 0        1       2    3        4    5    6
            ikiwa node.children[3].type == syms.arglist:
                arglist = node.children[3]
            # Node(classdef, ['class', 'name', '(', 'Parent', ')', ':', suite])
            isipokua:
                parent = node.children[3].clone()
                arglist = Node(syms.arglist, [parent])
                node.set_child(3, arglist)
        lasivyo len(node.children) == 6:
            # Node(classdef, ['class', 'name', '(',  ')', ':', suite])
            #                 0        1       2     3    4    5
            arglist = Node(syms.arglist, [])
            node.insert_child(3, arglist)
        lasivyo len(node.children) == 4:
            # Node(classdef, ['class', 'name', ':', suite])
            #                 0        1       2    3
            arglist = Node(syms.arglist, [])
            node.insert_child(2, Leaf(token.RPAR, ')'))
            node.insert_child(2, arglist)
            node.insert_child(2, Leaf(token.LPAR, '('))
        isipokua:
            ashiria ValueError("Unexpected kundi definition")

        # now stick the metakundi kwenye the arglist
        meta_txt = last_metaclass.children[0].children[0]
        meta_txt.value = 'metaclass'
        orig_meta_prefix = meta_txt.prefix

        ikiwa arglist.children:
            arglist.append_child(Leaf(token.COMMA, ','))
            meta_txt.prefix = ' '
        isipokua:
            meta_txt.prefix = ''

        # compact the expression "metakundi = Meta" -> "metaclass=Meta"
        expr_stmt = last_metaclass.children[0]
        assert expr_stmt.type == syms.expr_stmt
        expr_stmt.children[1].prefix = ''
        expr_stmt.children[2].prefix = ''

        arglist.append_child(last_metaclass)

        fixup_indent(suite)

        # check kila empty suite
        ikiwa sio suite.children:
            # one-liner that was just __metaclass_
            suite.remove()
            pita_leaf = Leaf(text_type, 'pita')
            pita_leaf.prefix = orig_meta_prefix
            node.append_child(pita_leaf)
            node.append_child(Leaf(token.NEWLINE, '\n'))

        lasivyo len(suite.children) > 1 na \
                 (suite.children[-2].type == token.INDENT and
                  suite.children[-1].type == token.DEDENT):
            # there was only one line kwenye the kundi body na it was __metaclass__
            pita_leaf = Leaf(text_type, 'pita')
            suite.insert_child(-1, pita_leaf)
            suite.insert_child(-1, Leaf(token.NEWLINE, '\n'))
