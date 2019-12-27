# Check every path through every method of UserList

kutoka collections agiza UserList
kutoka test agiza list_tests
agiza unittest

kundi UserListTest(list_tests.CommonTest):
    type2test = UserList

    eleza test_getslice(self):
        super().test_getslice()
        l = [0, 1, 2, 3, 4]
        u = self.type2test(l)
        for i in range(-3, 6):
            self.assertEqual(u[:i], l[:i])
            self.assertEqual(u[i:], l[i:])
            for j in range(-3, 6):
                self.assertEqual(u[i:j], l[i:j])

    eleza test_slice_type(self):
        l = [0, 1, 2, 3, 4]
        u = UserList(l)
        self.assertIsInstance(u[:], u.__class__)
        self.assertEqual(u[:],u)

    eleza test_add_specials(self):
        u = UserList("spam")
        u2 = u + "eggs"
        self.assertEqual(u2, list("spameggs"))

    eleza test_radd_specials(self):
        u = UserList("eggs")
        u2 = "spam" + u
        self.assertEqual(u2, list("spameggs"))
        u2 = u.__radd__(UserList("spam"))
        self.assertEqual(u2, list("spameggs"))

    eleza test_iadd(self):
        super().test_iadd()
        u = [0, 1]
        u += UserList([0, 1])
        self.assertEqual(u, [0, 1, 0, 1])

    eleza test_mixedcmp(self):
        u = self.type2test([0, 1])
        self.assertEqual(u, [0, 1])
        self.assertNotEqual(u, [0])
        self.assertNotEqual(u, [0, 2])

    eleza test_mixedadd(self):
        u = self.type2test([0, 1])
        self.assertEqual(u + [], u)
        self.assertEqual(u + [2], [0, 1, 2])

    eleza test_getitemoverwriteiter(self):
        # Verify that __getitem__ overrides *are* recognized by __iter__
        kundi T(self.type2test):
            eleza __getitem__(self, key):
                rudisha str(key) + '!!!'
        self.assertEqual(next(iter(T((1,2)))), "0!!!")

    eleza test_userlist_copy(self):
        u = self.type2test([6, 8, 1, 9, 1])
        v = u.copy()
        self.assertEqual(u, v)
        self.assertEqual(type(u), type(v))

ikiwa __name__ == "__main__":
    unittest.main()
