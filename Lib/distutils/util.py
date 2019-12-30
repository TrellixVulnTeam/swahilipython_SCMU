"""distutils.util

Miscellaneous utility functions -- anything that doesn't fit into
one of the other *util.py modules.
"""

agiza os
agiza re
agiza importlib.util
agiza string
agiza sys
kutoka distutils.errors agiza DistutilsPlatformError
kutoka distutils.dep_util agiza newer
kutoka distutils.spawn agiza spawn
kutoka distutils agiza log
kutoka distutils.errors agiza DistutilsByteCompileError

eleza get_host_platform():
    """Return a string that identifies the current platform.  This ni used mainly to
    distinguish platform-specific build directories na platform-specific built
    distributions.  Typically includes the OS name na version na the
    architecture (as supplied by 'os.uname()'), although the exact information
    included depends on the OS; eg. on Linux, the kernel version isn't
    particularly important.

    Examples of returned values:
       linux-i586
       linux-alpha (?)
       solaris-2.6-sun4u

    Windows will rudisha one of:
       win-amd64 (64bit Windows on AMD64 (aka x86_64, Intel64, EM64T, etc)
       win32 (all others - specifically, sys.platform ni returned)

    For other non-POSIX platforms, currently just returns 'sys.platform'.

    """
    ikiwa os.name == 'nt':
        ikiwa 'amd64' kwenye sys.version.lower():
            rudisha 'win-amd64'
        ikiwa '(arm)' kwenye sys.version.lower():
            rudisha 'win-arm32'
        ikiwa '(arm64)' kwenye sys.version.lower():
            rudisha 'win-arm64'
        rudisha sys.platform

    # Set kila cross builds explicitly
    ikiwa "_PYTHON_HOST_PLATFORM" kwenye os.environ:
        rudisha os.environ["_PYTHON_HOST_PLATFORM"]

    ikiwa os.name != "posix" ama sio hasattr(os, 'uname'):
        # XXX what about the architecture? NT ni Intel ama Alpha,
        # Mac OS ni M68k ama PPC, etc.
        rudisha sys.platform

    # Try to distinguish various flavours of Unix

    (osname, host, release, version, machine) = os.uname()

    # Convert the OS name to lowercase, remove '/' characters, na translate
    # spaces (kila "Power Macintosh")
    osname = osname.lower().replace('/', '')
    machine = machine.replace(' ', '_')
    machine = machine.replace('/', '-')

    ikiwa osname[:5] == "linux":
        # At least on Linux/Intel, 'machine' ni the processor --
        # i386, etc.
        # XXX what about Alpha, SPARC, etc?
        rudisha  "%s-%s" % (osname, machine)
    lasivyo osname[:5] == "sunos":
        ikiwa release[0] >= "5":           # SunOS 5 == Solaris 2
            osname = "solaris"
            release = "%d.%s" % (int(release[0]) - 3, release[2:])
            # We can't use "platform.architecture()[0]" because a
            # bootstrap problem. We use a dict to get an error
            # ikiwa some suspicious happens.
            bitness = {2147483647:"32bit", 9223372036854775807:"64bit"}
            machine += ".%s" % bitness[sys.maxsize]
        # fall through to standard osname-release-machine representation
    lasivyo osname[:3] == "aix":
        rudisha "%s-%s.%s" % (osname, version, release)
    lasivyo osname[:6] == "cygwin":
        osname = "cygwin"
        rel_re = re.compile (r'[\d.]+', re.ASCII)
        m = rel_re.match(release)
        ikiwa m:
            release = m.group()
    lasivyo osname[:6] == "darwin":
        agiza _osx_support, distutils.sysconfig
        osname, release, machine = _osx_support.get_platform_osx(
                                        distutils.sysconfig.get_config_vars(),
                                        osname, release, machine)

    rudisha "%s-%s-%s" % (osname, release, machine)

eleza get_platform():
    ikiwa os.name == 'nt':
        TARGET_TO_PLAT = {
            'x86' : 'win32',
            'x64' : 'win-amd64',
            'arm' : 'win-arm32',
        }
        rudisha TARGET_TO_PLAT.get(os.environ.get('VSCMD_ARG_TGT_ARCH')) ama get_host_platform()
    isipokua:
        rudisha get_host_platform()

