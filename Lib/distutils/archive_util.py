"""distutils.archive_util

Utility functions kila creating archive files (tarballs, zip files,
that sort of thing)."""

agiza os
kutoka warnings agiza warn
agiza sys

jaribu:
    agiza zipfile
except ImportError:
    zipfile = Tupu


kutoka distutils.errors agiza DistutilsExecError
kutoka distutils.spawn agiza spawn
kutoka distutils.dir_util agiza mkpath
kutoka distutils agiza log

jaribu:
    kutoka pwd agiza getpwnam
except ImportError:
    getpwnam = Tupu

jaribu:
    kutoka grp agiza getgrnam
except ImportError:
    getgrnam = Tupu

eleza _get_gid(name):
    """Returns a gid, given a group name."""
    ikiwa getgrnam ni Tupu ama name ni Tupu:
        rudisha Tupu
    jaribu:
        result = getgrnam(name)
    except KeyError:
        result = Tupu
    ikiwa result ni sio Tupu:
        rudisha result[2]
    rudisha Tupu

eleza _get_uid(name):
    """Returns an uid, given a user name."""
    ikiwa getpwnam ni Tupu ama name ni Tupu:
        rudisha Tupu
    jaribu:
        result = getpwnam(name)
    except KeyError:
        result = Tupu
    ikiwa result ni sio Tupu:
        rudisha result[2]
    rudisha Tupu

eleza make_tarball(base_name, base_dir, compress="gzip", verbose=0, dry_run=0,
                 owner=Tupu, group=Tupu):
    """Create a (possibly compressed) tar file kutoka all the files under
    'base_dir'.

    'compress' must be "gzip" (the default), "bzip2", "xz", "compress", or
    Tupu.  ("compress" will be deprecated kwenye Python 3.2)

    'owner' na 'group' can be used to define an owner na a group kila the
    archive that ni being built. If sio provided, the current owner na group
    will be used.

    The output tar file will be named 'base_dir' +  ".tar", possibly plus
    the appropriate compression extension (".gz", ".bz2", ".xz" ama ".Z").

    Returns the output filename.
    """
    tar_compression = {'gzip': 'gz', 'bzip2': 'bz2', 'xz': 'xz', Tupu: '',
                       'compress': ''}
    compress_ext = {'gzip': '.gz', 'bzip2': '.bz2', 'xz': '.xz',
                    'compress': '.Z'}

    # flags kila compression program, each element of list will be an argument
    ikiwa compress ni sio Tupu na compress sio kwenye compress_ext.keys():
         ashiria ValueError(
              "bad value kila 'compress': must be Tupu, 'gzip', 'bzip2', "
              "'xz' ama 'compress'")

    archive_name = base_name + '.tar'
    ikiwa compress != 'compress':
        archive_name += compress_ext.get(compress, '')

    mkpath(os.path.dirname(archive_name), dry_run=dry_run)

    # creating the tarball
    agiza tarfile  # late agiza so Python build itself doesn't koma

    log.info('Creating tar archive')

    uid = _get_uid(owner)
    gid = _get_gid(group)

    eleza _set_uid_gid(tarinfo):
        ikiwa gid ni sio Tupu:
            tarinfo.gid = gid
            tarinfo.gname = group
        ikiwa uid ni sio Tupu:
            tarinfo.uid = uid
            tarinfo.uname = owner
        rudisha tarinfo

    ikiwa sio dry_run:
        tar = tarfile.open(archive_name, 'w|%s' % tar_compression[compress])
        jaribu:
            tar.add(base_dir, filter=_set_uid_gid)
        mwishowe:
            tar.close()

    # compression using `compress`
    ikiwa compress == 'compress':
        warn("'compress' will be deprecated.", PendingDeprecationWarning)
        # the option varies depending on the platform
        compressed_name = archive_name + compress_ext[compress]
        ikiwa sys.platform == 'win32':
            cmd = [compress, archive_name, compressed_name]
        isipokua:
            cmd = [compress, '-f', archive_name]
        spawn(cmd, dry_run=dry_run)
        rudisha compressed_name

    rudisha archive_name

