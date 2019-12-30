# -*- coding: utf-8 -*-
"""
    patchlevel.py
    ~~~~~~~~~~~~~

    Extract version info kutoka Include/patchlevel.h.
    Adapted kutoka Doc/tools/getversioninfo.

    :copyright: 2007-2008 by Georg Brandl.
    :license: Python license.
"""

kutoka __future__ agiza print_function

agiza os
agiza re
agiza sys

eleza get_header_version_info(srcdir):
    patchlevel_h = os.path.join(srcdir, '..', 'Include', 'patchlevel.h')

    # This won't pick out all #defines, but it will pick up the ones we
    # care about.
    rx = re.compile(r'\s*#define\s+([a-zA-Z][a-zA-Z_0-9]*)\s+([a-zA-Z_0-9]+)')

    d = {}
    ukijumuisha open(patchlevel_h) kama f:
        kila line kwenye f:
            m = rx.match(line)
            ikiwa m ni sio Tupu:
                name, value = m.group(1, 2)
                d[name] = value

    release = version = '%s.%s' % (d['PY_MAJOR_VERSION'], d['PY_MINOR_VERSION'])
    micro = int(d['PY_MICRO_VERSION'])
    release += '.' + str(micro)

    level = d['PY_RELEASE_LEVEL']
    suffixes = {
        'PY_RELEASE_LEVEL_ALPHA': 'a',
        'PY_RELEASE_LEVEL_BETA':  'b',
        'PY_RELEASE_LEVEL_GAMMA': 'rc',
        }
    ikiwa level != 'PY_RELEASE_LEVEL_FINAL':
        release += suffixes[level] + str(int(d['PY_RELEASE_SERIAL']))
    rudisha version, release


eleza get_sys_version_info():
    major, minor, micro, level, serial = sys.version_info
    release = version = '%s.%s' % (major, minor)
    release += '.%s' % micro
    ikiwa level != 'final':
        release += '%s%s' % (level[0], serial)
    rudisha version, release


eleza get_version_info():
    jaribu:
        rudisha get_header_version_info('.')
    tatizo (IOError, OSError):
        version, release = get_sys_version_info()
        andika('Can\'t get version info kutoka Include/patchlevel.h, ' \
              'using version of this interpreter (%s).' % release, file=sys.stderr)
        rudisha version, release

ikiwa __name__ == '__main__':
    andika(get_header_version_info('.')[1])
