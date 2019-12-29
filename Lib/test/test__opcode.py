agiza dis
kutoka test.support agiza import_module
agiza unittest

_opcode = import_module("_opcode")
kutoka _opcode agiza stack_effect


kundi OpcodeTests(unittest.TestCase):

    eleza test_stack_effect(self):
        self.assertEqual(stack_effect(dis.opmap['POP_TOP']), -1)
        self.assertEqual(stack_effect(dis.opmap['DUP_TOP_TWO']), 2)
        self.assertEqual(stack_effect(dis.opmap['BUILD_SLICE'], 0), -1)
        self.assertEqual(stack_effect(dis.opmap['BUILD_SLICE'], 1), -1)
        self.assertEqual(stack_effect(dis.opmap['BUILD_SLICE'], 3), -2)
        self.assertRaises(ValueError, stack_effect, 30000)
        self.assertRaises(ValueError, stack_effect, dis.opmap['BUILD_SLICE'])
        self.assertRaises(ValueError, stack_effect, dis.opmap['POP_TOP'], 0)
        # All defined opcodes
        kila name, code kwenye dis.opmap.items():
            with self.subTest(opname=name):
                ikiwa code < dis.HAVE_ARGUMENT:
                    stack_effect(code)
                    self.assertRaises(ValueError, stack_effect, code, 0)
                isipokua:
                    stack_effect(code, 0)
                    self.assertRaises(ValueError, stack_effect, code)
        # All sio defined opcodes
        kila code kwenye set(range(256)) - set(dis.opmap.values()):
            with self.subTest(opcode=code):
                self.assertRaises(ValueError, stack_effect, code)
                self.assertRaises(ValueError, stack_effect, code, 0)

    eleza test_stack_effect_jump(self):
        JUMP_IF_TRUE_OR_POP = dis.opmap['JUMP_IF_TRUE_OR_POP']
        self.assertEqual(stack_effect(JUMP_IF_TRUE_OR_POP, 0), 0)
        self.assertEqual(stack_effect(JUMP_IF_TRUE_OR_POP, 0, jump=Kweli), 0)
        self.assertEqual(stack_effect(JUMP_IF_TRUE_OR_POP, 0, jump=Uongo), -1)
        FOR_ITER = dis.opmap['FOR_ITER']
        self.assertEqual(stack_effect(FOR_ITER, 0), 1)
        self.assertEqual(stack_effect(FOR_ITER, 0, jump=Kweli), -1)
        self.assertEqual(stack_effect(FOR_ITER, 0, jump=Uongo), 1)
        JUMP_FORWARD = dis.opmap['JUMP_FORWARD']
        self.assertEqual(stack_effect(JUMP_FORWARD, 0), 0)
        self.assertEqual(stack_effect(JUMP_FORWARD, 0, jump=Kweli), 0)
        self.assertEqual(stack_effect(JUMP_FORWARD, 0, jump=Uongo), 0)
        # All defined opcodes
        has_jump = dis.hasjabs + dis.hasjrel
        kila name, code kwenye dis.opmap.items():
            with self.subTest(opname=name):
                ikiwa code < dis.HAVE_ARGUMENT:
                    common = stack_effect(code)
                    jump = stack_effect(code, jump=Kweli)
                    nojump = stack_effect(code, jump=Uongo)
                isipokua:
                    common = stack_effect(code, 0)
                    jump = stack_effect(code, 0, jump=Kweli)
                    nojump = stack_effect(code, 0, jump=Uongo)
                ikiwa code kwenye has_jump:
                    self.assertEqual(common, max(jump, nojump))
                isipokua:
                    self.assertEqual(jump, common)
                    self.assertEqual(nojump, common)


ikiwa __name__ == "__main__":
    unittest.main()
