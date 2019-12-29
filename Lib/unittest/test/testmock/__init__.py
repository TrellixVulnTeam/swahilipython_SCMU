agiza os
agiza sys
agiza unittest


here = os.path.dirname(__file__)
loader = unittest.defaultTestLoader

eleza load_tests(*args):
    suite = unittest.TestSuite()
    kila fn kwenye os.listdir(here):
        ikiwa fn.startswith("test") na fn.endswith(".py"):
            modname = "unittest.test.testmock." + fn[:-3]
            __import__(modname)
            module = sys.modules[modname]
            suite.addTest(loader.loadTestsFromModule(module))
    rudisha suite
