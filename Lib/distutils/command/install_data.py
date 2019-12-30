"""distutils.command.install_data

Implements the Distutils 'install_data' command, kila installing
platform-independent data files."""

# contributed by Bastian Kleineidam

agiza os
kutoka distutils.core agiza Command
kutoka distutils.util agiza change_root, convert_path

kundi install_data(Command):

    description = "install data files"

    user_options = [
        ('install-dir=', 'd',
         "base directory kila installing data files "
         "(default: installation base dir)"),
        ('root=', Tupu,
         "install everything relative to this alternate root directory"),
        ('force', 'f', "force installation (overwrite existing files)"),
        ]

    boolean_options = ['force']

    eleza initialize_options(self):
        self.install_dir = Tupu
        self.outfiles = []
        self.root = Tupu
        self.force = 0
        self.data_files = self.distribution.data_files
        self.warn_dir = 1

    eleza finalize_options(self):
        self.set_undefined_options('install',
                                   ('install_data', 'install_dir'),
                                   ('root', 'root'),
                                   ('force', 'force'),
                                  )

    eleza run(self):
        self.mkpath(self.install_dir)
        kila f kwenye self.data_files:
            ikiwa isinstance(f, str):
                # it's a simple file, so copy it
                f = convert_path(f)
                ikiwa self.warn_dir:
                    self.warn("setup script did sio provide a directory kila "
                              "'%s' -- installing right kwenye '%s'" %
                              (f, self.install_dir))
                (out, _) = self.copy_file(f, self.install_dir)
                self.outfiles.append(out)
            isipokua:
                # it's a tuple ukijumuisha path to install to na a list of files
                dir = convert_path(f[0])
                ikiwa sio os.path.isabs(dir):
                    dir = os.path.join(self.install_dir, dir)
                lasivyo self.root:
                    dir = change_root(self.root, dir)
                self.mkpath(dir)

                ikiwa f[1] == []:
                    # If there are no files listed, the user must be
                    # trying to create an empty directory, so add the
                    # directory to the list of output files.
                    self.outfiles.append(dir)
                isipokua:
                    # Copy files, adding them to the list of output files.
                    kila data kwenye f[1]:
                        data = convert_path(data)
                        (out, _) = self.copy_file(data, dir)
                        self.outfiles.append(out)

    eleza get_inputs(self):
        rudisha self.data_files ama []

    eleza get_outputs(self):
        rudisha self.outfiles
