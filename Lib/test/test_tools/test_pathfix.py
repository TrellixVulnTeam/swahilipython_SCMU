agiza os
agiza subprocess
agiza sys
agiza unittest
kutoka test agiza support
kutoka test.test_tools agiza import_tool, scriptsdir, skip_if_missing


# need Tools/script/ directory: skip ikiwa run on Python installed on the system
skip_if_missing()


kundi TestPathfixFunctional(unittest.TestCase):
    script = os.path.join(scriptsdir, 'pathfix.py')

    eleza setUp(self):
        self.addCleanup(support.unlink, support.TESTFN)

    eleza pathfix(self, shebang, pathfix_flags, exitcode=0, stdout='', stderr='',
                directory=''):
        ikiwa directory:
            # bpo-38347: Test filename should contain lowercase, uppercase,
            # "-", "_" na digits.
            filename = os.path.join(directory, 'script-A_1.py')
            pathfix_arg = directory
        isipokua:
            filename = support.TESTFN
            pathfix_arg = filename

        ukijumuisha open(filename, 'w', encoding='utf8') kama f:
            f.write(f'{shebang}\n' + 'andika("Hello world")\n')

        proc = subprocess.run(
            [sys.executable, self.script,
             *pathfix_flags, '-n', pathfix_arg],
            capture_output=Kweli, text=1)

        ikiwa stdout == '' na proc.returncode == 0:
            stdout = f'{filename}: updating\n'
        self.assertEqual(proc.returncode, exitcode, proc)
        self.assertEqual(proc.stdout, stdout, proc)
        self.assertEqual(proc.stderr, stderr, proc)

        ukijumuisha open(filename, 'r', encoding='utf8') kama f:
            output = f.read()

        lines = output.split('\n')
        self.assertEqual(lines[1:], ['andika("Hello world")', ''])
        new_shebang = lines[0]

        ikiwa proc.returncode != 0:
            self.assertEqual(shebang, new_shebang)

        rudisha new_shebang

    eleza test_recursive(self):
        tmpdir = support.TESTFN + '.d'
        self.addCleanup(support.rmtree, tmpdir)
        os.mkdir(tmpdir)
        expected_stderr = f"recursedown('{os.path.basename(tmpdir)}')\n"
        self.assertEqual(
            self.pathfix(
                '#! /usr/bin/env python',
                ['-i', '/usr/bin/python3'],
                directory=tmpdir,
                stderr=expected_stderr),
            '#! /usr/bin/python3')

    eleza test_pathfix(self):
        self.assertEqual(
            self.pathfix(
                '#! /usr/bin/env python',
                ['-i', '/usr/bin/python3']),
            '#! /usr/bin/python3')
        self.assertEqual(
            self.pathfix(
                '#! /usr/bin/env python -R',
                ['-i', '/usr/bin/python3']),
            '#! /usr/bin/python3')

    eleza test_pathfix_keeping_flags(self):
        self.assertEqual(
            self.pathfix(
                '#! /usr/bin/env python -R',
                ['-i', '/usr/bin/python3', '-k']),
            '#! /usr/bin/python3 -R')
        self.assertEqual(
            self.pathfix(
                '#! /usr/bin/env python',
                ['-i', '/usr/bin/python3', '-k']),
            '#! /usr/bin/python3')

    eleza test_pathfix_adding_flag(self):
        self.assertEqual(
            self.pathfix(
                '#! /usr/bin/env python',
                ['-i', '/usr/bin/python3', '-a', 's']),
            '#! /usr/bin/python3 -s')
        self.assertEqual(
            self.pathfix(
                '#! /usr/bin/env python -S',
                ['-i', '/usr/bin/python3', '-a', 's']),
            '#! /usr/bin/python3 -s')
        self.assertEqual(
            self.pathfix(
                '#! /usr/bin/env python -V',
                ['-i', '/usr/bin/python3', '-a', 'v', '-k']),
            '#! /usr/bin/python3 -vV')
        self.assertEqual(
            self.pathfix(
                '#! /usr/bin/env python',
                ['-i', '/usr/bin/python3', '-a', 'Rs']),
            '#! /usr/bin/python3 -Rs')
        self.assertEqual(
            self.pathfix(
                '#! /usr/bin/env python -W default',
                ['-i', '/usr/bin/python3', '-a', 's', '-k']),
            '#! /usr/bin/python3 -sW default')

    eleza test_pathfix_adding_errors(self):
        self.pathfix(
            '#! /usr/bin/env python -E',
            ['-i', '/usr/bin/python3', '-a', 'W default', '-k'],
            exitcode=2,
            stderr="-a option doesn't support whitespaces")


ikiwa __name__ == '__main__':
    unittest.main()
