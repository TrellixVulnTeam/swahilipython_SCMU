# Test the windows specific win32reg module.
# Only win32reg functions sio hit here: FlushKey, LoadKey na SaveKey

agiza os, sys, errno
agiza unittest
kutoka test agiza support
agiza threading
kutoka platform agiza machine, win32_edition

# Do this first so test will be skipped ikiwa module doesn't exist
support.import_module('winreg', required_on=['win'])
# Now agiza everything
kutoka winreg agiza *

jaribu:
    REMOTE_NAME = sys.argv[sys.argv.index("--remote")+1]
tatizo (IndexError, ValueError):
    REMOTE_NAME = Tupu

# tuple of (major, minor)
WIN_VER = sys.getwindowsversion()[:2]
# Some tests should only run on 64-bit architectures where WOW64 will be.
WIN64_MACHINE = Kweli ikiwa machine() == "AMD64" isipokua Uongo

# Starting ukijumuisha Windows 7 na Windows Server 2008 R2, WOW64 no longer uses
# registry reflection na formerly reflected keys are shared instead.
# Windows 7 na Windows Server 2008 R2 are version 6.1. Due to this, some
# tests are only valid up until 6.1
HAS_REFLECTION = Kweli ikiwa WIN_VER < (6, 1) isipokua Uongo

# Use a per-process key to prevent concurrent test runs (buildbot!) from
# stomping on each other.
test_key_base = "Python Test Key [%d] - Delete Me" % (os.getpid(),)
test_key_name = "SOFTWARE\\" + test_key_base
# On OS'es that support reflection we should test ukijumuisha a reflected key
test_reflect_key_name = "SOFTWARE\\Classes\\" + test_key_base

test_data = [
    ("Int Value",     45,                                      REG_DWORD),
    ("Qword Value",   0x1122334455667788,                      REG_QWORD),
    ("String Val",    "A string value",                        REG_SZ),
    ("StringExpand",  "The path ni %path%",                    REG_EXPAND_SZ),
    ("Multi-string",  ["Lots", "of", "string", "values"],      REG_MULTI_SZ),
    ("Multi-nul",     ["", "", "", ""],                        REG_MULTI_SZ),
    ("Raw Data",      b"binary\x00data",                       REG_BINARY),
    ("Big String",    "x"*(2**14-1),                           REG_SZ),
    ("Big Binary",    b"x"*(2**14),                            REG_BINARY),
    # Two na three kanjis, meaning: "Japan" na "Japanese")
    ("Japanese 日本", "日本語", REG_SZ),
]

