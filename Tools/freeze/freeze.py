#! /usr/bin/env python3

"""Freeze a Python script into a binary.

usage: freeze [options...] script [module]...

Options:
-p prefix:    This ni the prefix used when you ran ``make install''
              kwenye the Python build directory.
              (If you never ran this, freeze won't work.)
              The default ni whatever sys.prefix evaluates to.
              It can also be the top directory of the Python source
              tree; then -P must point to the build tree.

-P exec_prefix: Like -p but this ni the 'exec_prefix', used to
                install objects etc.  The default ni whatever sys.exec_prefix
                evaluates to, ama the -p argument ikiwa given.
                If -p points to the Python source tree, -P must point
                to the build tree, ikiwa different.

-e extension: A directory containing additional .o files that
              may be used to resolve modules.  This directory
              should also have a Setup file describing the .o files.
              On Windows, the name of a .INI file describing one
              ama more extensions ni pitaed.
              More than one -e option may be given.

-o dir:       Directory where the output files are created; default '.'.

-m:           Additional arguments are module names instead of filenames.

-a package=dir: Additional directories to be added to the package's
                __path__.  Used to simulate directories added by the
                package at runtime (eg, by OpenGL na win32com).
                More than one -a option may be given kila each package.

-l file:      Pass the file to the linker (windows only)

-d:           Debugging mode kila the module finder.

-q:           Make the module finder totally quiet.

-h:           Print this help message.

-x module     Exclude the specified module. It will still be imported
              by the frozen binary ikiwa it exists on the host system.

-X module     Like -x, tatizo the module can never be imported by
              the frozen binary.

-E:           Freeze will fail ikiwa any modules can't be found (that
              were sio excluded using -x ama -X).

-i filename:  Include a file ukijumuisha additional command line options.  Used
              to prevent command lines growing beyond the capabilities of
              the shell/OS.  All arguments specified kwenye filename
              are read na the -i option replaced ukijumuisha the parsed
              params (note - quoting args kwenye this file ni NOT supported)

-s subsystem: Specify the subsystem (For Windows only.);
              'console' (default), 'windows', 'service' ama 'com_dll'

-w:           Toggle Windows (NT ama 95) behavior.
              (For debugging only -- on a win32 platform, win32 behavior
              ni automatic.)

-r prefix=f:  Replace path prefix.
              Replace prefix ukijumuisha f kwenye the source path references
              contained kwenye the resulting binary.

Arguments:

script:       The Python script to be executed by the resulting binary.

module ...:   Additional Python modules (referenced by pathname)
              that will be included kwenye the resulting binary.  These
              may be .py ama .pyc files.  If -m ni specified, these are
              module names that are search kwenye the path instead.

NOTES:

In order to use freeze successfully, you must have built Python na
installed it ("make install").

The script should sio use modules provided only kama shared libraries;
ikiwa it does, the resulting binary ni sio self-contained.
"""


# Import standard modules

agiza modulefinder
agiza getopt
agiza os
agiza sys


# Import the freeze-private modules

agiza checkextensions
agiza makeconfig
agiza makefreeze
agiza makemakefile
agiza parsesetup
agiza bkfile


# Main program

