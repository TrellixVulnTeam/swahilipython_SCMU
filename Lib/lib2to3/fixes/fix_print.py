# Copyright 2006 Google, Inc. All Rights Reserved.
# Licensed to PSF under a Contributor Agreement.

"""Fixer kila print.

Change:
    'print'          into 'andika()'
    'print ...'      into 'andika(...)'
    'print ... ,'    into 'andika(..., end=" ")'
    'print >>x, ...' into 'andika(..., file=x)'

No changes are applied ikiwa print_function ni imported kutoka __future__

"""

# Local imports
kutoka .. agiza patcomp
kutoka .. agiza pytree
kutoka ..pgen2 agiza token
kutoka .. agiza fixer_base
kutoka ..fixer_util agiza Name, Call, Comma, String


parend_expr = patcomp.compile_pattern(
              """atom< '(' [atom|STRING|NAME] ')' >"""
              )


kundi FixPrint(fixer_base.BaseFix):

    BM_compatible = Kweli

    PATTERN = """
              simple_stmt< any* bare='print' any* > | print_stmt
              """

    eleza transform(self, node, results):
        assert results

        bare_print = results.get("bare")

        ikiwa bare_print:
            # Special-case andika all by itself
            bare_print.replace(Call(Name("print"), [],
                               prefix=bare_print.prefix))
            rudisha
        assert node.children[0] == Name("print")
        args = node.children[1:]
        ikiwa len(args) == 1 na parend_expr.match(args[0]):
            # We don't want to keep sticking parens around an
            # already-parenthesised expression.
            rudisha

        sep = end = file = Tupu
        ikiwa args na args[-1] == Comma():
            args = args[:-1]
            end = " "
        ikiwa args na args[0] == pytree.Leaf(token.RIGHTSHIFT, ">>"):
            assert len(args) >= 2
            file = args[1].clone()
            args = args[3:] # Strip a possible comma after the file expression
        # Now synthesize a andika(args, sep=..., end=..., file=...) node.
        l_args = [arg.clone() kila arg kwenye args]
        ikiwa l_args:
            l_args[0].prefix = ""
        ikiwa sep ni sio Tupu ama end ni sio Tupu ama file ni sio Tupu:
            ikiwa sep ni sio Tupu:
                self.add_kwarg(l_args, "sep", String(repr(sep)))
            ikiwa end ni sio Tupu:
                self.add_kwarg(l_args, "end", String(repr(end)))
            ikiwa file ni sio Tupu:
                self.add_kwarg(l_args, "file", file)
        n_stmt = Call(Name("print"), l_args)
        n_stmt.prefix = node.prefix
        rudisha n_stmt

    eleza add_kwarg(self, l_nodes, s_kwd, n_expr):
        # XXX All this prefix-setting may lose comments (though rarely)
        n_expr.prefix = ""
        n_argument = pytree.Node(self.syms.argument,
                                 (Name(s_kwd),
                                  pytree.Leaf(token.EQUAL, "="),
                                  n_expr))
        ikiwa l_nodes:
            l_nodes.append(Comma())
            n_argument.prefix = " "
        l_nodes.append(n_argument)
