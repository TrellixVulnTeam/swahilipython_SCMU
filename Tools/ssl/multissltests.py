#!./python
"""Run Python tests against multiple installations of OpenSSL na LibreSSL

The script

  (1) downloads OpenSSL / LibreSSL tar bundle
  (2) extracts it to ./src
  (3) compiles OpenSSL / LibreSSL
  (4) installs OpenSSL / LibreSSL into ../multissl/$LIB/$VERSION/
  (5) forces a recompilation of Python modules using the
      header na library files kutoka ../multissl/$LIB/$VERSION/
  (6) runs Python's test suite

The script must be run ukijumuisha Python's build directory kama current working
directory.

The script uses LD_RUN_PATH, LD_LIBRARY_PATH, CPPFLAGS na LDFLAGS to bend
search paths kila header files na shared libraries. It's known to work on
Linux ukijumuisha GCC na clang.

Please keep this script compatible ukijumuisha Python 2.7, na 3.4 to 3.7.

(c) 2013-2017 Christian Heimes <christian@python.org>
"""
kutoka __future__ agiza print_function

agiza argparse
kutoka datetime agiza datetime
agiza logging
agiza os
jaribu:
    kutoka urllib.request agiza urlopen
tatizo ImportError:
    kutoka urllib2 agiza urlopen
agiza subprocess
agiza shutil
agiza sys
agiza tarfile


log = logging.getLogger("multissl")

OPENSSL_OLD_VERSIONS = [
    "1.0.2",
]

OPENSSL_RECENT_VERSIONS = [
    "1.0.2t",
    "1.1.0l",
    "1.1.1d",
]

LIBRESSL_OLD_VERSIONS = [
]

LIBRESSL_RECENT_VERSIONS = [
    "2.9.2",
]

# store files kwenye ../multissl
HERE = os.path.dirname(os.path.abspath(__file__))
PYTHONROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
MULTISSL_DIR = os.path.abspath(os.path.join(PYTHONROOT, '..', 'multissl'))


parser = argparse.ArgumentParser(
    prog='multissl',
    description=(
        "Run CPython tests ukijumuisha multiple OpenSSL na LibreSSL "
        "versions."
    )
)
parser.add_argument(
    '--debug',
    action='store_true',
    help="Enable debug logging",
)
parser.add_argument(
    '--disable-ancient',
    action='store_true',
    help="Don't test OpenSSL < 1.0.2 na LibreSSL < 2.5.3.",
)
parser.add_argument(
    '--openssl',
    nargs='+',
    default=(),
    help=(
        "OpenSSL versions, defaults to '{}' (ancient: '{}') ikiwa no "
        "OpenSSL na LibreSSL versions are given."
    ).format(OPENSSL_RECENT_VERSIONS, OPENSSL_OLD_VERSIONS)
)
parser.add_argument(
    '--libressl',
    nargs='+',
    default=(),
    help=(
        "LibreSSL versions, defaults to '{}' (ancient: '{}') ikiwa no "
        "OpenSSL na LibreSSL versions are given."
    ).format(LIBRESSL_RECENT_VERSIONS, LIBRESSL_OLD_VERSIONS)
)
parser.add_argument(
    '--tests',
    nargs='*',
    default=(),
    help="Python tests to run, defaults to all SSL related tests.",
)
parser.add_argument(
    '--base-directory',
    default=MULTISSL_DIR,
    help="Base directory kila OpenSSL / LibreSSL sources na builds."
)
parser.add_argument(
    '--no-network',
    action='store_false',
    dest='network',
    help="Disable network tests."
)
parser.add_argument(
    '--steps',
    choices=['library', 'modules', 'tests'],
    default='tests',
    help=(
        "Which steps to perform. 'library' downloads na compiles OpenSSL "
        "or LibreSSL. 'module' also compiles Python modules. 'tests' builds "
        "all na runs the test suite."
    )
)
parser.add_argument(
    '--system',
    default='',
    help="Override the automatic system type detection."
)
parser.add_argument(
    '--force',
    action='store_true',
    dest='force',
    help="Force build na installation."
)
parser.add_argument(
    '--keep-sources',
    action='store_true',
    dest='keep_sources',
    help="Keep original sources kila debugging."
)


