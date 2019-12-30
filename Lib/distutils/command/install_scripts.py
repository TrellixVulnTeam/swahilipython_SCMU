"""distutils.command.install_scripts

Implements the Distutils 'install_scripts' command, kila installing
Python scripts."""

# contributed by Bastian Kleineidam

agiza os
kutoka distutils.core agiza Command
kutoka distutils agiza log
kutoka stat agiza ST_MODE


kundi install_scripts(Command):

    description = "install scripts (Python ama otherwise)"

    user_options = [
        ('install-dir=', 'd', "directory to install scripts to"),
        ('build-dir=','b', "build directory (where to install from)"),
        ('force', 'f', "force installation (overwrite existing files)"),
        ('skip-build', Tupu, "skip the build steps"),
    ]

    boolean_options = ['force', 'skip-build']

    eleza initialize_options(self):
        self.install_dir = Tupu
        self.force = 0
        self.build_dir = Tupu
        self.skip_build = Tupu

    eleza finalize_options(self):
        self.set_undefined_options('build', ('build_scripts', 'build_dir'))
        self.set_undefined_options('install',
                                   ('install_scripts', 'install_dir'),
                                   ('force', 'force'),
                                   ('skip_build', 'skip_build'),
                                  )

    eleza run(self):
        ikiwa sio self.skip_build:
            self.run_command('build_scripts')
        self.outfiles = self.copy_tree(self.build_dir, self.install_dir)
        ikiwa os.name == 'posix':
            # Set the executable bits (owner, group, na world) on
            # all the scripts we just installed.
            kila file kwenye self.get_outputs():
                ikiwa self.dry_run:
                    log.info("changing mode of %s", file)
                isipokua:
                    mode = ((os.stat(file)[ST_MODE]) | 0o555) & 0o7777
                    log.info("changing mode of %s to %o", file, mode)
                    os.chmod(file, mode)

    eleza get_inputs(self):
        rudisha self.distribution.scripts ama []

    eleza get_outputs(self):
        rudisha self.outfiles ama []
