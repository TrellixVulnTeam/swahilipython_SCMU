"""Utilities kila comparing files na directories.

Classes:
    dircmp

Functions:
    cmp(f1, f2, shallow=Kweli) -> int
    cmpfiles(a, b, common) -> ([], [], [])
    clear_cache()

"""

agiza os
agiza stat
kutoka itertools agiza filterfalse

__all__ = ['clear_cache', 'cmp', 'dircmp', 'cmpfiles', 'DEFAULT_IGNORES']

_cache = {}
BUFSIZE = 8*1024

DEFAULT_IGNORES = [
    'RCS', 'CVS', 'tags', '.git', '.hg', '.bzr', '_darcs', '__pycache__']

eleza clear_cache():
    """Clear the filecmp cache."""
    _cache.clear()

eleza cmp(f1, f2, shallow=Kweli):
    """Compare two files.

    Arguments:

    f1 -- First file name

    f2 -- Second file name

    shallow -- Just check stat signature (do sio read the files).
               defaults to Kweli.

    Return value:

    Kweli ikiwa the files are the same, Uongo otherwise.

    This function uses a cache kila past comparisons na the results,
    ukijumuisha cache entries invalidated ikiwa their stat information
    changes.  The cache may be cleared by calling clear_cache().

    """

    s1 = _sig(os.stat(f1))
    s2 = _sig(os.stat(f2))
    ikiwa s1[0] != stat.S_IFREG ama s2[0] != stat.S_IFREG:
        rudisha Uongo
    ikiwa shallow na s1 == s2:
        rudisha Kweli
    ikiwa s1[1] != s2[1]:
        rudisha Uongo

    outcome = _cache.get((f1, f2, s1, s2))
    ikiwa outcome ni Tupu:
        outcome = _do_cmp(f1, f2)
        ikiwa len(_cache) > 100:      # limit the maximum size of the cache
            clear_cache()
        _cache[f1, f2, s1, s2] = outcome
    rudisha outcome

eleza _sig(st):
    rudisha (stat.S_IFMT(st.st_mode),
            st.st_size,
            st.st_mtime)

eleza _do_cmp(f1, f2):
    bufsize = BUFSIZE
    ukijumuisha open(f1, 'rb') kama fp1, open(f2, 'rb') kama fp2:
        wakati Kweli:
            b1 = fp1.read(bufsize)
            b2 = fp2.read(bufsize)
            ikiwa b1 != b2:
                rudisha Uongo
            ikiwa sio b1:
                rudisha Kweli

