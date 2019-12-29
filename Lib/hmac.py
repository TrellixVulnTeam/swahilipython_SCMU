"""HMAC (Keyed-Hashing kila Message Authentication) Python module.

Implements the HMAC algorithm kama described by RFC 2104.
"""

agiza warnings kama _warnings
kutoka _operator agiza _compare_digest kama compare_digest
jaribu:
    agiza _hashlib kama _hashopenssl
tatizo ImportError:
    _hashopenssl = Tupu
    _openssl_md_meths = Tupu
isipokua:
    _openssl_md_meths = frozenset(_hashopenssl.openssl_md_meth_names)
agiza hashlib kama _hashlib

trans_5C = bytes((x ^ 0x5C) kila x kwenye range(256))
trans_36 = bytes((x ^ 0x36) kila x kwenye range(256))

# The size of the digests rudishaed by HMAC depends on the underlying
# hashing module used.  Use digest_size kutoka the instance of HMAC instead.
digest_size = Tupu



kundi HMAC:
    """RFC 2104 HMAC class.  Also complies ukijumuisha RFC 4231.

    This supports the API kila Cryptographic Hash Functions (PEP 247).
    """
    blocksize = 64  # 512-bit HMAC; can be changed kwenye subclasses.

    eleza __init__(self, key, msg = Tupu, digestmod = Tupu):
        """Create a new HMAC object.

        key:       key kila the keyed hash object.
        msg:       Initial input kila the hash, ikiwa provided.
        digestmod: Required.  A module supporting PEP 247.  *OR*
                   A hashlib constructor rudishaing a new hash object.  *OR*
                   A hash name suitable kila hashlib.new().

        Note: key na msg must be a bytes ama bytearray objects.
        """

        ikiwa sio isinstance(key, (bytes, bytearray)):
            ashiria TypeError("key: expected bytes ama bytearray, but got %r" % type(key).__name__)

        ikiwa digestmod ni Tupu:
            ashiria ValueError('`digestmod` ni required.')

        ikiwa callable(digestmod):
            self.digest_cons = digestmod
        lasivyo isinstance(digestmod, str):
            self.digest_cons = lambda d=b'': _hashlib.new(digestmod, d)
        isipokua:
            self.digest_cons = lambda d=b'': digestmod.new(d)

        self.outer = self.digest_cons()
        self.inner = self.digest_cons()
        self.digest_size = self.inner.digest_size

        ikiwa hasattr(self.inner, 'block_size'):
            blocksize = self.inner.block_size
            ikiwa blocksize < 16:
                _warnings.warn('block_size of %d seems too small; using our '
                               'default of %d.' % (blocksize, self.blocksize),
                               RuntimeWarning, 2)
                blocksize = self.blocksize
        isipokua:
            _warnings.warn('No block_size attribute on given digest object; '
                           'Assuming %d.' % (self.blocksize),
                           RuntimeWarning, 2)
            blocksize = self.blocksize

        # self.blocksize ni the default blocksize. self.block_size is
        # effective block size kama well kama the public API attribute.
        self.block_size = blocksize

        ikiwa len(key) > blocksize:
            key = self.digest_cons(key).digest()

        key = key.ljust(blocksize, b'\0')
        self.outer.update(key.translate(trans_5C))
        self.inner.update(key.translate(trans_36))
        ikiwa msg ni sio Tupu:
            self.update(msg)

    @property
    eleza name(self):
        rudisha "hmac-" + self.inner.name

    eleza update(self, msg):
        """Update this hashing object ukijumuisha the string msg.
        """
        self.inner.update(msg)

    eleza copy(self):
        """Return a separate copy of this hashing object.

        An update to this copy won't affect the original object.
        """
        # Call __new__ directly to avoid the expensive __init__.
        other = self.__class__.__new__(self.__class__)
        other.digest_cons = self.digest_cons
        other.digest_size = self.digest_size
        other.inner = self.inner.copy()
        other.outer = self.outer.copy()
        rudisha other

    eleza _current(self):
        """Return a hash object kila the current state.

        To be used only internally ukijumuisha digest() na hexdigest().
        """
        h = self.outer.copy()
        h.update(self.inner.digest())
        rudisha h

    eleza digest(self):
        """Return the hash value of this hashing object.

        This rudishas a string containing 8-bit data.  The object is
        sio altered kwenye any way by this function; you can endelea
        updating the object after calling this function.
        """
        h = self._current()
        rudisha h.digest()

    eleza hexdigest(self):
        """Like digest(), but rudishas a string of hexadecimal digits instead.
        """
        h = self._current()
        rudisha h.hexdigest()

eleza new(key, msg = Tupu, digestmod = Tupu):
    """Create a new hashing object na rudisha it.

    key: The starting key kila the hash.
    msg: ikiwa available, will immediately be hashed into the object's starting
    state.

    You can now feed arbitrary strings into the object using its update()
    method, na can ask kila the hash value at any time by calling its digest()
    method.
    """
    rudisha HMAC(key, msg, digestmod)


eleza digest(key, msg, digest):
    """Fast inline implementation of HMAC

    key:    key kila the keyed hash object.
    msg:    input message
    digest: A hash name suitable kila hashlib.new() kila best performance. *OR*
            A hashlib constructor rudishaing a new hash object. *OR*
            A module supporting PEP 247.

    Note: key na msg must be a bytes ama bytearray objects.
    """
    ikiwa (_hashopenssl ni sio Tupu and
            isinstance(digest, str) na digest kwenye _openssl_md_meths):
        rudisha _hashopenssl.hmac_digest(key, msg, digest)

    ikiwa callable(digest):
        digest_cons = digest
    lasivyo isinstance(digest, str):
        digest_cons = lambda d=b'': _hashlib.new(digest, d)
    isipokua:
        digest_cons = lambda d=b'': digest.new(d)

    inner = digest_cons()
    outer = digest_cons()
    blocksize = getattr(inner, 'block_size', 64)
    ikiwa len(key) > blocksize:
        key = digest_cons(key).digest()
    key = key + b'\x00' * (blocksize - len(key))
    inner.update(key.translate(trans_36))
    outer.update(key.translate(trans_5C))
    inner.update(msg)
    outer.update(inner.digest())
    rudisha outer.digest()
