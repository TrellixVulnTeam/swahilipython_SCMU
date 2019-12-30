"""
Main program kila 2to3.
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

    Output files can optionally be written to a different directory na ama
    have an extra file suffix appended to their name kila use kwenye situations
    where you do sio want to replace the input files.
    """

    eleza __init__(self, fixers, options, explicit, nobackups, show_diffs,
                 input_base_dir='', output_dir='', append_suffix=''):
        """
        Args:
            fixers: A list of fixers to agiza.
            options: A dict ukijumuisha RefactoringTool configuration.
            explicit: A list of fixers to run even ikiwa they are explicit.
            nobackups: If true no backup '.bak' files will be created kila those
                files that are being refactored.
            show_diffs: Should diffs of the refactoring be printed to stdout?
            input_base_dir: The base directory kila all input files.  This class
                will strip this path prefix off of filenames before substituting
                it ukijumuisha output_dir.  Only meaningful ikiwa output_dir ni supplied.
                All files processed by refactor() must start ukijumuisha this path.
            output_dir: If supplied, all converted files will be written into
                this directory tree instead of input_base_dir.
            append_suffix: If supplied, all files output by this tool will have
                this appended to their filename.  Useful kila changing .py to
                .py3 kila example by pitaing append_suffix='3'.
        """
        self.nobackups = nobackups
        self.show_diffs = show_diffs
        ikiwa input_base_dir na sio input_base_dir.endswith(os.sep):
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
            isipokua:
                ashiria ValueError('filename %s does sio start ukijumuisha the '
                                 'input_base_dir %s' % (
                                         filename, self._input_base_dir))
        ikiwa self._append_suffix:
            filename += self._append_suffix
        ikiwa orig_filename != filename:
            output_dir = os.path.dirname(filename)
            ikiwa sio os.path.isdir(output_dir) na output_dir:
                os.makedirs(output_dir)
            self.log_message('Writing converted %s to %s.', orig_filename,
                             filename)
        ikiwa sio self.nobackups:
            # Make backup
            backup = filename + ".bak"
            ikiwa os.path.lexists(backup):
                jaribu:
                    os.remove(backup)
                tatizo OSError kama err:
                    self.log_message("Can't remove backup %s", backup)
            jaribu:
                os.rename(filename, backup)
            tatizo OSError kama err:
                self.log_message("Can't rename %s to %s", filename, backup)
        # Actually write the new file
        write = super(StdoutRefactoringTool, self).write_file
        write(new_text, filename, old_text, encoding)
        ikiwa sio self.nobackups:
            shutil.copymode(backup, filename)
        ikiwa orig_filename != filename:
            # Preserve the file mode kwenye the new output directory.
            shutil.copymode(orig_filename, filename)

    eleza print_output(self, old, new, filename, equal):
        ikiwa equal:
            self.log_message("No changes to %s", filename)
        isipokua:
            self.log_message("Refactored %s", filename)
            ikiwa self.show_diffs:
                diff_lines = diff_texts(old, new, filename)
                jaribu:
                    ikiwa self.output_lock ni sio Tupu:
                        ukijumuisha self.output_lock:
                            kila line kwenye diff_lines:
                                andika(line)
                            sys.stdout.flush()
                    isipokua:
                        kila line kwenye diff_lines:
                            andika(line)
                tatizo UnicodeEncodeError:
                    warn("couldn't encode %s's diff kila your terminal" %
                         (filename,))
                    rudisha

eleza warn(msg):
    andika("WARNING: %s" % (msg,), file=sys.stderr)


