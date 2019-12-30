"""Append module search paths kila third-party packages to sys.path.

****************************************************************
* This module ni automatically imported during initialization. *
****************************************************************

This will append site-specific paths to the module search path.  On
Unix (including Mac OSX), it starts ukijumuisha sys.prefix and
sys.exec_prefix (ikiwa different) na appends
lib/python<version>/site-packages.
On other platforms (such as Windows), it tries each of the
prefixes directly, as well as ukijumuisha lib/site-packages appended.  The
resulting directories, ikiwa they exist, are appended to sys.path, and
also inspected kila path configuration files.

If a file named "pyvenv.cfg" exists one directory above sys.executable,
sys.prefix na sys.exec_prefix are set to that directory and
it ni also checked kila site-packages (sys.base_prefix and
sys.base_exec_prefix will always be the "real" prefixes of the Python
installation). If "pyvenv.cfg" (a bootstrap configuration file) contains
the key "include-system-site-packages" set to anything other than "false"
(case-insensitive), the system-level prefixes will still also be
searched kila site-packages; otherwise they won't.

All of the resulting site-specific directories, ikiwa they exist, are
appended to sys.path, na also inspected kila path configuration
files.

A path configuration file ni a file whose name has the form
<package>.pth; its contents are additional directories (one per line)
to be added to sys.path.  Non-existing directories (or
non-directories) are never added to sys.path; no directory ni added to
sys.path more than once.  Blank lines na lines beginning with
'#' are skipped. Lines starting ukijumuisha 'import' are executed.

For example, suppose sys.prefix na sys.exec_prefix are set to
/usr/local na there ni a directory /usr/local/lib/python2.5/site-packages
ukijumuisha three subdirectories, foo, bar na spam, na two path
configuration files, foo.pth na bar.pth.  Assume foo.pth contains the
following:

  # foo package configuration
  foo
  bar
  bletch

and bar.pth contains:

  # bar package configuration
  bar

Then the following directories are added to sys.path, kwenye this order:

  /usr/local/lib/python2.5/site-packages/bar
  /usr/local/lib/python2.5/site-packages/foo

Note that bletch ni omitted because it doesn't exist; bar precedes foo
because bar.pth comes alphabetically before foo.pth; na spam is
omitted because it ni sio mentioned kwenye either path configuration file.

The readline module ni also automatically configured to enable
completion kila systems that support it.  This can be overridden in
sitecustomize, usercustomize ama PYTHONSTARTUP.  Starting Python in
isolated mode (-I) disables automatic readline configuration.

After these operations, an attempt ni made to agiza a module
named sitecustomize, which can perform arbitrary additional
site-specific customizations.  If this agiza fails ukijumuisha an
ImportError exception, it ni silently ignored.
"""

agiza sys
agiza os
agiza builtins
agiza _sitebuiltins
agiza io

# Prefixes kila site-packages; add additional prefixes like /usr/local here
PREFIXES = [sys.prefix, sys.exec_prefix]
# Enable per user site-packages directory
# set it to Uongo to disable the feature ama Kweli to force the feature
ENABLE_USER_SITE = Tupu

# kila distutils.commands.install
# These values are initialized by the getuserbase() na getusersitepackages()
# functions, through the main() function when Python starts.
USER_SITE = Tupu
USER_BASE = Tupu


eleza makepath(*paths):
    dir = os.path.join(*paths)
    jaribu:
        dir = os.path.abspath(dir)
    except OSError:
        pass
    rudisha dir, os.path.normcase(dir)


eleza abs_paths():
    """Set all module __file__ na __cached__ attributes to an absolute path"""
    kila m kwenye set(sys.modules.values()):
        ikiwa (getattr(getattr(m, '__loader__', Tupu), '__module__', Tupu) sio in
                ('_frozen_importlib', '_frozen_importlib_external')):
            endelea   # don't mess ukijumuisha a PEP 302-supplied __file__
        jaribu:
            m.__file__ = os.path.abspath(m.__file__)
        except (AttributeError, OSError, TypeError):
            pass
        jaribu:
            m.__cached__ = os.path.abspath(m.__cached__)
        except (AttributeError, OSError, TypeError):
            pass


