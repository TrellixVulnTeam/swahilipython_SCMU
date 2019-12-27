"""Append module search paths for third-party packages to sys.path.

****************************************************************
* This module is automatically imported during initialization. *
****************************************************************

This will append site-specific paths to the module search path.  On
Unix (including Mac OSX), it starts with sys.prefix and
sys.exec_prefix (ikiwa different) and appends
lib/python<version>/site-packages.
On other platforms (such as Windows), it tries each of the
prefixes directly, as well as with lib/site-packages appended.  The
resulting directories, ikiwa they exist, are appended to sys.path, and
also inspected for path configuration files.

If a file named "pyvenv.cfg" exists one directory above sys.executable,
sys.prefix and sys.exec_prefix are set to that directory and
it is also checked for site-packages (sys.base_prefix and
sys.base_exec_prefix will always be the "real" prefixes of the Python
installation). If "pyvenv.cfg" (a bootstrap configuration file) contains
the key "include-system-site-packages" set to anything other than "false"
(case-insensitive), the system-level prefixes will still also be
searched for site-packages; otherwise they won't.

All of the resulting site-specific directories, ikiwa they exist, are
appended to sys.path, and also inspected for path configuration
files.

A path configuration file is a file whose name has the form
<package>.pth; its contents are additional directories (one per line)
to be added to sys.path.  Non-existing directories (or
non-directories) are never added to sys.path; no directory is added to
sys.path more than once.  Blank lines and lines beginning with
'#' are skipped. Lines starting with 'agiza' are executed.

For example, suppose sys.prefix and sys.exec_prefix are set to
/usr/local and there is a directory /usr/local/lib/python2.5/site-packages
with three subdirectories, foo, bar and spam, and two path
configuration files, foo.pth and bar.pth.  Assume foo.pth contains the
following:

  # foo package configuration
  foo
  bar
  bletch

and bar.pth contains:

  # bar package configuration
  bar

Then the following directories are added to sys.path, in this order:

  /usr/local/lib/python2.5/site-packages/bar
  /usr/local/lib/python2.5/site-packages/foo

Note that bletch is omitted because it doesn't exist; bar precedes foo
because bar.pth comes alphabetically before foo.pth; and spam is
omitted because it is not mentioned in either path configuration file.

The readline module is also automatically configured to enable
completion for systems that support it.  This can be overridden in
sitecustomize, usercustomize or PYTHONSTARTUP.  Starting Python in
isolated mode (-I) disables automatic readline configuration.

After these operations, an attempt is made to agiza a module
named sitecustomize, which can perform arbitrary additional
site-specific customizations.  If this agiza fails with an
ImportError exception, it is silently ignored.
"""

agiza sys
agiza os
agiza builtins
agiza _sitebuiltins
agiza io

# Prefixes for site-packages; add additional prefixes like /usr/local here
PREFIXES = [sys.prefix, sys.exec_prefix]
# Enable per user site-packages directory
# set it to False to disable the feature or True to force the feature
ENABLE_USER_SITE = None

# for distutils.commands.install
# These values are initialized by the getuserbase() and getusersitepackages()
# functions, through the main() function when Python starts.
USER_SITE = None
USER_BASE = None


eleza makepath(*paths):
    dir = os.path.join(*paths)
    try:
        dir = os.path.abspath(dir)
    except OSError:
        pass
    rudisha dir, os.path.normcase(dir)


eleza abs_paths():
    """Set all module __file__ and __cached__ attributes to an absolute path"""
    for m in set(sys.modules.values()):
        ikiwa (getattr(getattr(m, '__loader__', None), '__module__', None) not in
                ('_frozen_importlib', '_frozen_importlib_external')):
            continue   # don't mess with a PEP 302-supplied __file__
        try:
            m.__file__ = os.path.abspath(m.__file__)
        except (AttributeError, OSError, TypeError):
            pass
        try:
            m.__cached__ = os.path.abspath(m.__cached__)
        except (AttributeError, OSError, TypeError):
            pass


