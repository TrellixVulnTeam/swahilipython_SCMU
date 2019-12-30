"""distutils.command.bdist_rpm

Implements the Distutils 'bdist_rpm' command (create RPM source na binary
distributions)."""

agiza subprocess, sys, os
kutoka distutils.core agiza Command
kutoka distutils.debug agiza DEBUG
kutoka distutils.util agiza get_platform
kutoka distutils.file_util agiza write_file
kutoka distutils.errors agiza *
kutoka distutils.sysconfig agiza get_python_version
kutoka distutils agiza log

kundi bdist_rpm(Command):

    description = "create an RPM distribution"

    user_options = [
        ('bdist-base=', Tupu,
         "base directory kila creating built distributions"),
        ('rpm-base=', Tupu,
         "base directory kila creating RPMs (defaults to \"rpm\" under "
         "--bdist-base; must be specified kila RPM 2)"),
        ('dist-dir=', 'd',
         "directory to put final RPM files kwenye "
         "(and .spec files ikiwa --spec-only)"),
        ('python=', Tupu,
         "path to Python interpreter to hard-code kwenye the .spec file "
         "(default: \"python\")"),
        ('fix-python', Tupu,
         "hard-code the exact path to the current Python interpreter kwenye "
         "the .spec file"),
        ('spec-only', Tupu,
         "only regenerate spec file"),
        ('source-only', Tupu,
         "only generate source RPM"),
        ('binary-only', Tupu,
         "only generate binary RPM"),
        ('use-bzip2', Tupu,
         "use bzip2 instead of gzip to create source distribution"),

        # More meta-data: too RPM-specific to put kwenye the setup script,
        # but needs to go kwenye the .spec file -- so we make these options
        # to "bdist_rpm".  The idea ni that packagers would put this
        # info kwenye setup.cfg, although they are of course free to
        # supply it on the command line.
        ('distribution-name=', Tupu,
         "name of the (Linux) distribution to which this "
         "RPM applies (*not* the name of the module distribution!)"),
        ('group=', Tupu,
         "package classification [default: \"Development/Libraries\"]"),
        ('release=', Tupu,
         "RPM release number"),
        ('serial=', Tupu,
         "RPM serial number"),
        ('vendor=', Tupu,
         "RPM \"vendor\" (eg. \"Joe Blow <joe@example.com>\") "
         "[default: maintainer ama author kutoka setup script]"),
        ('packager=', Tupu,
         "RPM packager (eg. \"Jane Doe <jane@example.net>\") "
         "[default: vendor]"),
        ('doc-files=', Tupu,
         "list of documentation files (space ama comma-separated)"),
        ('changelog=', Tupu,
         "RPM changelog"),
        ('icon=', Tupu,
         "name of icon file"),
        ('provides=', Tupu,
         "capabilities provided by this package"),
        ('requires=', Tupu,
         "capabilities required by this package"),
        ('conflicts=', Tupu,
         "capabilities which conflict ukijumuisha this package"),
        ('build-requires=', Tupu,
         "capabilities required to build this package"),
        ('obsoletes=', Tupu,
         "capabilities made obsolete by this package"),
        ('no-autoreq', Tupu,
         "do sio automatically calculate dependencies"),

        # Actions to take when building RPM
        ('keep-temp', 'k',
         "don't clean up RPM build directory"),
        ('no-keep-temp', Tupu,
         "clean up RPM build directory [default]"),
        ('use-rpm-opt-flags', Tupu,
         "compile ukijumuisha RPM_OPT_FLAGS when building kutoka source RPM"),
        ('no-rpm-opt-flags', Tupu,
         "do sio pita any RPM CFLAGS to compiler"),
        ('rpm3-mode', Tupu,
         "RPM 3 compatibility mode (default)"),
        ('rpm2-mode', Tupu,
         "RPM 2 compatibility mode"),

        # Add the hooks necessary kila specifying custom scripts
        ('prep-script=', Tupu,
         "Specify a script kila the PREP phase of RPM building"),
        ('build-script=', Tupu,
         "Specify a script kila the BUILD phase of RPM building"),

        ('pre-install=', Tupu,
         "Specify a script kila the pre-INSTALL phase of RPM building"),
        ('install-script=', Tupu,
         "Specify a script kila the INSTALL phase of RPM building"),
        ('post-install=', Tupu,
         "Specify a script kila the post-INSTALL phase of RPM building"),

        ('pre-uninstall=', Tupu,
         "Specify a script kila the pre-UNINSTALL phase of RPM building"),
        ('post-uninstall=', Tupu,
         "Specify a script kila the post-UNINSTALL phase of RPM building"),

        ('clean-script=', Tupu,
         "Specify a script kila the CLEAN phase of RPM building"),

        ('verify-script=', Tupu,
         "Specify a script kila the VERIFY phase of the RPM build"),

        # Allow a packager to explicitly force an architecture
        ('force-arch=', Tupu,
         "Force an architecture onto the RPM build process"),

        ('quiet', 'q',
         "Run the INSTALL phase of RPM building kwenye quiet mode"),
        ]

    boolean_options = ['keep-temp', 'use-rpm-opt-flags', 'rpm3-mode',
                       'no-autoreq', 'quiet']

    negative_opt = {'no-keep-temp': 'keep-temp',
                    'no-rpm-opt-flags': 'use-rpm-opt-flags',
                    'rpm2-mode': 'rpm3-mode'}


    eleza initialize_options(self):
        self.bdist_base = Tupu
        self.rpm_base = Tupu
        self.dist_dir = Tupu
        self.python = Tupu
        self.fix_python = Tupu
        self.spec_only = Tupu
        self.binary_only = Tupu
        self.source_only = Tupu
        self.use_bzip2 = Tupu

        self.distribution_name = Tupu
        self.group = Tupu
        self.release = Tupu
        self.serial = Tupu
        self.vendor = Tupu
        self.packager = Tupu
        self.doc_files = Tupu
        self.changelog = Tupu
        self.icon = Tupu

        self.prep_script = Tupu
        self.build_script = Tupu
        self.install_script = Tupu
        self.clean_script = Tupu
        self.verify_script = Tupu
        self.pre_install = Tupu
        self.post_install = Tupu
        self.pre_uninstall = Tupu
        self.post_uninstall = Tupu
        self.prep = Tupu
        self.provides = Tupu
        self.requires = Tupu
        self.conflicts = Tupu
        self.build_requires = Tupu
        self.obsoletes = Tupu

        self.keep_temp = 0
        self.use_rpm_opt_flags = 1
        self.rpm3_mode = 1
        self.no_autoreq = 0

        self.force_arch = Tupu
        self.quiet = 0

    eleza finalize_options(self):
        self.set_undefined_options('bdist', ('bdist_base', 'bdist_base'))
        ikiwa self.rpm_base ni Tupu:
            ikiwa sio self.rpm3_mode:
                ashiria DistutilsOptionError(
                      "you must specify --rpm-base kwenye RPM 2 mode")
            self.rpm_base = os.path.join(self.bdist_base, "rpm")

        ikiwa self.python ni Tupu:
            ikiwa self.fix_python:
                self.python = sys.executable
            isipokua:
                self.python = "python3"
        lasivyo self.fix_python:
            ashiria DistutilsOptionError(
                  "--python na --fix-python are mutually exclusive options")

        ikiwa os.name != 'posix':
            ashiria DistutilsPlatformError("don't know how to create RPM "
                   "distributions on platform %s" % os.name)
        ikiwa self.binary_only na self.source_only:
            ashiria DistutilsOptionError(
                  "cansio supply both '--source-only' na '--binary-only'")

        # don't pita CFLAGS to pure python distributions
        ikiwa sio self.distribution.has_ext_modules():
            self.use_rpm_opt_flags = 0

        self.set_undefined_options('bdist', ('dist_dir', 'dist_dir'))
        self.finalize_package_data()

    eleza finalize_package_data(self):
        self.ensure_string('group', "Development/Libraries")
        self.ensure_string('vendor',
                           "%s <%s>" % (self.distribution.get_contact(),
                                        self.distribution.get_contact_email()))
        self.ensure_string('packager')
        self.ensure_string_list('doc_files')
        ikiwa isinstance(self.doc_files, list):
            kila readme kwenye ('README', 'README.txt'):
                ikiwa os.path.exists(readme) na readme haiko kwenye self.doc_files:
                    self.doc_files.append(readme)

        self.ensure_string('release', "1")
        self.ensure_string('serial')   # should it be an int?

        self.ensure_string('distribution_name')

        self.ensure_string('changelog')
          # Format changelog correctly
        self.changelog = self._format_changelog(self.changelog)

        self.ensure_filename('icon')

        self.ensure_filename('prep_script')
        self.ensure_filename('build_script')
        self.ensure_filename('install_script')
        self.ensure_filename('clean_script')
        self.ensure_filename('verify_script')
        self.ensure_filename('pre_install')
        self.ensure_filename('post_install')
        self.ensure_filename('pre_uninstall')
        self.ensure_filename('post_uninstall')

        # XXX don't forget we punted on summaries na descriptions -- they
        # should be handled here eventually!

        # Now *this* ni some meta-data that belongs kwenye the setup script...
        self.ensure_string_list('provides')
        self.ensure_string_list('requires')
        self.ensure_string_list('conflicts')
        self.ensure_string_list('build_requires')
        self.ensure_string_list('obsoletes')

        self.ensure_string('force_arch')

    eleza run(self):
        ikiwa DEBUG:
            andika("before _get_package_data():")
            andika("vendor =", self.vendor)
            andika("packager =", self.packager)
            andika("doc_files =", self.doc_files)
            andika("changelog =", self.changelog)

        # make directories
        ikiwa self.spec_only:
            spec_dir = self.dist_dir
            self.mkpath(spec_dir)
        isipokua:
            rpm_dir = {}
            kila d kwenye ('SOURCES', 'SPECS', 'BUILD', 'RPMS', 'SRPMS'):
                rpm_dir[d] = os.path.join(self.rpm_base, d)
                self.mkpath(rpm_dir[d])
            spec_dir = rpm_dir['SPECS']

        # Spec file goes into 'dist_dir' ikiwa '--spec-only specified',
        # build/rpm.<plat> otherwise.
        spec_path = os.path.join(spec_dir,
                                 "%s.spec" % self.distribution.get_name())
        self.execute(write_file,
                     (spec_path,
                      self._make_spec_file()),
                     "writing '%s'" % spec_path)

        ikiwa self.spec_only: # stop ikiwa requested
            rudisha

        # Make a source distribution na copy to SOURCES directory with
        # optional icon.
        saved_dist_files = self.distribution.dist_files[:]
        sdist = self.reinitialize_command('sdist')
        ikiwa self.use_bzip2:
            sdist.formats = ['bztar']
        isipokua:
            sdist.formats = ['gztar']
        self.run_command('sdist')
        self.distribution.dist_files = saved_dist_files

        source = sdist.get_archive_files()[0]
        source_dir = rpm_dir['SOURCES']
        self.copy_file(source, source_dir)

        ikiwa self.icon:
            ikiwa os.path.exists(self.icon):
                self.copy_file(self.icon, source_dir)
            isipokua:
                ashiria DistutilsFileError(
                      "icon file '%s' does sio exist" % self.icon)

        # build package
        log.info("building RPMs")
        rpm_cmd = ['rpmbuild']

        ikiwa self.source_only: # what kind of RPMs?
            rpm_cmd.append('-bs')
        lasivyo self.binary_only:
            rpm_cmd.append('-bb')
        isipokua:
            rpm_cmd.append('-ba')
        rpm_cmd.extend(['--define', '__python %s' % self.python])
        ikiwa self.rpm3_mode:
            rpm_cmd.extend(['--define',
                             '_topdir %s' % os.path.abspath(self.rpm_base)])
        ikiwa sio self.keep_temp:
            rpm_cmd.append('--clean')

        ikiwa self.quiet:
            rpm_cmd.append('--quiet')

        rpm_cmd.append(spec_path)
        # Determine the binary rpm names that should be built out of this spec
        # file
        # Note that some of these may sio be really built (ikiwa the file
        # list ni empty)
        nvr_string = "%{name}-%{version}-%{release}"
        src_rpm = nvr_string + ".src.rpm"
        non_src_rpm = "%{arch}/" + nvr_string + ".%{arch}.rpm"
        q_cmd = r"rpm -q --qf '%s %s\n' --specfile '%s'" % (
            src_rpm, non_src_rpm, spec_path)

        out = os.popen(q_cmd)
        jaribu:
            binary_rpms = []
            source_rpm = Tupu
            wakati Kweli:
                line = out.readline()
                ikiwa sio line:
                    koma
                l = line.strip().split()
                assert(len(l) == 2)
                binary_rpms.append(l[1])
                # The source rpm ni named after the first entry kwenye the spec file
                ikiwa source_rpm ni Tupu:
                    source_rpm = l[0]

            status = out.close()
            ikiwa status:
                ashiria DistutilsExecError("Failed to execute: %s" % repr(q_cmd))

        mwishowe:
            out.close()

        self.spawn(rpm_cmd)

        ikiwa sio self.dry_run:
            ikiwa self.distribution.has_ext_modules():
                pyversion = get_python_version()
            isipokua:
                pyversion = 'any'

            ikiwa sio self.binary_only:
                srpm = os.path.join(rpm_dir['SRPMS'], source_rpm)
                assert(os.path.exists(srpm))
                self.move_file(srpm, self.dist_dir)
                filename = os.path.join(self.dist_dir, source_rpm)
                self.distribution.dist_files.append(
                    ('bdist_rpm', pyversion, filename))

            ikiwa sio self.source_only:
                kila rpm kwenye binary_rpms:
                    rpm = os.path.join(rpm_dir['RPMS'], rpm)
                    ikiwa os.path.exists(rpm):
                        self.move_file(rpm, self.dist_dir)
                        filename = os.path.join(self.dist_dir,
                                                os.path.basename(rpm))
                        self.distribution.dist_files.append(
                            ('bdist_rpm', pyversion, filename))

    eleza _dist_path(self, path):
        rudisha os.path.join(self.dist_dir, os.path.basename(path))

    eleza _make_spec_file(self):
        """Generate the text of an RPM spec file na rudisha it kama a
        list of strings (one per line).
        """
        # definitions na headers
        spec_file = [
            '%define name ' + self.distribution.get_name(),
            '%define version ' + self.distribution.get_version().replace('-','_'),
            '%define unmangled_version ' + self.distribution.get_version(),
            '%define release ' + self.release.replace('-','_'),
            '',
            'Summary: ' + self.distribution.get_description(),
            ]

        # Workaround kila #14443 which affects some RPM based systems such as
        # RHEL6 (and probably derivatives)
        vendor_hook = subprocess.getoutput('rpm --eval %{__os_install_post}')
        # Generate a potential replacement value kila __os_install_post (whilst
        # normalizing the whitespace to simplify the test kila whether the
        # invocation of brp-python-bytecompile pitaes kwenye __python):
        vendor_hook = '\n'.join(['  %s \\' % line.strip()
                                 kila line kwenye vendor_hook.splitlines()])
        problem = "brp-python-bytecompile \\\n"
        fixed = "brp-python-bytecompile %{__python} \\\n"
        fixed_hook = vendor_hook.replace(problem, fixed)
        ikiwa fixed_hook != vendor_hook:
            spec_file.append('# Workaround kila http://bugs.python.org/issue14443')
            spec_file.append('%define __os_install_post ' + fixed_hook + '\n')

        # put locale summaries into spec file
        # XXX sio supported kila now (hard to put a dictionary
        # kwenye a config file -- arg!)
        #kila locale kwenye self.summaries.keys():
        #    spec_file.append('Summary(%s): %s' % (locale,
        #                                          self.summaries[locale]))

        spec_file.extend([
            'Name: %{name}',
            'Version: %{version}',
            'Release: %{release}',])

        # XXX yuck! this filename ni available kutoka the "sdist" command,
        # but only after it has run: na we create the spec file before
        # running "sdist", kwenye case of --spec-only.
        ikiwa self.use_bzip2:
            spec_file.append('Source0: %{name}-%{unmangled_version}.tar.bz2')
        isipokua:
            spec_file.append('Source0: %{name}-%{unmangled_version}.tar.gz')

        spec_file.extend([
            'License: ' + self.distribution.get_license(),
            'Group: ' + self.group,
            'BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot',
            'Prefix: %{_prefix}', ])

        ikiwa sio self.force_arch:
            # noarch ikiwa no extension modules
            ikiwa sio self.distribution.has_ext_modules():
                spec_file.append('BuildArch: noarch')
        isipokua:
            spec_file.append( 'BuildArch: %s' % self.force_arch )

        kila field kwenye ('Vendor',
                      'Packager',
                      'Provides',
                      'Requires',
                      'Conflicts',
                      'Obsoletes',
                      ):
            val = getattr(self, field.lower())
            ikiwa isinstance(val, list):
                spec_file.append('%s: %s' % (field, ' '.join(val)))
            lasivyo val ni sio Tupu:
                spec_file.append('%s: %s' % (field, val))


        ikiwa self.distribution.get_url() != 'UNKNOWN':
            spec_file.append('Url: ' + self.distribution.get_url())

        ikiwa self.distribution_name:
            spec_file.append('Distribution: ' + self.distribution_name)

        ikiwa self.build_requires:
            spec_file.append('BuildRequires: ' +
                             ' '.join(self.build_requires))

        ikiwa self.icon:
            spec_file.append('Icon: ' + os.path.basename(self.icon))

        ikiwa self.no_autoreq:
            spec_file.append('AutoReq: 0')

        spec_file.extend([
            '',
            '%description',
            self.distribution.get_long_description()
            ])

        # put locale descriptions into spec file
        # XXX again, suppressed because config file syntax doesn't
        # easily support this ;-(
        #kila locale kwenye self.descriptions.keys():
        #    spec_file.extend([
        #        '',
        #        '%description -l ' + locale,
        #        self.descriptions[locale],
        #        ])

        # rpm scripts
        # figure out default build script
        def_setup_call = "%s %s" % (self.python,os.path.basename(sys.argv[0]))
        def_build = "%s build" % def_setup_call
        ikiwa self.use_rpm_opt_flags:
            def_build = 'env CFLAGS="$RPM_OPT_FLAGS" ' + def_build

        # insert contents of files

        # XXX this ni kind of misleading: user-supplied options are files
        # that we open na interpolate into the spec file, but the defaults
        # are just text that we drop kwenye as-is.  Hmmm.

        install_cmd = ('%s install -O1 --root=$RPM_BUILD_ROOT '
                       '--record=INSTALLED_FILES') % def_setup_call

        script_options = [
            ('prep', 'prep_script', "%setup -n %{name}-%{unmangled_version}"),
            ('build', 'build_script', def_build),
            ('install', 'install_script', install_cmd),
            ('clean', 'clean_script', "rm -rf $RPM_BUILD_ROOT"),
            ('verifyscript', 'verify_script', Tupu),
            ('pre', 'pre_install', Tupu),
            ('post', 'post_install', Tupu),
            ('preun', 'pre_uninstall', Tupu),
            ('postun', 'post_uninstall', Tupu),
        ]

        kila (rpm_opt, attr, default) kwenye script_options:
            # Insert contents of file referred to, ikiwa no file ni referred to
            # use 'default' kama contents of script
            val = getattr(self, attr)
            ikiwa val ama default:
                spec_file.extend([
                    '',
                    '%' + rpm_opt,])
                ikiwa val:
                    ukijumuisha open(val) kama f:
                        spec_file.extend(f.read().split('\n'))
                isipokua:
                    spec_file.append(default)


        # files section
        spec_file.extend([
            '',
            '%files -f INSTALLED_FILES',
            '%defattr(-,root,root)',
            ])

        ikiwa self.doc_files:
            spec_file.append('%doc ' + ' '.join(self.doc_files))

        ikiwa self.changelog:
            spec_file.extend([
                '',
                '%changelog',])
            spec_file.extend(self.changelog)

        rudisha spec_file

    eleza _format_changelog(self, changelog):
        """Format the changelog correctly na convert it to a list of strings
        """
        ikiwa sio changelog:
            rudisha changelog
        new_changelog = []
        kila line kwenye changelog.strip().split('\n'):
            line = line.strip()
            ikiwa line[0] == '*':
                new_changelog.extend(['', line])
            lasivyo line[0] == '-':
                new_changelog.append(line)
            isipokua:
                new_changelog.append('  ' + line)

        # strip trailing newline inserted by first changelog entry
        ikiwa sio new_changelog[0]:
            toa new_changelog[0]

        rudisha new_changelog
