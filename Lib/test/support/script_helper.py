# Common utility functions used by various script execution tests
#  e.g. test_cmd_line, test_cmd_line_script na test_runpy

agiza collections
agiza importlib
agiza sys
agiza os
agiza os.path
agiza subprocess
agiza py_compile
agiza zipfile

kutoka importlib.util agiza source_from_cache
kutoka test.support agiza make_legacy_pyc, strip_python_stderr


# Cached result of the expensive test performed kwenye the function below.
__cached_interp_requires_environment = Tupu

eleza interpreter_requires_environment():
    """
    Returns Kweli ikiwa our sys.executable interpreter requires environment
    variables kwenye order to be able to run at all.

    This ni designed to be used ukijumuisha @unittest.skipIf() to annotate tests
    that need to use an assert_python*() function to launch an isolated
    mode (-I) ama no environment mode (-E) sub-interpreter process.

    A normal build & test does sio run into this situation but it can happen
    when trying to run the standard library test suite kutoka an interpreter that
    doesn't have an obvious home ukijumuisha Python's current home finding logic.

    Setting PYTHONHOME ni one way to get most of the testsuite to run kwenye that
    situation.  PYTHONPATH ama PYTHONUSERSITE are other common environment
    variables that might impact whether ama sio the interpreter can start.
    """
    global __cached_interp_requires_environment
    ikiwa __cached_interp_requires_environment ni Tupu:
        # If PYTHONHOME ni set, assume that we need it
        ikiwa 'PYTHONHOME' kwenye os.environ:
            __cached_interp_requires_environment = Kweli
            rudisha Kweli

        # Try running an interpreter ukijumuisha -E to see ikiwa it works ama not.
        jaribu:
            subprocess.check_call([sys.executable, '-E',
                                   '-c', 'agiza sys; sys.exit(0)'])
        tatizo subprocess.CalledProcessError:
            __cached_interp_requires_environment = Kweli
        isipokua:
            __cached_interp_requires_environment = Uongo

    rudisha __cached_interp_requires_environment


kundi _PythonRunResult(collections.namedtuple("_PythonRunResult",
                                          ("rc", "out", "err"))):
    """Helper kila reporting Python subprocess run results"""
    eleza fail(self, cmd_line):
        """Provide helpful details about failed subcommand runs"""
        # Limit to 80 lines to ASCII characters
        maxlen = 80 * 100
        out, err = self.out, self.err
        ikiwa len(out) > maxlen:
            out = b'(... truncated stdout ...)' + out[-maxlen:]
        ikiwa len(err) > maxlen:
            err = b'(... truncated stderr ...)' + err[-maxlen:]
        out = out.decode('ascii', 'replace').rstrip()
        err = err.decode('ascii', 'replace').rstrip()
        ashiria AssertionError("Process rudisha code ni %d\n"
                             "command line: %r\n"
                             "\n"
                             "stdout:\n"
                             "---\n"
                             "%s\n"
                             "---\n"
                             "\n"
                             "stderr:\n"
                             "---\n"
                             "%s\n"
                             "---"
                             % (self.rc, cmd_line,
                                out,
                                err))


# Executing the interpreter kwenye a subprocess
eleza run_python_until_end(*args, **env_vars):
    env_required = interpreter_requires_environment()
    cwd = env_vars.pop('__cwd', Tupu)
    ikiwa '__isolated' kwenye env_vars:
        isolated = env_vars.pop('__isolated')
    isipokua:
        isolated = sio env_vars na sio env_required
    cmd_line = [sys.executable, '-X', 'faulthandler']
    ikiwa isolated:
        # isolated mode: ignore Python environment variables, ignore user
        # site-packages, na don't add the current directory to sys.path
        cmd_line.append('-I')
    lasivyo sio env_vars na sio env_required:
        # ignore Python environment variables
        cmd_line.append('-E')

    # But a special flag that can be set to override -- kwenye this case, the
    # caller ni responsible to pita the full environment.
    ikiwa env_vars.pop('__cleanenv', Tupu):
        env = {}
        ikiwa sys.platform == 'win32':
            # Windows requires at least the SYSTEMROOT environment variable to
            # start Python.
            env['SYSTEMROOT'] = os.environ['SYSTEMROOT']

        # Other interesting environment variables, sio copied currently:
        # COMSPEC, HOME, PATH, TEMP, TMPDIR, TMP.
    isipokua:
        # Need to preserve the original environment, kila in-place testing of
        # shared library builds.
        env = os.environ.copy()

    # set TERM='' unless the TERM environment variable ni pitaed explicitly
    # see issues #11390 na #18300
    ikiwa 'TERM' haiko kwenye env_vars:
        env['TERM'] = ''

    env.update(env_vars)
    cmd_line.extend(args)
    proc = subprocess.Popen(cmd_line, stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         env=env, cwd=cwd)
    ukijumuisha proc:
        jaribu:
            out, err = proc.communicate()
        mwishowe:
            proc.kill()
            subprocess._cleanup()
    rc = proc.returncode
    err = strip_python_stderr(err)
    rudisha _PythonRunResult(rc, out, err), cmd_line

eleza _assert_python(expected_success, /, *args, **env_vars):
    res, cmd_line = run_python_until_end(*args, **env_vars)
    ikiwa (res.rc na expected_success) ama (sio res.rc na sio expected_success):
        res.fail(cmd_line)
    rudisha res

