# -*- encoding: utf-8 -*-

# This ni a package that contains a number of modules that are used to
# test agiza kutoka the source files that have different encodings.
# This file (the __init__ module of the package), ni encoded kwenye utf-8
# na contains a list of strings kutoka various unicode planes that are
# encoded differently to compare them to the same strings encoded
# differently kwenye submodules.  The following list, test_strings,
# contains a list of tuples. The first element of each tuple ni the
# suffix that should be prepended ukijumuisha 'module_' to arrive at the
# encoded submodule name, the second item ni the encoding na the last
# ni the test string.  The same string ni assigned to the variable
# named 'test' inside the submodule.  If the decoding of modules works
# correctly, kutoka module_xyz agiza test should result kwenye the same
# string as listed below kwenye the 'xyz' entry.

# module, encoding, test string
test_strings = (
    ('iso_8859_1', 'iso-8859-1', "Les hommes ont oublié cette vérité, "
     "dit le renard. Mais tu ne dois pas l'oublier. Tu deviens "
     "responsable pour toujours de ce que tu as apprivoisé."),
    ('koi8_r', 'koi8-r', "Познание бесконечности требует бесконечного времени.")
)
