"""Fixer kila generator.throw(E, V, T).

g.throw(E)       -> g.throw(E)
g.throw(E, V)    -> g.throw(E(V))
g.throw(E, V, T) -> g.throw(E(V).with_traceback(T))

g.throw("foo"[, V[, T]]) will warn about string exceptions."""
# Author: Collin Winter

# Local imports
kutoka .. agiza pytree
kutoka ..pgen2 agiza token
kutoka .. agiza fixer_base
kutoka ..fixer_util agiza Name, Call, ArgList, Attr, is_tuple

kundi FixThrow(fixer_base.BaseFix):
    BM_compatible = Kweli
    PATTERN = """
    power< any trailer< '.' 'throw' >
           trailer< '(' args=arglist< exc=any ',' val=any [',' tb=any] > ')' >
    >
    |
    power< any trailer< '.' 'throw' > trailer< '(' exc=any ')' > >
    """

    eleza transform(self, node, results):
        syms = self.syms

        exc = results["exc"].clone()
        ikiwa exc.type ni token.STRING:
            self.cannot_convert(node, "Python 3 does sio support string exceptions")
            return

        # Leave "g.throw(E)" alone
        val = results.get("val")
        ikiwa val ni Tupu:
            return

        val = val.clone()
        ikiwa is_tuple(val):
            args = [c.clone() kila c kwenye val.children[1:-1]]
        isipokua:
            val.prefix = ""
            args = [val]

        throw_args = results["args"]

        ikiwa "tb" kwenye results:
            tb = results["tb"].clone()
            tb.prefix = ""

            e = Call(exc, args)
            with_tb = Attr(e, Name('with_traceback')) + [ArgList([tb])]
            throw_args.replace(pytree.Node(syms.power, with_tb))
        isipokua:
            throw_args.replace(Call(exc, args))