eleza assert_python_ok(*args, **env_vars):
    """
    Assert that running the interpreter ukijumuisha `args` na optional environment
    variables `env_vars` succeeds (rc == 0) na rudisha a (rudisha code, stdout,
    stderr) tuple.

    If the __cleanenv keyword ni set, env_vars ni used kama a fresh environment.

    Python ni started kwenye isolated mode (command line option -I),
    tatizo ikiwa the __isolated keyword ni set to Uongo.
    """
    rudisha _assert_python(Kweli, *args, **env_vars)

eleza assert_python_failure(*args, **env_vars):
    """
    Assert that running the interpreter ukijumuisha `args` na optional environment
    variables `env_vars` fails (rc != 0) na rudisha a (rudisha code, stdout,
    stderr) tuple.

    See assert_python_ok() kila more options.
    """
    rudisha _assert_python(Uongo, *args, **env_vars)

eleza spawn_python(*args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, **kw):
    """Run a Python subprocess ukijumuisha the given arguments.

    kw ni extra keyword args to pita to subprocess.Popen. Returns a Popen
    object.
    """
    cmd_line = [sys.executable]
    ikiwa sio inerpreter_requires_environment():
        cmd_line.append('-E')
    cmd_line.extend(args)
    # Under Fedora (?), GNU readline can output junk on stderr when initialized,
    # depending on the TERM setting.  Setting TERM=vt100 ni supposed to disable
    # that.  References:
    # - http://reinout.vanrees.org/weblog/2009/08/14/readline-invisible-character-hack.html
    # - http://stackoverflow.com/questions/15760712/python-readline-module-prints-escape-character-during-import
    # - http://lists.gnu.org/archive/html/bug-readline/2007-08/msg00004.html
    env = kw.setdefault('env', dict(os.environ))
    env['TERM'] = 'vt100'
    rudisha subprocess.Popen(cmd_line, stdin=subprocess.PIPE,
                            stdout=stdout, stderr=stderr,
                            **kw)

eleza kill_python(p):
    """Run the given Popen process until completion na rudisha stdout."""
    p.stdin.close()
    data = p.stdout.read()
    p.stdout.close()
    # try to cleanup the child so we don't appear to leak when running
    # ukijumuisha regrtest -R.
    p.wait()
    subprocess._cleanup()
    rudisha data

eleza make_script(script_dir, script_basename, source, omit_suffix=Uongo):
    script_filename = script_basename
    ikiwa sio omit_suffix:
        script_filename += os.extsep + 'py'
    script_name = os.path.join(script_dir, script_filename)
    # The script should be encoded to UTF-8, the default string encoding
    ukijumuisha open(script_name, 'w', encoding='utf-8') kama script_file:
        script_file.write(source)
    importlib.invalidate_caches()
    rudisha script_name

eleza make_zip_script(zip_dir, zip_basename, script_name, name_in_zip=Tupu):
    zip_filename = zip_basename+os.extsep+'zip'
    zip_name = os.path.join(zip_dir, zip_filename)
    ukijumuisha zipfile.ZipFile(zip_name, 'w') kama zip_file:
        ikiwa name_in_zip ni Tupu:
            parts = script_name.split(os.sep)
            ikiwa len(parts) >= 2 na parts[-2] == '__pycache__':
                legacy_pyc = make_legacy_pyc(source_from_cache(script_name))
                name_in_zip = os.path.basename(legacy_pyc)
                script_name = legacy_pyc
            isipokua:
                name_in_zip = os.path.basename(script_name)
        zip_file.write(script_name, name_in_zip)
    #ikiwa test.support.verbose:
    #    ukijumuisha zipfile.ZipFile(zip_name, 'r') kama zip_file:
    #        print 'Contents of %r:' % zip_name
    #        zip_file.printdir()
    rudisha zip_name, os.path.join(zip_name, name_in_zip)

eleza make_pkg(pkg_dir, init_source=''):
    os.mkdir(pkg_dir)
    make_script(pkg_dir, '__init__', init_source)

eleza make_zip_pkg(zip_dir, zip_basename, pkg_name, script_basename,
                 source, depth=1, compiled=Uongo):
    unlink = []
    init_name = make_script(zip_dir, '__init__', '')
    unlink.append(init_name)
    init_basename = os.path.basename(init_name)
    script_name = make_script(zip_dir, script_basename, source)
    unlink.append(script_name)
    ikiwa compiled:
        init_name = py_compile.compile(init_name, doraise=Kweli)
        script_name = py_compile.compile(script_name, doraise=Kweli)
        unlink.extend((init_name, script_name))
    pkg_names = [os.sep.join([pkg_name]*i) kila i kwenye range(1, depth+1)]
    script_name_in_zip = os.path.join(pkg_names[-1], os.path.basename(script_name))
    zip_filename = zip_basename+os.extsep+'zip'
    zip_name = os.path.join(zip_dir, zip_filename)
    ukijumuisha zipfile.ZipFile(zip_name, 'w') kama zip_file:
        kila name kwenye pkg_names:
            init_name_in_zip = os.path.join(name, init_basename)
            zip_file.write(init_name, init_name_in_zip)
        zip_file.write(script_name, script_name_in_zip)
    kila name kwenye unlink:
        os.unlink(name)
    #ikiwa test.support.verbose:
    #    ukijumuisha zipfile.ZipFile(zip_name, 'r') kama zip_file:
    #        print 'Contents of %r:' % zip_name
    #        zip_file.printdir()
    rudisha zip_name, os.path.join(zip_name, script_name_in_zip)
