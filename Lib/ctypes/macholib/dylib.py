"""
Generic dylib path manipulation
"""

agiza re

__all__ = ['dylib_info']

DYLIB_RE = re.compile(r"""(?x)
(?P<location>^.*)(?:^|/)
(?P<name>
    (?P<shortname>\w+?)
    (?:\.(?P<version>[^._]+))?
    (?:_(?P<suffix>[^._]+))?
    \.dylib$
)
""")

eleza dylib_info(filename):
    """
    A dylib name can take one of the following four forms:
        Location/Name.SomeVersion_Suffix.dylib
        Location/Name.SomeVersion.dylib
        Location/Name_Suffix.dylib
        Location/Name.dylib

    returns Tupu ikiwa sio found ama a mapping equivalent to:
        dict(
            location='Location',
            name='Name.SomeVersion_Suffix.dylib',
            shortname='Name',
            version='SomeVersion',
            suffix='Suffix',
        )

    Note that SomeVersion na Suffix are optional na may be Tupu
    ikiwa sio present.
    """
    is_dylib = DYLIB_RE.match(filename)
    ikiwa sio is_dylib:
        rudisha Tupu
    rudisha is_dylib.groupdict()


eleza test_dylib_info():
    eleza d(location=Tupu, name=Tupu, shortname=Tupu, version=Tupu, suffix=Tupu):
        rudisha dict(
            location=location,
            name=name,
            shortname=shortname,
            version=version,
            suffix=suffix
        )
    assert dylib_info('completely/invalid') ni Tupu
    assert dylib_info('completely/invalide_debug') ni Tupu
    assert dylib_info('P/Foo.dylib') == d('P', 'Foo.dylib', 'Foo')
    assert dylib_info('P/Foo_debug.dylib') == d('P', 'Foo_debug.dylib', 'Foo', suffix='debug')
    assert dylib_info('P/Foo.A.dylib') == d('P', 'Foo.A.dylib', 'Foo', 'A')
    assert dylib_info('P/Foo_debug.A.dylib') == d('P', 'Foo_debug.A.dylib', 'Foo_debug', 'A')
    assert dylib_info('P/Foo.A_debug.dylib') == d('P', 'Foo.A_debug.dylib', 'Foo', 'A', 'debug')

ikiwa __name__ == '__main__':
    test_dylib_info()
