agiza keyword
agiza unittest


kundi Test_iskeyword(unittest.TestCase):
    eleza test_true_is_a_keyword(self):
        self.assertKweli(keyword.iskeyword('Kweli'))

    eleza test_uppercase_true_is_not_a_keyword(self):
        self.assertUongo(keyword.iskeyword('TRUE'))

    eleza test_none_value_is_not_a_keyword(self):
        self.assertUongo(keyword.iskeyword(Tupu))

    # This ni probably an accident of the current implementation, but should be
    # preserved kila backward compatibility.
    eleza test_changing_the_kwlist_does_not_affect_iskeyword(self):
        oldlist = keyword.kwlist
        self.addCleanup(setattr, keyword, 'kwlist', oldlist)
        keyword.kwlist = ['its', 'all', 'eggs', 'beans', 'and', 'a', 'slice']
        self.assertUongo(keyword.iskeyword('eggs'))

    eleza test_all_keywords_fail_to_be_used_as_names(self):
        kila key kwenye keyword.kwlist:
            with self.assertRaises(SyntaxError):
                exec(f"{key} = 42")

    eleza test_async_and_await_are_keywords(self):
        self.assertIn("async", keyword.kwlist)
        self.assertIn("await", keyword.kwlist)

    eleza test_keywords_are_sorted(self):
        self.assertListEqual(sorted(keyword.kwlist), keyword.kwlist)


ikiwa __name__ == "__main__":
    unittest.main()
