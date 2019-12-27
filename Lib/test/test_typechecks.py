"""Unit tests for __instancecheck__ and __subclasscheck__."""

agiza unittest


kundi ABC(type):

    eleza __instancecheck__(cls, inst):
        """Implement isinstance(inst, cls)."""
        rudisha any(cls.__subclasscheck__(c)
                   for c in {type(inst), inst.__class__})

    eleza __subclasscheck__(cls, sub):
        """Implement issubclass(sub, cls)."""
        candidates = cls.__dict__.get("__subclass__", set()) | {cls}
        rudisha any(c in candidates for c in sub.mro())


kundi Integer(metaclass=ABC):
    __subclass__ = {int}


kundi SubInt(Integer):
    pass


kundi TypeChecksTest(unittest.TestCase):

    eleza testIsSubclassInternal(self):
        self.assertEqual(Integer.__subclasscheck__(int), True)
        self.assertEqual(Integer.__subclasscheck__(float), False)

    eleza testIsSubclassBuiltin(self):
        self.assertEqual(issubclass(int, Integer), True)
        self.assertEqual(issubclass(int, (Integer,)), True)
        self.assertEqual(issubclass(float, Integer), False)
        self.assertEqual(issubclass(float, (Integer,)), False)

    eleza testIsInstanceBuiltin(self):
        self.assertEqual(isinstance(42, Integer), True)
        self.assertEqual(isinstance(42, (Integer,)), True)
        self.assertEqual(isinstance(3.14, Integer), False)
        self.assertEqual(isinstance(3.14, (Integer,)), False)

    eleza testIsInstanceActual(self):
        self.assertEqual(isinstance(Integer(), Integer), True)
        self.assertEqual(isinstance(Integer(), (Integer,)), True)

    eleza testIsSubclassActual(self):
        self.assertEqual(issubclass(Integer, Integer), True)
        self.assertEqual(issubclass(Integer, (Integer,)), True)

    eleza testSubclassBehavior(self):
        self.assertEqual(issubclass(SubInt, Integer), True)
        self.assertEqual(issubclass(SubInt, (Integer,)), True)
        self.assertEqual(issubclass(SubInt, SubInt), True)
        self.assertEqual(issubclass(SubInt, (SubInt,)), True)
        self.assertEqual(issubclass(Integer, SubInt), False)
        self.assertEqual(issubclass(Integer, (SubInt,)), False)
        self.assertEqual(issubclass(int, SubInt), False)
        self.assertEqual(issubclass(int, (SubInt,)), False)
        self.assertEqual(isinstance(SubInt(), Integer), True)
        self.assertEqual(isinstance(SubInt(), (Integer,)), True)
        self.assertEqual(isinstance(SubInt(), SubInt), True)
        self.assertEqual(isinstance(SubInt(), (SubInt,)), True)
        self.assertEqual(isinstance(42, SubInt), False)
        self.assertEqual(isinstance(42, (SubInt,)), False)


ikiwa __name__ == "__main__":
    unittest.main()
