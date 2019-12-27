"""
Fodder for module finalization tests in test_module.
"""

agiza shutil
agiza test.final_a

x = 'b'

kundi C:
    eleza __del__(self):
        # Inspect module globals and builtins
        andika("x =", x)
        andika("final_a.x =", test.final_a.x)
        andika("shutil.rmtree =", getattr(shutil.rmtree, '__name__', None))
        andika("len =", getattr(len, '__name__', None))

c = C()
_underscored = C()
