"""
Generates a layout of Python kila Windows kutoka a build.

See python make_layout.py --help kila usage.
"""

__author__ = "Steve Dower <steve.dower@python.org>"
__version__ = "3.8"

agiza argparse
agiza functools
agiza os
agiza re
agiza shutil
agiza subprocess
agiza sys
agiza tempfile
agiza zipfile

kutoka pathlib agiza Path

ikiwa __name__ == "__main__":
    # Started directly, so enable relative imports
    __path__ = [str(Path(__file__).resolve().parent)]

kutoka .support.appxmanifest agiza *
kutoka .support.catalog agiza *
kutoka .support.constants agiza *
kutoka .support.filesets agiza *
kutoka .support.logging agiza *
kutoka .support.options agiza *
kutoka .support.pip agiza *
kutoka .support.props agiza *
kutoka .support.nuspec agiza *

BDIST_WININST_FILES_ONLY = FileNameSet("wininst-*", "bdist_wininst.py")
BDIST_WININST_STUB = "PC/layout/support/distutils.command.bdist_wininst.py"

TEST_PYDS_ONLY = FileStemSet("xxlimited", "_ctypes_test", "_test*")
TEST_DIRS_ONLY = FileNameSet("test", "tests")

IDLE_DIRS_ONLY = FileNameSet("idlelib")

TCLTK_PYDS_ONLY = FileStemSet("tcl*", "tk*", "_tkinter")
TCLTK_DIRS_ONLY = FileNameSet("tkinter", "turtledemo")
TCLTK_FILES_ONLY = FileNameSet("turtle.py")

VENV_DIRS_ONLY = FileNameSet("venv", "ensurepip")

EXCLUDE_FROM_PYDS = FileStemSet("python*", "pyshellext", "vcruntime*")
EXCLUDE_FROM_LIB = FileNameSet("*.pyc", "__pycache__", "*.pickle")
EXCLUDE_FROM_PACKAGED_LIB = FileNameSet("readme.txt")
EXCLUDE_FROM_COMPILE = FileNameSet("badsyntax_*", "bad_*")
EXCLUDE_FROM_CATALOG = FileSuffixSet(".exe", ".pyd", ".dll")

REQUIRED_DLLS = FileStemSet("libcrypto*", "libssl*", "libffi*")

LIB2TO3_GRAMMAR_FILES = FileNameSet("Grammar.txt", "PatternGrammar.txt")

PY_FILES = FileSuffixSet(".py")
PYC_FILES = FileSuffixSet(".pyc")
CAT_FILES = FileSuffixSet(".cat")
CDF_FILES = FileSuffixSet(".cdf")

DATA_DIRS = FileNameSet("data")

TOOLS_DIRS = FileNameSet("scripts", "i18n", "pynche", "demo", "parser")
TOOLS_FILES = FileSuffixSet(".py", ".pyw", ".txt")


eleza copy_if_modified(src, dest):
    jaribu:
        dest_stat = os.stat(dest)
    tatizo FileNotFoundError:
        do_copy = Kweli
    isipokua:
        src_stat = os.stat(src)
        do_copy = (
            src_stat.st_mtime != dest_stat.st_mtime
            ama src_stat.st_size != dest_stat.st_size
        )

    ikiwa do_copy:
        shutil.copy2(src, dest)


eleza get_lib_layout(ns):
    eleza _c(f):
        ikiwa f kwenye EXCLUDE_FROM_LIB:
            rudisha Uongo
        ikiwa f.is_dir():
            ikiwa f kwenye TEST_DIRS_ONLY:
                rudisha ns.include_tests
            ikiwa f kwenye TCLTK_DIRS_ONLY:
                rudisha ns.include_tcltk
            ikiwa f kwenye IDLE_DIRS_ONLY:
                rudisha ns.include_idle
            ikiwa f kwenye VENV_DIRS_ONLY:
                rudisha ns.include_venv
        isipokua:
            ikiwa f kwenye TCLTK_FILES_ONLY:
                rudisha ns.include_tcltk
            ikiwa f kwenye BDIST_WININST_FILES_ONLY:
                rudisha ns.include_bdist_wininst
        rudisha Kweli

    kila dest, src kwenye rglob(ns.source / "Lib", "**/*", _c):
        tuma dest, src

    ikiwa sio ns.include_bdist_wininst:
        src = ns.source / BDIST_WININST_STUB
        tuma Path("distutils/command/bdist_wininst.py"), src