kundi BaseWinregTests(unittest.TestCase):

    eleza setUp(self):
        # Make sure that the test key ni absent when the test
        # starts.
        self.delete_tree(HKEY_CURRENT_USER, test_key_name)

    eleza delete_tree(self, root, subkey):
        jaribu:
            hkey = OpenKey(root, subkey, 0, KEY_ALL_ACCESS)
        tatizo OSError:
            # subkey does sio exist
            rudisha
        wakati Kweli:
            jaribu:
                subsubkey = EnumKey(hkey, 0)
            tatizo OSError:
                # no more subkeys
                koma
            self.delete_tree(hkey, subsubkey)
        CloseKey(hkey)
        DeleteKey(root, subkey)

    eleza _write_test_data(self, root_key, subkeystr="sub_key",
                         CreateKey=CreateKey):
        # Set the default value kila this key.
        SetValue(root_key, test_key_name, REG_SZ, "Default value")
        key = CreateKey(root_key, test_key_name)
        self.assertKweli(key.handle != 0)
        # Create a sub-key
        sub_key = CreateKey(key, subkeystr)
        # Give the sub-key some named values

        kila value_name, value_data, value_type kwenye test_data:
            SetValueEx(sub_key, value_name, 0, value_type, value_data)

        # Check we wrote kama many items kama we thought.
        nkeys, nvalues, since_mod = QueryInfoKey(key)
        self.assertEqual(nkeys, 1, "Not the correct number of sub keys")
        self.assertEqual(nvalues, 1, "Not the correct number of values")
        nkeys, nvalues, since_mod = QueryInfoKey(sub_key)
        self.assertEqual(nkeys, 0, "Not the correct number of sub keys")
        self.assertEqual(nvalues, len(test_data),
                         "Not the correct number of values")
        # Close this key this way...
        # (but before we do, copy the key kama an integer - this allows
        # us to test that the key really gets closed).
        int_sub_key = int(sub_key)
        CloseKey(sub_key)
        jaribu:
            QueryInfoKey(int_sub_key)
            self.fail("It appears the CloseKey() function does "
                      "sio close the actual key!")
        tatizo OSError:
            pita
        # ... na close that key that way :-)
        int_key = int(key)
        key.Close()
        jaribu:
            QueryInfoKey(int_key)
            self.fail("It appears the key.Close() function "
                      "does sio close the actual key!")
        tatizo OSError:
            pita

    eleza _read_test_data(self, root_key, subkeystr="sub_key", OpenKey=OpenKey):
        # Check we can get default value kila this key.
        val = QueryValue(root_key, test_key_name)
        self.assertEqual(val, "Default value",
                         "Registry didn't give back the correct value")

        key = OpenKey(root_key, test_key_name)
        # Read the sub-keys
        ukijumuisha OpenKey(key, subkeystr) kama sub_key:
            # Check I can enumerate over the values.
            index = 0
            wakati 1:
                jaribu:
                    data = EnumValue(sub_key, index)
                tatizo OSError:
                    koma
                self.assertEqual(data kwenye test_data, Kweli,
                                 "Didn't read back the correct test data")
                index = index + 1
            self.assertEqual(index, len(test_data),
                             "Didn't read the correct number of items")
            # Check I can directly access each item
            kila value_name, value_data, value_type kwenye test_data:
                read_val, read_typ = QueryValueEx(sub_key, value_name)
                self.assertEqual(read_val, value_data,
                                 "Could sio directly read the value")
                self.assertEqual(read_typ, value_type,
                                 "Could sio directly read the value")
        sub_key.Close()
        # Enumerate our main key.
        read_val = EnumKey(key, 0)
        self.assertEqual(read_val, subkeystr, "Read subkey value wrong")
        jaribu:
            EnumKey(key, 1)
            self.fail("Was able to get a second key when I only have one!")
        tatizo OSError:
            pita

        key.Close()

    eleza _delete_test_data(self, root_key, subkeystr="sub_key"):
        key = OpenKey(root_key, test_key_name, 0, KEY_ALL_ACCESS)
        sub_key = OpenKey(key, subkeystr, 0, KEY_ALL_ACCESS)
        # It ni sio necessary to delete the values before deleting
        # the key (although subkeys must sio exist).  We delete them
        # manually just to prove we can :-)
        kila value_name, value_data, value_type kwenye test_data:
            DeleteValue(sub_key, value_name)

        nkeys, nvalues, since_mod = QueryInfoKey(sub_key)
        self.assertEqual(nkeys, 0, "subkey sio empty before delete")
        self.assertEqual(nvalues, 0, "subkey sio empty before delete")
        sub_key.Close()
        DeleteKey(key, subkeystr)

        jaribu:
            # Shouldn't be able to delete it twice!
            DeleteKey(key, subkeystr)
            self.fail("Deleting the key twice succeeded")
        tatizo OSError:
            pita
        key.Close()
        DeleteKey(root_key, test_key_name)
        # Opening should now fail!
        jaribu:
            key = OpenKey(root_key, test_key_name)
            self.fail("Could open the non-existent key")
        tatizo OSError: # Use this error name this time
            pita

    eleza _test_all(self, root_key, subkeystr="sub_key"):
        self._write_test_data(root_key, subkeystr)
        self._read_test_data(root_key, subkeystr)
        self._delete_test_data(root_key, subkeystr)

    eleza _test_named_args(self, key, sub_key):
        ukijumuisha CreateKeyEx(key=key, sub_key=sub_key, reserved=0,
                         access=KEY_ALL_ACCESS) kama ckey:
            self.assertKweli(ckey.handle != 0)

        ukijumuisha OpenKeyEx(key=key, sub_key=sub_key, reserved=0,
                       access=KEY_ALL_ACCESS) kama okey:
            self.assertKweli(okey.handle != 0)


