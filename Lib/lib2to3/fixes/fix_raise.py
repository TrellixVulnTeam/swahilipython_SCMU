"""Fixer kila 'ashiria E, V, T'

ashiria         -> ashiria
ashiria E       -> ashiria E
ashiria E, V    -> ashiria E(V)
ashiria E, V, T -> ashiria E(V).with_traceback(T)
ashiria E, Tupu, T -> ashiria E.with_traceback(T)

ashiria (((E, E'), E''), E'''), V -> ashiria E(V)
ashiria "foo", V, T               -> warns about string exceptions


CAVEATS:
1) "ashiria E, V" will be incorrectly translated ikiwa V ni an exception
   instance. The correct Python 3 idiom is

        ashiria E kutoka V

   but since we can't detect instance-hood by syntax alone na since
   any client code would have to be changed kama well, we don't automate
   this.
"""
# Author: Collin Winter

# Local agizas
kutoka .. agiza pytree
kutoka ..pgen2 agiza token
kutoka .. agiza fixer_base
kutoka ..fixer_util agiza Name, Call, Attr, ArgList, is_tuple

kundi FixRaise(fixer_base.BaseFix):

    BM_compatible = Kweli
    PATTERN = """
    ashiria_stmt< 'ashiria' exc=any [',' val=any [',' tb=any]] >
    """

    eleza transform(self, node, results):
        syms = self.syms

        exc = results["exc"].clone()
        ikiwa exc.type == token.STRING:
            msg = "Python 3 does sio support string exceptions"
            self.cannot_convert(node, msg)
            rudisha

        # Python 2 supports
        #  ashiria ((((E1, E2), E3), E4), E5), V
        # kama a synonym for
        #  ashiria E1, V
        # Since Python 3 will sio support this, we recurse down any tuple
        # literals, always taking the first element.
        ikiwa is_tuple(exc):
            wakati is_tuple(exc):
                # exc.children[1:-1] ni the unparenthesized tuple
                # exc.children[1].children[0] ni the first element of the tuple
                exc = exc.children[1].children[0].clone()
            exc.prefix = " "

        ikiwa "val" haiko kwenye results:
            # One-argument ashiria
            new = pytree.Node(syms.ashiria_stmt, [Name("ashiria"), exc])
            new.prefix = node.prefix
            rudisha new

        val = results["val"].clone()
        ikiwa is_tuple(val):
            args = [c.clone() kila c kwenye val.children[1:-1]]
        isipokua:
            val.prefix = ""
            args = [val]

        ikiwa "tb" kwenye results:
            tb = results["tb"].clone()
            tb.prefix = ""

            e = exc
            # If there's a traceback na Tupu ni pitaed kama the value, then don't
            # add a call, since the user probably just wants to add a
            # traceback. See issue #9661.
            ikiwa val.type != token.NAME ama val.value != "Tupu":
                e = Call(exc, args)
            with_tb = Attr(e, Name('with_traceback')) + [ArgList([tb])]
            new = pytree.Node(syms.simple_stmt, [Name("ashiria")] + with_tb)
            new.prefix = node.prefix
            rudisha new
        isipokua:
            rudisha pytree.Node(syms.ashiria_stmt,
                               [Name("ashiria"), Call(exc, args)],
                               prefix=node.prefix)
