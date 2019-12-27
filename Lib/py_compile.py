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
    """Exception raised when an error occurs while attempting to
    compile the file.

    To raise this exception, use

        raise PyCompileError(exc_type,exc_value,file[,msg])

    where

        exc_type:   exception type to be used in error message
                    type name can be accesses as kundi variable
                    'exc_type_name'

        exc_value:  exception value to be used in error message
                    can be accesses as kundi variable 'exc_value'

        file:       name of file being compiled to be used in error message
                    can be accesses as kundi variable 'file'

        msg:        string message to be written as error message
                    If no value is given, a default exception message will be
                    given, consistent with 'standard' py_compile output.
                    message (or default) can be accesses as kundi variable
                    'msg'

    """

    eleza __init__(self, exc_type, exc_value, file, msg=''):
        exc_type_name = exc_type.__name__
        ikiwa exc_type is SyntaxError:
            tbtext = ''.join(traceback.format_exception_only(
                exc_type, exc_value))
            errmsg = tbtext.replace('File "<string>"', 'File "%s"' % file)
        else:
            errmsg = "Sorry: %s: %s" % (exc_type_name,exc_value)

        Exception.__init__(self,msg or errmsg,exc_type_name,exc_value,file)

        self.exc_type_name = exc_type_name
        self.exc_value = exc_value
        self.file = file
        self.msg = msg or errmsg

    eleza __str__(self):
        rudisha self.msg


kundi PycInvalidationMode(enum.Enum):
    TIMESTAMP = 1
    CHECKED_HASH = 2
    UNCHECKED_HASH = 3


eleza _get_default_invalidation_mode():
    ikiwa os.environ.get('SOURCE_DATE_EPOCH'):
        rudisha PycInvalidationMode.CHECKED_HASH
    else:
        rudisha PycInvalidationMode.TIMESTAMP


eleza compile(file, cfile=None, dfile=None, doraise=False, optimize=-1,
            invalidation_mode=None, quiet=0):
    """Byte-compile one Python source file to Python bytecode.

    :param file: The source file name.
    :param cfile: The target byte compiled file name.  When not given, this
        defaults to the PEP 3147/PEP 488 location.
    :param dfile: Purported file name, i.e. the file name that shows up in
        error messages.  Defaults to the source file name.
    :param doraise: Flag indicating whether or not an exception should be
        raised when a compile error is found.  If an exception occurs and this
        flag is set to False, a string indicating the nature of the exception
        will be printed, and the function will rudisha to the caller. If an
        exception occurs and this flag is set to True, a PyCompileError
        exception will be raised.
    :param optimize: The optimization level for the compiler.  Valid values
        are -1, 0, 1 and 2.  A value of -1 means to use the optimization
        level of the current interpreter, as given by -O command line options.
    :param invalidation_mode:
    :param quiet: Return full output with False or 0, errors only with 1,
        and no output with 2.

    :return: Path to the resulting byte compiled file.

    Note that it isn't necessary to byte-compile Python modules for
    execution efficiency -- Python itself byte-compiles a module when
    it is loaded, and ikiwa it can, writes out the bytecode to the
    corresponding .pyc file.

    However, ikiwa a Python installation is shared between users, it is a
    good idea to byte-compile all modules upon installation, since
    other users may not be able to write in the source directories,
    and thus they won't be able to write the .pyc file, and then
    they would be byte-compiling every module each time it is loaded.
    This can slow down program start-up considerably.

    See compileall.py for a script/module that uses this module to
    byte-compile all installed files (or all files in selected
    directories).

    Do note that FileExistsError is raised ikiwa cfile ends up pointing at a
    non-regular file or symlink. Because the compilation uses a file renaming,
    the resulting file would be regular and thus not the same type of file as
    it was previously.
    """
    ikiwa invalidation_mode is None:
        invalidation_mode = _get_default_invalidation_mode()
    ikiwa cfile is None:
        ikiwa optimize >= 0:
            optimization = optimize ikiwa optimize >= 1 else ''
            cfile = importlib.util.cache_kutoka_source(file,
                                                     optimization=optimization)
        else:
            cfile = importlib.util.cache_kutoka_source(file)
    ikiwa os.path.islink(cfile):
        msg = ('{} is a symlink and will be changed into a regular file ikiwa '
               'agiza writes a byte-compiled file to it')
        raise FileExistsError(msg.format(cfile))
    elikiwa os.path.exists(cfile) and not os.path.isfile(cfile):
        msg = ('{} is a non-regular file and will be changed into a regular '
               'one ikiwa agiza writes a byte-compiled file to it')
        raise FileExistsError(msg.format(cfile))
    loader = importlib.machinery.SourceFileLoader('<py_compile>', file)
    source_bytes = loader.get_data(file)
    try:
        code = loader.source_to_code(source_bytes, dfile or file,
                                     _optimize=optimize)
    except Exception as err:
        py_exc = PyCompileError(err.__class__, err, dfile or file)
        ikiwa quiet < 2:
            ikiwa doraise:
                raise py_exc
            else:
                sys.stderr.write(py_exc.msg + '\n')
        return
    try:
        dirname = os.path.dirname(cfile)
        ikiwa dirname:
            os.makedirs(dirname)
    except FileExistsError:
        pass
    ikiwa invalidation_mode == PycInvalidationMode.TIMESTAMP:
        source_stats = loader.path_stats(file)
        bytecode = importlib._bootstrap_external._code_to_timestamp_pyc(
            code, source_stats['mtime'], source_stats['size'])
    else:
        source_hash = importlib.util.source_hash(source_bytes)
        bytecode = importlib._bootstrap_external._code_to_hash_pyc(
            code,
            source_hash,
            (invalidation_mode == PycInvalidationMode.CHECKED_HASH),
        )
    mode = importlib._bootstrap_external._calc_mode(file)
    importlib._bootstrap_external._write_atomic(cfile, bytecode, mode)
    rudisha cfile


eleza main(args=None):
    """Compile several source files.

    The files named in 'args' (or on the command line, ikiwa 'args' is
    not specified) are compiled and the resulting bytecode is cached
    in the normal manner.  This function does not search a directory
    structure to locate source files; it only compiles files named
    explicitly.  If '-' is the only parameter in args, the list of
    files is taken kutoka standard input.

    """
    ikiwa args is None:
        args = sys.argv[1:]
    rv = 0
    ikiwa args == ['-']:
        while True:
            filename = sys.stdin.readline()
            ikiwa not filename:
                break
            filename = filename.rstrip('\n')
            try:
                compile(filename, doraise=True)
            except PyCompileError as error:
                rv = 1
                ikiwa quiet < 2:
                    sys.stderr.write("%s\n" % error.msg)
            except OSError as error:
                rv = 1
                ikiwa quiet < 2:
                    sys.stderr.write("%s\n" % error)
    else:
        for filename in args:
            try:
                compile(filename, doraise=True)
            except PyCompileError as error:
                # rudisha value to indicate at least one failure
                rv = 1
                ikiwa quiet < 2:
                    sys.stderr.write("%s\n" % error.msg)
    rudisha rv

ikiwa __name__ == "__main__":
    sys.exit(main())