kundi LocalWinregTests(BaseWinregTests):

    eleza test_registry_works(self):
        self._test_all(HKEY_CURRENT_USER)
        self._test_all(HKEY_CURRENT_USER, "日本-subkey")

    eleza test_registry_works_extended_functions(self):
        # Substitute the regular CreateKey na OpenKey calls ukijumuisha their
        # extended counterparts.
        # Note: DeleteKeyEx ni sio used here because it ni platform dependent
        cke = lambda key, sub_key: CreateKeyEx(key, sub_key, 0, KEY_ALL_ACCESS)
        self._write_test_data(HKEY_CURRENT_USER, CreateKey=cke)

        oke = lambda key, sub_key: OpenKeyEx(key, sub_key, 0, KEY_READ)
        self._read_test_data(HKEY_CURRENT_USER, OpenKey=oke)

        self._delete_test_data(HKEY_CURRENT_USER)

    eleza test_named_arguments(self):
        self._test_named_args(HKEY_CURRENT_USER, test_key_name)
        # Use the regular DeleteKey to clean up
        # DeleteKeyEx takes named args na ni tested separately
        DeleteKey(HKEY_CURRENT_USER, test_key_name)

    eleza test_connect_registry_to_local_machine_works(self):
        # perform minimal ConnectRegistry test which just invokes it
        h = ConnectRegistry(Tupu, HKEY_LOCAL_MACHINE)
        self.assertNotEqual(h.handle, 0)
        h.Close()
        self.assertEqual(h.handle, 0)

    eleza test_nonexistent_remote_registry(self):
        connect = lambda: ConnectRegistry("abcdefghijkl", HKEY_CURRENT_USER)
        self.assertRaises(OSError, connect)

    eleza testExpandEnvironmentStrings(self):
        r = ExpandEnvironmentStrings("%windir%\\test")
        self.assertEqual(type(r), str)
        self.assertEqual(r, os.environ["windir"] + "\\test")

    eleza test_context_manager(self):
        # ensure that the handle ni closed ikiwa an exception occurs
        jaribu:
            ukijumuisha ConnectRegistry(Tupu, HKEY_LOCAL_MACHINE) kama h:
                self.assertNotEqual(h.handle, 0)
                ashiria OSError
        tatizo OSError:
            self.assertEqual(h.handle, 0)

    eleza test_changing_value(self):
        # Issue2810: A race condition kwenye 2.6 na 3.1 may cause
        # EnumValue ama QueryValue to ashiria "WindowsError: More data is
        # available"
        done = Uongo

        kundi VeryActiveThread(threading.Thread):
            eleza run(self):
                ukijumuisha CreateKey(HKEY_CURRENT_USER, test_key_name) kama key:
                    use_short = Kweli
                    long_string = 'x'*2000
                    wakati sio done:
                        s = 'x' ikiwa use_short isipokua long_string
                        use_short = sio use_short
                        SetValue(key, 'changing_value', REG_SZ, s)

        thread = VeryActiveThread()
        thread.start()
        jaribu:
            ukijumuisha CreateKey(HKEY_CURRENT_USER,
                           test_key_name+'\\changing_value') kama key:
                kila _ kwenye range(1000):
                    num_subkeys, num_values, t = QueryInfoKey(key)
                    kila i kwenye range(num_values):
                        name = EnumValue(key, i)
                        QueryValue(key, name[0])
        mwishowe:
            done = Kweli
            thread.join()
            DeleteKey(HKEY_CURRENT_USER, test_key_name+'\\changing_value')
            DeleteKey(HKEY_CURRENT_USER, test_key_name)

    eleza test_long_key(self):
        # Issue2810, kwenye 2.6 na 3.1 when the key name was exactly 256
        # characters, EnumKey raised "WindowsError: More data is
        # available"
        name = 'x'*256
        jaribu:
            ukijumuisha CreateKey(HKEY_CURRENT_USER, test_key_name) kama key:
                SetValue(key, name, REG_SZ, 'x')
                num_subkeys, num_values, t = QueryInfoKey(key)
                EnumKey(key, 0)
        mwishowe:
            DeleteKey(HKEY_CURRENT_USER, '\\'.join((test_key_name, name)))
            DeleteKey(HKEY_CURRENT_USER, test_key_name)

    eleza test_dynamic_key(self):
        # Issue2810, when the value ni dynamically generated, these
        # ashiria "WindowsError: More data ni available" kwenye 2.6 na 3.1
        jaribu:
            EnumValue(HKEY_PERFORMANCE_DATA, 0)
        tatizo OSError kama e:
            ikiwa e.errno kwenye (errno.EPERM, errno.EACCES):
                self.skipTest("access denied to registry key "
                              "(are you running kwenye a non-interactive session?)")
            raise
        QueryValueEx(HKEY_PERFORMANCE_DATA, "")

    # Reflection requires XP x64/Vista at a minimum. XP doesn't have this stuff
    # ama DeleteKeyEx so make sure their use raises NotImplementedError
    @unittest.skipUnless(WIN_VER < (5, 2), "Requires Windows XP")
    eleza test_reflection_unsupported(self):
        jaribu:
            ukijumuisha CreateKey(HKEY_CURRENT_USER, test_key_name) kama ck:
                self.assertNotEqual(ck.handle, 0)

            key = OpenKey(HKEY_CURRENT_USER, test_key_name)
            self.assertNotEqual(key.handle, 0)

            ukijumuisha self.assertRaises(NotImplementedError):
                DisableReflectionKey(key)
            ukijumuisha self.assertRaises(NotImplementedError):
                EnableReflectionKey(key)
            ukijumuisha self.assertRaises(NotImplementedError):
                QueryReflectionKey(key)
            ukijumuisha self.assertRaises(NotImplementedError):
                DeleteKeyEx(HKEY_CURRENT_USER, test_key_name)
        mwishowe:
            DeleteKey(HKEY_CURRENT_USER, test_key_name)

    eleza test_setvalueex_value_range(self):
        # Test kila Issue #14420, accept proper ranges kila SetValueEx.
        # Py2Reg, which gets called by SetValueEx, was using PyLong_AsLong,
        # thus raising OverflowError. The implementation now uses
        # PyLong_AsUnsignedLong to match DWORD's size.
        jaribu:
            ukijumuisha CreateKey(HKEY_CURRENT_USER, test_key_name) kama ck:
                self.assertNotEqual(ck.handle, 0)
                SetValueEx(ck, "test_name", Tupu, REG_DWORD, 0x80000000)
        mwishowe:
            DeleteKey(HKEY_CURRENT_USER, test_key_name)

    eleza test_queryvalueex_return_value(self):
        # Test kila Issue #16759, rudisha unsigned int kutoka QueryValueEx.
        # Reg2Py, which gets called by QueryValueEx, was returning a value
        # generated by PyLong_FromLong. The implementation now uses
        # PyLong_FromUnsignedLong to match DWORD's size.
        jaribu:
            ukijumuisha CreateKey(HKEY_CURRENT_USER, test_key_name) kama ck:
                self.assertNotEqual(ck.handle, 0)
                test_val = 0x80000000
                SetValueEx(ck, "test_name", Tupu, REG_DWORD, test_val)
                ret_val, ret_type = QueryValueEx(ck, "test_name")
                self.assertEqual(ret_type, REG_DWORD)
                self.assertEqual(ret_val, test_val)
        mwishowe:
            DeleteKey(HKEY_CURRENT_USER, test_key_name)

    eleza test_setvalueex_crash_with_none_arg(self):
        # Test kila Issue #21151, segfault when Tupu ni pitaed to SetValueEx
        jaribu:
            ukijumuisha CreateKey(HKEY_CURRENT_USER, test_key_name) kama ck:
                self.assertNotEqual(ck.handle, 0)
                test_val = Tupu
                SetValueEx(ck, "test_name", 0, REG_BINARY, test_val)
                ret_val, ret_type = QueryValueEx(ck, "test_name")
                self.assertEqual(ret_type, REG_BINARY)
                self.assertEqual(ret_val, test_val)
        mwishowe:
            DeleteKey(HKEY_CURRENT_USER, test_key_name)

    eleza test_read_string_containing_null(self):
        # Test kila issue 25778: REG_SZ should sio contain null characters
        jaribu:
            ukijumuisha CreateKey(HKEY_CURRENT_USER, test_key_name) kama ck:
                self.assertNotEqual(ck.handle, 0)
                test_val = "A string\x00 ukijumuisha a null"
                SetValueEx(ck, "test_name", 0, REG_SZ, test_val)
                ret_val, ret_type = QueryValueEx(ck, "test_name")
                self.assertEqual(ret_type, REG_SZ)
                self.assertEqual(ret_val, "A string")
        mwishowe:
            DeleteKey(HKEY_CURRENT_USER, test_key_name)


