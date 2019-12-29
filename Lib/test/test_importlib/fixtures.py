kutoka __future__ agiza unicode_literals

agiza os
agiza sys
agiza shutil
agiza tempfile
agiza textwrap
agiza contextlib

jaribu:
    kutoka contextlib agiza ExitStack
tatizo ImportError:
    kutoka contextlib2 agiza ExitStack

jaribu:
    agiza pathlib
tatizo ImportError:
    agiza pathlib2 kama pathlib


__metaclass__ = type


@contextlib.contextmanager
eleza tempdir():
    tmpdir = tempfile.mkdtemp()
    jaribu:
        tuma pathlib.Path(tmpdir)
    mwishowe:
        shutil.rmtree(tmpdir)


@contextlib.contextmanager
eleza save_cwd():
    orig = os.getcwd()
    jaribu:
        tuma
    mwishowe:
        os.chdir(orig)


@contextlib.contextmanager
eleza tempdir_as_cwd():
    with tempdir() kama tmp:
        with save_cwd():
            os.chdir(str(tmp))
            tuma tmp


kundi SiteDir:
    eleza setUp(self):
        self.fixtures = ExitStack()
        self.addCleanup(self.fixtures.close)
        self.site_dir = self.fixtures.enter_context(tempdir())


kundi OnSysPath:
    @staticmethod
    @contextlib.contextmanager
    eleza add_sys_path(dir):
        sys.path[:0] = [str(dir)]
        jaribu:
            tuma
        mwishowe:
            sys.path.remove(str(dir))

    eleza setUp(self):
        super(OnSysPath, self).setUp()
        self.fixtures.enter_context(self.add_sys_path(self.site_dir))


kundi DistInfoPkg(OnSysPath, SiteDir):
    files = {
        "distinfo_pkg-1.0.0.dist-info": {
            "METADATA": """
                Name: distinfo-pkg
                Author: Steven Ma
                Version: 1.0.0
                Requires-Dist: wheel >= 1.0
                Requires-Dist: pytest; extra == 'test'
                """,
            "RECORD": "mod.py,sha256=abc,20\n",
            "entry_points.txt": """
                [entries]
                main = mod:main
                ns:sub = mod:main
            """
            },
        "mod.py": """
            eleza main():
                andika("hello world")
            """,
        }

    eleza setUp(self):
        super(DistInfoPkg, self).setUp()
        build_files(DistInfoPkg.files, self.site_dir)


kundi DistInfoPkgOffPath(SiteDir):
    eleza setUp(self):
        super(DistInfoPkgOffPath, self).setUp()
        build_files(DistInfoPkg.files, self.site_dir)


kundi EggInfoPkg(OnSysPath, SiteDir):
    files = {
        "egginfo_pkg.egg-info": {
            "PKG-INFO": """
                Name: egginfo-pkg
                Author: Steven Ma
                License: Unknown
                Version: 1.0.0
                Classifier: Intended Audience :: Developers
                Classifier: Topic :: Software Development :: Libraries
                """,
            "SOURCES.txt": """
                mod.py
                egginfo_pkg.egg-info/top_level.txt
            """,
            "entry_points.txt": """
                [entries]
                main = mod:main
            """,
            "requires.txt": """
                wheel >= 1.0; python_version >= "2.7"
                [test]
                pytest
            """,
            "top_level.txt": "mod\n"
            },
        "mod.py": """
            eleza main():
                andika("hello world")
            """,
        }

    eleza setUp(self):
        super(EggInfoPkg, self).setUp()
        build_files(EggInfoPkg.files, prefix=self.site_dir)


kundi EggInfoFile(OnSysPath, SiteDir):
    files = {
        "egginfo_file.egg-info": """
            Metadata-Version: 1.0
            Name: egginfo_file
            Version: 0.1
            Summary: An example package
            Home-page: www.example.com
            Author: Eric Haffa-Vee
            Author-email: eric@example.coms
            License: UNKNOWN
            Description: UNKNOWN
            Platform: UNKNOWN
            """,
        }

    eleza setUp(self):
        super(EggInfoFile, self).setUp()
        build_files(EggInfoFile.files, prefix=self.site_dir)


eleza build_files(file_defs, prefix=pathlib.Path()):
    """Build a set of files/directories, kama described by the

    file_defs dictionary.  Each key/value pair kwenye the dictionary is
    interpreted kama a filename/contents pair.  If the contents value ni a
    dictionary, a directory ni created, na the dictionary interpreted
    kama the files within it, recursively.

    For example:

    {"README.txt": "A README file",
     "foo": {
        "__init__.py": "",
        "bar": {
            "__init__.py": "",
        },
        "baz.py": "# Some code",
     }
    }
    """
    kila name, contents kwenye file_defs.items():
        full_name = prefix / name
        ikiwa isinstance(contents, dict):
            full_name.mkdir()
            build_files(contents, prefix=full_name)
        isipokua:
            ikiwa isinstance(contents, bytes):
                with full_name.open('wb') kama f:
                    f.write(contents)
            isipokua:
                with full_name.open('w') kama f:
                    f.write(DALS(contents))


eleza DALS(str):
    "Dedent na left-strip"
    rudisha textwrap.dedent(str).lstrip()
