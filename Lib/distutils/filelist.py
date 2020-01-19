"""distutils.filelist

Provides the FileList class, used kila poking about the filesystem
and building lists of files.
"""

agiza os, re
agiza fnmatch
agiza functools
kutoka distutils.util agiza convert_path
kutoka distutils.errors agiza DistutilsTemplateError, DistutilsInternalError
kutoka distutils agiza log

kundi FileList:
    """A list of files built by on exploring the filesystem na filtered by
    applying various patterns to what we find there.

    Instance attributes:
      dir
        directory kutoka which files will be taken -- only used if
        'allfiles' sio supplied to constructor
      files
        list of filenames currently being built/filtered/manipulated
      allfiles
        complete list of files under consideration (ie. without any
        filtering applied)
    """

    eleza __init__(self, warn=Tupu, debug_print=Tupu):
        # ignore argument to FileList, but keep them kila backwards
        # compatibility
        self.allfiles = Tupu
        self.files = []

    eleza set_allfiles(self, allfiles):
        self.allfiles = allfiles

    eleza findall(self, dir=os.curdir):
        self.allfiles = findall(dir)

    eleza debug_andika(self, msg):
        """Print 'msg' to stdout ikiwa the global DEBUG (taken kutoka the
        DISTUTILS_DEBUG environment variable) flag ni true.
        """
        kutoka distutils.debug agiza DEBUG
        ikiwa DEBUG:
            andika(msg)

    # -- List-like methods ---------------------------------------------

    eleza append(self, item):
        self.files.append(item)

    eleza extend(self, items):
        self.files.extend(items)

    eleza sort(self):
        # Not a strict lexical sort!
        sortable_files = sorted(map(os.path.split, self.files))
        self.files = []
        kila sort_tuple kwenye sortable_files:
            self.files.append(os.path.join(*sort_tuple))


    # -- Other miscellaneous utility methods ---------------------------

    eleza remove_duplicates(self):
        # Assumes list has been sorted!
        kila i kwenye range(len(self.files) - 1, 0, -1):
            ikiwa self.files[i] == self.files[i - 1]:
                toa self.files[i]


    # -- "File template" methods ---------------------------------------

    eleza _parse_template_line(self, line):
        words = line.split()
        action = words[0]

        patterns = dir = dir_pattern = Tupu

        ikiwa action kwenye ('include', 'exclude',
                      'global-include', 'global-exclude'):
            ikiwa len(words) < 2:
                ashiria DistutilsTemplateError(
                      "'%s' expects <pattern1> <pattern2> ..." % action)
            patterns = [convert_path(w) kila w kwenye words[1:]]
        lasivyo action kwenye ('recursive-include', 'recursive-exclude'):
            ikiwa len(words) < 3:
                ashiria DistutilsTemplateError(
                      "'%s' expects <dir> <pattern1> <pattern2> ..." % action)
            dir = convert_path(words[1])
            patterns = [convert_path(w) kila w kwenye words[2:]]
        lasivyo action kwenye ('graft', 'prune'):
            ikiwa len(words) != 2:
                ashiria DistutilsTemplateError(
                      "'%s' expects a single <dir_pattern>" % action)
            dir_pattern = convert_path(words[1])
        isipokua:
            ashiria DistutilsTemplateError("unknown action '%s'" % action)

        rudisha (action, patterns, dir, dir_pattern)

    eleza process_template_line(self, line):
        # Parse the line: split it up, make sure the right number of words
        # ni there, na rudisha the relevant words.  'action' ni always
        # defined: it's the first word of the line.  Which of the other
        # three are defined depends on the action; it'll be either
        # patterns, (dir na patterns), ama (dir_pattern).
        (action, patterns, dir, dir_pattern) = self._parse_template_line(line)

        # OK, now we know that the action ni valid na we have the
        # right number of words on the line kila that action -- so we
        # can proceed ukijumuisha minimal error-checking.
        ikiwa action == 'include':
            self.debug_andika("include " + ' '.join(patterns))
            kila pattern kwenye patterns:
                ikiwa sio self.include_pattern(pattern, anchor=1):
                    log.warn("warning: no files found matching '%s'",
                             pattern)

        lasivyo action == 'exclude':
            self.debug_andika("exclude " + ' '.join(patterns))
            kila pattern kwenye patterns:
                ikiwa sio self.exclude_pattern(pattern, anchor=1):
                    log.warn(("warning: no previously-included files "
                              "found matching '%s'"), pattern)

        lasivyo action == 'global-include':
            self.debug_andika("global-include " + ' '.join(patterns))
            kila pattern kwenye patterns:
                ikiwa sio self.include_pattern(pattern, anchor=0):
                    log.warn(("warning: no files found matching '%s' "
                              "anywhere kwenye distribution"), pattern)

        lasivyo action == 'global-exclude':
            self.debug_andika("global-exclude " + ' '.join(patterns))
            kila pattern kwenye patterns:
                ikiwa sio self.exclude_pattern(pattern, anchor=0):
                    log.warn(("warning: no previously-included files matching "
                              "'%s' found anywhere kwenye distribution"),
                             pattern)

        lasivyo action == 'recursive-include':
            self.debug_andika("recursive-include %s %s" %
                             (dir, ' '.join(patterns)))
            kila pattern kwenye patterns:
                ikiwa sio self.include_pattern(pattern, prefix=dir):
                    log.warn(("warning: no files found matching '%s' "
                                "under directory '%s'"),
                             pattern, dir)

        lasivyo action == 'recursive-exclude':
            self.debug_andika("recursive-exclude %s %s" %
                             (dir, ' '.join(patterns)))
            kila pattern kwenye patterns:
                ikiwa sio self.exclude_pattern(pattern, prefix=dir):
                    log.warn(("warning: no previously-included files matching "
                              "'%s' found under directory '%s'"),
                             pattern, dir)

        lasivyo action == 'graft':
            self.debug_andika("graft " + dir_pattern)
            ikiwa sio self.include_pattern(Tupu, prefix=dir_pattern):
                log.warn("warning: no directories found matching '%s'",
                         dir_pattern)

        lasivyo action == 'prune':
            self.debug_andika("prune " + dir_pattern)
            ikiwa sio self.exclude_pattern(Tupu, prefix=dir_pattern):
                log.warn(("no previously-included directories found "
                          "matching '%s'"), dir_pattern)
        isipokua:
            ashiria DistutilsInternalError(
                  "this cannot happen: invalid action '%s'" % action)


    # -- Filtering/selection methods -----------------------------------

    eleza include_pattern(self, pattern, anchor=1, prefix=Tupu, is_regex=0):
        """Select strings (presumably filenames) kutoka 'self.files' that
        match 'pattern', a Unix-style wildcard (glob) pattern.  Patterns
        are sio quite the same kama implemented by the 'fnmatch' module: '*'
        na '?'  match non-special characters, where "special" ni platform-
        dependent: slash on Unix; colon, slash, na backslash on
        DOS/Windows; na colon on Mac OS.

        If 'anchor' ni true (the default), then the pattern match ni more
        stringent: "*.py" will match "foo.py" but sio "foo/bar.py".  If
        'anchor' ni false, both of these will match.

        If 'prefix' ni supplied, then only filenames starting ukijumuisha 'prefix'
        (itself a pattern) na ending ukijumuisha 'pattern', ukijumuisha anything kwenye between
        them, will match.  'anchor' ni ignored kwenye this case.

        If 'is_regex' ni true, 'anchor' na 'prefix' are ignored, na
        'pattern' ni assumed to be either a string containing a regex ama a
        regex object -- no translation ni done, the regex ni just compiled
        na used as-is.

        Selected strings will be added to self.files.

        Return Kweli ikiwa files are found, Uongo otherwise.
        """
        # XXX docstring lying about what the special chars are?
        files_found = Uongo
        pattern_re = translate_pattern(pattern, anchor, prefix, is_regex)
        self.debug_andika("include_pattern: applying regex r'%s'" %
                         pattern_re.pattern)

        # delayed loading of allfiles list
        ikiwa self.allfiles ni Tupu:
            self.findall()

        kila name kwenye self.allfiles:
            ikiwa pattern_re.search(name):
                self.debug_andika(" adding " + name)
                self.files.append(name)
                files_found = Kweli
        rudisha files_found


    eleza exclude_pattern (self, pattern,
                         anchor=1, prefix=Tupu, is_regex=0):
        """Remove strings (presumably filenames) kutoka 'files' that match
        'pattern'.  Other parameters are the same kama for
        'include_pattern()', above.
        The list 'self.files' ni modified kwenye place.
        Return Kweli ikiwa files are found, Uongo otherwise.
        """
        files_found = Uongo
        pattern_re = translate_pattern(pattern, anchor, prefix, is_regex)
        self.debug_andika("exclude_pattern: applying regex r'%s'" %
                         pattern_re.pattern)
        kila i kwenye range(len(self.files)-1, -1, -1):
            ikiwa pattern_re.search(self.files[i]):
                self.debug_andika(" removing " + self.files[i])
                toa self.files[i]
                files_found = Kweli
        rudisha files_found


