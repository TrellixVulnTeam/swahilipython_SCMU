r"""Fixer for unicode.

* Changes unicode to str and unichr to chr.

* If "...\u..." is not unicode literal change it into "...\\u...".

* Change u"..." into "...".

"""

kutoka ..pgen2 agiza token
kutoka .. agiza fixer_base

_mapping = {"unichr" : "chr", "unicode" : "str"}

kundi FixUnicode(fixer_base.BaseFix):
    BM_compatible = True
    PATTERN = "STRING | 'unicode' | 'unichr'"

    eleza start_tree(self, tree, filename):
        super(FixUnicode, self).start_tree(tree, filename)
        self.unicode_literals = 'unicode_literals' in tree.future_features

    eleza transform(self, node, results):
        ikiwa node.type == token.NAME:
            new = node.clone()
            new.value = _mapping[node.value]
            rudisha new
        elikiwa node.type == token.STRING:
            val = node.value
            ikiwa not self.unicode_literals and val[0] in '\'"' and '\\' in val:
                val = r'\\'.join([
                    v.replace('\\u', r'\\u').replace('\\U', r'\\U')
                    for v in val.split(r'\\')
                ])
            ikiwa val[0] in 'uU':
                val = val[1:]
            ikiwa val == node.value:
                rudisha node
            new = node.clone()
            new.value = val
            rudisha new
