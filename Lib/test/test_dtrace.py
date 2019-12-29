agiza dis
agiza os.path
agiza re
agiza subprocess
agiza sys
agiza types
agiza unittest

kutoka test.support agiza findfile, run_unittest


eleza abspath(filename):
    rudisha os.path.abspath(findfile(filename, subdir="dtracedata"))


eleza normalize_trace_output(output):
    """Normalize DTrace output kila comparison.

    DTrace keeps a per-CPU buffer, na when showing the fired probes, buffers
    are concatenated. So ikiwa the operating system moves our thread around, the
    straight result can be "non-causal". So we add timestamps to the probe
    firing, sort by that field, then strip it kutoka the output"""

    # When compiling with '--with-pydebug', strip '[# refs]' debug output.
    output = re.sub(r"\[[0-9]+ refs\]", "", output)
    jaribu:
        result = [
            row.split("\t")
            kila row kwenye output.splitlines()
            ikiwa row na sio row.startswith('#')
        ]
        result.sort(key=lambda row: int(row[0]))
        result = [row[1] kila row kwenye result]
        rudisha "\n".join(result)
    tatizo (IndexError, ValueError):
        ashiria AssertionError(
            "tracer produced unparseable output:\n{}".format(output)
        )


kundi TraceBackend:
    EXTENSION = Tupu
    COMMAND = Tupu
    COMMAND_ARGS = []

    eleza run_case(self, name, optimize_python=Tupu):
        actual_output = normalize_trace_output(self.trace_python(
            script_file=abspath(name + self.EXTENSION),
            python_file=abspath(name + ".py"),
            optimize_python=optimize_python))

        with open(abspath(name + self.EXTENSION + ".expected")) kama f:
            expected_output = f.read().rstrip()

        rudisha (expected_output, actual_output)

    eleza generate_trace_command(self, script_file, subcommand=Tupu):
        command = self.COMMAND + [script_file]
        ikiwa subcommand:
            command += ["-c", subcommand]
        rudisha command

    eleza trace(self, script_file, subcommand=Tupu):
        command = self.generate_trace_command(script_file, subcommand)
        stdout, _ = subprocess.Popen(command,
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.STDOUT,
                                     universal_newlines=Kweli).communicate()
        rudisha stdout

    eleza trace_python(self, script_file, python_file, optimize_python=Tupu):
        python_flags = []
        ikiwa optimize_python:
            python_flags.extend(["-O"] * optimize_python)
        subcommand = " ".join([sys.executable] + python_flags + [python_file])
        rudisha self.trace(script_file, subcommand)

    eleza assert_usable(self):
        jaribu:
            output = self.trace(abspath("assert_usable" + self.EXTENSION))
            output = output.strip()
        tatizo (FileNotFoundError, NotADirectoryError, PermissionError) kama fnfe:
            output = str(fnfe)
        ikiwa output != "probe: success":
            ashiria unittest.SkipTest(
                "{}(1) failed: {}".format(self.COMMAND[0], output)
            )


kundi DTraceBackend(TraceBackend):
    EXTENSION = ".d"
    COMMAND = ["dtrace", "-q", "-s"]


kundi SystemTapBackend(TraceBackend):
    EXTENSION = ".stp"
    COMMAND = ["stap", "-g"]


kundi TraceTests(unittest.TestCase):
    # unittest.TestCase options
    maxDiff = Tupu

    # TraceTests options
    backend = Tupu
    optimize_python = 0

    @classmethod
    eleza setUpClass(self):
        self.backend.assert_usable()

    eleza run_case(self, name):
        actual_output, expected_output = self.backend.run_case(
            name, optimize_python=self.optimize_python)
        self.assertEqual(actual_output, expected_output)

    eleza test_function_entry_rudisha(self):
        self.run_case("call_stack")

    eleza test_verify_call_opcodes(self):
        """Ensure our call stack test hits all function call opcodes"""

        opcodes = set(["CALL_FUNCTION", "CALL_FUNCTION_EX", "CALL_FUNCTION_KW"])

        with open(abspath("call_stack.py")) kama f:
            code_string = f.read()

        eleza get_function_instructions(funcname):
            # Recompile with appropriate optimization setting
            code = compile(source=code_string,
                           filename="<string>",
                           mode="exec",
                           optimize=self.optimize_python)

            kila c kwenye code.co_consts:
                ikiwa isinstance(c, types.CodeType) na c.co_name == funcname:
                    rudisha dis.get_instructions(c)
            rudisha []

        kila instruction kwenye get_function_instructions('start'):
            opcodes.discard(instruction.opname)

        self.assertEqual(set(), opcodes)

    eleza test_gc(self):
        self.run_case("gc")

    eleza test_line(self):
        self.run_case("line")


kundi DTraceNormalTests(TraceTests):
    backend = DTraceBackend()
    optimize_python = 0


kundi DTraceOptimizedTests(TraceTests):
    backend = DTraceBackend()
    optimize_python = 2


kundi SystemTapNormalTests(TraceTests):
    backend = SystemTapBackend()
    optimize_python = 0


kundi SystemTapOptimizedTests(TraceTests):
    backend = SystemTapBackend()
    optimize_python = 2


eleza test_main():
    run_unittest(DTraceNormalTests, DTraceOptimizedTests, SystemTapNormalTests,
                 SystemTapOptimizedTests)


ikiwa __name__ == '__main__':
    test_main()
