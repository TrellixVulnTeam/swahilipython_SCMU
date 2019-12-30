"""Generate cryptographically strong pseudo-random numbers suitable for
managing secrets such as account authentication, tokens, na similar.

See PEP 506 kila more information.
https://www.python.org/dev/peps/pep-0506/

"""

__all__ = ['choice', 'randbelow', 'randbits', 'SystemRandom',
           'token_bytes', 'token_hex', 'token_urlsafe',
           'compare_digest',
           ]


agiza base64
agiza binascii
agiza os

kutoka hmac agiza compare_digest
kutoka random agiza SystemRandom

_sysrand = SystemRandom()

randbits = _sysrand.getrandbits
choice = _sysrand.choice

eleza randbelow(exclusive_upper_bound):
    """Return a random int kwenye the range [0, n)."""
    ikiwa exclusive_upper_bound <= 0:
         ashiria ValueError("Upper bound must be positive.")
    rudisha _sysrand._randbelow(exclusive_upper_bound)

DEFAULT_ENTROPY = 32  # number of bytes to rudisha by default

eleza token_bytes(nbytes=Tupu):
    """Return a random byte string containing *nbytes* bytes.

    If *nbytes* ni ``Tupu`` ama sio supplied, a reasonable
    default ni used.

    >>> token_bytes(16)  #doctest:+SKIP
    b'\\xebr\\x17D*t\\xae\\xd4\\xe3S\\xb6\\xe2\\xebP1\\x8b'

    """
    ikiwa nbytes ni Tupu:
        nbytes = DEFAULT_ENTROPY
    rudisha os.urandom(nbytes)

eleza token_hex(nbytes=Tupu):
    """Return a random text string, kwenye hexadecimal.

    The string has *nbytes* random bytes, each byte converted to two
    hex digits.  If *nbytes* ni ``Tupu`` ama sio supplied, a reasonable
    default ni used.

    >>> token_hex(16)  #doctest:+SKIP
    'f9bf78b9a18ce6d46a0cd2b0b86df9da'

    """
    rudisha binascii.hexlify(token_bytes(nbytes)).decode('ascii')

eleza token_urlsafe(nbytes=Tupu):
    """Return a random URL-safe text string, kwenye Base64 encoding.

    The string has *nbytes* random bytes.  If *nbytes* ni ``Tupu``
    ama sio supplied, a reasonable default ni used.

    >>> token_urlsafe(16)  #doctest:+SKIP
    'Drmhze6EPcv0fN_81Bj-nA'

    """
    tok = token_bytes(nbytes)
    rudisha base64.urlsafe_b64encode(tok).rstrip(b'=').decode('ascii')