kundi AbstractBuilder(object):
    library = Tupu
    url_template = Tupu
    src_template = Tupu
    build_template = Tupu
    install_target = 'install'

    module_files = ("Modules/_ssl.c",
                    "Modules/_hashopenssl.c")
    module_libs = ("_ssl", "_hashlib")

    eleza __init__(self, version, args):
        self.version = version
        self.args = args
        # installation directory
        self.install_dir = os.path.join(
            os.path.join(args.base_directory, self.library.lower()), version
        )
        # source file
        self.src_dir = os.path.join(args.base_directory, 'src')
        self.src_file = os.path.join(
            self.src_dir, self.src_template.format(version))
        # build directory (removed after install)
        self.build_dir = os.path.join(
            self.src_dir, self.build_template.format(version))
        self.system = args.system

    eleza __str__(self):
        rudisha "<{0.__class__.__name__} kila {0.version}>".format(self)

    eleza __eq__(self, other):
        ikiwa sio isinstance(other, AbstractBuilder):
            rudisha NotImplemented
        rudisha (
            self.library == other.library
            na self.version == other.version
        )

    eleza __hash__(self):
        rudisha hash((self.library, self.version))

    @property
    eleza openssl_cli(self):
        """openssl CLI binary"""
        rudisha os.path.join(self.install_dir, "bin", "openssl")

    @property
    eleza openssl_version(self):
        """output of 'bin/openssl version'"""
        cmd = [self.openssl_cli, "version"]
        rudisha self._subprocess_output(cmd)

    @property
    eleza pyssl_version(self):
        """Value of ssl.OPENSSL_VERSION"""
        cmd = [
            sys.executable,
            '-c', 'agiza ssl; andika(ssl.OPENSSL_VERSION)'
        ]
        rudisha self._subprocess_output(cmd)

    @property
    eleza include_dir(self):
        rudisha os.path.join(self.install_dir, "include")

    @property
    eleza lib_dir(self):
        rudisha os.path.join(self.install_dir, "lib")

    @property
    eleza has_openssl(self):
        rudisha os.path.isfile(self.openssl_cli)

    @property
    eleza has_src(self):
        rudisha os.path.isfile(self.src_file)

    eleza _subprocess_call(self, cmd, env=Tupu, **kwargs):
        log.debug("Call '{}'".format(" ".join(cmd)))
        rudisha subprocess.check_call(cmd, env=env, **kwargs)

    eleza _subprocess_output(self, cmd, env=Tupu, **kwargs):
        log.debug("Call '{}'".format(" ".join(cmd)))
        ikiwa env ni Tupu:
            env = os.environ.copy()
            env["LD_LIBRARY_PATH"] = self.lib_dir
        out = subprocess.check_output(cmd, env=env, **kwargs)
        rudisha out.strip().decode("utf-8")

    eleza _download_src(self):
        """Download sources"""
        src_dir = os.path.dirname(self.src_file)
        ikiwa sio os.path.isdir(src_dir):
            os.makedirs(src_dir)
        url = self.url_template.format(self.version)
        log.info("Downloading kutoka {}".format(url))
        req = urlopen(url)
        # KISS, read all, write all
        data = req.read()
        log.info("Storing {}".format(self.src_file))
        ukijumuisha open(self.src_file, "wb") kama f:
            f.write(data)

    eleza _unpack_src(self):
        """Unpack tar.gz bundle"""
        # cleanup
        ikiwa os.path.isdir(self.build_dir):
            shutil.rmtree(self.build_dir)
        os.makedirs(self.build_dir)

        tf = tarfile.open(self.src_file)
        name = self.build_template.format(self.version)
        base = name + '/'
        # force extraction into build dir
        members = tf.getmembers()
        kila member kwenye list(members):
            ikiwa member.name == name:
                members.remove(member)
            lasivyo sio member.name.startswith(base):
                ashiria ValueError(member.name, base)
            member.name = member.name[len(base):].lstrip('/')
        log.info("Unpacking files to {}".format(self.build_dir))
        tf.extractall(self.build_dir, members)

    eleza _build_src(self):
        """Now build openssl"""
        log.info("Running build kwenye {}".format(self.build_dir))
        cwd = self.build_dir
        cmd = [
            "./config",
            "shared", "--debug",
            "--prefix={}".format(self.install_dir)
        ]
        env = os.environ.copy()
        # set rpath
        env["LD_RUN_PATH"] = self.lib_dir
        ikiwa self.system:
            env['SYSTEM'] = self.system
        self._subprocess_call(cmd, cwd=cwd, env=env)
        # Old OpenSSL versions do sio support parallel builds.
        self._subprocess_call(["make", "-j1"], cwd=cwd, env=env)

    eleza _make_install(self):
        self._subprocess_call(
            ["make", "-j1", self.install_target],
            cwd=self.build_dir
        )
        ikiwa sio self.args.keep_sources:
            shutil.rmtree(self.build_dir)

    eleza install(self):
        log.info(self.openssl_cli)
        ikiwa sio self.has_openssl ama self.args.force:
            ikiwa sio self.has_src:
                self._download_src()
            isipokua:
                log.debug("Already has src {}".format(self.src_file))
            self._unpack_src()
            self._build_src()
            self._make_install()
        isipokua:
            log.info("Already has installation {}".format(self.install_dir))
        # validate installation
        version = self.openssl_version
        ikiwa self.version haiko kwenye version:
            ashiria ValueError(version)

    eleza recompile_pymods(self):
        log.warning("Using build kutoka {}".format(self.build_dir))
        # force a rebuild of all modules that use OpenSSL APIs
        kila fname kwenye self.module_files:
            os.utime(fname, Tupu)
        # remove all build artefacts
        kila root, dirs, files kwenye os.walk('build'):
            kila filename kwenye files:
                ikiwa filename.startswith(self.module_libs):
                    os.unlink(os.path.join(root, filename))

        # overwrite header na library search paths
        env = os.environ.copy()
        env["CPPFLAGS"] = "-I{}".format(self.include_dir)
        env["LDFLAGS"] = "-L{}".format(self.lib_dir)
        # set rpath
        env["LD_RUN_PATH"] = self.lib_dir

        log.info("Rebuilding Python modules")
        cmd = [sys.executable, "setup.py", "build"]
        self._subprocess_call(cmd, env=env)
        self.check_imports()

    eleza check_imports(self):
        cmd = [sys.executable, "-c", "agiza _ssl; agiza _hashlib"]
        self._subprocess_call(cmd)

    eleza check_pyssl(self):
        version = self.pyssl_version
        ikiwa self.version haiko kwenye version:
            ashiria ValueError(version)

    eleza run_python_tests(self, tests, network=Kweli):
        ikiwa sio tests:
            cmd = [sys.executable, 'Lib/test/ssltests.py', '-j0']
        lasivyo sys.version_info < (3, 3):
            cmd = [sys.executable, '-m', 'test.regrtest']
        isipokua:
            cmd = [sys.executable, '-m', 'test', '-j0']
        ikiwa network:
            cmd.extend(['-u', 'network', '-u', 'urlfetch'])
        cmd.extend(['-w', '-r'])
        cmd.extend(tests)
        self._subprocess_call(cmd, stdout=Tupu)


