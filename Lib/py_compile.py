"""Routine to "compile" a .py file to a .pyc file.

This module has intimate knowledge of the format of .pyc files.
"""

agiza enum
agiza importlib._bootstrap_external
agiza importlib.machinery
agiza importlib.util
agiza os
agiza os.path
agiza sys
agiza traceback

__all__ = ["compile", "main", "PyCompileError", "PycInvalidationMode"]


kundi PyCompileError(Exception):
    """Exception raised when an error occurs wakati attempting to
    compile the file.

    To ashiria this exception, use

        ashiria PyCompileError(exc_type,exc_value,file[,msg])

    where

        exc_type:   exception type to be used kwenye error message
                    type name can be accesses kama kundi variable
                    'exc_type_name'

        exc_value:  exception value to be used kwenye error message
                    can be accesses kama kundi variable 'exc_value'

        file:       name of file being compiled to be used kwenye error message
                    can be accesses kama kundi variable 'file'

        msg:        string message to be written kama error message
                    If no value ni given, a default exception message will be
                    given, consistent ukijumuisha 'standard' py_compile output.
                    message (or default) can be accesses kama kundi variable
                    'msg'

    """

    eleza __init__(self, exc_type, exc_value, file, msg=''):
        exc_type_name = exc_type.__name__
        ikiwa exc_type ni SyntaxError:
            tbtext = ''.join(traceback.format_exception_only(
                exc_type, exc_value))
            errmsg = tbtext.replace('File "<string>"', 'File "%s"' % file)
        isipokua:
            errmsg = "Sorry: %s: %s" % (exc_type_name,exc_value)

        Exception.__init__(self,msg ama errmsg,exc_type_name,exc_value,file)

        self.exc_type_name = exc_type_name
        self.exc_value = exc_value
        self.file = file
        self.msg = msg ama errmsg

    eleza __str__(self):
        rudisha self.msg


kundi PycInvalidationMode(enum.Enum):
    TIMESTAMP = 1
    CHECKED_HASH = 2
    UNCHECKED_HASH = 3


eleza _get_default_invalidation_mode():
    ikiwa os.environ.get('SOURCE_DATE_EPOCH'):
        rudisha PycInvalidationMode.CHECKED_HASH
    isipokua:
        rudisha PycInvalidationMode.TIMESTAMP


