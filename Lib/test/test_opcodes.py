# Python test set -- part 2, opcodes

agiza unittest
kutoka test agiza ann_module, support

kundi OpcodeTest(unittest.TestCase):

    eleza test_try_inside_for_loop(self):
        n = 0
        kila i kwenye range(10):
            n = n+i
            jaribu: 1/0
            tatizo NameError: pita
            tatizo ZeroDivisionError: pita
            tatizo TypeError: pita
            jaribu: pita
            tatizo: pita
            jaribu: pita
            mwishowe: pita
            n = n+i
        ikiwa n != 90:
            self.fail('try inside for')

    eleza test_setup_annotations_line(self):
        # check that SETUP_ANNOTATIONS does sio create spurious line numbers
        jaribu:
            ukijumuisha open(ann_module.__file__) kama f:
                txt = f.read()
            co = compile(txt, ann_module.__file__, 'exec')
            self.assertEqual(co.co_firstlineno, 3)
        tatizo OSError:
            pita

    eleza test_no_annotations_if_not_needed(self):
        kundi C: pita
        ukijumuisha self.assertRaises(AttributeError):
            C.__annotations__

    eleza test_use_existing_annotations(self):
        ns = {'__annotations__': {1: 2}}
        exec('x: int', ns)
        self.assertEqual(ns['__annotations__'], {'x': int, 1: 2})

    eleza test_do_not_recreate_annotations(self):
        # Don't rely on the existence of the '__annotations__' global.
        ukijumuisha support.swap_item(globals(), '__annotations__', {}):
            toa globals()['__annotations__']
            kundi C:
                toa __annotations__
                ukijumuisha self.assertRaises(NameError):
                    x: int

    eleza test_raise_class_exceptions(self):

        kundi AClass(Exception): pita
        kundi BClass(AClass): pita
        kundi CClass(Exception): pita
        kundi DClass(AClass):
            eleza __init__(self, ignore):
                pita

        jaribu: ashiria AClass()
        tatizo: pita

        jaribu: ashiria AClass()
        tatizo AClass: pita

        jaribu: ashiria BClass()
        tatizo AClass: pita

        jaribu: ashiria BClass()
        tatizo CClass: self.fail()
        tatizo: pita

        a = AClass()
        b = BClass()

        jaribu:
            ashiria b
        tatizo AClass kama v:
            self.assertEqual(v, b)
        isipokua:
            self.fail("no exception")

        # sio enough arguments
        ##jaribu:  ashiria BClass, a
        ##tatizo TypeError: pita
        ##isipokua: self.fail("no exception")

        jaribu:  ashiria DClass(a)
        tatizo DClass kama v:
            self.assertIsInstance(v, DClass)
        isipokua:
            self.fail("no exception")

    eleza test_compare_function_objects(self):

        f = eval('lambda: Tupu')
        g = eval('lambda: Tupu')
        self.assertNotEqual(f, g)

        f = eval('lambda a: a')
        g = eval('lambda a: a')
        self.assertNotEqual(f, g)

        f = eval('lambda a=1: a')
        g = eval('lambda a=1: a')
        self.assertNotEqual(f, g)

        f = eval('lambda: 0')
        g = eval('lambda: 1')
        self.assertNotEqual(f, g)

        f = eval('lambda: Tupu')
        g = eval('lambda a: Tupu')
        self.assertNotEqual(f, g)

        f = eval('lambda a: Tupu')
        g = eval('lambda b: Tupu')
        self.assertNotEqual(f, g)

        f = eval('lambda a: Tupu')
        g = eval('lambda a=Tupu: Tupu')
        self.assertNotEqual(f, g)

        f = eval('lambda a=0: Tupu')
        g = eval('lambda a=1: Tupu')
        self.assertNotEqual(f, g)

    eleza test_modulo_of_string_subclasses(self):
        kundi MyString(str):
            eleza __mod__(self, value):
                rudisha 42
        self.assertEqual(MyString() % 3, 42)


ikiwa __name__ == '__main__':
    unittest.main()
