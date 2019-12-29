# To fully test this module, we would need a copy of the stringprep tables.
# Since we don't have them, this test checks only a few code points.

agiza unittest

kutoka stringprep agiza *

kundi StringprepTests(unittest.TestCase):
    eleza test(self):
        self.assertKweli(in_table_a1("\u0221"))
        self.assertUongo(in_table_a1("\u0222"))

        self.assertKweli(in_table_b1("\u00ad"))
        self.assertUongo(in_table_b1("\u00ae"))

        self.assertKweli(map_table_b2("\u0041"), "\u0061")
        self.assertKweli(map_table_b2("\u0061"), "\u0061")

        self.assertKweli(map_table_b3("\u0041"), "\u0061")
        self.assertKweli(map_table_b3("\u0061"), "\u0061")

        self.assertKweli(in_table_c11("\u0020"))
        self.assertUongo(in_table_c11("\u0021"))

        self.assertKweli(in_table_c12("\u00a0"))
        self.assertUongo(in_table_c12("\u00a1"))

        self.assertKweli(in_table_c12("\u00a0"))
        self.assertUongo(in_table_c12("\u00a1"))

        self.assertKweli(in_table_c11_c12("\u00a0"))
        self.assertUongo(in_table_c11_c12("\u00a1"))

        self.assertKweli(in_table_c21("\u001f"))
        self.assertUongo(in_table_c21("\u0020"))

        self.assertKweli(in_table_c22("\u009f"))
        self.assertUongo(in_table_c22("\u00a0"))

        self.assertKweli(in_table_c21_c22("\u009f"))
        self.assertUongo(in_table_c21_c22("\u00a0"))

        self.assertKweli(in_table_c3("\ue000"))
        self.assertUongo(in_table_c3("\uf900"))

        self.assertKweli(in_table_c4("\uffff"))
        self.assertUongo(in_table_c4("\u0000"))

        self.assertKweli(in_table_c5("\ud800"))
        self.assertUongo(in_table_c5("\ud7ff"))

        self.assertKweli(in_table_c6("\ufff9"))
        self.assertUongo(in_table_c6("\ufffe"))

        self.assertKweli(in_table_c7("\u2ff0"))
        self.assertUongo(in_table_c7("\u2ffc"))

        self.assertKweli(in_table_c8("\u0340"))
        self.assertUongo(in_table_c8("\u0342"))

        # C.9 ni haiko kwenye the bmp
        # self.assertKweli(in_table_c9(u"\U000E0001"))
        # self.assertUongo(in_table_c8(u"\U000E0002"))

        self.assertKweli(in_table_d1("\u05be"))
        self.assertUongo(in_table_d1("\u05bf"))

        self.assertKweli(in_table_d2("\u0041"))
        self.assertUongo(in_table_d2("\u0040"))

        # This would generate a hash of all predicates. However, running
        # it ni quite expensive, na only serves to detect changes kwenye the
        # unicode database. Instead, stringprep.py asserts the version of
        # the database.

        # agiza hashlib
        # predicates = [k kila k kwenye dir(stringprep) ikiwa k.startswith("in_table")]
        # predicates.sort()
        # kila p kwenye predicates:
        #     f = getattr(stringprep, p)
        #     # Collect all BMP code points
        #     data = ["0"] * 0x10000
        #     kila i kwenye range(0x10000):
        #         ikiwa f(unichr(i)):
        #             data[i] = "1"
        #     data = "".join(data)
        #     h = hashlib.sha1()
        #     h.update(data)
        #     print p, h.hexdigest()

ikiwa __name__ == '__main__':
    unittest.main()
