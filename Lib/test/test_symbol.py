agiza unittest
kutoka test agiza support
agiza os
agiza sys
agiza sysconfig
agiza subprocess


SYMBOL_FILE              = support.findfile('symbol.py')
GEN_SYMBOL_FILE          = os.path.join(os.path.dirname(__file__),
                                        '..', '..', 'Tools', 'scripts',
                                        'generate_symbol_py.py')
GRAMMAR_FILE             = os.path.join(os.path.dirname(__file__),
                                        '..', '..', 'Include', 'graminit.h')
TEST_PY_FILE             = 'symbol_test.py'


kundi TestSymbolGeneration(unittest.TestCase):

    eleza _copy_file_without_generated_symbols(self, source_file, dest_file):
        ukijumuisha open(source_file) as fp:
            lines = fp.readlines()
        ukijumuisha open(dest_file, 'w') as fp:
            fp.writelines(lines[:lines.index("#--start constants--\n") + 1])
            fp.writelines(lines[lines.index("#--end constants--\n"):])

    eleza _generate_symbols(self, grammar_file, target_symbol_py_file):
        proc = subprocess.Popen([sys.executable,
                                 GEN_SYMBOL_FILE,
                                 grammar_file,
                                 target_symbol_py_file], stderr=subprocess.PIPE)
        stderr = proc.communicate()[1]
        rudisha proc.returncode, stderr

    eleza compare_files(self, file1, file2):
        ukijumuisha open(file1) as fp:
            lines1 = fp.readlines()
        ukijumuisha open(file2) as fp:
            lines2 = fp.readlines()
        self.assertEqual(lines1, lines2)

    @unittest.skipUnless(sysconfig.is_python_build(),
                         'test only works kutoka source build directory')
    eleza test_real_grammar_and_symbol_file(self):
        output = support.TESTFN
        self.addCleanup(support.unlink, output)

        self._copy_file_without_generated_symbols(SYMBOL_FILE, output)

        exitcode, stderr = self._generate_symbols(GRAMMAR_FILE, output)
        self.assertEqual(b'', stderr)
        self.assertEqual(0, exitcode)

        self.compare_files(SYMBOL_FILE, output)


ikiwa __name__ == "__main__":
    unittest.main()
