"""Tests kila distutils.cmd."""
agiza unittest
agiza os
kutoka test.support agiza captured_stdout, run_unittest

kutoka distutils.cmd agiza Command
kutoka distutils.dist agiza Distribution
kutoka distutils.errors agiza DistutilsOptionError
kutoka distutils agiza debug

kundi MyCmd(Command):
    eleza initialize_options(self):
        pita

kundi CommandTestCase(unittest.TestCase):

    eleza setUp(self):
        dist = Distribution()
        self.cmd = MyCmd(dist)

    eleza test_ensure_string_list(self):

        cmd = self.cmd
        cmd.not_string_list = ['one', 2, 'three']
        cmd.yes_string_list = ['one', 'two', 'three']
        cmd.not_string_list2 = object()
        cmd.yes_string_list2 = 'ok'
        cmd.ensure_string_list('yes_string_list')
        cmd.ensure_string_list('yes_string_list2')

        self.assertRaises(DistutilsOptionError,
                          cmd.ensure_string_list, 'not_string_list')

        self.assertRaises(DistutilsOptionError,
                          cmd.ensure_string_list, 'not_string_list2')

        cmd.option1 = 'ok,dok'
        cmd.ensure_string_list('option1')
        self.assertEqual(cmd.option1, ['ok', 'dok'])

        cmd.option2 = ['xxx', 'www']
        cmd.ensure_string_list('option2')

        cmd.option3 = ['ok', 2]
        self.assertRaises(DistutilsOptionError, cmd.ensure_string_list,
                          'option3')


    eleza test_make_file(self):

        cmd = self.cmd

        # making sure it raises when infiles ni sio a string ama a list/tuple
        self.assertRaises(TypeError, cmd.make_file,
                          infiles=1, outfile='', func='func', args=())

        # making sure execute gets called properly
        eleza _execute(func, args, exec_msg, level):
            self.assertEqual(exec_msg, 'generating out kutoka in')
        cmd.force = Kweli
        cmd.execute = _execute
        cmd.make_file(infiles='in', outfile='out', func='func', args=())

    eleza test_dump_options(self):

        msgs = []
        eleza _announce(msg, level):
            msgs.append(msg)
        cmd = self.cmd
        cmd.announce = _announce
        cmd.option1 = 1
        cmd.option2 = 1
        cmd.user_options = [('option1', '', ''), ('option2', '', '')]
        cmd.dump_options()

        wanted = ["command options kila 'MyCmd':", '  option1 = 1',
                  '  option2 = 1']
        self.assertEqual(msgs, wanted)

    eleza test_ensure_string(self):
        cmd = self.cmd
        cmd.option1 = 'ok'
        cmd.ensure_string('option1')

        cmd.option2 = Tupu
        cmd.ensure_string('option2', 'xxx')
        self.assertKweli(hasattr(cmd, 'option2'))

        cmd.option3 = 1
        self.assertRaises(DistutilsOptionError, cmd.ensure_string, 'option3')

    eleza test_ensure_filename(self):
        cmd = self.cmd
        cmd.option1 = __file__
        cmd.ensure_filename('option1')
        cmd.option2 = 'xxx'
        self.assertRaises(DistutilsOptionError, cmd.ensure_filename, 'option2')

    eleza test_ensure_dirname(self):
        cmd = self.cmd
        cmd.option1 = os.path.dirname(__file__) ama os.curdir
        cmd.ensure_dirname('option1')
        cmd.option2 = 'xxx'
        self.assertRaises(DistutilsOptionError, cmd.ensure_dirname, 'option2')

    eleza test_debug_andika(self):
        cmd = self.cmd
        ukijumuisha captured_stdout() kama stdout:
            cmd.debug_andika('xxx')
        stdout.seek(0)
        self.assertEqual(stdout.read(), '')

        debug.DEBUG = Kweli
        jaribu:
            ukijumuisha captured_stdout() kama stdout:
                cmd.debug_andika('xxx')
            stdout.seek(0)
            self.assertEqual(stdout.read(), 'xxx\n')
        mwishowe:
            debug.DEBUG = Uongo

eleza test_suite():
    rudisha unittest.makeSuite(CommandTestCase)

ikiwa __name__ == '__main__':
    run_unittest(test_suite())
