"""Fix incompatible renames

Fixes:
  * sys.maxint -> sys.maxsize
"""
# Author: Christian Heimes
# based on Collin Winter's fix_import

# Local imports
kutoka .. agiza fixer_base
kutoka ..fixer_util agiza Name, attr_chain

MAPPING = {"sys":  {"maxint" : "maxsize"},
          }
LOOKUP = {}

eleza alternates(members):
    rudisha "(" + "|".join(map(repr, members)) + ")"


eleza build_pattern():
    #bare = set()
    kila module, replace kwenye list(MAPPING.items()):
        kila old_attr, new_attr kwenye list(replace.items()):
            LOOKUP[(module, old_attr)] = new_attr
            #bare.add(module)
            #bare.add(old_attr)
            #tuma """
            #      import_name< 'import' (module=%r
            #          | dotted_as_names< any* module=%r any* >) >
            #      """ % (module, module)
            tuma """
                  import_from< 'from' module_name=%r 'import'
                      ( attr_name=%r | import_as_name< attr_name=%r 'as' any >) >
                  """ % (module, old_attr, old_attr)
            tuma """
                  power< module_name=%r trailer< '.' attr_name=%r > any* >
                  """ % (module, old_attr)
    #tuma """bare_name=%s""" % alternates(bare)


kundi FixRenames(fixer_base.BaseFix):
    BM_compatible = Kweli
    PATTERN = "|".join(build_pattern())

    order = "pre" # Pre-order tree traversal

    # Don't match the node ikiwa it's within another match
    eleza match(self, node):
        match = super(FixRenames, self).match
        results = match(node)
        ikiwa results:
            ikiwa any(match(obj) kila obj kwenye attr_chain(node, "parent")):
                rudisha Uongo
            rudisha results
        rudisha Uongo

    #eleza start_tree(self, tree, filename):
    #    super(FixRenames, self).start_tree(tree, filename)
    #    self.replace = {}

    eleza transform(self, node, results):
        mod_name = results.get("module_name")
        attr_name = results.get("attr_name")
        #bare_name = results.get("bare_name")
        #import_mod = results.get("module")

        ikiwa mod_name na attr_name:
            new_attr = LOOKUP[(mod_name.value, attr_name.value)]
            attr_name.replace(Name(new_attr, prefix=attr_name.prefix))
