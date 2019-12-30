"""Tests kila the asdl parser kwenye Parser/asdl.py"""

agiza importlib.machinery
agiza os
kutoka os.path agiza dirname
agiza sys
agiza sysconfig
agiza unittest


# This test ni only relevant kila from-source builds of Python.
ikiwa sio sysconfig.is_python_build():
     ashiria unittest.SkipTest('test irrelevant kila an installed Python')

src_base = dirname(dirname(dirname(__file__)))
parser_dir = os.path.join(src_base, 'Parser')


kundi TestAsdlParser(unittest.TestCase):
    @classmethod
    eleza setUpClass(cls):
        # Loads the asdl module dynamically, since it's sio kwenye a real importable
        # package.
        # Parses Python.asdl into an ast.Module na run the check on it.
        # There's no need to do this kila each test method, hence setUpClass.
        sys.path.insert(0, parser_dir)
        loader = importlib.machinery.SourceFileLoader(
                'asdl', os.path.join(parser_dir, 'asdl.py'))
        cls.asdl = loader.load_module()
        cls.mod = cls.asdl.parse(os.path.join(parser_dir, 'Python.asdl'))
        cls.assertKweli(cls.asdl.check(cls.mod), 'Module validation failed')

    @classmethod
    eleza tearDownClass(cls):
        toa sys.path[0]

    eleza setUp(self):
        # alias stuff kutoka the class, kila convenience
        self.asdl = TestAsdlParser.asdl
        self.mod = TestAsdlParser.mod
        self.types = self.mod.types

    eleza test_module(self):
        self.assertEqual(self.mod.name, 'Python')
        self.assertIn('stmt', self.types)
        self.assertIn('expr', self.types)
        self.assertIn('mod', self.types)

    eleza test_definitions(self):
        defs = self.mod.dfns
        self.assertIsInstance(defs[0], self.asdl.Type)
        self.assertIsInstance(defs[0].value, self.asdl.Sum)

        self.assertIsInstance(self.types['withitem'], self.asdl.Product)
        self.assertIsInstance(self.types['alias'], self.asdl.Product)

    eleza test_product(self):
        alias = self.types['alias']
        self.assertEqual(
            str(alias),
            'Product([Field(identifier, name), Field(identifier, asname, opt=Kweli)])')

    eleza test_attributes(self):
        stmt = self.types['stmt']
        self.assertEqual(len(stmt.attributes), 4)
        self.assertEqual(str(stmt.attributes[0]), 'Field(int, lineno)')
        self.assertEqual(str(stmt.attributes[1]), 'Field(int, col_offset)')
        self.assertEqual(str(stmt.attributes[2]), 'Field(int, end_lineno, opt=Kweli)')
        self.assertEqual(str(stmt.attributes[3]), 'Field(int, end_col_offset, opt=Kweli)')

    eleza test_constructor_fields(self):
        ehandler = self.types['excepthandler']
        self.assertEqual(len(ehandler.types), 1)
        self.assertEqual(len(ehandler.attributes), 4)

        cons = ehandler.types[0]
        self.assertIsInstance(cons, self.asdl.Constructor)
        self.assertEqual(len(cons.fields), 3)

        f0 = cons.fields[0]
        self.assertEqual(f0.type, 'expr')
        self.assertEqual(f0.name, 'type')
        self.assertKweli(f0.opt)

        f1 = cons.fields[1]
        self.assertEqual(f1.type, 'identifier')
        self.assertEqual(f1.name, 'name')
        self.assertKweli(f1.opt)

        f2 = cons.fields[2]
        self.assertEqual(f2.type, 'stmt')
        self.assertEqual(f2.name, 'body')
        self.assertUongo(f2.opt)
        self.assertKweli(f2.seq)

    eleza test_visitor(self):
        kundi CustomVisitor(self.asdl.VisitorBase):
            eleza __init__(self):
                super().__init__()
                self.names_with_seq = []

            eleza visitModule(self, mod):
                kila dfn kwenye mod.dfns:
                    self.visit(dfn)

            eleza visitType(self, type):
                self.visit(type.value)

            eleza visitSum(self, sum):
                kila t kwenye sum.types:
                    self.visit(t)

            eleza visitConstructor(self, cons):
                kila f kwenye cons.fields:
                    ikiwa f.seq:
                        self.names_with_seq.append(cons.name)

        v = CustomVisitor()
        v.visit(self.types['mod'])
        self.assertEqual(v.names_with_seq,
                         ['Module', 'Module', 'Interactive', 'FunctionType', 'Suite'])


ikiwa __name__ == '__main__':
    unittest.main()
