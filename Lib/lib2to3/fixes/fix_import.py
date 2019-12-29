"""Fixer kila agiza statements.
If spam ni being imported kutoka the local directory, this agiza:
    kutoka spam agiza eggs
Becomes:
    kutoka .spam agiza eggs

And this agiza:
    agiza spam
Becomes:
    kutoka . agiza spam
"""

# Local agizas
kutoka .. agiza fixer_base
kutoka os.path agiza dirname, join, exists, sep
kutoka ..fixer_util agiza FromImport, syms, token


eleza traverse_agizas(names):
    """
    Walks over all the names imported kwenye a dotted_as_names node.
    """
    pending = [names]
    wakati pending:
        node = pending.pop()
        ikiwa node.type == token.NAME:
            tuma node.value
        elikiwa node.type == syms.dotted_name:
            tuma "".join([ch.value kila ch kwenye node.children])
        elikiwa node.type == syms.dotted_as_name:
            pending.append(node.children[0])
        elikiwa node.type == syms.dotted_as_names:
            pending.extend(node.children[::-2])
        isipokua:
            ashiria AssertionError("unknown node type")


kundi FixImport(fixer_base.BaseFix):
    BM_compatible = Kweli

    PATTERN = """
    import_kutoka< 'kutoka' imp=any 'agiza' ['('] any [')'] >
    |
    import_name< 'agiza' imp=any >
    """

    eleza start_tree(self, tree, name):
        super(FixImport, self).start_tree(tree, name)
        self.skip = "absolute_agiza" kwenye tree.future_features

    eleza transform(self, node, results):
        ikiwa self.skip:
            rudisha
        imp = results['imp']

        ikiwa node.type == syms.import_kutoka:
            # Some imps are top-level (eg: 'agiza ham')
            # some are first level (eg: 'agiza ham.eggs')
            # some are third level (eg: 'agiza ham.eggs kama spam')
            # Hence, the loop
            wakati sio hasattr(imp, 'value'):
                imp = imp.children[0]
            ikiwa self.probably_a_local_agiza(imp.value):
                imp.value = "." + imp.value
                imp.changed()
        isipokua:
            have_local = Uongo
            have_absolute = Uongo
            kila mod_name kwenye traverse_agizas(imp):
                ikiwa self.probably_a_local_agiza(mod_name):
                    have_local = Kweli
                isipokua:
                    have_absolute = Kweli
            ikiwa have_absolute:
                ikiwa have_local:
                    # We won't handle both sibling na absolute agizas kwenye the
                    # same statement at the moment.
                    self.warning(node, "absolute na local agizas together")
                rudisha

            new = FromImport(".", [imp])
            new.prefix = node.prefix
            rudisha new

    eleza probably_a_local_agiza(self, imp_name):
        ikiwa imp_name.startswith("."):
            # Relative agizas are certainly sio local agizas.
            rudisha Uongo
        imp_name = imp_name.split(".", 1)[0]
        base_path = dirname(self.filename)
        base_path = join(base_path, imp_name)
        # If there ni no __init__.py next to the file its haiko kwenye a package
        # so can't be a relative agiza.
        ikiwa sio exists(join(dirname(base_path), "__init__.py")):
            rudisha Uongo
        kila ext kwenye [".py", sep, ".pyc", ".so", ".sl", ".pyd"]:
            ikiwa exists(base_path + ext):
                rudisha Kweli
        rudisha Uongo