eleza main(fixer_pkg, args=Tupu):
    """Main program.

    Args:
        fixer_pkg: the name of a package where the fixers are located.
        args: optional; a list of command line arguments. If omitted,
              sys.argv[1:] ni used.

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
                      help="Modify the grammar so that andika() ni a function")
    parser.add_option("-v", "--verbose", action="store_true",
                      help="More verbose logging")
    parser.add_option("--no-diffs", action="store_true",
                      help="Don't show diffs of the refactoring")
    parser.add_option("-w", "--write", action="store_true",
                      help="Write back modified files")
    parser.add_option("-n", "--nobackups", action="store_true", default=Uongo,
                      help="Don't write backups kila modified files")
    parser.add_option("-o", "--output-dir", action="store", type="str",
                      default="", help="Put output files kwenye this directory "
                      "instead of overwriting the input files.  Requires -n.")
    parser.add_option("-W", "--write-unchanged-files", action="store_true",
                      help="Also write files even ikiwa no changes were required"
                      " (useful ukijumuisha --output-dir); implies -w.")
    parser.add_option("--add-suffix", action="store", type="str", default="",
                      help="Append this string to all output filenames."
                      " Requires -n ikiwa non-empty.  "
                      "ex: --add-suffix='3' will generate .py3 files.")

    # Parse command line arguments
    refactor_stdin = Uongo
    flags = {}
    options, args = parser.parse_args(args)
    ikiwa options.write_unchanged_files:
        flags["write_unchanged_files"] = Kweli
        ikiwa sio options.write:
            warn("--write-unchanged-files/-W implies -w.")
        options.write = Kweli
    # If we allowed these, the original files would be renamed to backup names
    # but sio replaced.
    ikiwa options.output_dir na sio options.nobackups:
        parser.error("Can't use --output-dir/-o without -n.")
    ikiwa options.add_suffix na sio options.nobackups:
        parser.error("Can't use --add-suffix without -n.")

    ikiwa sio options.write na options.no_diffs:
        warn("not writing files na sio printing diffs; that's sio very useful")
    ikiwa sio options.write na options.nobackups:
        parser.error("Can't use -n without -w")
    ikiwa options.list_fixes:
        andika("Available transformations kila the -f/--fix option:")
        kila fixname kwenye refactor.get_all_fix_names(fixer_pkg):
            andika(fixname)
        ikiwa sio args:
            rudisha 0
    ikiwa sio args:
        andika("At least one file ama directory argument required.", file=sys.stderr)
        andika("Use --help to show usage.", file=sys.stderr)
        rudisha 2
    ikiwa "-" kwenye args:
        refactor_stdin = Kweli
        ikiwa options.write:
            andika("Can't write to stdin.", file=sys.stderr)
            rudisha 2
    ikiwa options.print_function:
        flags["print_function"] = Kweli

    # Set up logging handler
    level = logging.DEBUG ikiwa options.verbose isipokua logging.INFO
    logging.basicConfig(format='%(name)s: %(message)s', level=level)
    logger = logging.getLogger('lib2to3.main')

    # Initialize the refactoring tool
    avail_fixes = set(refactor.get_fixers_from_package(fixer_pkg))
    unwanted_fixes = set(fixer_pkg + ".fix_" + fix kila fix kwenye options.nofix)
    explicit = set()
    ikiwa options.fix:
        all_present = Uongo
        kila fix kwenye options.fix:
            ikiwa fix == "all":
                all_present = Kweli
            isipokua:
                explicit.add(fixer_pkg + ".fix_" + fix)
        requested = avail_fixes.union(explicit) ikiwa all_present isipokua explicit
    isipokua:
        requested = avail_fixes.union(explicit)
    fixer_names = requested.difference(unwanted_fixes)
    input_base_dir = os.path.commonprefix(args)
    ikiwa (input_base_dir na sio input_base_dir.endswith(os.sep)
        na sio os.path.isdir(input_base_dir)):
        # One ama more similar names were pitaed, their directory ni the base.
        # os.path.commonprefix() ni ignorant of path elements, this corrects
        # kila that weird API.
        input_base_dir = os.path.dirname(input_base_dir)
    ikiwa options.output_dir:
        input_base_dir = input_base_dir.rstrip(os.sep)
        logger.info('Output kwenye %r will mirror the input directory %r layout.',
                    options.output_dir, input_base_dir)
    rt = StdoutRefactoringTool(
            sorted(fixer_names), flags, sorted(explicit),
            options.nobackups, sio options.no_diffs,
            input_base_dir=input_base_dir,
            output_dir=options.output_dir,
            append_suffix=options.add_suffix)

    # Refactor all files na directories pitaed kama arguments
    ikiwa sio rt.errors:
        ikiwa refactor_stdin:
            rt.refactor_stdin()
        isipokua:
            jaribu:
                rt.refactor(args, options.write, options.doctests_only,
                            options.processes)
            tatizo refactor.MultiprocessingUnsupported:
                assert options.processes > 1
                andika("Sorry, -j isn't supported on this platform.",
                      file=sys.stderr)
                rudisha 1
        rt.summarize()

    # Return error status (0 ikiwa rt.errors ni zero)
    rudisha int(bool(rt.errors))