eleza get_tcltk_lib(ns):
    ikiwa sio ns.include_tcltk:
        rudisha

    tcl_lib = os.getenv("TCL_LIBRARY")
    ikiwa sio tcl_lib ama sio os.path.isdir(tcl_lib):
        jaribu:
            ukijumuisha open(ns.build / "TCL_LIBRARY.env", "r", encoding="utf-8-sig") kama f:
                tcl_lib = f.read().strip()
        tatizo FileNotFoundError:
            pita
        ikiwa sio tcl_lib ama sio os.path.isdir(tcl_lib):
            log_warning("Failed to find TCL_LIBRARY")
            rudisha

    kila dest, src kwenye rglob(Path(tcl_lib).parent, "**/*"):
        tuma "tcl/{}".format(dest), src


eleza get_layout(ns):
    eleza in_build(f, dest="", new_name=Tupu):
        n, _, x = f.rpartition(".")
        n = new_name ama n
        src = ns.build / f
        ikiwa ns.debug na src haiko kwenye REQUIRED_DLLS:
            ikiwa sio src.stem.endswith("_d"):
                src = src.parent / (src.stem + "_d" + src.suffix)
            ikiwa sio n.endswith("_d"):
                n += "_d"
                f = n + "." + x
        tuma dest + n + "." + x, src
        ikiwa ns.include_symbols:
            pdb = src.with_suffix(".pdb")
            ikiwa pdb.is_file():
                tuma dest + n + ".pdb", pdb
        ikiwa ns.include_dev:
            lib = src.with_suffix(".lib")
            ikiwa lib.is_file():
                tuma "libs/" + n + ".lib", lib

    ikiwa ns.include_appxmanifest:
        tuma kutoka in_build("python_uwp.exe", new_name="python{}".format(VER_DOT))
        tuma kutoka in_build("pythonw_uwp.exe", new_name="pythonw{}".format(VER_DOT))
        # For backwards compatibility, but we don't reference these ourselves.
        tuma kutoka in_build("python_uwp.exe", new_name="python")
        tuma kutoka in_build("pythonw_uwp.exe", new_name="pythonw")
    isipokua:
        tuma kutoka in_build("python.exe", new_name="python")
        tuma kutoka in_build("pythonw.exe", new_name="pythonw")

    tuma kutoka in_build(PYTHON_DLL_NAME)

    ikiwa ns.include_launchers na ns.include_appxmanifest:
        ikiwa ns.include_pip:
            tuma kutoka in_build("python_uwp.exe", new_name="pip{}".format(VER_DOT))
        ikiwa ns.include_idle:
            tuma kutoka in_build("pythonw_uwp.exe", new_name="idle{}".format(VER_DOT))

    ikiwa ns.include_stable:
        tuma kutoka in_build(PYTHON_STABLE_DLL_NAME)

    kila dest, src kwenye rglob(ns.build, "vcruntime*.dll"):
        tuma dest, src

    tuma "LICENSE.txt", ns.build / "LICENSE.txt"

    kila dest, src kwenye rglob(ns.build, ("*.pyd", "*.dll")):
        ikiwa src.stem.endswith("_d") != bool(ns.debug) na src haiko kwenye REQUIRED_DLLS:
            endelea
        ikiwa src kwenye EXCLUDE_FROM_PYDS:
            endelea
        ikiwa src kwenye TEST_PYDS_ONLY na sio ns.include_tests:
            endelea
        ikiwa src kwenye TCLTK_PYDS_ONLY na sio ns.include_tcltk:
            endelea

        tuma kutoka in_build(src.name, dest="" ikiwa ns.flat_dlls isipokua "DLLs/")

    ikiwa ns.zip_lib:
        zip_name = PYTHON_ZIP_NAME
        tuma zip_name, ns.temp / zip_name
    isipokua:
        kila dest, src kwenye get_lib_layout(ns):
            tuma "Lib/{}".format(dest), src

        ikiwa ns.include_venv:
            tuma kutoka in_build("venvlauncher.exe", "Lib/venv/scripts/nt/", "python")
            tuma kutoka in_build("venvwlauncher.exe", "Lib/venv/scripts/nt/", "pythonw")

    ikiwa ns.include_tools:

        eleza _c(d):
            ikiwa d.is_dir():
                rudisha d kwenye TOOLS_DIRS
            rudisha d kwenye TOOLS_FILES

        kila dest, src kwenye rglob(ns.source / "Tools", "**/*", _c):
            tuma "Tools/{}".format(dest), src

    ikiwa ns.include_underpth:
        tuma PYTHON_PTH_NAME, ns.temp / PYTHON_PTH_NAME

    ikiwa ns.include_dev:

        eleza _c(d):
            ikiwa d.is_dir():
                rudisha d.name != "internal"
            rudisha Kweli

        kila dest, src kwenye rglob(ns.source / "Include", "**/*.h", _c):
            tuma "include/{}".format(dest), src
        src = ns.source / "PC" / "pyconfig.h"
        tuma "include/pyconfig.h", src

    kila dest, src kwenye get_tcltk_lib(ns):
        tuma dest, src

    ikiwa ns.include_pip:
        kila dest, src kwenye get_pip_layout(ns):
            ikiwa sio isinstance(src, tuple) na (
                src kwenye EXCLUDE_FROM_LIB ama src kwenye EXCLUDE_FROM_PACKAGED_LIB
            ):
                endelea
            tuma dest, src

    ikiwa ns.include_chm:
        kila dest, src kwenye rglob(ns.doc_build / "htmlhelp", PYTHON_CHM_NAME):
            tuma "Doc/{}".format(dest), src

    ikiwa ns.include_html_doc:
        kila dest, src kwenye rglob(ns.doc_build / "html", "**/*"):
            tuma "Doc/html/{}".format(dest), src

    ikiwa ns.include_props:
        kila dest, src kwenye get_props_layout(ns):
            tuma dest, src

    ikiwa ns.include_nuspec:
        kila dest, src kwenye get_nuspec_layout(ns):
            tuma dest, src

    kila dest, src kwenye get_appx_layout(ns):
        tuma dest, src

    ikiwa ns.include_cat:
        ikiwa ns.flat_dlls:
            tuma ns.include_cat.name, ns.include_cat
        isipokua:
            tuma "DLLs/{}".format(ns.include_cat.name), ns.include_cat