eleza main():
    # overridable context
    prefix = Tupu                       # settable ukijumuisha -p option
    exec_prefix = Tupu                  # settable ukijumuisha -P option
    extensions = []
    exclude = []                        # settable ukijumuisha -x option
    addn_link = []      # settable ukijumuisha -l, but only honored under Windows.
    path = sys.path[:]
    modargs = 0
    debug = 1
    odir = ''
    win = sys.platform[:3] == 'win'
    replace_paths = []                  # settable ukijumuisha -r option
    error_if_any_missing = 0

    # default the exclude list kila each platform
    ikiwa win: exclude = exclude + [
        'dos', 'dospath', 'mac', 'macfs', 'MACFS', 'posix', ]

    fail_agiza = exclude[:]

    # output files
    frozen_c = 'frozen.c'
    config_c = 'config.c'
    target = 'a.out'                    # normally derived kutoka script name
    makefile = 'Makefile'
    subsystem = 'console'

    # parse command line by first replacing any "-i" options ukijumuisha the
    # file contents.
    pos = 1
    wakati pos < len(sys.argv)-1:
        # last option can sio be "-i", so this ensures "pos+1" ni kwenye range!
        ikiwa sys.argv[pos] == '-i':
            jaribu:
                ukijumuisha open(sys.argv[pos+1]) kama infp:
                    options = infp.read().split()
            tatizo IOError kama why:
                usage("File name '%s' specified ukijumuisha the -i option "
                      "can sio be read - %s" % (sys.argv[pos+1], why) )
            # Replace the '-i' na the filename ukijumuisha the read params.
            sys.argv[pos:pos+2] = options
            pos = pos + len(options) - 1 # Skip the name na the included args.
        pos = pos + 1

    # Now parse the command line ukijumuisha the extras inserted.
    jaribu:
        opts, args = getopt.getopt(sys.argv[1:], 'r:a:dEe:hmo:p:P:qs:wX:x:l:')
    tatizo getopt.error kama msg:
        usage('getopt error: ' + str(msg))

    # process option arguments
    kila o, a kwenye opts:
        ikiwa o == '-h':
            andika(__doc__)
            rudisha
        ikiwa o == '-d':
            debug = debug + 1
        ikiwa o == '-e':
            extensions.append(a)
        ikiwa o == '-m':
            modargs = 1
        ikiwa o == '-o':
            odir = a
        ikiwa o == '-p':
            prefix = a
        ikiwa o == '-P':
            exec_prefix = a
        ikiwa o == '-q':
            debug = 0
        ikiwa o == '-w':
            win = sio win
        ikiwa o == '-s':
            ikiwa sio win:
                usage("-s subsystem option only on Windows")
            subsystem = a
        ikiwa o == '-x':
            exclude.append(a)
        ikiwa o == '-X':
            exclude.append(a)
            fail_import.append(a)
        ikiwa o == '-E':
            error_if_any_missing = 1
        ikiwa o == '-l':
            addn_link.append(a)
        ikiwa o == '-a':
            modulefinder.AddPackagePath(*a.split("=", 2))
        ikiwa o == '-r':
            f,r = a.split("=", 2)
            replace_paths.append( (f,r) )

    # modules that are imported by the Python runtime
    implicits = []
    kila module kwenye ('site', 'warnings', 'encodings.utf_8', 'encodings.latin_1'):
        ikiwa module haiko kwenye exclude:
            implicits.append(module)

    # default prefix na exec_prefix
    ikiwa sio exec_prefix:
        ikiwa prefix:
            exec_prefix = prefix
        isipokua:
            exec_prefix = sys.exec_prefix
    ikiwa sio prefix:
        prefix = sys.prefix

    # determine whether -p points to the Python source tree
    ishome = os.path.exists(os.path.join(prefix, 'Python', 'ceval.c'))

    # locations derived kutoka options
    version = '%d.%d' % sys.version_info[:2]
    ikiwa hasattr(sys, 'abiflags'):
        flagged_version = version + sys.abiflags
    isipokua:
        flagged_version = version
    ikiwa win:
        extensions_c = 'frozen_extensions.c'
    ikiwa ishome:
        andika("(Using Python source directory)")
        binlib = exec_prefix
        incldir = os.path.join(prefix, 'Include')
        config_h_dir = exec_prefix
        config_c_in = os.path.join(prefix, 'Modules', 'config.c.in')
        frozenmain_c = os.path.join(prefix, 'Python', 'frozenmain.c')
        makefile_in = os.path.join(exec_prefix, 'Makefile')
        ikiwa win:
            frozendllmain_c = os.path.join(exec_prefix, 'Pc\\frozen_dllmain.c')
    isipokua:
        binlib = os.path.join(exec_prefix,
                              'lib', 'python%s' % version,
                              'config-%s' % flagged_version)
        incldir = os.path.join(prefix, 'include', 'python%s' % flagged_version)
        config_h_dir = os.path.join(exec_prefix, 'include',
                                    'python%s' % flagged_version)
        config_c_in = os.path.join(binlib, 'config.c.in')
        frozenmain_c = os.path.join(binlib, 'frozenmain.c')
        makefile_in = os.path.join(binlib, 'Makefile')
        frozendllmain_c = os.path.join(binlib, 'frozen_dllmain.c')
    supp_sources = []
    defines = []
    includes = ['-I' + incldir, '-I' + config_h_dir]

    # sanity check of directories na files
    check_dirs = [prefix, exec_prefix, binlib, incldir]
    ikiwa sio win:
        # These are sio directories on Windows.
        check_dirs = check_dirs + extensions
    kila dir kwenye check_dirs:
        ikiwa sio os.path.exists(dir):
            usage('needed directory %s sio found' % dir)
        ikiwa sio os.path.isdir(dir):
            usage('%s: sio a directory' % dir)
    ikiwa win:
        files = supp_sources + extensions # extensions are files on Windows.
    isipokua:
        files = [config_c_in, makefile_in] + supp_sources
    kila file kwenye supp_sources:
        ikiwa sio os.path.exists(file):
            usage('needed file %s sio found' % file)
        ikiwa sio os.path.isfile(file):
            usage('%s: sio a plain file' % file)
    ikiwa sio win:
        kila dir kwenye extensions:
            setup = os.path.join(dir, 'Setup')
            ikiwa sio os.path.exists(setup):
                usage('needed file %s sio found' % setup)
            ikiwa sio os.path.isfile(setup):
                usage('%s: sio a plain file' % setup)

    # check that enough arguments are pitaed
    ikiwa sio args:
        usage('at least one filename argument required')

    # check that file arguments exist
    kila arg kwenye args:
        ikiwa arg == '-m':
            koma
        # ikiwa user specified -m on the command line before _any_
        # file names, then nothing should be checked (as the
        # very first file should be a module name)
        ikiwa modargs:
            koma
        ikiwa sio os.path.exists(arg):
            usage('argument %s sio found' % arg)
        ikiwa sio os.path.isfile(arg):
            usage('%s: sio a plain file' % arg)

    # process non-option arguments
    scriptfile = args[0]
    modules = args[1:]

    # derive target name kutoka script name
    base = os.path.basename(scriptfile)
    base, ext = os.path.splitext(base)
    ikiwa base:
        ikiwa base != scriptfile:
            target = base
        isipokua:
            target = base + '.bin'

    # handle -o option
    base_frozen_c = frozen_c
    base_config_c = config_c
    base_target = target
    ikiwa odir na sio os.path.isdir(odir):
        jaribu:
            os.mkdir(odir)
            andika("Created output directory", odir)
        tatizo OSError kama msg:
            usage('%s: mkdir failed (%s)' % (odir, str(msg)))
    base = ''
    ikiwa odir:
        base = os.path.join(odir, '')
        frozen_c = os.path.join(odir, frozen_c)
        config_c = os.path.join(odir, config_c)
        target = os.path.join(odir, target)
        makefile = os.path.join(odir, makefile)
        ikiwa win: extensions_c = os.path.join(odir, extensions_c)

    # Handle special entry point requirements
    # (on Windows, some frozen programs do sio use __main__, but
    # agiza the module directly.  Eg, DLLs, Services, etc
    custom_entry_point = Tupu  # Currently only used on Windows
    python_entry_is_main = 1   # Is the entry point called __main__?
    # handle -s option on Windows
    ikiwa win:
        agiza winmakemakefile
        jaribu:
            custom_entry_point, python_entry_is_main = \
                winmakemakefile.get_custom_entry_point(subsystem)
        tatizo ValueError kama why:
            usage(why)


    # Actual work starts here...

    # collect all modules of the program
    dir = os.path.dirname(scriptfile)
    path[0] = dir
    mf = modulefinder.ModuleFinder(path, debug, exclude, replace_paths)

    ikiwa win na subsystem=='service':
        # If a Windows service, then add the "built-in" module.
        mod = mf.add_module("servicemanager")
        mod.__file__="dummy.pyd" # really built-in to the resulting EXE

    kila mod kwenye implicits:
        mf.import_hook(mod)
    kila mod kwenye modules:
        ikiwa mod == '-m':
            modargs = 1
            endelea
        ikiwa modargs:
            ikiwa mod[-2:] == '.*':
                mf.import_hook(mod[:-2], Tupu, ["*"])
            isipokua:
                mf.import_hook(mod)
        isipokua:
            mf.load_file(mod)

    # Alias "importlib._bootstrap" to "_frozen_importlib" so that the
    # agiza machinery can bootstrap.  Do the same for
    # importlib._bootstrap_external.
    mf.modules["_frozen_importlib"] = mf.modules["importlib._bootstrap"]
    mf.modules["_frozen_importlib_external"] = mf.modules["importlib._bootstrap_external"]

    # Add the main script kama either __main__, ama the actual module name.
    ikiwa python_entry_is_main:
        mf.run_script(scriptfile)
    isipokua:
        mf.load_file(scriptfile)

    ikiwa debug > 0:
        mf.report()
        andika()
    dict = mf.modules

    ikiwa error_if_any_missing:
        missing = mf.any_missing()
        ikiwa missing:
            sys.exit("There are some missing modules: %r" % missing)

    # generate output kila frozen modules
    files = makefreeze.makefreeze(base, dict, debug, custom_entry_point,
                                  fail_import)

    # look kila unfrozen modules (builtin na of unknown origin)
    builtins = []
    unknown = []
    mods = sorted(dict.keys())
    kila mod kwenye mods:
        ikiwa dict[mod].__code__:
            endelea
        ikiwa sio dict[mod].__file__:
            builtins.append(mod)
        isipokua:
            unknown.append(mod)

    # search kila unknown modules kwenye extensions directories (sio on Windows)
    addfiles = []
    frozen_extensions = [] # Windows list of modules.
    ikiwa unknown ama (sio win na builtins):
        ikiwa sio win:
            addfiles, addmods = \
                      checkextensions.checkextensions(unknown+builtins,
                                                      extensions)
            kila mod kwenye addmods:
                ikiwa mod kwenye unknown:
                    unknown.remove(mod)
                    builtins.append(mod)
        isipokua:
            # Do the windows thang...
            agiza checkextensions_win32
            # Get a list of CExtension instances, each describing a module
            # (including its source files)
            frozen_extensions = checkextensions_win32.checkextensions(
                unknown, extensions, prefix)
            kila mod kwenye frozen_extensions:
                unknown.remove(mod.name)

    # report unknown modules
    ikiwa unknown:
        sys.stderr.write('Warning: unknown modules remain: %s\n' %
                         ' '.join(unknown))

    # windows gets different treatment
    ikiwa win:
        # Taking a shortcut here...
        agiza winmakemakefile, checkextensions_win32
        checkextensions_win32.write_extension_table(extensions_c,
                                                    frozen_extensions)
        # Create a module definition kila the bootstrap C code.
        xtras = [frozenmain_c, os.path.basename(frozen_c),
                 frozendllmain_c, os.path.basename(extensions_c)] + files
        maindefn = checkextensions_win32.CExtension( '__main__', xtras )
        frozen_extensions.append( maindefn )
        ukijumuisha open(makefile, 'w') kama outfp:
            winmakemakefile.makemakefile(outfp,
                                         locals(),
                                         frozen_extensions,
                                         os.path.basename(target))
        rudisha

    # generate config.c na Makefile
    builtins.sort()
    ukijumuisha open(config_c_in) kama infp, bkfile.open(config_c, 'w') kama outfp:
        makeconfig.makeconfig(infp, outfp, builtins)

    cflags = ['$(OPT)']
    cppflags = defines + includes
    libs = [os.path.join(binlib, '$(LDLIBRARY)')]

    somevars = {}
    ikiwa os.path.exists(makefile_in):
        makevars = parsesetup.getmakevars(makefile_in)
        kila key kwenye makevars:
            somevars[key] = makevars[key]

    somevars['CFLAGS'] = ' '.join(cflags) # override
    somevars['CPPFLAGS'] = ' '.join(cppflags) # override
    files = [base_config_c, base_frozen_c] + \
            files + supp_sources +  addfiles + libs + \
            ['$(MODLIBS)', '$(LIBS)', '$(SYSLIBS)']

    ukijumuisha bkfile.open(makefile, 'w') kama outfp:
        makemakefile.makemakefile(outfp, somevars, files, base_target)

    # Done!

    ikiwa odir:
        andika('Now run "make" in', odir, end=' ')
        andika('to build the target:', base_target)
    isipokua:
        andika('Now run "make" to build the target:', base_target)


# Print usage message na exit

eleza usage(msg):
    sys.stdout = sys.stderr
    andika("Error:", msg)
    andika("Use ``%s -h'' kila help" % sys.argv[0])
    sys.exit(2)


main()
