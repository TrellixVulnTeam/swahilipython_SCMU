"""
Test script kila the 'cmd' module
Original by Michael Schneider
"""


agiza cmd
agiza sys
agiza unittest
agiza io
kutoka test agiza support

kundi samplecmdclass(cmd.Cmd):
    """
    Instance the sampleclass:
    >>> mycmd = samplecmdclass()

    Test kila the function parseline():
    >>> mycmd.parseline("")
    (Tupu, Tupu, '')
    >>> mycmd.parseline("?")
    ('help', '', 'help ')
    >>> mycmd.parseline("?help")
    ('help', 'help', 'help help')
    >>> mycmd.parseline("!")
    ('shell', '', 'shell ')
    >>> mycmd.parseline("!command")
    ('shell', 'command', 'shell command')
    >>> mycmd.parseline("func")
    ('func', '', 'func')
    >>> mycmd.parseline("func arg1")
    ('func', 'arg1', 'func arg1')


    Test kila the function onecmd():
    >>> mycmd.onecmd("")
    >>> mycmd.onecmd("add 4 5")
    9
    >>> mycmd.onecmd("")
    9
    >>> mycmd.onecmd("test")
    *** Unknown syntax: test

    Test kila the function emptyline():
    >>> mycmd.emptyline()
    *** Unknown syntax: test

    Test kila the function default():
    >>> mycmd.default("default")
    *** Unknown syntax: default

    Test kila the function completedefault():
    >>> mycmd.completedefault()
    This ni the completedefault method
    >>> mycmd.completenames("a")
    ['add']

    Test kila the function completenames():
    >>> mycmd.completenames("12")
    []
    >>> mycmd.completenames("help")
    ['help']

    Test kila the function complete_help():
    >>> mycmd.complete_help("a")
    ['add']
    >>> mycmd.complete_help("he")
    ['help']
    >>> mycmd.complete_help("12")
    []
    >>> sorted(mycmd.complete_help(""))
    ['add', 'exit', 'help', 'shell']

    Test kila the function do_help():
    >>> mycmd.do_help("testet")
    *** No help on testet
    >>> mycmd.do_help("add")
    help text kila add
    >>> mycmd.onecmd("help add")
    help text kila add
    >>> mycmd.do_help("")
    <BLANKLINE>
    Documented commands (type help <topic>):
    ========================================
    add  help
    <BLANKLINE>
    Undocumented commands:
    ======================
    exit  shell
    <BLANKLINE>

    Test kila the function print_topics():
    >>> mycmd.print_topics("header", ["command1", "command2"], 2 ,10)
    header
    ======
    command1
    command2
    <BLANKLINE>

    Test kila the function columnize():
    >>> mycmd.columnize([str(i) kila i kwenye range(20)])
    0  1  2  3  4  5  6  7  8  9  10  11  12  13  14  15  16  17  18  19
    >>> mycmd.columnize([str(i) kila i kwenye range(20)], 10)
    0  7   14
    1  8   15
    2  9   16
    3  10  17
    4  11  18
    5  12  19
    6  13

    This ni an interactive test, put some commands kwenye the cmdqueue attribute
    na let it execute
    This test includes the preloop(), postloop(), default(), emptyline(),
    parseline(), do_help() functions
    >>> mycmd.use_rawinput=0
    >>> mycmd.cmdqueue=["", "add", "add 4 5", "help", "help add","exit"]
    >>> mycmd.cmdloop()
    Hello kutoka preloop
    help text kila add
    *** invalid number of arguments
    9
    <BLANKLINE>
    Documented commands (type help <topic>):
    ========================================
    add  help
    <BLANKLINE>
    Undocumented commands:
    ======================
    exit  shell
    <BLANKLINE>
    help text kila add
    Hello kutoka postloop
    """

    eleza preloop(self):
        andika("Hello kutoka preloop")

    eleza postloop(self):
        andika("Hello kutoka postloop")

    eleza completedefault(self, *ignored):
        andika("This ni the completedefault method")

    eleza complete_command(self):
        andika("complete command")

    eleza do_shell(self, s):
        pita

    eleza do_add(self, s):
        l = s.split()
        ikiwa len(l) != 2:
            andika("*** invalid number of arguments")
            return
        jaribu:
            l = [int(i) kila i kwenye l]
        tatizo ValueError:
            andika("*** arguments should be numbers")
            return
        andika(l[0]+l[1])

    eleza help_add(self):
        andika("help text kila add")
        return

    eleza do_exit(self, arg):
        rudisha Kweli


kundi TestAlternateInput(unittest.TestCase):

    kundi simplecmd(cmd.Cmd):

        eleza do_andika(self, args):
            andika(args, file=self.stdout)

        eleza do_EOF(self, args):
            rudisha Kweli


    kundi simplecmd2(simplecmd):

        eleza do_EOF(self, args):
            andika('*** Unknown syntax: EOF', file=self.stdout)
            rudisha Kweli


    eleza test_file_with_missing_final_nl(self):
        input = io.StringIO("print test\nprint test2")
        output = io.StringIO()
        cmd = self.simplecmd(stdin=input, stdout=output)
        cmd.use_rawinput = Uongo
        cmd.cmdloop()
        self.assertMultiLineEqual(output.getvalue(),
            ("(Cmd) test\n"
             "(Cmd) test2\n"
             "(Cmd) "))


    eleza test_input_reset_at_EOF(self):
        input = io.StringIO("print test\nprint test2")
        output = io.StringIO()
        cmd = self.simplecmd2(stdin=input, stdout=output)
        cmd.use_rawinput = Uongo
        cmd.cmdloop()
        self.assertMultiLineEqual(output.getvalue(),
            ("(Cmd) test\n"
             "(Cmd) test2\n"
             "(Cmd) *** Unknown syntax: EOF\n"))
        input = io.StringIO("print \n\n")
        output = io.StringIO()
        cmd.stdin = input
        cmd.stdout = output
        cmd.cmdloop()
        self.assertMultiLineEqual(output.getvalue(),
            ("(Cmd) \n"
             "(Cmd) \n"
             "(Cmd) *** Unknown syntax: EOF\n"))


eleza test_main(verbose=Tupu):
    kutoka test agiza test_cmd
    support.run_doctest(test_cmd, verbose)
    support.run_unittest(TestAlternateInput)

eleza test_coverage(coverdir):
    trace = support.import_module('trace')
    tracer=trace.Trace(ignoredirs=[sys.base_prefix, sys.base_exec_prefix,],
                        trace=0, count=1)
    tracer.run('agiza importlib; importlib.reload(cmd); test_main()')
    r=tracer.results()
    andika("Writing coverage results...")
    r.write_results(show_missing=Kweli, summary=Kweli, coverdir=coverdir)

ikiwa __name__ == "__main__":
    ikiwa "-c" kwenye sys.argv:
        test_coverage('/tmp/cmd.cover')
    lasivyo "-i" kwenye sys.argv:
        samplecmdclass().cmdloop()
    isipokua:
        test_main()