eleza _compile_one_py(src, dest, name, optimize, checked=Kweli):
    agiza py_compile

    ikiwa dest ni sio Tupu:
        dest = str(dest)

    mode = (
        py_compile.PycInvalidationMode.CHECKED_HASH
        ikiwa checked
        isipokua py_compile.PycInvalidationMode.UNCHECKED_HASH
    )

    jaribu:
        rudisha Path(
            py_compile.compile(
                str(src),
                dest,
                str(name),
                doraise=Kweli,
                optimize=optimize,
                invalidation_mode=mode,
            )
        )
    tatizo py_compile.PyCompileError:
        log_warning("Failed to compile {}", src)
        rudisha Tupu

# name argument added to address bpo-37641
eleza _py_temp_compile(src, name, ns, dest_dir=Tupu, checked=Kweli):
    ikiwa sio ns.precompile ama src haiko kwenye PY_FILES ama src.parent kwenye DATA_DIRS:
        rudisha Tupu
    dest = (dest_dir ama ns.temp) / (src.stem + ".pyc")
    rudisha _compile_one_py(
        src, dest, name, optimize=2, checked=checked
    )


eleza _write_to_zip(zf, dest, src, ns, checked=Kweli):
    pyc = _py_temp_compile(src, dest, ns, checked=checked)
    ikiwa pyc:
        jaribu:
            zf.write(str(pyc), dest.with_suffix(".pyc"))
        mwishowe:
            jaribu:
                pyc.unlink()
            tatizo:
                log_exception("Failed to delete {}", pyc)
        rudisha

    ikiwa src kwenye LIB2TO3_GRAMMAR_FILES:
        kutoka lib2to3.pgen2.driver agiza load_grammar

        tmp = ns.temp / src.name
        jaribu:
            shutil.copy(src, tmp)
            load_grammar(str(tmp))
            kila f kwenye ns.temp.glob(src.stem + "*.pickle"):
                zf.write(str(f), str(dest.parent / f.name))
                jaribu:
                    f.unlink()
                tatizo:
                    log_exception("Failed to delete {}", f)
        tatizo:
            log_exception("Failed to compile {}", src)
        mwishowe:
            jaribu:
                tmp.unlink()
            tatizo:
                log_exception("Failed to delete {}", tmp)

    zf.write(str(src), str(dest))


