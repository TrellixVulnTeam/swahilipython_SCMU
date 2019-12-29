'''Test Tools/scripts/fixcid.py.'''

kutoka io agiza StringIO
agiza os, os.path
agiza runpy
agiza sys
kutoka test agiza support
kutoka test.test_tools agiza skip_if_missing, scriptsdir
agiza unittest

skip_if_missing()

kundi Test(unittest.TestCase):
    eleza test_parse_strings(self):
        old1 = 'int xx = "xx\\"xx"[xx];\n'
        old2 = "int xx = 'x\\'xx' + xx;\n"
        output = self.run_script(old1 + old2)
        new1 = 'int yy = "xx\\"xx"[yy];\n'
        new2 = "int yy = 'x\\'xx' + yy;\n"
        self.assertMultiLineEqual(output,
            "1\n"
            "< {old1}"
            "> {new1}"
            "{new1}"
            "2\n"
            "< {old2}"
            "> {new2}"
            "{new2}".format(old1=old1, old2=old2, new1=new1, new2=new2)
        )

    eleza test_alter_comments(self):
        output = self.run_script(
            substfile=
                "xx yy\n"
                "*aa bb\n",
            args=("-c", "-",),
            input=
                "/* xx altered */\n"
                "int xx;\n"
                "/* aa unaltered */\n"
                "int aa;\n",
        )
        self.assertMultiLineEqual(output,
            "1\n"
            "< /* xx altered */\n"
            "> /* yy altered */\n"
            "/* yy altered */\n"
            "2\n"
            "< int xx;\n"
            "> int yy;\n"
            "int yy;\n"
            "/* aa unaltered */\n"
            "4\n"
            "< int aa;\n"
            "> int bb;\n"
            "int bb;\n"
        )

    eleza test_directory(self):
        os.mkdir(support.TESTFN)
        self.addCleanup(support.rmtree, support.TESTFN)
        c_filename = os.path.join(support.TESTFN, "file.c")
        ukijumuisha open(c_filename, "w") kama file:
            file.write("int xx;\n")
        ukijumuisha open(os.path.join(support.TESTFN, "file.py"), "w") kama file:
            file.write("xx = 'unaltered'\n")
        script = os.path.join(scriptsdir, "fixcid.py")
        output = self.run_script(args=(support.TESTFN,))
        self.assertMultiLineEqual(output,
            "{}:\n"
            "1\n"
            '< int xx;\n'
            '> int yy;\n'.format(c_filename)
        )

    eleza run_script(self, input="", *, args=("-",), substfile="xx yy\n"):
        substfilename = support.TESTFN + ".subst"
        ukijumuisha open(substfilename, "w") kama file:
            file.write(substfile)
        self.addCleanup(support.unlink, substfilename)

        argv = ["fixcid.py", "-s", substfilename] + list(args)
        script = os.path.join(scriptsdir, "fixcid.py")
        ukijumuisha support.swap_attr(sys, "argv", argv), \
                support.swap_attr(sys, "stdin", StringIO(input)), \
                support.captured_stdout() kama output, \
                support.captured_stderr():
            jaribu:
                runpy.run_path(script, run_name="__main__")
            tatizo SystemExit kama exit:
                self.assertEqual(exit.code, 0)
        rudisha output.getvalue()
