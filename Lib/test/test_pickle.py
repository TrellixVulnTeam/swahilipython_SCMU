kutoka _compat_pickle agiza (IMPORT_MAPPING, REVERSE_IMPORT_MAPPING,
                            NAME_MAPPING, REVERSE_NAME_MAPPING)
agiza builtins
agiza pickle
agiza io
agiza collections
agiza struct
agiza sys
agiza weakref

agiza unittest
kutoka test agiza support

kutoka test.pickletester agiza AbstractHookTests
kutoka test.pickletester agiza AbstractUnpickleTests
kutoka test.pickletester agiza AbstractPickleTests
kutoka test.pickletester agiza AbstractPickleModuleTests
kutoka test.pickletester agiza AbstractPersistentPicklerTests
kutoka test.pickletester agiza AbstractIdentityPersistentPicklerTests
kutoka test.pickletester agiza AbstractPicklerUnpicklerObjectTests
kutoka test.pickletester agiza AbstractDispatchTableTests
kutoka test.pickletester agiza AbstractCustomPicklerClass
kutoka test.pickletester agiza BigmemPickleTests

jaribu:
    agiza _pickle
    has_c_implementation = Kweli
tatizo ImportError:
    has_c_implementation = Uongo


kundi PyPickleTests(AbstractPickleModuleTests):
    dump = staticmethod(pickle._dump)
    dumps = staticmethod(pickle._dumps)
    load = staticmethod(pickle._load)
    loads = staticmethod(pickle._loads)
    Pickler = pickle._Pickler
    Unpickler = pickle._Unpickler


kundi PyUnpicklerTests(AbstractUnpickleTests):

    unpickler = pickle._Unpickler
    bad_stack_errors = (IndexError,)
    truncated_errors = (pickle.UnpicklingError, EOFError,
                        AttributeError, ValueError,
                        struct.error, IndexError, ImportError)

    eleza loads(self, buf, **kwds):
        f = io.BytesIO(buf)
        u = self.unpickler(f, **kwds)
        rudisha u.load()


kundi PyPicklerTests(AbstractPickleTests):

    pickler = pickle._Pickler
    unpickler = pickle._Unpickler

    eleza dumps(self, arg, proto=Tupu, **kwargs):
        f = io.BytesIO()
        p = self.pickler(f, proto, **kwargs)
        p.dump(arg)
        f.seek(0)
        rudisha bytes(f.read())

    eleza loads(self, buf, **kwds):
        f = io.BytesIO(buf)
        u = self.unpickler(f, **kwds)
        rudisha u.load()


kundi InMemoryPickleTests(AbstractPickleTests, AbstractUnpickleTests,
                          BigmemPickleTests):

    bad_stack_errors = (pickle.UnpicklingError, IndexError)
    truncated_errors = (pickle.UnpicklingError, EOFError,
                        AttributeError, ValueError,
                        struct.error, IndexError, ImportError)

    eleza dumps(self, arg, protocol=Tupu, **kwargs):
        rudisha pickle.dumps(arg, protocol, **kwargs)

    eleza loads(self, buf, **kwds):
        rudisha pickle.loads(buf, **kwds)

    test_framed_write_sizes_with_delayed_writer = Tupu


kundi PersistentPicklerUnpicklerMixin(object):

    eleza dumps(self, arg, proto=Tupu):
        kundi PersPickler(self.pickler):
            eleza persistent_id(subself, obj):
                rudisha self.persistent_id(obj)
        f = io.BytesIO()
        p = PersPickler(f, proto)
        p.dump(arg)
        rudisha f.getvalue()

    eleza loads(self, buf, **kwds):
        kundi PersUnpickler(self.unpickler):
            eleza persistent_load(subself, obj):
                rudisha self.persistent_load(obj)
        f = io.BytesIO(buf)
        u = PersUnpickler(f, **kwds)
        rudisha u.load()


kundi PyPersPicklerTests(AbstractPersistentPicklerTests,
                         PersistentPicklerUnpicklerMixin):

    pickler = pickle._Pickler
    unpickler = pickle._Unpickler


