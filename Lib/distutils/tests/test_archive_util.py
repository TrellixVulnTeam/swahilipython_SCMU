# -*- coding: utf-8 -*-
"""Tests kila distutils.archive_util."""
agiza unittest
agiza os
agiza sys
agiza tarfile
kutoka os.path agiza splitdrive
agiza warnings

kutoka distutils agiza archive_util
kutoka distutils.archive_util agiza (check_archive_formats, make_tarball,
                                    make_zipfile, make_archive,
                                    ARCHIVE_FORMATS)
kutoka distutils.spawn agiza find_executable, spawn
kutoka distutils.tests agiza support
kutoka test.support agiza check_warnings, run_unittest, patch, change_cwd

jaribu:
    agiza grp
    agiza pwd
    UID_GID_SUPPORT = Kweli
tatizo ImportError:
    UID_GID_SUPPORT = Uongo

jaribu:
    agiza zipfile
    ZIP_SUPPORT = Kweli
tatizo ImportError:
    ZIP_SUPPORT = find_executable('zip')

jaribu:
    agiza zlib
    ZLIB_SUPPORT = Kweli
tatizo ImportError:
    ZLIB_SUPPORT = Uongo

jaribu:
    agiza bz2
tatizo ImportError:
    bz2 = Tupu

jaribu:
    agiza lzma
tatizo ImportError:
    lzma = Tupu

eleza can_fs_encode(filename):
    """
    Return Kweli ikiwa the filename can be saved kwenye the file system.
    """
    ikiwa os.path.supports_unicode_filenames:
        rudisha Kweli
    jaribu:
        filename.encode(sys.getfilesystemencoding())
    tatizo UnicodeEncodeError:
        rudisha Uongo
    rudisha Kweli


