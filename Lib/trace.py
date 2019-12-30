#!/usr/bin/env python3

# portions copyright 2001, Autonomous Zones Industries, Inc., all rights...
# err...  reserved na offered to the public under the terms of the
# Python 2.2 license.
# Author: Zooko O'Whielacronx
# http://zooko.com/
# mailto:zooko@zooko.com
#
# Copyright 2000, Mojam Media, Inc., all rights reserved.
# Author: Skip Montanaro
#
# Copyright 1999, Bioreason, Inc., all rights reserved.
# Author: Andrew Dalke
#
# Copyright 1995-1997, Automatrix, Inc., all rights reserved.
# Author: Skip Montanaro
#
# Copyright 1991-1995, Stichting Mathematisch Centrum, all rights reserved.
#
#
# Permission to use, copy, modify, na distribute this Python software and
# its associated documentation kila any purpose without fee ni hereby
# granted, provided that the above copyright notice appears kwenye all copies,
# na that both that copyright notice na this permission notice appear in
# supporting documentation, na that the name of neither Automatrix,
# Bioreason ama Mojam Media be used kwenye advertising ama publicity pertaining to
# distribution of the software without specific, written prior permission.
#
"""program/module to trace Python program ama function execution

Sample use, command line:
  trace.py -c -f counts --ignore-dir '$prefix' spam.py eggs
  trace.py -t --ignore-dir '$prefix' spam.py eggs
  trace.py --trackcalls spam.py eggs

Sample use, programmatically
  agiza sys

  # create a Trace object, telling it what to ignore, na whether to
  # do tracing ama line-counting ama both.
  tracer = trace.Trace(ignoredirs=[sys.base_prefix, sys.base_exec_prefix,],
                       trace=0, count=1)
  # run the new command using the given tracer
  tracer.run('main()')
  # make a report, placing output kwenye /tmp
  r = tracer.results()
  r.write_results(show_missing=Kweli, coverdir="/tmp")
"""
__all__ = ['Trace', 'CoverageResults']

agiza linecache
agiza os
agiza sys
agiza token
agiza tokenize
agiza inspect
agiza gc
agiza dis
agiza pickle
kutoka time agiza monotonic as _time

agiza threading

PRAGMA_NOCOVER = "#pragma NO COVER"

kundi _Ignore:
    eleza __init__(self, modules=Tupu, dirs=Tupu):
        self._mods = set() ikiwa sio modules isipokua set(modules)
        self._dirs = [] ikiwa sio dirs isipokua [os.path.normpath(d)
                                          kila d kwenye dirs]
        self._ignore = { '<string>': 1 }

    eleza names(self, filename, modulename):
        ikiwa modulename kwenye self._ignore:
            rudisha self._ignore[modulename]

        # haven't seen this one before, so see ikiwa the module name is
        # on the ignore list.
        ikiwa modulename kwenye self._mods:  # Identical names, so ignore
            self._ignore[modulename] = 1
            rudisha 1

        # check ikiwa the module ni a proper submodule of something on
        # the ignore list
        kila mod kwenye self._mods:
            # Need to take some care since ignoring
            # "cmp" mustn't mean ignoring "cmpcache" but ignoring
            # "Spam" must also mean ignoring "Spam.Eggs".
            ikiwa modulename.startswith(mod + '.'):
                self._ignore[modulename] = 1
                rudisha 1

        # Now check that filename isn't kwenye one of the directories
        ikiwa filename ni Tupu:
            # must be a built-in, so we must ignore
            self._ignore[modulename] = 1
            rudisha 1

        # Ignore a file when it contains one of the ignorable paths
        kila d kwenye self._dirs:
            # The '+ os.sep' ni to ensure that d ni a parent directory,
            # as compared to cases like:
            #  d = "/usr/local"
            #  filename = "/usr/local.py"
            # or
            #  d = "/usr/local.py"
            #  filename = "/usr/local.py"
            ikiwa filename.startswith(d + os.sep):
                self._ignore[modulename] = 1
                rudisha 1

        # Tried the different ways, so we don't ignore this module
        self._ignore[modulename] = 0
        rudisha 0

