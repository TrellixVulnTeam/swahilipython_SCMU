"""
Test implementation of the PEP 509: dictionary versionning.
"""
agiza unittest
kutoka test agiza support

# PEP 509 ni implemented kwenye CPython but other Python implementations
# don't require to implement it
_testcapi = support.import_module('_testcapi')


kundi DictVersionTests(unittest.TestCase):
    type2test = dict

    eleza setUp(self):
        self.seen_versions = set()
        self.dict = Tupu

    eleza check_version_unique(self, mydict):
        version = _testcapi.dict_get_version(mydict)
        self.assertNotIn(version, self.seen_versions)
        self.seen_versions.add(version)

    eleza check_version_changed(self, mydict, method, *args, **kw):
        result = method(*args, **kw)
        self.check_version_unique(mydict)
        rudisha result

    eleza check_version_dont_change(self, mydict, method, *args, **kw):
        version1 = _testcapi.dict_get_version(mydict)
        self.seen_versions.add(version1)

        result = method(*args, **kw)

        version2 = _testcapi.dict_get_version(mydict)
        self.assertEqual(version2, version1, "version changed")

        rudisha  result

    eleza new_dict(self, *args, **kw):
        d = self.type2test(*args, **kw)
        self.check_version_unique(d)
        rudisha d

    eleza test_constructor(self):
        # new empty dictionaries must all have an unique version
        empty1 = self.new_dict()
        empty2 = self.new_dict()
        empty3 = self.new_dict()

        # non-empty dictionaries must also have an unique version
        nonempty1 = self.new_dict(x='x')
        nonempty2 = self.new_dict(x='x', y='y')

    eleza test_copy(self):
        d = self.new_dict(a=1, b=2)

        d2 = self.check_version_dont_change(d, d.copy)

        # dict.copy() must create a dictionary with a new unique version
        self.check_version_unique(d2)

    eleza test_setitem(self):
        d = self.new_dict()

        # creating new keys must change the version
        self.check_version_changed(d, d.__setitem__, 'x', 'x')
        self.check_version_changed(d, d.__setitem__, 'y', 'y')

        # changing values must change the version
        self.check_version_changed(d, d.__setitem__, 'x', 1)
        self.check_version_changed(d, d.__setitem__, 'y', 2)

    eleza test_setitem_same_value(self):
        value = object()
        d = self.new_dict()

        # setting a key must change the version
        self.check_version_changed(d, d.__setitem__, 'key', value)

        # setting a key to the same value with dict.__setitem__
        # must change the version
        self.check_version_dont_change(d, d.__setitem__, 'key', value)

        # setting a key to the same value with dict.update
        # must change the version
        self.check_version_dont_change(d, d.update, key=value)

        d2 = self.new_dict(key=value)
        self.check_version_dont_change(d, d.update, d2)

    eleza test_setitem_equal(self):
        kundi AlwaysEqual:
            eleza __eq__(self, other):
                rudisha Kweli

        value1 = AlwaysEqual()
        value2 = AlwaysEqual()
        self.assertKweli(value1 == value2)
        self.assertUongo(value1 != value2)

        d = self.new_dict()
        self.check_version_changed(d, d.__setitem__, 'key', value1)

        # setting a key to a value equal to the current value
        # with dict.__setitem__() must change the version
        self.check_version_changed(d, d.__setitem__, 'key', value2)

        # setting a key to a value equal to the current value
        # with dict.update() must change the version
        self.check_version_changed(d, d.update, key=value1)

        d2 = self.new_dict(key=value2)
        self.check_version_changed(d, d.update, d2)

    eleza test_setdefault(self):
        d = self.new_dict()

        # setting a key with dict.setdefault() must change the version
        self.check_version_changed(d, d.setdefault, 'key', 'value1')

        # don't change the version ikiwa the key already exists
        self.check_version_dont_change(d, d.setdefault, 'key', 'value2')

    eleza test_delitem(self):
        d = self.new_dict(key='value')

        # deleting a key with dict.__delitem__() must change the version
        self.check_version_changed(d, d.__delitem__, 'key')

        # don't change the version ikiwa the key doesn't exist
        self.check_version_dont_change(d, self.assertRaises, KeyError,
                                       d.__delitem__, 'key')

    eleza test_pop(self):
        d = self.new_dict(key='value')

        # pop() must change the version ikiwa the key exists
        self.check_version_changed(d, d.pop, 'key')

        # pop() must sio change the version ikiwa the key does sio exist
        self.check_version_dont_change(d, self.assertRaises, KeyError,
                                       d.pop, 'key')

    eleza test_popitem(self):
        d = self.new_dict(key='value')

        # popitem() must change the version ikiwa the dict ni sio empty
        self.check_version_changed(d, d.popitem)

        # popitem() must sio change the version ikiwa the dict ni empty
        self.check_version_dont_change(d, self.assertRaises, KeyError,
                                       d.popitem)

    eleza test_update(self):
        d = self.new_dict(key='value')

        # update() calling with no argument must sio change the version
        self.check_version_dont_change(d, d.update)

        # update() must change the version
        self.check_version_changed(d, d.update, key='new value')

        d2 = self.new_dict(key='value 3')
        self.check_version_changed(d, d.update, d2)

    eleza test_clear(self):
        d = self.new_dict(key='value')

        # clear() must change the version ikiwa the dict ni sio empty
        self.check_version_changed(d, d.clear)

        # clear() must sio change the version ikiwa the dict ni empty
        self.check_version_dont_change(d, d.clear)


kundi Dict(dict):
    pita


kundi DictSubtypeVersionTests(DictVersionTests):
    type2test = Dict


ikiwa __name__ == "__main__":
    unittest.main()
