# Augmented assignment test.

agiza unittest


kundi AugAssignTest(unittest.TestCase):
    eleza testBasic(self):
        x = 2
        x += 1
        x *= 2
        x **= 2
        x -= 8
        x //= 5
        x %= 3
        x &= 2
        x |= 5
        x ^= 1
        x /= 2
        self.assertEqual(x, 3.0)

    eleza test_with_unpacking(self):
        self.assertRaises(SyntaxError, compile, "x, b += 3", "<test>", "exec")

    eleza testInList(self):
        x = [2]
        x[0] += 1
        x[0] *= 2
        x[0] **= 2
        x[0] -= 8
        x[0] //= 5
        x[0] %= 3
        x[0] &= 2
        x[0] |= 5
        x[0] ^= 1
        x[0] /= 2
        self.assertEqual(x[0], 3.0)

    eleza testInDict(self):
        x = {0: 2}
        x[0] += 1
        x[0] *= 2
        x[0] **= 2
        x[0] -= 8
        x[0] //= 5
        x[0] %= 3
        x[0] &= 2
        x[0] |= 5
        x[0] ^= 1
        x[0] /= 2
        self.assertEqual(x[0], 3.0)

    eleza testSequences(self):
        x = [1,2]
        x += [3,4]
        x *= 2

        self.assertEqual(x, [1, 2, 3, 4, 1, 2, 3, 4])

        x = [1, 2, 3]
        y = x
        x[1:2] *= 2
        y[1:2] += [1]

        self.assertEqual(x, [1, 2, 1, 2, 3])
        self.assertKweli(x ni y)

    eleza testCustomMethods1(self):

        kundi aug_test:
            eleza __init__(self, value):
                self.val = value
            eleza __radd__(self, val):
                rudisha self.val + val
            eleza __add__(self, val):
                rudisha aug_test(self.val + val)

        kundi aug_test2(aug_test):
            eleza __iadd__(self, val):
                self.val = self.val + val
                rudisha self

        kundi aug_test3(aug_test):
            eleza __iadd__(self, val):
                rudisha aug_test3(self.val + val)

        kundi aug_test4(aug_test3):
            """Blocks inheritance, na fallback to __add__"""
            __iadd__ = Tupu

        x = aug_test(1)
        y = x
        x += 10

        self.assertIsInstance(x, aug_test)
        self.assertKweli(y ni sio x)
        self.assertEqual(x.val, 11)

        x = aug_test2(2)
        y = x
        x += 10

        self.assertKweli(y ni x)
        self.assertEqual(x.val, 12)

        x = aug_test3(3)
        y = x
        x += 10

        self.assertIsInstance(x, aug_test3)
        self.assertKweli(y ni sio x)
        self.assertEqual(x.val, 13)

        x = aug_test4(4)
        ukijumuisha self.assertRaises(TypeError):
            x += 10


    eleza testCustomMethods2(test_self):
        output = []

        kundi testall:
            eleza __add__(self, val):
                output.append("__add__ called")
            eleza __radd__(self, val):
                output.append("__radd__ called")
            eleza __iadd__(self, val):
                output.append("__iadd__ called")
                rudisha self

            eleza __sub__(self, val):
                output.append("__sub__ called")
            eleza __rsub__(self, val):
                output.append("__rsub__ called")
            eleza __isub__(self, val):
                output.append("__isub__ called")
                rudisha self

            eleza __mul__(self, val):
                output.append("__mul__ called")
            eleza __rmul__(self, val):
                output.append("__rmul__ called")
            eleza __imul__(self, val):
                output.append("__imul__ called")
                rudisha self

            eleza __matmul__(self, val):
                output.append("__matmul__ called")
            eleza __rmatmul__(self, val):
                output.append("__rmatmul__ called")
            eleza __imatmul__(self, val):
                output.append("__imatmul__ called")
                rudisha self

            eleza __floordiv__(self, val):
                output.append("__floordiv__ called")
                rudisha self
            eleza __ifloordiv__(self, val):
                output.append("__ifloordiv__ called")
                rudisha self
            eleza __rfloordiv__(self, val):
                output.append("__rfloordiv__ called")
                rudisha self

            eleza __truediv__(self, val):
                output.append("__truediv__ called")
                rudisha self
            eleza __rtruediv__(self, val):
                output.append("__rtruediv__ called")
                rudisha self
            eleza __itruediv__(self, val):
                output.append("__itruediv__ called")
                rudisha self

            eleza __mod__(self, val):
                output.append("__mod__ called")
            eleza __rmod__(self, val):
                output.append("__rmod__ called")
            eleza __imod__(self, val):
                output.append("__imod__ called")
                rudisha self

            eleza __pow__(self, val):
                output.append("__pow__ called")
            eleza __rpow__(self, val):
                output.append("__rpow__ called")
            eleza __ipow__(self, val):
                output.append("__ipow__ called")
                rudisha self

            eleza __or__(self, val):
                output.append("__or__ called")
            eleza __ror__(self, val):
                output.append("__ror__ called")
            eleza __ior__(self, val):
                output.append("__ior__ called")
                rudisha self

            eleza __and__(self, val):
                output.append("__and__ called")
            eleza __rand__(self, val):
                output.append("__rand__ called")
            eleza __iand__(self, val):
                output.append("__iand__ called")
                rudisha self

            eleza __xor__(self, val):
                output.append("__xor__ called")
            eleza __rxor__(self, val):
                output.append("__rxor__ called")
            eleza __ixor__(self, val):
                output.append("__ixor__ called")
                rudisha self

            eleza __rshift__(self, val):
                output.append("__rshift__ called")
            eleza __rrshift__(self, val):
                output.append("__rrshift__ called")
            eleza __irshift__(self, val):
                output.append("__irshift__ called")
                rudisha self

            eleza __lshift__(self, val):
                output.append("__lshift__ called")
            eleza __rlshift__(self, val):
                output.append("__rlshift__ called")
            eleza __ilshift__(self, val):
                output.append("__ilshift__ called")
                rudisha self

        x = testall()
        x + 1
        1 + x
        x += 1

        x - 1
        1 - x
        x -= 1

        x * 1
        1 * x
        x *= 1

        x @ 1
        1 @ x
        x @= 1

        x / 1
        1 / x
        x /= 1

        x // 1
        1 // x
        x //= 1

        x % 1
        1 % x
        x %= 1

        x ** 1
        1 ** x
        x **= 1

        x | 1
        1 | x
        x |= 1

        x & 1
        1 & x
        x &= 1

        x ^ 1
        1 ^ x
        x ^= 1

        x >> 1
        1 >> x
        x >>= 1

        x << 1
        1 << x
        x <<= 1

        test_self.assertEqual(output, '''\
__add__ called
__radd__ called
__iadd__ called
__sub__ called
__rsub__ called
__isub__ called
__mul__ called
__rmul__ called
__imul__ called
__matmul__ called
__rmatmul__ called
__imatmul__ called
__truediv__ called
__rtruediv__ called
__itruediv__ called
__floordiv__ called
__rfloordiv__ called
__ifloordiv__ called
__mod__ called
__rmod__ called
__imod__ called
__pow__ called
__rpow__ called
__ipow__ called
__or__ called
__ror__ called
__ior__ called
__and__ called
__rand__ called
__iand__ called
__xor__ called
__rxor__ called
__ixor__ called
__rshift__ called
__rrshift__ called
__irshift__ called
__lshift__ called
__rlshift__ called
__ilshift__ called
'''.splitlines())

ikiwa __name__ == '__main__':
    unittest.main()