eleza removeduppaths():
    """ Remove duplicate entries kutoka sys.path along with making them
    absolute"""
    # This ensures that the initial path provided by the interpreter contains
    # only absolute pathnames, even ikiwa we're running kutoka the build directory.
    L = []
    known_paths = set()
    for dir in sys.path:
        # Filter out duplicate paths (on case-insensitive file systems also
        # ikiwa they only differ in case); turn relative paths into absolute
        # paths.
        dir, dircase = makepath(dir)
        ikiwa dircase not in known_paths:
            L.append(dir)
            known_paths.add(dircase)
    sys.path[:] = L
    rudisha known_paths


eleza _init_pathinfo():
    """Return a set containing all existing file system items kutoka sys.path."""
    d = set()
    for item in sys.path:
        try:
            ikiwa os.path.exists(item):
                _, itemcase = makepath(item)
                d.add(itemcase)
        except TypeError:
            continue
    rudisha d


eleza addpackage(sitedir, name, known_paths):
    """Process a .pth file within the site-packages directory:
       For each line in the file, either combine it with sitedir to a path
       and add that to known_paths, or execute it ikiwa it starts with 'agiza '.
    """
    ikiwa known_paths is None:
        known_paths = _init_pathinfo()
        reset = True
    else:
        reset = False
    fullname = os.path.join(sitedir, name)
    try:
        f = io.TextIOWrapper(io.open_code(fullname))
    except OSError:
        return
    with f:
        for n, line in enumerate(f):
            ikiwa line.startswith("#"):
                continue
            try:
                ikiwa line.startswith(("agiza ", "agiza\t")):
                    exec(line)
                    continue
                line = line.rstrip()
                dir, dircase = makepath(sitedir, line)
                ikiwa not dircase in known_paths and os.path.exists(dir):
                    sys.path.append(dir)
                    known_paths.add(dircase)
            except Exception:
                andika("Error processing line {:d} of {}:\n".format(n+1, fullname),
                      file=sys.stderr)
                agiza traceback
                for record in traceback.format_exception(*sys.exc_info()):
                    for line in record.splitlines():
                        andika('  '+line, file=sys.stderr)
                andika("\nRemainder of file ignored", file=sys.stderr)
                break
    ikiwa reset:
        known_paths = None
    rudisha known_paths


eleza addsitedir(sitedir, known_paths=None):
    """Add 'sitedir' argument to sys.path ikiwa missing and handle .pth files in
    'sitedir'"""
    ikiwa known_paths is None:
        known_paths = _init_pathinfo()
        reset = True
    else:
        reset = False
    sitedir, sitedircase = makepath(sitedir)
    ikiwa not sitedircase in known_paths:
        sys.path.append(sitedir)        # Add path component
        known_paths.add(sitedircase)
    try:
        names = os.listdir(sitedir)
    except OSError:
        return
    names = [name for name in names ikiwa name.endswith(".pth")]
    for name in sorted(names):
        addpackage(sitedir, name, known_paths)
    ikiwa reset:
        known_paths = None
    rudisha known_paths


eleza check_enableusersite():
    """Check ikiwa user site directory is safe for inclusion

    The function tests for the command line flag (including environment var),
    process uid/gid equal to effective uid/gid.

    None: Disabled for security reasons
    False: Disabled by user (command line option)
    True: Safe and enabled
    """
    ikiwa sys.flags.no_user_site:
        rudisha False

    ikiwa hasattr(os, "getuid") and hasattr(os, "geteuid"):
        # check process uid == effective uid
        ikiwa os.geteuid() != os.getuid():
            rudisha None
    ikiwa hasattr(os, "getgid") and hasattr(os, "getegid"):
        # check process gid == effective gid
        ikiwa os.getegid() != os.getgid():
            rudisha None

    rudisha True


# NOTE: sysconfig and it's dependencies are relatively large but site module
# needs very limited part of them.
# To speedup startup time, we have copy of them.
#
# See https://bugs.python.org/issue29585

