"""Unit tests kila __instancecheck__ na __subclasscheck__."""

agiza unittest


kundi ABC(type):

    eleza __instancecheck__(cls, inst):
        """Implement isinstance(inst, cls)."""
        rudisha any(cls.__subclasscheck__(c)
                   kila c kwenye {type(inst), inst.__class__})

    eleza __subclasscheck__(cls, sub):
        """Implement issubclass(sub, cls)."""
        candidates = cls.__dict__.get("__subclass__", set()) | {cls}
        rudisha any(c kwenye candidates kila c kwenye sub.mro())


kundi Integer(metaclass=ABC):
    __subclass__ = {int}


kundi SubInt(Integer):
    pita


kundi TypeChecksTest(unittest.TestCase):

    eleza testIsSubclassInternal(self):
        self.assertEqual(Integer.__subclasscheck__(int), Kweli)
        self.assertEqual(Integer.__subclasscheck__(float), Uongo)

    eleza testIsSubclassBuiltin(self):
        self.assertEqual(issubclass(int, Integer), Kweli)
        self.assertEqual(issubclass(int, (Integer,)), Kweli)
        self.assertEqual(issubclass(float, Integer), Uongo)
        self.assertEqual(issubclass(float, (Integer,)), Uongo)

    eleza testIsInstanceBuiltin(self):
        self.assertEqual(isinstance(42, Integer), Kweli)
        self.assertEqual(isinstance(42, (Integer,)), Kweli)
        self.assertEqual(isinstance(3.14, Integer), Uongo)
        self.assertEqual(isinstance(3.14, (Integer,)), Uongo)

    eleza testIsInstanceActual(self):
        self.assertEqual(isinstance(Integer(), Integer), Kweli)
        self.assertEqual(isinstance(Integer(), (Integer,)), Kweli)

    eleza testIsSubclassActual(self):
        self.assertEqual(issubclass(Integer, Integer), Kweli)
        self.assertEqual(issubclass(Integer, (Integer,)), Kweli)

    eleza testSubclassBehavior(self):
        self.assertEqual(issubclass(SubInt, Integer), Kweli)
        self.assertEqual(issubclass(SubInt, (Integer,)), Kweli)
        self.assertEqual(issubclass(SubInt, SubInt), Kweli)
        self.assertEqual(issubclass(SubInt, (SubInt,)), Kweli)
        self.assertEqual(issubclass(Integer, SubInt), Uongo)
        self.assertEqual(issubclass(Integer, (SubInt,)), Uongo)
        self.assertEqual(issubclass(int, SubInt), Uongo)
        self.assertEqual(issubclass(int, (SubInt,)), Uongo)
        self.assertEqual(isinstance(SubInt(), Integer), Kweli)
        self.assertEqual(isinstance(SubInt(), (Integer,)), Kweli)
        self.assertEqual(isinstance(SubInt(), SubInt), Kweli)
        self.assertEqual(isinstance(SubInt(), (SubInt,)), Kweli)
        self.assertEqual(isinstance(42, SubInt), Uongo)
        self.assertEqual(isinstance(42, (SubInt,)), Uongo)


ikiwa __name__ == "__main__":
    unittest.main()
