"""
These tests are meant to exercise that requests to create objects bigger
than what the address space allows are properly met with an OverflowError
(rather than crash weirdly).

Primarily, this means 32-bit builds with at least 2 GiB of available memory.
You need to pass the -M option to regrtest (e.g. "-M 2.1G") for tests to
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
        # the address space, and then try to build a new, larger one through
        # concatenation.
        try:
            x = b"x" * (MAX_Py_ssize_t - 128)
            self.assertRaises(OverflowError, operator.add, x, b"x" * 128)
        finally:
            x = None

    @bigaddrspacetest
    eleza test_optimized_concat(self):
        try:
            x = b"x" * (MAX_Py_ssize_t - 128)

            with self.assertRaises(OverflowError) as cm:
                # this statement used a fast path in ceval.c
                x = x + b"x" * 128

            with self.assertRaises(OverflowError) as cm:
                # this statement used a fast path in ceval.c
                x +=  b"x" * 128
        finally:
            x = None

    @bigaddrspacetest
    eleza test_repeat(self):
        try:
            x = b"x" * (MAX_Py_ssize_t - 128)
            self.assertRaises(OverflowError, operator.mul, x, 128)
        finally:
            x = None


kundi StrTest(unittest.TestCase):

    unicodesize = 2 ikiwa sys.maxunicode < 65536 else 4

    @bigaddrspacetest
    eleza test_concat(self):
        try:
            # Create a string that would fill almost the address space
            x = "x" * int(MAX_Py_ssize_t // (1.1 * self.unicodesize))
            # Unicode objects trigger MemoryError in case an operation that's
            # going to cause a size overflow is executed
            self.assertRaises(MemoryError, operator.add, x, x)
        finally:
            x = None

    @bigaddrspacetest
    eleza test_optimized_concat(self):
        try:
            x = "x" * int(MAX_Py_ssize_t // (1.1 * self.unicodesize))

            with self.assertRaises(MemoryError) as cm:
                # this statement uses a fast path in ceval.c
                x = x + x

            with self.assertRaises(MemoryError) as cm:
                # this statement uses a fast path in ceval.c
                x +=  x
        finally:
            x = None

    @bigaddrspacetest
    eleza test_repeat(self):
        try:
            x = "x" * int(MAX_Py_ssize_t // (1.1 * self.unicodesize))
            self.assertRaises(MemoryError, operator.mul, x, 2)
        finally:
            x = None


eleza test_main():
    support.run_unittest(BytesTest, StrTest)

ikiwa __name__ == '__main__':
    ikiwa len(sys.argv) > 1:
        support.set_memlimit(sys.argv[1])
    test_main()
