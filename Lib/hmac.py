"""HMAC (Keyed-Hashing for Message Authentication) Python module.

Implements the HMAC algorithm as described by RFC 2104.
"""

agiza warnings as _warnings
kutoka _operator agiza _compare_digest as compare_digest
try:
    agiza _hashlib as _hashopenssl
except ImportError:
    _hashopenssl = None
    _openssl_md_meths = None
else:
    _openssl_md_meths = frozenset(_hashopenssl.openssl_md_meth_names)
agiza hashlib as _hashlib

trans_5C = bytes((x ^ 0x5C) for x in range(256))
trans_36 = bytes((x ^ 0x36) for x in range(256))

# The size of the digests returned by HMAC depends on the underlying
# hashing module used.  Use digest_size kutoka the instance of HMAC instead.
digest_size = None



kundi HMAC:
    """RFC 2104 HMAC class.  Also complies with RFC 4231.

    This supports the API for Cryptographic Hash Functions (PEP 247).
    """
    blocksize = 64  # 512-bit HMAC; can be changed in subclasses.

    eleza __init__(self, key, msg = None, digestmod = None):
        """Create a new HMAC object.

        key:       key for the keyed hash object.
        msg:       Initial input for the hash, ikiwa provided.
        digestmod: Required.  A module supporting PEP 247.  *OR*
                   A hashlib constructor returning a new hash object.  *OR*
                   A hash name suitable for hashlib.new().

        Note: key and msg must be a bytes or bytearray objects.
        """

        ikiwa not isinstance(key, (bytes, bytearray)):
            raise TypeError("key: expected bytes or bytearray, but got %r" % type(key).__name__)

        ikiwa digestmod is None:
            raise ValueError('`digestmod` is required.')

        ikiwa callable(digestmod):
            self.digest_cons = digestmod
        elikiwa isinstance(digestmod, str):
            self.digest_cons = lambda d=b'': _hashlib.new(digestmod, d)
        else:
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
        else:
            _warnings.warn('No block_size attribute on given digest object; '
                           'Assuming %d.' % (self.blocksize),
                           RuntimeWarning, 2)
            blocksize = self.blocksize

        # self.blocksize is the default blocksize. self.block_size is
        # effective block size as well as the public API attribute.
        self.block_size = blocksize

        ikiwa len(key) > blocksize:
            key = self.digest_cons(key).digest()

        key = key.ljust(blocksize, b'\0')
        self.outer.update(key.translate(trans_5C))
        self.inner.update(key.translate(trans_36))
        ikiwa msg is not None:
            self.update(msg)

    @property
    eleza name(self):
        rudisha "hmac-" + self.inner.name

    eleza update(self, msg):
        """Update this hashing object with the string msg.
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
        """Return a hash object for the current state.

        To be used only internally with digest() and hexdigest().
        """
        h = self.outer.copy()
        h.update(self.inner.digest())
        rudisha h

    eleza digest(self):
        """Return the hash value of this hashing object.

        This returns a string containing 8-bit data.  The object is
        not altered in any way by this function; you can continue
        updating the object after calling this function.
        """
        h = self._current()
        rudisha h.digest()

    eleza hexdigest(self):
        """Like digest(), but returns a string of hexadecimal digits instead.
        """
        h = self._current()
        rudisha h.hexdigest()

eleza new(key, msg = None, digestmod = None):
    """Create a new hashing object and rudisha it.

    key: The starting key for the hash.
    msg: ikiwa available, will immediately be hashed into the object's starting
    state.

    You can now feed arbitrary strings into the object using its update()
    method, and can ask for the hash value at any time by calling its digest()
    method.
    """
    rudisha HMAC(key, msg, digestmod)


eleza digest(key, msg, digest):
    """Fast inline implementation of HMAC

    key:    key for the keyed hash object.
    msg:    input message
    digest: A hash name suitable for hashlib.new() for best performance. *OR*
            A hashlib constructor returning a new hash object. *OR*
            A module supporting PEP 247.

    Note: key and msg must be a bytes or bytearray objects.
    """
    ikiwa (_hashopenssl is not None and
            isinstance(digest, str) and digest in _openssl_md_meths):
        rudisha _hashopenssl.hmac_digest(key, msg, digest)

    ikiwa callable(digest):
        digest_cons = digest
    elikiwa isinstance(digest, str):
        digest_cons = lambda d=b'': _hashlib.new(digest, d)
    else:
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
