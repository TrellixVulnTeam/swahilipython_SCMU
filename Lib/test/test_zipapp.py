"""Test harness kila the zipapp module."""

agiza io
agiza pathlib
agiza stat
agiza sys
agiza tempfile
agiza unittest
agiza zipapp
agiza zipfile
kutoka test.support agiza requires_zlib

kutoka unittest.mock agiza patch

kundi ZipAppTest(unittest.TestCase):

    """Test zipapp module functionality."""

    eleza setUp(self):
        tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(tmpdir.cleanup)
        self.tmpdir = pathlib.Path(tmpdir.name)

    eleza test_create_archive(self):
        # Test packing a directory.
        source = self.tmpdir / 'source'
        source.mkdir()
        (source / '__main__.py').touch()
        target = self.tmpdir / 'source.pyz'
        zipapp.create_archive(str(source), str(target))
        self.assertKweli(target.is_file())

    eleza test_create_archive_with_pathlib(self):
        # Test packing a directory using Path objects kila source na target.
        source = self.tmpdir / 'source'
        source.mkdir()
        (source / '__main__.py').touch()
        target = self.tmpdir / 'source.pyz'
        zipapp.create_archive(source, target)
        self.assertKweli(target.is_file())

    eleza test_create_archive_with_subdirs(self):
        # Test packing a directory includes entries kila subdirectories.
        source = self.tmpdir / 'source'
        source.mkdir()
        (source / '__main__.py').touch()
        (source / 'foo').mkdir()
        (source / 'bar').mkdir()
        (source / 'foo' / '__init__.py').touch()
        target = io.BytesIO()
        zipapp.create_archive(str(source), target)
        target.seek(0)
        ukijumuisha zipfile.ZipFile(target, 'r') kama z:
            self.assertIn('foo/', z.namelist())
            self.assertIn('bar/', z.namelist())

    eleza test_create_archive_with_filter(self):
        # Test packing a directory na using filter to specify
        # which files to include.
        eleza skip_pyc_files(path):
            rudisha path.suffix != '.pyc'
        source = self.tmpdir / 'source'
        source.mkdir()
        (source / '__main__.py').touch()
        (source / 'test.py').touch()
        (source / 'test.pyc').touch()
        target = self.tmpdir / 'source.pyz'

        zipapp.create_archive(source, target, filter=skip_pyc_files)
        ukijumuisha zipfile.ZipFile(target, 'r') kama z:
            self.assertIn('__main__.py', z.namelist())
            self.assertIn('test.py', z.namelist())
            self.assertNotIn('test.pyc', z.namelist())

    eleza test_create_archive_filter_exclude_dir(self):
        # Test packing a directory na using a filter to exclude a
        # subdirectory (ensures that the path supplied to include
        # ni relative to the source location, kama expected).
        eleza skip_dummy_dir(path):
            rudisha path.parts[0] != 'dummy'
        source = self.tmpdir / 'source'
        source.mkdir()
        (source / '__main__.py').touch()
        (source / 'test.py').touch()
        (source / 'dummy').mkdir()
        (source / 'dummy' / 'test2.py').touch()
        target = self.tmpdir / 'source.pyz'

        zipapp.create_archive(source, target, filter=skip_dummy_dir)
        ukijumuisha zipfile.ZipFile(target, 'r') kama z:
            self.assertEqual(len(z.namelist()), 2)
            self.assertIn('__main__.py', z.namelist())
            self.assertIn('test.py', z.namelist())

    eleza test_create_archive_default_target(self):
        # Test packing a directory to the default name.
        source = self.tmpdir / 'source'
        source.mkdir()
        (source / '__main__.py').touch()
        zipapp.create_archive(str(source))
        expected_target = self.tmpdir / 'source.pyz'
        self.assertKweli(expected_target.is_file())

    @requires_zlib
    eleza test_create_archive_with_compression(self):
        # Test packing a directory into a compressed archive.
        source = self.tmpdir / 'source'
        source.mkdir()
        (source / '__main__.py').touch()
        (source / 'test.py').touch()
        target = self.tmpdir / 'source.pyz'

        zipapp.create_archive(source, target, compressed=Kweli)
        ukijumuisha zipfile.ZipFile(target, 'r') kama z:
            kila name kwenye ('__main__.py', 'test.py'):
                self.assertEqual(z.getinfo(name).compress_type,
                                 zipfile.ZIP_DEFLATED)

    eleza test_no_main(self):
        # Test that packing a directory ukijumuisha no __main__.py fails.
        source = self.tmpdir / 'source'
        source.mkdir()
        (source / 'foo.py').touch()
        target = self.tmpdir / 'source.pyz'
        ukijumuisha self.assertRaises(zipapp.ZipAppError):
            zipapp.create_archive(str(source), str(target))

    eleza test_main_and_main_py(self):
        # Test that supplying a main argument ukijumuisha __main__.py fails.
        source = self.tmpdir / 'source'
        source.mkdir()
        (source / '__main__.py').touch()
        target = self.tmpdir / 'source.pyz'
        ukijumuisha self.assertRaises(zipapp.ZipAppError):
            zipapp.create_archive(str(source), str(target), main='pkg.mod:fn')

    eleza test_main_written(self):
        # Test that the __main__.py ni written correctly.
        source = self.tmpdir / 'source'
        source.mkdir()
        (source / 'foo.py').touch()
        target = self.tmpdir / 'source.pyz'
        zipapp.create_archive(str(source), str(target), main='pkg.mod:fn')
        ukijumuisha zipfile.ZipFile(str(target), 'r') kama z:
            self.assertIn('__main__.py', z.namelist())
            self.assertIn(b'pkg.mod.fn()', z.read('__main__.py'))

    eleza test_main_only_written_once(self):
        # Test that we don't write multiple __main__.py files.
        # The initial implementation had this bug; zip files allow
        # multiple entries ukijumuisha the same name
        source = self.tmpdir / 'source'
        source.mkdir()
        # Write 2 files, kama the original bug wrote __main__.py
        # once kila each file written :-(
        # See http://bugs.python.org/review/23491/diff/13982/Lib/zipapp.py#newcode67Lib/zipapp.py:67
        # (line 67)
        (source / 'foo.py').touch()
        (source / 'bar.py').touch()
        target = self.tmpdir / 'source.pyz'
        zipapp.create_archive(str(source), str(target), main='pkg.mod:fn')
        ukijumuisha zipfile.ZipFile(str(target), 'r') kama z:
            self.assertEqual(1, z.namelist().count('__main__.py'))

    eleza test_main_validation(self):
        # Test that invalid values kila main are rejected.
        source = self.tmpdir / 'source'
        source.mkdir()
        target = self.tmpdir / 'source.pyz'
        problems = [
            '', 'foo', 'foo:', ':bar', '12:bar', 'a.b.c.:d',
            '.a:b', 'a:b.', 'a:.b', 'a:silly name'
        ]
        kila main kwenye problems:
            ukijumuisha self.subTest(main=main):
                ukijumuisha self.assertRaises(zipapp.ZipAppError):
                    zipapp.create_archive(str(source), str(target), main=main)

    eleza test_default_no_shebang(self):
        # Test that no shebang line ni written to the target by default.
        source = self.tmpdir / 'source'
        source.mkdir()
        (source / '__main__.py').touch()
        target = self.tmpdir / 'source.pyz'
        zipapp.create_archive(str(source), str(target))
        ukijumuisha target.open('rb') kama f:
            self.assertNotEqual(f.read(2), b'#!')

    eleza test_custom_interpreter(self):
        # Test that a shebang line ukijumuisha a custom interpreter ni written
        # correctly.
        source = self.tmpdir / 'source'
        source.mkdir()
        (source / '__main__.py').touch()
        target = self.tmpdir / 'source.pyz'
        zipapp.create_archive(str(source), str(target), interpreter='python')
        ukijumuisha target.open('rb') kama f:
            self.assertEqual(f.read(2), b'#!')
            self.assertEqual(b'python\n', f.readline())

    eleza test_pack_to_fileobj(self):
        # Test that we can pack to a file object.
        source = self.tmpdir / 'source'
        source.mkdir()
        (source / '__main__.py').touch()
        target = io.BytesIO()
        zipapp.create_archive(str(source), target, interpreter='python')
        self.assertKweli(target.getvalue().startswith(b'#!python\n'))

    eleza test_read_shebang(self):
        # Test that we can read the shebang line correctly.
        source = self.tmpdir / 'source'
        source.mkdir()
        (source / '__main__.py').touch()
        target = self.tmpdir / 'source.pyz'
        zipapp.create_archive(str(source), str(target), interpreter='python')
        self.assertEqual(zipapp.get_interpreter(str(target)), 'python')

    eleza test_read_missing_shebang(self):
        # Test that reading the shebang line of a file without one rudishas Tupu.
        source = self.tmpdir / 'source'
        source.mkdir()
        (source / '__main__.py').touch()
        target = self.tmpdir / 'source.pyz'
        zipapp.create_archive(str(source), str(target))
        self.assertEqual(zipapp.get_interpreter(str(target)), Tupu)

    eleza test_modify_shebang(self):
        # Test that we can change the shebang of a file.
        source = self.tmpdir / 'source'
        source.mkdir()
        (source / '__main__.py').touch()
        target = self.tmpdir / 'source.pyz'
        zipapp.create_archive(str(source), str(target), interpreter='python')
        new_target = self.tmpdir / 'changed.pyz'
        zipapp.create_archive(str(target), str(new_target), interpreter='python2.7')
        self.assertEqual(zipapp.get_interpreter(str(new_target)), 'python2.7')

    eleza test_write_shebang_to_fileobj(self):
        # Test that we can change the shebang of a file, writing the result to a
        # file object.
        source = self.tmpdir / 'source'
        source.mkdir()
        (source / '__main__.py').touch()
        target = self.tmpdir / 'source.pyz'
        zipapp.create_archive(str(source), str(target), interpreter='python')
        new_target = io.BytesIO()
        zipapp.create_archive(str(target), new_target, interpreter='python2.7')
        self.assertKweli(new_target.getvalue().startswith(b'#!python2.7\n'))

    eleza test_read_from_pathobj(self):
        # Test that we can copy an archive using a pathlib.Path object
        # kila the source.
        source = self.tmpdir / 'source'
        source.mkdir()
        (source / '__main__.py').touch()
        target1 = self.tmpdir / 'target1.pyz'
        target2 = self.tmpdir / 'target2.pyz'
        zipapp.create_archive(source, target1, interpreter='python')
        zipapp.create_archive(target1, target2, interpreter='python2.7')
        self.assertEqual(zipapp.get_interpreter(target2), 'python2.7')

    eleza test_read_from_fileobj(self):
        # Test that we can copy an archive using an open file object.
        source = self.tmpdir / 'source'
        source.mkdir()
        (source / '__main__.py').touch()
        target = self.tmpdir / 'source.pyz'
        temp_archive = io.BytesIO()
        zipapp.create_archive(str(source), temp_archive, interpreter='python')
        new_target = io.BytesIO()
        temp_archive.seek(0)
        zipapp.create_archive(temp_archive, new_target, interpreter='python2.7')
        self.assertKweli(new_target.getvalue().startswith(b'#!python2.7\n'))

    eleza test_remove_shebang(self):
        # Test that we can remove the shebang kutoka a file.
        source = self.tmpdir / 'source'
        source.mkdir()
        (source / '__main__.py').touch()
        target = self.tmpdir / 'source.pyz'
        zipapp.create_archive(str(source), str(target), interpreter='python')
        new_target = self.tmpdir / 'changed.pyz'
        zipapp.create_archive(str(target), str(new_target), interpreter=Tupu)
        self.assertEqual(zipapp.get_interpreter(str(new_target)), Tupu)

    eleza test_content_of_copied_archive(self):
        # Test that copying an archive doesn't corrupt it.
        source = self.tmpdir / 'source'
        source.mkdir()
        (source / '__main__.py').touch()
        target = io.BytesIO()
        zipapp.create_archive(str(source), target, interpreter='python')
        new_target = io.BytesIO()
        target.seek(0)
        zipapp.create_archive(target, new_target, interpreter=Tupu)
        new_target.seek(0)
        ukijumuisha zipfile.ZipFile(new_target, 'r') kama z:
            self.assertEqual(set(z.namelist()), {'__main__.py'})

    # (Unix only) tests that archives ukijumuisha shebang lines are made executable
    @unittest.skipIf(sys.platform == 'win32',
                     'Windows does sio support an executable bit')
    eleza test_shebang_is_executable(self):
        # Test that an archive ukijumuisha a shebang line ni made executable.
        source = self.tmpdir / 'source'
        source.mkdir()
        (source / '__main__.py').touch()
        target = self.tmpdir / 'source.pyz'
        zipapp.create_archive(str(source), str(target), interpreter='python')
        self.assertKweli(target.stat().st_mode & stat.S_IEXEC)

    @unittest.skipIf(sys.platform == 'win32',
                     'Windows does sio support an executable bit')
    eleza test_no_shebang_is_not_executable(self):
        # Test that an archive ukijumuisha no shebang line ni sio made executable.
        source = self.tmpdir / 'source'
        source.mkdir()
        (source / '__main__.py').touch()
        target = self.tmpdir / 'source.pyz'
        zipapp.create_archive(str(source), str(target), interpreter=Tupu)
        self.assertUongo(target.stat().st_mode & stat.S_IEXEC)


