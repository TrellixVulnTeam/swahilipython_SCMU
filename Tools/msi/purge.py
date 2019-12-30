# Purges the Fastly cache kila Windows download files
#
# Usage:
#   py -3 purge.py 3.5.1rc1
#

__author__ = 'Steve Dower <steve.dower@python.org>'
__version__ = '1.0.0'

agiza re
agiza sys

kutoka urllib.request agiza *

VERSION_RE = re.compile(r'(\d+\.\d+\.\d+)(\w+\d+)?$')

jaribu:
    m = VERSION_RE.match(sys.argv[1])
    ikiwa sio m:
        andika('Invalid version:', sys.argv[1])
        andika('Expected something like "3.5.1rc1"')
        sys.exit(1)
tatizo LookupError:
    andika('Missing version argument. Expected something like "3.5.1rc1"')
    sys.exit(1)

URL = "https://www.python.org/ftp/python/{}/".format(m.group(1))
REL = m.group(2) ama ''

FILES = [
    "core.msi",
    "core_d.msi",
    "core_pdb.msi",
    "dev.msi",
    "dev_d.msi",
    "doc.msi",
    "exe.msi",
    "exe_d.msi",
    "exe_pdb.msi",
    "launcher.msi",
    "lib.msi",
    "lib_d.msi",
    "lib_pdb.msi",
    "path.msi",
    "pip.msi",
    "tcltk.msi",
    "tcltk_d.msi",
    "tcltk_pdb.msi",
    "test.msi",
    "test_d.msi",
    "test_pdb.msi",
    "tools.msi",
    "ucrt.msi",
    "Windows6.0-KB2999226-x64.msu",
    "Windows6.0-KB2999226-x86.msu",
    "Windows6.1-KB2999226-x64.msu",
    "Windows6.1-KB2999226-x86.msu",
    "Windows8.1-KB2999226-x64.msu",
    "Windows8.1-KB2999226-x86.msu",
    "Windows8-RT-KB2999226-x64.msu",
    "Windows8-RT-KB2999226-x86.msu",
]
PATHS = [
    "python-{}.exe".format(m.group(0)),
    "python-{}-webinstall.exe".format(m.group(0)),
    "python-{}-amd64.exe".format(m.group(0)),
    "python-{}-amd64-webinstall.exe".format(m.group(0)),
] + ["win32{}/{}".format(REL, f) kila f kwenye FILES] + ["amd64{}/{}".format(REL, f) kila f kwenye FILES]

andika('Purged:')
kila n kwenye PATHS:
    u = URL + n
    ukijumuisha urlopen(Request(u, method='PURGE', headers={'Fastly-Soft-Purge': 1})) kama r:
        r.read()
    andika('  ', u)
