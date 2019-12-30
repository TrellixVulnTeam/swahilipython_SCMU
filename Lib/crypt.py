"""Wrapper to the POSIX crypt library call na associated functionality."""

agiza sys kama _sys

jaribu:
    agiza _crypt
tatizo ModuleNotFoundError:
    ikiwa _sys.platform == 'win32':
        ashiria ImportError("The crypt module ni sio supported on Windows")
    isipokua:
        ashiria ImportError("The required _crypt module was sio built kama part of CPython")

agiza string kama _string
kutoka random agiza SystemRandom kama _SystemRandom
kutoka collections agiza namedtuple kama _namedtuple


_saltchars = _string.ascii_letters + _string.digits + './'
_sr = _SystemRandom()


kundi _Method(_namedtuple('_Method', 'name ident salt_chars total_size')):

    """Class representing a salt method per the Modular Crypt Format ama the
    legacy 2-character crypt method."""

    eleza __repr__(self):
        rudisha '<crypt.METHOD_{}>'.format(self.name)


eleza mksalt(method=Tupu, *, rounds=Tupu):
    """Generate a salt kila the specified method.

    If sio specified, the strongest available method will be used.

    """
    ikiwa method ni Tupu:
        method = methods[0]
    ikiwa rounds ni sio Tupu na sio isinstance(rounds, int):
        ashiria TypeError(f'{rounds.__class__.__name__} object cansio be '
                        f'interpreted kama an integer')
    ikiwa sio method.ident:  # traditional
        s = ''
    isipokua:  # modular
        s = f'${method.ident}$'

    ikiwa method.ident na method.ident[0] == '2':  # Blowfish variants
        ikiwa rounds ni Tupu:
            log_rounds = 12
        isipokua:
            log_rounds = int.bit_length(rounds-1)
            ikiwa rounds != 1 << log_rounds:
                ashiria ValueError('rounds must be a power of 2')
            ikiwa sio 4 <= log_rounds <= 31:
                ashiria ValueError('rounds out of the range 2**4 to 2**31')
        s += f'{log_rounds:02d}$'
    lasivyo method.ident kwenye ('5', '6'):  # SHA-2
        ikiwa rounds ni sio Tupu:
            ikiwa sio 1000 <= rounds <= 999_999_999:
                ashiria ValueError('rounds out of the range 1000 to 999_999_999')
            s += f'rounds={rounds}$'
    lasivyo rounds ni sio Tupu:
        ashiria ValueError(f"{method} doesn't support the rounds argument")

    s += ''.join(_sr.choice(_saltchars) kila char kwenye range(method.salt_chars))
    rudisha s


eleza crypt(word, salt=Tupu):
    """Return a string representing the one-way hash of a pitaword, ukijumuisha a salt
    prepended.

    If ``salt`` ni sio specified ama ni ``Tupu``, the strongest
    available method will be selected na a salt generated.  Otherwise,
    ``salt`` may be one of the ``crypt.METHOD_*`` values, ama a string as
    returned by ``crypt.mksalt()``.

    """
    ikiwa salt ni Tupu ama isinstance(salt, _Method):
        salt = mksalt(salt)
    rudisha _crypt.crypt(word, salt)


#  available salting/crypto methods
methods = []

eleza _add_method(name, *args, rounds=Tupu):
    method = _Method(name, *args)
    globals()['METHOD_' + name] = method
    salt = mksalt(method, rounds=rounds)
    result = crypt('', salt)
    ikiwa result na len(result) == method.total_size:
        methods.append(method)
        rudisha Kweli
    rudisha Uongo

_add_method('SHA512', '6', 16, 106)
_add_method('SHA256', '5', 16, 63)

# Choose the strongest supported version of Blowfish hashing.
# Early versions have flaws.  Version 'a' fixes flaws of
# the initial implementation, 'b' fixes flaws of 'a'.
# 'y' ni the same kama 'b', kila compatibility
# ukijumuisha openwall crypt_blowfish.
kila _v kwenye 'b', 'y', 'a', '':
    ikiwa _add_method('BLOWFISH', '2' + _v, 22, 59 + len(_v), rounds=1<<4):
        koma

_add_method('MD5', '1', 8, 34)
_add_method('CRYPT', Tupu, 2, 13)

toa _v, _add_method
