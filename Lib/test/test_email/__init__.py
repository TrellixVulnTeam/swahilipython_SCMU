agiza os
agiza unittest
agiza collections
agiza email
kutoka email.message agiza Message
kutoka email._policybase agiza compat32
kutoka test.support agiza load_package_tests
kutoka test.test_email agiza __file__ kama landmark

# Load all tests kwenye package
eleza load_tests(*args):
    rudisha load_package_tests(os.path.dirname(__file__), *args)


# helper code used by a number of test modules.

eleza openfile(filename, *args, **kws):
    path = os.path.join(os.path.dirname(landmark), 'data', filename)
    rudisha open(path, *args, **kws)


# Base test class
kundi TestEmailBase(unittest.TestCase):

    maxDiff = Tupu
    # Currently the default policy ni compat32.  By setting that kama the default
    # here we make minimal changes kwenye the test_email tests compared to their
    # pre-3.3 state.
    policy = compat32
    # Likewise, the default message object ni Message.
    message = Message

    eleza __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.addTypeEqualityFunc(bytes, self.assertBytesEqual)

    # Backward compatibility to minimize test_email test changes.
    ndiffAssertEqual = unittest.TestCase.assertEqual

    eleza _msgobj(self, filename):
        ukijumuisha openfile(filename) kama fp:
            rudisha email.message_kutoka_file(fp, policy=self.policy)

    eleza _str_msg(self, string, message=Tupu, policy=Tupu):
        ikiwa policy ni Tupu:
            policy = self.policy
        ikiwa message ni Tupu:
            message = self.message
        rudisha email.message_kutoka_string(string, message, policy=policy)

    eleza _bytes_msg(self, bytestring, message=Tupu, policy=Tupu):
        ikiwa policy ni Tupu:
            policy = self.policy
        ikiwa message ni Tupu:
            message = self.message
        rudisha email.message_kutoka_bytes(bytestring, message, policy=policy)

    eleza _make_message(self):
        rudisha self.message(policy=self.policy)

    eleza _bytes_repr(self, b):
        rudisha [repr(x) kila x kwenye b.splitlines(keepends=Kweli)]

    eleza assertBytesEqual(self, first, second, msg):
        """Our byte strings are really encoded strings; improve diff output"""
        self.assertEqual(self._bytes_repr(first), self._bytes_repr(second))

    eleza assertDefectsEqual(self, actual, expected):
        self.assertEqual(len(actual), len(expected), actual)
        kila i kwenye range(len(actual)):
            self.assertIsInstance(actual[i], expected[i],
                                    'item {}'.format(i))


eleza parameterize(cls):
    """A test method parameterization kundi decorator.

    Parameters are specified kama the value of a kundi attribute that ends with
    the string '_params'.  Call the portion before '_params' the prefix.  Then
    a method to be parameterized must have the same prefix, the string
    '_as_', na an arbitrary suffix.

    The value of the _params attribute may be either a dictionary ama a list.
    The values kwenye the dictionary na the elements of the list may either be
    single values, ama a list.  If single values, they are turned into single
    element tuples.  However derived, the resulting sequence ni pitaed via
    *args to the parameterized test function.

    In a _params dictionary, the keys become part of the name of the generated
    tests.  In a _params list, the values kwenye the list are converted into a
    string by joining the string values of the elements of the tuple by '_' and
    converting any blanks into '_'s, na this become part of the name.
    The  full name of a generated test ni a 'test_' prefix, the portion of the
    test function name after the  '_as_' separator, plus an '_', plus the name
    derived kama explained above.

    For example, ikiwa we have:

        count_params = range(2)

        eleza count_as_foo_arg(self, foo):
            self.assertEqual(foo+1, myfunc(foo))

    we will get parameterized test methods named:
        test_foo_arg_0
        test_foo_arg_1
        test_foo_arg_2

    Or we could have:

        example_params = {'foo': ('bar', 1), 'bing': ('bang', 2)}

        eleza example_as_myfunc_input(self, name, count):
            self.assertEqual(name+str(count), myfunc(name, count))

    na get:
        test_myfunc_input_foo
        test_myfunc_input_bing

    Note: ikiwa na only ikiwa the generated test name ni a valid identifier can it
    be used to select the test individually kutoka the unittest command line.

    The values kwenye the params dict can be a single value, a tuple, ama a
    dict.  If a single value of a tuple, it ni pitaed to the test function
    kama positional arguments.  If a dict, it ni a pitaed via **kw.

    """
    paramdicts = {}
    testers = collections.defaultdict(list)
    kila name, attr kwenye cls.__dict__.items():
        ikiwa name.endswith('_params'):
            ikiwa sio hasattr(attr, 'keys'):
                d = {}
                kila x kwenye attr:
                    ikiwa sio hasattr(x, '__iter__'):
                        x = (x,)
                    n = '_'.join(str(v) kila v kwenye x).replace(' ', '_')
                    d[n] = x
                attr = d
            paramdicts[name[:-7] + '_as_'] = attr
        ikiwa '_as_' kwenye name:
            testers[name.split('_as_')[0] + '_as_'].append(name)
    testfuncs = {}
    kila name kwenye paramdicts:
        ikiwa name haiko kwenye testers:
            ashiria ValueError("No tester found kila {}".format(name))
    kila name kwenye testers:
        ikiwa name haiko kwenye paramdicts:
            ashiria ValueError("No params found kila {}".format(name))
    kila name, attr kwenye cls.__dict__.items():
        kila paramsname, paramsdict kwenye paramdicts.items():
            ikiwa name.startswith(paramsname):
                testnameroot = 'test_' + name[len(paramsname):]
                kila paramname, params kwenye paramsdict.items():
                    ikiwa hasattr(params, 'keys'):
                        test = (lambda self, name=name, params=params:
                                    getattr(self, name)(**params))
                    isipokua:
                        test = (lambda self, name=name, params=params:
                                        getattr(self, name)(*params))
                    testname = testnameroot + '_' + paramname
                    test.__name__ = testname
                    testfuncs[testname] = test
    kila key, value kwenye testfuncs.items():
        setattr(cls, key, value)
    rudisha cls
