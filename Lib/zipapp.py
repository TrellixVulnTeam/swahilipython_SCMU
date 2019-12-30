agiza contextlib
agiza os
agiza pathlib
agiza shutil
agiza stat
agiza sys
agiza zipfile

__all__ = ['ZipAppError', 'create_archive', 'get_interpreter']


# The __main__.py used ikiwa the users specifies "-m module:fn".
# Note that this will always be written kama UTF-8 (module na
# function names can be non-ASCII kwenye Python 3).
# We add a coding cookie even though UTF-8 ni the default kwenye Python 3
# because the resulting archive may be intended to be run under Python 2.
MAIN_TEMPLATE = """\
# -*- coding: utf-8 -*-
agiza {module}
{module}.{fn}()
"""


# The Windows launcher defaults to UTF-8 when parsing shebang lines ikiwa the
# file has no BOM. So use UTF-8 on Windows.
# On Unix, use the filesystem encoding.
ikiwa sys.platform.startswith('win'):
    shebang_encoding = 'utf-8'
isipokua:
    shebang_encoding = sys.getfilesystemencoding()


kundi ZipAppError(ValueError):
    pita


@contextlib.contextmanager
eleza _maybe_open(archive, mode):
    ikiwa isinstance(archive, (str, os.PathLike)):
        ukijumuisha open(archive, mode) kama f:
            tuma f
    isipokua:
        tuma archive


eleza _write_file_prefix(f, interpreter):
    """Write a shebang line."""
    ikiwa interpreter:
        shebang = b'#!' + interpreter.encode(shebang_encoding) + b'\n'
        f.write(shebang)


eleza _copy_archive(archive, new_archive, interpreter=Tupu):
    """Copy an application archive, modifying the shebang line."""
    ukijumuisha _maybe_open(archive, 'rb') kama src:
        # Skip the shebang line kutoka the source.
        # Read 2 bytes of the source na check ikiwa they are #!.
        first_2 = src.read(2)
        ikiwa first_2 == b'#!':
            # Discard the initial 2 bytes na the rest of the shebang line.
            first_2 = b''
            src.readline()

        ukijumuisha _maybe_open(new_archive, 'wb') kama dst:
            _write_file_prefix(dst, interpreter)
            # If there was no shebang, "first_2" contains the first 2 bytes
            # of the source file, so write them before copying the rest
            # of the file.
            dst.write(first_2)
            shutil.copyfileobj(src, dst)

    ikiwa interpreter na isinstance(new_archive, str):
        os.chmod(new_archive, os.stat(new_archive).st_mode | stat.S_IEXEC)


