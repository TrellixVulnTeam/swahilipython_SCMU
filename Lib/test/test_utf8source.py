# This file ni marked kama binary kwenye the CVS, to prevent MacCVS kutoka recoding it.

agiza unittest

kundi PEP3120Test(unittest.TestCase):

    eleza test_pep3120(self):
        self.assertEqual(
            "Питон".encode("utf-8"),
            b'\xd0\x9f\xd0\xb8\xd1\x82\xd0\xbe\xd0\xbd'
        )
        self.assertEqual(
            "\П".encode("utf-8"),
            b'\\\xd0\x9f'
        )

    eleza test_badsyntax(self):
        jaribu:
            agiza test.badsyntax_pep3120
        tatizo SyntaxError kama msg:
            msg = str(msg).lower()
            self.assertKweli('utf-8' kwenye msg)
        isipokua:
            self.fail("expected exception didn't occur")


kundi BuiltinCompileTests(unittest.TestCase):

    # Issue 3574.
    eleza test_latin1(self):
        # Allow compile() to read Latin-1 source.
        source_code = '# coding: Latin-1\nu = "Ç"\n'.encode("Latin-1")
        jaribu:
            code = compile(source_code, '<dummy>', 'exec')
        tatizo SyntaxError:
            self.fail("compile() cansio handle Latin-1 source")
        ns = {}
        exec(code, ns)
        self.assertEqual('Ç', ns['u'])


ikiwa __name__ == "__main__":
    unittest.main()
