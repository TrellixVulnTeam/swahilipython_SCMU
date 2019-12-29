# Copyright 2006 Google, Inc. All Rights Reserved.
# Licensed to PSF under a Contributor Agreement.

"""Fixer kila execfile.

This converts usages of the execfile function into calls to the built-in
exec() function.
"""

kutoka .. agiza fixer_base
kutoka ..fixer_util agiza (Comma, Name, Call, LParen, RParen, Dot, Node,
                          ArgList, String, syms)


kundi FixExecfile(fixer_base.BaseFix):
    BM_compatible = Kweli

    PATTERN = """
    power< 'execfile' trailer< '(' arglist< filename=any [',' globals=any [',' locals=any ] ] > ')' > >
    |
    power< 'execfile' trailer< '(' filename=any ')' > >
    """

    eleza transform(self, node, results):
        assert results
        filename = results["filename"]
        globals = results.get("globals")
        locals = results.get("locals")

        # Copy over the prefix kutoka the right parentheses end of the execfile
        # call.
        execfile_paren = node.children[-1].children[-1].clone()
        # Construct open().read().
        open_args = ArgList([filename.clone(), Comma(), String('"rb"', ' ')],
                            rparen=execfile_paren)
        open_call = Node(syms.power, [Name("open"), open_args])
        read = [Node(syms.trailer, [Dot(), Name('read')]),
                Node(syms.trailer, [LParen(), RParen()])]
        open_expr = [open_call] + read
        # Wrap the open call kwenye a compile call. This ni so the filename will be
        # preserved kwenye the execed code.
        filename_arg = filename.clone()
        filename_arg.prefix = " "
        exec_str = String("'exec'", " ")
        compile_args = open_expr + [Comma(), filename_arg, Comma(), exec_str]
        compile_call = Call(Name("compile"), compile_args, "")
        # Finally, replace the execfile call ukijumuisha an exec call.
        args = [compile_call]
        ikiwa globals ni sio Tupu:
            args.extend([Comma(), globals.clone()])
        ikiwa locals ni sio Tupu:
            args.extend([Comma(), locals.clone()])
        rudisha Call(Name("exec"), args, prefix=node.prefix)
