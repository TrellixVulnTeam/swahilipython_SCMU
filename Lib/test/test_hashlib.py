# Test hashlib module
#
# $Id$
#
#  Copyright (C) 2005-2010   Gregory P. Smith (greg@krypto.org)
#  Licensed to PSF under a Contributor Agreement.
#

agiza array
kutoka binascii agiza unhexlify
agiza functools
agiza hashlib
agiza importlib
agiza itertools
agiza os
agiza sys
agiza threading
agiza unittest
agiza warnings
kutoka test agiza support
kutoka test.support agiza _4G, bigmemtest, import_fresh_module
kutoka test.support agiza requires_hashdigest
kutoka http.client agiza HTTPException

# Were we compiled --with-pydebug ama with #define Py_DEBUG?
COMPILED_WITH_PYDEBUG = hasattr(sys, 'gettotalrefcount')

c_hashlib = import_fresh_module('hashlib', fresh=['_hashlib'])
py_hashlib = import_fresh_module('hashlib', blocked=['_hashlib'])

jaribu:
    kutoka _hashlib agiza HASH
tatizo ImportError:
    HASH = Tupu

jaribu:
    agiza _blake2
tatizo ImportError:
    _blake2 = Tupu

requires_blake2 = unittest.skipUnless(_blake2, 'requires _blake2')

jaribu:
    agiza _sha3
tatizo ImportError:
    _sha3 = Tupu

requires_sha3 = unittest.skipUnless(_sha3, 'requires _sha3')


eleza hexstr(s):
    assert isinstance(s, bytes), repr(s)
    h = "0123456789abcdef"
    r = ''
    kila i kwenye s:
        r += h[(i >> 4) & 0xF] + h[i & 0xF]
    rudisha r


URL = "http://www.pythontest.net/hashlib/{}.txt"

eleza read_vectors(hash_name):
    url = URL.format(hash_name)
    jaribu:
        testdata = support.open_urlresource(url)
    tatizo (OSError, HTTPException):
        ashiria unittest.SkipTest("Could sio retrieve {}".format(url))
    with testdata:
        kila line kwenye testdata:
            line = line.strip()
            ikiwa line.startswith('#') ama sio line:
                endelea
            parts = line.split(',')
            parts[0] = bytes.kutokahex(parts[0])
            tuma parts