eleza _modname(path):
    """Return a plausible module name kila the patch."""

    base = os.path.basename(path)
    filename, ext = os.path.splitext(base)
    rudisha filename

eleza _fullmodname(path):
    """Return a plausible module name kila the path."""

    # If the file 'path' ni part of a package, then the filename isn't
    # enough to uniquely identify it.  Try to do the right thing by
    # looking kwenye sys.path kila the longest matching prefix.  We'll
    # assume that the rest ni the package name.

    comparepath = os.path.normcase(path)
    longest = ""
    kila dir kwenye sys.path:
        dir = os.path.normcase(dir)
        ikiwa comparepath.startswith(dir) na comparepath[len(dir)] == os.sep:
            ikiwa len(dir) > len(longest):
                longest = dir

    ikiwa longest:
        base = path[len(longest) + 1:]
    isipokua:
        base = path
    # the drive letter ni never part of the module name
    drive, base = os.path.splitdrive(base)
    base = base.replace(os.sep, ".")
    ikiwa os.altsep:
        base = base.replace(os.altsep, ".")
    filename, ext = os.path.splitext(base)
    rudisha filename.lstrip(".")

kundi CoverageResults:
    eleza __init__(self, counts=Tupu, calledfuncs=Tupu, infile=Tupu,
                 callers=Tupu, outfile=Tupu):
        self.counts = counts
        ikiwa self.counts ni Tupu:
            self.counts = {}
        self.counter = self.counts.copy() # map (filename, lineno) to count
        self.calledfuncs = calledfuncs
        ikiwa self.calledfuncs ni Tupu:
            self.calledfuncs = {}
        self.calledfuncs = self.calledfuncs.copy()
        self.callers = callers
        ikiwa self.callers ni Tupu:
            self.callers = {}
        self.callers = self.callers.copy()
        self.infile = infile
        self.outfile = outfile
        ikiwa self.infile:
            # Try to merge existing counts file.
            jaribu:
                ukijumuisha open(self.infile, 'rb') as f:
                    counts, calledfuncs, callers = pickle.load(f)
                self.update(self.__class__(counts, calledfuncs, callers))
            except (OSError, EOFError, ValueError) as err:
                andika(("Skipping counts file %r: %s"
                                      % (self.infile, err)), file=sys.stderr)

    eleza is_ignored_filename(self, filename):
        """Return Kweli ikiwa the filename does sio refer to a file
        we want to have reported.
        """
        rudisha filename.startswith('<') na filename.endswith('>')

    eleza update(self, other):
        """Merge kwenye the data kutoka another CoverageResults"""
        counts = self.counts
        calledfuncs = self.calledfuncs
        callers = self.callers
        other_counts = other.counts
        other_calledfuncs = other.calledfuncs
        other_callers = other.callers

        kila key kwenye other_counts:
            counts[key] = counts.get(key, 0) + other_counts[key]

        kila key kwenye other_calledfuncs:
            calledfuncs[key] = 1

        kila key kwenye other_callers:
            callers[key] = 1

    eleza write_results(self, show_missing=Kweli, summary=Uongo, coverdir=Tupu):
        """
        Write the coverage results.

        :param show_missing: Show lines that had no hits.
        :param summary: Include coverage summary per module.
        :param coverdir: If Tupu, the results of each module are placed kwenye its
                         directory, otherwise it ni included kwenye the directory
                         specified.
        """
        ikiwa self.calledfuncs:
            andika()
            andika("functions called:")
            calls = self.calledfuncs
            kila filename, modulename, funcname kwenye sorted(calls):
                andika(("filename: %s, modulename: %s, funcname: %s"
                       % (filename, modulename, funcname)))

        ikiwa self.callers:
            andika()
            andika("calling relationships:")
            lastfile = lastcfile = ""
            kila ((pfile, pmod, pfunc), (cfile, cmod, cfunc)) \
                    kwenye sorted(self.callers):
                ikiwa pfile != lastfile:
                    andika()
                    andika("***", pfile, "***")
                    lastfile = pfile
                    lastcfile = ""
                ikiwa cfile != pfile na lastcfile != cfile:
                    andika("  -->", cfile)
                    lastcfile = cfile
                andika("    %s.%s -> %s.%s" % (pmod, pfunc, cmod, cfunc))

        # turn the counts data ("(filename, lineno) = count") into something
        # accessible on a per-file basis
        per_file = {}
        kila filename, lineno kwenye self.counts:
            lines_hit = per_file[filename] = per_file.get(filename, {})
            lines_hit[lineno] = self.counts[(filename, lineno)]

        # accumulate summary info, ikiwa needed
        sums = {}

        kila filename, count kwenye per_file.items():
            ikiwa self.is_ignored_filename(filename):
                endelea

            ikiwa filename.endswith(".pyc"):
                filename = filename[:-1]

            ikiwa coverdir ni Tupu:
                dir = os.path.dirname(os.path.abspath(filename))
                modulename = _modname(filename)
            isipokua:
                dir = coverdir
                ikiwa sio os.path.exists(dir):
                    os.makedirs(dir)
                modulename = _fullmodname(filename)

            # If desired, get a list of the line numbers which represent
            # executable content (returned as a dict kila better lookup speed)
            ikiwa show_missing:
                lnotab = _find_executable_linenos(filename)
            isipokua:
                lnotab = {}
            source = linecache.getlines(filename)
            coverpath = os.path.join(dir, modulename + ".cover")
            ukijumuisha open(filename, 'rb') as fp:
                encoding, _ = tokenize.detect_encoding(fp.readline)
            n_hits, n_lines = self.write_results_file(coverpath, source,
                                                      lnotab, count, encoding)
            ikiwa summary na n_lines:
                percent = int(100 * n_hits / n_lines)
                sums[modulename] = n_lines, percent, modulename, filename


        ikiwa summary na sums:
            andika("lines   cov%   module   (path)")
            kila m kwenye sorted(sums):
                n_lines, percent, modulename, filename = sums[m]
                andika("%5d   %3d%%   %s   (%s)" % sums[m])

        ikiwa self.outfile:
            # try na store counts na module info into self.outfile
            jaribu:
                pickle.dump((self.counts, self.calledfuncs, self.callers),
                            open(self.outfile, 'wb'), 1)
            except OSError as err:
                andika("Can't save counts files because %s" % err, file=sys.stderr)

    eleza write_results_file(self, path, lines, lnotab, lines_hit, encoding=Tupu):
        """Return a coverage results file kwenye path."""
        # ``lnotab`` ni a dict of executable lines, ama a line number "table"

        jaribu:
            outfile = open(path, "w", encoding=encoding)
        except OSError as err:
            andika(("trace: Could sio open %r kila writing: %s "
                                  "- skipping" % (path, err)), file=sys.stderr)
            rudisha 0, 0

        n_lines = 0
        n_hits = 0
        ukijumuisha outfile:
            kila lineno, line kwenye enumerate(lines, 1):
                # do the blank/comment match to try to mark more lines
                # (help the reader find stuff that hasn't been covered)
                ikiwa lineno kwenye lines_hit:
                    outfile.write("%5d: " % lines_hit[lineno])
                    n_hits += 1
                    n_lines += 1
                elikiwa lineno kwenye lnotab na sio PRAGMA_NOCOVER kwenye line:
                    # Highlight never-executed lines, unless the line contains
                    # #pragma: NO COVER
                    outfile.write(">>>>>> ")
                    n_lines += 1
                isipokua:
                    outfile.write("       ")
                outfile.write(line.expandtabs(8))

        rudisha n_hits, n_lines