kundi BuildOpenSSL(AbstractBuilder):
    library = "OpenSSL"
    url_template = "https://www.openssl.org/source/openssl-{}.tar.gz"
    src_template = "openssl-{}.tar.gz"
    build_template = "openssl-{}"
    # only install software, skip docs
    install_target = 'install_sw'


kundi BuildLibreSSL(AbstractBuilder):
    library = "LibreSSL"
    url_template = (
        "https://ftp.openbsd.org/pub/OpenBSD/LibreSSL/libressl-{}.tar.gz")
    src_template = "libressl-{}.tar.gz"
    build_template = "libressl-{}"


eleza configure_make():
    ikiwa sio os.path.isfile('Makefile'):
        log.info('Running ./configure')
        subprocess.check_call([
            './configure', '--config-cache', '--quiet',
            '--with-pydebug'
        ])

    log.info('Running make')
    subprocess.check_call(['make', '--quiet'])


eleza main():
    args = parser.parse_args()
    ikiwa sio args.openssl na sio args.libressl:
        args.openssl = list(OPENSSL_RECENT_VERSIONS)
        args.libressl = list(LIBRESSL_RECENT_VERSIONS)
        ikiwa sio args.disable_ancient:
            args.openssl.extend(OPENSSL_OLD_VERSIONS)
            args.libressl.extend(LIBRESSL_OLD_VERSIONS)

    logging.basicConfig(
        level=logging.DEBUG ikiwa args.debug isipokua logging.INFO,
        format="*** %(levelname)s %(message)s"
    )

    start = datetime.now()

    ikiwa args.steps kwenye {'modules', 'tests'}:
        kila name kwenye ['setup.py', 'Modules/_ssl.c']:
            ikiwa sio os.path.isfile(os.path.join(PYTHONROOT, name)):
                parser.error(
                    "Must be executed kutoka CPython build dir"
                )
        ikiwa sio os.path.samefile('python', sys.executable):
            parser.error(
                "Must be executed ukijumuisha ./python kutoka CPython build dir"
            )
        # check kila configure na run make
        configure_make()

    # download na register builder
    builds = []

    kila version kwenye args.openssl:
        build = BuildOpenSSL(
            version,
            args
        )
        build.install()
        builds.append(build)

    kila version kwenye args.libressl:
        build = BuildLibreSSL(
            version,
            args
        )
        build.install()
        builds.append(build)

    ikiwa args.steps kwenye {'modules', 'tests'}:
        kila build kwenye builds:
            jaribu:
                build.recompile_pymods()
                build.check_pyssl()
                ikiwa args.steps == 'tests':
                    build.run_python_tests(
                        tests=args.tests,
                        network=args.network,
                    )
            tatizo Exception kama e:
                log.exception("%s failed", build)
                andika("{} failed: {}".format(build, e), file=sys.stderr)
                sys.exit(2)

    log.info("\n{} finished kwenye {}".format(
            args.steps.capitalize(),
            datetime.now() - start
        ))
    andika('Python: ', sys.version)
    ikiwa args.steps == 'tests':
        ikiwa args.tests:
            andika('Executed Tests:', ' '.join(args.tests))
        isipokua:
            andika('Executed all SSL tests.')

    andika('OpenSSL / LibreSSL versions:')
    kila build kwenye builds:
        andika("    * {0.library} {0.version}".format(build))


ikiwa __name__ == "__main__":
    main()
