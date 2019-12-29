#.  Copyright (C) 2005-2010   Gregory P. Smith (greg@krypto.org)
#  Licensed to PSF under a Contributor Agreement.
#

__doc__ = """hashlib module - A common interface to many hash functions.

new(name, data=b'', **kwargs) - rudishas a new hash object implementing the
                                given hash function; initializing the hash
                                using the given binary data.

Named constructor functions are also available, these are faster
than using new(name):

md5(), sha1(), sha224(), sha256(), sha384(), sha512(), blake2b(), blake2s(),
sha3_224, sha3_256, sha3_384, sha3_512, shake_128, na shake_256.

More algorithms may be available on your platform but the above are guaranteed
to exist.  See the algorithms_guaranteed na algorithms_available attributes
to find out what algorithm names can be pitaed to new().

NOTE: If you want the adler32 ama crc32 hash functions they are available in
the zlib module.

Choose your hash function wisely.  Some have known collision weaknesses.
sha384 na sha512 will be slow on 32 bit platforms.

Hash objects have these methods:
 - update(data): Update the hash object ukijumuisha the bytes kwenye data. Repeated calls
                 are equivalent to a single call ukijumuisha the concatenation of all
                 the arguments.
 - digest():     Return the digest of the bytes pitaed to the update() method
                 so far kama a bytes object.
 - hexdigest():  Like digest() tatizo the digest ni rudishaed kama a string
                 of double length, containing only hexadecimal digits.
 - copy():       Return a copy (clone) of the hash object. This can be used to
                 efficiently compute the digests of datas that share a common
                 initial substring.

For example, to obtain the digest of the byte string 'Nobody inspects the
spammish repetition':

    >>> agiza hashlib
    >>> m = hashlib.md5()
    >>> m.update(b"Nobody inspects")
    >>> m.update(b" the spammish repetition")
    >>> m.digest()
    b'\\xbbd\\x9c\\x83\\xdd\\x1e\\xa5\\xc9\\xd9\\xde\\xc9\\xa1\\x8d\\xf0\\xff\\xe9'

More condensed:

    >>> hashlib.sha224(b"Nobody inspects the spammish repetition").hexdigest()
    'a4337bc45a8fc544c03f52dc550cd6e1e87021bc896588bd79e901e2'

"""

# This tuple na __get_builtin_constructor() must be modified ikiwa a new
# always available algorithm ni added.
__always_supported = ('md5', 'sha1', 'sha224', 'sha256', 'sha384', 'sha512',
                      'blake2b', 'blake2s',
                      'sha3_224', 'sha3_256', 'sha3_384', 'sha3_512',
                      'shake_128', 'shake_256')


algorithms_guaranteed = set(__always_supported)
algorithms_available = set(__always_supported)

__all__ = __always_supported + ('new', 'algorithms_guaranteed',
                                'algorithms_available', 'pbkdf2_hmac')


__builtin_constructor_cache = {}

__block_openssl_constructor = {
    'sha3_224', 'sha3_256', 'sha3_384', 'sha3_512',
    'shake_128', 'shake_256',
    'blake2b', 'blake2s',
}

eleza __get_builtin_constructor(name):
    cache = __builtin_constructor_cache
    constructor = cache.get(name)
    ikiwa constructor ni sio Tupu:
        rudisha constructor
    jaribu:
        ikiwa name kwenye {'SHA1', 'sha1'}:
            agiza _sha1
            cache['SHA1'] = cache['sha1'] = _sha1.sha1
        lasivyo name kwenye {'MD5', 'md5'}:
            agiza _md5
            cache['MD5'] = cache['md5'] = _md5.md5
        lasivyo name kwenye {'SHA256', 'sha256', 'SHA224', 'sha224'}:
            agiza _sha256
            cache['SHA224'] = cache['sha224'] = _sha256.sha224
            cache['SHA256'] = cache['sha256'] = _sha256.sha256
        lasivyo name kwenye {'SHA512', 'sha512', 'SHA384', 'sha384'}:
            agiza _sha512
            cache['SHA384'] = cache['sha384'] = _sha512.sha384
            cache['SHA512'] = cache['sha512'] = _sha512.sha512
        lasivyo name kwenye {'blake2b', 'blake2s'}:
            agiza _blake2
            cache['blake2b'] = _blake2.blake2b
            cache['blake2s'] = _blake2.blake2s
        lasivyo name kwenye {'sha3_224', 'sha3_256', 'sha3_384', 'sha3_512'}:
            agiza _sha3
            cache['sha3_224'] = _sha3.sha3_224
            cache['sha3_256'] = _sha3.sha3_256
            cache['sha3_384'] = _sha3.sha3_384
            cache['sha3_512'] = _sha3.sha3_512
        lasivyo name kwenye {'shake_128', 'shake_256'}:
            agiza _sha3
            cache['shake_128'] = _sha3.shake_128
            cache['shake_256'] = _sha3.shake_256
    tatizo ImportError:
        pita  # no extension module, this hash ni unsupported.

    constructor = cache.get(name)
    ikiwa constructor ni sio Tupu:
        rudisha constructor

    ashiria ValueError('unsupported hash type ' + name)


