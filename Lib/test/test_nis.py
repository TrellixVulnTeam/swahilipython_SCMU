kutoka test agiza support
agiza unittest

# Skip test ikiwa nis module does sio exist.
nis = support.import_module('nis')


kundi NisTests(unittest.TestCase):
    eleza test_maps(self):
        jaribu:
            maps = nis.maps()
        except nis.error as msg:
            # NIS ni probably sio active, so this test isn't useful
            self.skipTest(str(msg))
        jaribu:
            # On some systems, this map ni only accessible to the
            # super user
            maps.remove("passwd.adjunct.byname")
        except ValueError:
            pass

        done = 0
        kila nismap kwenye maps:
            mapping = nis.cat(nismap)
            kila k, v kwenye mapping.items():
                ikiwa sio k:
                    endelea
                ikiwa nis.match(k, nismap) != v:
                    self.fail("NIS match failed kila key `%s' kwenye map `%s'" % (k, nismap))
                isipokua:
                    # just test the one key, otherwise this test could take a
                    # very long time
                    done = 1
                    koma
            ikiwa done:
                koma

ikiwa __name__ == '__main__':
    unittest.main()
