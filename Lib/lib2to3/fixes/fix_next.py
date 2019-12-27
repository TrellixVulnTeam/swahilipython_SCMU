"""Fixer for it.next() -> next(it), per PEP 3114."""
# Author: Collin Winter

# Things that currently aren't covered:
#   - listcomp "next" names aren't warned
#   - "with" statement targets aren't checked

# Local agizas
kutoka ..pgen2 agiza token
kutoka ..pygram agiza python_symbols as syms
kutoka .. agiza fixer_base
kutoka ..fixer_util agiza Name, Call, find_binding

bind_warning = "Calls to builtin next() possibly shadowed by global binding"


kundi FixNext(fixer_base.BaseFix):
    BM_compatible = True
    PATTERN = """
    power< base=any+ trailer< '.' attr='next' > trailer< '(' ')' > >
    |
    power< head=any+ trailer< '.' attr='next' > not trailer< '(' ')' > >
    |
    classdef< 'class' any+ ':'
              suite< any*
                     funcdef< 'def'
                              name='next'
                              parameters< '(' NAME ')' > any+ >
                     any* > >
    |
    global=global_stmt< 'global' any* 'next' any* >
    """

    order = "pre" # Pre-order tree traversal

    eleza start_tree(self, tree, filename):
        super(FixNext, self).start_tree(tree, filename)

        n = find_binding('next', tree)
        ikiwa n:
            self.warning(n, bind_warning)
            self.shadowed_next = True
        else:
            self.shadowed_next = False

    eleza transform(self, node, results):
        assert results

        base = results.get("base")
        attr = results.get("attr")
        name = results.get("name")

        ikiwa base:
            ikiwa self.shadowed_next:
                attr.replace(Name("__next__", prefix=attr.prefix))
            else:
                base = [n.clone() for n in base]
                base[0].prefix = ""
                node.replace(Call(Name("next", prefix=node.prefix), base))
        elikiwa name:
            n = Name("__next__", prefix=name.prefix)
            name.replace(n)
        elikiwa attr:
            # We don't do this transformation ikiwa we're assigning to "x.next".
            # Unfortunately, it doesn't seem possible to do this in PATTERN,
            #  so it's being done here.
            ikiwa is_assign_target(node):
                head = results["head"]
                ikiwa "".join([str(n) for n in head]).strip() == '__builtin__':
                    self.warning(node, bind_warning)
                return
            attr.replace(Name("__next__"))
        elikiwa "global" in results:
            self.warning(node, bind_warning)
            self.shadowed_next = True


### The following functions help test ikiwa node is part of an assignment
###  target.

eleza is_assign_target(node):
    assign = find_assign(node)
    ikiwa assign is None:
        rudisha False

    for child in assign.children:
        ikiwa child.type == token.EQUAL:
            rudisha False
        elikiwa is_subtree(child, node):
            rudisha True
    rudisha False

eleza find_assign(node):
    ikiwa node.type == syms.expr_stmt:
        rudisha node
    ikiwa node.type == syms.simple_stmt or node.parent is None:
        rudisha None
    rudisha find_assign(node.parent)

eleza is_subtree(root, node):
    ikiwa root == node:
        rudisha True
    rudisha any(is_subtree(c, node) for c in root.children)
