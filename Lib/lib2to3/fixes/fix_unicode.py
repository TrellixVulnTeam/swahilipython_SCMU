r"""Fixer kila unicode.

* Changes unicode to str na unichr to chr.

* If "...\u..." ni sio unicode literal change it into "...\\u...".

* Change u"..." into "...".

"""

kutoka ..pgen2 agiza token
kutoka .. agiza fixer_base

_mapping = {"unichr" : "chr", "unicode" : "str"}

kundi FixUnicode(fixer_base.BaseFix):
    BM_compatible = Kweli
    PATTERN = "STRING | 'unicode' | 'unichr'"

    eleza start_tree(self, tree, filename):
        super(FixUnicode, self).start_tree(tree, filename)
        self.unicode_literals = 'unicode_literals' kwenye tree.future_features

    eleza transform(self, node, results):
        ikiwa node.type == token.NAME:
            new = node.clone()
            new.value = _mapping[node.value]
            rudisha new
        lasivyo node.type == token.STRING:
            val = node.value
            ikiwa sio self.unicode_literals na val[0] kwenye '\'"' na '\\' kwenye val:
                val = r'\\'.join([
                    v.replace('\\u', r'\\u').replace('\\U', r'\\U')
                    kila v kwenye val.split(r'\\')
                ])
            ikiwa val[0] kwenye 'uU':
                val = val[1:]
            ikiwa val == node.value:
                rudisha node
            new = node.clone()
            new.value = val
            rudisha new
