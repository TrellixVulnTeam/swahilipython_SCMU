'''
   Test cases kila pyclbr.py
   Nick Mathewson
'''

agiza sys
kutoka textwrap agiza dedent
kutoka types agiza FunctionType, MethodType, BuiltinFunctionType
agiza pyclbr
kutoka unittest agiza TestCase, main as unittest_main
kutoka test.test_importlib agiza util as test_importlib_util


StaticMethodType = type(staticmethod(lambda: Tupu))
ClassMethodType = type(classmethod(lambda c: Tupu))

# Here we test the python kundi browser code.
#
# The main function kwenye this suite, 'testModule', compares the output
# of pyclbr ukijumuisha the introspected members of a module.  Because pyclbr
# ni imperfect (as designed), testModule ni called ukijumuisha a set of
# members to ignore.

kundi PyclbrTest(TestCase):

    eleza assertListEq(self, l1, l2, ignore):
        ''' succeed iff {l1} - {ignore} == {l2} - {ignore} '''
        missing = (set(l1) ^ set(l2)) - set(ignore)
        ikiwa missing:
            andika("l1=%r\nl2=%r\nignore=%r" % (l1, l2, ignore), file=sys.stderr)
            self.fail("%r missing" % missing.pop())

    eleza assertHasattr(self, obj, attr, ignore):
        ''' succeed iff hasattr(obj,attr) ama attr kwenye ignore. '''
        ikiwa attr kwenye ignore: return
        ikiwa sio hasattr(obj, attr): andika("???", attr)
        self.assertKweli(hasattr(obj, attr),
                        'expected hasattr(%r, %r)' % (obj, attr))


    eleza assertHaskey(self, obj, key, ignore):
        ''' succeed iff key kwenye obj ama key kwenye ignore. '''
        ikiwa key kwenye ignore: return
        ikiwa key sio kwenye obj:
            andika("***",key, file=sys.stderr)
        self.assertIn(key, obj)

    eleza assertEqualsOrIgnored(self, a, b, ignore):
        ''' succeed iff a == b ama a kwenye ignore ama b kwenye ignore '''
        ikiwa a sio kwenye ignore na b sio kwenye ignore:
            self.assertEqual(a, b)

    eleza checkModule(self, moduleName, module=Tupu, ignore=()):
        ''' succeed iff pyclbr.readmodule_ex(modulename) corresponds
            to the actual module object, module.  Any identifiers in
            ignore are ignored.   If no module ni provided, the appropriate
            module ni loaded ukijumuisha __import__.'''

        ignore = set(ignore) | set(['object'])

        ikiwa module ni Tupu:
            # Import it.
            # ('<silly>' ni to work around an API silliness kwenye __import__)
            module = __import__(moduleName, globals(), {}, ['<silly>'])

        dict = pyclbr.readmodule_ex(moduleName)

        eleza ismethod(oclass, obj, name):
            classdict = oclass.__dict__
            ikiwa isinstance(obj, MethodType):
                # could be a classmethod
                ikiwa (not isinstance(classdict[name], ClassMethodType) or
                    obj.__self__ ni sio oclass):
                    rudisha Uongo
            elikiwa sio isinstance(obj, FunctionType):
                rudisha Uongo

            objname = obj.__name__
            ikiwa objname.startswith("__") na sio objname.endswith("__"):
                objname = "_%s%s" % (oclass.__name__, objname)
            rudisha objname == name

        # Make sure the toplevel functions na classes are the same.
        kila name, value kwenye dict.items():
            ikiwa name kwenye ignore:
                endelea
            self.assertHasattr(module, name, ignore)
            py_item = getattr(module, name)
            ikiwa isinstance(value, pyclbr.Function):
                self.assertIsInstance(py_item, (FunctionType, BuiltinFunctionType))
                ikiwa py_item.__module__ != moduleName:
                    endelea   # skip functions that came kutoka somewhere else
                self.assertEqual(py_item.__module__, value.module)
            isipokua:
                self.assertIsInstance(py_item, type)
                ikiwa py_item.__module__ != moduleName:
                    endelea   # skip classes that came kutoka somewhere else

                real_bases = [base.__name__ kila base kwenye py_item.__bases__]
                pyclbr_bases = [ getattr(base, 'name', base)
                                 kila base kwenye value.super ]

                jaribu:
                    self.assertListEq(real_bases, pyclbr_bases, ignore)
                tatizo:
                    andika("class=%s" % py_item, file=sys.stderr)
                    raise

                actualMethods = []
                kila m kwenye py_item.__dict__.keys():
                    ikiwa ismethod(py_item, getattr(py_item, m), m):
                        actualMethods.append(m)
                foundMethods = []
                kila m kwenye value.methods.keys():
                    ikiwa m[:2] == '__' na m[-2:] != '__':
                        foundMethods.append('_'+name+m)
                    isipokua:
                        foundMethods.append(m)

                jaribu:
                    self.assertListEq(foundMethods, actualMethods, ignore)
                    self.assertEqual(py_item.__module__, value.module)

                    self.assertEqualsOrIgnored(py_item.__name__, value.name,
                                               ignore)
                    # can't check file ama lineno
                tatizo:
                    andika("class=%s" % py_item, file=sys.stderr)
                    raise

        # Now check kila missing stuff.
        eleza defined_in(item, module):
            ikiwa isinstance(item, type):
                rudisha item.__module__ == module.__name__
            ikiwa isinstance(item, FunctionType):
                rudisha item.__globals__ ni module.__dict__
            rudisha Uongo
        kila name kwenye dir(module):
            item = getattr(module, name)
            ikiwa isinstance(item,  (type, FunctionType)):
                ikiwa defined_in(item, module):
                    self.assertHaskey(dict, name, ignore)

    eleza test_easy(self):
        self.checkModule('pyclbr')
        # XXX: Metaclasses are sio supported
        # self.checkModule('ast')
        self.checkModule('doctest', ignore=("TestResults", "_SpoofOut",
                                            "DocTestCase", '_DocTestSuite'))
        self.checkModule('difflib', ignore=("Match",))

    eleza test_decorators(self):
        # XXX: See comment kwenye pyclbr_input.py kila a test that would fail
        #      ikiwa it were sio commented out.
        #
        self.checkModule('test.pyclbr_input', ignore=['om'])

    eleza test_nested(self):
        mb = pyclbr
        # Set arguments kila descriptor creation na _creat_tree call.
        m, p, f, t, i = 'test', '', 'test.py', {}, Tupu
        source = dedent("""\
        eleza f0:
            eleza f1(a,b,c):
                eleza f2(a=1, b=2, c=3): pass
                    rudisha f1(a,b,d)
            kundi c1: pass
        kundi C0:
            "Test class."
            eleza F1():
                "Method."
                rudisha 'return'
            kundi C1():
                kundi C2:
                    "Class nested within nested class."
                    eleza F3(): rudisha 1+1

        """)
        actual = mb._create_tree(m, p, f, source, t, i)

        # Create descriptors, linked together, na expected dict.
        f0 = mb.Function(m, 'f0', f, 1)
        f1 = mb._nest_function(f0, 'f1', 2)
        f2 = mb._nest_function(f1, 'f2', 3)
        c1 = mb._nest_class(f0, 'c1', 5)
        C0 = mb.Class(m, 'C0', Tupu, f, 6)
        F1 = mb._nest_function(C0, 'F1', 8)
        C1 = mb._nest_class(C0, 'C1', 11)
        C2 = mb._nest_class(C1, 'C2', 12)
        F3 = mb._nest_function(C2, 'F3', 14)
        expected = {'f0':f0, 'C0':C0}

        eleza compare(parent1, children1, parent2, children2):
            """Return equality of tree pairs.

            Each parent,children pair define a tree.  The parents are
            assumed equal.  Comparing the children dictionaries as such
            does sio work due to comparison by identity na double
            linkage.  We separate comparing string na number attributes
            kutoka comparing the children of input children.
            """
            self.assertEqual(children1.keys(), children2.keys())
            kila ob kwenye children1.values():
                self.assertIs(ob.parent, parent1)
            kila ob kwenye children2.values():
                self.assertIs(ob.parent, parent2)
            kila key kwenye children1.keys():
                o1, o2 = children1[key], children2[key]
                t1 = type(o1), o1.name, o1.file, o1.module, o1.lineno
                t2 = type(o2), o2.name, o2.file, o2.module, o2.lineno
                self.assertEqual(t1, t2)
                ikiwa type(o1) ni mb.Class:
                    self.assertEqual(o1.methods, o2.methods)
                # Skip superclasses kila now as sio part of example
                compare(o1, o1.children, o2, o2.children)

        compare(Tupu, actual, Tupu, expected)

    eleza test_others(self):
        cm = self.checkModule

        # These were once about the 10 longest modules
        cm('random', ignore=('Random',))  # kutoka _random agiza Random as CoreGenerator
        cm('cgi', ignore=('log',))      # set ukijumuisha = kwenye module
        cm('pickle', ignore=('partial', 'PickleBuffer'))
        # TODO(briancurtin): openfp ni deprecated as of 3.7.
        # Update this once it has been removed.
        cm('aifc', ignore=('openfp', '_aifc_params'))  # set ukijumuisha = kwenye module
        cm('sre_parse', ignore=('dump', 'groups', 'pos')) # kutoka sre_constants agiza *; property
        cm('pdb')
        cm('pydoc', ignore=('input', 'output',)) # properties

        # Tests kila modules inside packages
        cm('email.parser')
        cm('test.test_pyclbr')


kundi ReadmoduleTests(TestCase):

    eleza setUp(self):
        self._modules = pyclbr._modules.copy()

    eleza tearDown(self):
        pyclbr._modules = self._modules


    eleza test_dotted_name_not_a_package(self):
        # test ImportError ni raised when the first part of a dotted name is
        # sio a package.
        #
        # Issue #14798.
        self.assertRaises(ImportError, pyclbr.readmodule_ex, 'asyncore.foo')

    eleza test_module_has_no_spec(self):
        module_name = "doesnotexist"
        assert module_name sio kwenye pyclbr._modules
        ukijumuisha test_importlib_util.uncache(module_name):
            ukijumuisha self.assertRaises(ModuleNotFoundError):
                pyclbr.readmodule_ex(module_name)


ikiwa __name__ == "__main__":
    unittest_main()
