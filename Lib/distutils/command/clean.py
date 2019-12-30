"""distutils.command.clean

Implements the Distutils 'clean' command."""

# contributed by Bastian Kleineidam <calvin@cs.uni-sb.de>, added 2000-03-18

agiza os
kutoka distutils.core agiza Command
kutoka distutils.dir_util agiza remove_tree
kutoka distutils agiza log

kundi clean(Command):

    description = "clean up temporary files kutoka 'build' command"
    user_options = [
        ('build-base=', 'b',
         "base build directory (default: 'build.build-base')"),
        ('build-lib=', Tupu,
         "build directory kila all modules (default: 'build.build-lib')"),
        ('build-temp=', 't',
         "temporary build directory (default: 'build.build-temp')"),
        ('build-scripts=', Tupu,
         "build directory kila scripts (default: 'build.build-scripts')"),
        ('bdist-base=', Tupu,
         "temporary directory kila built distributions"),
        ('all', 'a',
         "remove all build output, sio just temporary by-products")
    ]

    boolean_options = ['all']

    eleza initialize_options(self):
        self.build_base = Tupu
        self.build_lib = Tupu
        self.build_temp = Tupu
        self.build_scripts = Tupu
        self.bdist_base = Tupu
        self.all = Tupu

    eleza finalize_options(self):
        self.set_undefined_options('build',
                                   ('build_base', 'build_base'),
                                   ('build_lib', 'build_lib'),
                                   ('build_scripts', 'build_scripts'),
                                   ('build_temp', 'build_temp'))
        self.set_undefined_options('bdist',
                                   ('bdist_base', 'bdist_base'))

    eleza run(self):
        # remove the build/temp.<plat> directory (unless it's already
        # gone)
        ikiwa os.path.exists(self.build_temp):
            remove_tree(self.build_temp, dry_run=self.dry_run)
        isipokua:
            log.debug("'%s' does sio exist -- can't clean it",
                      self.build_temp)

        ikiwa self.all:
            # remove build directories
            kila directory kwenye (self.build_lib,
                              self.bdist_base,
                              self.build_scripts):
                ikiwa os.path.exists(directory):
                    remove_tree(directory, dry_run=self.dry_run)
                isipokua:
                    log.warn("'%s' does sio exist -- can't clean it",
                             directory)

        # just kila the heck of it, try to remove the base build directory:
        # we might have emptied it right now, but ikiwa sio we don't care
        ikiwa sio self.dry_run:
            jaribu:
                os.rmdir(self.build_base)
                log.info("removing '%s'", self.build_base)
            tatizo OSError:
                pita