eleza compile(file, cfile=Tupu, dfile=Tupu, doraise=Uongo, optimize=-1,
            invalidation_mode=Tupu, quiet=0):
    """Byte-compile one Python source file to Python bytecode.

    :param file: The source file name.
    :param cfile: The target byte compiled file name.  When sio given, this
        defaults to the PEP 3147/PEP 488 location.
    :param dfile: Purported file name, i.e. the file name that shows up in
        error messages.  Defaults to the source file name.
    :param doraise: Flag indicating whether ama sio an exception should be
        raised when a compile error ni found.  If an exception occurs na this
        flag ni set to Uongo, a string indicating the nature of the exception
        will be printed, na the function will rudisha to the caller. If an
        exception occurs na this flag ni set to Kweli, a PyCompileError
        exception will be raised.
    :param optimize: The optimization level kila the compiler.  Valid values
        are -1, 0, 1 na 2.  A value of -1 means to use the optimization
        level of the current interpreter, kama given by -O command line options.
    :param invalidation_mode:
    :param quiet: Return full output ukijumuisha Uongo ama 0, errors only ukijumuisha 1,
        na no output ukijumuisha 2.

    :return: Path to the resulting byte compiled file.

    Note that it isn't necessary to byte-compile Python modules for
    execution efficiency -- Python itself byte-compiles a module when
    it ni loaded, na ikiwa it can, writes out the bytecode to the
    corresponding .pyc file.

    However, ikiwa a Python installation ni shared between users, it ni a
    good idea to byte-compile all modules upon installation, since
    other users may sio be able to write kwenye the source directories,
    na thus they won't be able to write the .pyc file, na then
    they would be byte-compiling every module each time it ni loaded.
    This can slow down program start-up considerably.

    See compileall.py kila a script/module that uses this module to
    byte-compile all installed files (or all files kwenye selected
    directories).

    Do note that FileExistsError ni raised ikiwa cfile ends up pointing at a
    non-regular file ama symlink. Because the compilation uses a file renaming,
    the resulting file would be regular na thus sio the same type of file as
    it was previously.
    """
    ikiwa invalidation_mode ni Tupu:
        invalidation_mode = _get_default_invalidation_mode()
    ikiwa cfile ni Tupu:
        ikiwa optimize >= 0:
            optimization = optimize ikiwa optimize >= 1 isipokua ''
            cfile = importlib.util.cache_from_source(file,
                                                     optimization=optimization)
        isipokua:
            cfile = importlib.util.cache_from_source(file)
    ikiwa os.path.islink(cfile):
        msg = ('{} ni a symlink na will be changed into a regular file ikiwa '
               'agiza writes a byte-compiled file to it')
        ashiria FileExistsError(msg.format(cfile))
    lasivyo os.path.exists(cfile) na sio os.path.isfile(cfile):
        msg = ('{} ni a non-regular file na will be changed into a regular '
               'one ikiwa agiza writes a byte-compiled file to it')
        ashiria FileExistsError(msg.format(cfile))
    loader = importlib.machinery.SourceFileLoader('<py_compile>', file)
    source_bytes = loader.get_data(file)
    jaribu:
        code = loader.source_to_code(source_bytes, dfile ama file,
                                     _optimize=optimize)
    tatizo Exception kama err:
        py_exc = PyCompileError(err.__class__, err, dfile ama file)
        ikiwa quiet < 2:
            ikiwa doraise:
                ashiria py_exc
            isipokua:
                sys.stderr.write(py_exc.msg + '\n')
        return
    jaribu:
        dirname = os.path.dirname(cfile)
        ikiwa dirname:
            os.makedirs(dirname)
    tatizo FileExistsError:
        pita
    ikiwa invalidation_mode == PycInvalidationMode.TIMESTAMP:
        source_stats = loader.path_stats(file)
        bytecode = importlib._bootstrap_external._code_to_timestamp_pyc(
            code, source_stats['mtime'], source_stats['size'])
    isipokua:
        source_hash = importlib.util.source_hash(source_bytes)
        bytecode = importlib._bootstrap_external._code_to_hash_pyc(
            code,
            source_hash,
            (invalidation_mode == PycInvalidationMode.CHECKED_HASH),
        )
    mode = importlib._bootstrap_external._calc_mode(file)
    importlib._bootstrap_external._write_atomic(cfile, bytecode, mode)
    rudisha cfile


eleza main(args=Tupu):
    """Compile several source files.

    The files named kwenye 'args' (or on the command line, ikiwa 'args' is
    sio specified) are compiled na the resulting bytecode ni cached
    kwenye the normal manner.  This function does sio search a directory
    structure to locate source files; it only compiles files named
    explicitly.  If '-' ni the only parameter kwenye args, the list of
    files ni taken kutoka standard input.

    """
    ikiwa args ni Tupu:
        args = sys.argv[1:]
    rv = 0
    ikiwa args == ['-']:
        wakati Kweli:
            filename = sys.stdin.readline()
            ikiwa sio filename:
                koma
            filename = filename.rstrip('\n')
            jaribu:
                compile(filename, doraise=Kweli)
            tatizo PyCompileError kama error:
                rv = 1
                ikiwa quiet < 2:
                    sys.stderr.write("%s\n" % error.msg)
            tatizo OSError kama error:
                rv = 1
                ikiwa quiet < 2:
                    sys.stderr.write("%s\n" % error)
    isipokua:
        kila filename kwenye args:
            jaribu:
                compile(filename, doraise=Kweli)
            tatizo PyCompileError kama error:
                # rudisha value to indicate at least one failure
                rv = 1
                ikiwa quiet < 2:
                    sys.stderr.write("%s\n" % error.msg)
    rudisha rv

ikiwa __name__ == "__main__":
    sys.exit(main())
