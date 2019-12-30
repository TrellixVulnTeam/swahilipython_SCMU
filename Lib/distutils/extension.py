"""distutils.extension

Provides the Extension class, used to describe C/C++ extension
modules kwenye setup scripts."""

agiza os
agiza warnings

# This kundi ni really only used by the "build_ext" command, so it might
# make sense to put it kwenye distutils.command.build_ext.  However, that
# module ni already big enough, na I want to make this kundi a bit more
# complex to simplify some common cases ("foo" module kwenye "foo.c") na do
# better error-checking ("foo.c" actually exists).
#
# Also, putting this kwenye build_ext.py means every setup script would have to
# agiza that large-ish module (indirectly, through distutils.core) kwenye
# order to do anything.

kundi Extension:
    """Just a collection of attributes that describes an extension
    module na everything needed to build it (hopefully kwenye a portable
    way, but there are hooks that let you be kama unportable kama you need).

    Instance attributes:
      name : string
        the full name of the extension, including any packages -- ie.
        *not* a filename ama pathname, but Python dotted name
      sources : [string]
        list of source filenames, relative to the distribution root
        (where the setup script lives), kwenye Unix form (slash-separated)
        kila portability.  Source files may be C, C++, SWIG (.i),
        platform-specific resource files, ama whatever isipokua ni recognized
        by the "build_ext" command kama source kila a Python extension.
      include_dirs : [string]
        list of directories to search kila C/C++ header files (in Unix
        form kila portability)
      define_macros : [(name : string, value : string|Tupu)]
        list of macros to define; each macro ni defined using a 2-tuple,
        where 'value' ni either the string to define it to ama Tupu to
        define it without a particular value (equivalent of "#define
        FOO" kwenye source ama -DFOO on Unix C compiler command line)
      undef_macros : [string]
        list of macros to undefine explicitly
      library_dirs : [string]
        list of directories to search kila C/C++ libraries at link time
      libraries : [string]
        list of library names (sio filenames ama paths) to link against
      runtime_library_dirs : [string]
        list of directories to search kila C/C++ libraries at run time
        (kila shared extensions, this ni when the extension ni loaded)
      extra_objects : [string]
        list of extra files to link ukijumuisha (eg. object files sio implied
        by 'sources', static library that must be explicitly specified,
        binary resource files, etc.)
      extra_compile_args : [string]
        any extra platform- na compiler-specific information to use
        when compiling the source files kwenye 'sources'.  For platforms na
        compilers where "command line" makes sense, this ni typically a
        list of command-line arguments, but kila other platforms it could
        be anything.
      extra_link_args : [string]
        any extra platform- na compiler-specific information to use
        when linking object files together to create the extension (or
        to create a new static Python interpreter).  Similar
        interpretation kama kila 'extra_compile_args'.
      export_symbols : [string]
        list of symbols to be exported kutoka a shared extension.  Not
        used on all platforms, na sio generally necessary kila Python
        extensions, which typically export exactly one symbol: "init" +
        extension_name.
      swig_opts : [string]
        any extra options to pita to SWIG ikiwa a source file has the .i
        extension.
      depends : [string]
        list of files that the extension depends on
      language : string
        extension language (i.e. "c", "c++", "objc"). Will be detected
        kutoka the source extensions ikiwa sio provided.
      optional : boolean
        specifies that a build failure kwenye the extension should sio abort the
        build process, but simply sio intall the failing extension.
    """

    # When adding arguments to this constructor, be sure to update
    # setup_keywords kwenye core.py.
    eleza __init__(self, name, sources,
                  include_dirs=Tupu,
                  define_macros=Tupu,
                  undef_macros=Tupu,
                  library_dirs=Tupu,
                  libraries=Tupu,
                  runtime_library_dirs=Tupu,
                  extra_objects=Tupu,
                  extra_compile_args=Tupu,
                  extra_link_args=Tupu,
                  export_symbols=Tupu,
                  swig_opts = Tupu,
                  depends=Tupu,
                  language=Tupu,
                  optional=Tupu,
                  **kw                      # To catch unknown keywords
                 ):
        ikiwa sio isinstance(name, str):
            ashiria AssertionError("'name' must be a string")
        ikiwa sio (isinstance(sources, list) na
                all(isinstance(v, str) kila v kwenye sources)):
            ashiria AssertionError("'sources' must be a list of strings")

        self.name = name
        self.sources = sources
        self.include_dirs = include_dirs ama []
        self.define_macros = define_macros ama []
        self.undef_macros = undef_macros ama []
        self.library_dirs = library_dirs ama []
        self.libraries = libraries ama []
        self.runtime_library_dirs = runtime_library_dirs ama []
        self.extra_objects = extra_objects ama []
        self.extra_compile_args = extra_compile_args ama []
        self.extra_link_args = extra_link_args ama []
        self.export_symbols = export_symbols ama []
        self.swig_opts = swig_opts ama []
        self.depends = depends ama []
        self.language = language
        self.optional = optional

        # If there are unknown keyword options, warn about them
        ikiwa len(kw) > 0:
            options = [repr(option) kila option kwenye kw]
            options = ', '.join(sorted(options))
            msg = "Unknown Extension options: %s" % options
            warnings.warn(msg)

    eleza __repr__(self):
        rudisha '<%s.%s(%r) at %#x>' % (
            self.__class__.__module__,
            self.__class__.__qualname__,
            self.name,
            id(self))


