"""
Main program for 2to3.
"""

kutoka __future__ agiza with_statement, print_function

agiza sys
agiza os
agiza difflib
agiza logging
agiza shutil
agiza optparse

kutoka . agiza refactor


eleza diff_texts(a, b, filename):
    """Return a unified diff of two strings."""
    a = a.splitlines()
    b = b.splitlines()
    rudisha difflib.unified_diff(a, b, filename, filename,
                                "(original)", "(refactored)",
                                lineterm="")


kundi StdoutRefactoringTool(refactor.MultiprocessRefactoringTool):
    """
    A refactoring tool that can avoid overwriting its input files.
    Prints output to stdout.

    Output files can optionally be written to a different directory and or
    have an extra file suffix appended to their name for use in situations
    where you do not want to replace the input files.
    """

    eleza __init__(self, fixers, options, explicit, nobackups, show_diffs,
                 input_base_dir='', output_dir='', append_suffix=''):
        """
        Args:
            fixers: A list of fixers to agiza.
            options: A dict with RefactoringTool configuration.
            explicit: A list of fixers to run even ikiwa they are explicit.
            nobackups: If true no backup '.bak' files will be created for those
                files that are being refactored.
            show_diffs: Should diffs of the refactoring be printed to stdout?
            input_base_dir: The base directory for all input files.  This class
                will strip this path prefix off of filenames before substituting
                it with output_dir.  Only meaningful ikiwa output_dir is supplied.
                All files processed by refactor() must start with this path.
            output_dir: If supplied, all converted files will be written into
                this directory tree instead of input_base_dir.
            append_suffix: If supplied, all files output by this tool will have
                this appended to their filename.  Useful for changing .py to
                .py3 for example by passing append_suffix='3'.
        """
        self.nobackups = nobackups
        self.show_diffs = show_diffs
        ikiwa input_base_dir and not input_base_dir.endswith(os.sep):
            input_base_dir += os.sep
        self._input_base_dir = input_base_dir
        self._output_dir = output_dir
        self._append_suffix = append_suffix
        super(StdoutRefactoringTool, self).__init__(fixers, options, explicit)

    eleza log_error(self, msg, *args, **kwargs):
        self.errors.append((msg, args, kwargs))
        self.logger.error(msg, *args, **kwargs)

    eleza write_file(self, new_text, filename, old_text, encoding):
        orig_filename = filename
        ikiwa self._output_dir:
            ikiwa filename.startswith(self._input_base_dir):
                filename = os.path.join(self._output_dir,
                                        filename[len(self._input_base_dir):])
            else:
                raise ValueError('filename %s does not start with the '
                                 'input_base_dir %s' % (
                                         filename, self._input_base_dir))
        ikiwa self._append_suffix:
            filename += self._append_suffix
        ikiwa orig_filename != filename:
            output_dir = os.path.dirname(filename)
            ikiwa not os.path.isdir(output_dir) and output_dir:
                os.makedirs(output_dir)
            self.log_message('Writing converted %s to %s.', orig_filename,
                             filename)
        ikiwa not self.nobackups:
            # Make backup
            backup = filename + ".bak"
            ikiwa os.path.lexists(backup):
                try:
                    os.remove(backup)
                except OSError as err:
                    self.log_message("Can't remove backup %s", backup)
            try:
                os.rename(filename, backup)
            except OSError as err:
                self.log_message("Can't rename %s to %s", filename, backup)
        # Actually write the new file
        write = super(StdoutRefactoringTool, self).write_file
        write(new_text, filename, old_text, encoding)
        ikiwa not self.nobackups:
            shutil.copymode(backup, filename)
        ikiwa orig_filename != filename:
            # Preserve the file mode in the new output directory.
            shutil.copymode(orig_filename, filename)

    eleza print_output(self, old, new, filename, equal):
        ikiwa equal:
            self.log_message("No changes to %s", filename)
        else:
            self.log_message("Refactored %s", filename)
            ikiwa self.show_diffs:
                diff_lines = diff_texts(old, new, filename)
                try:
                    ikiwa self.output_lock is not None:
                        with self.output_lock:
                            for line in diff_lines:
                                andika(line)
                            sys.stdout.flush()
                    else:
                        for line in diff_lines:
                            andika(line)
                except UnicodeEncodeError:
                    warn("couldn't encode %s's diff for your terminal" %
                         (filename,))
                    return

eleza warn(msg):
    andika("WARNING: %s" % (msg,), file=sys.stderr)