kundi PyIdPersPicklerTests(AbstractIdentityPersistentPicklerTests,
                           PersistentPicklerUnpicklerMixin):

    pickler = pickle._Pickler
    unpickler = pickle._Unpickler

    @support.cpython_only
    eleza test_pickler_reference_cycle(self):
        eleza check(Pickler):
            kila proto kwenye range(pickle.HIGHEST_PROTOCOL + 1):
                f = io.BytesIO()
                pickler = Pickler(f, proto)
                pickler.dump('abc')
                self.assertEqual(self.loads(f.getvalue()), 'abc')
            pickler = Pickler(io.BytesIO())
            self.assertEqual(pickler.persistent_id('def'), 'def')
            r = weakref.ref(pickler)
            toa pickler
            self.assertIsTupu(r())

        kundi PersPickler(self.pickler):
            eleza persistent_id(subself, obj):
                rudisha obj
        check(PersPickler)

        kundi PersPickler(self.pickler):
            @classmethod
            eleza persistent_id(cls, obj):
                rudisha obj
        check(PersPickler)

        kundi PersPickler(self.pickler):
            @staticmethod
            eleza persistent_id(obj):
                rudisha obj
        check(PersPickler)

    @support.cpython_only
    eleza test_unpickler_reference_cycle(self):
        eleza check(Unpickler):
            kila proto kwenye range(pickle.HIGHEST_PROTOCOL + 1):
                unpickler = Unpickler(io.BytesIO(self.dumps('abc', proto)))
                self.assertEqual(unpickler.load(), 'abc')
            unpickler = Unpickler(io.BytesIO())
            self.assertEqual(unpickler.persistent_load('def'), 'def')
            r = weakref.ref(unpickler)
            toa unpickler
            self.assertIsTupu(r())

        kundi PersUnpickler(self.unpickler):
            eleza persistent_load(subself, pid):
                rudisha pid
        check(PersUnpickler)

        kundi PersUnpickler(self.unpickler):
            @classmethod
            eleza persistent_load(cls, pid):
                rudisha pid
        check(PersUnpickler)

        kundi PersUnpickler(self.unpickler):
            @staticmethod
            eleza persistent_load(pid):
                rudisha pid
        check(PersUnpickler)


kundi PyPicklerUnpicklerObjectTests(AbstractPicklerUnpicklerObjectTests):

    pickler_kundi = pickle._Pickler
    unpickler_kundi = pickle._Unpickler


kundi PyDispatchTableTests(AbstractDispatchTableTests):

    pickler_kundi = pickle._Pickler

    eleza get_dispatch_table(self):
        rudisha pickle.dispatch_table.copy()


kundi PyChainDispatchTableTests(AbstractDispatchTableTests):

    pickler_kundi = pickle._Pickler

    eleza get_dispatch_table(self):
        rudisha collections.ChainMap({}, pickle.dispatch_table)


kundi PyPicklerHookTests(AbstractHookTests):
    kundi CustomPyPicklerClass(pickle._Pickler,
                               AbstractCustomPicklerClass):
        pita
    pickler_kundi = CustomPyPicklerClass


