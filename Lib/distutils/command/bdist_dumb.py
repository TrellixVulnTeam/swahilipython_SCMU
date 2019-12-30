"""distutils.command.bdist_dumb

Implements the Distutils 'bdist_dumb' command (create a "dumb" built
distribution -- i.e., just an archive to be unpacked under $prefix ama
$exec_prefix)."""

agiza os
kutoka distutils.core agiza Command
kutoka distutils.util agiza get_platform
kutoka distutils.dir_util agiza remove_tree, ensure_relative
kutoka distutils.errors agiza *
kutoka distutils.sysconfig agiza get_python_version
kutoka distutils agiza log

kundi bdist_dumb(Command):

    description = "create a \"dumb\" built distribution"

    user_options = [('bdist-dir=', 'd',
                     "temporary directory kila creating the distribution"),
                    ('plat-name=', 'p',
                     "platform name to embed kwenye generated filenames "
                     "(default: %s)" % get_platform()),
                    ('format=', 'f',
                     "archive format to create (tar, gztar, bztar, xztar, "
                     "ztar, zip)"),
                    ('keep-temp', 'k',
                     "keep the pseudo-installation tree around after " +
                     "creating the distribution archive"),
                    ('dist-dir=', 'd',
                     "directory to put final built distributions in"),
                    ('skip-build', Tupu,
                     "skip rebuilding everything (kila testing/debugging)"),
                    ('relative', Tupu,
                     "build the archive using relative paths "
                     "(default: false)"),
                    ('owner=', 'u',
                     "Owner name used when creating a tar file"
                     " [default: current user]"),
                    ('group=', 'g',
                     "Group name used when creating a tar file"
                     " [default: current group]"),
                   ]

    boolean_options = ['keep-temp', 'skip-build', 'relative']

    default_format = { 'posix': 'gztar',
                       'nt': 'zip' }

    eleza initialize_options(self):
        self.bdist_dir = Tupu
        self.plat_name = Tupu
        self.format = Tupu
        self.keep_temp = 0
        self.dist_dir = Tupu
        self.skip_build = Tupu
        self.relative = 0
        self.owner = Tupu
        self.group = Tupu

    eleza finalize_options(self):
        ikiwa self.bdist_dir ni Tupu:
            bdist_base = self.get_finalized_command('bdist').bdist_base
            self.bdist_dir = os.path.join(bdist_base, 'dumb')

        ikiwa self.format ni Tupu:
            jaribu:
                self.format = self.default_format[os.name]
            tatizo KeyError:
                ashiria DistutilsPlatformError(
                       "don't know how to create dumb built distributions "
                       "on platform %s" % os.name)

        self.set_undefined_options('bdist',
                                   ('dist_dir', 'dist_dir'),
                                   ('plat_name', 'plat_name'),
                                   ('skip_build', 'skip_build'))

    eleza run(self):
        ikiwa sio self.skip_build:
            self.run_command('build')

        install = self.reinitialize_command('install', reinit_subcommands=1)
        install.root = self.bdist_dir
        install.skip_build = self.skip_build
        install.warn_dir = 0

        log.info("installing to %s", self.bdist_dir)
        self.run_command('install')

        # And make an archive relative to the root of the
        # pseudo-installation tree.
        archive_basename = "%s.%s" % (self.distribution.get_fullname(),
                                      self.plat_name)

        pseudoinstall_root = os.path.join(self.dist_dir, archive_basename)
        ikiwa sio self.relative:
            archive_root = self.bdist_dir
        isipokua:
            ikiwa (self.distribution.has_ext_modules() na
                (install.install_base != install.install_platbase)):
                ashiria DistutilsPlatformError(
                       "can't make a dumb built distribution where "
                       "base na platbase are different (%s, %s)"
                       % (repr(install.install_base),
                          repr(install.install_platbase)))
            isipokua:
                archive_root = os.path.join(self.bdist_dir,
                                   ensure_relative(install.install_base))

        # Make the archive
        filename = self.make_archive(pseudoinstall_root,
                                     self.format, root_dir=archive_root,
                                     owner=self.owner, group=self.group)
        ikiwa self.distribution.has_ext_modules():
            pyversion = get_python_version()
        isipokua:
            pyversion = 'any'
        self.distribution.dist_files.append(('bdist_dumb', pyversion,
                                             filename))

        ikiwa sio self.keep_temp:
            remove_tree(self.bdist_dir, dry_run=self.dry_run)
