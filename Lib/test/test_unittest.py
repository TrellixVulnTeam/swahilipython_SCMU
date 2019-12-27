agiza unittest.test

kutoka test agiza support


eleza test_main():
    # used by regrtest
    support.run_unittest(unittest.test.suite())
    support.reap_children()

eleza load_tests(*_):
    # used by unittest
    rudisha unittest.test.suite()

ikiwa __name__ == "__main__":
    test_main()
