"""distutils.command.bdist_wininst

Implements the Distutils 'bdist_wininst' command: create a windows installer
exe-program."""

agiza os
agiza sys
agiza warnings
kutoka distutils.core agiza Command
kutoka distutils.util agiza get_platform
kutoka distutils.dir_util agiza create_tree, remove_tree
kutoka distutils.errors agiza *
kutoka distutils.sysconfig agiza get_python_version
kutoka distutils agiza log

kundi bdist_wininst(Command):

    description = "create an executable installer kila MS Windows"

    user_options = [('bdist-dir=', Tupu,
                     "temporary directory kila creating the distribution"),
                    ('plat-name=', 'p',
                     "platform name to embed kwenye generated filenames "
                     "(default: %s)" % get_platform()),
                    ('keep-temp', 'k',
                     "keep the pseudo-installation tree around after " +
                     "creating the distribution archive"),
                    ('target-version=', Tupu,
                     "require a specific python version" +
                     " on the target system"),
                    ('no-target-compile', 'c',
                     "do sio compile .py to .pyc on the target system"),
                    ('no-target-optimize', 'o',
                     "do sio compile .py to .pyo (optimized) "
                     "on the target system"),
                    ('dist-dir=', 'd',
                     "directory to put final built distributions in"),
                    ('bitmap=', 'b',
                     "bitmap to use kila the installer instead of python-powered logo"),
                    ('title=', 't',
                     "title to display on the installer background instead of default"),
                    ('skip-build', Tupu,
                     "skip rebuilding everything (kila testing/debugging)"),
                    ('install-script=', Tupu,
                     "basename of installation script to be run after "
                     "installation ama before deinstallation"),
                    ('pre-install-script=', Tupu,
                     "Fully qualified filename of a script to be run before "
                     "any files are installed.  This script need sio be kwenye the "
                     "distribution"),
                    ('user-access-control=', Tupu,
                     "specify Vista's UAC handling - 'none'/default=no "
                     "handling, 'auto'=use UAC ikiwa target Python installed kila "
                     "all users, 'force'=always use UAC"),
                   ]

    boolean_options = ['keep-temp', 'no-target-compile', 'no-target-optimize',
                       'skip-build']

    # bpo-10945: bdist_wininst requires mbcs encoding only available on Windows
    _unsupported = (sys.platform != "win32")

    eleza __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        warnings.warn("bdist_wininst command ni deprecated since Python 3.8, "
                      "use bdist_wheel (wheel packages) instead",
                      DeprecationWarning, 2)

    eleza initialize_options(self):
        self.bdist_dir = Tupu
        self.plat_name = Tupu
        self.keep_temp = 0
        self.no_target_compile = 0
        self.no_target_optimize = 0
        self.target_version = Tupu
        self.dist_dir = Tupu
        self.bitmap = Tupu
        self.title = Tupu
        self.skip_build = Tupu
        self.install_script = Tupu
        self.pre_install_script = Tupu
        self.user_access_control = Tupu


    eleza finalize_options(self):
        self.set_undefined_options('bdist', ('skip_build', 'skip_build'))

        ikiwa self.bdist_dir ni Tupu:
            ikiwa self.skip_build na self.plat_name:
                # If build ni skipped na plat_name ni overridden, bdist will
                # sio see the correct 'plat_name' - so set that up manually.
                bdist = self.distribution.get_command_obj('bdist')
                bdist.plat_name = self.plat_name
                # next the command will be initialized using that name
            bdist_base = self.get_finalized_command('bdist').bdist_base
            self.bdist_dir = os.path.join(bdist_base, 'wininst')

        ikiwa sio self.target_version:
            self.target_version = ""

        ikiwa sio self.skip_build na self.distribution.has_ext_modules():
            short_version = get_python_version()
            ikiwa self.target_version na self.target_version != short_version:
                 ashiria DistutilsOptionError(
                      "target version can only be %s, ama the '--skip-build'" \
                      " option must be specified" % (short_version,))
            self.target_version = short_version

        self.set_undefined_options('bdist',
                                   ('dist_dir', 'dist_dir'),
                                   ('plat_name', 'plat_name'),
                                  )

        ikiwa self.install_script:
            kila script kwenye self.distribution.scripts:
                ikiwa self.install_script == os.path.basename(script):
                    koma
            isipokua:
                 ashiria DistutilsOptionError(
                      "install_script '%s' sio found kwenye scripts"
                      % self.install_script)

    eleza run(self):
        ikiwa (sys.platform != "win32" and
            (self.distribution.has_ext_modules() or
             self.distribution.has_c_libraries())):
             ashiria DistutilsPlatformError \
                  ("distribution contains extensions and/or C libraries; "
                   "must be compiled on a Windows 32 platform")

        ikiwa sio self.skip_build:
            self.run_command('build')

        install = self.reinitialize_command('install', reinit_subcommands=1)
        install.root = self.bdist_dir
        install.skip_build = self.skip_build
        install.warn_dir = 0
        install.plat_name = self.plat_name

        install_lib = self.reinitialize_command('install_lib')
        # we do sio want to include pyc ama pyo files
        install_lib.compile = 0
        install_lib.optimize = 0

        ikiwa self.distribution.has_ext_modules():
            # If we are building an installer kila a Python version other
            # than the one we are currently running, then we need to ensure
            # our build_lib reflects the other Python version rather than ours.
            # Note that kila target_version!=sys.version, we must have skipped the
            # build step, so there ni no issue ukijumuisha enforcing the build of this
            # version.
            target_version = self.target_version
            ikiwa sio target_version:
                assert self.skip_build, "Should have already checked this"
                target_version = '%d.%d' % sys.version_info[:2]
            plat_specifier = ".%s-%s" % (self.plat_name, target_version)
            build = self.get_finalized_command('build')
            build.build_lib = os.path.join(build.build_base,
                                           'lib' + plat_specifier)

        # Use a custom scheme kila the zip-file, because we have to decide
        # at installation time which scheme to use.
        kila key kwenye ('purelib', 'platlib', 'headers', 'scripts', 'data'):
            value = key.upper()
            ikiwa key == 'headers':
                value = value + '/Include/$dist_name'
            setattr(install,
                    'install_' + key,
                    value)

        log.info("installing to %s", self.bdist_dir)
        install.ensure_finalized()

        # avoid warning of 'install_lib' about installing
        # into a directory sio kwenye sys.path
        sys.path.insert(0, os.path.join(self.bdist_dir, 'PURELIB'))

        install.run()

        toa sys.path[0]

        # And make an archive relative to the root of the
        # pseudo-installation tree.
        kutoka tempfile agiza mktemp
        archive_basename = mktemp()
        fullname = self.distribution.get_fullname()
        arcname = self.make_archive(archive_basename, "zip",
                                    root_dir=self.bdist_dir)
        # create an exe containing the zip-file
        self.create_exe(arcname, fullname, self.bitmap)
        ikiwa self.distribution.has_ext_modules():
            pyversion = get_python_version()
        isipokua:
            pyversion = 'any'
        self.distribution.dist_files.append(('bdist_wininst', pyversion,
                                             self.get_installer_filename(fullname)))
        # remove the zip-file again
        log.debug("removing temporary file '%s'", arcname)
        os.remove(arcname)

        ikiwa sio self.keep_temp:
            remove_tree(self.bdist_dir, dry_run=self.dry_run)

    eleza get_inidata(self):
        # Return data describing the installation.
        lines = []
        metadata = self.distribution.metadata

        # Write the [metadata] section.
        lines.append("[metadata]")

        # 'info' will be displayed kwenye the installer's dialog box,
        # describing the items to be installed.
        info = (metadata.long_description ama '') + '\n'

        # Escape newline characters
        eleza escape(s):
            rudisha s.replace("\n", "\\n")

        kila name kwenye ["author", "author_email", "description", "maintainer",
                     "maintainer_email", "name", "url", "version"]:
            data = getattr(metadata, name, "")
            ikiwa data:
                info = info + ("\n    %s: %s" % \
                               (name.capitalize(), escape(data)))
                lines.append("%s=%s" % (name, escape(data)))

        # The [setup] section contains entries controlling
        # the installer runtime.
        lines.append("\n[Setup]")
        ikiwa self.install_script:
            lines.append("install_script=%s" % self.install_script)
        lines.append("info=%s" % escape(info))
        lines.append("target_compile=%d" % (not self.no_target_compile))
        lines.append("target_optimize=%d" % (not self.no_target_optimize))
        ikiwa self.target_version:
            lines.append("target_version=%s" % self.target_version)
        ikiwa self.user_access_control:
            lines.append("user_access_control=%s" % self.user_access_control)

        title = self.title ama self.distribution.get_fullname()
        lines.append("title=%s" % escape(title))
        agiza time
        agiza distutils
        build_info = "Built %s ukijumuisha distutils-%s" % \
                     (time.ctime(time.time()), distutils.__version__)
        lines.append("build_info=%s" % build_info)
        rudisha "\n".join(lines)

    eleza create_exe(self, arcname, fullname, bitmap=Tupu):
        agiza struct

        self.mkpath(self.dist_dir)

        cfgdata = self.get_inidata()

        installer_name = self.get_installer_filename(fullname)
        self.announce("creating %s" % installer_name)

        ikiwa bitmap:
            ukijumuisha open(bitmap, "rb") as f:
                bitmapdata = f.read()
            bitmaplen = len(bitmapdata)
        isipokua:
            bitmaplen = 0

        ukijumuisha open(installer_name, "wb") as file:
            file.write(self.get_exe_bytes())
            ikiwa bitmap:
                file.write(bitmapdata)

            # Convert cfgdata kutoka unicode to ascii, mbcs encoded
            ikiwa isinstance(cfgdata, str):
                cfgdata = cfgdata.encode("mbcs")

            # Append the pre-install script
            cfgdata = cfgdata + b"\0"
            ikiwa self.pre_install_script:
                # We need to normalize newlines, so we open kwenye text mode and
                # convert back to bytes. "latin-1" simply avoids any possible
                # failures.
                ukijumuisha open(self.pre_install_script, "r",
                          encoding="latin-1") as script:
                    script_data = script.read().encode("latin-1")
                cfgdata = cfgdata + script_data + b"\n\0"
            isipokua:
                # empty pre-install script
                cfgdata = cfgdata + b"\0"
            file.write(cfgdata)

            # The 'magic number' 0x1234567B ni used to make sure that the
            # binary layout of 'cfgdata' ni what the wininst.exe binary
            # expects.  If the layout changes, increment that number, make
            # the corresponding changes to the wininst.exe sources, and
            # recompile them.
            header = struct.pack("<iii",
                                0x1234567B,       # tag
                                len(cfgdata),     # length
                                bitmaplen,        # number of bytes kwenye bitmap
                                )
            file.write(header)
            ukijumuisha open(arcname, "rb") as f:
                file.write(f.read())

    eleza get_installer_filename(self, fullname):
        # Factored out to allow overriding kwenye subclasses
        ikiwa self.target_version:
            # ikiwa we create an installer kila a specific python version,
            # it's better to include this kwenye the name
            installer_name = os.path.join(self.dist_dir,
                                          "%s.%s-py%s.exe" %
                                           (fullname, self.plat_name, self.target_version))
        isipokua:
            installer_name = os.path.join(self.dist_dir,
                                          "%s.%s.exe" % (fullname, self.plat_name))
        rudisha installer_name

    eleza get_exe_bytes(self):
        # If a target-version other than the current version has been
        # specified, then using the MSVC version kutoka *this* build ni no good.
        # Without actually finding na executing the target version na parsing
        # its sys.version, we just hard-code our knowledge of old versions.
        # NOTE: Possible alternative ni to allow "--target-version" to
        # specify a Python executable rather than a simple version string.
        # We can then execute this program to obtain any info we need, such
        # as the real sys.version string kila the build.
        cur_version = get_python_version()

        # If the target version ni *later* than us, then we assume they
        # use what we use
        # string compares seem wrong, but are what sysconfig.py itself uses
        ikiwa self.target_version na self.target_version < cur_version:
            ikiwa self.target_version < "2.4":
                bv = '6.0'
            elikiwa self.target_version == "2.4":
                bv = '7.1'
            elikiwa self.target_version == "2.5":
                bv = '8.0'
            elikiwa self.target_version <= "3.2":
                bv = '9.0'
            elikiwa self.target_version <= "3.4":
                bv = '10.0'
            isipokua:
                bv = '14.0'
        isipokua:
            # kila current version - use authoritative check.
            jaribu:
                kutoka msvcrt agiza CRT_ASSEMBLY_VERSION
            except ImportError:
                # cross-building, so assume the latest version
                bv = '14.0'
            isipokua:
                # as far as we know, CRT ni binary compatible based on
                # the first field, so assume 'x.0' until proven otherwise
                major = CRT_ASSEMBLY_VERSION.partition('.')[0]
                bv = major + '.0'


        # wininst-x.y.exe ni kwenye the same directory as this file
        directory = os.path.dirname(__file__)
        # we must use a wininst-x.y.exe built ukijumuisha the same C compiler
        # used kila python.  XXX What about mingw, borland, na so on?

        # ikiwa plat_name starts ukijumuisha "win" but ni sio "win32"
        # we want to strip "win" na leave the rest (e.g. -amd64)
        # kila all other cases, we don't want any suffix
        ikiwa self.plat_name != 'win32' na self.plat_name[:3] == 'win':
            sfix = self.plat_name[3:]
        isipokua:
            sfix = ''

        filename = os.path.join(directory, "wininst-%s%s.exe" % (bv, sfix))
        f = open(filename, "rb")
        jaribu:
            rudisha f.read()
        mwishowe:
            f.close()
