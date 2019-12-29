agiza unittest
agiza sys

kutoka test.support agiza import_fresh_module, run_unittest

TESTS = 'test.datetimetester'

jaribu:
    pure_tests = import_fresh_module(TESTS, fresh=['datetime', '_strptime'],
                                     blocked=['_datetime'])
    fast_tests = import_fresh_module(TESTS, fresh=['datetime',
                                                   '_datetime', '_strptime'])
mwishowe:
    # XXX: import_fresh_module() ni supposed to leave sys.module cache untouched,
    # XXX: but it does not, so we have to cleanup ourselves.
    kila modname kwenye ['datetime', '_datetime', '_strptime']:
        sys.modules.pop(modname, Tupu)
test_modules = [pure_tests, fast_tests]
test_suffixes = ["_Pure", "_Fast"]
# XXX(gb) First run all the _Pure tests, then all the _Fast tests.  You might
# sio believe this, but kwenye spite of all the sys.modules trickery running a _Pure
# test last will leave a mix of pure na native datetime stuff lying around.
all_test_classes = []

kila module, suffix kwenye zip(test_modules, test_suffixes):
    test_classes = []
    kila name, cls kwenye module.__dict__.items():
        ikiwa sio isinstance(cls, type):
            endelea
        ikiwa issubclass(cls, unittest.TestCase):
            test_classes.append(cls)
        elikiwa issubclass(cls, unittest.TestSuite):
            suit = cls()
            test_classes.extend(type(test) kila test kwenye suit)
    test_classes = sorted(set(test_classes), key=lambda cls: cls.__qualname__)
    kila cls kwenye test_classes:
        cls.__name__ += suffix
        cls.__qualname__ += suffix
        @classmethod
        eleza setUpClass(cls_, module=module):
            cls_._save_sys_modules = sys.modules.copy()
            sys.modules[TESTS] = module
            sys.modules['datetime'] = module.datetime_module
            sys.modules['_strptime'] = module._strptime
        @classmethod
        eleza tearDownClass(cls_):
            sys.modules.clear()
            sys.modules.update(cls_._save_sys_modules)
        cls.setUpClass = setUpClass
        cls.tearDownClass = tearDownClass
    all_test_classes.extend(test_classes)

eleza test_main():
    run_unittest(*all_test_classes)

ikiwa __name__ == "__main__":
    test_main()