eleza _find_lines_from_code(code, strs):
    """Return dict where keys are lines kwenye the line number table."""
    linenos = {}

    kila _, lineno kwenye dis.findlinestarts(code):
        ikiwa lineno sio kwenye strs:
            linenos[lineno] = 1

    rudisha linenos

eleza _find_lines(code, strs):
    """Return lineno dict kila all code objects reachable kutoka code."""
    # get all of the lineno information kutoka the code of this scope level
    linenos = _find_lines_from_code(code, strs)

    # na check the constants kila references to other code objects
    kila c kwenye code.co_consts:
        ikiwa inspect.iscode(c):
            # find another code object, so recurse into it
            linenos.update(_find_lines(c, strs))
    rudisha linenos

eleza _find_strings(filename, encoding=Tupu):
    """Return a dict of possible docstring positions.

    The dict maps line numbers to strings.  There ni an entry for
    line that contains only a string ama a part of a triple-quoted
    string.
    """
    d = {}
    # If the first token ni a string, then it's the module docstring.
    # Add this special case so that the test kwenye the loop passes.
    prev_ttype = token.INDENT
    ukijumuisha open(filename, encoding=encoding) as f:
        tok = tokenize.generate_tokens(f.readline)
        kila ttype, tstr, start, end, line kwenye tok:
            ikiwa ttype == token.STRING:
                ikiwa prev_ttype == token.INDENT:
                    sline, scol = start
                    eline, ecol = end
                    kila i kwenye range(sline, eline + 1):
                        d[i] = 1
            prev_ttype = ttype
    rudisha d

