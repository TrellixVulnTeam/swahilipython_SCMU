#!/usr/local/bin/python3.8d
# -*- python -*-

# Keep this script kwenye sync ukijumuisha python-config.sh.in

agiza getopt
agiza os
agiza sys
agiza sysconfig

valid_opts = ['prefix', 'exec-prefix', 'includes', 'libs', 'cflags',
              'ldflags', 'extension-suffix', 'help', 'abiflags', 'configdir',
              'embed']

eleza exit_with_usage(code=1):
    andika("Usage: {0} [{1}]".format(
        sys.argv[0], '|'.join('--'+opt kila opt kwenye valid_opts)), file=sys.stderr)
    sys.exit(code)

jaribu:
    opts, args = getopt.getopt(sys.argv[1:], '', valid_opts)
tatizo getopt.error:
    exit_with_usage()

ikiwa sio opts:
    exit_with_usage()

pyver = sysconfig.get_config_var('VERSION')
getvar = sysconfig.get_config_var

opt_flags = [flag kila (flag, val) kwenye opts]

ikiwa '--help' kwenye opt_flags:
    exit_with_usage(code=0)

kila opt kwenye opt_flags:
    ikiwa opt == '--prefix':
        andika(sysconfig.get_config_var('prefix'))

    lasivyo opt == '--exec-prefix':
        andika(sysconfig.get_config_var('exec_prefix'))

    lasivyo opt kwenye ('--includes', '--cflags'):
        flags = ['-I' + sysconfig.get_path('include'),
                 '-I' + sysconfig.get_path('platinclude')]
        ikiwa opt == '--cflags':
            flags.extend(getvar('CFLAGS').split())
        andika(' '.join(flags))

    lasivyo opt kwenye ('--libs', '--ldflags'):
        libs = []
        ikiwa '--embed' kwenye opt_flags:
            libs.append('-lpython' + pyver + sys.abiflags)
        isipokua:
            libpython = getvar('LIBPYTHON')
            ikiwa libpython:
                libs.append(libpython)
        libs.extend(getvar('LIBS').split() + getvar('SYSLIBS').split())

        # add the prefix/lib/pythonX.Y/config dir, but only ikiwa there ni no
        # shared library kwenye prefix/lib/.
        ikiwa opt == '--ldflags':
            ikiwa sio getvar('Py_ENABLE_SHARED'):
                libs.insert(0, '-L' + getvar('LIBPL'))
        andika(' '.join(libs))

    lasivyo opt == '--extension-suffix':
        andika(sysconfig.get_config_var('EXT_SUFFIX'))

    lasivyo opt == '--abiflags':
        andika(sys.abiflags)

    lasivyo opt == '--configdir':
        andika(sysconfig.get_config_var('LIBPL'))