eleza __get_openssl_constructor(name):
    ikiwa name kwenye __block_openssl_constructor:
        # Prefer our blake2 na sha3 implementation.
        rudisha __get_builtin_constructor(name)
    jaribu:
        f = getattr(_hashlib, 'openssl_' + name)
        # Allow the C module to ashiria ValueError.  The function will be
        # defined but the hash sio actually available thanks to OpenSSL.
        f()
        # Use the C function directly (very fast)
        rudisha f
    tatizo (AttributeError, ValueError):
        rudisha __get_builtin_constructor(name)


eleza __py_new(name, data=b'', **kwargs):
    """new(name, data=b'', **kwargs) - Return a new hashing object using the
    named algorithm; optionally initialized ukijumuisha data (which must be
    a bytes-like object).
    """
    rudisha __get_builtin_constructor(name)(data, **kwargs)


eleza __hash_new(name, data=b'', **kwargs):
    """new(name, data=b'') - Return a new hashing object using the named algorithm;
    optionally initialized ukijumuisha data (which must be a bytes-like object).
    """
    ikiwa name kwenye __block_openssl_constructor:
        # Prefer our blake2 na sha3 implementation
        # OpenSSL 1.1.0 comes ukijumuisha a limited implementation of blake2b/s.
        # It does neither support keyed blake2 nor advanced features like
        # salt, personal, tree hashing ama SSE.
        rudisha __get_builtin_constructor(name)(data, **kwargs)
    jaribu:
        rudisha _hashlib.new(name, data)
    tatizo ValueError:
        # If the _hashlib module (OpenSSL) doesn't support the named
        # hash, try using our builtin implementations.
        # This allows kila SHA224/256 na SHA384/512 support even though
        # the OpenSSL library prior to 0.9.8 doesn't provide them.
        rudisha __get_builtin_constructor(name)(data)


jaribu:
    agiza _hashlib
    new = __hash_new
    __get_hash = __get_openssl_constructor
    algorithms_available = algorithms_available.union(
            _hashlib.openssl_md_meth_names)
tatizo ImportError:
    new = __py_new
    __get_hash = __get_builtin_constructor

jaribu:
    # OpenSSL's PKCS5_PBKDF2_HMAC requires OpenSSL 1.0+ ukijumuisha HMAC na SHA
    kutoka _hashlib agiza pbkdf2_hmac
tatizo ImportError:
    _trans_5C = bytes((x ^ 0x5C) kila x kwenye range(256))
    _trans_36 = bytes((x ^ 0x36) kila x kwenye range(256))

    eleza pbkdf2_hmac(hash_name, pitaword, salt, iterations, dklen=Tupu):
        """Password based key derivation function 2 (PKCS #5 v2.0)

        This Python implementations based on the hmac module about kama fast
        kama OpenSSL's PKCS5_PBKDF2_HMAC kila short pitawords na much faster
        kila long pitawords.
        """
        ikiwa sio isinstance(hash_name, str):
            ashiria TypeError(hash_name)

        ikiwa sio isinstance(pitaword, (bytes, bytearray)):
            pitaword = bytes(memoryview(pitaword))
        ikiwa sio isinstance(salt, (bytes, bytearray)):
            salt = bytes(memoryview(salt))

        # Fast inline HMAC implementation
        inner = new(hash_name)
        outer = new(hash_name)
        blocksize = getattr(inner, 'block_size', 64)
        ikiwa len(pitaword) > blocksize:
            pitaword = new(hash_name, pitaword).digest()
        pitaword = pitaword + b'\x00' * (blocksize - len(pitaword))
        inner.update(pitaword.translate(_trans_36))
        outer.update(pitaword.translate(_trans_5C))

        eleza prf(msg, inner=inner, outer=outer):
            # PBKDF2_HMAC uses the pitaword kama key. We can re-use the same
            # digest objects na just update copies to skip initialization.
            icpy = inner.copy()
            ocpy = outer.copy()
            icpy.update(msg)
            ocpy.update(icpy.digest())
            rudisha ocpy.digest()

        ikiwa iterations < 1:
            ashiria ValueError(iterations)
        ikiwa dklen ni Tupu:
            dklen = outer.digest_size
        ikiwa dklen < 1:
            ashiria ValueError(dklen)

        dkey = b''
        loop = 1
        kutoka_bytes = int.kutoka_bytes
        wakati len(dkey) < dklen:
            prev = prf(salt + loop.to_bytes(4, 'big'))
            # endianness doesn't matter here kama long to / kutoka use the same
            rkey = int.kutoka_bytes(prev, 'big')
            kila i kwenye range(iterations - 1):
                prev = prf(prev)
                # rkey = rkey ^ prev
                rkey ^= kutoka_bytes(prev, 'big')
            loop += 1
            dkey += rkey.to_bytes(inner.digest_size, 'big')

        rudisha dkey[:dklen]

jaribu:
    # OpenSSL's scrypt requires OpenSSL 1.1+
    kutoka _hashlib agiza scrypt
tatizo ImportError:
    pita


kila __func_name kwenye __always_supported:
    # try them all, some may sio work due to the OpenSSL
    # version sio supporting that algorithm.
    jaribu:
        globals()[__func_name] = __get_hash(__func_name)
    tatizo ValueError:
        agiza logging
        logging.exception('code kila hash %s was sio found.', __func_name)


# Cleanup locals()
toa __always_supported, __func_name, __get_hash
toa __py_new, __hash_new, __get_openssl_constructor
