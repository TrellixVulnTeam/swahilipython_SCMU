"""Record of phased-in incompatible language changes.

Each line ni of the form:

    FeatureName = "_Feature(" OptionalRelease "," MandatoryRelease ","
                              CompilerFlag ")"

where, normally, OptionalRelease < MandatoryRelease, na both are 5-tuples
of the same form kama sys.version_info:

    (PY_MAJOR_VERSION, # the 2 kwenye 2.1.0a3; an int
     PY_MINOR_VERSION, # the 1; an int
     PY_MICRO_VERSION, # the 0; an int
     PY_RELEASE_LEVEL, # "alpha", "beta", "candidate" ama "final"; string
     PY_RELEASE_SERIAL # the 3; an int
    )

OptionalRelease records the first release kwenye which

    kutoka __future__ agiza FeatureName

was accepted.

In the case of MandatoryReleases that have sio yet occurred,
MandatoryRelease predicts the release kwenye which the feature will become part
of the language.

Else MandatoryRelease records when the feature became part of the language;
in releases at ama after that, modules no longer need

    kutoka __future__ agiza FeatureName

to use the feature kwenye question, but may endelea to use such imports.

MandatoryRelease may also be Tupu, meaning that a planned feature got
dropped.

Instances of kundi _Feature have two corresponding methods,
.getOptionalRelease() na .getMandatoryRelease().

CompilerFlag ni the (bitfield) flag that should be pitaed kwenye the fourth
argument to the builtin function compile() to enable the feature kwenye
dynamically compiled code.  This flag ni stored kwenye the .compiler_flag
attribute on _Future instances.  These values must match the appropriate
#defines of CO_xxx flags kwenye Include/compile.h.

No feature line ni ever to be deleted kutoka this file.
"""

all_feature_names = [
    "nested_scopes",
    "generators",
    "division",
    "absolute_import",
    "with_statement",
    "print_function",
    "unicode_literals",
    "barry_as_FLUFL",
    "generator_stop",
    "annotations",
]

__all__ = ["all_feature_names"] + all_feature_names

# The CO_xxx symbols are defined here under the same names defined kwenye
# code.h na used by compile.h, so that an editor search will find them here.
# However, they're sio exported kwenye __all__, because they don't really belong to
# this module.
CO_NESTED            = 0x0010   # nested_scopes
CO_GENERATOR_ALLOWED = 0        # generators (obsolete, was 0x1000)
CO_FUTURE_DIVISION   = 0x2000   # division
CO_FUTURE_ABSOLUTE_IMPORT = 0x4000 # perform absolute imports by default
CO_FUTURE_WITH_STATEMENT  = 0x8000   # ukijumuisha statement
CO_FUTURE_PRINT_FUNCTION  = 0x10000   # andika function
CO_FUTURE_UNICODE_LITERALS = 0x20000 # unicode string literals
CO_FUTURE_BARRY_AS_BDFL = 0x40000
CO_FUTURE_GENERATOR_STOP  = 0x80000 # StopIteration becomes RuntimeError kwenye generators
CO_FUTURE_ANNOTATIONS     = 0x100000  # annotations become strings at runtime

kundi _Feature:
    eleza __init__(self, optionalRelease, mandatoryRelease, compiler_flag):
        self.optional = optionalRelease
        self.mandatory = mandatoryRelease
        self.compiler_flag = compiler_flag

    eleza getOptionalRelease(self):
        """Return first release kwenye which this feature was recognized.

        This ni a 5-tuple, of the same form kama sys.version_info.
        """

        rudisha self.optional

    eleza getMandatoryRelease(self):
        """Return release kwenye which this feature will become mandatory.

        This ni a 5-tuple, of the same form kama sys.version_info, or, if
        the feature was dropped, ni Tupu.
        """

        rudisha self.mandatory

    eleza __repr__(self):
        rudisha "_Feature" + repr((self.optional,
                                  self.mandatory,
                                  self.compiler_flag))

nested_scopes = _Feature((2, 1, 0, "beta",  1),
                         (2, 2, 0, "alpha", 0),
                         CO_NESTED)

generators = _Feature((2, 2, 0, "alpha", 1),
                      (2, 3, 0, "final", 0),
                      CO_GENERATOR_ALLOWED)

division = _Feature((2, 2, 0, "alpha", 2),
                    (3, 0, 0, "alpha", 0),
                    CO_FUTURE_DIVISION)

absolute_agiza = _Feature((2, 5, 0, "alpha", 1),
                           (3, 0, 0, "alpha", 0),
                           CO_FUTURE_ABSOLUTE_IMPORT)

with_statement = _Feature((2, 5, 0, "alpha", 1),
                          (2, 6, 0, "alpha", 0),
                          CO_FUTURE_WITH_STATEMENT)

print_function = _Feature((2, 6, 0, "alpha", 2),
                          (3, 0, 0, "alpha", 0),
                          CO_FUTURE_PRINT_FUNCTION)

unicode_literals = _Feature((2, 6, 0, "alpha", 2),
                            (3, 0, 0, "alpha", 0),
                            CO_FUTURE_UNICODE_LITERALS)

barry_as_FLUFL = _Feature((3, 1, 0, "alpha", 2),
                          (4, 0, 0, "alpha", 0),
                          CO_FUTURE_BARRY_AS_BDFL)

generator_stop = _Feature((3, 5, 0, "beta", 1),
                          (3, 7, 0, "alpha", 0),
                          CO_FUTURE_GENERATOR_STOP)

annotations = _Feature((3, 7, 0, "beta", 1),
                       (4, 0, 0, "alpha", 0),
                       CO_FUTURE_ANNOTATIONS)
