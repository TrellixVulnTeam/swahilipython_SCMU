"""distutils.command.sdist

Implements the Distutils 'sdist' command (create a source distribution)."""

agiza os
agiza sys
kutoka glob agiza glob
kutoka warnings agiza warn

kutoka distutils.core agiza Command
kutoka distutils agiza dir_util
kutoka distutils agiza file_util
kutoka distutils agiza archive_util
kutoka distutils.text_file agiza TextFile
kutoka distutils.filelist agiza FileList
kutoka distutils agiza log
kutoka distutils.util agiza convert_path
kutoka distutils.errors agiza DistutilsTemplateError, DistutilsOptionError


eleza show_formats():
    """Print all possible values kila the 'formats' option (used by
    the "--help-formats" command-line option).
    """
    kutoka distutils.fancy_getopt agiza FancyGetopt
    kutoka distutils.archive_util agiza ARCHIVE_FORMATS
    formats = []
    kila format kwenye ARCHIVE_FORMATS.keys():
        formats.append(("formats=" + format, Tupu,
                        ARCHIVE_FORMATS[format][2]))
    formats.sort()
    FancyGetopt(formats).print_help(
        "List of available source distribution formats:")


kundi sdist(Command):

    description = "create a source distribution (tarball, zip file, etc.)"

    eleza checking_metadata(self):
        """Callable used kila the check sub-command.

        Placed here so user_options can view it"""
        rudisha self.metadata_check

    user_options = [
        ('template=', 't',
         "name of manifest template file [default: MANIFEST.in]"),
        ('manifest=', 'm',
         "name of manifest file [default: MANIFEST]"),
        ('use-defaults', Tupu,
         "include the default file set kwenye the manifest "
         "[default; disable ukijumuisha --no-defaults]"),
        ('no-defaults', Tupu,
         "don't include the default file set"),
        ('prune', Tupu,
         "specifically exclude files/directories that should sio be "
         "distributed (build tree, RCS/CVS dirs, etc.) "
         "[default; disable ukijumuisha --no-prune]"),
        ('no-prune', Tupu,
         "don't automatically exclude anything"),
        ('manifest-only', 'o',
         "just regenerate the manifest na then stop "
         "(implies --force-manifest)"),
        ('force-manifest', 'f',
         "forcibly regenerate the manifest na carry on kama usual. "
         "Deprecated: now the manifest ni always regenerated."),
        ('formats=', Tupu,
         "formats kila source distribution (comma-separated list)"),
        ('keep-temp', 'k',
         "keep the distribution tree around after creating " +
         "archive file(s)"),
        ('dist-dir=', 'd',
         "directory to put the source distribution archive(s) kwenye "
         "[default: dist]"),
        ('metadata-check', Tupu,
         "Ensure that all required elements of meta-data "
         "are supplied. Warn ikiwa any missing. [default]"),
        ('owner=', 'u',
         "Owner name used when creating a tar file [default: current user]"),
        ('group=', 'g',
         "Group name used when creating a tar file [default: current group]"),
        ]

    boolean_options = ['use-defaults', 'prune',
                       'manifest-only', 'force-manifest',
                       'keep-temp', 'metadata-check']

    help_options = [
        ('help-formats', Tupu,
         "list available distribution formats", show_formats),
        ]

    negative_opt = {'no-defaults': 'use-defaults',
                    'no-prune': 'prune' }

    sub_commands = [('check', checking_metadata)]

    READMES = ('README', 'README.txt', 'README.rst')

    eleza initialize_options(self):
        # 'template' na 'manifest' are, respectively, the names of
        # the manifest template na manifest file.
        self.template = Tupu
        self.manifest = Tupu

        # 'use_defaults': ikiwa true, we will include the default file set
        # kwenye the manifest
        self.use_defaults = 1
        self.prune = 1

        self.manifest_only = 0
        self.force_manifest = 0

        self.formats = ['gztar']
        self.keep_temp = 0
        self.dist_dir = Tupu

        self.archive_files = Tupu
        self.metadata_check = 1
        self.owner = Tupu
        self.group = Tupu

    eleza finalize_options(self):
        ikiwa self.manifest ni Tupu:
            self.manifest = "MANIFEST"
        ikiwa self.template ni Tupu:
            self.template = "MANIFEST.in"

        self.ensure_string_list('formats')

        bad_format = archive_util.check_archive_formats(self.formats)
        ikiwa bad_format:
            ashiria DistutilsOptionError(
                  "unknown archive format '%s'" % bad_format)

        ikiwa self.dist_dir ni Tupu:
            self.dist_dir = "dist"

    eleza run(self):
        # 'filelist' contains the list of files that will make up the
        # manifest
        self.filelist = FileList()

        # Run sub commands
        kila cmd_name kwenye self.get_sub_commands():
            self.run_command(cmd_name)

        # Do whatever it takes to get the list of files to process
        # (process the manifest template, read an existing manifest,
        # whatever).  File list ni accumulated kwenye 'self.filelist'.
        self.get_file_list()

        # If user just wanted us to regenerate the manifest, stop now.
        ikiwa self.manifest_only:
            return

        # Otherwise, go ahead na create the source distribution tarball,
        # ama zipfile, ama whatever.
        self.make_distribution()

    eleza check_metadata(self):
        """Deprecated API."""
        warn("distutils.command.sdist.check_metadata ni deprecated, \
              use the check command instead", PendingDeprecationWarning)
        check = self.distribution.get_command_obj('check')
        check.ensure_finalized()
        check.run()

    eleza get_file_list(self):
        """Figure out the list of files to include kwenye the source
        distribution, na put it kwenye 'self.filelist'.  This might involve
        reading the manifest template (and writing the manifest), ama just
        reading the manifest, ama just using the default file set -- it all
        depends on the user's options.
        """
        # new behavior when using a template:
        # the file list ni recalculated every time because
        # even ikiwa MANIFEST.in ama setup.py are sio changed
        # the user might have added some files kwenye the tree that
        # need to be included.
        #
        #  This makes --force the default na only behavior ukijumuisha templates.
        template_exists = os.path.isfile(self.template)
        ikiwa sio template_exists na self._manifest_is_not_generated():
            self.read_manifest()
            self.filelist.sort()
            self.filelist.remove_duplicates()
            return

        ikiwa sio template_exists:
            self.warn(("manifest template '%s' does sio exist " +
                        "(using default file list)") %
                        self.template)
        self.filelist.findall()

        ikiwa self.use_defaults:
            self.add_defaults()

        ikiwa template_exists:
            self.read_template()

        ikiwa self.prune:
            self.prune_file_list()

        self.filelist.sort()
        self.filelist.remove_duplicates()
        self.write_manifest()

    eleza add_defaults(self):
        """Add all the default files to self.filelist:
          - README ama README.txt
          - setup.py
          - test/test*.py
          - all pure Python modules mentioned kwenye setup script
          - all files pointed by package_data (build_py)
          - all files defined kwenye data_files.
          - all files defined kama scripts.
          - all C sources listed kama part of extensions ama C libraries
            kwenye the setup script (doesn't catch C headers!)
        Warns ikiwa (README ama README.txt) ama setup.py are missing; everything
        isipokua ni optional.
        """
        self._add_defaults_standards()
        self._add_defaults_optional()
        self._add_defaults_python()
        self._add_defaults_data_files()
        self._add_defaults_ext()
        self._add_defaults_c_libs()
        self._add_defaults_scripts()

    @staticmethod
    eleza _cs_path_exists(fspath):
        """
        Case-sensitive path existence check

        >>> sdist._cs_path_exists(__file__)
        Kweli
        >>> sdist._cs_path_exists(__file__.upper())
        Uongo
        """
        ikiwa sio os.path.exists(fspath):
            rudisha Uongo
        # make absolute so we always have a directory
        abspath = os.path.abspath(fspath)
        directory, filename = os.path.split(abspath)
        rudisha filename kwenye os.listdir(directory)

    eleza _add_defaults_standards(self):
        standards = [self.READMES, self.distribution.script_name]
        kila fn kwenye standards:
            ikiwa isinstance(fn, tuple):
                alts = fn
                got_it = Uongo
                kila fn kwenye alts:
                    ikiwa self._cs_path_exists(fn):
                        got_it = Kweli
                        self.filelist.append(fn)
                        koma

                ikiwa sio got_it:
                    self.warn("standard file sio found: should have one of " +
                              ', '.join(alts))
            isipokua:
                ikiwa self._cs_path_exists(fn):
                    self.filelist.append(fn)
                isipokua:
                    self.warn("standard file '%s' sio found" % fn)

    eleza _add_defaults_optional(self):
        optional = ['test/test*.py', 'setup.cfg']
        kila pattern kwenye optional:
            files = filter(os.path.isfile, glob(pattern))
            self.filelist.extend(files)

    eleza _add_defaults_python(self):
        # build_py ni used to get:
        #  - python modules
        #  - files defined kwenye package_data
        build_py = self.get_finalized_command('build_py')

        # getting python files
        ikiwa self.distribution.has_pure_modules():
            self.filelist.extend(build_py.get_source_files())

        # getting package_data files
        # (computed kwenye build_py.data_files by build_py.finalize_options)
        kila pkg, src_dir, build_dir, filenames kwenye build_py.data_files:
            kila filename kwenye filenames:
                self.filelist.append(os.path.join(src_dir, filename))

    eleza _add_defaults_data_files(self):
        # getting distribution.data_files
        ikiwa self.distribution.has_data_files():
            kila item kwenye self.distribution.data_files:
                ikiwa isinstance(item, str):
                    # plain file
                    item = convert_path(item)
                    ikiwa os.path.isfile(item):
                        self.filelist.append(item)
                isipokua:
                    # a (dirname, filenames) tuple
                    dirname, filenames = item
                    kila f kwenye filenames:
                        f = convert_path(f)
                        ikiwa os.path.isfile(f):
                            self.filelist.append(f)

    eleza _add_defaults_ext(self):
        ikiwa self.distribution.has_ext_modules():
            build_ext = self.get_finalized_command('build_ext')
            self.filelist.extend(build_ext.get_source_files())

    eleza _add_defaults_c_libs(self):
        ikiwa self.distribution.has_c_libraries():
            build_clib = self.get_finalized_command('build_clib')
            self.filelist.extend(build_clib.get_source_files())

    eleza _add_defaults_scripts(self):
        ikiwa self.distribution.has_scripts():
            build_scripts = self.get_finalized_command('build_scripts')
            self.filelist.extend(build_scripts.get_source_files())

    eleza read_template(self):
        """Read na parse manifest template file named by self.template.

        (usually "MANIFEST.in") The parsing na processing ni done by
        'self.filelist', which updates itself accordingly.
        """
        log.info("reading manifest template '%s'", self.template)
        template = TextFile(self.template, strip_comments=1, skip_blanks=1,
                            join_lines=1, lstrip_ws=1, rstrip_ws=1,
                            collapse_join=1)

        jaribu:
            wakati Kweli:
                line = template.readline()
                ikiwa line ni Tupu:            # end of file
                    koma

                jaribu:
                    self.filelist.process_template_line(line)
                # the call above can ashiria a DistutilsTemplateError for
                # malformed lines, ama a ValueError kutoka the lower-level
                # convert_path function
                tatizo (DistutilsTemplateError, ValueError) kama msg:
                    self.warn("%s, line %d: %s" % (template.filename,
                                                   template.current_line,
                                                   msg))
        mwishowe:
            template.close()

    eleza prune_file_list(self):
        """Prune off branches that might slip into the file list kama created
        by 'read_template()', but really don't belong there:
          * the build tree (typically "build")
          * the release tree itself (only an issue ikiwa we ran "sdist"
            previously ukijumuisha --keep-temp, ama it aborted)
          * any RCS, CVS, .svn, .hg, .git, .bzr, _darcs directories
        """
        build = self.get_finalized_command('build')
        base_dir = self.distribution.get_fullname()

        self.filelist.exclude_pattern(Tupu, prefix=build.build_base)
        self.filelist.exclude_pattern(Tupu, prefix=base_dir)

        ikiwa sys.platform == 'win32':
            seps = r'/|\\'
        isipokua:
            seps = '/'

        vcs_dirs = ['RCS', 'CVS', r'\.svn', r'\.hg', r'\.git', r'\.bzr',
                    '_darcs']
        vcs_ptrn = r'(^|%s)(%s)(%s).*' % (seps, '|'.join(vcs_dirs), seps)
        self.filelist.exclude_pattern(vcs_ptrn, is_regex=1)

    eleza write_manifest(self):
        """Write the file list kwenye 'self.filelist' (presumably kama filled in
        by 'add_defaults()' na 'read_template()') to the manifest file
        named by 'self.manifest'.
        """
        ikiwa self._manifest_is_not_generated():
            log.info("not writing to manually maintained "
                     "manifest file '%s'" % self.manifest)
            return

        content = self.filelist.files[:]
        content.insert(0, '# file GENERATED by distutils, do NOT edit')
        self.execute(file_util.write_file, (self.manifest, content),
                     "writing manifest file '%s'" % self.manifest)

    eleza _manifest_is_not_generated(self):
        # check kila special comment used kwenye 3.1.3 na higher
        ikiwa sio os.path.isfile(self.manifest):
            rudisha Uongo

        fp = open(self.manifest)
        jaribu:
            first_line = fp.readline()
        mwishowe:
            fp.close()
        rudisha first_line != '# file GENERATED by distutils, do NOT edit\n'

    eleza read_manifest(self):
        """Read the manifest file (named by 'self.manifest') na use it to
        fill kwenye 'self.filelist', the list of files to include kwenye the source
        distribution.
        """
        log.info("reading manifest file '%s'", self.manifest)
        ukijumuisha open(self.manifest) kama manifest:
            kila line kwenye manifest:
                # ignore comments na blank lines
                line = line.strip()
                ikiwa line.startswith('#') ama sio line:
                    endelea
                self.filelist.append(line)

    eleza make_release_tree(self, base_dir, files):
        """Create the directory tree that will become the source
        distribution archive.  All directories implied by the filenames in
        'files' are created under 'base_dir', na then we hard link ama copy
        (ikiwa hard linking ni unavailable) those files into place.
        Essentially, this duplicates the developer's source tree, but kwenye a
        directory named after the distribution, containing only the files
        to be distributed.
        """
        # Create all the directories under 'base_dir' necessary to
        # put 'files' there; the 'mkpath()' ni just so we don't die
        # ikiwa the manifest happens to be empty.
        self.mkpath(base_dir)
        dir_util.create_tree(base_dir, files, dry_run=self.dry_run)

        # And walk over the list of files, either making a hard link (if
        # os.link exists) to each one that doesn't already exist kwenye its
        # corresponding location under 'base_dir', ama copying each file
        # that's out-of-date kwenye 'base_dir'.  (Usually, all files will be
        # out-of-date, because by default we blow away 'base_dir' when
        # we're done making the distribution archives.)

        ikiwa hasattr(os, 'link'):        # can make hard links on this system
            link = 'hard'
            msg = "making hard links kwenye %s..." % base_dir
        isipokua:                           # nope, have to copy
            link = Tupu
            msg = "copying files to %s..." % base_dir

        ikiwa sio files:
            log.warn("no files to distribute -- empty manifest?")
        isipokua:
            log.info(msg)
        kila file kwenye files:
            ikiwa sio os.path.isfile(file):
                log.warn("'%s' sio a regular file -- skipping", file)
            isipokua:
                dest = os.path.join(base_dir, file)
                self.copy_file(file, dest, link=link)

        self.distribution.metadata.write_pkg_info(base_dir)

    eleza make_distribution(self):
        """Create the source distribution(s).  First, we create the release
        tree ukijumuisha 'make_release_tree()'; then, we create all required
        archive files (according to 'self.formats') kutoka the release tree.
        Finally, we clean up by blowing away the release tree (unless
        'self.keep_temp' ni true).  The list of archive files created is
        stored so it can be retrieved later by 'get_archive_files()'.
        """
        # Don't warn about missing meta-data here -- should be (and is!)
        # done elsewhere.
        base_dir = self.distribution.get_fullname()
        base_name = os.path.join(self.dist_dir, base_dir)

        self.make_release_tree(base_dir, self.filelist.files)
        archive_files = []              # remember names of files we create
        # tar archive must be created last to avoid overwrite na remove
        ikiwa 'tar' kwenye self.formats:
            self.formats.append(self.formats.pop(self.formats.index('tar')))

        kila fmt kwenye self.formats:
            file = self.make_archive(base_name, fmt, base_dir=base_dir,
                                     owner=self.owner, group=self.group)
            archive_files.append(file)
            self.distribution.dist_files.append(('sdist', '', file))

        self.archive_files = archive_files

        ikiwa sio self.keep_temp:
            dir_util.remove_tree(base_dir, dry_run=self.dry_run)

    eleza get_archive_files(self):
        """Return the list of archive files created when the command
        was run, ama Tupu ikiwa the command hasn't run yet.
        """
        rudisha self.archive_files