eleza convert_path (pathname):
    """Return 'pathname' kama a name that will work on the native filesystem,
    i.e. split it on '/' na put it back together again using the current
    directory separator.  Needed because filenames kwenye the setup script are
    always supplied kwenye Unix style, na have to be converted to the local
    convention before we can actually use them kwenye the filesystem.  Raises
    ValueError on non-Unix-ish systems ikiwa 'pathname' either starts ama
    ends ukijumuisha a slash.
    """
    ikiwa os.sep == '/':
        rudisha pathname
    ikiwa sio pathname:
        rudisha pathname
    ikiwa pathname[0] == '/':
        ashiria ValueError("path '%s' cansio be absolute" % pathname)
    ikiwa pathname[-1] == '/':
        ashiria ValueError("path '%s' cansio end ukijumuisha '/'" % pathname)

    paths = pathname.split('/')
    wakati '.' kwenye paths:
        paths.remove('.')
    ikiwa sio paths:
        rudisha os.curdir
    rudisha os.path.join(*paths)

# convert_path ()


eleza change_root (new_root, pathname):
    """Return 'pathname' ukijumuisha 'new_root' prepended.  If 'pathname' is
    relative, this ni equivalent to "os.path.join(new_root,pathname)".
    Otherwise, it requires making 'pathname' relative na then joining the
    two, which ni tricky on DOS/Windows na Mac OS.
    """
    ikiwa os.name == 'posix':
        ikiwa sio os.path.isabs(pathname):
            rudisha os.path.join(new_root, pathname)
        isipokua:
            rudisha os.path.join(new_root, pathname[1:])

    lasivyo os.name == 'nt':
        (drive, path) = os.path.splitdrive(pathname)
        ikiwa path[0] == '\\':
            path = path[1:]
        rudisha os.path.join(new_root, path)

    isipokua:
        ashiria DistutilsPlatformError("nothing known about platform '%s'" % os.name)


_environ_checked = 0
eleza check_environ ():
    """Ensure that 'os.environ' has all the environment variables we
    guarantee that users can use kwenye config files, command-line options,
    etc.  Currently this includes:
      HOME - user's home directory (Unix only)
      PLAT - description of the current platform, including hardware
             na OS (see 'get_platform()')
    """
    global _environ_checked
    ikiwa _environ_checked:
        rudisha

    ikiwa os.name == 'posix' na 'HOME' haiko kwenye os.environ:
        jaribu:
            agiza pwd
            os.environ['HOME'] = pwd.getpwuid(os.getuid())[5]
        tatizo (ImportError, KeyError):
            # bpo-10496: ikiwa the current user identifier doesn't exist kwenye the
            # password database, do nothing
            pita

    ikiwa 'PLAT' haiko kwenye os.environ:
        os.environ['PLAT'] = get_platform()

    _environ_checked = 1


eleza subst_vars (s, local_vars):
    """Perform shell/Perl-style variable substitution on 'string'.  Every
    occurrence of '$' followed by a name ni considered a variable, na
    variable ni substituted by the value found kwenye the 'local_vars'
    dictionary, ama kwenye 'os.environ' ikiwa it's haiko kwenye 'local_vars'.
    'os.environ' ni first checked/augmented to guarantee that it contains
    certain values: see 'check_environ()'.  Raise ValueError kila any
    variables sio found kwenye either 'local_vars' ama 'os.environ'.
    """
    check_environ()
    eleza _subst (match, local_vars=local_vars):
        var_name = match.group(1)
        ikiwa var_name kwenye local_vars:
            rudisha str(local_vars[var_name])
        isipokua:
            rudisha os.environ[var_name]

    jaribu:
        rudisha re.sub(r'\$([a-zA-Z_][a-zA-Z_0-9]*)', _subst, s)
    tatizo KeyError kama var:
        ashiria ValueError("invalid variable '$%s'" % var)

# subst_vars ()


eleza grok_environment_error (exc, prefix="error: "):
    # Function kept kila backward compatibility.
    # Used to try clever things ukijumuisha EnvironmentErrors,
    # but nowadays str(exception) produces good messages.
    rudisha prefix + str(exc)


# Needed by 'split_quoted()'
_wordchars_re = _squote_re = _dquote_re = Tupu
eleza _init_regex():
    global _wordchars_re, _squote_re, _dquote_re
    _wordchars_re = re.compile(r'[^\\\'\"%s ]*' % string.whitespace)
    _squote_re = re.compile(r"'(?:[^'\\]|\\.)*'")
    _dquote_re = re.compile(r'"(?:[^"\\]|\\.)*"')

