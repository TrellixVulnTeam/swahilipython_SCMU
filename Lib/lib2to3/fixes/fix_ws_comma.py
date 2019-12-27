"""Fixer that changes 'a ,b' into 'a, b'.

This also changes '{a :b}' into '{a: b}', but does not touch other
uses of colons.  It does not touch other uses of whitespace.

"""

kutoka .. agiza pytree
kutoka ..pgen2 agiza token
kutoka .. agiza fixer_base

kundi FixWsComma(fixer_base.BaseFix):

    explicit = True # The user must ask for this fixers

    PATTERN = """
    any<(not(',') any)+ ',' ((not(',') any)+ ',')* [not(',') any]>
    """

    COMMA = pytree.Leaf(token.COMMA, ",")
    COLON = pytree.Leaf(token.COLON, ":")
    SEPS = (COMMA, COLON)

    eleza transform(self, node, results):
        new = node.clone()
        comma = False
        for child in new.children:
            ikiwa child in self.SEPS:
                prefix = child.prefix
                ikiwa prefix.isspace() and "\n" not in prefix:
                    child.prefix = ""
                comma = True
            else:
                ikiwa comma:
                    prefix = child.prefix
                    ikiwa not prefix:
                        child.prefix = " "
                comma = False
        rudisha new