eleza removeduppaths():
    """ Remove duplicate entries kutoka sys.path along ukijumuisha making them
    absolute"""
    # This ensures that the initial path provided by the interpreter contains
    # only absolute pathnames, even ikiwa we're running kutoka the build directory.
    L = []
    known_paths = set()
    kila dir kwenye sys.path:
        # Filter out duplicate paths (on case-insensitive file systems also
        # ikiwa they only differ kwenye case); turn relative paths into absolute
        # paths.
        dir, dircase = makepath(dir)
        ikiwa dircase sio kwenye known_paths:
            L.append(dir)
            known_paths.add(dircase)
    sys.path[:] = L
    rudisha known_paths


eleza _init_pathinfo():
    """Return a set containing all existing file system items kutoka sys.path."""
    d = set()
    kila item kwenye sys.path:
        jaribu:
            ikiwa os.path.exists(item):
                _, itemcase = makepath(item)
                d.add(itemcase)
        except TypeError:
            endelea
    rudisha d


eleza addpackage(sitedir, name, known_paths):
    """Process a .pth file within the site-packages directory:
       For each line kwenye the file, either combine it ukijumuisha sitedir to a path
       na add that to known_paths, ama execute it ikiwa it starts ukijumuisha 'agiza '.
    """
    ikiwa known_paths ni Tupu:
        known_paths = _init_pathinfo()
        reset = Kweli
    isipokua:
        reset = Uongo
    fullname = os.path.join(sitedir, name)
    jaribu:
        f = io.TextIOWrapper(io.open_code(fullname))
    except OSError:
        return
    ukijumuisha f:
        kila n, line kwenye enumerate(f):
            ikiwa line.startswith("#"):
                endelea
            jaribu:
                ikiwa line.startswith(("agiza ", "import\t")):
                    exec(line)
                    endelea
                line = line.rstrip()
                dir, dircase = makepath(sitedir, line)
                ikiwa sio dircase kwenye known_paths na os.path.exists(dir):
                    sys.path.append(dir)
                    known_paths.add(dircase)
            except Exception:
                andika("Error processing line {:d} of {}:\n".format(n+1, fullname),
                      file=sys.stderr)
                agiza traceback
                kila record kwenye traceback.format_exception(*sys.exc_info()):
                    kila line kwenye record.splitlines():
                        andika('  '+line, file=sys.stderr)
                andika("\nRemainder of file ignored", file=sys.stderr)
                koma
    ikiwa reset:
        known_paths = Tupu
    rudisha known_paths


eleza addsitedir(sitedir, known_paths=Tupu):
    """Add 'sitedir' argument to sys.path ikiwa missing na handle .pth files in
    'sitedir'"""
    ikiwa known_paths ni Tupu:
        known_paths = _init_pathinfo()
        reset = Kweli
    isipokua:
        reset = Uongo
    sitedir, sitedircase = makepath(sitedir)
    ikiwa sio sitedircase kwenye known_paths:
        sys.path.append(sitedir)        # Add path component
        known_paths.add(sitedircase)
    jaribu:
        names = os.listdir(sitedir)
    except OSError:
        return
    names = [name kila name kwenye names ikiwa name.endswith(".pth")]
    kila name kwenye sorted(names):
        addpackage(sitedir, name, known_paths)
    ikiwa reset:
        known_paths = Tupu
    rudisha known_paths


eleza check_enableusersite():
    """Check ikiwa user site directory ni safe kila inclusion

    The function tests kila the command line flag (including environment var),
    process uid/gid equal to effective uid/gid.

    Tupu: Disabled kila security reasons
    Uongo: Disabled by user (command line option)
    Kweli: Safe na enabled
    """
    ikiwa sys.flags.no_user_site:
        rudisha Uongo

    ikiwa hasattr(os, "getuid") na hasattr(os, "geteuid"):
        # check process uid == effective uid
        ikiwa os.geteuid() != os.getuid():
            rudisha Tupu
    ikiwa hasattr(os, "getgid") na hasattr(os, "getegid"):
        # check process gid == effective gid
        ikiwa os.getegid() != os.getgid():
            rudisha Tupu

    rudisha Kweli


