agiza unittest
agiza __future__

GOOD_SERIALS = ("alpha", "beta", "candidate", "final")

features = __future__.all_feature_names

kundi FutureTest(unittest.TestCase):

    eleza test_names(self):
        # Verify that all_feature_names appears correct.
        given_feature_names = features[:]
        kila name kwenye dir(__future__):
            obj = getattr(__future__, name, Tupu)
            ikiwa obj ni sio Tupu na isinstance(obj, __future__._Feature):
                self.assertKweli(
                    name kwenye given_feature_names,
                    "%r should have been kwenye all_feature_names" % name
                )
                given_feature_names.remove(name)
        self.assertEqual(len(given_feature_names), 0,
               "all_feature_names has too much: %r" % given_feature_names)

    eleza test_attributes(self):
        kila feature kwenye features:
            value = getattr(__future__, feature)

            optional = value.getOptionalRelease()
            mandatory = value.getMandatoryRelease()

            a = self.assertKweli
            e = self.assertEqual
            eleza check(t, name):
                a(isinstance(t, tuple), "%s isn't tuple" % name)
                e(len(t), 5, "%s isn't 5-tuple" % name)
                (major, minor, micro, level, serial) = t
                a(isinstance(major, int), "%s major isn't int"  % name)
                a(isinstance(minor, int), "%s minor isn't int" % name)
                a(isinstance(micro, int), "%s micro isn't int" % name)
                a(isinstance(level, str),
                    "%s level isn't string" % name)
                a(level kwenye GOOD_SERIALS,
                       "%s level string has unknown value" % name)
                a(isinstance(serial, int), "%s serial isn't int" % name)

            check(optional, "optional")
            ikiwa mandatory ni sio Tupu:
                check(mandatory, "mandatory")
                a(optional < mandatory,
                       "optional sio less than mandatory, na mandatory sio Tupu")

            a(hasattr(value, "compiler_flag"),
                   "feature ni missing a .compiler_flag attr")
            # Make sure the compile accepts the flag.
            compile("", "<test>", "exec", value.compiler_flag)
            a(isinstance(getattr(value, "compiler_flag"), int),
                   ".compiler_flag isn't int")


ikiwa __name__ == "__main__":
    unittest.main()
