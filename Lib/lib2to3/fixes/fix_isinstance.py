# Copyright 2008 Armin Ronacher.
# Licensed to PSF under a Contributor Agreement.

"""Fixer that cleans up a tuple argument to isinstance after the tokens
in it were fixed.  This is mainly used to remove double occurrences of
tokens as a leftover of the long -> int / unicode -> str conversion.

eg.  isinstance(x, (int, long)) -> isinstance(x, (int, int))
       -> isinstance(x, int)
"""

kutoka .. agiza fixer_base
kutoka ..fixer_util agiza token


kundi FixIsinstance(fixer_base.BaseFix):
    BM_compatible = True
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
        for idx, arg in iterator:
            ikiwa arg.type == token.NAME and arg.value in names_inserted:
                ikiwa idx < len(args) - 1 and args[idx + 1].type == token.COMMA:
                    next(iterator)
                    continue
            else:
                new_args.append(arg)
                ikiwa arg.type == token.NAME:
                    names_inserted.add(arg.value)
        ikiwa new_args and new_args[-1].type == token.COMMA:
            del new_args[-1]
        ikiwa len(new_args) == 1:
            atom = testlist.parent
            new_args[0].prefix = atom.prefix
            atom.replace(new_args[0])
        else:
            args[:] = new_args
            node.changed()