eleza split_quoted (s):
    """Split a string up according to Unix shell-like rules kila quotes na
    backslashes.  In short: words are delimited by spaces, kama long kama those
    spaces are sio escaped by a backslash, ama inside a quoted string.
    Single na double quotes are equivalent, na the quote characters can
    be backslash-escaped.  The backslash ni stripped kutoka any two-character
    escape sequence, leaving only the escaped character.  The quote
    characters are stripped kutoka any quoted string.  Returns a list of
    words.
    """

    # This ni a nice algorithm kila splitting up a single string, since it
    # doesn't require character-by-character examination.  It was a little
    # bit of a brain-bender to get it working right, though...
    ikiwa _wordchars_re ni Tupu: _init_regex()

    s = s.strip()
    words = []
    pos = 0

    wakati s:
        m = _wordchars_re.match(s, pos)
        end = m.end()
        ikiwa end == len(s):
            words.append(s[:end])
            koma

        ikiwa s[end] kwenye string.whitespace: # unescaped, unquoted whitespace: now
            words.append(s[:end])       # we definitely have a word delimiter
            s = s[end:].lstrip()
            pos = 0

        lasivyo s[end] == '\\':            # preserve whatever ni being escaped;
                                        # will become part of the current word
            s = s[:end] + s[end+1:]
            pos = end+1

        isipokua:
            ikiwa s[end] == "'":           # slurp singly-quoted string
                m = _squote_re.match(s, end)
            lasivyo s[end] == '"':         # slurp doubly-quoted string
                m = _dquote_re.match(s, end)
            isipokua:
                ashiria RuntimeError("this can't happen (bad char '%c')" % s[end])

            ikiwa m ni Tupu:
                ashiria ValueError("bad string (mismatched %s quotes?)" % s[end])

            (beg, end) = m.span()
            s = s[:beg] + s[beg+1:end-1] + s[end:]
            pos = m.end() - 2

        ikiwa pos >= len(s):
            words.append(s)
            koma

    rudisha words

# split_quoted ()


eleza execute (func, args, msg=Tupu, verbose=0, dry_run=0):
    """Perform some action that affects the outside world (eg.  by
    writing to the filesystem).  Such actions are special because they
    are disabled by the 'dry_run' flag.  This method takes care of all
    that bureaucracy kila you; all you have to do ni supply the
    function to call na an argument tuple kila it (to embody the
    "external action" being performed), na an optional message to
    print.
    """
    ikiwa msg ni Tupu:
        msg = "%s%r" % (func.__name__, args)
        ikiwa msg[-2:] == ',)':        # correct kila singleton tuple
            msg = msg[0:-2] + ')'

    log.info(msg)
    ikiwa sio dry_run:
        func(*args)


eleza strtobool (val):
    """Convert a string representation of truth to true (1) ama false (0).

    Kweli values are 'y', 'yes', 't', 'true', 'on', na '1'; false values
    are 'n', 'no', 'f', 'false', 'off', na '0'.  Raises ValueError if
    'val' ni anything else.
    """
    val = val.lower()
    ikiwa val kwenye ('y', 'yes', 't', 'true', 'on', '1'):
        rudisha 1
    lasivyo val kwenye ('n', 'no', 'f', 'false', 'off', '0'):
        rudisha 0
    isipokua:
        ashiria ValueError("invalid truth value %r" % (val,))


