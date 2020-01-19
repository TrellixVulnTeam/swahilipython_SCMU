"""distutils.dir_util

Utility functions kila manipulating directories na directory trees."""

agiza os
agiza errno
kutoka distutils.errors agiza DistutilsFileError, DistutilsInternalError
kutoka distutils agiza log

# cache kila by mkpath() -- kwenye addition to cheapening redundant calls,
# eliminates redundant "creating /foo/bar/baz" messages kwenye dry-run mode
_path_created = {}

# I don't use os.makedirs because a) it's new to Python 1.5.2, na
# b) it blows up ikiwa the directory already exists (I want to silently
# succeed kwenye that case).
eleza mkpath(name, mode=0o777, verbose=1, dry_run=0):
    """Create a directory na any missing ancestor directories.

    If the directory already exists (or ikiwa 'name' ni the empty string, which
    means the current directory, which of course exists), then do nothing.
    Raise DistutilsFileError ikiwa unable to create some directory along the way
    (eg. some sub-path exists, but ni a file rather than a directory).
    If 'verbose' ni true, andika a one-line summary of each mkdir to stdout.
    Return the list of directories actually created.
    """

    global _path_created

    # Detect a common bug -- name ni Tupu
    ikiwa sio isinstance(name, str):
        ashiria DistutilsInternalError(
              "mkpath: 'name' must be a string (got %r)" % (name,))

    # XXX what's the better way to handle verbosity? andika kama we create
    # each directory kwenye the path (the current behaviour), ama only announce
    # the creation of the whole path? (quite easy to do the latter since
    # we're sio using a recursive algorithm)

    name = os.path.normpath(name)
    created_dirs = []
    ikiwa os.path.isdir(name) ama name == '':
        rudisha created_dirs
    ikiwa _path_created.get(os.path.abspath(name)):
        rudisha created_dirs

    (head, tail) = os.path.split(name)
    tails = [tail]                      # stack of lone dirs to create

    wakati head na tail na sio os.path.isdir(head):
        (head, tail) = os.path.split(head)
        tails.insert(0, tail)          # push next higher dir onto stack

    # now 'head' contains the deepest directory that already exists
    # (that is, the child of 'head' kwenye 'name' ni the highest directory
    # that does *not* exist)
    kila d kwenye tails:
        #print "head = %s, d = %s: " % (head, d),
        head = os.path.join(head, d)
        abs_head = os.path.abspath(head)

        ikiwa _path_created.get(abs_head):
            endelea

        ikiwa verbose >= 1:
            log.info("creating %s", head)

        ikiwa sio dry_run:
            jaribu:
                os.mkdir(head, mode)
            tatizo OSError kama exc:
                ikiwa sio (exc.errno == errno.EEXIST na os.path.isdir(head)):
                    ashiria DistutilsFileError(
                          "could sio create '%s': %s" % (head, exc.args[-1]))
            created_dirs.append(head)

        _path_created[abs_head] = 1
    rudisha created_dirs

eleza create_tree(base_dir, files, mode=0o777, verbose=1, dry_run=0):
    """Create all the empty directories under 'base_dir' needed to put 'files'
    there.

    'base_dir' ni just the name of a directory which doesn't necessarily
    exist yet; 'files' ni a list of filenames to be interpreted relative to
    'base_dir'.  'base_dir' + the directory portion of every file kwenye 'files'
    will be created ikiwa it doesn't already exist.  'mode', 'verbose' na
    'dry_run' flags are kama kila 'mkpath()'.
    """
    # First get the list of directories to create
    need_dir = set()
    kila file kwenye files:
        need_dir.add(os.path.join(base_dir, os.path.dirname(file)))

    # Now create them
    kila dir kwenye sorted(need_dir):
        mkpath(dir, mode, verbose=verbose, dry_run=dry_run)