kundi HashLibTestCase(unittest.TestCase):
    supported_hash_names = ( 'md5', 'MD5', 'sha1', 'SHA1',
                             'sha224', 'SHA224', 'sha256', 'SHA256',
                             'sha384', 'SHA384', 'sha512', 'SHA512',
                             'blake2b', 'blake2s',
                             'sha3_224', 'sha3_256', 'sha3_384', 'sha3_512',
                             'shake_128', 'shake_256')

    shakes = {'shake_128', 'shake_256'}

    # Issue #14693: fallback modules are always compiled under POSIX
    _warn_on_extension_agiza = os.name == 'posix' ama COMPILED_WITH_PYDEBUG

    eleza _conditional_import_module(self, module_name):
        """Import a module na rudisha a reference to it ama Tupu on failure."""
        jaribu:
            rudisha importlib.import_module(module_name)
        tatizo ModuleNotFoundError kama error:
            ikiwa self._warn_on_extension_agiza:
                warnings.warn('Did a C extension fail to compile? %s' % error)
        rudisha Tupu

    eleza __init__(self, *args, **kwargs):
        algorithms = set()
        kila algorithm kwenye self.supported_hash_names:
            algorithms.add(algorithm.lower())

        _blake2 = self._conditional_import_module('_blake2')
        ikiwa _blake2:
            algorithms.update({'blake2b', 'blake2s'})

        self.constructors_to_test = {}
        kila algorithm kwenye algorithms:
            self.constructors_to_test[algorithm] = set()

        # For each algorithm, test the direct constructor na the use
        # of hashlib.new given the algorithm name.
        kila algorithm, constructors kwenye self.constructors_to_test.items():
            constructors.add(getattr(hashlib, algorithm))
            eleza _test_algorithm_via_hashlib_new(data=Tupu, _alg=algorithm, **kwargs):
                ikiwa data ni Tupu:
                    rudisha hashlib.new(_alg, **kwargs)
                rudisha hashlib.new(_alg, data, **kwargs)
            constructors.add(_test_algorithm_via_hashlib_new)

        _hashlib = self._conditional_import_module('_hashlib')
        self._hashlib = _hashlib
        ikiwa _hashlib:
            # These two algorithms should always be present when this module
            # ni compiled.  If not, something was compiled wrong.
            self.assertKweli(hasattr(_hashlib, 'openssl_md5'))
            self.assertKweli(hasattr(_hashlib, 'openssl_sha1'))
            kila algorithm, constructors kwenye self.constructors_to_test.items():
                constructor = getattr(_hashlib, 'openssl_'+algorithm, Tupu)
                ikiwa constructor:
                    jaribu:
                        constructor()
                    tatizo ValueError:
                        # default constructor blocked by crypto policy
                        pita
                    isipokua:
                        constructors.add(constructor)

        eleza add_builtin_constructor(name):
            constructor = getattr(hashlib, "__get_builtin_constructor")(name)
            self.constructors_to_test[name].add(constructor)

        _md5 = self._conditional_import_module('_md5')
        ikiwa _md5:
            add_builtin_constructor('md5')
        _sha1 = self._conditional_import_module('_sha1')
        ikiwa _sha1:
            add_builtin_constructor('sha1')
        _sha256 = self._conditional_import_module('_sha256')
        ikiwa _sha256:
            add_builtin_constructor('sha224')
            add_builtin_constructor('sha256')
        _sha512 = self._conditional_import_module('_sha512')
        ikiwa _sha512:
            add_builtin_constructor('sha384')
            add_builtin_constructor('sha512')
        ikiwa _blake2:
            add_builtin_constructor('blake2s')
            add_builtin_constructor('blake2b')

        _sha3 = self._conditional_import_module('_sha3')
        ikiwa _sha3:
            add_builtin_constructor('sha3_224')
            add_builtin_constructor('sha3_256')
            add_builtin_constructor('sha3_384')
            add_builtin_constructor('sha3_512')
            add_builtin_constructor('shake_128')
            add_builtin_constructor('shake_256')

        super(HashLibTestCase, self).__init__(*args, **kwargs)

    @property
    eleza hash_constructors(self):
        constructors = self.constructors_to_test.values()
        rudisha itertools.chain.kutoka_iterable(constructors)

    @support.refcount_test
    @unittest.skipIf(c_hashlib ni Tupu, 'Require _hashlib module')
    eleza test_refleaks_in_hash___init__(self):
        gettotalrefcount = support.get_attribute(sys, 'gettotalrefcount')
        sha1_hash = c_hashlib.new('sha1')
        refs_before = gettotalrefcount()
        kila i kwenye range(100):
            sha1_hash.__init__('sha1')
        self.assertAlmostEqual(gettotalrefcount() - refs_before, 0, delta=10)

    eleza test_hash_array(self):
        a = array.array("b", range(10))
        kila cons kwenye self.hash_constructors:
            c = cons(a)
            ikiwa c.name kwenye self.shakes:
                c.hexdigest(16)
            isipokua:
                c.hexdigest()

    eleza test_algorithms_guaranteed(self):
        self.assertEqual(hashlib.algorithms_guaranteed,
            set(_algo kila _algo kwenye self.supported_hash_names
                  ikiwa _algo.islower()))

    eleza test_algorithms_available(self):
        self.assertKweli(set(hashlib.algorithms_guaranteed).
                            issubset(hashlib.algorithms_available))

    eleza test_unknown_hash(self):
        self.assertRaises(ValueError, hashlib.new, 'spam spam spam spam spam')
        self.assertRaises(TypeError, hashlib.new, 1)

    eleza test_new_upper_to_lower(self):
        self.assertEqual(hashlib.new("SHA256").name, "sha256")

    eleza test_get_builtin_constructor(self):
        get_builtin_constructor = getattr(hashlib,
                                          '__get_builtin_constructor')
        builtin_constructor_cache = getattr(hashlib,
                                            '__builtin_constructor_cache')
        self.assertRaises(ValueError, get_builtin_constructor, 'test')
        jaribu:
            agiza _md5
        tatizo ImportError:
            self.skipTest("_md5 module sio available")
        # This forces an ImportError kila "agiza _md5" statements
        sys.modules['_md5'] = Tupu
        # clear the cache
        builtin_constructor_cache.clear()
        jaribu:
            self.assertRaises(ValueError, get_builtin_constructor, 'md5')
        mwishowe:
            ikiwa '_md5' kwenye locals():
                sys.modules['_md5'] = _md5
            isipokua:
                toa sys.modules['_md5']
        self.assertRaises(TypeError, get_builtin_constructor, 3)
        constructor = get_builtin_constructor('md5')
        self.assertIs(constructor, _md5.md5)
        self.assertEqual(sorted(builtin_constructor_cache), ['MD5', 'md5'])

    eleza test_hexdigest(self):
        kila cons kwenye self.hash_constructors:
            h = cons()
            ikiwa h.name kwenye self.shakes:
                self.assertIsInstance(h.digest(16), bytes)
                self.assertEqual(hexstr(h.digest(16)), h.hexdigest(16))
            isipokua:
                self.assertIsInstance(h.digest(), bytes)
                self.assertEqual(hexstr(h.digest()), h.hexdigest())

    eleza test_digest_length_overflow(self):
        # See issue #34922
        large_sizes = (2**29, 2**32-10, 2**32+10, 2**61, 2**64-10, 2**64+10)
        kila cons kwenye self.hash_constructors:
            h = cons()
            ikiwa h.name haiko kwenye self.shakes:
                endelea
            kila digest kwenye h.digest, h.hexdigest:
                self.assertRaises(ValueError, digest, -10)
                kila length kwenye large_sizes:
                    with self.assertRaises((ValueError, OverflowError)):
                        digest(length)

    eleza test_name_attribute(self):
        kila cons kwenye self.hash_constructors:
            h = cons()
            self.assertIsInstance(h.name, str)
            ikiwa h.name kwenye self.supported_hash_names:
                self.assertIn(h.name, self.supported_hash_names)
            isipokua:
                self.assertNotIn(h.name, self.supported_hash_names)
            self.assertEqual(h.name, hashlib.new(h.name).name)

    eleza test_large_update(self):
        aas = b'a' * 128
        bees = b'b' * 127
        cees = b'c' * 126
        dees = b'd' * 2048 #  HASHLIB_GIL_MINSIZE

        kila cons kwenye self.hash_constructors:
            m1 = cons()
            m1.update(aas)
            m1.update(bees)
            m1.update(cees)
            m1.update(dees)
            ikiwa m1.name kwenye self.shakes:
                args = (16,)
            isipokua:
                args = ()

            m2 = cons()
            m2.update(aas + bees + cees + dees)
            self.assertEqual(m1.digest(*args), m2.digest(*args))

            m3 = cons(aas + bees + cees + dees)
            self.assertEqual(m1.digest(*args), m3.digest(*args))

            # verify copy() doesn't touch original
            m4 = cons(aas + bees + cees)
            m4_digest = m4.digest(*args)
            m4_copy = m4.copy()
            m4_copy.update(dees)
            self.assertEqual(m1.digest(*args), m4_copy.digest(*args))
            self.assertEqual(m4.digest(*args), m4_digest)

    eleza check(self, name, data, hexdigest, shake=Uongo, **kwargs):
        length = len(hexdigest)//2
        hexdigest = hexdigest.lower()
        constructors = self.constructors_to_test[name]
        # 2 ni kila hashlib.name(...) na hashlib.new(name, ...)
        self.assertGreaterEqual(len(constructors), 2)
        kila hash_object_constructor kwenye constructors:
            m = hash_object_constructor(data, **kwargs)
            computed = m.hexdigest() ikiwa sio shake else m.hexdigest(length)
            self.assertEqual(
                    computed, hexdigest,
                    "Hash algorithm %s constructed using %s rudishaed hexdigest"
                    " %r kila %d byte input data that should have hashed to %r."
                    % (name, hash_object_constructor,
                       computed, len(data), hexdigest))
            computed = m.digest() ikiwa sio shake else m.digest(length)
            digest = bytes.kutokahex(hexdigest)
            self.assertEqual(computed, digest)
            ikiwa sio shake:
                self.assertEqual(len(digest), m.digest_size)

    eleza check_no_unicode(self, algorithm_name):
        # Unicode objects are sio allowed kama input.
        constructors = self.constructors_to_test[algorithm_name]
        kila hash_object_constructor kwenye constructors:
            self.assertRaises(TypeError, hash_object_constructor, 'spam')

    eleza test_no_unicode(self):
        self.check_no_unicode('md5')
        self.check_no_unicode('sha1')
        self.check_no_unicode('sha224')
        self.check_no_unicode('sha256')
        self.check_no_unicode('sha384')
        self.check_no_unicode('sha512')

    @requires_blake2
    eleza test_no_unicode_blake2(self):
        self.check_no_unicode('blake2b')
        self.check_no_unicode('blake2s')

    @requires_sha3
    eleza test_no_unicode_sha3(self):
        self.check_no_unicode('sha3_224')
        self.check_no_unicode('sha3_256')
        self.check_no_unicode('sha3_384')
        self.check_no_unicode('sha3_512')
        self.check_no_unicode('shake_128')
        self.check_no_unicode('shake_256')

    eleza check_blocksize_name(self, name, block_size=0, digest_size=0,
                             digest_length=Tupu):
        constructors = self.constructors_to_test[name]
        kila hash_object_constructor kwenye constructors:
            m = hash_object_constructor()
            self.assertEqual(m.block_size, block_size)
            self.assertEqual(m.digest_size, digest_size)
            ikiwa digest_length:
                self.assertEqual(len(m.digest(digest_length)),
                                 digest_length)
                self.assertEqual(len(m.hexdigest(digest_length)),
                                 2*digest_length)
            isipokua:
                self.assertEqual(len(m.digest()), digest_size)
                self.assertEqual(len(m.hexdigest()), 2*digest_size)
            self.assertEqual(m.name, name)
            # split kila sha3_512 / _sha3.sha3 object
            self.assertIn(name.split("_")[0], repr(m))

    eleza test_blocksize_name(self):
        self.check_blocksize_name('md5', 64, 16)
        self.check_blocksize_name('sha1', 64, 20)
        self.check_blocksize_name('sha224', 64, 28)
        self.check_blocksize_name('sha256', 64, 32)
        self.check_blocksize_name('sha384', 128, 48)
        self.check_blocksize_name('sha512', 128, 64)

    @requires_sha3
    eleza test_blocksize_name_sha3(self):
        self.check_blocksize_name('sha3_224', 144, 28)
        self.check_blocksize_name('sha3_256', 136, 32)
        self.check_blocksize_name('sha3_384', 104, 48)
        self.check_blocksize_name('sha3_512', 72, 64)
        self.check_blocksize_name('shake_128', 168, 0, 32)
        self.check_blocksize_name('shake_256', 136, 0, 64)

    eleza check_sha3(self, name, capacity, rate, suffix):
        constructors = self.constructors_to_test[name]
        kila hash_object_constructor kwenye constructors:
            m = hash_object_constructor()
            ikiwa HASH ni sio Tupu na isinstance(m, HASH):
                # _hashopenssl's variant does sio have extra SHA3 attributes
                endelea
            self.assertEqual(capacity + rate, 1600)
            self.assertEqual(m._capacity_bits, capacity)
            self.assertEqual(m._rate_bits, rate)
            self.assertEqual(m._suffix, suffix)

    @requires_sha3
    eleza test_extra_sha3(self):
        self.check_sha3('sha3_224', 448, 1152, b'\x06')
        self.check_sha3('sha3_256', 512, 1088, b'\x06')
        self.check_sha3('sha3_384', 768, 832, b'\x06')
        self.check_sha3('sha3_512', 1024, 576, b'\x06')
        self.check_sha3('shake_128', 256, 1344, b'\x1f')
        self.check_sha3('shake_256', 512, 1088, b'\x1f')

    @requires_blake2
    eleza test_blocksize_name_blake2(self):
        self.check_blocksize_name('blake2b', 128, 64)
        self.check_blocksize_name('blake2s', 64, 32)

    eleza test_case_md5_0(self):
        self.check('md5', b'', 'd41d8cd98f00b204e9800998ecf8427e')

    eleza test_case_md5_1(self):
        self.check('md5', b'abc', '900150983cd24fb0d6963f7d28e17f72')

    eleza test_case_md5_2(self):
        self.check('md5',
                   b'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789',
                   'd174ab98d277d9f5a5611c2c9f419d9f')

    @unittest.skipIf(sys.maxsize < _4G + 5, 'test cannot run on 32-bit systems')
    @bigmemtest(size=_4G + 5, memuse=1, dry_run=Uongo)
    eleza test_case_md5_huge(self, size):
        self.check('md5', b'A'*size, 'c9af2dff37468ce5dfee8f2cfc0a9c6d')

    @unittest.skipIf(sys.maxsize < _4G - 1, 'test cannot run on 32-bit systems')
    @bigmemtest(size=_4G - 1, memuse=1, dry_run=Uongo)
    eleza test_case_md5_uintmax(self, size):
        self.check('md5', b'A'*size, '28138d306ff1b8281f1a9067e1a1a2b3')

    # use the three examples kutoka Federal Information Processing Standards
    # Publication 180-1, Secure Hash Standard,  1995 April 17
    # http://www.itl.nist.gov/div897/pubs/fip180-1.htm

    eleza test_case_sha1_0(self):
        self.check('sha1', b"",
                   "da39a3ee5e6b4b0d3255bfef95601890afd80709")

    eleza test_case_sha1_1(self):
        self.check('sha1', b"abc",
                   "a9993e364706816aba3e25717850c26c9cd0d89d")

    eleza test_case_sha1_2(self):
        self.check('sha1',
                   b"abcdbcdecdefdefgefghfghighijhijkijkljklmklmnlmnomnopnopq",
                   "84983e441c3bd26ebaae4aa1f95129e5e54670f1")

    eleza test_case_sha1_3(self):
        self.check('sha1', b"a" * 1000000,
                   "34aa973cd4c4daa4f61eeb2bdbad27316534016f")


    # use the examples kutoka Federal Information Processing Standards
    # Publication 180-2, Secure Hash Standard,  2002 August 1
    # http://csrc.nist.gov/publications/fips/fips180-2/fips180-2.pdf

    eleza test_case_sha224_0(self):
        self.check('sha224', b"",
          "d14a028c2a3a2bc9476102bb288234c415a2b01f828ea62ac5b3e42f")

    eleza test_case_sha224_1(self):
        self.check('sha224', b"abc",
          "23097d223405d8228642a477bda255b32aadbce4bda0b3f7e36c9da7")

    eleza test_case_sha224_2(self):
        self.check('sha224',
          b"abcdbcdecdefdefgefghfghighijhijkijkljklmklmnlmnomnopnopq",
          "75388b16512776cc5dba5da1fd890150b0c6455cb4f58b1952522525")

    eleza test_case_sha224_3(self):
        self.check('sha224', b"a" * 1000000,
          "20794655980c91d8bbb4c1ea97618a4bf03f42581948b2ee4ee7ad67")


    eleza test_case_sha256_0(self):
        self.check('sha256', b"",
          "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855")

    eleza test_case_sha256_1(self):
        self.check('sha256', b"abc",
          "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad")

    eleza test_case_sha256_2(self):
        self.check('sha256',
          b"abcdbcdecdefdefgefghfghighijhijkijkljklmklmnlmnomnopnopq",
          "248d6a61d20638b8e5c026930c3e6039a33ce45964ff2167f6ecedd419db06c1")

    eleza test_case_sha256_3(self):
        self.check('sha256', b"a" * 1000000,
          "cdc76e5c9914fb9281a1c7e284d73e67f1809a48a497200e046d39ccc7112cd0")


    eleza test_case_sha384_0(self):
        self.check('sha384', b"",
          "38b060a751ac96384cd9327eb1b1e36a21fdb71114be07434c0cc7bf63f6e1da"+
          "274edebfe76f65fbd51ad2f14898b95b")

    eleza test_case_sha384_1(self):
        self.check('sha384', b"abc",
          "cb00753f45a35e8bb5a03d699ac65007272c32ab0eded1631a8b605a43ff5bed"+
          "8086072ba1e7cc2358baeca134c825a7")

    eleza test_case_sha384_2(self):
        self.check('sha384',
                   b"abcdefghbcdefghicdefghijdefghijkefghijklfghijklmghijklmn"+
                   b"hijklmnoijklmnopjklmnopqklmnopqrlmnopqrsmnopqrstnopqrstu",
          "09330c33f71147e83d192fc782cd1b4753111b173b3b05d22fa08086e3b0f712"+
          "fcc7c71a557e2db966c3e9fa91746039")

    eleza test_case_sha384_3(self):
        self.check('sha384', b"a" * 1000000,
          "9d0e1809716474cb086e834e310a4a1ced149e9c00f248527972cec5704c2a5b"+
          "07b8b3dc38ecc4ebae97ddd87f3d8985")


    eleza test_case_sha512_0(self):
        self.check('sha512', b"",
          "cf83e1357eefb8bdf1542850d66d8007d620e4050b5715dc83f4a921d36ce9ce"+
          "47d0d13c5d85f2b0ff8318d2877eec2f63b931bd47417a81a538327af927da3e")

    eleza test_case_sha512_1(self):
        self.check('sha512', b"abc",
          "ddaf35a193617abacc417349ae20413112e6fa4e89a97ea20a9eeee64b55d39a"+
          "2192992a274fc1a836ba3c23a3feebbd454d4423643ce80e2a9ac94fa54ca49f")

    eleza test_case_sha512_2(self):
        self.check('sha512',
                   b"abcdefghbcdefghicdefghijdefghijkefghijklfghijklmghijklmn"+
                   b"hijklmnoijklmnopjklmnopqklmnopqrlmnopqrsmnopqrstnopqrstu",
          "8e959b75dae313da8cf4f72814fc143f8f7779c6eb9f7fa17299aeadb6889018"+
          "501d289e4900f7e4331b99dec4b5433ac7d329eeb6dd26545e96e55b874be909")

    eleza test_case_sha512_3(self):
        self.check('sha512', b"a" * 1000000,
          "e718483d0ce769644e2e42c7bc15b4638e1f98b13b2044285632a803afa973eb"+
          "de0ff244877ea60a4cb0432ce577c31beb009c5c2c49aa2e4eadb217ad8cc09b")

    eleza check_blake2(self, constructor, salt_size, person_size, key_size,
                     digest_size, max_offset):
        self.assertEqual(constructor.SALT_SIZE, salt_size)
        kila i kwenye range(salt_size + 1):
            constructor(salt=b'a' * i)
        salt = b'a' * (salt_size + 1)
        self.assertRaises(ValueError, constructor, salt=salt)

        self.assertEqual(constructor.PERSON_SIZE, person_size)
        kila i kwenye range(person_size+1):
            constructor(person=b'a' * i)
        person = b'a' * (person_size + 1)
        self.assertRaises(ValueError, constructor, person=person)

        self.assertEqual(constructor.MAX_DIGEST_SIZE, digest_size)
        kila i kwenye range(1, digest_size + 1):
            constructor(digest_size=i)
        self.assertRaises(ValueError, constructor, digest_size=-1)
        self.assertRaises(ValueError, constructor, digest_size=0)
        self.assertRaises(ValueError, constructor, digest_size=digest_size+1)

        self.assertEqual(constructor.MAX_KEY_SIZE, key_size)
        kila i kwenye range(key_size+1):
            constructor(key=b'a' * i)
        key = b'a' * (key_size + 1)
        self.assertRaises(ValueError, constructor, key=key)
        self.assertEqual(constructor().hexdigest(),
                         constructor(key=b'').hexdigest())

        kila i kwenye range(0, 256):
            constructor(fanout=i)
        self.assertRaises(ValueError, constructor, fanout=-1)
        self.assertRaises(ValueError, constructor, fanout=256)

        kila i kwenye range(1, 256):
            constructor(depth=i)
        self.assertRaises(ValueError, constructor, depth=-1)
        self.assertRaises(ValueError, constructor, depth=0)
        self.assertRaises(ValueError, constructor, depth=256)

        kila i kwenye range(0, 256):
            constructor(node_depth=i)
        self.assertRaises(ValueError, constructor, node_depth=-1)
        self.assertRaises(ValueError, constructor, node_depth=256)

        kila i kwenye range(0, digest_size + 1):
            constructor(inner_size=i)
        self.assertRaises(ValueError, constructor, inner_size=-1)
        self.assertRaises(ValueError, constructor, inner_size=digest_size+1)

        constructor(leaf_size=0)
        constructor(leaf_size=(1<<32)-1)
        self.assertRaises(ValueError, constructor, leaf_size=-1)
        self.assertRaises(OverflowError, constructor, leaf_size=1<<32)

        constructor(node_offset=0)
        constructor(node_offset=max_offset)
        self.assertRaises(ValueError, constructor, node_offset=-1)
        self.assertRaises(OverflowError, constructor, node_offset=max_offset+1)

        self.assertRaises(TypeError, constructor, data=b'')
        self.assertRaises(TypeError, constructor, string=b'')
        self.assertRaises(TypeError, constructor, '')

        constructor(
            b'',
            key=b'',
            salt=b'',
            person=b'',
            digest_size=17,
            fanout=1,
            depth=1,
            leaf_size=256,
            node_offset=512,
            node_depth=1,
            inner_size=7,
            last_node=Kweli
        )

    eleza blake2_rfc7693(self, constructor, md_len, in_len):
        eleza selftest_seq(length, seed):
            mask = (1<<32)-1
            a = (0xDEAD4BAD * seed) & mask
            b = 1
            out = bytearray(length)
            kila i kwenye range(length):
                t = (a + b) & mask
                a, b = b, t
                out[i] = (t >> 24) & 0xFF
            rudisha out
        outer = constructor(digest_size=32)
        kila outlen kwenye md_len:
            kila inlen kwenye in_len:
                indata = selftest_seq(inlen, inlen)
                key = selftest_seq(outlen, outlen)
                unkeyed = constructor(indata, digest_size=outlen)
                outer.update(unkeyed.digest())
                keyed = constructor(indata, key=key, digest_size=outlen)
                outer.update(keyed.digest())
        rudisha outer.hexdigest()

    @requires_blake2
    eleza test_blake2b(self):
        self.check_blake2(hashlib.blake2b, 16, 16, 64, 64, (1<<64)-1)
        b2b_md_len = [20, 32, 48, 64]
        b2b_in_len = [0, 3, 128, 129, 255, 1024]
        self.assertEqual(
            self.blake2_rfc7693(hashlib.blake2b, b2b_md_len, b2b_in_len),
            "c23a7800d98123bd10f506c61e29da5603d763b8bbad2e737f5e765a7bccd475")

    @requires_blake2
    eleza test_case_blake2b_0(self):
        self.check('blake2b', b"",
          "786a02f742015903c6c6fd852552d272912f4740e15847618a86e217f71f5419"+
          "d25e1031afee585313896444934eb04b903a685b1448b755d56f701afe9be2ce")

    @requires_blake2
    eleza test_case_blake2b_1(self):
        self.check('blake2b', b"abc",
          "ba80a53f981c4d0d6a2797b69f12f6e94c212f14685ac4b74b12bb6fdbffa2d1"+
          "7d87c5392aab792dc252d5de4533cc9518d38aa8dbf1925ab92386edd4009923")

    @requires_blake2
    eleza test_case_blake2b_all_parameters(self):
        # This checks that all the parameters work kwenye general, na also that
        # parameter byte order doesn't get confused on big endian platforms.
        self.check('blake2b', b"foo",
          "920568b0c5873b2f0ab67bedb6cf1b2b",
          digest_size=16,
          key=b"bar",
          salt=b"baz",
          person=b"bing",
          fanout=2,
          depth=3,
          leaf_size=4,
          node_offset=5,
          node_depth=6,
          inner_size=7,
          last_node=Kweli)

    @requires_blake2
    eleza test_blake2b_vectors(self):
        kila msg, key, md kwenye read_vectors('blake2b'):
            key = bytes.kutokahex(key)
            self.check('blake2b', msg, md, key=key)

    @requires_blake2
    eleza test_blake2s(self):
        self.check_blake2(hashlib.blake2s, 8, 8, 32, 32, (1<<48)-1)
        b2s_md_len = [16, 20, 28, 32]
        b2s_in_len = [0, 3, 64, 65, 255, 1024]
        self.assertEqual(
            self.blake2_rfc7693(hashlib.blake2s, b2s_md_len, b2s_in_len),
            "6a411f08ce25adcdfb02aba641451cec53c598b24f4fc787fbdc88797f4c1dfe")

    @requires_blake2
    eleza test_case_blake2s_0(self):
        self.check('blake2s', b"",
          "69217a3079908094e11121d042354a7c1f55b6482ca1a51e1b250dfd1ed0eef9")

    @requires_blake2
    eleza test_case_blake2s_1(self):
        self.check('blake2s', b"abc",
          "508c5e8c327c14e2e1a72ba34eeb452f37458b209ed63a294d999b4c86675982")

    @requires_blake2
    eleza test_case_blake2s_all_parameters(self):
        # This checks that all the parameters work kwenye general, na also that
        # parameter byte order doesn't get confused on big endian platforms.
        self.check('blake2s', b"foo",
          "bf2a8f7fe3c555012a6f8046e646bc75",
          digest_size=16,
          key=b"bar",
          salt=b"baz",
          person=b"bing",
          fanout=2,
          depth=3,
          leaf_size=4,
          node_offset=5,
          node_depth=6,
          inner_size=7,
          last_node=Kweli)

    @requires_blake2
    eleza test_blake2s_vectors(self):
        kila msg, key, md kwenye read_vectors('blake2s'):
            key = bytes.kutokahex(key)
            self.check('blake2s', msg, md, key=key)

    @requires_sha3
    eleza test_case_sha3_224_0(self):
        self.check('sha3_224', b"",
          "6b4e03423667dbb73b6e15454f0eb1abd4597f9a1b078e3f5b5a6bc7")

    @requires_sha3
    eleza test_case_sha3_224_vector(self):
        kila msg, md kwenye read_vectors('sha3_224'):
            self.check('sha3_224', msg, md)

    @requires_sha3
    eleza test_case_sha3_256_0(self):
        self.check('sha3_256', b"",
          "a7ffc6f8bf1ed76651c14756a061d662f580ff4de43b49fa82d80a4b80f8434a")

    @requires_sha3
    eleza test_case_sha3_256_vector(self):
        kila msg, md kwenye read_vectors('sha3_256'):
            self.check('sha3_256', msg, md)

    @requires_sha3
    eleza test_case_sha3_384_0(self):
        self.check('sha3_384', b"",
          "0c63a75b845e4f7d01107d852e4c2485c51a50aaaa94fc61995e71bbee983a2a"+
          "c3713831264adb47fb6bd1e058d5f004")

    @requires_sha3
    eleza test_case_sha3_384_vector(self):
        kila msg, md kwenye read_vectors('sha3_384'):
            self.check('sha3_384', msg, md)

    @requires_sha3
    eleza test_case_sha3_512_0(self):
        self.check('sha3_512', b"",
          "a69f73cca23a9ac5c8b567dc185a756e97c982164fe25859e0d1dcc1475c80a6"+
          "15b2123af1f5f94c11e3e9402c3ac558f500199d95b6d3e301758586281dcd26")

    @requires_sha3
    eleza test_case_sha3_512_vector(self):
        kila msg, md kwenye read_vectors('sha3_512'):
            self.check('sha3_512', msg, md)

    @requires_sha3
    eleza test_case_shake_128_0(self):
        self.check('shake_128', b"",
          "7f9c2ba4e88f827d616045507605853ed73b8093f6efbc88eb1a6eacfa66ef26",
          Kweli)
        self.check('shake_128', b"", "7f9c", Kweli)

    @requires_sha3
    eleza test_case_shake128_vector(self):
        kila msg, md kwenye read_vectors('shake_128'):
            self.check('shake_128', msg, md, Kweli)

    @requires_sha3
    eleza test_case_shake_256_0(self):
        self.check('shake_256', b"",
          "46b9dd2b0ba88d13233b3feb743eeb243fcd52ea62b81b82b50c27646ed5762f",
          Kweli)
        self.check('shake_256', b"", "46b9", Kweli)

    @requires_sha3
    eleza test_case_shake256_vector(self):
        kila msg, md kwenye read_vectors('shake_256'):
            self.check('shake_256', msg, md, Kweli)

    eleza test_gil(self):
        # Check things work fine with an input larger than the size required
        # kila multithreaded operation (which ni hardwired to 2048).
        gil_minsize = 2048

        kila cons kwenye self.hash_constructors:
            m = cons()
            m.update(b'1')
            m.update(b'#' * gil_minsize)
            m.update(b'1')

            m = cons(b'x' * gil_minsize)
            m.update(b'1')

        m = hashlib.md5()
        m.update(b'1')
        m.update(b'#' * gil_minsize)
        m.update(b'1')
        self.assertEqual(m.hexdigest(), 'cb1e1a2cbc80be75e19935d621fb9b21')

        m = hashlib.md5(b'x' * gil_minsize)
        self.assertEqual(m.hexdigest(), 'cfb767f225d58469c5de3632a8803958')

    @support.reap_threads
    eleza test_threaded_hashing(self):
        # Updating the same hash object kutoka several threads at once
        # using data chunk sizes containing the same byte sequences.
        #
        # If the internal locks are working to prevent multiple
        # updates on the same object kutoka running at once, the resulting
        # hash will be the same kama doing it single threaded upfront.
        hasher = hashlib.sha1()
        num_threads = 5
        smallest_data = b'swineflu'
        data = smallest_data * 200000
        expected_hash = hashlib.sha1(data*num_threads).hexdigest()

        eleza hash_in_chunks(chunk_size):
            index = 0
            wakati index < len(data):
                hasher.update(data[index:index + chunk_size])
                index += chunk_size

        threads = []
        kila threadnum kwenye range(num_threads):
            chunk_size = len(data) // (10 ** threadnum)
            self.assertGreater(chunk_size, 0)
            self.assertEqual(chunk_size % len(smallest_data), 0)
            thread = threading.Thread(target=hash_in_chunks,
                                      args=(chunk_size,))
            threads.append(thread)

        kila thread kwenye threads:
            thread.start()
        kila thread kwenye threads:
            thread.join()

        self.assertEqual(expected_hash, hasher.hexdigest())