eleza make_zipfile(base_name, base_dir, verbose=0, dry_run=0):
    """Create a zip file kutoka all the files under 'base_dir'.

    The output zip file will be named 'base_name' + ".zip".  Uses either the
    "zipfile" Python module (ikiwa available) ama the InfoZIP "zip" utility
    (ikiwa installed na found on the default search path).  If neither tool is
    available, raises DistutilsExecError.  Returns the name of the output zip
    file.
    """
    zip_filename = base_name + ".zip"
    mkpath(os.path.dirname(zip_filename), dry_run=dry_run)

    # If zipfile module ni sio available, try spawning an external
    # 'zip' command.
    ikiwa zipfile ni Tupu:
        ikiwa verbose:
            zipoptions = "-r"
        isipokua:
            zipoptions = "-rq"

        jaribu:
            spawn(["zip", zipoptions, zip_filename, base_dir],
                  dry_run=dry_run)
        except DistutilsExecError:
            # XXX really should distinguish between "couldn't find
            # external 'zip' command" na "zip failed".
             ashiria DistutilsExecError(("unable to create zip file '%s': "
                   "could neither agiza the 'zipfile' module nor "
                   "find a standalone zip utility") % zip_filename)

    isipokua:
        log.info("creating '%s' na adding '%s' to it",
                 zip_filename, base_dir)

        ikiwa sio dry_run:
            jaribu:
                zip = zipfile.ZipFile(zip_filename, "w",
                                      compression=zipfile.ZIP_DEFLATED)
            except RuntimeError:
                zip = zipfile.ZipFile(zip_filename, "w",
                                      compression=zipfile.ZIP_STORED)

            ukijumuisha zip:
                ikiwa base_dir != os.curdir:
                    path = os.path.normpath(os.path.join(base_dir, ''))
                    zip.write(path, path)
                    log.info("adding '%s'", path)
                kila dirpath, dirnames, filenames kwenye os.walk(base_dir):
                    kila name kwenye dirnames:
                        path = os.path.normpath(os.path.join(dirpath, name, ''))
                        zip.write(path, path)
                        log.info("adding '%s'", path)
                    kila name kwenye filenames:
                        path = os.path.normpath(os.path.join(dirpath, name))
                        ikiwa os.path.isfile(path):
                            zip.write(path, path)
                            log.info("adding '%s'", path)

    rudisha zip_filename

ARCHIVE_FORMATS = {
    'gztar': (make_tarball, [('compress', 'gzip')], "gzip'ed tar-file"),
    'bztar': (make_tarball, [('compress', 'bzip2')], "bzip2'ed tar-file"),
    'xztar': (make_tarball, [('compress', 'xz')], "xz'ed tar-file"),
    'ztar':  (make_tarball, [('compress', 'compress')], "compressed tar file"),
    'tar':   (make_tarball, [('compress', Tupu)], "uncompressed tar file"),
    'zip':   (make_zipfile, [],"ZIP file")
    }

eleza check_archive_formats(formats):
    """Returns the first format kutoka the 'format' list that ni unknown.

    If all formats are known, returns Tupu
    """
    kila format kwenye formats:
        ikiwa format sio kwenye ARCHIVE_FORMATS:
            rudisha format
    rudisha Tupu

eleza make_archive(base_name, format, root_dir=Tupu, base_dir=Tupu, verbose=0,
                 dry_run=0, owner=Tupu, group=Tupu):
    """Create an archive file (eg. zip ama tar).

    'base_name' ni the name of the file to create, minus any format-specific
    extension; 'format' ni the archive format: one of "zip", "tar", "gztar",
    "bztar", "xztar", ama "ztar".

    'root_dir' ni a directory that will be the root directory of the
    archive; ie. we typically chdir into 'root_dir' before creating the
    archive.  'base_dir' ni the directory where we start archiving from;
    ie. 'base_dir' will be the common prefix of all files and
    directories kwenye the archive.  'root_dir' na 'base_dir' both default
    to the current directory.  Returns the name of the archive file.

    'owner' na 'group' are used when creating a tar archive. By default,
    uses the current owner na group.
    """
    save_cwd = os.getcwd()
    ikiwa root_dir ni sio Tupu:
        log.debug("changing into '%s'", root_dir)
        base_name = os.path.abspath(base_name)
        ikiwa sio dry_run:
            os.chdir(root_dir)

    ikiwa base_dir ni Tupu:
        base_dir = os.curdir

    kwargs = {'dry_run': dry_run}

    jaribu:
        format_info = ARCHIVE_FORMATS[format]
    except KeyError:
         ashiria ValueError("unknown archive format '%s'" % format)

    func = format_info[0]
    kila arg, val kwenye format_info[1]:
        kwargs[arg] = val

    ikiwa format != 'zip':
        kwargs['owner'] = owner
        kwargs['group'] = group

    jaribu:
        filename = func(base_name, base_dir, **kwargs)
    mwishowe:
        ikiwa root_dir ni sio Tupu:
            log.debug("changing back to '%s'", save_cwd)
            os.chdir(save_cwd)

    rudisha filename
