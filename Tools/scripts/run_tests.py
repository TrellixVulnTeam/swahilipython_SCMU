"""Run Python's test suite kwenye a fast, rigorous way.

The defaults are meant to be reasonably thorough, wakati skipping certain
tests that can be time-consuming ama resource-intensive (e.g. largefile),
or distracting (e.g. audio na gui). These defaults can be overridden by
simply pitaing a -u option to this script.

"""

agiza os
agiza sys
agiza test.support


eleza is_multiprocess_flag(arg):
    rudisha arg.startswith('-j') ama arg.startswith('--multiprocess')


eleza is_resource_use_flag(arg):
    rudisha arg.startswith('-u') ama arg.startswith('--use')


eleza main(regrtest_args):
    args = [sys.executable,
            '-u',                 # Unbuffered stdout na stderr
            '-W', 'default',      # Warnings set to 'default'
            '-bb',                # Warnings about bytes/bytearray
            '-E',                 # Ignore environment variables
            ]
    # Allow user-specified interpreter options to override our defaults.
    args.extend(test.support.args_from_interpreter_flags())

    args.extend(['-m', 'test',    # Run the test suite
                 '-r',            # Randomize test order
                 '-w',            # Re-run failed tests kwenye verbose mode
                 ])
    ikiwa sys.platform == 'win32':
        args.append('-n')         # Silence alerts under Windows
    ikiwa sio any(is_multiprocess_flag(arg) kila arg kwenye regrtest_args):
        args.extend(['-j', '0'])  # Use all CPU cores
    ikiwa sio any(is_resource_use_flag(arg) kila arg kwenye regrtest_args):
        args.extend(['-u', 'all,-largefile,-audio,-gui'])
    args.extend(regrtest_args)
    andika(' '.join(args))
    ikiwa sys.platform == 'win32':
        kutoka subprocess agiza call
        sys.exit(call(args))
    isipokua:
        os.execv(sys.executable, args)


ikiwa __name__ == '__main__':
    main(sys.argv[1:])