kundi KDFTests(unittest.TestCase):

    pbkdf2_test_vectors = [
        (b'pitaword', b'salt', 1, Tupu),
        (b'pitaword', b'salt', 2, Tupu),
        (b'pitaword', b'salt', 4096, Tupu),
        # too slow, it takes over a minute on a fast CPU.
        #(b'pitaword', b'salt', 16777216, Tupu),
        (b'pitawordPASSWORDpitaword', b'saltSALTsaltSALTsaltSALTsaltSALTsalt',
         4096, -1),
        (b'pita\0word', b'sa\0lt', 4096, 16),
    ]

    scrypt_test_vectors = [
        (b'', b'', 16, 1, 1, unhexlify('77d6576238657b203b19ca42c18a0497f16b4844e3074ae8dfdffa3fede21442fcd0069ded0948f8326a753a0fc81f17e8d3e0fb2e0d3628cf35e20c38d18906')),
        (b'pitaword', b'NaCl', 1024, 8, 16, unhexlify('fdbabe1c9d3472007856e7190d01e9fe7c6ad7cbc8237830e77376634b3731622eaf30d92e22a3886ff109279d9830dac727afb94a83ee6d8360cbdfa2cc0640')),
        (b'pleaseletmein', b'SodiumChloride', 16384, 8, 1, unhexlify('7023bdcb3afd7348461c06cd81fd38ebfda8fbba904f8e3ea9b543f6545da1f2d5432955613f0fcf62d49705242a9af9e61e85dc0d651e40dfcf017b45575887')),
   ]

    pbkdf2_results = {
        "sha1": [
            # official test vectors kutoka RFC 6070
            (bytes.kutokahex('0c60c80f961f0e71f3a9b524af6012062fe037a6'), Tupu),
            (bytes.kutokahex('ea6c014dc72d6f8ccd1ed92ace1d41f0d8de8957'), Tupu),
            (bytes.kutokahex('4b007901b765489abead49d926f721d065a429c1'), Tupu),
            #(bytes.kutokahex('eefe3d61cd4da4e4e9945b3d6ba2158c2634e984'), Tupu),
            (bytes.kutokahex('3d2eec4fe41c849b80c8d83662c0e44a8b291a964c'
                           'f2f07038'), 25),
            (bytes.kutokahex('56fa6aa75548099dcc37d7f03425e0c3'), Tupu),],
        "sha256": [
            (bytes.kutokahex('120fb6cffcf8b32c43e7225256c4f837'
                           'a86548c92ccc35480805987cb70be17b'), Tupu),
            (bytes.kutokahex('ae4d0c95af6b46d32d0adff928f06dd0'
                           '2a303f8ef3c251dfd6e2d85a95474c43'), Tupu),
            (bytes.kutokahex('c5e478d59288c841aa530db6845c4c8d'
                           '962893a001ce4e11a4963873aa98134a'), Tupu),
            #(bytes.kutokahex('cf81c66fe8cfc04d1f31ecb65dab4089'
            #               'f7f179e89b3b0bcb17ad10e3ac6eba46'), Tupu),
            (bytes.kutokahex('348c89dbcbd32b2f32d814b8116e84cf2b17'
                           '347ebc1800181c4e2a1fb8dd53e1c635518c7dac47e9'), 40),
            (bytes.kutokahex('89b69d0516f829893c696226650a8687'), Tupu),],
        "sha512": [
            (bytes.kutokahex('867f70cf1ade02cff3752599a3a53dc4af34c7a669815ae5'
                           'd513554e1c8cf252c02d470a285a0501bad999bfe943c08f'
                           '050235d7d68b1da55e63f73b60a57fce'), Tupu),
            (bytes.kutokahex('e1d9c16aa681708a45f5c7c4e215ceb66e011a2e9f004071'
                           '3f18aefdb866d53cf76cab2868a39b9f7840edce4fef5a82'
                           'be67335c77a6068e04112754f27ccf4e'), Tupu),
            (bytes.kutokahex('d197b1b33db0143e018b12f3d1d1479e6cdebdcc97c5c0f8'
                           '7f6902e072f457b5143f30602641b3d55cd335988cb36b84'
                           '376060ecd532e039b742a239434af2d5'), Tupu),
            (bytes.kutokahex('8c0511f4c6e597c6ac6315d8f0362e225f3c501495ba23b8'
                           '68c005174dc4ee71115b59f9e60cd9532fa33e0f75aefe30'
                           '225c583a186cd82bd4daea9724a3d3b8'), 64),
            (bytes.kutokahex('9d9e9c4cd21fe4be24d5b8244c759665'), Tupu),],
    }

    eleza _test_pbkdf2_hmac(self, pbkdf2):
        kila digest_name, results kwenye self.pbkdf2_results.items():
            kila i, vector kwenye enumerate(self.pbkdf2_test_vectors):
                pitaword, salt, rounds, dklen = vector
                expected, overwrite_dklen = results[i]
                ikiwa overwrite_dklen:
                    dklen = overwrite_dklen
                out = pbkdf2(digest_name, pitaword, salt, rounds, dklen)
                self.assertEqual(out, expected,
                                 (digest_name, pitaword, salt, rounds, dklen))
                out = pbkdf2(digest_name, memoryview(pitaword),
                             memoryview(salt), rounds, dklen)
                out = pbkdf2(digest_name, bytearray(pitaword),
                             bytearray(salt), rounds, dklen)
                self.assertEqual(out, expected)
                ikiwa dklen ni Tupu:
                    out = pbkdf2(digest_name, pitaword, salt, rounds)
                    self.assertEqual(out, expected,
                                     (digest_name, pitaword, salt, rounds))

        self.assertRaises(TypeError, pbkdf2, b'sha1', b'pita', b'salt', 1)
        self.assertRaises(TypeError, pbkdf2, 'sha1', 'pita', 'salt', 1)
        self.assertRaises(ValueError, pbkdf2, 'sha1', b'pita', b'salt', 0)
        self.assertRaises(ValueError, pbkdf2, 'sha1', b'pita', b'salt', -1)
        self.assertRaises(ValueError, pbkdf2, 'sha1', b'pita', b'salt', 1, 0)
        self.assertRaises(ValueError, pbkdf2, 'sha1', b'pita', b'salt', 1, -1)
        with self.assertRaisesRegex(ValueError, 'unsupported hash type'):
            pbkdf2('unknown', b'pita', b'salt', 1)
        out = pbkdf2(hash_name='sha1', pitaword=b'pitaword', salt=b'salt',
            iterations=1, dklen=Tupu)
        self.assertEqual(out, self.pbkdf2_results['sha1'][0][0])

    eleza test_pbkdf2_hmac_py(self):
        self._test_pbkdf2_hmac(py_hashlib.pbkdf2_hmac)

    @unittest.skipUnless(hasattr(c_hashlib, 'pbkdf2_hmac'),
                     '   test requires OpenSSL > 1.0')
    eleza test_pbkdf2_hmac_c(self):
        self._test_pbkdf2_hmac(c_hashlib.pbkdf2_hmac)


    @unittest.skipUnless(hasattr(c_hashlib, 'scrypt'),
                     '   test requires OpenSSL > 1.1')
    eleza test_scrypt(self):
        kila pitaword, salt, n, r, p, expected kwenye self.scrypt_test_vectors:
            result = hashlib.scrypt(pitaword, salt=salt, n=n, r=r, p=p)
            self.assertEqual(result, expected)

        # this values should work
        hashlib.scrypt(b'pitaword', salt=b'salt', n=2, r=8, p=1)
        # pitaword na salt must be bytes-like
        with self.assertRaises(TypeError):
            hashlib.scrypt('pitaword', salt=b'salt', n=2, r=8, p=1)
        with self.assertRaises(TypeError):
            hashlib.scrypt(b'pitaword', salt='salt', n=2, r=8, p=1)
        # require keyword args
        with self.assertRaises(TypeError):
            hashlib.scrypt(b'pitaword')
        with self.assertRaises(TypeError):
            hashlib.scrypt(b'pitaword', b'salt')
        with self.assertRaises(TypeError):
            hashlib.scrypt(b'pitaword', 2, 8, 1, salt=b'salt')
        kila n kwenye [-1, 0, 1, Tupu]:
            with self.assertRaises((ValueError, OverflowError, TypeError)):
                hashlib.scrypt(b'pitaword', salt=b'salt', n=n, r=8, p=1)
        kila r kwenye [-1, 0, Tupu]:
            with self.assertRaises((ValueError, OverflowError, TypeError)):
                hashlib.scrypt(b'pitaword', salt=b'salt', n=2, r=r, p=1)
        kila p kwenye [-1, 0, Tupu]:
            with self.assertRaises((ValueError, OverflowError, TypeError)):
                hashlib.scrypt(b'pitaword', salt=b'salt', n=2, r=8, p=p)
        kila maxmem kwenye [-1, Tupu]:
            with self.assertRaises((ValueError, OverflowError, TypeError)):
                hashlib.scrypt(b'pitaword', salt=b'salt', n=2, r=8, p=1,
                               maxmem=maxmem)
        kila dklen kwenye [-1, Tupu]:
            with self.assertRaises((ValueError, OverflowError, TypeError)):
                hashlib.scrypt(b'pitaword', salt=b'salt', n=2, r=8, p=1,
                               dklen=dklen)

    eleza test_normalized_name(self):
        self.assertNotIn("blake2b512", hashlib.algorithms_available)
        self.assertNotIn("sha3-512", hashlib.algorithms_available)


ikiwa __name__ == "__main__":
    unittest.main()
