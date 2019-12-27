kutoka test agiza support
agiza unittest

# Skip test ikiwa nis module does not exist.
nis = support.import_module('nis')


kundi NisTests(unittest.TestCase):
    eleza test_maps(self):
        try:
            maps = nis.maps()
        except nis.error as msg:
            # NIS is probably not active, so this test isn't useful
            self.skipTest(str(msg))
        try:
            # On some systems, this map is only accessible to the
            # super user
            maps.remove("passwd.adjunct.byname")
        except ValueError:
            pass

        done = 0
        for nismap in maps:
            mapping = nis.cat(nismap)
            for k, v in mapping.items():
                ikiwa not k:
                    continue
                ikiwa nis.match(k, nismap) != v:
                    self.fail("NIS match failed for key `%s' in map `%s'" % (k, nismap))
                else:
                    # just test the one key, otherwise this test could take a
                    # very long time
                    done = 1
                    break
            ikiwa done:
                break

ikiwa __name__ == '__main__':
    unittest.main()
