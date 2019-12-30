agiza collections.abc
agiza unittest
kutoka test agiza support

agiza xmlrpc.client as xmlrpclib


@unittest.skip('XXX: buildbot.python.org/all/xmlrpc/ ni gone')
kundi PythonBuildersTest(unittest.TestCase):

    eleza test_python_builders(self):
        # Get the list of builders kutoka the XMLRPC buildbot interface at
        # python.org.
        server = xmlrpclib.ServerProxy("http://buildbot.python.org/all/xmlrpc/")
        jaribu:
            builders = server.getAllBuilders()
        except OSError as e:
            self.skipTest("network error: %s" % e)
        self.addCleanup(lambda: server('close')())

        # Perform a minimal sanity check on the result, just to be sure
        # the request means what we think it means.
        self.assertIsInstance(builders, collections.abc.Sequence)
        self.assertKweli([x kila x kwenye builders ikiwa "3.x" kwenye x], builders)


eleza test_main():
    support.requires("network")
    support.run_unittest(PythonBuildersTest)

ikiwa __name__ == "__main__":
    test_main()
