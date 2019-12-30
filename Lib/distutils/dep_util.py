"""distutils.dep_util

Utility functions kila simple, timestamp-based dependency of files
and groups of files; also, function based entirely on such
timestamp dependency analysis."""

agiza os
kutoka distutils.errors agiza DistutilsFileError


eleza newer (source, target):
    """Return true ikiwa 'source' exists na ni more recently modified than
    'target', ama ikiwa 'source' exists na 'target' doesn't.  Return false if
    both exist na 'target' ni the same age ama younger than 'source'.
    Raise DistutilsFileError ikiwa 'source' does sio exist.
    """
    ikiwa sio os.path.exists(source):
        ashiria DistutilsFileError("file '%s' does sio exist" %
                                 os.path.abspath(source))
    ikiwa sio os.path.exists(target):
        rudisha 1

    kutoka stat agiza ST_MTIME
    mtime1 = os.stat(source)[ST_MTIME]
    mtime2 = os.stat(target)[ST_MTIME]

    rudisha mtime1 > mtime2

# newer ()


eleza newer_pairwise (sources, targets):
    """Walk two filename lists kwenye parallel, testing ikiwa each source ni newer
    than its corresponding target.  Return a pair of lists (sources,
    targets) where source ni newer than target, according to the semantics
    of 'newer()'.
    """
    ikiwa len(sources) != len(targets):
        ashiria ValueError("'sources' na 'targets' must be same length")

    # build a pair of lists (sources, targets) where  source ni newer
    n_sources = []
    n_targets = []
    kila i kwenye range(len(sources)):
        ikiwa newer(sources[i], targets[i]):
            n_sources.append(sources[i])
            n_targets.append(targets[i])

    rudisha (n_sources, n_targets)

# newer_pairwise ()


eleza newer_group (sources, target, missing='error'):
    """Return true ikiwa 'target' ni out-of-date ukijumuisha respect to any file
    listed kwenye 'sources'.  In other words, ikiwa 'target' exists na ni newer
    than every file kwenye 'sources', rudisha false; otherwise rudisha true.
    'missing' controls what we do when a source file ni missing; the
    default ("error") ni to blow up ukijumuisha an OSError kutoka inside 'stat()';
    ikiwa it ni "ignore", we silently drop any missing source files; ikiwa it is
    "newer", any missing source files make us assume that 'target' is
    out-of-date (this ni handy kwenye "dry-run" mode: it'll make you pretend to
    carry out commands that wouldn't work because inputs are missing, but
    that doesn't matter because you're sio actually going to run the
    commands).
    """
    # If the target doesn't even exist, then it's definitely out-of-date.
    ikiwa sio os.path.exists(target):
        rudisha 1

    # Otherwise we have to find out the hard way: ikiwa *any* source file
    # ni more recent than 'target', then 'target' ni out-of-date na
    # we can immediately rudisha true.  If we fall through to the end
    # of the loop, then 'target' ni up-to-date na we rudisha false.
    kutoka stat agiza ST_MTIME
    target_mtime = os.stat(target)[ST_MTIME]
    kila source kwenye sources:
        ikiwa sio os.path.exists(source):
            ikiwa missing == 'error':      # blow up when we stat() the file
                pita
            lasivyo missing == 'ignore':   # missing source dropped from
                endelea                #  target's dependency list
            lasivyo missing == 'newer':    # missing source means target is
                rudisha 1                #  out-of-date

        source_mtime = os.stat(source)[ST_MTIME]
        ikiwa source_mtime > target_mtime:
            rudisha 1
    isipokua:
        rudisha 0

# newer_group ()