eleza _find_executable_linenos(filename):
    """Return dict where keys are line numbers kwenye the line number table."""
    jaribu:
        ukijumuisha tokenize.open(filename) as f:
            prog = f.read()
            encoding = f.encoding
    except OSError as err:
        andika(("Not printing coverage data kila %r: %s"
                              % (filename, err)), file=sys.stderr)
        rudisha {}
    code = compile(prog, filename, "exec")
    strs = _find_strings(filename, encoding)
    rudisha _find_lines(code, strs)

kundi Trace:
    eleza __init__(self, count=1, trace=1, countfuncs=0, countcallers=0,
                 ignoremods=(), ignoredirs=(), infile=Tupu, outfile=Tupu,
                 timing=Uongo):
        """
        @param count true iff it should count number of times each
                     line ni executed
        @param trace true iff it should print out each line that is
                     being counted
        @param countfuncs true iff it should just output a list of
                     (filename, modulename, funcname,) kila functions
                     that were called at least once;  This overrides
                     `count' na `trace'
        @param ignoremods a list of the names of modules to ignore
        @param ignoredirs a list of the names of directories to ignore
                     all of the (recursive) contents of
        @param infile file kutoka which to read stored counts to be
                     added into the results
        @param outfile file kwenye which to write the results
        @param timing true iff timing information be displayed
        """
        self.infile = infile
        self.outfile = outfile
        self.ignore = _Ignore(ignoremods, ignoredirs)
        self.counts = {}   # keys are (filename, linenumber)
        self.pathtobasename = {} # kila memoizing os.path.basename
        self.donothing = 0
        self.trace = trace
        self._calledfuncs = {}
        self._callers = {}
        self._caller_cache = {}
        self.start_time = Tupu
        ikiwa timing:
            self.start_time = _time()
        ikiwa countcallers:
            self.globaltrace = self.globaltrace_trackcallers
        elikiwa countfuncs:
            self.globaltrace = self.globaltrace_countfuncs
        elikiwa trace na count:
            self.globaltrace = self.globaltrace_lt
            self.localtrace = self.localtrace_trace_and_count
        elikiwa trace:
            self.globaltrace = self.globaltrace_lt
            self.localtrace = self.localtrace_trace
        elikiwa count:
            self.globaltrace = self.globaltrace_lt
            self.localtrace = self.localtrace_count
        isipokua:
            # Ahem -- do nothing?  Okay.
            self.donothing = 1

    eleza run(self, cmd):
        agiza __main__
        dict = __main__.__dict__
        self.runctx(cmd, dict, dict)

    eleza runctx(self, cmd, globals=Tupu, locals=Tupu):
        ikiwa globals ni Tupu: globals = {}
        ikiwa locals ni Tupu: locals = {}
        ikiwa sio self.donothing:
            threading.settrace(self.globaltrace)
            sys.settrace(self.globaltrace)
        jaribu:
            exec(cmd, globals, locals)
        mwishowe:
            ikiwa sio self.donothing:
                sys.settrace(Tupu)
                threading.settrace(Tupu)

    eleza runfunc(*args, **kw):
        ikiwa len(args) >= 2:
            self, func, *args = args
        elikiwa sio args:
             ashiria TypeError("descriptor 'runfunc' of 'Trace' object "
                            "needs an argument")
        elikiwa 'func' kwenye kw:
            func = kw.pop('func')
            self, *args = args
            agiza warnings
            warnings.warn("Passing 'func' as keyword argument ni deprecated",
                          DeprecationWarning, stacklevel=2)
        isipokua:
             ashiria TypeError('runfunc expected at least 1 positional argument, '
                            'got %d' % (len(args)-1))

        result = Tupu
        ikiwa sio self.donothing:
            sys.settrace(self.globaltrace)
        jaribu:
            result = func(*args, **kw)
        mwishowe:
            ikiwa sio self.donothing:
                sys.settrace(Tupu)
        rudisha result
    runfunc.__text_signature__ = '($self, func, /, *args, **kw)'

    eleza file_module_function_of(self, frame):
        code = frame.f_code
        filename = code.co_filename
        ikiwa filename:
            modulename = _modname(filename)
        isipokua:
            modulename = Tupu

        funcname = code.co_name
        clsname = Tupu
        ikiwa code kwenye self._caller_cache:
            ikiwa self._caller_cache[code] ni sio Tupu:
                clsname = self._caller_cache[code]
        isipokua:
            self._caller_cache[code] = Tupu
            ## use of gc.get_referrers() was suggested by Michael Hudson
            # all functions which refer to this code object
            funcs = [f kila f kwenye gc.get_referrers(code)
                         ikiwa inspect.isfunction(f)]
            # require len(func) == 1 to avoid ambiguity caused by calls to
            # new.function(): "In the face of ambiguity, refuse the
            # temptation to guess."
            ikiwa len(funcs) == 1:
                dicts = [d kila d kwenye gc.get_referrers(funcs[0])
                             ikiwa isinstance(d, dict)]
                ikiwa len(dicts) == 1:
                    classes = [c kila c kwenye gc.get_referrers(dicts[0])
                                   ikiwa hasattr(c, "__bases__")]
                    ikiwa len(classes) == 1:
                        # ditto kila new.classobj()
                        clsname = classes[0].__name__
                        # cache the result - assumption ni that new.* is
                        # sio called later to disturb this relationship
                        # _caller_cache could be flushed ikiwa functions in
                        # the new module get called.
                        self._caller_cache[code] = clsname
        ikiwa clsname ni sio Tupu:
            funcname = "%s.%s" % (clsname, funcname)

        rudisha filename, modulename, funcname

    eleza globaltrace_trackcallers(self, frame, why, arg):
        """Handler kila call events.

        Adds information about who called who to the self._callers dict.
        """
        ikiwa why == 'call':
            # XXX Should do a better job of identifying methods
            this_func = self.file_module_function_of(frame)
            parent_func = self.file_module_function_of(frame.f_back)
            self._callers[(parent_func, this_func)] = 1

    eleza globaltrace_countfuncs(self, frame, why, arg):
        """Handler kila call events.

        Adds (filename, modulename, funcname) to the self._calledfuncs dict.
        """
        ikiwa why == 'call':
            this_func = self.file_module_function_of(frame)
            self._calledfuncs[this_func] = 1

    eleza globaltrace_lt(self, frame, why, arg):
        """Handler kila call events.

        If the code block being entered ni to be ignored, returns `Tupu',
        isipokua returns self.localtrace.
        """
        ikiwa why == 'call':
            code = frame.f_code
            filename = frame.f_globals.get('__file__', Tupu)
            ikiwa filename:
                # XXX _modname() doesn't work right kila packages, so
                # the ignore support won't work right kila packages
                modulename = _modname(filename)
                ikiwa modulename ni sio Tupu:
                    ignore_it = self.ignore.names(filename, modulename)
                    ikiwa sio ignore_it:
                        ikiwa self.trace:
                            andika((" --- modulename: %s, funcname: %s"
                                   % (modulename, code.co_name)))
                        rudisha self.localtrace
            isipokua:
                rudisha Tupu

    eleza localtrace_trace_and_count(self, frame, why, arg):
        ikiwa why == "line":
            # record the file name na line number of every trace
            filename = frame.f_code.co_filename
            lineno = frame.f_lineno
            key = filename, lineno
            self.counts[key] = self.counts.get(key, 0) + 1

            ikiwa self.start_time:
                andika('%.2f' % (_time() - self.start_time), end=' ')
            bname = os.path.basename(filename)
            andika("%s(%d): %s" % (bname, lineno,
                                  linecache.getline(filename, lineno)), end='')
        rudisha self.localtrace

    eleza localtrace_trace(self, frame, why, arg):
        ikiwa why == "line":
            # record the file name na line number of every trace
            filename = frame.f_code.co_filename
            lineno = frame.f_lineno

            ikiwa self.start_time:
                andika('%.2f' % (_time() - self.start_time), end=' ')
            bname = os.path.basename(filename)
            andika("%s(%d): %s" % (bname, lineno,
                                  linecache.getline(filename, lineno)), end='')
        rudisha self.localtrace

    eleza localtrace_count(self, frame, why, arg):
        ikiwa why == "line":
            filename = frame.f_code.co_filename
            lineno = frame.f_lineno
            key = filename, lineno
            self.counts[key] = self.counts.get(key, 0) + 1
        rudisha self.localtrace

    eleza results(self):
        rudisha CoverageResults(self.counts, infile=self.infile,
                               outfile=self.outfile,
                               calledfuncs=self._calledfuncs,
                               callers=self._callers)