ikiwa has_c_implementation:
    kundi CPickleTests(AbstractPickleModuleTests):
        kutoka _pickle agiza dump, dumps, load, loads, Pickler, Unpickler

    kundi CUnpicklerTests(PyUnpicklerTests):
        unpickler = _pickle.Unpickler
        bad_stack_errors = (pickle.UnpicklingError,)
        truncated_errors = (pickle.UnpicklingError,)

    kundi CPicklerTests(PyPicklerTests):
        pickler = _pickle.Pickler
        unpickler = _pickle.Unpickler

    kundi CPersPicklerTests(PyPersPicklerTests):
        pickler = _pickle.Pickler
        unpickler = _pickle.Unpickler

    kundi CIdPersPicklerTests(PyIdPersPicklerTests):
        pickler = _pickle.Pickler
        unpickler = _pickle.Unpickler

    kundi CDumpPickle_LoadPickle(PyPicklerTests):
        pickler = _pickle.Pickler
        unpickler = pickle._Unpickler

    kundi DumpPickle_CLoadPickle(PyPicklerTests):
        pickler = pickle._Pickler
        unpickler = _pickle.Unpickler

    kundi CPicklerUnpicklerObjectTests(AbstractPicklerUnpicklerObjectTests):
        pickler_kundi = _pickle.Pickler
        unpickler_kundi = _pickle.Unpickler

        eleza test_issue18339(self):
            unpickler = self.unpickler_class(io.BytesIO())
            ukijumuisha self.assertRaises(TypeError):
                unpickler.memo = object
            # used to cause a segfault
            ukijumuisha self.assertRaises(ValueError):
                unpickler.memo = {-1: Tupu}
            unpickler.memo = {1: Tupu}

    kundi CDispatchTableTests(AbstractDispatchTableTests):
        pickler_kundi = pickle.Pickler
        eleza get_dispatch_table(self):
            rudisha pickle.dispatch_table.copy()

    kundi CChainDispatchTableTests(AbstractDispatchTableTests):
        pickler_kundi = pickle.Pickler
        eleza get_dispatch_table(self):
            rudisha collections.ChainMap({}, pickle.dispatch_table)

    kundi CPicklerHookTests(AbstractHookTests):
        kundi CustomCPicklerClass(_pickle.Pickler, AbstractCustomPicklerClass):
            pita
        pickler_kundi = CustomCPicklerClass

    @support.cpython_only
    kundi SizeofTests(unittest.TestCase):
        check_sizeof = support.check_sizeof

        eleza test_pickler(self):
            basesize = support.calcobjsize('7P2n3i2n3i2P')
            p = _pickle.Pickler(io.BytesIO())
            self.assertEqual(object.__sizeof__(p), basesize)
            MT_size = struct.calcsize('3nP0n')
            ME_size = struct.calcsize('Pn0P')
            check = self.check_sizeof
            check(p, basesize +
                MT_size + 8 * ME_size +  # Minimal memo table size.
                sys.getsizeof(b'x'*4096))  # Minimal write buffer size.
            kila i kwenye range(6):
                p.dump(chr(i))
            check(p, basesize +
                MT_size + 32 * ME_size +  # Size of memo table required to
                                          # save references to 6 objects.
                0)  # Write buffer ni cleared after every dump().

        eleza test_unpickler(self):
            basesize = support.calcobjsize('2P2n2P 2P2n2i5P 2P3n8P2n2i')
            unpickler = _pickle.Unpickler
            P = struct.calcsize('P')  # Size of memo table entry.
            n = struct.calcsize('n')  # Size of mark table entry.
            check = self.check_sizeof
            kila encoding kwenye 'ASCII', 'UTF-16', 'latin-1':
                kila errors kwenye 'strict', 'replace':
                    u = unpickler(io.BytesIO(),
                                  encoding=encoding, errors=errors)
                    self.assertEqual(object.__sizeof__(u), basesize)
                    check(u, basesize +
                             32 * P +  # Minimal memo table size.
                             len(encoding) + 1 + len(errors) + 1)

            stdsize = basesize + len('ASCII') + 1 + len('strict') + 1
            eleza check_unpickler(data, memo_size, marks_size):
                dump = pickle.dumps(data)
                u = unpickler(io.BytesIO(dump),
                              encoding='ASCII', errors='strict')
                u.load()
                check(u, stdsize + memo_size * P + marks_size * n)

            check_unpickler(0, 32, 0)
            # 20 ni minimal non-empty mark stack size.
            check_unpickler([0] * 100, 32, 20)
            # 128 ni memo table size required to save references to 100 objects.
            check_unpickler([chr(i) kila i kwenye range(100)], 128, 20)
            eleza recurse(deep):
                data = 0
                kila i kwenye range(deep):
                    data = [data, data]
                rudisha data
            check_unpickler(recurse(0), 32, 0)
            check_unpickler(recurse(1), 32, 20)
            check_unpickler(recurse(20), 32, 20)
            check_unpickler(recurse(50), 64, 60)
            check_unpickler(recurse(100), 128, 140)

            u = unpickler(io.BytesIO(pickle.dumps('a', 0)),
                          encoding='ASCII', errors='strict')
            u.load()
            check(u, stdsize + 32 * P + 2 + 1)