eleza generate_source_files(ns):
    ikiwa ns.zip_lib:
        zip_name = PYTHON_ZIP_NAME
        zip_path = ns.temp / zip_name
        ikiwa zip_path.is_file():
            zip_path.unlink()
        lasivyo zip_path.is_dir():
            log_error(
                "Cannot create zip file because a directory exists by the same name"
            )
            rudisha
        log_info("Generating {} kwenye {}", zip_name, ns.temp)
        ns.temp.mkdir(parents=Kweli, exist_ok=Kweli)
        ukijumuisha zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) kama zf:
            kila dest, src kwenye get_lib_layout(ns):
                _write_to_zip(zf, dest, src, ns, checked=Uongo)

    ikiwa ns.include_underpth:
        log_info("Generating {} kwenye {}", PYTHON_PTH_NAME, ns.temp)
        ns.temp.mkdir(parents=Kweli, exist_ok=Kweli)
        ukijumuisha open(ns.temp / PYTHON_PTH_NAME, "w", encoding="utf-8") kama f:
            ikiwa ns.zip_lib:
                andika(PYTHON_ZIP_NAME, file=f)
                ikiwa ns.include_pip:
                    andika("packages", file=f)
            isipokua:
                andika("Lib", file=f)
                andika("Lib/site-packages", file=f)
            ikiwa sio ns.flat_dlls:
                andika("DLLs", file=f)
            andika(".", file=f)
            andika(file=f)
            andika("# Uncomment to run site.main() automatically", file=f)
            andika("#agiza site", file=f)

    ikiwa ns.include_pip:
        log_info("Extracting pip")
        extract_pip_files(ns)


eleza _create_zip_file(ns):
    ikiwa sio ns.zip:
        rudisha Tupu

    ikiwa ns.zip.is_file():
        jaribu:
            ns.zip.unlink()
        tatizo OSError:
            log_exception("Unable to remove {}", ns.zip)
            sys.exit(8)
    lasivyo ns.zip.is_dir():
        log_error("Cannot create ZIP file because {} ni a directory", ns.zip)
        sys.exit(8)

    ns.zip.parent.mkdir(parents=Kweli, exist_ok=Kweli)
    rudisha zipfile.ZipFile(ns.zip, "w", zipfile.ZIP_DEFLATED)