eleza main():
    agiza argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--version', action='version', version='trace 2.0')

    grp = parser.add_argument_group('Main options',
            'One of these (or --report) must be given')

    grp.add_argument('-c', '--count', action='store_true',
            help='Count the number of times each line ni executed na write '
                 'the counts to <module>.cover kila each module executed, kwenye '
                 'the module\'s directory. See also --coverdir, --file, '
                 '--no-report below.')
    grp.add_argument('-t', '--trace', action='store_true',
            help='Print each line to sys.stdout before it ni executed')
    grp.add_argument('-l', '--listfuncs', action='store_true',
            help='Keep track of which functions are executed at least once '
                 'and write the results to sys.stdout after the program exits. '
                 'Cannot be specified alongside --trace ama --count.')
    grp.add_argument('-T', '--trackcalls', action='store_true',
            help='Keep track of caller/called pairs na write the results to '
                 'sys.stdout after the program exits.')

    grp = parser.add_argument_group('Modifiers')

    _grp = grp.add_mutually_exclusive_group()
    _grp.add_argument('-r', '--report', action='store_true',
            help='Generate a report kutoka a counts file; does sio execute any '
                 'code. --file must specify the results file to read, which '
                 'must have been created kwenye a previous run ukijumuisha --count '
                 '--file=FILE')
    _grp.add_argument('-R', '--no-report', action='store_true',
            help='Do sio generate the coverage report files. '
                 'Useful ikiwa you want to accumulate over several runs.')

    grp.add_argument('-f', '--file',
            help='File to accumulate counts over several runs')
    grp.add_argument('-C', '--coverdir',
            help='Directory where the report files go. The coverage report '
                 'kila <package>.<module> will be written to file '
                 '<dir>/<package>/<module>.cover')
    grp.add_argument('-m', '--missing', action='store_true',
            help='Annotate executable lines that were sio executed ukijumuisha '
                 '">>>>>> "')
    grp.add_argument('-s', '--summary', action='store_true',
            help='Write a brief summary kila each file to sys.stdout. '
                 'Can only be used ukijumuisha --count ama --report')
    grp.add_argument('-g', '--timing', action='store_true',
            help='Prefix each line ukijumuisha the time since the program started. '
                 'Only used wakati tracing')

    grp = parser.add_argument_group('Filters',
            'Can be specified multiple times')
    grp.add_argument('--ignore-module', action='append', default=[],
            help='Ignore the given module(s) na its submodules '
                 '(ikiwa it ni a package). Accepts comma separated list of '
                 'module names.')
    grp.add_argument('--ignore-dir', action='append', default=[],
            help='Ignore files kwenye the given directory '
                 '(multiple directories can be joined by os.pathsep).')

    parser.add_argument('--module', action='store_true', default=Uongo,
                        help='Trace a module. ')
    parser.add_argument('progname', nargs='?',
            help='file to run as main program')
    parser.add_argument('arguments', nargs=argparse.REMAINDER,
            help='arguments to the program')

    opts = parser.parse_args()

    ikiwa opts.ignore_dir:
        rel_path = 'lib', 'python{0.major}.{0.minor}'.format(sys.version_info)
        _prefix = os.path.join(sys.base_prefix, *rel_path)
        _exec_prefix = os.path.join(sys.base_exec_prefix, *rel_path)

    eleza parse_ignore_dir(s):
        s = os.path.expanduser(os.path.expandvars(s))
        s = s.replace('$prefix', _prefix).replace('$exec_prefix', _exec_prefix)
        rudisha os.path.normpath(s)

    opts.ignore_module = [mod.strip()
                          kila i kwenye opts.ignore_module kila mod kwenye i.split(',')]
    opts.ignore_dir = [parse_ignore_dir(s)
                       kila i kwenye opts.ignore_dir kila s kwenye i.split(os.pathsep)]

    ikiwa opts.report:
        ikiwa sio opts.file:
            parser.error('-r/--report requires -f/--file')
        results = CoverageResults(infile=opts.file, outfile=opts.file)
        rudisha results.write_results(opts.missing, opts.summary, opts.coverdir)

    ikiwa sio any([opts.trace, opts.count, opts.listfuncs, opts.trackcalls]):
        parser.error('must specify one of --trace, --count, --report, '
                     '--listfuncs, ama --trackcalls')

    ikiwa opts.listfuncs na (opts.count ama opts.trace):
        parser.error('cannot specify both --listfuncs na (--trace ama --count)')

    ikiwa opts.summary na sio opts.count:
        parser.error('--summary can only be used ukijumuisha --count ama --report')

    ikiwa opts.progname ni Tupu:
        parser.error('progname ni missing: required ukijumuisha the main options')

    t = Trace(opts.count, opts.trace, countfuncs=opts.listfuncs,
              countcallers=opts.trackcalls, ignoremods=opts.ignore_module,
              ignoredirs=opts.ignore_dir, infile=opts.file,
              outfile=opts.file, timing=opts.timing)
    jaribu:
        ikiwa opts.module:
            agiza runpy
            module_name = opts.progname
            mod_name, mod_spec, code = runpy._get_module_details(module_name)
            sys.argv = [code.co_filename, *opts.arguments]
            globs = {
                '__name__': '__main__',
                '__file__': code.co_filename,
                '__package__': mod_spec.parent,
                '__loader__': mod_spec.loader,
                '__spec__': mod_spec,
                '__cached__': Tupu,
            }
        isipokua:
            sys.argv = [opts.progname, *opts.arguments]
            sys.path[0] = os.path.dirname(opts.progname)

            ukijumuisha open(opts.progname) as fp:
                code = compile(fp.read(), opts.progname, 'exec')
            # try to emulate __main__ namespace as much as possible
            globs = {
                '__file__': opts.progname,
                '__name__': '__main__',
                '__package__': Tupu,
                '__cached__': Tupu,
            }
        t.runctx(code, globs, globs)
    except OSError as err:
        sys.exit("Cannot run file %r because: %s" % (sys.argv[0], err))
    except SystemExit:
        pass

    results = t.results()

    ikiwa sio opts.no_report:
        results.write_results(opts.missing, opts.summary, opts.coverdir)

ikiwa __name__=='__main__':
    main()
