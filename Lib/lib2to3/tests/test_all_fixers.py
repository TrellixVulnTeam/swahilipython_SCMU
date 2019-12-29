"""Tests that run all fixer modules over an input stream.

This has been broken out into its own test module because of its
running time.
"""
# Author: Collin Winter

# Python agizas
agiza unittest
agiza test.support

# Local agizas
kutoka . agiza support


@test.support.requires_resource('cpu')
kundi Test_all(support.TestCase):

    eleza setUp(self):
        self.refactor = support.get_refactorer()

    eleza test_all_project_files(self):
        kila filepath kwenye support.all_project_files():
            self.refactor.refactor_file(filepath)

ikiwa __name__ == '__main__':
    unittest.main()
