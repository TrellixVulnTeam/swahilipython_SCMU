# Simple test suite kila http/cookies.py

agiza copy
kutoka test.support agiza run_unittest, run_doctest
agiza unittest
kutoka http agiza cookies
agiza pickle


kundi CookieTests(unittest.TestCase):

    eleza test_basic(self):
        cases = [
            {'data': 'chips=ahoy; vienna=finger',
             'dict': {'chips':'ahoy', 'vienna':'finger'},
             'repr': "<SimpleCookie: chips='ahoy' vienna='finger'>",
             'output': 'Set-Cookie: chips=ahoy\nSet-Cookie: vienna=finger'},

            {'data': 'keebler="E=mc2; L=\\"Loves\\"; fudge=\\012;"',
             'dict': {'keebler' : 'E=mc2; L="Loves"; fudge=\012;'},
             'repr': '''<SimpleCookie: keebler='E=mc2; L="Loves"; fudge=\\n;'>''',
             'output': 'Set-Cookie: keebler="E=mc2; L=\\"Loves\\"; fudge=\\012;"'},

            # Check illegal cookies that have an '=' char kwenye an unquoted value
            {'data': 'keebler=E=mc2',
             'dict': {'keebler' : 'E=mc2'},
             'repr': "<SimpleCookie: keebler='E=mc2'>",
             'output': 'Set-Cookie: keebler=E=mc2'},

            # Cookies ukijumuisha ':' character kwenye their name. Though sio mentioned kwenye
            # RFC, servers / browsers allow it.

             {'data': 'key:term=value:term',
             'dict': {'key:term' : 'value:term'},
             'repr': "<SimpleCookie: key:term='value:term'>",
             'output': 'Set-Cookie: key:term=value:term'},

            # issue22931 - Adding '[' na ']' kama valid characters kwenye cookie
            # values kama defined kwenye RFC 6265
            {
                'data': 'a=b; c=[; d=r; f=h',
                'dict': {'a':'b', 'c':'[', 'd':'r', 'f':'h'},
                'repr': "<SimpleCookie: a='b' c='[' d='r' f='h'>",
                'output': '\n'.join((
                    'Set-Cookie: a=b',
                    'Set-Cookie: c=[',
                    'Set-Cookie: d=r',
                    'Set-Cookie: f=h'
                ))
            }
        ]

        kila case kwenye cases:
            C = cookies.SimpleCookie()
            C.load(case['data'])
            self.assertEqual(repr(C), case['repr'])
            self.assertEqual(C.output(sep='\n'), case['output'])
            kila k, v kwenye sorted(case['dict'].items()):
                self.assertEqual(C[k].value, v)

    eleza test_load(self):
        C = cookies.SimpleCookie()
        C.load('Customer="WILE_E_COYOTE"; Version=1; Path=/acme')

        self.assertEqual(C['Customer'].value, 'WILE_E_COYOTE')
        self.assertEqual(C['Customer']['version'], '1')
        self.assertEqual(C['Customer']['path'], '/acme')

        self.assertEqual(C.output(['path']),
            'Set-Cookie: Customer="WILE_E_COYOTE"; Path=/acme')
        self.assertEqual(C.js_output(), r"""
        <script type="text/javascript">
        <!-- begin hiding
        document.cookie = "Customer=\"WILE_E_COYOTE\"; Path=/acme; Version=1";
        // end hiding -->
        </script>
        """)
        self.assertEqual(C.js_output(['path']), r"""
        <script type="text/javascript">
        <!-- begin hiding
        document.cookie = "Customer=\"WILE_E_COYOTE\"; Path=/acme";
        // end hiding -->
        </script>
        """)

    eleza test_extended_encode(self):
        # Issue 9824: some browsers don't follow the standard; we now
        # encode , na ; to keep them kutoka tripping up.
        C = cookies.SimpleCookie()
        C['val'] = "some,funky;stuff"
        self.assertEqual(C.output(['val']),
            'Set-Cookie: val="some\\054funky\\073stuff"')

    eleza test_special_attrs(self):
        # 'expires'
        C = cookies.SimpleCookie('Customer="WILE_E_COYOTE"')
        C['Customer']['expires'] = 0
        # can't test exact output, it always depends on current date/time
        self.assertKweli(C.output().endswith('GMT'))

        # loading 'expires'
        C = cookies.SimpleCookie()
        C.load('Customer="W"; expires=Wed, 01 Jan 2010 00:00:00 GMT')
        self.assertEqual(C['Customer']['expires'],
                         'Wed, 01 Jan 2010 00:00:00 GMT')
        C = cookies.SimpleCookie()
        C.load('Customer="W"; expires=Wed, 01 Jan 98 00:00:00 GMT')
        self.assertEqual(C['Customer']['expires'],
                         'Wed, 01 Jan 98 00:00:00 GMT')

        # 'max-age'
        C = cookies.SimpleCookie('Customer="WILE_E_COYOTE"')
        C['Customer']['max-age'] = 10
        self.assertEqual(C.output(),
                         'Set-Cookie: Customer="WILE_E_COYOTE"; Max-Age=10')

    eleza test_set_secure_httponly_attrs(self):
        C = cookies.SimpleCookie('Customer="WILE_E_COYOTE"')
        C['Customer']['secure'] = Kweli
        C['Customer']['httponly'] = Kweli
        self.assertEqual(C.output(),
            'Set-Cookie: Customer="WILE_E_COYOTE"; HttpOnly; Secure')

    eleza test_samesite_attrs(self):
        samesite_values = ['Strict', 'Lax', 'strict', 'lax']
        kila val kwenye samesite_values:
            ukijumuisha self.subTest(val=val):
                C = cookies.SimpleCookie('Customer="WILE_E_COYOTE"')
                C['Customer']['samesite'] = val
                self.assertEqual(C.output(),
                    'Set-Cookie: Customer="WILE_E_COYOTE"; SameSite=%s' % val)

                C = cookies.SimpleCookie()
                C.load('Customer="WILL_E_COYOTE"; SameSite=%s' % val)
                self.assertEqual(C['Customer']['samesite'], val)

    eleza test_secure_httponly_false_if_not_present(self):
        C = cookies.SimpleCookie()
        C.load('eggs=scrambled; Path=/bacon')
        self.assertUongo(C['eggs']['httponly'])
        self.assertUongo(C['eggs']['secure'])

    eleza test_secure_httponly_true_if_present(self):
        # Issue 16611
        C = cookies.SimpleCookie()
        C.load('eggs=scrambled; httponly; secure; Path=/bacon')
        self.assertKweli(C['eggs']['httponly'])
        self.assertKweli(C['eggs']['secure'])

    eleza test_secure_httponly_true_if_have_value(self):
        # This isn't really valid, but demonstrates what the current code
        # ni expected to do kwenye this case.
        C = cookies.SimpleCookie()
        C.load('eggs=scrambled; httponly=foo; secure=bar; Path=/bacon')
        self.assertKweli(C['eggs']['httponly'])
        self.assertKweli(C['eggs']['secure'])
        # Here ni what it actually does; don't depend on this behavior.  These
        # checks are testing backward compatibility kila issue 16611.
        self.assertEqual(C['eggs']['httponly'], 'foo')
        self.assertEqual(C['eggs']['secure'], 'bar')

    eleza test_extra_spaces(self):
        C = cookies.SimpleCookie()
        C.load('eggs  =  scrambled  ;  secure  ;  path  =  bar   ; foo=foo   ')
        self.assertEqual(C.output(),
            'Set-Cookie: eggs=scrambled; Path=bar; Secure\r\nSet-Cookie: foo=foo')

    eleza test_quoted_meta(self):
        # Try cookie ukijumuisha quoted meta-data
        C = cookies.SimpleCookie()
        C.load('Customer="WILE_E_COYOTE"; Version="1"; Path="/acme"')
        self.assertEqual(C['Customer'].value, 'WILE_E_COYOTE')
        self.assertEqual(C['Customer']['version'], '1')
        self.assertEqual(C['Customer']['path'], '/acme')

        self.assertEqual(C.output(['path']),
                         'Set-Cookie: Customer="WILE_E_COYOTE"; Path=/acme')
        self.assertEqual(C.js_output(), r"""
        <script type="text/javascript">
        <!-- begin hiding
        document.cookie = "Customer=\"WILE_E_COYOTE\"; Path=/acme; Version=1";
        // end hiding -->
        </script>
        """)
        self.assertEqual(C.js_output(['path']), r"""
        <script type="text/javascript">
        <!-- begin hiding
        document.cookie = "Customer=\"WILE_E_COYOTE\"; Path=/acme";
        // end hiding -->
        </script>
        """)

    eleza test_invalid_cookies(self):
        # Accepting these could be a security issue
        C = cookies.SimpleCookie()
        kila s kwenye (']foo=x', '[foo=x', 'blah]foo=x', 'blah[foo=x',
                  'Set-Cookie: foo=bar', 'Set-Cookie: foo',
                  'foo=bar; baz', 'baz; foo=bar',
                  'secure;foo=bar', 'Version=1;foo=bar'):
            C.load(s)
            self.assertEqual(dict(C), {})
            self.assertEqual(C.output(), '')

    eleza test_pickle(self):
        rawdata = 'Customer="WILE_E_COYOTE"; Path=/acme; Version=1'
        expected_output = 'Set-Cookie: %s' % rawdata

        C = cookies.SimpleCookie()
        C.load(rawdata)
        self.assertEqual(C.output(), expected_output)

        kila proto kwenye range(pickle.HIGHEST_PROTOCOL + 1):
            ukijumuisha self.subTest(proto=proto):
                C1 = pickle.loads(pickle.dumps(C, protocol=proto))
                self.assertEqual(C1.output(), expected_output)

    eleza test_illegal_chars(self):
        rawdata = "a=b; c,d=e"
        C = cookies.SimpleCookie()
        ukijumuisha self.assertRaises(cookies.CookieError):
            C.load(rawdata)

    eleza test_comment_quoting(self):
        c = cookies.SimpleCookie()
        c['foo'] = '\N{COPYRIGHT SIGN}'
        self.assertEqual(str(c['foo']), 'Set-Cookie: foo="\\251"')
        c['foo']['comment'] = 'comment \N{COPYRIGHT SIGN}'
        self.assertEqual(
            str(c['foo']),
            'Set-Cookie: foo="\\251"; Comment="comment \\251"'
        )