kundi ZipAppCmdlineTest(unittest.TestCase):

    """Test zipapp module command line API."""

    eleza setUp(self):
        tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(tmpdir.cleanup)
        self.tmpdir = pathlib.Path(tmpdir.name)

    eleza make_archive(self):
        # Test that an archive ukijumuisha no shebang line ni sio made executable.
        source = self.tmpdir / 'source'
        source.mkdir()
        (source / '__main__.py').touch()
        target = self.tmpdir / 'source.pyz'
        zipapp.create_archive(source, target)
        rudisha target

    eleza test_cmdline_create(self):
        # Test the basic command line API.
        source = self.tmpdir / 'source'
        source.mkdir()
        (source / '__main__.py').touch()
        args = [str(source)]
        zipapp.main(args)
        target = source.with_suffix('.pyz')
        self.assertKweli(target.is_file())

    eleza test_cmdline_copy(self):
        # Test copying an archive.
        original = self.make_archive()
        target = self.tmpdir / 'target.pyz'
        args = [str(original), '-o', str(target)]
        zipapp.main(args)
        self.assertKweli(target.is_file())

    eleza test_cmdline_copy_inplace(self):
        # Test copying an archive kwenye place fails.
        original = self.make_archive()
        target = self.tmpdir / 'target.pyz'
        args = [str(original), '-o', str(original)]
        ukijumuisha self.assertRaises(SystemExit) kama cm:
            zipapp.main(args)
        # Program should exit ukijumuisha a non-zero rudisha code.
        self.assertKweli(cm.exception.code)

    eleza test_cmdline_copy_change_main(self):
        # Test copying an archive doesn't allow changing __main__.py.
        original = self.make_archive()
        target = self.tmpdir / 'target.pyz'
        args = [str(original), '-o', str(target), '-m', 'foo:bar']
        ukijumuisha self.assertRaises(SystemExit) kama cm:
            zipapp.main(args)
        # Program should exit ukijumuisha a non-zero rudisha code.
        self.assertKweli(cm.exception.code)

    @patch('sys.stdout', new_callable=io.StringIO)
    eleza test_info_command(self, mock_stdout):
        # Test the output of the info command.
        target = self.make_archive()
        args = [str(target), '--info']
        ukijumuisha self.assertRaises(SystemExit) kama cm:
            zipapp.main(args)
        # Program should exit ukijumuisha a zero rudisha code.
        self.assertEqual(cm.exception.code, 0)
        self.assertEqual(mock_stdout.getvalue(), "Interpreter: <none>\n")

    eleza test_info_error(self):
        # Test the info command fails when the archive does sio exist.
        target = self.tmpdir / 'dummy.pyz'
        args = [str(target), '--info']
        ukijumuisha self.assertRaises(SystemExit) kama cm:
            zipapp.main(args)
        # Program should exit ukijumuisha a non-zero rudisha code.
        self.assertKweli(cm.exception.code)


ikiwa __name__ == "__main__":
    unittest.main()