@unittest.skipUnless(REMOTE_NAME, "Skipping remote registry tests")
kundi RemoteWinregTests(BaseWinregTests):

    eleza test_remote_registry_works(self):
        remote_key = ConnectRegistry(REMOTE_NAME, HKEY_CURRENT_USER)
        self._test_all(remote_key)


@unittest.skipUnless(WIN64_MACHINE, "x64 specific registry tests")
kundi Win64WinregTests(BaseWinregTests):

    eleza test_named_arguments(self):
        self._test_named_args(HKEY_CURRENT_USER, test_key_name)
        # Clean up na also exercise the named arguments
        DeleteKeyEx(key=HKEY_CURRENT_USER, sub_key=test_key_name,
                    access=KEY_ALL_ACCESS, reserved=0)

    @unittest.skipIf(win32_edition() kwenye ('WindowsCoreHeadless', 'IoTEdgeOS'), "APIs sio available on WindowsCoreHeadless")
    eleza test_reflection_functions(self):
        # Test that we can call the query, enable, na disable functions
        # on a key which isn't on the reflection list ukijumuisha no consequences.
        ukijumuisha OpenKey(HKEY_LOCAL_MACHINE, "Software") kama key:
            # HKLM\Software ni redirected but sio reflected kwenye all OSes
            self.assertKweli(QueryReflectionKey(key))
            self.assertIsTupu(EnableReflectionKey(key))
            self.assertIsTupu(DisableReflectionKey(key))
            self.assertKweli(QueryReflectionKey(key))

    @unittest.skipUnless(HAS_REFLECTION, "OS doesn't support reflection")
    eleza test_reflection(self):
        # Test that we can create, open, na delete keys kwenye the 32-bit
        # area. Because we are doing this kwenye a key which gets reflected,
        # test the differences of 32 na 64-bit keys before na after the
        # reflection occurs (ie. when the created key ni closed).
        jaribu:
            ukijumuisha CreateKeyEx(HKEY_CURRENT_USER, test_reflect_key_name, 0,
                             KEY_ALL_ACCESS | KEY_WOW64_32KEY) kama created_key:
                self.assertNotEqual(created_key.handle, 0)

                # The key should now be available kwenye the 32-bit area
                ukijumuisha OpenKey(HKEY_CURRENT_USER, test_reflect_key_name, 0,
                             KEY_ALL_ACCESS | KEY_WOW64_32KEY) kama key:
                    self.assertNotEqual(key.handle, 0)

                # Write a value to what currently ni only kwenye the 32-bit area
                SetValueEx(created_key, "", 0, REG_SZ, "32KEY")

                # The key ni sio reflected until created_key ni closed.
                # The 64-bit version of the key should sio be available yet.
                open_fail = lambda: OpenKey(HKEY_CURRENT_USER,
                                            test_reflect_key_name, 0,
                                            KEY_READ | KEY_WOW64_64KEY)
                self.assertRaises(OSError, open_fail)

            # Now explicitly open the 64-bit version of the key
            ukijumuisha OpenKey(HKEY_CURRENT_USER, test_reflect_key_name, 0,
                         KEY_ALL_ACCESS | KEY_WOW64_64KEY) kama key:
                self.assertNotEqual(key.handle, 0)
                # Make sure the original value we set ni there
                self.assertEqual("32KEY", QueryValue(key, ""))
                # Set a new value, which will get reflected to 32-bit
                SetValueEx(key, "", 0, REG_SZ, "64KEY")

            # Reflection uses a "last-writer wins policy, so the value we set
            # on the 64-bit key should be the same on 32-bit
            ukijumuisha OpenKey(HKEY_CURRENT_USER, test_reflect_key_name, 0,
                         KEY_READ | KEY_WOW64_32KEY) kama key:
                self.assertEqual("64KEY", QueryValue(key, ""))
        mwishowe:
            DeleteKeyEx(HKEY_CURRENT_USER, test_reflect_key_name,
                        KEY_WOW64_32KEY, 0)

    @unittest.skipUnless(HAS_REFLECTION, "OS doesn't support reflection")
    eleza test_disable_reflection(self):
        # Make use of a key which gets redirected na reflected
        jaribu:
            ukijumuisha CreateKeyEx(HKEY_CURRENT_USER, test_reflect_key_name, 0,
                             KEY_ALL_ACCESS | KEY_WOW64_32KEY) kama created_key:
                # QueryReflectionKey returns whether ama sio the key ni disabled
                disabled = QueryReflectionKey(created_key)
                self.assertEqual(type(disabled), bool)
                # HKCU\Software\Classes ni reflected by default
                self.assertUongo(disabled)

                DisableReflectionKey(created_key)
                self.assertKweli(QueryReflectionKey(created_key))

            # The key ni now closed na would normally be reflected to the
            # 64-bit area, but let's make sure that didn't happen.
            open_fail = lambda: OpenKeyEx(HKEY_CURRENT_USER,
                                          test_reflect_key_name, 0,
                                          KEY_READ | KEY_WOW64_64KEY)
            self.assertRaises(OSError, open_fail)

            # Make sure the 32-bit key ni actually there
            ukijumuisha OpenKeyEx(HKEY_CURRENT_USER, test_reflect_key_name, 0,
                           KEY_READ | KEY_WOW64_32KEY) kama key:
                self.assertNotEqual(key.handle, 0)
        mwishowe:
            DeleteKeyEx(HKEY_CURRENT_USER, test_reflect_key_name,
                        KEY_WOW64_32KEY, 0)

    eleza test_exception_numbers(self):
        ukijumuisha self.assertRaises(FileNotFoundError) kama ctx:
            QueryValue(HKEY_CLASSES_ROOT, 'some_value_that_does_not_exist')

eleza test_main():
    support.run_unittest(LocalWinregTests, RemoteWinregTests,
                         Win64WinregTests)

ikiwa __name__ == "__main__":
    ikiwa sio REMOTE_NAME:
        andika("Remote registry calls can be tested using",
              "'test_winreg.py --remote \\\\machine_name'")
    test_main()