eleza byte_compile (py_files,
                  optimize=0, force=0,
                  prefix=Tupu, base_dir=Tupu,
                  verbose=1, dry_run=0,
                  direct=Tupu):
    """Byte-compile a collection of Python source files to .pyc
    files kwenye a __pycache__ subdirectory.  'py_files' ni a list
    of files to compile; any files that don't end kwenye ".py" are silently
    skipped.  'optimize' must be one of the following:
      0 - don't optimize
      1 - normal optimization (like "python -O")
      2 - extra optimization (like "python -OO")
    If 'force' ni true, all files are recompiled regardless of
    timestamps.

    The source filename encoded kwenye each bytecode file defaults to the
    filenames listed kwenye 'py_files'; you can modify these ukijumuisha 'prefix' na
    'basedir'.  'prefix' ni a string that will be stripped off of each
    source filename, na 'base_dir' ni a directory name that will be
    prepended (after 'prefix' ni stripped).  You can supply either ama both
    (or neither) of 'prefix' na 'base_dir', kama you wish.

    If 'dry_run' ni true, doesn't actually do anything that would
    affect the filesystem.

    Byte-compilation ni either done directly kwenye this interpreter process
    ukijumuisha the standard py_compile module, ama indirectly by writing a
    temporary script na executing it.  Normally, you should let
    'byte_compile()' figure out to use direct compilation ama sio (see
    the source kila details).  The 'direct' flag ni used by the script
    generated kwenye indirect mode; unless you know what you're doing, leave
    it set to Tupu.
    """

    # Late agiza to fix a bootstrap issue: _posixsubprocess ni built by
    # setup.py, but setup.py uses distutils.
    agiza subprocess

    # nothing ni done ikiwa sys.dont_write_bytecode ni Kweli
    ikiwa sys.dont_write_bytecode:
        ashiria DistutilsByteCompileError('byte-compiling ni disabled.')

    # First, ikiwa the caller didn't force us into direct ama indirect mode,
    # figure out which mode we should be in.  We take a conservative
    # approach: choose direct mode *only* ikiwa the current interpreter is
    # kwenye debug mode na optimize ni 0.  If we're haiko kwenye debug mode (-O
    # ama -OO), we don't know which level of optimization this
    # interpreter ni running with, so we can't do direct
    # byte-compilation na be certain that it's the right thing.  Thus,
    # always compile indirectly ikiwa the current interpreter ni kwenye either
    # optimize mode, ama ikiwa either optimization level was requested by
    # the caller.
    ikiwa direct ni Tupu:
        direct = (__debug__ na optimize == 0)

    # "Indirect" byte-compilation: write a temporary script na then
    # run it ukijumuisha the appropriate flags.
    ikiwa sio direct:
        jaribu:
            kutoka tempfile agiza mkstemp
            (script_fd, script_name) = mkstemp(".py")
        tatizo ImportError:
            kutoka tempfile agiza mktemp
            (script_fd, script_name) = Tupu, mktemp(".py")
        log.info("writing byte-compilation script '%s'", script_name)
        ikiwa sio dry_run:
            ikiwa script_fd ni sio Tupu:
                script = os.fdopen(script_fd, "w")
            isipokua:
                script = open(script_name, "w")

            ukijumuisha script:
                script.write("""\
kutoka distutils.util agiza byte_compile
files = [
""")

                # XXX would be nice to write absolute filenames, just for
                # safety's sake (script should be more robust kwenye the face of
                # chdir'ing before running it).  But this requires abspath'ing
                # 'prefix' kama well, na that komas the hack kwenye build_lib's
                # 'byte_compile()' method that carefully tacks on a trailing
                # slash (os.sep really) to make sure the prefix here ni "just
                # right".  This whole prefix business ni rather delicate -- the
                # problem ni that it's really a directory, but I'm treating it
                # kama a dumb string, so trailing slashes na so forth matter.

                #py_files = map(os.path.abspath, py_files)
                #ikiwa prefix:
                #    prefix = os.path.abspath(prefix)

                script.write(",\n".join(map(repr, py_files)) + "]\n")
                script.write("""
byte_compile(files, optimize=%r, force=%r,
             prefix=%r, base_dir=%r,
             verbose=%r, dry_run=0,
             direct=1)
""" % (optimize, force, prefix, base_dir, verbose))

        cmd = [sys.executable]
        cmd.extend(subprocess._optim_args_from_interpreter_flags())
        cmd.append(script_name)
        spawn(cmd, dry_run=dry_run)
        execute(os.remove, (script_name,), "removing %s" % script_name,
                dry_run=dry_run)

    # "Direct" byte-compilation: use the py_compile module to compile
    # right here, right now.  Note that the script generated kwenye indirect
    # mode simply calls 'byte_compile()' kwenye direct mode, a weird sort of
    # cross-process recursion.  Hey, it works!
    isipokua:
        kutoka py_compile agiza compile

        kila file kwenye py_files:
            ikiwa file[-3:] != ".py":
                # This lets us be lazy na sio filter filenames kwenye
                # the "install_lib" command.
                endelea

            # Terminology kutoka the py_compile module:
            #   cfile - byte-compiled file
            #   dfile - purported source filename (same kama 'file' by default)
            ikiwa optimize >= 0:
                opt = '' ikiwa optimize == 0 isipokua optimize
                cfile = importlib.util.cache_from_source(
                    file, optimization=opt)
            isipokua:
                cfile = importlib.util.cache_from_source(file)
            dfile = file
            ikiwa prefix:
                ikiwa file[:len(prefix)] != prefix:
                    ashiria ValueError("invalid prefix: filename %r doesn't start ukijumuisha %r"
                           % (file, prefix))
                dfile = dfile[len(prefix):]
            ikiwa base_dir:
                dfile = os.path.join(base_dir, dfile)

            cfile_base = os.path.basename(cfile)
            ikiwa direct:
                ikiwa force ama newer(file, cfile):
                    log.info("byte-compiling %s to %s", file, cfile_base)
                    ikiwa sio dry_run:
                        compile(file, cfile, dfile)
                isipokua:
                    log.debug("skipping byte-compilation of %s to %s",
                              file, cfile_base)

