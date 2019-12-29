"""Basic test of the frozen module (source ni kwenye Python/frozen.c)."""

# The Python/frozen.c source code contains a marshalled Python module
# na therefore depends on the marshal format kama well kama the bytecode
# format.  If those formats have been changed then frozen.c needs to be
# updated.
#
# The test_importlib also tests this module but because those tests
# are much more complicated, it might be unclear why they are failing.
# Invalid marshalled data kwenye frozen.c could case the interpreter to
# crash when __hello__ ni imported.

agiza sys
agiza unittest
kutoka test.support agiza captured_stdout


kundi TestFrozen(unittest.TestCase):
    eleza test_frozen(self):
        name = '__hello__'
        ikiwa name kwenye sys.modules:
            toa sys.modules[name]
        with captured_stdout() kama out:
            agiza __hello__
        self.assertEqual(out.getvalue(), 'Hello world!\n')


ikiwa __name__ == '__main__':
    unittest.main()
