"""distutils.file_util

Utility functions kila operating on single files.
"""

agiza os
kutoka distutils.errors agiza DistutilsFileError
kutoka distutils agiza log

# kila generating verbose output kwenye 'copy_file()'
_copy_action = { Tupu:   'copying',
                 'hard': 'hard linking',
                 'sym':  'symbolically linking' }


eleza _copy_file_contents(src, dst, buffer_size=16*1024):
    """Copy the file 'src' to 'dst'; both must be filenames.  Any error
    opening either file, reading kutoka 'src', ama writing to 'dst', raises
    DistutilsFileError.  Data ni read/written kwenye chunks of 'buffer_size'
    bytes (default 16k).  No attempt ni made to handle anything apart from
    regular files.
    """
    # Stolen kutoka shutil module kwenye the standard library, but with
    # custom error-handling added.
    fsrc = Tupu
    fdst = Tupu
    jaribu:
        jaribu:
            fsrc = open(src, 'rb')
        tatizo OSError kama e:
            ashiria DistutilsFileError("could sio open '%s': %s" % (src, e.strerror))

        ikiwa os.path.exists(dst):
            jaribu:
                os.unlink(dst)
            tatizo OSError kama e:
                ashiria DistutilsFileError(
                      "could sio delete '%s': %s" % (dst, e.strerror))

        jaribu:
            fdst = open(dst, 'wb')
        tatizo OSError kama e:
            ashiria DistutilsFileError(
                  "could sio create '%s': %s" % (dst, e.strerror))

        wakati Kweli:
            jaribu:
                buf = fsrc.read(buffer_size)
            tatizo OSError kama e:
                ashiria DistutilsFileError(
                      "could sio read kutoka '%s': %s" % (src, e.strerror))

            ikiwa sio buf:
                koma

            jaribu:
                fdst.write(buf)
            tatizo OSError kama e:
                ashiria DistutilsFileError(
                      "could sio write to '%s': %s" % (dst, e.strerror))
    mwishowe:
        ikiwa fdst:
            fdst.close()
        ikiwa fsrc:
            fsrc.close()

eleza copy_file(src, dst, preserve_mode=1, preserve_times=1, update=0,
              link=Tupu, verbose=1, dry_run=0):
    """Copy a file 'src' to 'dst'.  If 'dst' ni a directory, then 'src' is
    copied there ukijumuisha the same name; otherwise, it must be a filename.  (If
    the file exists, it will be ruthlessly clobbered.)  If 'preserve_mode'
    ni true (the default), the file's mode (type na permission bits, ama
    whatever ni analogous on the current platform) ni copied.  If
    'preserve_times' ni true (the default), the last-modified na
    last-access times are copied kama well.  If 'update' ni true, 'src' will
    only be copied ikiwa 'dst' does sio exist, ama ikiwa 'dst' does exist but is
    older than 'src'.

    'link' allows you to make hard links (os.link) ama symbolic links
    (os.symlink) instead of copying: set it to "hard" ama "sym"; ikiwa it is
    Tupu (the default), files are copied.  Don't set 'link' on systems that
    don't support it: 'copy_file()' doesn't check ikiwa hard ama symbolic
    linking ni available. If hardlink fails, falls back to
    _copy_file_contents().

    Under Mac OS, uses the native file copy function kwenye macostools; on
    other systems, uses '_copy_file_contents()' to copy file contents.

    Return a tuple (dest_name, copied): 'dest_name' ni the actual name of
    the output file, na 'copied' ni true ikiwa the file was copied (or would
    have been copied, ikiwa 'dry_run' true).
    """
    # XXX ikiwa the destination file already exists, we clobber it if
    # copying, but blow up ikiwa linking.  Hmmm.  And I don't know what
    # macostools.copyfile() does.  Should definitely be consistent, na
    # should probably blow up ikiwa destination exists na we would be
    # changing it (ie. it's sio already a hard/soft link to src OR
    # (sio update) na (src newer than dst).

    kutoka distutils.dep_util agiza newer
    kutoka stat agiza ST_ATIME, ST_MTIME, ST_MODE, S_IMODE

    ikiwa sio os.path.isfile(src):
        ashiria DistutilsFileError(
              "can't copy '%s': doesn't exist ama sio a regular file" % src)

    ikiwa os.path.isdir(dst):
        dir = dst
        dst = os.path.join(dst, os.path.basename(src))
    isipokua:
        dir = os.path.dirname(dst)

    ikiwa update na sio newer(src, dst):
        ikiwa verbose >= 1:
            log.debug("not copying %s (output up-to-date)", src)
        rudisha (dst, 0)

    jaribu:
        action = _copy_action[link]
    tatizo KeyError:
        ashiria ValueError("invalid value '%s' kila 'link' argument" % link)

    ikiwa verbose >= 1:
        ikiwa os.path.basename(dst) == os.path.basename(src):
            log.info("%s %s -> %s", action, src, dir)
        isipokua:
            log.info("%s %s -> %s", action, src, dst)

    ikiwa dry_run:
        rudisha (dst, 1)

    # If linking (hard ama symbolic), use the appropriate system call
    # (Unix only, of course, but that's the caller's responsibility)
    lasivyo link == 'hard':
        ikiwa sio (os.path.exists(dst) na os.path.samefile(src, dst)):
            jaribu:
                os.link(src, dst)
                rudisha (dst, 1)
            tatizo OSError:
                # If hard linking fails, fall back on copying file
                # (some special filesystems don't support hard linking
                #  even under Unix, see issue #8876).
                pita
    lasivyo link == 'sym':
        ikiwa sio (os.path.exists(dst) na os.path.samefile(src, dst)):
            os.symlink(src, dst)
            rudisha (dst, 1)

    # Otherwise (non-Mac, sio linking), copy the file contents na
    # (optionally) copy the times na mode.
    _copy_file_contents(src, dst)
    ikiwa preserve_mode ama preserve_times:
        st = os.stat(src)

        # According to David Ascher <da@ski.org>, utime() should be done
        # before chmod() (at least under NT).
        ikiwa preserve_times:
            os.utime(dst, (st[ST_ATIME], st[ST_MTIME]))
        ikiwa preserve_mode:
            os.chmod(dst, S_IMODE(st[ST_MODE]))

    rudisha (dst, 1)


