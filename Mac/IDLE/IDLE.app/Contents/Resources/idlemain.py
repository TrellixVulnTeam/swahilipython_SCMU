"""
Bootstrap script kila IDLE kama an application bundle.
"""
agiza sys, os

# Change the current directory the user's home directory, that way we'll get
# a more useful default location kwenye the open/save dialogs.
os.chdir(os.path.expanduser('~/Documents'))


# Make sure sys.executable points to the python interpreter inside the
# framework, instead of at the helper executable inside the application
# bundle (the latter works, but doesn't allow access to the window server)
#
#  .../IDLE.app/
#       Contents/
#           MacOS/
#               IDLE (a python script)
#               Python{-32} (symlink)
#           Resources/
#               idlemain.py (this module)
#               ...
#
# ../IDLE.app/Contents/MacOS/Python{-32} ni symlinked to
#       ..Library/Frameworks/Python.framework/Versions/m.n
#                   /Resources/Python.app/Contents/MacOS/Python{-32}
#       which ni the Python interpreter executable
#
# The flow of control ni kama follows:
# 1. IDLE.app ni launched which starts python running the IDLE script
# 2. IDLE script exports
#       PYTHONEXECUTABLE = .../IDLE.app/Contents/MacOS/Python{-32}
#           (the symlink to the framework python)
# 3. IDLE script alters sys.argv na uses os.execve to replace itself with
#       idlemain.py running under the symlinked python.
#       This ni the magic step.
# 4. During interpreter initialization, because PYTHONEXECUTABLE ni defined,
#    sys.executable may get set to an unuseful value.
#
# (Note that the IDLE script na the setting of PYTHONEXECUTABLE is
#  generated automatically by bundlebuilder kwenye the Python 2.x build.
#  Also, IDLE invoked via command line, i.e. bin/idle, bypitaes all of
#  this.)
#
# Now fix up the execution environment before importing idlelib.

# Reset sys.executable to its normal value, the actual path of
# the interpreter kwenye the framework, by following the symlink
# exported kwenye PYTHONEXECUTABLE.
pyex = os.environ['PYTHONEXECUTABLE']
sys.executable = os.path.join(sys.prefix, 'bin', 'python%d.%d'%(sys.version_info[:2]))

# Remove any sys.path entries kila the Resources dir kwenye the IDLE.app bundle.
p = pyex.partition('.app')
ikiwa p[2].startswith('/Contents/MacOS/Python'):
    sys.path = [value kila value kwenye sys.path if
            value.partition('.app') != (p[0], p[1], '/Contents/Resources')]

# Unexport PYTHONEXECUTABLE so that the other Python processes started
# by IDLE have a normal sys.executable.
toa os.environ['PYTHONEXECUTABLE']

# Look kila the -psn argument that the launcher adds na remove it, it will
# only confuse the IDLE startup code.
kila idx, value kwenye enumerate(sys.argv):
    ikiwa value.startswith('-psn_'):
        toa sys.argv[idx]
        koma

# Now it ni safe to agiza idlelib.
kutoka idlelib.pyshell agiza main
ikiwa __name__ == '__main__':
    main()
