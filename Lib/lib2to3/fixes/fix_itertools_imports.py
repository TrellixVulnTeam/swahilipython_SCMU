""" Fixer for agizas of itertools.(imap|ifilter|izip|ifilterfalse) """

# Local agizas
kutoka lib2to3 agiza fixer_base
kutoka lib2to3.fixer_util agiza BlankLine, syms, token


class FixItertoolsImports(fixer_base.BaseFix):
    BM_compatible = True
    PATTERN = """
              import_from< 'from' 'itertools' 'agiza' agizas=any >
              """ %(locals())

    def transform(self, node, results):
        agizas = results['agizas']
        if agizas.type == syms.import_as_name or not agizas.children:
            children = [agizas]
        else:
            children = agizas.children
        for child in children[::2]:
            if child.type == token.NAME:
                member = child.value
                name_node = child
            elif child.type == token.STAR:
                # Just leave the agiza as is.
                return
            else:
                assert child.type == syms.import_as_name
                name_node = child.children[0]
            member_name = name_node.value
            if member_name in ('imap', 'izip', 'ifilter'):
                child.value = None
                child.remove()
            elif member_name in ('ifilterfalse', 'izip_longest'):
                node.changed()
                name_node.value = ('filterfalse' if member_name[1] == 'f'
                                   else 'zip_longest')

        # Make sure the agiza statement is still sane
        children = agizas.children[:] or [agizas]
        remove_comma = True
        for child in children:
            if remove_comma and child.type == token.COMMA:
                child.remove()
            else:
                remove_comma ^= True

        while children and children[-1].type == token.COMMA:
            children.pop().remove()

        # If there are no agizas left, just get rid of the entire statement
        if (not (agizas.children or getattr(agizas, 'value', None)) or
            agizas.parent is None):
            p = node.prefix
            node = BlankLine()
            node.prefix = p
            return node
