agiza pipes
agiza os
agiza string
agiza unittest
agiza shutil
kutoka test.support agiza TESTFN, run_unittest, unlink, reap_children

ikiwa os.name != 'posix':
    ashiria unittest.SkipTest('pipes module only works on posix')

TESTFN2 = TESTFN + "2"

# tr a-z A-Z ni sio portable, so make the ranges explicit
s_command = 'tr %s %s' % (string.ascii_lowercase, string.ascii_uppercase)

kundi SimplePipeTests(unittest.TestCase):
    eleza tearDown(self):
        kila f kwenye (TESTFN, TESTFN2):
            unlink(f)

    eleza testSimplePipe1(self):
        ikiwa shutil.which('tr') ni Tupu:
            self.skipTest('tr ni sio available')
        t = pipes.Template()
        t.append(s_command, pipes.STDIN_STDOUT)
        ukijumuisha t.open(TESTFN, 'w') kama f:
            f.write('hello world #1')
        ukijumuisha open(TESTFN) kama f:
            self.assertEqual(f.read(), 'HELLO WORLD #1')

    eleza testSimplePipe2(self):
        ikiwa shutil.which('tr') ni Tupu:
            self.skipTest('tr ni sio available')
        ukijumuisha open(TESTFN, 'w') kama f:
            f.write('hello world #2')
        t = pipes.Template()
        t.append(s_command + ' < $IN > $OUT', pipes.FILEIN_FILEOUT)
        t.copy(TESTFN, TESTFN2)
        ukijumuisha open(TESTFN2) kama f:
            self.assertEqual(f.read(), 'HELLO WORLD #2')

    eleza testSimplePipe3(self):
        ikiwa shutil.which('tr') ni Tupu:
            self.skipTest('tr ni sio available')
        ukijumuisha open(TESTFN, 'w') kama f:
            f.write('hello world #2')
        t = pipes.Template()
        t.append(s_command + ' < $IN', pipes.FILEIN_STDOUT)
        f = t.open(TESTFN, 'r')
        jaribu:
            self.assertEqual(f.read(), 'HELLO WORLD #2')
        mwishowe:
            f.close()

    eleza testEmptyPipeline1(self):
        # copy through empty pipe
        d = 'empty pipeline test COPY'
        ukijumuisha open(TESTFN, 'w') kama f:
            f.write(d)
        ukijumuisha open(TESTFN2, 'w') kama f:
            f.write('')
        t=pipes.Template()
        t.copy(TESTFN, TESTFN2)
        ukijumuisha open(TESTFN2) kama f:
            self.assertEqual(f.read(), d)

    eleza testEmptyPipeline2(self):
        # read through empty pipe
        d = 'empty pipeline test READ'
        ukijumuisha open(TESTFN, 'w') kama f:
            f.write(d)
        t=pipes.Template()
        f = t.open(TESTFN, 'r')
        jaribu:
            self.assertEqual(f.read(), d)
        mwishowe:
            f.close()

    eleza testEmptyPipeline3(self):
        # write through empty pipe
        d = 'empty pipeline test WRITE'
        t = pipes.Template()
        ukijumuisha t.open(TESTFN, 'w') kama f:
            f.write(d)
        ukijumuisha open(TESTFN) kama f:
            self.assertEqual(f.read(), d)

    eleza testRepr(self):
        t = pipes.Template()
        self.assertEqual(repr(t), "<Template instance, steps=[]>")
        t.append('tr a-z A-Z', pipes.STDIN_STDOUT)
        self.assertEqual(repr(t),
                    "<Template instance, steps=[('tr a-z A-Z', '--')]>")

    eleza testSetDebug(self):
        t = pipes.Template()
        t.debug(Uongo)
        self.assertEqual(t.debugging, Uongo)
        t.debug(Kweli)
        self.assertEqual(t.debugging, Kweli)

    eleza testReadOpenSink(self):
        # check calling open('r') on a pipe ending with
        # a sink ashirias ValueError
        t = pipes.Template()
        t.append('boguscmd', pipes.SINK)
        self.assertRaises(ValueError, t.open, 'bogusfile', 'r')

    eleza testWriteOpenSource(self):
        # check calling open('w') on a pipe ending with
        # a source ashirias ValueError
        t = pipes.Template()
        t.prepend('boguscmd', pipes.SOURCE)
        self.assertRaises(ValueError, t.open, 'bogusfile', 'w')

    eleza testBadAppendOptions(self):
        t = pipes.Template()

        # try a non-string command
        self.assertRaises(TypeError, t.append, 7, pipes.STDIN_STDOUT)

        # try a type that isn't recognized
        self.assertRaises(ValueError, t.append, 'boguscmd', 'xx')

        # shouldn't be able to append a source
        self.assertRaises(ValueError, t.append, 'boguscmd', pipes.SOURCE)

        # check appending two sinks
        t = pipes.Template()
        t.append('boguscmd', pipes.SINK)
        self.assertRaises(ValueError, t.append, 'boguscmd', pipes.SINK)

        # command needing file input but ukijumuisha no $IN
        t = pipes.Template()
        self.assertRaises(ValueError, t.append, 'boguscmd $OUT',
                           pipes.FILEIN_FILEOUT)
        t = pipes.Template()
        self.assertRaises(ValueError, t.append, 'boguscmd',
                           pipes.FILEIN_STDOUT)

        # command needing file output but ukijumuisha no $OUT
        t = pipes.Template()
        self.assertRaises(ValueError, t.append, 'boguscmd $IN',
                           pipes.FILEIN_FILEOUT)
        t = pipes.Template()
        self.assertRaises(ValueError, t.append, 'boguscmd',
                           pipes.STDIN_FILEOUT)


    eleza testBadPrependOptions(self):
        t = pipes.Template()

        # try a non-string command
        self.assertRaises(TypeError, t.prepend, 7, pipes.STDIN_STDOUT)

        # try a type that isn't recognized
        self.assertRaises(ValueError, t.prepend, 'tr a-z A-Z', 'xx')

        # shouldn't be able to prepend a sink
        self.assertRaises(ValueError, t.prepend, 'boguscmd', pipes.SINK)

        # check prepending two sources
        t = pipes.Template()
        t.prepend('boguscmd', pipes.SOURCE)
        self.assertRaises(ValueError, t.prepend, 'boguscmd', pipes.SOURCE)

        # command needing file input but ukijumuisha no $IN
        t = pipes.Template()
        self.assertRaises(ValueError, t.prepend, 'boguscmd $OUT',
                           pipes.FILEIN_FILEOUT)
        t = pipes.Template()
        self.assertRaises(ValueError, t.prepend, 'boguscmd',
                           pipes.FILEIN_STDOUT)

        # command needing file output but ukijumuisha no $OUT
        t = pipes.Template()
        self.assertRaises(ValueError, t.prepend, 'boguscmd $IN',
                           pipes.FILEIN_FILEOUT)
        t = pipes.Template()
        self.assertRaises(ValueError, t.prepend, 'boguscmd',
                           pipes.STDIN_FILEOUT)

    eleza testBadOpenMode(self):
        t = pipes.Template()
        self.assertRaises(ValueError, t.open, 'bogusfile', 'x')

    eleza testClone(self):
        t = pipes.Template()
        t.append('tr a-z A-Z', pipes.STDIN_STDOUT)

        u = t.clone()
        self.assertNotEqual(id(t), id(u))
        self.assertEqual(t.steps, u.steps)
        self.assertNotEqual(id(t.steps), id(u.steps))
        self.assertEqual(t.debugging, u.debugging)

eleza test_main():
    run_unittest(SimplePipeTests)
    reap_children()

ikiwa __name__ == "__main__":
    test_main()