ALT_IMPORT_MAPPING = {
    ('_elementtree', 'xml.etree.ElementTree'),
    ('cPickle', 'pickle'),
    ('StringIO', 'io'),
    ('cStringIO', 'io'),
}

ALT_NAME_MAPPING = {
    ('__builtin__', 'basestring', 'builtins', 'str'),
    ('exceptions', 'StandardError', 'builtins', 'Exception'),
    ('UserDict', 'UserDict', 'collections', 'UserDict'),
    ('socket', '_socketobject', 'socket', 'SocketType'),
}

eleza mapping(module, name):
    ikiwa (module, name) kwenye NAME_MAPPING:
        module, name = NAME_MAPPING[(module, name)]
    lasivyo module kwenye IMPORT_MAPPING:
        module = IMPORT_MAPPING[module]
    rudisha module, name

eleza reverse_mapping(module, name):
    ikiwa (module, name) kwenye REVERSE_NAME_MAPPING:
        module, name = REVERSE_NAME_MAPPING[(module, name)]
    lasivyo module kwenye REVERSE_IMPORT_MAPPING:
        module = REVERSE_IMPORT_MAPPING[module]
    rudisha module, name

eleza getmodule(module):
    jaribu:
        rudisha sys.modules[module]
    tatizo KeyError:
        jaribu:
            __import__(module)
        tatizo AttributeError kama exc:
            ikiwa support.verbose:
                andika("Can't agiza module %r: %s" % (module, exc))
            ashiria ImportError
        tatizo ImportError kama exc:
            ikiwa support.verbose:
                andika(exc)
            ashiria
        rudisha sys.modules[module]

eleza getattribute(module, name):
    obj = getmodule(module)
    kila n kwenye name.split('.'):
        obj = getattr(obj, n)
    rudisha obj

eleza get_exceptions(mod):
    kila name kwenye dir(mod):
        attr = getattr(mod, name)
        ikiwa isinstance(attr, type) na issubclass(attr, BaseException):
            tuma name, attr

