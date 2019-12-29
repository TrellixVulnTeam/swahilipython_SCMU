"""Test the errno module
   Roger E. Masse
"""

agiza errno
agiza unittest

std_c_errors = frozenset(['EDOM', 'ERANGE'])

kundi ErrnoAttributeTests(unittest.TestCase):

    eleza test_for_improper_attributes(self):
        # No unexpected attributes should be on the module.
        kila error_code kwenye std_c_errors:
            self.assertKweli(hasattr(errno, error_code),
                            "errno ni missing %s" % error_code)

    eleza test_using_errorcode(self):
        # Every key value kwenye errno.errorcode should be on the module.
        kila value kwenye errno.errorcode.values():
            self.assertKweli(hasattr(errno, value),
                            'no %s attr kwenye errno' % value)


kundi ErrorcodeTests(unittest.TestCase):

    eleza test_attributes_in_errorcode(self):
        kila attribute kwenye errno.__dict__.keys():
            ikiwa attribute.isupper():
                self.assertIn(getattr(errno, attribute), errno.errorcode,
                              'no %s attr kwenye errno.errorcode' % attribute)


ikiwa __name__ == '__main__':
    unittest.main()