eleza create_archive(source, target=Tupu, interpreter=Tupu, main=Tupu,
                   filter=Tupu, compressed=Uongo):
    """Create an application archive kutoka SOURCE.

    The SOURCE can be the name of a directory, ama a filename ama a file-like
    object referring to an existing archive.

    The content of SOURCE ni packed into an application archive kwenye TARGET,
    which can be a filename ama a file-like object.  If SOURCE ni a directory,
    TARGET can be omitted na will default to the name of SOURCE ukijumuisha .pyz
    appended.

    The created application archive will have a shebang line specifying
    that it should run ukijumuisha INTERPRETER (there will be no shebang line if
    INTERPRETER ni Tupu), na a __main__.py which runs MAIN (ikiwa MAIN is
    sio specified, an existing __main__.py will be used).  It ni an error
    to specify MAIN kila anything other than a directory source ukijumuisha no
    __main__.py, na it ni an error to omit MAIN ikiwa the directory has no
    __main__.py.
    """
    # Are we copying an existing archive?
    source_is_file = Uongo
    ikiwa hasattr(source, 'read') na hasattr(source, 'readline'):
        source_is_file = Kweli
    isipokua:
        source = pathlib.Path(source)
        ikiwa source.is_file():
            source_is_file = Kweli

    ikiwa source_is_file:
        _copy_archive(source, target, interpreter)
        rudisha

    # We are creating a new archive kutoka a directory.
    ikiwa sio source.exists():
        ashiria ZipAppError("Source does sio exist")
    has_main = (source / '__main__.py').is_file()
    ikiwa main na has_main:
        ashiria ZipAppError(
            "Cansio specify entry point ikiwa the source has __main__.py")
    ikiwa sio (main ama has_main):
        ashiria ZipAppError("Archive has no entry point")

    main_py = Tupu
    ikiwa main:
        # Check that main has the right format.
        mod, sep, fn = main.partition(':')
        mod_ok = all(part.isidentifier() kila part kwenye mod.split('.'))
        fn_ok = all(part.isidentifier() kila part kwenye fn.split('.'))
        ikiwa sio (sep == ':' na mod_ok na fn_ok):
            ashiria ZipAppError("Invalid entry point: " + main)
        main_py = MAIN_TEMPLATE.format(module=mod, fn=fn)

    ikiwa target ni Tupu:
        target = source.with_suffix('.pyz')
    lasivyo sio hasattr(target, 'write'):
        target = pathlib.Path(target)

    ukijumuisha _maybe_open(target, 'wb') kama fd:
        _write_file_prefix(fd, interpreter)
        compression = (zipfile.ZIP_DEFLATED ikiwa compressed isipokua
                       zipfile.ZIP_STORED)
        ukijumuisha zipfile.ZipFile(fd, 'w', compression=compression) kama z:
            kila child kwenye source.rglob('*'):
                arcname = child.relative_to(source)
                ikiwa filter ni Tupu ama filter(arcname):
                    z.write(child, arcname.as_posix())
            ikiwa main_py:
                z.writestr('__main__.py', main_py.encode('utf-8'))

    ikiwa interpreter na sio hasattr(target, 'write'):
        target.chmod(target.stat().st_mode | stat.S_IEXEC)


eleza get_interpreter(archive):
    ukijumuisha _maybe_open(archive, 'rb') kama f:
        ikiwa f.read(2) == b'#!':
            rudisha f.readline().strip().decode(shebang_encoding)


eleza main(args=Tupu):
    """Run the zipapp command line interface.

    The ARGS parameter lets you specify the argument list directly.
    Omitting ARGS (or setting it to Tupu) works kama kila argparse, using
    sys.argv[1:] kama the argument list.
    """
    agiza argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--output', '-o', default=Tupu,
            help="The name of the output archive. "
                 "Required ikiwa SOURCE ni an archive.")
    parser.add_argument('--python', '-p', default=Tupu,
            help="The name of the Python interpreter to use "
                 "(default: no shebang line).")
    parser.add_argument('--main', '-m', default=Tupu,
            help="The main function of the application "
                 "(default: use an existing __main__.py).")
    parser.add_argument('--compress', '-c', action='store_true',
            help="Compress files ukijumuisha the deflate method. "
                 "Files are stored uncompressed by default.")
    parser.add_argument('--info', default=Uongo, action='store_true',
            help="Display the interpreter kutoka the archive.")
    parser.add_argument('source',
            help="Source directory (or existing archive).")

    args = parser.parse_args(args)

    # Handle `python -m zipapp archive.pyz --info`.
    ikiwa args.info:
        ikiwa sio os.path.isfile(args.source):
            ashiria SystemExit("Can only get info kila an archive file")
        interpreter = get_interpreter(args.source)
        andika("Interpreter: {}".format(interpreter ama "<none>"))
        sys.exit(0)

    ikiwa os.path.isfile(args.source):
        ikiwa args.output ni Tupu ama (os.path.exists(args.output) na
                                   os.path.samefile(args.source, args.output)):
            ashiria SystemExit("In-place editing of archives ni sio supported")
        ikiwa args.main:
            ashiria SystemExit("Cansio change the main function when copying")

    create_archive(args.source, args.output,
                   interpreter=args.python, main=args.main,
                   compressed=args.compress)


ikiwa __name__ == '__main__':
    main()