# Copy of sysconfig._getuserbase()
eleza _getuserbase():
    env_base = os.environ.get("PYTHONUSERBASE", None)
    ikiwa env_base:
        rudisha env_base

    eleza joinuser(*args):
        rudisha os.path.expanduser(os.path.join(*args))

    ikiwa os.name == "nt":
        base = os.environ.get("APPDATA") or "~"
        rudisha joinuser(base, "Python")

    ikiwa sys.platform == "darwin" and sys._framework:
        rudisha joinuser("~", "Library", sys._framework,
                        "%d.%d" % sys.version_info[:2])

    rudisha joinuser("~", ".local")


# Same to sysconfig.get_path('purelib', os.name+'_user')
eleza _get_path(userbase):
    version = sys.version_info

    ikiwa os.name == 'nt':
        rudisha f'{userbase}\\Python{version[0]}{version[1]}\\site-packages'

    ikiwa sys.platform == 'darwin' and sys._framework:
        rudisha f'{userbase}/lib/python/site-packages'

    rudisha f'{userbase}/lib/python{version[0]}.{version[1]}/site-packages'


eleza getuserbase():
    """Returns the `user base` directory path.

    The `user base` directory can be used to store data. If the global
    variable ``USER_BASE`` is not initialized yet, this function will also set
    it.
    """
    global USER_BASE
    ikiwa USER_BASE is None:
        USER_BASE = _getuserbase()
    rudisha USER_BASE


eleza getusersitepackages():
    """Returns the user-specific site-packages directory path.

    If the global variable ``USER_SITE`` is not initialized yet, this
    function will also set it.
    """
    global USER_SITE
    userbase = getuserbase() # this will also set USER_BASE

    ikiwa USER_SITE is None:
        USER_SITE = _get_path(userbase)

    rudisha USER_SITE

eleza addusersitepackages(known_paths):
    """Add a per user site-package to sys.path

    Each user has its own python directory with site-packages in the
    home directory.
    """
    # get the per user site-package path
    # this call will also make sure USER_BASE and USER_SITE are set
    user_site = getusersitepackages()

    ikiwa ENABLE_USER_SITE and os.path.isdir(user_site):
        addsitedir(user_site, known_paths)
    rudisha known_paths

eleza getsitepackages(prefixes=None):
    """Returns a list containing all global site-packages directories.

    For each directory present in ``prefixes`` (or the global ``PREFIXES``),
    this function will find its `site-packages` subdirectory depending on the
    system environment, and will rudisha a list of full paths.
    """
    sitepackages = []
    seen = set()

    ikiwa prefixes is None:
        prefixes = PREFIXES

    for prefix in prefixes:
        ikiwa not prefix or prefix in seen:
            continue
        seen.add(prefix)

        ikiwa os.sep == '/':
            sitepackages.append(os.path.join(prefix, "lib",
                                        "python%d.%d" % sys.version_info[:2],
                                        "site-packages"))
        else:
            sitepackages.append(prefix)
            sitepackages.append(os.path.join(prefix, "lib", "site-packages"))
    rudisha sitepackages

eleza addsitepackages(known_paths, prefixes=None):
    """Add site-packages to sys.path"""
    for sitedir in getsitepackages(prefixes):
        ikiwa os.path.isdir(sitedir):
            addsitedir(sitedir, known_paths)

    rudisha known_paths

eleza setquit():
    """Define new builtins 'quit' and 'exit'.

    These are objects which make the interpreter exit when called.
    The repr of each object contains a hint at how it works.

    """
    ikiwa os.sep == '\\':
        eof = 'Ctrl-Z plus Return'
    else:
        eof = 'Ctrl-D (i.e. EOF)'

    builtins.quit = _sitebuiltins.Quitter('quit', eof)
    builtins.exit = _sitebuiltins.Quitter('exit', eof)


