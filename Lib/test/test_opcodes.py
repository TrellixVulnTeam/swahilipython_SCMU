# Python test set -- part 2, opcodes

agiza unittest
kutoka test agiza ann_module, support

kundi OpcodeTest(unittest.TestCase):

    eleza test_try_inside_for_loop(self):
        n = 0
        for i in range(10):
            n = n+i
            try: 1/0
            except NameError: pass
            except ZeroDivisionError: pass
            except TypeError: pass
            try: pass
            except: pass
            try: pass
            finally: pass
            n = n+i
        ikiwa n != 90:
            self.fail('try inside for')

    eleza test_setup_annotations_line(self):
        # check that SETUP_ANNOTATIONS does not create spurious line numbers
        try:
            with open(ann_module.__file__) as f:
                txt = f.read()
            co = compile(txt, ann_module.__file__, 'exec')
            self.assertEqual(co.co_firstlineno, 3)
        except OSError:
            pass

    eleza test_no_annotations_if_not_needed(self):
        kundi C: pass
        with self.assertRaises(AttributeError):
            C.__annotations__

    eleza test_use_existing_annotations(self):
        ns = {'__annotations__': {1: 2}}
        exec('x: int', ns)
        self.assertEqual(ns['__annotations__'], {'x': int, 1: 2})

    eleza test_do_not_recreate_annotations(self):
        # Don't rely on the existence of the '__annotations__' global.
        with support.swap_item(globals(), '__annotations__', {}):
            del globals()['__annotations__']
            kundi C:
                del __annotations__
                with self.assertRaises(NameError):
                    x: int

    eleza test_raise_class_exceptions(self):

        kundi AClass(Exception): pass
        kundi BClass(AClass): pass
        kundi CClass(Exception): pass
        kundi DClass(AClass):
            eleza __init__(self, ignore):
                pass

        try: raise AClass()
        except: pass

        try: raise AClass()
        except AClass: pass

        try: raise BClass()
        except AClass: pass

        try: raise BClass()
        except CClass: self.fail()
        except: pass

        a = AClass()
        b = BClass()

        try:
            raise b
        except AClass as v:
            self.assertEqual(v, b)
        else:
            self.fail("no exception")

        # not enough arguments
        ##try:  raise BClass, a
        ##except TypeError: pass
        ##else: self.fail("no exception")

        try:  raise DClass(a)
        except DClass as v:
            self.assertIsInstance(v, DClass)
        else:
            self.fail("no exception")

    eleza test_compare_function_objects(self):

        f = eval('lambda: None')
        g = eval('lambda: None')
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

        f = eval('lambda: None')
        g = eval('lambda a: None')
        self.assertNotEqual(f, g)

        f = eval('lambda a: None')
        g = eval('lambda b: None')
        self.assertNotEqual(f, g)

        f = eval('lambda a: None')
        g = eval('lambda a=None: None')
        self.assertNotEqual(f, g)

        f = eval('lambda a=0: None')
        g = eval('lambda a=1: None')
        self.assertNotEqual(f, g)

    eleza test_modulo_of_string_subclasses(self):
        kundi MyString(str):
            eleza __mod__(self, value):
                rudisha 42
        self.assertEqual(MyString() % 3, 42)


ikiwa __name__ == '__main__':
    unittest.main()
