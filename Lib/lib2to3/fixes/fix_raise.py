"""Fixer for 'raise E, V, T'

raise         -> raise
raise E       -> raise E
raise E, V    -> raise E(V)
raise E, V, T -> raise E(V).with_traceback(T)
raise E, None, T -> raise E.with_traceback(T)

raise (((E, E'), E''), E'''), V -> raise E(V)
raise "foo", V, T               -> warns about string exceptions


CAVEATS:
1) "raise E, V" will be incorrectly translated ikiwa V is an exception
   instance. The correct Python 3 idiom is

        raise E kutoka V

   but since we can't detect instance-hood by syntax alone and since
   any client code would have to be changed as well, we don't automate
   this.
"""
# Author: Collin Winter

# Local agizas
kutoka .. agiza pytree
kutoka ..pgen2 agiza token
kutoka .. agiza fixer_base
kutoka ..fixer_util agiza Name, Call, Attr, ArgList, is_tuple

kundi FixRaise(fixer_base.BaseFix):

    BM_compatible = True
    PATTERN = """
    raise_stmt< 'raise' exc=any [',' val=any [',' tb=any]] >
    """

    eleza transform(self, node, results):
        syms = self.syms

        exc = results["exc"].clone()
        ikiwa exc.type == token.STRING:
            msg = "Python 3 does not support string exceptions"
            self.cannot_convert(node, msg)
            return

        # Python 2 supports
        #  raise ((((E1, E2), E3), E4), E5), V
        # as a synonym for
        #  raise E1, V
        # Since Python 3 will not support this, we recurse down any tuple
        # literals, always taking the first element.
        ikiwa is_tuple(exc):
            while is_tuple(exc):
                # exc.children[1:-1] is the unparenthesized tuple
                # exc.children[1].children[0] is the first element of the tuple
                exc = exc.children[1].children[0].clone()
            exc.prefix = " "

        ikiwa "val" not in results:
            # One-argument raise
            new = pytree.Node(syms.raise_stmt, [Name("raise"), exc])
            new.prefix = node.prefix
            rudisha new

        val = results["val"].clone()
        ikiwa is_tuple(val):
            args = [c.clone() for c in val.children[1:-1]]
        else:
            val.prefix = ""
            args = [val]

        ikiwa "tb" in results:
            tb = results["tb"].clone()
            tb.prefix = ""

            e = exc
            # If there's a traceback and None is passed as the value, then don't
            # add a call, since the user probably just wants to add a
            # traceback. See issue #9661.
            ikiwa val.type != token.NAME or val.value != "None":
                e = Call(exc, args)
            with_tb = Attr(e, Name('with_traceback')) + [ArgList([tb])]
            new = pytree.Node(syms.simple_stmt, [Name("raise")] + with_tb)
            new.prefix = node.prefix
            rudisha new
        else:
            rudisha pytree.Node(syms.raise_stmt,
                               [Name("raise"), Call(exc, args)],
                               prefix=node.prefix)