eleza setcopyright():
    """Set 'copyright' and 'credits' in builtins"""
    builtins.copyright = _sitebuiltins._Printer("copyright", sys.copyright)
    ikiwa sys.platform[:4] == 'java':
        builtins.credits = _sitebuiltins._Printer(
            "credits",
            "Jython is maintained by the Jython developers (www.jython.org).")
    else:
        builtins.credits = _sitebuiltins._Printer("credits", """\
    Thanks to CWI, CNRI, BeOpen.com, Zope Corporation and a cast of thousands
    for supporting Python development.  See www.python.org for more information.""")
    files, dirs = [], []
    # Not all modules are required to have a __file__ attribute.  See
    # PEP 420 for more details.
    ikiwa hasattr(os, '__file__'):
        here = os.path.dirname(os.__file__)
        files.extend(["LICENSE.txt", "LICENSE"])
        dirs.extend([os.path.join(here, os.pardir), here, os.curdir])
    builtins.license = _sitebuiltins._Printer(
        "license",
        "See https://www.python.org/psf/license/",
        files, dirs)


eleza sethelper():
    builtins.help = _sitebuiltins._Helper()

eleza enablerlcompleter():
    """Enable default readline configuration on interactive prompts, by
    registering a sys.__interactivehook__.

    If the readline module can be imported, the hook will set the Tab key
    as completion key and register ~/.python_history as history file.
    This can be overridden in the sitecustomize or usercustomize module,
    or in a PYTHONSTARTUP file.
    """
    eleza register_readline():
        agiza atexit
        try:
            agiza readline
            agiza rlcompleter
        except ImportError:
            return

        # Reading the initialization (config) file may not be enough to set a
        # completion key, so we set one first and then read the file.
        readline_doc = getattr(readline, '__doc__', '')
        ikiwa readline_doc is not None and 'libedit' in readline_doc:
            readline.parse_and_bind('bind ^I rl_complete')
        else:
            readline.parse_and_bind('tab: complete')

        try:
            readline.read_init_file()
        except OSError:
            # An OSError here could have many causes, but the most likely one
            # is that there's no .inputrc file (or .editrc file in the case of
            # Mac OS X + libedit) in the expected location.  In that case, we
            # want to ignore the exception.
            pass

        ikiwa readline.get_current_history_length() == 0:
            # If no history was loaded, default to .python_history.
            # The guard is necessary to avoid doubling history size at
            # each interpreter exit when readline was already configured
            # through a PYTHONSTARTUP hook, see:
            # http://bugs.python.org/issue5845#msg198636
            history = os.path.join(os.path.expanduser('~'),
                                   '.python_history')
            try:
                readline.read_history_file(history)
            except OSError:
                pass

            eleza write_history():
                try:
                    readline.write_history_file(history)
                except (FileNotFoundError, PermissionError):
                    # home directory does not exist or is not writable
                    # https://bugs.python.org/issue19891
                    pass

            atexit.register(write_history)

    sys.__interactivehook__ = register_readline

eleza venv(known_paths):
    global PREFIXES, ENABLE_USER_SITE

    env = os.environ
    ikiwa sys.platform == 'darwin' and '__PYVENV_LAUNCHER__' in env:
        executable = sys._base_executable = os.environ['__PYVENV_LAUNCHER__']
    else:
        executable = sys.executable
    exe_dir, _ = os.path.split(os.path.abspath(executable))
    site_prefix = os.path.dirname(exe_dir)
    sys._home = None
    conf_basename = 'pyvenv.cfg'
    candidate_confs = [
        conffile for conffile in (
            os.path.join(exe_dir, conf_basename),
            os.path.join(site_prefix, conf_basename)
            )
        ikiwa os.path.isfile(conffile)
        ]

    ikiwa candidate_confs:
        virtual_conf = candidate_confs[0]
        system_site = "true"
        # Issue 25185: Use UTF-8, as that's what the venv module uses when
        # writing the file.
        with open(virtual_conf, encoding='utf-8') as f:
            for line in f:
                ikiwa '=' in line:
                    key, _, value = line.partition('=')
                    key = key.strip().lower()
                    value = value.strip()
                    ikiwa key == 'include-system-site-packages':
                        system_site = value.lower()
                    elikiwa key == 'home':
                        sys._home = value

        sys.prefix = sys.exec_prefix = site_prefix

        # Doing this here ensures venv takes precedence over user-site
        addsitepackages(known_paths, [sys.prefix])

        # addsitepackages will process site_prefix again ikiwa its in PREFIXES,
        # but that's ok; known_paths will prevent anything being added twice
        ikiwa system_site == "true":
            PREFIXES.insert(0, sys.prefix)
        else:
            PREFIXES = [sys.prefix]
            ENABLE_USER_SITE = False

    rudisha known_paths