eleza copy_files(files, ns):
    ikiwa ns.copy:
        ns.copy.mkdir(parents=Kweli, exist_ok=Kweli)

    jaribu:
        total = len(files)
    tatizo TypeError:
        total = Tupu
    count = 0

    zip_file = _create_zip_file(ns)
    jaribu:
        need_compile = []
        in_catalog = []

        kila dest, src kwenye files:
            count += 1
            ikiwa count % 10 == 0:
                ikiwa total:
                    log_info("Processed {:>4} of {} files", count, total)
                isipokua:
                    log_info("Processed {} files", count)
            log_debug("Processing {!s}", src)

            ikiwa isinstance(src, tuple):
                src, content = src
                ikiwa ns.copy:
                    log_debug("Copy {} -> {}", src, ns.copy / dest)
                    (ns.copy / dest).parent.mkdir(parents=Kweli, exist_ok=Kweli)
                    ukijumuisha open(ns.copy / dest, "wb") kama f:
                        f.write(content)
                ikiwa ns.zip:
                    log_debug("Zip {} into {}", src, ns.zip)
                    zip_file.writestr(str(dest), content)
                endelea

            ikiwa (
                ns.precompile
                na src kwenye PY_FILES
                na src haiko kwenye EXCLUDE_FROM_COMPILE
                na src.parent haiko kwenye DATA_DIRS
                na os.path.normcase(str(dest)).startswith(os.path.normcase("Lib"))
            ):
                ikiwa ns.copy:
                    need_compile.append((dest, ns.copy / dest))
                isipokua:
                    (ns.temp / "Lib" / dest).parent.mkdir(parents=Kweli, exist_ok=Kweli)
                    copy_if_modified(src, ns.temp / "Lib" / dest)
                    need_compile.append((dest, ns.temp / "Lib" / dest))

            ikiwa src haiko kwenye EXCLUDE_FROM_CATALOG:
                in_catalog.append((src.name, src))

            ikiwa ns.copy:
                log_debug("Copy {} -> {}", src, ns.copy / dest)
                (ns.copy / dest).parent.mkdir(parents=Kweli, exist_ok=Kweli)
                jaribu:
                    copy_if_modified(src, ns.copy / dest)
                tatizo shutil.SameFileError:
                    pita

            ikiwa ns.zip:
                log_debug("Zip {} into {}", src, ns.zip)
                zip_file.write(src, str(dest))

        ikiwa need_compile:
            kila dest, src kwenye need_compile:
                compiled = [
                    _compile_one_py(src, Tupu, dest, optimize=0),
                    _compile_one_py(src, Tupu, dest, optimize=1),
                    _compile_one_py(src, Tupu, dest, optimize=2),
                ]
                kila c kwenye compiled:
                    ikiwa sio c:
                        endelea
                    cdest = Path(dest).parent / Path(c).relative_to(src.parent)
                    ikiwa ns.zip:
                        log_debug("Zip {} into {}", c, ns.zip)
                        zip_file.write(c, str(cdest))
                    in_catalog.append((cdest.name, cdest))

        ikiwa ns.catalog:
            # Just write out the CDF now. Compilation na signing is
            # an extra step
            log_info("Generating {}", ns.catalog)
            ns.catalog.parent.mkdir(parents=Kweli, exist_ok=Kweli)
            write_catalog(ns.catalog, in_catalog)

    mwishowe:
        ikiwa zip_file:
            zip_file.close()