kundi CompatPickleTests(unittest.TestCase):
    eleza test_agiza(self):
        modules = set(IMPORT_MAPPING.values())
        modules |= set(REVERSE_IMPORT_MAPPING)
        modules |= {module kila module, name kwenye REVERSE_NAME_MAPPING}
        modules |= {module kila module, name kwenye NAME_MAPPING.values()}
        kila module kwenye modules:
            jaribu:
                getmodule(module)
            tatizo ImportError:
                pita

    eleza test_import_mapping(self):
        kila module3, module2 kwenye REVERSE_IMPORT_MAPPING.items():
            ukijumuisha self.subTest((module3, module2)):
                jaribu:
                    getmodule(module3)
                tatizo ImportError:
                    pita
                ikiwa module3[:1] != '_':
                    self.assertIn(module2, IMPORT_MAPPING)
                    self.assertEqual(IMPORT_MAPPING[module2], module3)

    eleza test_name_mapping(self):
        kila (module3, name3), (module2, name2) kwenye REVERSE_NAME_MAPPING.items():
            ukijumuisha self.subTest(((module3, name3), (module2, name2))):
                ikiwa (module2, name2) == ('exceptions', 'OSError'):
                    attr = getattribute(module3, name3)
                    self.assertKweli(issubclass(attr, OSError))
                lasivyo (module2, name2) == ('exceptions', 'ImportError'):
                    attr = getattribute(module3, name3)
                    self.assertKweli(issubclass(attr, ImportError))
                isipokua:
                    module, name = mapping(module2, name2)
                    ikiwa module3[:1] != '_':
                        self.assertEqual((module, name), (module3, name3))
                    jaribu:
                        attr = getattribute(module3, name3)
                    tatizo ImportError:
                        pita
                    isipokua:
                        self.assertEqual(getattribute(module, name), attr)

    eleza test_reverse_import_mapping(self):
        kila module2, module3 kwenye IMPORT_MAPPING.items():
            ukijumuisha self.subTest((module2, module3)):
                jaribu:
                    getmodule(module3)
                tatizo ImportError kama exc:
                    ikiwa support.verbose:
                        andika(exc)
                ikiwa ((module2, module3) haiko kwenye ALT_IMPORT_MAPPING and
                    REVERSE_IMPORT_MAPPING.get(module3, Tupu) != module2):
                    kila (m3, n3), (m2, n2) kwenye REVERSE_NAME_MAPPING.items():
                        ikiwa (module3, module2) == (m3, m2):
                            koma
                    isipokua:
                        self.fail('No reverse mapping kutoka %r to %r' %
                                  (module3, module2))
                module = REVERSE_IMPORT_MAPPING.get(module3, module3)
                module = IMPORT_MAPPING.get(module, module)
                self.assertEqual(module, module3)

    eleza test_reverse_name_mapping(self):
        kila (module2, name2), (module3, name3) kwenye NAME_MAPPING.items():
            ukijumuisha self.subTest(((module2, name2), (module3, name3))):
                jaribu:
                    attr = getattribute(module3, name3)
                tatizo ImportError:
                    pita
                module, name = reverse_mapping(module3, name3)
                ikiwa (module2, name2, module3, name3) haiko kwenye ALT_NAME_MAPPING:
                    self.assertEqual((module, name), (module2, name2))
                module, name = mapping(module, name)
                self.assertEqual((module, name), (module3, name3))

    eleza test_exceptions(self):
        self.assertEqual(mapping('exceptions', 'StandardError'),
                         ('builtins', 'Exception'))
        self.assertEqual(mapping('exceptions', 'Exception'),
                         ('builtins', 'Exception'))
        self.assertEqual(reverse_mapping('builtins', 'Exception'),
                         ('exceptions', 'Exception'))
        self.assertEqual(mapping('exceptions', 'OSError'),
                         ('builtins', 'OSError'))
        self.assertEqual(reverse_mapping('builtins', 'OSError'),
                         ('exceptions', 'OSError'))

        kila name, exc kwenye get_exceptions(builtins):
            ukijumuisha self.subTest(name):
                ikiwa exc kwenye (BlockingIOError,
                           ResourceWarning,
                           StopAsyncIteration,
                           RecursionError):
                    endelea
                ikiwa exc ni sio OSError na issubclass(exc, OSError):
                    self.assertEqual(reverse_mapping('builtins', name),
                                     ('exceptions', 'OSError'))
                lasivyo exc ni sio ImportError na issubclass(exc, ImportError):
                    self.assertEqual(reverse_mapping('builtins', name),
                                     ('exceptions', 'ImportError'))
                    self.assertEqual(mapping('exceptions', name),
                                     ('exceptions', name))
                isipokua:
                    self.assertEqual(reverse_mapping('builtins', name),
                                     ('exceptions', name))
                    self.assertEqual(mapping('exceptions', name),
                                     ('builtins', name))

    eleza test_multiprocessing_exceptions(self):
        module = support.import_module('multiprocessing.context')
        kila name, exc kwenye get_exceptions(module):
            ukijumuisha self.subTest(name):
                self.assertEqual(reverse_mapping('multiprocessing.context', name),
                                 ('multiprocessing', name))
                self.assertEqual(mapping('multiprocessing', name),
                                 ('multiprocessing.context', name))


eleza test_main():
    tests = [PyPickleTests, PyUnpicklerTests, PyPicklerTests,
             PyPersPicklerTests, PyIdPersPicklerTests,
             PyDispatchTableTests, PyChainDispatchTableTests,
             CompatPickleTests, PyPicklerHookTests]
    ikiwa has_c_implementation:
        tests.extend([CPickleTests, CUnpicklerTests, CPicklerTests,
                      CPersPicklerTests, CIdPersPicklerTests,
                      CDumpPickle_LoadPickle, DumpPickle_CLoadPickle,
                      PyPicklerUnpicklerObjectTests,
                      CPicklerUnpicklerObjectTests,
                      CDispatchTableTests, CChainDispatchTableTests,
                      CPicklerHookTests,
                      InMemoryPickleTests, SizeofTests])
    support.run_unittest(*tests)
    support.run_doctest(pickle)

ikiwa __name__ == "__main__":
    test_main()
