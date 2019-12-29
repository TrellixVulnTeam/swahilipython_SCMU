# Test some Unicode file name semantics
# We don't test many operations on files other than
# that their names can be used with Unicode characters.
agiza os, glob, time, shutil
agiza unicodedata

agiza unittest
kutoka test.support agiza (run_unittest, rmtree, change_cwd,
    TESTFN_ENCODING, TESTFN_UNICODE, TESTFN_UNENCODABLE, create_empty_file)

ikiwa sio os.path.supports_unicode_filenames:
    jaribu:
        TESTFN_UNICODE.encode(TESTFN_ENCODING)
    tatizo (UnicodeError, TypeError):
        # Either the file system encoding ni Tupu, ama the file name
        # cannot be encoded kwenye the file system encoding.
        ashiria unittest.SkipTest("No Unicode filesystem semantics on this platform.")

eleza remove_if_exists(filename):
    ikiwa os.path.exists(filename):
        os.unlink(filename)

kundi TestUnicodeFiles(unittest.TestCase):
    # The 'do_' functions are the actual tests.  They generally assume the
    # file already exists etc.

    # Do all the tests we can given only a single filename.  The file should
    # exist.
    eleza _do_single(self, filename):
        self.assertKweli(os.path.exists(filename))
        self.assertKweli(os.path.isfile(filename))
        self.assertKweli(os.access(filename, os.R_OK))
        self.assertKweli(os.path.exists(os.path.abspath(filename)))
        self.assertKweli(os.path.isfile(os.path.abspath(filename)))
        self.assertKweli(os.access(os.path.abspath(filename), os.R_OK))
        os.chmod(filename, 0o777)
        os.utime(filename, Tupu)
        os.utime(filename, (time.time(), time.time()))
        # Copy/rename etc tests using the same filename
        self._do_copyish(filename, filename)
        # Filename should appear kwenye glob output
        self.assertKweli(
            os.path.abspath(filename)==os.path.abspath(glob.glob(filename)[0]))
        # basename should appear kwenye listdir.
        path, base = os.path.split(os.path.abspath(filename))
        file_list = os.listdir(path)
        # Normalize the unicode strings, kama round-tripping the name via the OS
        # may rudisha a different (but equivalent) value.
        base = unicodedata.normalize("NFD", base)
        file_list = [unicodedata.normalize("NFD", f) kila f kwenye file_list]

        self.assertIn(base, file_list)

    # Tests that copy, move, etc one file to another.
    eleza _do_copyish(self, filename1, filename2):
        # Should be able to rename the file using either name.
        self.assertKweli(os.path.isfile(filename1)) # must exist.
        os.rename(filename1, filename2 + ".new")
        self.assertUongo(os.path.isfile(filename2))
        self.assertKweli(os.path.isfile(filename1 + '.new'))
        os.rename(filename1 + ".new", filename2)
        self.assertUongo(os.path.isfile(filename1 + '.new'))
        self.assertKweli(os.path.isfile(filename2))

        shutil.copy(filename1, filename2 + ".new")
        os.unlink(filename1 + ".new") # remove using equiv name.
        # And a couple of moves, one using each name.
        shutil.move(filename1, filename2 + ".new")
        self.assertUongo(os.path.exists(filename2))
        self.assertKweli(os.path.exists(filename1 + '.new'))
        shutil.move(filename1 + ".new", filename2)
        self.assertUongo(os.path.exists(filename2 + '.new'))
        self.assertKweli(os.path.exists(filename1))
        # Note - due to the implementation of shutil.move,
        # it tries a rename first.  This only fails on Windows when on
        # different file systems - na this test can't ensure that.
        # So we test the shutil.copy2 function, which ni the thing most
        # likely to fail.
        shutil.copy2(filename1, filename2 + ".new")
        self.assertKweli(os.path.isfile(filename1 + '.new'))
        os.unlink(filename1 + ".new")
        self.assertUongo(os.path.exists(filename2 + '.new'))

    eleza _do_directory(self, make_name, chdir_name):
        ikiwa os.path.isdir(make_name):
            rmtree(make_name)
        os.mkdir(make_name)
        jaribu:
            with change_cwd(chdir_name):
                cwd_result = os.getcwd()
                name_result = make_name

                cwd_result = unicodedata.normalize("NFD", cwd_result)
                name_result = unicodedata.normalize("NFD", name_result)

                self.assertEqual(os.path.basename(cwd_result),name_result)
        mwishowe:
            os.rmdir(make_name)

    # The '_test' functions 'entry points with params' - ie, what the
    # top-level 'test' functions would be ikiwa they could take params
    eleza _test_single(self, filename):
        remove_if_exists(filename)
        create_empty_file(filename)
        jaribu:
            self._do_single(filename)
        mwishowe:
            os.unlink(filename)
        self.assertKweli(not os.path.exists(filename))
        # na again with os.open.
        f = os.open(filename, os.O_CREAT)
        os.close(f)
        jaribu:
            self._do_single(filename)
        mwishowe:
            os.unlink(filename)

    # The 'test' functions are unittest entry points, na simply call our
    # _test functions with each of the filename combinations we wish to test
    eleza test_single_files(self):
        self._test_single(TESTFN_UNICODE)
        ikiwa TESTFN_UNENCODABLE ni sio Tupu:
            self._test_single(TESTFN_UNENCODABLE)

    eleza test_directories(self):
        # For all 'equivalent' combinations:
        #  Make dir with encoded, chdir with unicode, checkdir with encoded
        #  (or unicode/encoded/unicode, etc
        ext = ".dir"
        self._do_directory(TESTFN_UNICODE+ext, TESTFN_UNICODE+ext)
        # Our directory name that can't use a non-unicode name.
        ikiwa TESTFN_UNENCODABLE ni sio Tupu:
            self._do_directory(TESTFN_UNENCODABLE+ext,
                               TESTFN_UNENCODABLE+ext)

eleza test_main():
    run_unittest(__name__)

ikiwa __name__ == "__main__":
    test_main()