eleza copy_tree(src, dst, preserve_mode=1, preserve_times=1,
              preserve_symlinks=0, update=0, verbose=1, dry_run=0):
    """Copy an entire directory tree 'src' to a new location 'dst'.

    Both 'src' na 'dst' must be directory names.  If 'src' ni sio a
    directory, ashiria DistutilsFileError.  If 'dst' does sio exist, it is
    created ukijumuisha 'mkpath()'.  The end result of the copy ni that every
    file kwenye 'src' ni copied to 'dst', na directories under 'src' are
    recursively copied to 'dst'.  Return the list of files that were
    copied ama might have been copied, using their output name.  The
    rudisha value ni unaffected by 'update' ama 'dry_run': it ni simply
    the list of all files under 'src', ukijumuisha the names changed to be
    under 'dst'.

    'preserve_mode' na 'preserve_times' are the same kama for
    'copy_file'; note that they only apply to regular files, sio to
    directories.  If 'preserve_symlinks' ni true, symlinks will be
    copied kama symlinks (on platforms that support them!); otherwise
    (the default), the destination of the symlink will be copied.
    'update' na 'verbose' are the same kama kila 'copy_file'.
    """
    kutoka distutils.file_util agiza copy_file

    ikiwa sio dry_run na sio os.path.isdir(src):
        ashiria DistutilsFileError(
              "cannot copy tree '%s': sio a directory" % src)
    jaribu:
        names = os.listdir(src)
    tatizo OSError kama e:
        ikiwa dry_run:
            names = []
        isipokua:
            ashiria DistutilsFileError(
                  "error listing files kwenye '%s': %s" % (src, e.strerror))

    ikiwa sio dry_run:
        mkpath(dst, verbose=verbose)

    outputs = []

    kila n kwenye names:
        src_name = os.path.join(src, n)
        dst_name = os.path.join(dst, n)

        ikiwa n.startswith('.nfs'):
            # skip NFS rename files
            endelea

        ikiwa preserve_symlinks na os.path.islink(src_name):
            link_dest = os.readlink(src_name)
            ikiwa verbose >= 1:
                log.info("linking %s -> %s", dst_name, link_dest)
            ikiwa sio dry_run:
                os.symlink(link_dest, dst_name)
            outputs.append(dst_name)

        lasivyo os.path.isdir(src_name):
            outputs.extend(
                copy_tree(src_name, dst_name, preserve_mode,
                          preserve_times, preserve_symlinks, update,
                          verbose=verbose, dry_run=dry_run))
        isipokua:
            copy_file(src_name, dst_name, preserve_mode,
                      preserve_times, update, verbose=verbose,
                      dry_run=dry_run)
            outputs.append(dst_name)

    rudisha outputs

eleza _build_cmdtuple(path, cmdtuples):
    """Helper kila remove_tree()."""
    kila f kwenye os.listdir(path):
        real_f = os.path.join(path,f)
        ikiwa os.path.isdir(real_f) na sio os.path.islink(real_f):
            _build_cmdtuple(real_f, cmdtuples)
        isipokua:
            cmdtuples.append((os.remove, real_f))
    cmdtuples.append((os.rmdir, path))

eleza remove_tree(directory, verbose=1, dry_run=0):
    """Recursively remove an entire directory tree.

    Any errors are ignored (apart kutoka being reported to stdout ikiwa 'verbose'
    ni true).
    """
    global _path_created

    ikiwa verbose >= 1:
        log.info("removing '%s' (and everything under it)", directory)
    ikiwa dry_run:
        rudisha
    cmdtuples = []
    _build_cmdtuple(directory, cmdtuples)
    kila cmd kwenye cmdtuples:
        jaribu:
            cmd[0](cmd[1])
            # remove dir kutoka cache ikiwa it's already there
            abspath = os.path.abspath(cmd[1])
            ikiwa abspath kwenye _path_created:
                toa _path_created[abspath]
        tatizo OSError kama exc:
            log.warn("error removing %s: %s", directory, exc)

eleza ensure_relative(path):
    """Take the full path 'path', na make it a relative path.

    This ni useful to make 'path' the second argument to os.path.join().
    """
    drive, path = os.path.splitdrive(path)
    ikiwa path[0:1] == os.sep:
        path = drive + path[1:]
    rudisha path