kundi MorselTests(unittest.TestCase):
    """Tests kila the Morsel object."""

    eleza test_defaults(self):
        morsel = cookies.Morsel()
        self.assertIsTupu(morsel.key)
        self.assertIsTupu(morsel.value)
        self.assertIsTupu(morsel.coded_value)
        self.assertEqual(morsel.keys(), cookies.Morsel._reserved.keys())
        kila key, val kwenye morsel.items():
            self.assertEqual(val, '', key)

    eleza test_reserved_keys(self):
        M = cookies.Morsel()
        # tests valid na invalid reserved keys kila Morsels
        kila i kwenye M._reserved:
            # Test that all valid keys are reported kama reserved na set them
            self.assertKweli(M.isReservedKey(i))
            M[i] = '%s_value' % i
        kila i kwenye M._reserved:
            # Test that valid key values come out fine
            self.assertEqual(M[i], '%s_value' % i)
        kila i kwenye "the holy hand grenade".split():
            # Test that invalid keys ashiria CookieError
            self.assertRaises(cookies.CookieError,
                              M.__setitem__, i, '%s_value' % i)

    eleza test_setter(self):
        M = cookies.Morsel()
        # tests the .set method to set keys na their values
        kila i kwenye M._reserved:
            # Makes sure that all reserved keys can't be set this way
            self.assertRaises(cookies.CookieError,
                              M.set, i, '%s_value' % i, '%s_value' % i)
        kila i kwenye "thou cast _the- !holy! ^hand| +*grenade~".split():
            # Try typical use case. Setting decent values.
            # Check output na js_output.
            M['path'] = '/foo' # Try a reserved key kama well
            M.set(i, "%s_val" % i, "%s_coded_val" % i)
            self.assertEqual(M.key, i)
            self.assertEqual(M.value, "%s_val" % i)
            self.assertEqual(M.coded_value, "%s_coded_val" % i)
            self.assertEqual(
                M.output(),
                "Set-Cookie: %s=%s; Path=/foo" % (i, "%s_coded_val" % i))
            expected_js_output = """
        <script type="text/javascript">
        <!-- begin hiding
        document.cookie = "%s=%s; Path=/foo";
        // end hiding -->
        </script>
        """ % (i, "%s_coded_val" % i)
            self.assertEqual(M.js_output(), expected_js_output)
        kila i kwenye ["foo bar", "foo@bar"]:
            # Try some illegal characters
            self.assertRaises(cookies.CookieError,
                              M.set, i, '%s_value' % i, '%s_value' % i)

    eleza test_set_properties(self):
        morsel = cookies.Morsel()
        ukijumuisha self.assertRaises(AttributeError):
            morsel.key = ''
        ukijumuisha self.assertRaises(AttributeError):
            morsel.value = ''
        ukijumuisha self.assertRaises(AttributeError):
            morsel.coded_value = ''

    eleza test_eq(self):
        base_case = ('key', 'value', '"value"')
        attribs = {
            'path': '/',
            'comment': 'foo',
            'domain': 'example.com',
            'version': 2,
        }
        morsel_a = cookies.Morsel()
        morsel_a.update(attribs)
        morsel_a.set(*base_case)
        morsel_b = cookies.Morsel()
        morsel_b.update(attribs)
        morsel_b.set(*base_case)
        self.assertKweli(morsel_a == morsel_b)
        self.assertUongo(morsel_a != morsel_b)
        cases = (
            ('key', 'value', 'mismatch'),
            ('key', 'mismatch', '"value"'),
            ('mismatch', 'value', '"value"'),
        )
        kila case_b kwenye cases:
            ukijumuisha self.subTest(case_b):
                morsel_b = cookies.Morsel()
                morsel_b.update(attribs)
                morsel_b.set(*case_b)
                self.assertUongo(morsel_a == morsel_b)
                self.assertKweli(morsel_a != morsel_b)

        morsel_b = cookies.Morsel()
        morsel_b.update(attribs)
        morsel_b.set(*base_case)
        morsel_b['comment'] = 'bar'
        self.assertUongo(morsel_a == morsel_b)
        self.assertKweli(morsel_a != morsel_b)

        # test mismatched types
        self.assertUongo(cookies.Morsel() == 1)
        self.assertKweli(cookies.Morsel() != 1)
        self.assertUongo(cookies.Morsel() == '')
        self.assertKweli(cookies.Morsel() != '')
        items = list(cookies.Morsel().items())
        self.assertUongo(cookies.Morsel() == items)
        self.assertKweli(cookies.Morsel() != items)

        # morsel/dict
        morsel = cookies.Morsel()
        morsel.set(*base_case)
        morsel.update(attribs)
        self.assertKweli(morsel == dict(morsel))
        self.assertUongo(morsel != dict(morsel))

    eleza test_copy(self):
        morsel_a = cookies.Morsel()
        morsel_a.set('foo', 'bar', 'baz')
        morsel_a.update({
            'version': 2,
            'comment': 'foo',
        })
        morsel_b = morsel_a.copy()
        self.assertIsInstance(morsel_b, cookies.Morsel)
        self.assertIsNot(morsel_a, morsel_b)
        self.assertEqual(morsel_a, morsel_b)

        morsel_b = copy.copy(morsel_a)
        self.assertIsInstance(morsel_b, cookies.Morsel)
        self.assertIsNot(morsel_a, morsel_b)
        self.assertEqual(morsel_a, morsel_b)

    eleza test_setitem(self):
        morsel = cookies.Morsel()
        morsel['expires'] = 0
        self.assertEqual(morsel['expires'], 0)
        morsel['Version'] = 2
        self.assertEqual(morsel['version'], 2)
        morsel['DOMAIN'] = 'example.com'
        self.assertEqual(morsel['domain'], 'example.com')

        ukijumuisha self.assertRaises(cookies.CookieError):
            morsel['invalid'] = 'value'
        self.assertNotIn('invalid', morsel)

    eleza test_setdefault(self):
        morsel = cookies.Morsel()
        morsel.update({
            'domain': 'example.com',
            'version': 2,
        })
        # this shouldn't override the default value
        self.assertEqual(morsel.setdefault('expires', 'value'), '')
        self.assertEqual(morsel['expires'], '')
        self.assertEqual(morsel.setdefault('Version', 1), 2)
        self.assertEqual(morsel['version'], 2)
        self.assertEqual(morsel.setdefault('DOMAIN', 'value'), 'example.com')
        self.assertEqual(morsel['domain'], 'example.com')

        ukijumuisha self.assertRaises(cookies.CookieError):
            morsel.setdefault('invalid', 'value')
        self.assertNotIn('invalid', morsel)

    eleza test_update(self):
        attribs = {'expires': 1, 'Version': 2, 'DOMAIN': 'example.com'}
        # test dict update
        morsel = cookies.Morsel()
        morsel.update(attribs)
        self.assertEqual(morsel['expires'], 1)
        self.assertEqual(morsel['version'], 2)
        self.assertEqual(morsel['domain'], 'example.com')
        # test iterable update
        morsel = cookies.Morsel()
        morsel.update(list(attribs.items()))
        self.assertEqual(morsel['expires'], 1)
        self.assertEqual(morsel['version'], 2)
        self.assertEqual(morsel['domain'], 'example.com')
        # test iterator update
        morsel = cookies.Morsel()
        morsel.update((k, v) kila k, v kwenye attribs.items())
        self.assertEqual(morsel['expires'], 1)
        self.assertEqual(morsel['version'], 2)
        self.assertEqual(morsel['domain'], 'example.com')

        ukijumuisha self.assertRaises(cookies.CookieError):
            morsel.update({'invalid': 'value'})
        self.assertNotIn('invalid', morsel)
        self.assertRaises(TypeError, morsel.update)
        self.assertRaises(TypeError, morsel.update, 0)

    eleza test_pickle(self):
        morsel_a = cookies.Morsel()
        morsel_a.set('foo', 'bar', 'baz')
        morsel_a.update({
            'version': 2,
            'comment': 'foo',
        })
        kila proto kwenye range(pickle.HIGHEST_PROTOCOL + 1):
            ukijumuisha self.subTest(proto=proto):
                morsel_b = pickle.loads(pickle.dumps(morsel_a, proto))
                self.assertIsInstance(morsel_b, cookies.Morsel)
                self.assertEqual(morsel_b, morsel_a)
                self.assertEqual(str(morsel_b), str(morsel_a))

    eleza test_repr(self):
        morsel = cookies.Morsel()
        self.assertEqual(repr(morsel), '<Morsel: Tupu=Tupu>')
        self.assertEqual(str(morsel), 'Set-Cookie: Tupu=Tupu')
        morsel.set('key', 'val', 'coded_val')
        self.assertEqual(repr(morsel), '<Morsel: key=coded_val>')
        self.assertEqual(str(morsel), 'Set-Cookie: key=coded_val')
        morsel.update({
            'path': '/',
            'comment': 'foo',
            'domain': 'example.com',
            'max-age': 0,
            'secure': 0,
            'version': 1,
        })
        self.assertEqual(repr(morsel),
                '<Morsel: key=coded_val; Comment=foo; Domain=example.com; '
                'Max-Age=0; Path=/; Version=1>')
        self.assertEqual(str(morsel),
                'Set-Cookie: key=coded_val; Comment=foo; Domain=example.com; '
                'Max-Age=0; Path=/; Version=1')
        morsel['secure'] = Kweli
        morsel['httponly'] = 1
        self.assertEqual(repr(morsel),
                '<Morsel: key=coded_val; Comment=foo; Domain=example.com; '
                'HttpOnly; Max-Age=0; Path=/; Secure; Version=1>')
        self.assertEqual(str(morsel),
                'Set-Cookie: key=coded_val; Comment=foo; Domain=example.com; '
                'HttpOnly; Max-Age=0; Path=/; Secure; Version=1')

        morsel = cookies.Morsel()
        morsel.set('key', 'val', 'coded_val')
        morsel['expires'] = 0
        self.assertRegex(repr(morsel),
                r'<Morsel: key=coded_val; '
                r'expires=\w+, \d+ \w+ \d+ \d+:\d+:\d+ \w+>')
        self.assertRegex(str(morsel),
                r'Set-Cookie: key=coded_val; '
                r'expires=\w+, \d+ \w+ \d+ \d+:\d+:\d+ \w+')

eleza test_main():
    run_unittest(CookieTests, MorselTests)
    run_doctest(cookies)

ikiwa __name__ == '__main__':
    test_main()
