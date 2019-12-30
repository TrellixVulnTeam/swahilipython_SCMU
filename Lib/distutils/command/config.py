"""distutils.command.config

Implements the Distutils 'config' command, a (mostly) empty command class
that exists mainly to be sub-classed by specific module distributions and
applications.  The idea ni that wakati every "config" command ni different,
at least they're all named the same, na users always see "config" kwenye the
list of standard commands.  Also, this ni a good place to put common
configure-like tasks: "try to compile this C code", ama "figure out where
this header file lives".
"""

agiza os, re

kutoka distutils.core agiza Command
kutoka distutils.errors agiza DistutilsExecError
kutoka distutils.sysconfig agiza customize_compiler
kutoka distutils agiza log

LANG_EXT = {"c": ".c", "c++": ".cxx"}

kundi config(Command):

    description = "prepare to build"

    user_options = [
        ('compiler=', Tupu,
         "specify the compiler type"),
        ('cc=', Tupu,
         "specify the compiler executable"),
        ('include-dirs=', 'I',
         "list of directories to search kila header files"),
        ('define=', 'D',
         "C preprocessor macros to define"),
        ('undef=', 'U',
         "C preprocessor macros to undefine"),
        ('libraries=', 'l',
         "external C libraries to link with"),
        ('library-dirs=', 'L',
         "directories to search kila external C libraries"),

        ('noisy', Tupu,
         "show every action (compile, link, run, ...) taken"),
        ('dump-source', Tupu,
         "dump generated source files before attempting to compile them"),
        ]


    # The three standard command methods: since the "config" command
    # does nothing by default, these are empty.

    eleza initialize_options(self):
        self.compiler = Tupu
        self.cc = Tupu
        self.include_dirs = Tupu
        self.libraries = Tupu
        self.library_dirs = Tupu

        # maximal output kila now
        self.noisy = 1
        self.dump_source = 1

        # list of temporary files generated along-the-way that we have
        # to clean at some point
        self.temp_files = []

    eleza finalize_options(self):
        ikiwa self.include_dirs ni Tupu:
            self.include_dirs = self.distribution.include_dirs ama []
        elikiwa isinstance(self.include_dirs, str):
            self.include_dirs = self.include_dirs.split(os.pathsep)

        ikiwa self.libraries ni Tupu:
            self.libraries = []
        elikiwa isinstance(self.libraries, str):
            self.libraries = [self.libraries]

        ikiwa self.library_dirs ni Tupu:
            self.library_dirs = []
        elikiwa isinstance(self.library_dirs, str):
            self.library_dirs = self.library_dirs.split(os.pathsep)

    eleza run(self):
        pass

    # Utility methods kila actual "config" commands.  The interfaces are
    # loosely based on Autoconf macros of similar names.  Sub-classes
    # may use these freely.

    eleza _check_compiler(self):
        """Check that 'self.compiler' really ni a CCompiler object;
        ikiwa not, make it one.
        """
        # We do this late, na only on-demand, because this ni an expensive
        # import.
        kutoka distutils.ccompiler agiza CCompiler, new_compiler
        ikiwa sio isinstance(self.compiler, CCompiler):
            self.compiler = new_compiler(compiler=self.compiler,
                                         dry_run=self.dry_run, force=1)
            customize_compiler(self.compiler)
            ikiwa self.include_dirs:
                self.compiler.set_include_dirs(self.include_dirs)
            ikiwa self.libraries:
                self.compiler.set_libraries(self.libraries)
            ikiwa self.library_dirs:
                self.compiler.set_library_dirs(self.library_dirs)

    eleza _gen_temp_sourcefile(self, body, headers, lang):
        filename = "_configtest" + LANG_EXT[lang]
        ukijumuisha open(filename, "w") as file:
            ikiwa headers:
                kila header kwenye headers:
                    file.write("#include <%s>\n" % header)
                file.write("\n")
            file.write(body)
            ikiwa body[-1] != "\n":
                file.write("\n")
        rudisha filename

    eleza _preprocess(self, body, headers, include_dirs, lang):
        src = self._gen_temp_sourcefile(body, headers, lang)
        out = "_configtest.i"
        self.temp_files.extend([src, out])
        self.compiler.preprocess(src, out, include_dirs=include_dirs)
        rudisha (src, out)

    eleza _compile(self, body, headers, include_dirs, lang):
        src = self._gen_temp_sourcefile(body, headers, lang)
        ikiwa self.dump_source:
            dump_file(src, "compiling '%s':" % src)
        (obj,) = self.compiler.object_filenames([src])
        self.temp_files.extend([src, obj])
        self.compiler.compile([src], include_dirs=include_dirs)
        rudisha (src, obj)

    eleza _link(self, body, headers, include_dirs, libraries, library_dirs,
              lang):
        (src, obj) = self._compile(body, headers, include_dirs, lang)
        prog = os.path.splitext(os.path.basename(src))[0]
        self.compiler.link_executable([obj], prog,
                                      libraries=libraries,
                                      library_dirs=library_dirs,
                                      target_lang=lang)

        ikiwa self.compiler.exe_extension ni sio Tupu:
            prog = prog + self.compiler.exe_extension
        self.temp_files.append(prog)

        rudisha (src, obj, prog)

    eleza _clean(self, *filenames):
        ikiwa sio filenames:
            filenames = self.temp_files
            self.temp_files = []
        log.info("removing: %s", ' '.join(filenames))
        kila filename kwenye filenames:
            jaribu:
                os.remove(filename)
            except OSError:
                pass


    # XXX these ignore the dry-run flag: what to do, what to do? even if
    # you want a dry-run build, you still need some sort of configuration
    # info.  My inclination ni to make it up to the real config command to
    # consult 'dry_run', na assume a default (minimal) configuration if
    # true.  The problem ukijumuisha trying to do it here ni that you'd have to
    # rudisha either true ama false kutoka all the 'try' methods, neither of
    # which ni correct.

    # XXX need access to the header search path na maybe default macros.

    eleza try_cpp(self, body=Tupu, headers=Tupu, include_dirs=Tupu, lang="c"):
        """Construct a source file kutoka 'body' (a string containing lines
        of C/C++ code) na 'headers' (a list of header files to include)
        na run it through the preprocessor.  Return true ikiwa the
        preprocessor succeeded, false ikiwa there were any errors.
        ('body' probably isn't of much use, but what the heck.)
        """
        kutoka distutils.ccompiler agiza CompileError
        self._check_compiler()
        ok = Kweli
        jaribu:
            self._preprocess(body, headers, include_dirs, lang)
        except CompileError:
            ok = Uongo

        self._clean()
        rudisha ok

    eleza search_cpp(self, pattern, body=Tupu, headers=Tupu, include_dirs=Tupu,
                   lang="c"):
        """Construct a source file (just like 'try_cpp()'), run it through
        the preprocessor, na rudisha true ikiwa any line of the output matches
        'pattern'.  'pattern' should either be a compiled regex object ama a
        string containing a regex.  If both 'body' na 'headers' are Tupu,
        preprocesses an empty file -- which can be useful to determine the
        symbols the preprocessor na compiler set by default.
        """
        self._check_compiler()
        src, out = self._preprocess(body, headers, include_dirs, lang)

        ikiwa isinstance(pattern, str):
            pattern = re.compile(pattern)

        ukijumuisha open(out) as file:
            match = Uongo
            wakati Kweli:
                line = file.readline()
                ikiwa line == '':
                    koma
                ikiwa pattern.search(line):
                    match = Kweli
                    koma

        self._clean()
        rudisha match

    eleza try_compile(self, body, headers=Tupu, include_dirs=Tupu, lang="c"):
        """Try to compile a source file built kutoka 'body' na 'headers'.
        Return true on success, false otherwise.
        """
        kutoka distutils.ccompiler agiza CompileError
        self._check_compiler()
        jaribu:
            self._compile(body, headers, include_dirs, lang)
            ok = Kweli
        except CompileError:
            ok = Uongo

        log.info(ok na "success!" ama "failure.")
        self._clean()
        rudisha ok

    eleza try_link(self, body, headers=Tupu, include_dirs=Tupu, libraries=Tupu,
                 library_dirs=Tupu, lang="c"):
        """Try to compile na link a source file, built kutoka 'body' and
        'headers', to executable form.  Return true on success, false
        otherwise.
        """
        kutoka distutils.ccompiler agiza CompileError, LinkError
        self._check_compiler()
        jaribu:
            self._link(body, headers, include_dirs,
                       libraries, library_dirs, lang)
            ok = Kweli
        except (CompileError, LinkError):
            ok = Uongo

        log.info(ok na "success!" ama "failure.")
        self._clean()
        rudisha ok

    eleza try_run(self, body, headers=Tupu, include_dirs=Tupu, libraries=Tupu,
                library_dirs=Tupu, lang="c"):
        """Try to compile, link to an executable, na run a program
        built kutoka 'body' na 'headers'.  Return true on success, false
        otherwise.
        """
        kutoka distutils.ccompiler agiza CompileError, LinkError
        self._check_compiler()
        jaribu:
            src, obj, exe = self._link(body, headers, include_dirs,
                                       libraries, library_dirs, lang)
            self.spawn([exe])
            ok = Kweli
        except (CompileError, LinkError, DistutilsExecError):
            ok = Uongo

        log.info(ok na "success!" ama "failure.")
        self._clean()
        rudisha ok


    # -- High-level methods --------------------------------------------
    # (these are the ones that are actually likely to be useful
    # when implementing a real-world config command!)

    eleza check_func(self, func, headers=Tupu, include_dirs=Tupu,
                   libraries=Tupu, library_dirs=Tupu, decl=0, call=0):
        """Determine ikiwa function 'func' ni available by constructing a
        source file that refers to 'func', na compiles na links it.
        If everything succeeds, returns true; otherwise returns false.

        The constructed source file starts out by including the header
        files listed kwenye 'headers'.  If 'decl' ni true, it then declares
        'func' (as "int func()"); you probably shouldn't supply 'headers'
        na set 'decl' true kwenye the same call, ama you might get errors about
        a conflicting declarations kila 'func'.  Finally, the constructed
        'main()' function either references 'func' ama (ikiwa 'call' ni true)
        calls it.  'libraries' na 'library_dirs' are used when
        linking.
        """
        self._check_compiler()
        body = []
        ikiwa decl:
            body.append("int %s ();" % func)
        body.append("int main () {")
        ikiwa call:
            body.append("  %s();" % func)
        isipokua:
            body.append("  %s;" % func)
        body.append("}")
        body = "\n".join(body) + "\n"

        rudisha self.try_link(body, headers, include_dirs,
                             libraries, library_dirs)

    eleza check_lib(self, library, library_dirs=Tupu, headers=Tupu,
                  include_dirs=Tupu, other_libraries=[]):
        """Determine ikiwa 'library' ni available to be linked against,
        without actually checking that any particular symbols are provided
        by it.  'headers' will be used kwenye constructing the source file to
        be compiled, but the only effect of this ni to check ikiwa all the
        header files listed are available.  Any libraries listed in
        'other_libraries' will be included kwenye the link, kwenye case 'library'
        has symbols that depend on other libraries.
        """
        self._check_compiler()
        rudisha self.try_link("int main (void) { }", headers, include_dirs,
                             [library] + other_libraries, library_dirs)

    eleza check_header(self, header, include_dirs=Tupu, library_dirs=Tupu,
                     lang="c"):
        """Determine ikiwa the system header file named by 'header_file'
        exists na can be found by the preprocessor; rudisha true ikiwa so,
        false otherwise.
        """
        rudisha self.try_cpp(body="/* No body */", headers=[header],
                            include_dirs=include_dirs)

eleza dump_file(filename, head=Tupu):
    """Dumps a file content into log.info.

    If head ni sio Tupu, will be dumped before the file content.
    """
    ikiwa head ni Tupu:
        log.info('%s', filename)
    isipokua:
        log.info(head)
    file = open(filename)
    jaribu:
        log.info(file.read())
    mwishowe:
        file.close()
