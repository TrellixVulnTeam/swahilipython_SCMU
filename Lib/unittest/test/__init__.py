agiza os
agiza sys
agiza unittest


here = os.path.dirname(__file__)
loader = unittest.defaultTestLoader

eleza suite():
    suite = unittest.TestSuite()
    kila fn kwenye os.listdir(here):
        ikiwa fn.startswith("test") na fn.endswith(".py"):
            modname = "unittest.test." + fn[:-3]
            __import__(modname)
            module = sys.modules[modname]
            suite.addTest(loader.loadTestsFromModule(module))
    suite.addTest(loader.loadTestsFromName('unittest.test.testmock'))
    rudisha suite


ikiwa __name__ == "__main__":
    unittest.main(defaultTest="suite")
