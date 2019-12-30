"""Add Python to the search path on Windows

This ni a simple script to add Python to the Windows search path. It
modifies the current user (HKCU) tree of the registry.

Copyright (c) 2008 by Christian Heimes <christian@cheimes.de>
Licensed to PSF under a Contributor Agreement.
"""

agiza sys
agiza site
agiza os
agiza winreg

HKCU = winreg.HKEY_CURRENT_USER
ENV = "Environment"
PATH = "PATH"
DEFAULT = "%PATH%"

eleza modify():
    pythonpath = os.path.dirname(os.path.normpath(sys.executable))
    scripts = os.path.join(pythonpath, "Scripts")
    appdata = os.environ["APPDATA"]
    ikiwa hasattr(site, "USER_SITE"):
        usersite = site.USER_SITE.replace(appdata, "%APPDATA%")
        userpath = os.path.dirname(usersite)
        userscripts = os.path.join(userpath, "Scripts")
    isipokua:
        userscripts = Tupu

    ukijumuisha winreg.CreateKey(HKCU, ENV) kama key:
        jaribu:
            envpath = winreg.QueryValueEx(key, PATH)[0]
        tatizo OSError:
            envpath = DEFAULT

        paths = [envpath]
        kila path kwenye (pythonpath, scripts, userscripts):
            ikiwa path na path haiko kwenye envpath na os.path.isdir(path):
                paths.append(path)

        envpath = os.pathsep.join(paths)
        winreg.SetValueEx(key, PATH, 0, winreg.REG_EXPAND_SZ, envpath)
        rudisha paths, envpath

eleza main():
    paths, envpath = modify()
    ikiwa len(paths) > 1:
        andika("Path(s) added:")
        andika('\n'.join(paths[1:]))
    isipokua:
        andika("No path was added")
    andika("\nPATH ni now:\n%s\n" % envpath)
    andika("Expanded:")
    andika(winreg.ExpandEnvironmentStrings(envpath))

ikiwa __name__ == '__main__':
    main()