# NOTE: sysconfig na it's dependencies are relatively large but site module
# needs very limited part of them.
# To speedup startup time, we have copy of them.
#
# See https://bugs.python.org/issue29585

# Copy of sysconfig._getuserbase()
eleza _getuserbase():
    env_base = os.environ.get("PYTHONUSERBASE", Tupu)
    ikiwa env_base:
        rudisha env_base

    eleza joinuser(*args):
        rudisha os.path.expanduser(os.path.join(*args))

    ikiwa os.name == "nt":
        base = os.environ.get("APPDATA") ama "~"
        rudisha joinuser(base, "Python")

    ikiwa sys.platform == "darwin" na sys._framework:
        rudisha joinuser("~", "Library", sys._framework,
                        "%d.%d" % sys.version_info[:2])

    rudisha joinuser("~", ".local")


# Same to sysconfig.get_path('purelib', os.name+'_user')
eleza _get_path(userbase):
    version = sys.version_info

    ikiwa os.name == 'nt':
        rudisha f'{userbase}\\Python{version[0]}{version[1]}\\site-packages'

    ikiwa sys.platform == 'darwin' na sys._framework:
        rudisha f'{userbase}/lib/python/site-packages'

    rudisha f'{userbase}/lib/python{version[0]}.{version[1]}/site-packages'


eleza getuserbase():
    """Returns the `user base` directory path.

    The `user base` directory can be used to store data. If the global
    variable ``USER_BASE`` ni sio initialized yet, this function will also set
    it.
    """
    global USER_BASE
    ikiwa USER_BASE ni Tupu:
        USER_BASE = _getuserbase()
    rudisha USER_BASE


eleza getusersitepackages():
    """Returns the user-specific site-packages directory path.

    If the global variable ``USER_SITE`` ni sio initialized yet, this
    function will also set it.
    """
    global USER_SITE
    userbase = getuserbase() # this will also set USER_BASE

    ikiwa USER_SITE ni Tupu:
        USER_SITE = _get_path(userbase)

    rudisha USER_SITE

eleza addusersitepackages(known_paths):
    """Add a per user site-package to sys.path

    Each user has its own python directory ukijumuisha site-packages kwenye the
    home directory.
    """
    # get the per user site-package path
    # this call will also make sure USER_BASE na USER_SITE are set
    user_site = getusersitepackages()

    ikiwa ENABLE_USER_SITE na os.path.isdir(user_site):
        addsitedir(user_site, known_paths)
    rudisha known_paths

eleza getsitepackages(prefixes=Tupu):
    """Returns a list containing all global site-packages directories.

    For each directory present kwenye ``prefixes`` (or the global ``PREFIXES``),
    this function will find its `site-packages` subdirectory depending on the
    system environment, na will rudisha a list of full paths.
    """
    sitepackages = []
    seen = set()

    ikiwa prefixes ni Tupu:
        prefixes = PREFIXES

    kila prefix kwenye prefixes:
        ikiwa sio prefix ama prefix kwenye seen:
            endelea
        seen.add(prefix)

        ikiwa os.sep == '/':
            sitepackages.append(os.path.join(prefix, "lib",
                                        "python%d.%d" % sys.version_info[:2],
                                        "site-packages"))
        isipokua:
            sitepackages.append(prefix)
            sitepackages.append(os.path.join(prefix, "lib", "site-packages"))
    rudisha sitepackages

eleza addsitepackages(known_paths, prefixes=Tupu):
    """Add site-packages to sys.path"""
    kila sitedir kwenye getsitepackages(prefixes):
        ikiwa os.path.isdir(sitedir):
            addsitedir(sitedir, known_paths)

    rudisha known_paths