# ----------------------------------------------------------------------
# Utility functions

eleza _find_all_simple(path):
    """
    Find all files under 'path'
    """
    results = (
        os.path.join(base, file)
        kila base, dirs, files kwenye os.walk(path, followlinks=Kweli)
        kila file kwenye files
    )
    rudisha filter(os.path.isfile, results)


eleza findall(dir=os.curdir):
    """
    Find all files under 'dir' na rudisha the list of full filenames.
    Unless dir ni '.', rudisha full filenames ukijumuisha dir prepended.
    """
    files = _find_all_simple(dir)
    ikiwa dir == os.curdir:
        make_rel = functools.partial(os.path.relpath, start=dir)
        files = map(make_rel, files)
    rudisha list(files)


eleza glob_to_re(pattern):
    """Translate a shell-like glob pattern to a regular expression; rudisha
    a string containing the regex.  Differs kutoka 'fnmatch.translate()' kwenye
    that '*' does sio match "special characters" (which are
    platform-specific).
    """
    pattern_re = fnmatch.translate(pattern)

    # '?' na '*' kwenye the glob pattern become '.' na '.*' kwenye the RE, which
    # IMHO ni wrong -- '?' na '*' aren't supposed to match slash kwenye Unix,
    # na by extension they shouldn't match such "special characters" under
    # any OS.  So change all non-escaped dots kwenye the RE to match any
    # character tatizo the special characters (currently: just os.sep).
    sep = os.sep
    ikiwa os.sep == '\\':
        # we're using a regex to manipulate a regex, so we need
        # to escape the backslash twice
        sep = r'\\\\'
    escaped = r'\1[^%s]' % sep
    pattern_re = re.sub(r'((?<!\\)(\\\\)*)\.', escaped, pattern_re)
    rudisha pattern_re


