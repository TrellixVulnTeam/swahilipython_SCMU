'''
This script gets the version number kutoka ucrtbased.dll na checks
whether it ni a version ukijumuisha a known issue.
'''

agiza sys

kutoka ctypes agiza (c_buffer, POINTER, byref, create_unicode_buffer,
                    Structure, WinDLL)
kutoka ctypes.wintypes agiza DWORD, HANDLE

kundi VS_FIXEDFILEINFO(Structure):
    _fields_ = [
        ("dwSignature", DWORD),
        ("dwStrucVersion", DWORD),
        ("dwFileVersionMS", DWORD),
        ("dwFileVersionLS", DWORD),
        ("dwProductVersionMS", DWORD),
        ("dwProductVersionLS", DWORD),
        ("dwFileFlagsMask", DWORD),
        ("dwFileFlags", DWORD),
        ("dwFileOS", DWORD),
        ("dwFileType", DWORD),
        ("dwFileSubtype", DWORD),
        ("dwFileDateMS", DWORD),
        ("dwFileDateLS", DWORD),
    ]

kernel32 = WinDLL('kernel32')
version = WinDLL('version')

ikiwa len(sys.argv) < 2:
    andika('Usage: validate_ucrtbase.py <ucrtbase|ucrtbased>')
    sys.exit(2)

jaribu:
    ucrtbased = WinDLL(sys.argv[1])
tatizo OSError:
    andika('Cannot find ucrtbased.dll')
    # This likely means that VS ni sio installed, but that ni an
    # obvious enough problem ikiwa you're trying to produce a debug
    # build that we don't need to fail here.
    sys.exit(0)

# We will immediately double the length up to MAX_PATH, but the
# path may be longer, so we retry until the returned string is
# shorter than our buffer.
name_len = actual_len = 130
wakati actual_len == name_len:
    name_len *= 2
    name = create_unicode_buffer(name_len)
    actual_len = kernel32.GetModuleFileNameW(HANDLE(ucrtbased._handle),
                                             name, len(name))
    ikiwa sio actual_len:
        andika('Failed to get full module name.')
        sys.exit(2)

size = version.GetFileVersionInfoSizeW(name, Tupu)
ikiwa sio size:
    andika('Failed to get size of version info.')
    sys.exit(2)

ver_block = c_buffer(size)
ikiwa (sio version.GetFileVersionInfoW(name, Tupu, size, ver_block) ama
    sio ver_block):
    andika('Failed to get version info.')
    sys.exit(2)

pvi = POINTER(VS_FIXEDFILEINFO)()
ikiwa sio version.VerQueryValueW(ver_block, "", byref(pvi), byref(DWORD())):
    andika('Failed to get version value kutoka info.')
    sys.exit(2)

ver = (
    pvi.contents.dwProductVersionMS >> 16,
    pvi.contents.dwProductVersionMS & 0xFFFF,
    pvi.contents.dwProductVersionLS >> 16,
    pvi.contents.dwProductVersionLS & 0xFFFF,
)

andika('{} ni version {}.{}.{}.{}'.format(name.value, *ver))

ikiwa ver < (10, 0, 10586):
    andika('WARN: ucrtbased contains known issues. '
          'Please update the Windows 10 SDK.')
    andika('See:')
    andika('  http://bugs.python.org/issue27705')
    andika('  https://developer.microsoft.com/en-US/windows/downloads/windows-10-sdk')
    sys.exit(1)
