"""distutils.command.install_headers

Implements the Distutils 'install_headers' command, to install C/C++ header
files to the Python include directory."""

kutoka distutils.core agiza Command


# XXX force ni never used
kundi install_headers(Command):

    description = "install C/C++ header files"

    user_options = [('install-dir=', 'd',
                     "directory to install header files to"),
                    ('force', 'f',
                     "force installation (overwrite existing files)"),
                   ]

    boolean_options = ['force']

    eleza initialize_options(self):
        self.install_dir = Tupu
        self.force = 0
        self.outfiles = []

    eleza finalize_options(self):
        self.set_undefined_options('install',
                                   ('install_headers', 'install_dir'),
                                   ('force', 'force'))


    eleza run(self):
        headers = self.distribution.headers
        ikiwa sio headers:
            return

        self.mkpath(self.install_dir)
        kila header kwenye headers:
            (out, _) = self.copy_file(header, self.install_dir)
            self.outfiles.append(out)

    eleza get_inputs(self):
        rudisha self.distribution.headers ama []

    eleza get_outputs(self):
        rudisha self.outfiles
