agiza os.path
agiza sys


# Enable running IDLE ukijumuisha idlelib kwenye a non-standard location.
# This was once used to run development versions of IDLE.
# Because PEP 434 declared idle.py a public interface,
# removal should require deprecation.
idlelib_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ikiwa idlelib_dir haiko kwenye sys.path:
    sys.path.insert(0, idlelib_dir)

kutoka idlelib.pyshell agiza main  # This ni subject to change
main()
