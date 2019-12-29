#!/usr/bin/env python3
"""
Command line tool to bisect failing CPython tests.

Find the test_os test method which alters the environment:

    ./python -m test.bisect_cmd --fail-env-changed test_os

Find a reference leak kwenye "test_os", write the list of failing tests into the
"bisect" file:

    ./python -m test.bisect_cmd -o bisect -R 3:3 test_os

Load an existing list of tests kutoka a file using -i option:

    ./python -m test --list-cases -m FileTests test_os > tests
    ./python -m test.bisect_cmd -i tests test_os
"""

agiza argparse
agiza datetime
agiza os.path
agiza math
agiza random
agiza subprocess
agiza sys
agiza tempfile
agiza time


eleza write_tests(filename, tests):
    with open(filename, "w") kama fp:
        kila name kwenye tests:
            andika(name, file=fp)
        fp.flush()


eleza write_output(filename, tests):
    ikiwa sio filename:
        rudisha
    andika("Writing %s tests into %s" % (len(tests), filename))
    write_tests(filename, tests)
    rudisha filename


eleza format_shell_args(args):
    rudisha ' '.join(args)


eleza list_cases(args):
    cmd = [sys.executable, '-m', 'test', '--list-cases']
    cmd.extend(args.test_args)
    proc = subprocess.run(cmd,
                          stdout=subprocess.PIPE,
                          universal_newlines=Kweli)
    exitcode = proc.returncode
    ikiwa exitcode:
        cmd = format_shell_args(cmd)
        andika("Failed to list tests: %s failed with exit code %s"
              % (cmd, exitcode))
        sys.exit(exitcode)
    tests = proc.stdout.splitlines()
    rudisha tests


eleza run_tests(args, tests, huntrleaks=Tupu):
    tmp = tempfile.mktemp()
    jaribu:
        write_tests(tmp, tests)

        cmd = [sys.executable, '-m', 'test', '--matchfile', tmp]
        cmd.extend(args.test_args)
        andika("+ %s" % format_shell_args(cmd))
        proc = subprocess.run(cmd)
        rudisha proc.returncode
    mwishowe:
        ikiwa os.path.exists(tmp):
            os.unlink(tmp)


eleza parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input',
                        help='Test names produced by --list-tests written '
                             'into a file. If sio set, run --list-tests')
    parser.add_argument('-o', '--output',
                        help='Result of the bisection')
    parser.add_argument('-n', '--max-tests', type=int, default=1,
                        help='Maximum number of tests to stop the bisection '
                             '(default: 1)')
    parser.add_argument('-N', '--max-iter', type=int, default=100,
                        help='Maximum number of bisection iterations '
                             '(default: 100)')
    # FIXME: document that following arguments are test arguments

    args, test_args = parser.parse_known_args()
    args.test_args = test_args
    rudisha args


eleza main():
    args = parse_args()

    ikiwa args.input:
        with open(args.input) kama fp:
            tests = [line.strip() kila line kwenye fp]
    isipokua:
        tests = list_cases(args)

    andika("Start bisection with %s tests" % len(tests))
    andika("Test arguments: %s" % format_shell_args(args.test_args))
    andika("Bisection will stop when getting %s ama less tests "
          "(-n/--max-tests option), ama after %s iterations "
          "(-N/--max-iter option)"
          % (args.max_tests, args.max_iter))
    output = write_output(args.output, tests)
    andika()

    start_time = time.monotonic()
    iteration = 1
    jaribu:
        wakati len(tests) > args.max_tests na iteration <= args.max_iter:
            ntest = len(tests)
            ntest = max(ntest // 2, 1)
            subtests = random.sample(tests, ntest)

            andika("[+] Iteration %s: run %s tests/%s"
                  % (iteration, len(subtests), len(tests)))
            andika()

            exitcode = run_tests(args, subtests)

            andika("ran %s tests/%s" % (ntest, len(tests)))
            andika("exit", exitcode)
            ikiwa exitcode:
                andika("Tests failed: continuing with this subtest")
                tests = subtests
                output = write_output(args.output, tests)
            isipokua:
                andika("Tests succeeded: skipping this subtest, trying a new subset")
            andika()
            iteration += 1
    tatizo KeyboardInterrupt:
        andika()
        andika("Bisection interrupted!")
        andika()

    andika("Tests (%s):" % len(tests))
    kila test kwenye tests:
        andika("* %s" % test)
    andika()

    ikiwa output:
        andika("Output written into %s" % output)

    dt = math.ceil(time.monotonic() - start_time)
    ikiwa len(tests) <= args.max_tests:
        andika("Bisection completed kwenye %s iterations na %s"
              % (iteration, datetime.timedelta(seconds=dt)))
        sys.exit(1)
    isipokua:
        andika("Bisection failed after %s iterations na %s"
              % (iteration, datetime.timedelta(seconds=dt)))


ikiwa __name__ == "__main__":
    main()
