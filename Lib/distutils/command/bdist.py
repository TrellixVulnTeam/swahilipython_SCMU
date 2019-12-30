"""distutils.command.bdist

Implements the Distutils 'bdist' command (create a built [binary]
distribution)."""

agiza os
kutoka distutils.core agiza Command
kutoka distutils.errors agiza *
kutoka distutils.util agiza get_platform


eleza show_formats():
    """Print list of available formats (arguments to "--format" option).
    """
    kutoka distutils.fancy_getopt agiza FancyGetopt
    formats = []
    kila format kwenye bdist.format_commands:
        formats.append(("formats=" + format, Tupu,
                        bdist.format_command[format][1]))
    pretty_printer = FancyGetopt(formats)
    pretty_printer.print_help("List of available distribution formats:")


kundi bdist(Command):

    description = "create a built (binary) distribution"

    user_options = [('bdist-base=', 'b',
                     "temporary directory kila creating built distributions"),
                    ('plat-name=', 'p',
                     "platform name to embed kwenye generated filenames "
                     "(default: %s)" % get_platform()),
                    ('formats=', Tupu,
                     "formats kila distribution (comma-separated list)"),
                    ('dist-dir=', 'd',
                     "directory to put final built distributions kwenye "
                     "[default: dist]"),
                    ('skip-build', Tupu,
                     "skip rebuilding everything (kila testing/debugging)"),
                    ('owner=', 'u',
                     "Owner name used when creating a tar file"
                     " [default: current user]"),
                    ('group=', 'g',
                     "Group name used when creating a tar file"
                     " [default: current group]"),
                   ]

    boolean_options = ['skip-build']

    help_options = [
        ('help-formats', Tupu,
         "lists available distribution formats", show_formats),
        ]

    # The following commands do sio take a format option kutoka bdist
    no_format_option = ('bdist_rpm',)

    # This won't do kwenye reality: will need to distinguish RPM-ish Linux,
    # Debian-ish Linux, Solaris, FreeBSD, ..., Windows, Mac OS.
    default_format = {'posix': 'gztar',
                      'nt': 'zip'}

    # Establish the preferred order (kila the --help-formats option).
    format_commands = ['rpm', 'gztar', 'bztar', 'xztar', 'ztar', 'tar',
                       'wininst', 'zip', 'msi']

    # And the real information.
    format_command = {'rpm':   ('bdist_rpm',  "RPM distribution"),
                      'gztar': ('bdist_dumb', "gzip'ed tar file"),
                      'bztar': ('bdist_dumb', "bzip2'ed tar file"),
                      'xztar': ('bdist_dumb', "xz'ed tar file"),
                      'ztar':  ('bdist_dumb', "compressed tar file"),
                      'tar':   ('bdist_dumb', "tar file"),
                      'wininst': ('bdist_wininst',
                                  "Windows executable installer"),
                      'zip':   ('bdist_dumb', "ZIP file"),
                      'msi':   ('bdist_msi',  "Microsoft Installer")
                      }


    eleza initialize_options(self):
        self.bdist_base = Tupu
        self.plat_name = Tupu
        self.formats = Tupu
        self.dist_dir = Tupu
        self.skip_build = 0
        self.group = Tupu
        self.owner = Tupu

    eleza finalize_options(self):
        # have to finalize 'plat_name' before 'bdist_base'
        ikiwa self.plat_name ni Tupu:
            ikiwa self.skip_build:
                self.plat_name = get_platform()
            isipokua:
                self.plat_name = self.get_finalized_command('build').plat_name

        # 'bdist_base' -- parent of per-built-distribution-format
        # temporary directories (eg. we'll probably have
        # "build/bdist.<plat>/dumb", "build/bdist.<plat>/rpm", etc.)
        ikiwa self.bdist_base ni Tupu:
            build_base = self.get_finalized_command('build').build_base
            self.bdist_base = os.path.join(build_base,
                                           'bdist.' + self.plat_name)

        self.ensure_string_list('formats')
        ikiwa self.formats ni Tupu:
            jaribu:
                self.formats = [self.default_format[os.name]]
            except KeyError:
                 ashiria DistutilsPlatformError(
                      "don't know how to create built distributions "
                      "on platform %s" % os.name)

        ikiwa self.dist_dir ni Tupu:
            self.dist_dir = "dist"

    eleza run(self):
        # Figure out which sub-commands we need to run.
        commands = []
        kila format kwenye self.formats:
            jaribu:
                commands.append(self.format_command[format][0])
            except KeyError:
                 ashiria DistutilsOptionError("invalid format '%s'" % format)

        # Reinitialize na run each command.
        kila i kwenye range(len(self.formats)):
            cmd_name = commands[i]
            sub_cmd = self.reinitialize_command(cmd_name)
            ikiwa cmd_name sio kwenye self.no_format_option:
                sub_cmd.format = self.formats[i]

            # passing the owner na group names kila tar archiving
            ikiwa cmd_name == 'bdist_dumb':
                sub_cmd.owner = self.owner
                sub_cmd.group = self.group

            # If we're going to need to run this command again, tell it to
            # keep its temporary files around so subsequent runs go faster.
            ikiwa cmd_name kwenye commands[i+1:]:
                sub_cmd.keep_temp = 1
            self.run_command(cmd_name)
