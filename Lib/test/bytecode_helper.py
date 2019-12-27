"""bytecode_helper - support tools for testing correct bytecode generation"""

agiza unittest
agiza dis
agiza io

_UNSPECIFIED = object()

kundi BytecodeTestCase(unittest.TestCase):
    """Custom assertion methods for inspecting bytecode."""

    eleza get_disassembly_as_string(self, co):
        s = io.StringIO()
        dis.dis(co, file=s)
        rudisha s.getvalue()

    eleza assertInBytecode(self, x, opname, argval=_UNSPECIFIED):
        """Returns instr ikiwa op is found, otherwise throws AssertionError"""
        for instr in dis.get_instructions(x):
            ikiwa instr.opname == opname:
                ikiwa argval is _UNSPECIFIED or instr.argval == argval:
                    rudisha instr
        disassembly = self.get_disassembly_as_string(x)
        ikiwa argval is _UNSPECIFIED:
            msg = '%s not found in bytecode:\n%s' % (opname, disassembly)
        else:
            msg = '(%s,%r) not found in bytecode:\n%s'
            msg = msg % (opname, argval, disassembly)
        self.fail(msg)

    eleza assertNotInBytecode(self, x, opname, argval=_UNSPECIFIED):
        """Throws AssertionError ikiwa op is found"""
        for instr in dis.get_instructions(x):
            ikiwa instr.opname == opname:
                disassembly = self.get_disassembly_as_string(x)
                ikiwa argval is _UNSPECIFIED:
                    msg = '%s occurs in bytecode:\n%s' % (opname, disassembly)
                elikiwa instr.argval == argval:
                    msg = '(%s,%r) occurs in bytecode:\n%s'
                    msg = msg % (opname, argval, disassembly)
                self.fail(msg)