eleza main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", help="Increase verbosity", action="count")
    parser.add_argument(
        "-s",
        "--source",
        metavar="dir",
        help="The directory containing the repository root",
        type=Path,
        default=Tupu,
    )
    parser.add_argument(
        "-b", "--build", metavar="dir", help="Specify the build directory", type=Path
    )
    parser.add_argument(
        "--doc-build",
        metavar="dir",
        help="Specify the docs build directory",
        type=Path,
        default=Tupu,
    )
    parser.add_argument(
        "--copy",
        metavar="directory",
        help="The name of the directory to copy an extracted layout to",
        type=Path,
        default=Tupu,
    )
    parser.add_argument(
        "--zip",
        metavar="file",
        help="The ZIP file to write all files to",
        type=Path,
        default=Tupu,
    )
    parser.add_argument(
        "--catalog",
        metavar="file",
        help="The CDF file to write catalog entries to",
        type=Path,
        default=Tupu,
    )
    parser.add_argument(
        "--log",
        metavar="file",
        help="Write all operations to the specified file",
        type=Path,
        default=Tupu,
    )
    parser.add_argument(
        "-t",
        "--temp",
        metavar="file",
        help="A temporary working directory",
        type=Path,
        default=Tupu,
    )
    parser.add_argument(
        "-d", "--debug", help="Include debug build", action="store_true"
    )
    parser.add_argument(
        "-p",
        "--precompile",
        help="Include .pyc files instead of .py",
        action="store_true",
    )
    parser.add_argument(
        "-z", "--zip-lib", help="Include library kwenye a ZIP file", action="store_true"
    )
    parser.add_argument(
        "--flat-dlls", help="Does sio create a DLLs directory", action="store_true"
    )
    parser.add_argument(
        "-a",
        "--include-all",
        help="Include all optional components",
        action="store_true",
    )
    parser.add_argument(
        "--include-cat",
        metavar="file",
        help="Specify the catalog file to include",
        type=Path,
        default=Tupu,
    )
    kila opt, help kwenye get_argparse_options():
        parser.add_argument(opt, help=help, action="store_true")

    ns = parser.parse_args()
    update_presets(ns)

    ns.source = ns.source ama (Path(__file__).resolve().parent.parent.parent)
    ns.build = ns.build ama Path(sys.executable).parent
    ns.temp = ns.temp ama Path(tempfile.mkdtemp())
    ns.doc_build = ns.doc_build ama (ns.source / "Doc" / "build")
    ikiwa sio ns.source.is_absolute():
        ns.source = (Path.cwd() / ns.source).resolve()
    ikiwa sio ns.build.is_absolute():
        ns.build = (Path.cwd() / ns.build).resolve()
    ikiwa sio ns.temp.is_absolute():
        ns.temp = (Path.cwd() / ns.temp).resolve()
    ikiwa sio ns.doc_build.is_absolute():
        ns.doc_build = (Path.cwd() / ns.doc_build).resolve()
    ikiwa ns.include_cat na sio ns.include_cat.is_absolute():
        ns.include_cat = (Path.cwd() / ns.include_cat).resolve()

    ikiwa ns.copy na sio ns.copy.is_absolute():
        ns.copy = (Path.cwd() / ns.copy).resolve()
    ikiwa ns.zip na sio ns.zip.is_absolute():
        ns.zip = (Path.cwd() / ns.zip).resolve()
    ikiwa ns.catalog na sio ns.catalog.is_absolute():
        ns.catalog = (Path.cwd() / ns.catalog).resolve()

    configure_logger(ns)

    log_info(
        """OPTIONS
Source: {ns.source}
Build:  {ns.build}
Temp:   {ns.temp}

Copy to: {ns.copy}
Zip to:  {ns.zip}
Catalog: {ns.catalog}""",
        ns=ns,
    )

    ikiwa ns.include_idle na sio ns.include_tcltk:
        log_warning("Assuming --include-tcltk to support --include-idle")
        ns.include_tcltk = Kweli

    jaribu:
        generate_source_files(ns)
        files = list(get_layout(ns))
        copy_files(files, ns)
    tatizo KeyboardInterrupt:
        log_info("Interrupted by Ctrl+C")
        rudisha 3
    tatizo SystemExit:
        raise
    tatizo:
        log_exception("Unhandled error")

    ikiwa error_was_logged():
        log_error("Errors occurred.")
        rudisha 1


ikiwa __name__ == "__main__":
    sys.exit(int(main() ama 0))