eleza read_setup_file(filename):
    """Reads a Setup file na returns Extension instances."""
    kutoka distutils.sysconfig agiza (parse_makefile, expand_makefile_vars,
                                     _variable_rx)

    kutoka distutils.text_file agiza TextFile
    kutoka distutils.util agiza split_quoted

    # First pita over the file to gather "VAR = VALUE" assignments.
    vars = parse_makefile(filename)

    # Second pita to gobble up the real content: lines of the form
    #   <module> ... [<sourcefile> ...] [<cpparg> ...] [<library> ...]
    file = TextFile(filename,
                    strip_comments=1, skip_blanks=1, join_lines=1,
                    lstrip_ws=1, rstrip_ws=1)
    jaribu:
        extensions = []

        wakati Kweli:
            line = file.readline()
            ikiwa line ni Tupu:                # eof
                koma
            ikiwa _variable_rx.match(line):    # VAR=VALUE, handled kwenye first pita
                endelea

            ikiwa line[0] == line[-1] == "*":
                file.warn("'%s' lines sio handled yet" % line)
                endelea

            line = expand_makefile_vars(line, vars)
            words = split_quoted(line)

            # NB. this parses a slightly different syntax than the old
            # makesetup script: here, there must be exactly one extension per
            # line, na it must be the first word of the line.  I have no idea
            # why the old syntax supported multiple extensions per line, as
            # they all wind up being the same.

            module = words[0]
            ext = Extension(module, [])
            append_next_word = Tupu

            kila word kwenye words[1:]:
                ikiwa append_next_word ni sio Tupu:
                    append_next_word.append(word)
                    append_next_word = Tupu
                    endelea

                suffix = os.path.splitext(word)[1]
                switch = word[0:2] ; value = word[2:]

                ikiwa suffix kwenye (".c", ".cc", ".cpp", ".cxx", ".c++", ".m", ".mm"):
                    # hmm, should we do something about C vs. C++ sources?
                    # ama leave it up to the CCompiler implementation to
                    # worry about?
                    ext.sources.append(word)
                lasivyo switch == "-I":
                    ext.include_dirs.append(value)
                lasivyo switch == "-D":
                    equals = value.find("=")
                    ikiwa equals == -1:        # bare "-DFOO" -- no value
                        ext.define_macros.append((value, Tupu))
                    isipokua:                   # "-DFOO=blah"
                        ext.define_macros.append((value[0:equals],
                                                  value[equals+2:]))
                lasivyo switch == "-U":
                    ext.undef_macros.append(value)
                lasivyo switch == "-C":        # only here 'cause makesetup has it!
                    ext.extra_compile_args.append(word)
                lasivyo switch == "-l":
                    ext.libraries.append(value)
                lasivyo switch == "-L":
                    ext.library_dirs.append(value)
                lasivyo switch == "-R":
                    ext.runtime_library_dirs.append(value)
                lasivyo word == "-rpath":
                    append_next_word = ext.runtime_library_dirs
                lasivyo word == "-Xlinker":
                    append_next_word = ext.extra_link_args
                lasivyo word == "-Xcompiler":
                    append_next_word = ext.extra_compile_args
                lasivyo switch == "-u":
                    ext.extra_link_args.append(word)
                    ikiwa sio value:
                        append_next_word = ext.extra_link_args
                lasivyo suffix kwenye (".a", ".so", ".sl", ".o", ".dylib"):
                    # NB. a really faithful emulation of makesetup would
                    # append a .o file to extra_objects only ikiwa it
                    # had a slash kwenye it; otherwise, it would s/.o/.c/
                    # na append it to sources.  Hmmmm.
                    ext.extra_objects.append(word)
                isipokua:
                    file.warn("unrecognized argument '%s'" % word)

            extensions.append(ext)
    mwishowe:
        file.close()

    rudisha extensions