eleza main(fixer_pkg, args=None):
    """Main program.

    Args:
        fixer_pkg: the name of a package where the fixers are located.
        args: optional; a list of command line arguments. If omitted,
              sys.argv[1:] is used.

    Returns a suggested exit status (0, 1, 2).
    """
    # Set up option parser
    parser = optparse.OptionParser(usage="2to3 [options] file|dir ...")
    parser.add_option("-d", "--doctests_only", action="store_true",
                      help="Fix up doctests only")
    parser.add_option("-f", "--fix", action="append", default=[],
                      help="Each FIX specifies a transformation; default: all")
    parser.add_option("-j", "--processes", action="store", default=1,
                      type="int", help="Run 2to3 concurrently")
    parser.add_option("-x", "--nofix", action="append", default=[],
                      help="Prevent a transformation kutoka being run")
    parser.add_option("-l", "--list-fixes", action="store_true",
                      help="List available transformations")
    parser.add_option("-p", "--print-function", action="store_true",
                      help="Modify the grammar so that andika() is a function")
    parser.add_option("-v", "--verbose", action="store_true",
                      help="More verbose logging")
    parser.add_option("--no-diffs", action="store_true",
                      help="Don't show diffs of the refactoring")
    parser.add_option("-w", "--write", action="store_true",
                      help="Write back modified files")
    parser.add_option("-n", "--nobackups", action="store_true", default=False,
                      help="Don't write backups for modified files")
    parser.add_option("-o", "--output-dir", action="store", type="str",
                      default="", help="Put output files in this directory "
                      "instead of overwriting the input files.  Requires -n.")
    parser.add_option("-W", "--write-unchanged-files", action="store_true",
                      help="Also write files even ikiwa no changes were required"
                      " (useful with --output-dir); implies -w.")
    parser.add_option("--add-suffix", action="store", type="str", default="",
                      help="Append this string to all output filenames."
                      " Requires -n ikiwa non-empty.  "
                      "ex: --add-suffix='3' will generate .py3 files.")

    # Parse command line arguments
    refactor_stdin = False
    flags = {}
    options, args = parser.parse_args(args)
    ikiwa options.write_unchanged_files:
        flags["write_unchanged_files"] = True
        ikiwa not options.write:
            warn("--write-unchanged-files/-W implies -w.")
        options.write = True
    # If we allowed these, the original files would be renamed to backup names
    # but not replaced.
    ikiwa options.output_dir and not options.nobackups:
        parser.error("Can't use --output-dir/-o without -n.")
    ikiwa options.add_suffix and not options.nobackups:
        parser.error("Can't use --add-suffix without -n.")

    ikiwa not options.write and options.no_diffs:
        warn("not writing files and not printing diffs; that's not very useful")
    ikiwa not options.write and options.nobackups:
        parser.error("Can't use -n without -w")
    ikiwa options.list_fixes:
        andika("Available transformations for the -f/--fix option:")
        for fixname in refactor.get_all_fix_names(fixer_pkg):
            andika(fixname)
        ikiwa not args:
            rudisha 0
    ikiwa not args:
        andika("At least one file or directory argument required.", file=sys.stderr)
        andika("Use --help to show usage.", file=sys.stderr)
        rudisha 2
    ikiwa "-" in args:
        refactor_stdin = True
        ikiwa options.write:
            andika("Can't write to stdin.", file=sys.stderr)
            rudisha 2
    ikiwa options.print_function:
        flags["print_function"] = True

    # Set up logging handler
    level = logging.DEBUG ikiwa options.verbose else logging.INFO
    logging.basicConfig(format='%(name)s: %(message)s', level=level)
    logger = logging.getLogger('lib2to3.main')

    # Initialize the refactoring tool
    avail_fixes = set(refactor.get_fixers_kutoka_package(fixer_pkg))
    unwanted_fixes = set(fixer_pkg + ".fix_" + fix for fix in options.nofix)
    explicit = set()
    ikiwa options.fix:
        all_present = False
        for fix in options.fix:
            ikiwa fix == "all":
                all_present = True
            else:
                explicit.add(fixer_pkg + ".fix_" + fix)
        requested = avail_fixes.union(explicit) ikiwa all_present else explicit
    else:
        requested = avail_fixes.union(explicit)
    fixer_names = requested.difference(unwanted_fixes)
    input_base_dir = os.path.commonprefix(args)
    ikiwa (input_base_dir and not input_base_dir.endswith(os.sep)
        and not os.path.isdir(input_base_dir)):
        # One or more similar names were passed, their directory is the base.
        # os.path.commonprefix() is ignorant of path elements, this corrects
        # for that weird API.
        input_base_dir = os.path.dirname(input_base_dir)
    ikiwa options.output_dir:
        input_base_dir = input_base_dir.rstrip(os.sep)
        logger.info('Output in %r will mirror the input directory %r layout.',
                    options.output_dir, input_base_dir)
    rt = StdoutRefactoringTool(
            sorted(fixer_names), flags, sorted(explicit),
            options.nobackups, not options.no_diffs,
            input_base_dir=input_base_dir,
            output_dir=options.output_dir,
            append_suffix=options.add_suffix)

    # Refactor all files and directories passed as arguments
    ikiwa not rt.errors:
        ikiwa refactor_stdin:
            rt.refactor_stdin()
        else:
            try:
                rt.refactor(args, options.write, options.doctests_only,
                            options.processes)
            except refactor.MultiprocessingUnsupported:
                assert options.processes > 1
                andika("Sorry, -j isn't supported on this platform.",
                      file=sys.stderr)
                rudisha 1
        rt.summarize()

    # Return error status (0 ikiwa rt.errors is zero)
    rudisha int(bool(rt.errors))