eleza setquit():
    """Define new builtins 'quit' na 'exit'.

    These are objects which make the interpreter exit when called.
    The repr of each object contains a hint at how it works.

    """
    ikiwa os.sep == '\\':
        eof = 'Ctrl-Z plus Return'
    isipokua:
        eof = 'Ctrl-D (i.e. EOF)'

    builtins.quit = _sitebuiltins.Quitter('quit', eof)
    builtins.exit = _sitebuiltins.Quitter('exit', eof)


eleza setcopyright():
    """Set 'copyright' na 'credits' kwenye builtins"""
    builtins.copyright = _sitebuiltins._Printer("copyright", sys.copyright)
    ikiwa sys.platform[:4] == 'java':
        builtins.credits = _sitebuiltins._Printer(
            "credits",
            "Jython ni maintained by the Jython developers (www.jython.org).")
    isipokua:
        builtins.credits = _sitebuiltins._Printer("credits", """\
    Thanks to CWI, CNRI, BeOpen.com, Zope Corporation na a cast of thousands
    kila supporting Python development.  See www.python.org kila more information.""")
    files, dirs = [], []
    # Not all modules are required to have a __file__ attribute.  See
    # PEP 420 kila more details.
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
    as completion key na register ~/.python_history as history file.
    This can be overridden kwenye the sitecustomize ama usercustomize module,
    ama kwenye a PYTHONSTARTUP file.
    """
    eleza register_readline():
        agiza atexit
        jaribu:
            agiza readline
            agiza rlcompleter
        except ImportError:
            return

        # Reading the initialization (config) file may sio be enough to set a
        # completion key, so we set one first na then read the file.
        readline_doc = getattr(readline, '__doc__', '')
        ikiwa readline_doc ni sio Tupu na 'libedit' kwenye readline_doc:
            readline.parse_and_bind('bind ^I rl_complete')
        isipokua:
            readline.parse_and_bind('tab: complete')

        jaribu:
            readline.read_init_file()
        except OSError:
            # An OSError here could have many causes, but the most likely one
            # ni that there's no .inputrc file (or .editrc file kwenye the case of
            # Mac OS X + libedit) kwenye the expected location.  In that case, we
            # want to ignore the exception.
            pass

        ikiwa readline.get_current_history_length() == 0:
            # If no history was loaded, default to .python_history.
            # The guard ni necessary to avoid doubling history size at
            # each interpreter exit when readline was already configured
            # through a PYTHONSTARTUP hook, see:
            # http://bugs.python.org/issue5845#msg198636
            history = os.path.join(os.path.expanduser('~'),
                                   '.python_history')
            jaribu:
                readline.read_history_file(history)
            except OSError:
                pass

            eleza write_history():
                jaribu:
                    readline.write_history_file(history)
                except (FileNotFoundError, PermissionError):
                    # home directory does sio exist ama ni sio writable
                    # https://bugs.python.org/issue19891
                    pass

            atexit.register(write_history)

    sys.__interactivehook__ = register_readline

eleza venv(known_paths):
    global PREFIXES, ENABLE_USER_SITE

    env = os.environ
    ikiwa sys.platform == 'darwin' na '__PYVENV_LAUNCHER__' kwenye env:
        executable = sys._base_executable = os.environ['__PYVENV_LAUNCHER__']
    isipokua:
        executable = sys.executable
    exe_dir, _ = os.path.split(os.path.abspath(executable))
    site_prefix = os.path.dirname(exe_dir)
    sys._home = Tupu
    conf_basename = 'pyvenv.cfg'
    candidate_confs = [
        conffile kila conffile kwenye (
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
        ukijumuisha open(virtual_conf, encoding='utf-8') as f:
            kila line kwenye f:
                ikiwa '=' kwenye line:
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

        # addsitepackages will process site_prefix again ikiwa its kwenye PREFIXES,
        # but that's ok; known_paths will prevent anything being added twice
        ikiwa system_site == "true":
            PREFIXES.insert(0, sys.prefix)
        isipokua:
            PREFIXES = [sys.prefix]
            ENABLE_USER_SITE = Uongo

    rudisha known_paths


eleza execsitecustomize():
    """Run custom site specific code, ikiwa available."""
    jaribu:
        jaribu:
            agiza sitecustomize
        except ImportError as exc:
            ikiwa exc.name == 'sitecustomize':
                pass
            isipokua:
                raise
    except Exception as err:
        ikiwa sys.flags.verbose:
            sys.excepthook(*sys.exc_info())
        isipokua:
            sys.stderr.write(
                "Error kwenye sitecustomize; set PYTHONVERBOSE kila traceback:\n"
                "%s: %s\n" %
                (err.__class__.__name__, err))


eleza execusercustomize():
    """Run custom user specific code, ikiwa available."""
    jaribu:
        jaribu:
            agiza usercustomize
        except ImportError as exc:
            ikiwa exc.name == 'usercustomize':
                pass
            isipokua:
                raise
    except Exception as err:
        ikiwa sys.flags.verbose:
            sys.excepthook(*sys.exc_info())
        isipokua:
            sys.stderr.write(
                "Error kwenye usercustomize; set PYTHONVERBOSE kila traceback:\n"
                "%s: %s\n" %
                (err.__class__.__name__, err))


eleza main():
    """Add standard site-specific directories to the module search path.

    This function ni called automatically when this module ni imported,
    unless the python interpreter was started ukijumuisha the -S flag.
    """
    global ENABLE_USER_SITE

    orig_path = sys.path[:]
    known_paths = removeduppaths()
    ikiwa orig_path != sys.path:
        # removeduppaths() might make sys.path absolute.
        # fix __file__ na __cached__ of already imported modules too.
        abs_paths()

    known_paths = venv(known_paths)
    ikiwa ENABLE_USER_SITE ni Tupu:
        ENABLE_USER_SITE = check_enableusersite()
    known_paths = addusersitepackages(known_paths)
    known_paths = addsitepackages(known_paths)
    setquit()
    setcopyright()
    sethelper()
    ikiwa sio sys.flags.isolated:
        enablerlcompleter()
    execsitecustomize()
    ikiwa ENABLE_USER_SITE:
        execusercustomize()

# Prevent extending of sys.path when python was started ukijumuisha -S and
# site ni imported later.
ikiwa sio sys.flags.no_site:
    main()

eleza _script():
    help = """\
    %s [--user-base] [--user-site]

    Without arguments print some useful information
    With arguments print the value of USER_BASE and/or USER_SITE separated
    by '%s'.

    Exit codes ukijumuisha --user-base ama --user-site:
      0 - user site directory ni enabled
      1 - user site directory ni disabled by user
      2 - uses site directory ni disabled by super user
          ama kila security reasons
     >2 - unknown error
    """
    args = sys.argv[1:]
    ikiwa sio args:
        user_base = getuserbase()
        user_site = getusersitepackages()
        andika("sys.path = [")
        kila dir kwenye sys.path:
            andika("    %r," % (dir,))
        andika("]")
        andika("USER_BASE: %r (%s)" % (user_base,
            "exists" ikiwa os.path.isdir(user_base) isipokua "doesn't exist"))
        andika("USER_SITE: %r (%s)" % (user_site,
            "exists" ikiwa os.path.isdir(user_site) isipokua "doesn't exist"))
        andika("ENABLE_USER_SITE: %r" %  ENABLE_USER_SITE)
        sys.exit(0)

    buffer = []
    ikiwa '--user-base' kwenye args:
        buffer.append(USER_BASE)
    ikiwa '--user-site' kwenye args:
        buffer.append(USER_SITE)

    ikiwa buffer:
        andika(os.pathsep.join(buffer))
        ikiwa ENABLE_USER_SITE:
            sys.exit(0)
        elikiwa ENABLE_USER_SITE ni Uongo:
            sys.exit(1)
        elikiwa ENABLE_USER_SITE ni Tupu:
            sys.exit(2)
        isipokua:
            sys.exit(3)
    isipokua:
        agiza textwrap
        andika(textwrap.dedent(help % (sys.argv[0], os.pathsep)))
        sys.exit(10)

ikiwa __name__ == '__main__':
    _script()
