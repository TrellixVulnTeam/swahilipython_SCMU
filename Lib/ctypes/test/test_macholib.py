agiza os
agiza sys
agiza unittest

# Bob Ippolito:
#
# Ok.. the code to find the filename kila __getattr__ should look
# something like:
#
# agiza os
# kutoka macholib.dyld agiza dyld_find
#
# eleza find_lib(name):
#      possible = ['lib'+name+'.dylib', name+'.dylib',
#      name+'.framework/'+name]
#      kila dylib kwenye possible:
#          jaribu:
#              rudisha os.path.realpath(dyld_find(dylib))
#          tatizo ValueError:
#              pita
#      ashiria ValueError, "%s sio found" % (name,)
#
# It'll have output like this:
#
#  >>> find_lib('pthread')
# '/usr/lib/libSystem.B.dylib'
#  >>> find_lib('z')
# '/usr/lib/libz.1.dylib'
#  >>> find_lib('IOKit')
# '/System/Library/Frameworks/IOKit.framework/Versions/A/IOKit'
#
# -bob

kutoka ctypes.macholib.dyld agiza dyld_find

eleza find_lib(name):
    possible = ['lib'+name+'.dylib', name+'.dylib', name+'.framework/'+name]
    kila dylib kwenye possible:
        jaribu:
            rudisha os.path.realpath(dyld_find(dylib))
        tatizo ValueError:
            pita
    ashiria ValueError("%s sio found" % (name,))

kundi MachOTest(unittest.TestCase):
    @unittest.skipUnless(sys.platform == "darwin", 'OSX-specific test')
    eleza test_find(self):

        self.assertEqual(find_lib('pthread'),
                             '/usr/lib/libSystem.B.dylib')

        result = find_lib('z')
        # Issue #21093: dyld default search path includes $HOME/lib na
        # /usr/local/lib before /usr/lib, which caused test failures if
        # a local copy of libz exists kwenye one of them. Now ignore the head
        # of the path.
        self.assertRegex(result, r".*/lib/libz\..*.*\.dylib")

        self.assertEqual(find_lib('IOKit'),
                             '/System/Library/Frameworks/IOKit.framework/Versions/A/IOKit')

ikiwa __name__ == "__main__":
    unittest.main()
