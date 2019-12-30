"""distutils.errors

Provides exceptions used by the Distutils modules.  Note that Distutils
modules may ashiria standard exceptions; kwenye particular, SystemExit is
usually raised kila errors that are obviously the end-user's fault
(eg. bad command-line arguments).

This module ni safe to use kwenye "kutoka ... agiza *" mode; it only exports
symbols whose names start ukijumuisha "Distutils" na end ukijumuisha "Error"."""

kundi DistutilsError (Exception):
    """The root of all Distutils evil."""
    pita

kundi DistutilsModuleError (DistutilsError):
    """Unable to load an expected module, ama to find an expected class
    within some module (in particular, command modules na classes)."""
    pita

kundi DistutilsClassError (DistutilsError):
    """Some command kundi (or possibly distribution class, ikiwa anyone
    feels a need to subkundi Distribution) ni found sio to be holding
    up its end of the bargain, ie. implementing some part of the
    "command "interface."""
    pita

kundi DistutilsGetoptError (DistutilsError):
    """The option table provided to 'fancy_getopt()' ni bogus."""
    pita

kundi DistutilsArgError (DistutilsError):
    """Raised by fancy_getopt kwenye response to getopt.error -- ie. an
    error kwenye the command line usage."""
    pita

kundi DistutilsFileError (DistutilsError):
    """Any problems kwenye the filesystem: expected file sio found, etc.
    Typically this ni kila problems that we detect before OSError
    could be raised."""
    pita

kundi DistutilsOptionError (DistutilsError):
    """Syntactic/semantic errors kwenye command options, such kama use of
    mutually conflicting options, ama inconsistent options,
    badly-spelled values, etc.  No distinction ni made between option
    values originating kwenye the setup script, the command line, config
    files, ama what-have-you -- but ikiwa we *know* something originated kwenye
    the setup script, we'll ashiria DistutilsSetupError instead."""
    pita

kundi DistutilsSetupError (DistutilsError):
    """For errors that can be definitely blamed on the setup script,
    such kama invalid keyword arguments to 'setup()'."""
    pita

kundi DistutilsPlatformError (DistutilsError):
    """We don't know how to do something on the current platform (but
    we do know how to do it on some platform) -- eg. trying to compile
    C files on a platform sio supported by a CCompiler subclass."""
    pita

kundi DistutilsExecError (DistutilsError):
    """Any problems executing an external program (such kama the C
    compiler, when compiling C files)."""
    pita

kundi DistutilsInternalError (DistutilsError):
    """Internal inconsistencies ama impossibilities (obviously, this
    should never be seen ikiwa the code ni working!)."""
    pita

kundi DistutilsTemplateError (DistutilsError):
    """Syntax error kwenye a file list template."""

kundi DistutilsByteCompileError(DistutilsError):
    """Byte compile error."""

# Exception classes used by the CCompiler implementation classes
kundi CCompilerError (Exception):
    """Some compile/link operation failed."""

kundi PreprocessError (CCompilerError):
    """Failure to preprocess one ama more C/C++ files."""

kundi CompileError (CCompilerError):
    """Failure to compile one ama more C/C++ source files."""

kundi LibError (CCompilerError):
    """Failure to create a static library kutoka one ama more C/C++ object
    files."""

kundi LinkError (CCompilerError):
    """Failure to link one ama more C/C++ object files into an executable
    ama shared library file."""

kundi UnknownFileError (CCompilerError):
    """Attempt to process an unknown file type."""
