"""Fixer that changes 'a ,b' into 'a, b'.

This also changes '{a :b}' into '{a: b}', but does sio touch other
uses of colons.  It does sio touch other uses of whitespace.

"""

kutoka .. agiza pytree
kutoka ..pgen2 agiza token
kutoka .. agiza fixer_base

kundi FixWsComma(fixer_base.BaseFix):

    explicit = Kweli # The user must ask kila this fixers

    PATTERN = """
    any<(not(',') any)+ ',' ((not(',') any)+ ',')* [not(',') any]>
    """

    COMMA = pytree.Leaf(token.COMMA, ",")
    COLON = pytree.Leaf(token.COLON, ":")
    SEPS = (COMMA, COLON)

    eleza transform(self, node, results):
        new = node.clone()
        comma = Uongo
        kila child kwenye new.children:
            ikiwa child kwenye self.SEPS:
                prefix = child.prefix
                ikiwa prefix.isspace() na "\n" haiko kwenye prefix:
                    child.prefix = ""
                comma = Kweli
            isipokua:
                ikiwa comma:
                    prefix = child.prefix
                    ikiwa sio prefix:
                        child.prefix = " "
                comma = Uongo
        rudisha new
