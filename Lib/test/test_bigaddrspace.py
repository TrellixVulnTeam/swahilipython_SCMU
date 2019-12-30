"""
These tests are meant to exercise that requests to create objects bigger
than what the address space allows are properly met ukijumuisha an OverflowError
(rather than crash weirdly).

Primarily, this means 32-bit builds ukijumuisha at least 2 GiB of available memory.
You need to pita the -M option to regrtest (e.g. "-M 2.1G") kila tests to
be enabled.
"""

kutoka test agiza support
kutoka test.support agiza bigaddrspacetest, MAX_Py_ssize_t

agiza unittest
agiza operator
agiza sys


kundi BytesTest(unittest.TestCase):

    @bigaddrspacetest
    eleza test_concat(self):
        # Allocate a bytestring that's near the maximum size allowed by
        # the address space, na then try to build a new, larger one through
        # concatenation.
        jaribu:
            x = b"x" * (MAX_Py_ssize_t - 128)
            self.assertRaises(OverflowError, operator.add, x, b"x" * 128)
        mwishowe:
            x = Tupu

    @bigaddrspacetest
    eleza test_optimized_concat(self):
        jaribu:
            x = b"x" * (MAX_Py_ssize_t - 128)

            ukijumuisha self.assertRaises(OverflowError) kama cm:
                # this statement used a fast path kwenye ceval.c
                x = x + b"x" * 128

            ukijumuisha self.assertRaises(OverflowError) kama cm:
                # this statement used a fast path kwenye ceval.c
                x +=  b"x" * 128
        mwishowe:
            x = Tupu

    @bigaddrspacetest
    eleza test_repeat(self):
        jaribu:
            x = b"x" * (MAX_Py_ssize_t - 128)
            self.assertRaises(OverflowError, operator.mul, x, 128)
        mwishowe:
            x = Tupu


kundi StrTest(unittest.TestCase):

    unicodesize = 2 ikiwa sys.maxunicode < 65536 isipokua 4

    @bigaddrspacetest
    eleza test_concat(self):
        jaribu:
            # Create a string that would fill almost the address space
            x = "x" * int(MAX_Py_ssize_t // (1.1 * self.unicodesize))
            # Unicode objects trigger MemoryError kwenye case an operation that's
            # going to cause a size overflow ni executed
            self.assertRaises(MemoryError, operator.add, x, x)
        mwishowe:
            x = Tupu

    @bigaddrspacetest
    eleza test_optimized_concat(self):
        jaribu:
            x = "x" * int(MAX_Py_ssize_t // (1.1 * self.unicodesize))

            ukijumuisha self.assertRaises(MemoryError) kama cm:
                # this statement uses a fast path kwenye ceval.c
                x = x + x

            ukijumuisha self.assertRaises(MemoryError) kama cm:
                # this statement uses a fast path kwenye ceval.c
                x +=  x
        mwishowe:
            x = Tupu

    @bigaddrspacetest
    eleza test_repeat(self):
        jaribu:
            x = "x" * int(MAX_Py_ssize_t // (1.1 * self.unicodesize))
            self.assertRaises(MemoryError, operator.mul, x, 2)
        mwishowe:
            x = Tupu


eleza test_main():
    support.run_unittest(BytesTest, StrTest)

ikiwa __name__ == '__main__':
    ikiwa len(sys.argv) > 1:
        support.set_memlimit(sys.argv[1])
    test_main()
