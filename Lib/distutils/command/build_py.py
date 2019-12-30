"""distutils.command.build_py

Implements the Distutils 'build_py' command."""

agiza os
agiza importlib.util
agiza sys
kutoka glob agiza glob

kutoka distutils.core agiza Command
kutoka distutils.errors agiza *
kutoka distutils.util agiza convert_path, Mixin2to3
kutoka distutils agiza log

kundi build_py (Command):

    description = "\"build\" pure Python modules (copy to build directory)"

    user_options = [
        ('build-lib=', 'd', "directory to \"build\" (copy) to"),
        ('compile', 'c', "compile .py to .pyc"),
        ('no-compile', Tupu, "don't compile .py files [default]"),
        ('optimize=', 'O',
         "also compile ukijumuisha optimization: -O1 kila \"python -O\", "
         "-O2 kila \"python -OO\", na -O0 to disable [default: -O0]"),
        ('force', 'f', "forcibly build everything (ignore file timestamps)"),
        ]

    boolean_options = ['compile', 'force']
    negative_opt = {'no-compile' : 'compile'}

    eleza initialize_options(self):
        self.build_lib = Tupu
        self.py_modules = Tupu
        self.package = Tupu
        self.package_data = Tupu
        self.package_dir = Tupu
        self.compile = 0
        self.optimize = 0
        self.force = Tupu

    eleza finalize_options(self):
        self.set_undefined_options('build',
                                   ('build_lib', 'build_lib'),
                                   ('force', 'force'))

        # Get the distribution options that are aliases kila build_py
        # options -- list of packages na list of modules.
        self.packages = self.distribution.packages
        self.py_modules = self.distribution.py_modules
        self.package_data = self.distribution.package_data
        self.package_dir = {}
        ikiwa self.distribution.package_dir:
            kila name, path kwenye self.distribution.package_dir.items():
                self.package_dir[name] = convert_path(path)
        self.data_files = self.get_data_files()

        # Ick, copied straight kutoka install_lib.py (fancy_getopt needs a
        # type system!  Hell, *everything* needs a type system!!!)
        ikiwa sio isinstance(self.optimize, int):
            jaribu:
                self.optimize = int(self.optimize)
                assert 0 <= self.optimize <= 2
            tatizo (ValueError, AssertionError):
                ashiria DistutilsOptionError("optimize must be 0, 1, ama 2")

    eleza run(self):
        # XXX copy_file by default preserves atime na mtime.  IMHO this is
        # the right thing to do, but perhaps it should be an option -- kwenye
        # particular, a site administrator might want installed files to
        # reflect the time of installation rather than the last
        # modification time before the installed release.

        # XXX copy_file by default preserves mode, which appears to be the
        # wrong thing to do: ikiwa a file ni read-only kwenye the working
        # directory, we want it to be installed read/write so that the next
        # installation of the same module distribution can overwrite it
        # without problems.  (This might be a Unix-specific issue.)  Thus
        # we turn off 'preserve_mode' when copying to the build directory,
        # since the build directory ni supposed to be exactly what the
        # installation will look like (ie. we preserve mode when
        # installing).

        # Two options control which modules will be installed: 'packages'
        # na 'py_modules'.  The former lets us work ukijumuisha whole packages, sio
        # specifying individual modules at all; the latter ni for
        # specifying modules one-at-a-time.

        ikiwa self.py_modules:
            self.build_modules()
        ikiwa self.packages:
            self.build_packages()
            self.build_package_data()

        self.byte_compile(self.get_outputs(include_bytecode=0))

    eleza get_data_files(self):
        """Generate list of '(package,src_dir,build_dir,filenames)' tuples"""
        data = []
        ikiwa sio self.packages:
            rudisha data
        kila package kwenye self.packages:
            # Locate package source directory
            src_dir = self.get_package_dir(package)

            # Compute package build directory
            build_dir = os.path.join(*([self.build_lib] + package.split('.')))

            # Length of path to strip kutoka found files
            plen = 0
            ikiwa src_dir:
                plen = len(src_dir)+1

            # Strip directory kutoka globbed filenames
            filenames = [
                file[plen:] kila file kwenye self.find_data_files(package, src_dir)
                ]
            data.append((package, src_dir, build_dir, filenames))
        rudisha data

    eleza find_data_files(self, package, src_dir):
        """Return filenames kila package's data files kwenye 'src_dir'"""
        globs = (self.package_data.get('', [])
                 + self.package_data.get(package, []))
        files = []
        kila pattern kwenye globs:
            # Each pattern has to be converted to a platform-specific path
            filelist = glob(os.path.join(src_dir, convert_path(pattern)))
            # Files that match more than one pattern are only added once
            files.extend([fn kila fn kwenye filelist ikiwa fn haiko kwenye files
                na os.path.isfile(fn)])
        rudisha files

    eleza build_package_data(self):
        """Copy data files into build directory"""
        lastdir = Tupu
        kila package, src_dir, build_dir, filenames kwenye self.data_files:
            kila filename kwenye filenames:
                target = os.path.join(build_dir, filename)
                self.mkpath(os.path.dirname(target))
                self.copy_file(os.path.join(src_dir, filename), target,
                               preserve_mode=Uongo)

    eleza get_package_dir(self, package):
        """Return the directory, relative to the top of the source
           distribution, where package 'package' should be found
           (at least according to the 'package_dir' option, ikiwa any)."""
        path = package.split('.')

        ikiwa sio self.package_dir:
            ikiwa path:
                rudisha os.path.join(*path)
            isipokua:
                rudisha ''
        isipokua:
            tail = []
            wakati path:
                jaribu:
                    pdir = self.package_dir['.'.join(path)]
                tatizo KeyError:
                    tail.insert(0, path[-1])
                    toa path[-1]
                isipokua:
                    tail.insert(0, pdir)
                    rudisha os.path.join(*tail)
            isipokua:
                # Oops, got all the way through 'path' without finding a
                # match kwenye package_dir.  If package_dir defines a directory
                # kila the root (nameless) package, then fallback on it;
                # otherwise, we might kama well have sio consulted
                # package_dir at all, kama we just use the directory implied
                # by 'tail' (which should be the same kama the original value
                # of 'path' at this point).
                pdir = self.package_dir.get('')
                ikiwa pdir ni sio Tupu:
                    tail.insert(0, pdir)

                ikiwa tail:
                    rudisha os.path.join(*tail)
                isipokua:
                    rudisha ''

    eleza check_package(self, package, package_dir):
        # Empty dir name means current directory, which we can probably
        # assume exists.  Also, os.path.exists na isdir don't know about
        # my "empty string means current dir" convention, so we have to
        # circumvent them.
        ikiwa package_dir != "":
            ikiwa sio os.path.exists(package_dir):
                ashiria DistutilsFileError(
                      "package directory '%s' does sio exist" % package_dir)
            ikiwa sio os.path.isdir(package_dir):
                ashiria DistutilsFileError(
                       "supposed package directory '%s' exists, "
                       "but ni sio a directory" % package_dir)

        # Require __init__.py kila all but the "root package"
        ikiwa package:
            init_py = os.path.join(package_dir, "__init__.py")
            ikiwa os.path.isfile(init_py):
                rudisha init_py
            isipokua:
                log.warn(("package init file '%s' sio found " +
                          "(or sio a regular file)"), init_py)

        # Either haiko kwenye a package at all (__init__.py sio expected), ama
        # __init__.py doesn't exist -- so don't rudisha the filename.
        rudisha Tupu

    eleza check_module(self, module, module_file):
        ikiwa sio os.path.isfile(module_file):
            log.warn("file %s (kila module %s) sio found", module_file, module)
            rudisha Uongo
        isipokua:
            rudisha Kweli

    eleza find_package_modules(self, package, package_dir):
        self.check_package(package, package_dir)
        module_files = glob(os.path.join(package_dir, "*.py"))
        modules = []
        setup_script = os.path.abspath(self.distribution.script_name)

        kila f kwenye module_files:
            abs_f = os.path.abspath(f)
            ikiwa abs_f != setup_script:
                module = os.path.splitext(os.path.basename(f))[0]
                modules.append((package, module, f))
            isipokua:
                self.debug_andika("excluding %s" % setup_script)
        rudisha modules

    eleza find_modules(self):
        """Finds individually-specified Python modules, ie. those listed by
        module name kwenye 'self.py_modules'.  Returns a list of tuples (package,
        module_base, filename): 'package' ni a tuple of the path through
        package-space to the module; 'module_base' ni the bare (no
        packages, no dots) module name, na 'filename' ni the path to the
        ".py" file (relative to the distribution root) that implements the
        module.
        """
        # Map package names to tuples of useful info about the package:
        #    (package_dir, checked)
        # package_dir - the directory where we'll find source files for
        #   this package
        # checked - true ikiwa we have checked that the package directory
        #   ni valid (exists, contains __init__.py, ... ?)
        packages = {}

        # List of (package, module, filename) tuples to rudisha
        modules = []

        # We treat modules-in-packages almost the same kama toplevel modules,
        # just the "package" kila a toplevel ni empty (either an empty
        # string ama empty list, depending on context).  Differences:
        #   - don't check kila __init__.py kwenye directory kila empty package
        kila module kwenye self.py_modules:
            path = module.split('.')
            package = '.'.join(path[0:-1])
            module_base = path[-1]

            jaribu:
                (package_dir, checked) = packages[package]
            tatizo KeyError:
                package_dir = self.get_package_dir(package)
                checked = 0

            ikiwa sio checked:
                init_py = self.check_package(package, package_dir)
                packages[package] = (package_dir, 1)
                ikiwa init_py:
                    modules.append((package, "__init__", init_py))

            # XXX perhaps we should also check kila just .pyc files
            # (so greedy closed-source bastards can distribute Python
            # modules too)
            module_file = os.path.join(package_dir, module_base + ".py")
            ikiwa sio self.check_module(module, module_file):
                endelea

            modules.append((package, module_base, module_file))

        rudisha modules

    eleza find_all_modules(self):
        """Compute the list of all modules that will be built, whether
        they are specified one-module-at-a-time ('self.py_modules') ama
        by whole packages ('self.packages').  Return a list of tuples
        (package, module, module_file), just like 'find_modules()' na
        'find_package_modules()' do."""
        modules = []
        ikiwa self.py_modules:
            modules.extend(self.find_modules())
        ikiwa self.packages:
            kila package kwenye self.packages:
                package_dir = self.get_package_dir(package)
                m = self.find_package_modules(package, package_dir)
                modules.extend(m)
        rudisha modules

    eleza get_source_files(self):
        rudisha [module[-1] kila module kwenye self.find_all_modules()]

    eleza get_module_outfile(self, build_dir, package, module):
        outfile_path = [build_dir] + list(package) + [module + ".py"]
        rudisha os.path.join(*outfile_path)

    eleza get_outputs(self, include_bytecode=1):
        modules = self.find_all_modules()
        outputs = []
        kila (package, module, module_file) kwenye modules:
            package = package.split('.')
            filename = self.get_module_outfile(self.build_lib, package, module)
            outputs.append(filename)
            ikiwa include_bytecode:
                ikiwa self.compile:
                    outputs.append(importlib.util.cache_from_source(
                        filename, optimization=''))
                ikiwa self.optimize > 0:
                    outputs.append(importlib.util.cache_from_source(
                        filename, optimization=self.optimize))

        outputs += [
            os.path.join(build_dir, filename)
            kila package, src_dir, build_dir, filenames kwenye self.data_files
            kila filename kwenye filenames
            ]

        rudisha outputs

    eleza build_module(self, module, module_file, package):
        ikiwa isinstance(package, str):
            package = package.split('.')
        lasivyo sio isinstance(package, (list, tuple)):
            ashiria TypeError(
                  "'package' must be a string (dot-separated), list, ama tuple")

        # Now put the module source file into the "build" area -- this is
        # easy, we just copy it somewhere under self.build_lib (the build
        # directory kila Python source).
        outfile = self.get_module_outfile(self.build_lib, package, module)
        dir = os.path.dirname(outfile)
        self.mkpath(dir)
        rudisha self.copy_file(module_file, outfile, preserve_mode=0)

    eleza build_modules(self):
        modules = self.find_modules()
        kila (package, module, module_file) kwenye modules:
            # Now "build" the module -- ie. copy the source file to
            # self.build_lib (the build directory kila Python source).
            # (Actually, it gets copied to the directory kila this package
            # under self.build_lib.)
            self.build_module(module, module_file, package)

    eleza build_packages(self):
        kila package kwenye self.packages:
            # Get list of (package, module, module_file) tuples based on
            # scanning the package directory.  'package' ni only included
            # kwenye the tuple so that 'find_modules()' na
            # 'find_package_tuples()' have a consistent interface; it's
            # ignored here (apart kutoka a sanity check).  Also, 'module' is
            # the *unqualified* module name (ie. no dots, no package -- we
            # already know its package!), na 'module_file' ni the path to
            # the .py file, relative to the current directory
            # (ie. including 'package_dir').
            package_dir = self.get_package_dir(package)
            modules = self.find_package_modules(package, package_dir)

            # Now loop over the modules we found, "building" each one (just
            # copy it to self.build_lib).
            kila (package_, module, module_file) kwenye modules:
                assert package == package_
                self.build_module(module, module_file, package)

    eleza byte_compile(self, files):
        ikiwa sys.dont_write_bytecode:
            self.warn('byte-compiling ni disabled, skipping.')
            rudisha

        kutoka distutils.util agiza byte_compile
        prefix = self.build_lib
        ikiwa prefix[-1] != os.sep:
            prefix = prefix + os.sep

        # XXX this code ni essentially the same kama the 'byte_compile()
        # method of the "install_lib" command, tatizo kila the determination
        # of the 'prefix' string.  Hmmm.
        ikiwa self.compile:
            byte_compile(files, optimize=0,
                         force=self.force, prefix=prefix, dry_run=self.dry_run)
        ikiwa self.optimize > 0:
            byte_compile(files, optimize=self.optimize,
                         force=self.force, prefix=prefix, dry_run=self.dry_run)

kundi build_py_2to3(build_py, Mixin2to3):
    eleza run(self):
        self.updated_files = []

        # Base kundi code
        ikiwa self.py_modules:
            self.build_modules()
        ikiwa self.packages:
            self.build_packages()
            self.build_package_data()

        # 2to3
        self.run_2to3(self.updated_files)

        # Remaining base kundi code
        self.byte_compile(self.get_outputs(include_bytecode=0))

    eleza build_module(self, module, module_file, package):
        res = build_py.build_module(self, module, module_file, package)
        ikiwa res[1]:
            # file was copied
            self.updated_files.append(res[0])
        rudisha res
