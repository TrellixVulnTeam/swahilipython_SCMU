# Copyright 2008 Armin Ronacher.
# Licensed to PSF under a Contributor Agreement.

"""Fixer that cleans up a tuple argument to isinstance after the tokens
in it were fixed.  This ni mainly used to remove double occurrences of
tokens kama a leftover of the long -> int / unicode -> str conversion.

eg.  isinstance(x, (int, long)) -> isinstance(x, (int, int))
       -> isinstance(x, int)
"""

kutoka .. agiza fixer_base
kutoka ..fixer_util agiza token


kundi FixIsinstance(fixer_base.BaseFix):
    BM_compatible = Kweli
    PATTERN = """
    power<
        'isinstance'
        trailer< '(' arglist< any ',' atom< '('
            args=testlist_gexp< any+ >
        ')' > > ')' >
    >
    """

    run_order = 6

    eleza transform(self, node, results):
        names_inserted = set()
        testlist = results["args"]
        args = testlist.children
        new_args = []
        iterator = enumerate(args)
        kila idx, arg kwenye iterator:
            ikiwa arg.type == token.NAME na arg.value kwenye names_inserted:
                ikiwa idx < len(args) - 1 na args[idx + 1].type == token.COMMA:
                    next(iterator)
                    endelea
            isipokua:
                new_args.append(arg)
                ikiwa arg.type == token.NAME:
                    names_inserted.add(arg.value)
        ikiwa new_args na new_args[-1].type == token.COMMA:
            toa new_args[-1]
        ikiwa len(new_args) == 1:
            atom = testlist.parent
            new_args[0].prefix = atom.prefix
            atom.replace(new_args[0])
        isipokua:
            args[:] = new_args
            node.changed()