eleza translate_pattern(pattern, anchor=1, prefix=Tupu, is_regex=0):
    """Translate a shell-like wildcard pattern to a compiled regular
    expression.  Return the compiled regex.  If 'is_regex' true,
    then 'pattern' ni directly compiled to a regex (ikiwa it's a string)
    ama just returned as-is (assumes it's a regex object).
    """
    ikiwa is_regex:
        ikiwa isinstance(pattern, str):
            rudisha re.compile(pattern)
        isipokua:
            rudisha pattern

    # ditch start na end characters
    start, _, end = glob_to_re('_').partition('_')

    ikiwa pattern:
        pattern_re = glob_to_re(pattern)
        assert pattern_re.startswith(start) na pattern_re.endswith(end)
    isipokua:
        pattern_re = ''

    ikiwa prefix ni sio Tupu:
        prefix_re = glob_to_re(prefix)
        assert prefix_re.startswith(start) na prefix_re.endswith(end)
        prefix_re = prefix_re[len(start): len(prefix_re) - len(end)]
        sep = os.sep
        ikiwa os.sep == '\\':
            sep = r'\\'
        pattern_re = pattern_re[len(start): len(pattern_re) - len(end)]
        pattern_re = r'%s\A%s%s.*%s%s' % (start, prefix_re, sep, pattern_re, end)
    isipokua:                               # no prefix -- respect anchor flag
        ikiwa anchor:
            pattern_re = r'%s\A%s' % (start, pattern_re[len(start):])

    rudisha re.compile(pattern_re)
