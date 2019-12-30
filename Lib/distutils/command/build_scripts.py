"""distutils.command.build_scripts

Implements the Distutils 'build_scripts' command."""

agiza os, re
kutoka stat agiza ST_MODE
kutoka distutils agiza sysconfig
kutoka distutils.core agiza Command
kutoka distutils.dep_util agiza newer
kutoka distutils.util agiza convert_path, Mixin2to3
kutoka distutils agiza log
agiza tokenize

# check ikiwa Python ni called on the first line ukijumuisha this expression
first_line_re = re.compile(b'^#!.*python[0-9.]*([ \t].*)?$')

kundi build_scripts(Command):

    description = "\"build\" scripts (copy na fixup #! line)"

    user_options = [
        ('build-dir=', 'd', "directory to \"build\" (copy) to"),
        ('force', 'f', "forcibly build everything (ignore file timestamps"),
        ('executable=', 'e', "specify final destination interpreter path"),
        ]

    boolean_options = ['force']


    eleza initialize_options(self):
        self.build_dir = Tupu
        self.scripts = Tupu
        self.force = Tupu
        self.executable = Tupu
        self.outfiles = Tupu

    eleza finalize_options(self):
        self.set_undefined_options('build',
                                   ('build_scripts', 'build_dir'),
                                   ('force', 'force'),
                                   ('executable', 'executable'))
        self.scripts = self.distribution.scripts

    eleza get_source_files(self):
        rudisha self.scripts

    eleza run(self):
        ikiwa sio self.scripts:
            rudisha
        self.copy_scripts()


    eleza copy_scripts(self):
        r"""Copy each script listed kwenye 'self.scripts'; ikiwa it's marked kama a
        Python script kwenye the Unix way (first line matches 'first_line_re',
        ie. starts ukijumuisha "\#!" na contains "python"), then adjust the first
        line to refer to the current Python interpreter kama we copy.
        """
        self.mkpath(self.build_dir)
        outfiles = []
        updated_files = []
        kila script kwenye self.scripts:
            adjust = Uongo
            script = convert_path(script)
            outfile = os.path.join(self.build_dir, os.path.basename(script))
            outfiles.append(outfile)

            ikiwa sio self.force na sio newer(script, outfile):
                log.debug("sio copying %s (up-to-date)", script)
                endelea

            # Always open the file, but ignore failures kwenye dry-run mode --
            # that way, we'll get accurate feedback ikiwa we can read the
            # script.
            jaribu:
                f = open(script, "rb")
            tatizo OSError:
                ikiwa sio self.dry_run:
                    raise
                f = Tupu
            isipokua:
                encoding, lines = tokenize.detect_encoding(f.readline)
                f.seek(0)
                first_line = f.readline()
                ikiwa sio first_line:
                    self.warn("%s ni an empty file (skipping)" % script)
                    endelea

                match = first_line_re.match(first_line)
                ikiwa match:
                    adjust = Kweli
                    post_interp = match.group(1) ama b''

            ikiwa adjust:
                log.info("copying na adjusting %s -> %s", script,
                         self.build_dir)
                updated_files.append(outfile)
                ikiwa sio self.dry_run:
                    ikiwa sio sysconfig.python_build:
                        executable = self.executable
                    isipokua:
                        executable = os.path.join(
                            sysconfig.get_config_var("BINDIR"),
                           "python%s%s" % (sysconfig.get_config_var("VERSION"),
                                           sysconfig.get_config_var("EXE")))
                    executable = os.fsencode(executable)
                    shebang = b"#!" + executable + post_interp + b"\n"
                    # Python parser starts to read a script using UTF-8 until
                    # it gets a #coding:xxx cookie. The shebang has to be the
                    # first line of a file, the #coding:xxx cookie cansio be
                    # written before. So the shebang has to be decodable from
                    # UTF-8.
                    jaribu:
                        shebang.decode('utf-8')
                    tatizo UnicodeDecodeError:
                        ashiria ValueError(
                            "The shebang ({!r}) ni sio decodable "
                            "kutoka utf-8".format(shebang))
                    # If the script ni encoded to a custom encoding (use a
                    # #coding:xxx cookie), the shebang has to be decodable from
                    # the script encoding too.
                    jaribu:
                        shebang.decode(encoding)
                    tatizo UnicodeDecodeError:
                        ashiria ValueError(
                            "The shebang ({!r}) ni sio decodable "
                            "kutoka the script encoding ({})"
                            .format(shebang, encoding))
                    ukijumuisha open(outfile, "wb") kama outf:
                        outf.write(shebang)
                        outf.writelines(f.readlines())
                ikiwa f:
                    f.close()
            isipokua:
                ikiwa f:
                    f.close()
                updated_files.append(outfile)
                self.copy_file(script, outfile)

        ikiwa os.name == 'posix':
            kila file kwenye outfiles:
                ikiwa self.dry_run:
                    log.info("changing mode of %s", file)
                isipokua:
                    oldmode = os.stat(file)[ST_MODE] & 0o7777
                    newmode = (oldmode | 0o555) & 0o7777
                    ikiwa newmode != oldmode:
                        log.info("changing mode of %s kutoka %o to %o",
                                 file, oldmode, newmode)
                        os.chmod(file, newmode)
        # XXX should we modify self.outfiles?
        rudisha outfiles, updated_files

kundi build_scripts_2to3(build_scripts, Mixin2to3):

    eleza copy_scripts(self):
        outfiles, updated_files = build_scripts.copy_scripts(self)
        ikiwa sio self.dry_run:
            self.run_2to3(updated_files)
        rudisha outfiles, updated_files