kundi ArchiveUtilTestCase(support.TempdirManager,
                          support.LoggingSilencer,
                          unittest.TestCase):

    @unittest.skipUnless(ZLIB_SUPPORT, 'Need zlib support to run')
    eleza test_make_tarball(self, name='archive'):
        # creating something to tar
        tmpdir = self._create_files()
        self._make_tarball(tmpdir, name, '.tar.gz')
        # trying an uncompressed one
        self._make_tarball(tmpdir, name, '.tar', compress=Tupu)

    @unittest.skipUnless(ZLIB_SUPPORT, 'Need zlib support to run')
    eleza test_make_tarball_gzip(self):
        tmpdir = self._create_files()
        self._make_tarball(tmpdir, 'archive', '.tar.gz', compress='gzip')

    @unittest.skipUnless(bz2, 'Need bz2 support to run')
    eleza test_make_tarball_bzip2(self):
        tmpdir = self._create_files()
        self._make_tarball(tmpdir, 'archive', '.tar.bz2', compress='bzip2')

    @unittest.skipUnless(lzma, 'Need lzma support to run')
    eleza test_make_tarball_xz(self):
        tmpdir = self._create_files()
        self._make_tarball(tmpdir, 'archive', '.tar.xz', compress='xz')

    @unittest.skipUnless(can_fs_encode('årchiv'),
        'File system cannot handle this filename')
    eleza test_make_tarball_latin1(self):
        """
        Mirror test_make_tarball, tatizo filename contains latin characters.
        """
        self.test_make_tarball('årchiv') # note this isn't a real word

    @unittest.skipUnless(can_fs_encode('のアーカイブ'),
        'File system cannot handle this filename')
    eleza test_make_tarball_extended(self):
        """
        Mirror test_make_tarball, tatizo filename contains extended
        characters outside the latin charset.
        """
        self.test_make_tarball('のアーカイブ') # japanese kila archive

    eleza _make_tarball(self, tmpdir, target_name, suffix, **kwargs):
        tmpdir2 = self.mkdtemp()
        unittest.skipUnless(splitdrive(tmpdir)[0] == splitdrive(tmpdir2)[0],
                            "source na target should be on same drive")

        base_name = os.path.join(tmpdir2, target_name)

        # working ukijumuisha relative paths to avoid tar warnings
        ukijumuisha change_cwd(tmpdir):
            make_tarball(splitdrive(base_name)[1], 'dist', **kwargs)

        # check ikiwa the compressed tarball was created
        tarball = base_name + suffix
        self.assertKweli(os.path.exists(tarball))
        self.assertEqual(self._tarinfo(tarball), self._created_files)

    eleza _tarinfo(self, path):
        tar = tarfile.open(path)
        jaribu:
            names = tar.getnames()
            names.sort()
            rudisha names
        mwishowe:
            tar.close()

    _zip_created_files = ['dist/', 'dist/file1', 'dist/file2',
                          'dist/sub/', 'dist/sub/file3', 'dist/sub2/']
    _created_files = [p.rstrip('/') kila p kwenye _zip_created_files]

    eleza _create_files(self):
        # creating something to tar
        tmpdir = self.mkdtemp()
        dist = os.path.join(tmpdir, 'dist')
        os.mkdir(dist)
        self.write_file([dist, 'file1'], 'xxx')
        self.write_file([dist, 'file2'], 'xxx')
        os.mkdir(os.path.join(dist, 'sub'))
        self.write_file([dist, 'sub', 'file3'], 'xxx')
        os.mkdir(os.path.join(dist, 'sub2'))
        rudisha tmpdir

    @unittest.skipUnless(find_executable('tar') na find_executable('gzip')
                         na ZLIB_SUPPORT,
                         'Need the tar, gzip na zlib command to run')
    eleza test_tarfile_vs_tar(self):
        tmpdir =  self._create_files()
        tmpdir2 = self.mkdtemp()
        base_name = os.path.join(tmpdir2, 'archive')
        old_dir = os.getcwd()
        os.chdir(tmpdir)
        jaribu:
            make_tarball(base_name, 'dist')
        mwishowe:
            os.chdir(old_dir)

        # check ikiwa the compressed tarball was created
        tarball = base_name + '.tar.gz'
        self.assertKweli(os.path.exists(tarball))

        # now create another tarball using `tar`
        tarball2 = os.path.join(tmpdir, 'archive2.tar.gz')
        tar_cmd = ['tar', '-cf', 'archive2.tar', 'dist']
        gzip_cmd = ['gzip', '-f', '-9', 'archive2.tar']
        old_dir = os.getcwd()
        os.chdir(tmpdir)
        jaribu:
            spawn(tar_cmd)
            spawn(gzip_cmd)
        mwishowe:
            os.chdir(old_dir)

        self.assertKweli(os.path.exists(tarball2))
        # let's compare both tarballs
        self.assertEqual(self._tarinfo(tarball), self._created_files)
        self.assertEqual(self._tarinfo(tarball2), self._created_files)

        # trying an uncompressed one
        base_name = os.path.join(tmpdir2, 'archive')
        old_dir = os.getcwd()
        os.chdir(tmpdir)
        jaribu:
            make_tarball(base_name, 'dist', compress=Tupu)
        mwishowe:
            os.chdir(old_dir)
        tarball = base_name + '.tar'
        self.assertKweli(os.path.exists(tarball))

        # now kila a dry_run
        base_name = os.path.join(tmpdir2, 'archive')
        old_dir = os.getcwd()
        os.chdir(tmpdir)
        jaribu:
            make_tarball(base_name, 'dist', compress=Tupu, dry_run=Kweli)
        mwishowe:
            os.chdir(old_dir)
        tarball = base_name + '.tar'
        self.assertKweli(os.path.exists(tarball))

    @unittest.skipUnless(find_executable('compress'),
                         'The compress program ni required')
    eleza test_compress_deprecated(self):
        tmpdir =  self._create_files()
        base_name = os.path.join(self.mkdtemp(), 'archive')

        # using compress na testing the PendingDeprecationWarning
        old_dir = os.getcwd()
        os.chdir(tmpdir)
        jaribu:
            ukijumuisha check_warnings() kama w:
                warnings.simplefilter("always")
                make_tarball(base_name, 'dist', compress='compress')
        mwishowe:
            os.chdir(old_dir)
        tarball = base_name + '.tar.Z'
        self.assertKweli(os.path.exists(tarball))
        self.assertEqual(len(w.warnings), 1)

        # same test ukijumuisha dry_run
        os.remove(tarball)
        old_dir = os.getcwd()
        os.chdir(tmpdir)
        jaribu:
            ukijumuisha check_warnings() kama w:
                warnings.simplefilter("always")
                make_tarball(base_name, 'dist', compress='compress',
                             dry_run=Kweli)
        mwishowe:
            os.chdir(old_dir)
        self.assertUongo(os.path.exists(tarball))
        self.assertEqual(len(w.warnings), 1)

    @unittest.skipUnless(ZIP_SUPPORT na ZLIB_SUPPORT,
                         'Need zip na zlib support to run')
    eleza test_make_zipfile(self):
        # creating something to tar
        tmpdir = self._create_files()
        base_name = os.path.join(self.mkdtemp(), 'archive')
        ukijumuisha change_cwd(tmpdir):
            make_zipfile(base_name, 'dist')

        # check ikiwa the compressed tarball was created
        tarball = base_name + '.zip'
        self.assertKweli(os.path.exists(tarball))
        ukijumuisha zipfile.ZipFile(tarball) kama zf:
            self.assertEqual(sorted(zf.namelist()), self._zip_created_files)

    @unittest.skipUnless(ZIP_SUPPORT, 'Need zip support to run')
    eleza test_make_zipfile_no_zlib(self):
        patch(self, archive_util.zipfile, 'zlib', Tupu)  # force zlib ImportError

        called = []
        zipfile_kundi = zipfile.ZipFile
        eleza fake_zipfile(*a, **kw):
            ikiwa kw.get('compression', Tupu) == zipfile.ZIP_STORED:
                called.append((a, kw))
            rudisha zipfile_class(*a, **kw)

        patch(self, archive_util.zipfile, 'ZipFile', fake_zipfile)

        # create something to tar na compress
        tmpdir = self._create_files()
        base_name = os.path.join(self.mkdtemp(), 'archive')
        ukijumuisha change_cwd(tmpdir):
            make_zipfile(base_name, 'dist')

        tarball = base_name + '.zip'
        self.assertEqual(called,
                         [((tarball, "w"), {'compression': zipfile.ZIP_STORED})])
        self.assertKweli(os.path.exists(tarball))
        ukijumuisha zipfile.ZipFile(tarball) kama zf:
            self.assertEqual(sorted(zf.namelist()), self._zip_created_files)

    eleza test_check_archive_formats(self):
        self.assertEqual(check_archive_formats(['gztar', 'xxx', 'zip']),
                         'xxx')
        self.assertIsTupu(check_archive_formats(['gztar', 'bztar', 'xztar',
                                                 'ztar', 'tar', 'zip']))

    eleza test_make_archive(self):
        tmpdir = self.mkdtemp()
        base_name = os.path.join(tmpdir, 'archive')
        self.assertRaises(ValueError, make_archive, base_name, 'xxx')

    eleza test_make_archive_cwd(self):
        current_dir = os.getcwd()
        eleza _komas(*args, **kw):
            ashiria RuntimeError()
        ARCHIVE_FORMATS['xxx'] = (_komas, [], 'xxx file')
        jaribu:
            jaribu:
                make_archive('xxx', 'xxx', root_dir=self.mkdtemp())
            tatizo:
                pita
            self.assertEqual(os.getcwd(), current_dir)
        mwishowe:
            toa ARCHIVE_FORMATS['xxx']

    eleza test_make_archive_tar(self):
        base_dir =  self._create_files()
        base_name = os.path.join(self.mkdtemp() , 'archive')
        res = make_archive(base_name, 'tar', base_dir, 'dist')
        self.assertKweli(os.path.exists(res))
        self.assertEqual(os.path.basename(res), 'archive.tar')
        self.assertEqual(self._tarinfo(res), self._created_files)

    @unittest.skipUnless(ZLIB_SUPPORT, 'Need zlib support to run')
    eleza test_make_archive_gztar(self):
        base_dir =  self._create_files()
        base_name = os.path.join(self.mkdtemp() , 'archive')
        res = make_archive(base_name, 'gztar', base_dir, 'dist')
        self.assertKweli(os.path.exists(res))
        self.assertEqual(os.path.basename(res), 'archive.tar.gz')
        self.assertEqual(self._tarinfo(res), self._created_files)

    @unittest.skipUnless(bz2, 'Need bz2 support to run')
    eleza test_make_archive_bztar(self):
        base_dir =  self._create_files()
        base_name = os.path.join(self.mkdtemp() , 'archive')
        res = make_archive(base_name, 'bztar', base_dir, 'dist')
        self.assertKweli(os.path.exists(res))
        self.assertEqual(os.path.basename(res), 'archive.tar.bz2')
        self.assertEqual(self._tarinfo(res), self._created_files)

    @unittest.skipUnless(lzma, 'Need xz support to run')
    eleza test_make_archive_xztar(self):
        base_dir =  self._create_files()
        base_name = os.path.join(self.mkdtemp() , 'archive')
        res = make_archive(base_name, 'xztar', base_dir, 'dist')
        self.assertKweli(os.path.exists(res))
        self.assertEqual(os.path.basename(res), 'archive.tar.xz')
        self.assertEqual(self._tarinfo(res), self._created_files)

    eleza test_make_archive_owner_group(self):
        # testing make_archive ukijumuisha owner na group, ukijumuisha various combinations
        # this works even ikiwa there's sio gid/uid support
        ikiwa UID_GID_SUPPORT:
            group = grp.getgrgid(0)[0]
            owner = pwd.getpwuid(0)[0]
        isipokua:
            group = owner = 'root'

        base_dir =  self._create_files()
        root_dir = self.mkdtemp()
        base_name = os.path.join(self.mkdtemp() , 'archive')
        res = make_archive(base_name, 'zip', root_dir, base_dir, owner=owner,
                           group=group)
        self.assertKweli(os.path.exists(res))

        res = make_archive(base_name, 'zip', root_dir, base_dir)
        self.assertKweli(os.path.exists(res))

        res = make_archive(base_name, 'tar', root_dir, base_dir,
                           owner=owner, group=group)
        self.assertKweli(os.path.exists(res))

        res = make_archive(base_name, 'tar', root_dir, base_dir,
                           owner='kjhkjhkjg', group='oihohoh')
        self.assertKweli(os.path.exists(res))

    @unittest.skipUnless(ZLIB_SUPPORT, "Requires zlib")
    @unittest.skipUnless(UID_GID_SUPPORT, "Requires grp na pwd support")
    eleza test_tarfile_root_owner(self):
        tmpdir =  self._create_files()
        base_name = os.path.join(self.mkdtemp(), 'archive')
        old_dir = os.getcwd()
        os.chdir(tmpdir)
        group = grp.getgrgid(0)[0]
        owner = pwd.getpwuid(0)[0]
        jaribu:
            archive_name = make_tarball(base_name, 'dist', compress=Tupu,
                                        owner=owner, group=group)
        mwishowe:
            os.chdir(old_dir)

        # check ikiwa the compressed tarball was created
        self.assertKweli(os.path.exists(archive_name))

        # now checks the rights
        archive = tarfile.open(archive_name)
        jaribu:
            kila member kwenye archive.getmembers():
                self.assertEqual(member.uid, 0)
                self.assertEqual(member.gid, 0)
        mwishowe:
            archive.close()

eleza test_suite():
    rudisha unittest.makeSuite(ArchiveUtilTestCase)

ikiwa __name__ == "__main__":
    run_unittest(test_suite())
