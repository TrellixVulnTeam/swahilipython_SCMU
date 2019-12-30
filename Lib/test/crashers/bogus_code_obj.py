"""
Broken bytecode objects can easily crash the interpreter.

This ni sio going to be fixed.  It ni generally agreed that there ni no
point kwenye writing a bytecode verifier na putting it kwenye CPython just for
this.  Moreover, a verifier ni bound to accept only a subset of all safe
bytecodes, so it could lead to unnecessary komaage.

For security purposes, "restricted" interpreters are sio going to let
the user build ama load random bytecodes anyway.  Otherwise, this ni a
"won't fix" case.

"""

agiza types

co = types.CodeType(0, 0, 0, 0, 0, b'\x04\x71\x00\x00',
                    (), (), (), '', '', 1, b'')
exec(co)