eleza execsitecustomize():
    """Run custom site specific code, ikiwa available."""
    try:
        try:
            agiza sitecustomize
        except ImportError as exc:
            ikiwa exc.name == 'sitecustomize':
                pass
            else:
                raise
    except Exception as err:
        ikiwa sys.flags.verbose:
            sys.excepthook(*sys.exc_info())
        else:
            sys.stderr.write(
                "Error in sitecustomize; set PYTHONVERBOSE for traceback:\n"
                "%s: %s\n" %
                (err.__class__.__name__, err))


eleza execusercustomize():
    """Run custom user specific code, ikiwa available."""
    try:
        try:
            agiza usercustomize
        except ImportError as exc:
            ikiwa exc.name == 'usercustomize':
                pass
            else:
                raise
    except Exception as err:
        ikiwa sys.flags.verbose:
            sys.excepthook(*sys.exc_info())
        else:
            sys.stderr.write(
                "Error in usercustomize; set PYTHONVERBOSE for traceback:\n"
                "%s: %s\n" %
                (err.__class__.__name__, err))


eleza main():
    """Add standard site-specific directories to the module search path.

    This function is called automatically when this module is imported,
    unless the python interpreter was started with the -S flag.
    """
    global ENABLE_USER_SITE

    orig_path = sys.path[:]
    known_paths = removeduppaths()
    ikiwa orig_path != sys.path:
        # removeduppaths() might make sys.path absolute.
        # fix __file__ and __cached__ of already imported modules too.
        abs_paths()

    known_paths = venv(known_paths)
    ikiwa ENABLE_USER_SITE is None:
        ENABLE_USER_SITE = check_enableusersite()
    known_paths = addusersitepackages(known_paths)
    known_paths = addsitepackages(known_paths)
    setquit()
    setcopyright()
    sethelper()
    ikiwa not sys.flags.isolated:
        enablerlcompleter()
    execsitecustomize()
    ikiwa ENABLE_USER_SITE:
        execusercustomize()

# Prevent extending of sys.path when python was started with -S and
# site is imported later.
ikiwa not sys.flags.no_site:
    main()

eleza _script():
    help = """\
    %s [--user-base] [--user-site]

    Without arguments print some useful information
    With arguments print the value of USER_BASE and/or USER_SITE separated
    by '%s'.

    Exit codes with --user-base or --user-site:
      0 - user site directory is enabled
      1 - user site directory is disabled by user
      2 - uses site directory is disabled by super user
          or for security reasons
     >2 - unknown error
    """
    args = sys.argv[1:]
    ikiwa not args:
        user_base = getuserbase()
        user_site = getusersitepackages()
        andika("sys.path = [")
        for dir in sys.path:
            andika("    %r," % (dir,))
        andika("]")
        andika("USER_BASE: %r (%s)" % (user_base,
            "exists" ikiwa os.path.isdir(user_base) else "doesn't exist"))
        andika("USER_SITE: %r (%s)" % (user_site,
            "exists" ikiwa os.path.isdir(user_site) else "doesn't exist"))
        andika("ENABLE_USER_SITE: %r" %  ENABLE_USER_SITE)
        sys.exit(0)

    buffer = []
    ikiwa '--user-base' in args:
        buffer.append(USER_BASE)
    ikiwa '--user-site' in args:
        buffer.append(USER_SITE)

    ikiwa buffer:
        andika(os.pathsep.join(buffer))
        ikiwa ENABLE_USER_SITE:
            sys.exit(0)
        elikiwa ENABLE_USER_SITE is False:
            sys.exit(1)
        elikiwa ENABLE_USER_SITE is None:
            sys.exit(2)
        else:
            sys.exit(3)
    else:
        agiza textwrap
        andika(textwrap.dedent(help % (sys.argv[0], os.pathsep)))
        sys.exit(10)

ikiwa __name__ == '__main__':
    _script()