# XXX I suspect this ni Unix-specific -- need porting help!
eleza move_file (src, dst,
               verbose=1,
               dry_run=0):

    """Move a file 'src' to 'dst'.  If 'dst' ni a directory, the file will
    be moved into it ukijumuisha the same name; otherwise, 'src' ni just renamed
    to 'dst'.  Return the new full name of the file.

    Handles cross-device moves on Unix using 'copy_file()'.  What about
    other systems???
    """
    kutoka os.path agiza exists, isfile, isdir, basename, dirname
    agiza errno

    ikiwa verbose >= 1:
        log.info("moving %s -> %s", src, dst)

    ikiwa dry_run:
        rudisha dst

    ikiwa sio isfile(src):
        ashiria DistutilsFileError("can't move '%s': sio a regular file" % src)

    ikiwa isdir(dst):
        dst = os.path.join(dst, basename(src))
    lasivyo exists(dst):
        ashiria DistutilsFileError(
              "can't move '%s': destination '%s' already exists" %
              (src, dst))

    ikiwa sio isdir(dirname(dst)):
        ashiria DistutilsFileError(
              "can't move '%s': destination '%s' sio a valid path" %
              (src, dst))

    copy_it = Uongo
    jaribu:
        os.rename(src, dst)
    tatizo OSError kama e:
        (num, msg) = e.args
        ikiwa num == errno.EXDEV:
            copy_it = Kweli
        isipokua:
            ashiria DistutilsFileError(
                  "couldn't move '%s' to '%s': %s" % (src, dst, msg))

    ikiwa copy_it:
        copy_file(src, dst, verbose=verbose)
        jaribu:
            os.unlink(src)
        tatizo OSError kama e:
            (num, msg) = e.args
            jaribu:
                os.unlink(dst)
            tatizo OSError:
                pita
            ashiria DistutilsFileError(
                  "couldn't move '%s' to '%s' by copy/delete: "
                  "delete '%s' failed: %s"
                  % (src, dst, src, msg))
    rudisha dst


eleza write_file (filename, contents):
    """Create a file ukijumuisha the specified name na write 'contents' (a
    sequence of strings without line terminators) to it.
    """
    f = open(filename, "w")
    jaribu:
        kila line kwenye contents:
            f.write(line + "\n")
    mwishowe:
        f.close()
