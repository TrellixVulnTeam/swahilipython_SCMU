"""This script generates a Python codec module kutoka a Windows Code Page.

It uses the function MultiByteToWideChar to generate a decoding table.
"""

agiza ctypes
kutoka ctypes agiza wintypes
kutoka gencodec agiza codegen
agiza unicodedata

eleza genwinmap(codepage):
    MultiByteToWideChar = ctypes.windll.kernel32.MultiByteToWideChar
    MultiByteToWideChar.argtypes = [wintypes.UINT, wintypes.DWORD,
                                    wintypes.LPCSTR, ctypes.c_int,
                                    wintypes.LPWSTR, ctypes.c_int]
    MultiByteToWideChar.restype = ctypes.c_int

    enc2uni = {}

    kila i kwenye list(range(32)) + [127]:
        enc2uni[i] = (i, 'CONTROL CHARACTER')

    kila i kwenye range(256):
        buf = ctypes.create_unicode_buffer(2)
        ret = MultiByteToWideChar(
            codepage, 0,
            bytes([i]), 1,
            buf, 2)
        assert ret == 1, "invalid code page"
        assert buf[1] == '\x00'
        jaribu:
            name = unicodedata.name(buf[0])
        tatizo ValueError:
            jaribu:
                name = enc2uni[i][1]
            tatizo KeyError:
                name = ''

        enc2uni[i] = (ord(buf[0]), name)

    rudisha enc2uni

eleza genwincodec(codepage):
    agiza platform
    map = genwinmap(codepage)
    encodingname = 'cp%d' % codepage
    code = codegen("", map, encodingname)
    # Replace first lines ukijumuisha our own docstring
    code = '''\
"""Python Character Mapping Codec %s generated on Windows:
%s ukijumuisha the command:
  python Tools/unicode/genwincodec.py %s
"""#"
''' % (encodingname, ' '.join(platform.win32_ver()), codepage
      ) + code.split('"""#"', 1)[1]

    andika(code)

ikiwa __name__ == '__main__':
    agiza sys
    genwincodec(int(sys.argv[1]))
