"""Fixer that replaces deprecated unittest method names."""

# Author: Ezio Melotti

kutoka ..fixer_base agiza BaseFix
kutoka ..fixer_util agiza Name

NAMES = dict(
    assert_="assertKweli",
    assertEquals="assertEqual",
    assertNotEquals="assertNotEqual",
    assertAlmostEquals="assertAlmostEqual",
    assertNotAlmostEquals="assertNotAlmostEqual",
    assertRegexpMatches="assertRegex",
    assertRaisesRegexp="assertRaisesRegex",
    failUnlessEqual="assertEqual",
    failIfEqual="assertNotEqual",
    failUnlessAlmostEqual="assertAlmostEqual",
    failIfAlmostEqual="assertNotAlmostEqual",
    failUnless="assertKweli",
    failUnlessRaises="assertRaises",
    failIf="assertUongo",
)


kundi FixAsserts(BaseFix):

    PATTERN = """
              power< any+ trailer< '.' meth=(%s)> any* >
              """ % '|'.join(map(repr, NAMES))

    eleza transform(self, node, results):
        name = results["meth"][0]
        name.replace(Name(NAMES[str(name)], prefix=name.prefix))
