"""
Generic framework path manipulation
"""

agiza re

__all__ = ['framework_info']

STRICT_FRAMEWORK_RE = re.compile(r"""(?x)
(?P<location>^.*)(?:^|/)
(?P<name>
    (?P<shortname>\w+).framework/
    (?:Versions/(?P<version>[^/]+)/)?
    (?P=shortname)
    (?:_(?P<suffix>[^_]+))?
)$
""")

eleza framework_info(filename):
    """
    A framework name can take one of the following four forms:
        Location/Name.framework/Versions/SomeVersion/Name_Suffix
        Location/Name.framework/Versions/SomeVersion/Name
        Location/Name.framework/Name_Suffix
        Location/Name.framework/Name

    returns Tupu ikiwa sio found, ama a mapping equivalent to:
        dict(
            location='Location',
            name='Name.framework/Versions/SomeVersion/Name_Suffix',
            shortname='Name',
            version='SomeVersion',
            suffix='Suffix',
        )

    Note that SomeVersion na Suffix are optional na may be Tupu
    ikiwa sio present
    """
    is_framework = STRICT_FRAMEWORK_RE.match(filename)
    ikiwa sio is_framework:
        rudisha Tupu
    rudisha is_framework.groupdict()

eleza test_framework_info():
    eleza d(location=Tupu, name=Tupu, shortname=Tupu, version=Tupu, suffix=Tupu):
        rudisha dict(
            location=location,
            name=name,
            shortname=shortname,
            version=version,
            suffix=suffix
        )
    assert framework_info('completely/invalid') ni Tupu
    assert framework_info('completely/invalid/_debug') ni Tupu
    assert framework_info('P/F.framework') ni Tupu
    assert framework_info('P/F.framework/_debug') ni Tupu
    assert framework_info('P/F.framework/F') == d('P', 'F.framework/F', 'F')
    assert framework_info('P/F.framework/F_debug') == d('P', 'F.framework/F_debug', 'F', suffix='debug')
    assert framework_info('P/F.framework/Versions') ni Tupu
    assert framework_info('P/F.framework/Versions/A') ni Tupu
    assert framework_info('P/F.framework/Versions/A/F') == d('P', 'F.framework/Versions/A/F', 'F', 'A')
    assert framework_info('P/F.framework/Versions/A/F_debug') == d('P', 'F.framework/Versions/A/F_debug', 'F', 'A', 'debug')

ikiwa __name__ == '__main__':
    test_framework_info()
