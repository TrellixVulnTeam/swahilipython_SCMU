"""bytecode_helper - support tools kila testing correct bytecode generation"""

agiza unittest
agiza dis
agiza io

_UNSPECIFIED = object()

kundi BytecodeTestCase(unittest.TestCase):
    """Custom assertion methods kila inspecting bytecode."""

    eleza get_disassembly_as_string(self, co):
        s = io.StringIO()
        dis.dis(co, file=s)
        rudisha s.getvalue()

    eleza assertInBytecode(self, x, opname, argval=_UNSPECIFIED):
        """Returns instr ikiwa op ni found, otherwise throws AssertionError"""
        kila instr kwenye dis.get_instructions(x):
            ikiwa instr.opname == opname:
                ikiwa argval ni _UNSPECIFIED ama instr.argval == argval:
                    rudisha instr
        disassembly = self.get_disassembly_as_string(x)
        ikiwa argval ni _UNSPECIFIED:
            msg = '%s sio found kwenye bytecode:\n%s' % (opname, disassembly)
        isipokua:
            msg = '(%s,%r) sio found kwenye bytecode:\n%s'
            msg = msg % (opname, argval, disassembly)
        self.fail(msg)

    eleza assertNotInBytecode(self, x, opname, argval=_UNSPECIFIED):
        """Throws AssertionError ikiwa op ni found"""
        kila instr kwenye dis.get_instructions(x):
            ikiwa instr.opname == opname:
                disassembly = self.get_disassembly_as_string(x)
                ikiwa argval ni _UNSPECIFIED:
                    msg = '%s occurs kwenye bytecode:\n%s' % (opname, disassembly)
                elikiwa instr.argval == argval:
                    msg = '(%s,%r) occurs kwenye bytecode:\n%s'
                    msg = msg % (opname, argval, disassembly)
                self.fail(msg)