# Directory comparison class.
#
kundi dircmp:
    """A kundi that manages the comparison of 2 directories.

    dircmp(a, b, ignore=Tupu, hide=Tupu)
      A na B are directories.
      IGNORE ni a list of names to ignore,
        defaults to DEFAULT_IGNORES.
      HIDE ni a list of names to hide,
        defaults to [os.curdir, os.pardir].

    High level usage:
      x = dircmp(dir1, dir2)
      x.report() -> prints a report on the differences between dir1 na dir2
       ama
      x.report_partial_closure() -> prints report on differences between dir1
            na dir2, na reports on common immediate subdirectories.
      x.report_full_closure() -> like report_partial_closure,
            but fully recursive.

    Attributes:
     left_list, right_list: The files kwenye dir1 na dir2,
        filtered by hide na ignore.
     common: a list of names kwenye both dir1 na dir2.
     left_only, right_only: names only kwenye dir1, dir2.
     common_dirs: subdirectories kwenye both dir1 na dir2.
     common_files: files kwenye both dir1 na dir2.
     common_funny: names kwenye both dir1 na dir2 where the type differs between
        dir1 na dir2, ama the name ni sio stat-able.
     same_files: list of identical files.
     diff_files: list of filenames which differ.
     funny_files: list of files which could sio be compared.
     subdirs: a dictionary of dircmp objects, keyed by names kwenye common_dirs.
     """

    eleza __init__(self, a, b, ignore=Tupu, hide=Tupu): # Initialize
        self.left = a
        self.right = b
        ikiwa hide ni Tupu:
            self.hide = [os.curdir, os.pardir] # Names never to be shown
        isipokua:
            self.hide = hide
        ikiwa ignore ni Tupu:
            self.ignore = DEFAULT_IGNORES
        isipokua:
            self.ignore = ignore

    eleza phase0(self): # Compare everything tatizo common subdirectories
        self.left_list = _filter(os.listdir(self.left),
                                 self.hide+self.ignore)
        self.right_list = _filter(os.listdir(self.right),
                                  self.hide+self.ignore)
        self.left_list.sort()
        self.right_list.sort()

    eleza phase1(self): # Compute common names
        a = dict(zip(map(os.path.normcase, self.left_list), self.left_list))
        b = dict(zip(map(os.path.normcase, self.right_list), self.right_list))
        self.common = list(map(a.__getitem__, filter(b.__contains__, a)))
        self.left_only = list(map(a.__getitem__, filterfalse(b.__contains__, a)))
        self.right_only = list(map(b.__getitem__, filterfalse(a.__contains__, b)))

    eleza phase2(self): # Distinguish files, directories, funnies
        self.common_dirs = []
        self.common_files = []
        self.common_funny = []

        kila x kwenye self.common:
            a_path = os.path.join(self.left, x)
            b_path = os.path.join(self.right, x)

            ok = 1
            jaribu:
                a_stat = os.stat(a_path)
            tatizo OSError kama why:
                # andika('Can\'t stat', a_path, ':', why.args[1])
                ok = 0
            jaribu:
                b_stat = os.stat(b_path)
            tatizo OSError kama why:
                # andika('Can\'t stat', b_path, ':', why.args[1])
                ok = 0

            ikiwa ok:
                a_type = stat.S_IFMT(a_stat.st_mode)
                b_type = stat.S_IFMT(b_stat.st_mode)
                ikiwa a_type != b_type:
                    self.common_funny.append(x)
                lasivyo stat.S_ISDIR(a_type):
                    self.common_dirs.append(x)
                lasivyo stat.S_ISREG(a_type):
                    self.common_files.append(x)
                isipokua:
                    self.common_funny.append(x)
            isipokua:
                self.common_funny.append(x)

    eleza phase3(self): # Find out differences between common files
        xx = cmpfiles(self.left, self.right, self.common_files)
        self.same_files, self.diff_files, self.funny_files = xx

    eleza phase4(self): # Find out differences between common subdirectories
        # A new dircmp object ni created kila each common subdirectory,
        # these are stored kwenye a dictionary indexed by filename.
        # The hide na ignore properties are inherited kutoka the parent
        self.subdirs = {}
        kila x kwenye self.common_dirs:
            a_x = os.path.join(self.left, x)
            b_x = os.path.join(self.right, x)
            self.subdirs[x]  = dircmp(a_x, b_x, self.ignore, self.hide)

    eleza phase4_closure(self): # Recursively call phase4() on subdirectories
        self.phase4()
        kila sd kwenye self.subdirs.values():
            sd.phase4_closure()

    eleza report(self): # Print a report on the differences between a na b
        # Output format ni purposely lousy
        andika('diff', self.left, self.right)
        ikiwa self.left_only:
            self.left_only.sort()
            andika('Only in', self.left, ':', self.left_only)
        ikiwa self.right_only:
            self.right_only.sort()
            andika('Only in', self.right, ':', self.right_only)
        ikiwa self.same_files:
            self.same_files.sort()
            andika('Identical files :', self.same_files)
        ikiwa self.diff_files:
            self.diff_files.sort()
            andika('Differing files :', self.diff_files)
        ikiwa self.funny_files:
            self.funny_files.sort()
            andika('Trouble ukijumuisha common files :', self.funny_files)
        ikiwa self.common_dirs:
            self.common_dirs.sort()
            andika('Common subdirectories :', self.common_dirs)
        ikiwa self.common_funny:
            self.common_funny.sort()
            andika('Common funny cases :', self.common_funny)

    eleza report_partial_closure(self): # Print reports on self na on subdirs
        self.report()
        kila sd kwenye self.subdirs.values():
            andika()
            sd.report()

    eleza report_full_closure(self): # Report on self na subdirs recursively
        self.report()
        kila sd kwenye self.subdirs.values():
            andika()
            sd.report_full_closure()

    methodmap = dict(subdirs=phase4,
                     same_files=phase3, diff_files=phase3, funny_files=phase3,
                     common_dirs = phase2, common_files=phase2, common_funny=phase2,
                     common=phase1, left_only=phase1, right_only=phase1,
                     left_list=phase0, right_list=phase0)

    eleza __getattr__(self, attr):
        ikiwa attr haiko kwenye self.methodmap:
            ashiria AttributeError(attr)
        self.methodmap[attr](self)
        rudisha getattr(self, attr)

eleza cmpfiles(a, b, common, shallow=Kweli):
    """Compare common files kwenye two directories.

    a, b -- directory names
    common -- list of file names found kwenye both directories
    shallow -- ikiwa true, do comparison based solely on stat() information

    Returns a tuple of three lists:
      files that compare equal
      files that are different
      filenames that aren't regular files.

    """
    res = ([], [], [])
    kila x kwenye common:
        ax = os.path.join(a, x)
        bx = os.path.join(b, x)
        res[_cmp(ax, bx, shallow)].append(x)
    rudisha res


# Compare two files.
# Return:
#       0 kila equal
#       1 kila different
#       2 kila funny cases (can't stat, etc.)
#
eleza _cmp(a, b, sh, abs=abs, cmp=cmp):
    jaribu:
        rudisha sio abs(cmp(a, b, sh))
    tatizo OSError:
        rudisha 2


# Return a copy ukijumuisha items that occur kwenye skip removed.
#
eleza _filter(flist, skip):
    rudisha list(filterfalse(skip.__contains__, flist))


# Demonstration na testing.
#
eleza demo():
    agiza sys
    agiza getopt
    options, args = getopt.getopt(sys.argv[1:], 'r')
    ikiwa len(args) != 2:
        ashiria getopt.GetoptError('need exactly two args', Tupu)
    dd = dircmp(args[0], args[1])
    ikiwa ('-r', '') kwenye options:
        dd.report_full_closure()
    isipokua:
        dd.report()

ikiwa __name__ == '__main__':
    demo()