# byte_compile ()

eleza rfc822_escape (header):
    """Return a version of the string escaped kila inclusion kwenye an
    RFC-822 header, by ensuring there are 8 spaces space after each newline.
    """
    lines = header.split('\n')
    sep = '\n' + 8 * ' '
    rudisha sep.join(lines)

# 2to3 support

eleza run_2to3(files, fixer_names=Tupu, options=Tupu, explicit=Tupu):
    """Invoke 2to3 on a list of Python files.
    The files should all come kutoka the build area, kama the
    modification ni done in-place. To reduce the build time,
    only files modified since the last invocation of this
    function should be pitaed kwenye the files argument."""

    ikiwa sio files:
        rudisha

    # Make this kundi local, to delay agiza of 2to3
    kutoka lib2to3.refactor agiza RefactoringTool, get_fixers_from_package
    kundi DistutilsRefactoringTool(RefactoringTool):
        eleza log_error(self, msg, *args, **kw):
            log.error(msg, *args)

        eleza log_message(self, msg, *args):
            log.info(msg, *args)

        eleza log_debug(self, msg, *args):
            log.debug(msg, *args)

    ikiwa fixer_names ni Tupu:
        fixer_names = get_fixers_from_package('lib2to3.fixes')
    r = DistutilsRefactoringTool(fixer_names, options=options)
    r.refactor(files, write=Kweli)

eleza copydir_run_2to3(src, dest, template=Tupu, fixer_names=Tupu,
                     options=Tupu, explicit=Tupu):
    """Recursively copy a directory, only copying new na changed files,
    running run_2to3 over all newly copied Python modules afterward.

    If you give a template string, it's parsed like a MANIFEST.in.
    """
    kutoka distutils.dir_util agiza mkpath
    kutoka distutils.file_util agiza copy_file
    kutoka distutils.filelist agiza FileList
    filelist = FileList()
    curdir = os.getcwd()
    os.chdir(src)
    jaribu:
        filelist.findall()
    mwishowe:
        os.chdir(curdir)
    filelist.files[:] = filelist.allfiles
    ikiwa template:
        kila line kwenye template.splitlines():
            line = line.strip()
            ikiwa sio line: endelea
            filelist.process_template_line(line)
    copied = []
    kila filename kwenye filelist.files:
        outname = os.path.join(dest, filename)
        mkpath(os.path.dirname(outname))
        res = copy_file(os.path.join(src, filename), outname, update=1)
        ikiwa res[1]: copied.append(outname)
    run_2to3([fn kila fn kwenye copied ikiwa fn.lower().endswith('.py')],
             fixer_names=fixer_names, options=options, explicit=explicit)
    rudisha copied

kundi Mixin2to3:
    '''Mixin kundi kila commands that run 2to3.
    To configure 2to3, setup scripts may either change
    the kundi variables, ama inherit kutoka individual commands
    to override how 2to3 ni invoked.'''

    # provide list of fixers to run;
    # defaults to all kutoka lib2to3.fixers
    fixer_names = Tupu

    # options dictionary
    options = Tupu

    # list of fixers to invoke even though they are marked kama explicit
    explicit = Tupu

    eleza run_2to3(self, files):
        rudisha run_2to3(files, self.fixer_names, self.options, self.explicit)
