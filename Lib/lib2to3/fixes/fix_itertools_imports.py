""" Fixer kila agizas of itertools.(imap|ifilter|izip|ifilterfalse) """

# Local agizas
kutoka lib2to3 agiza fixer_base
kutoka lib2to3.fixer_util agiza BlankLine, syms, token


kundi FixItertoolsImports(fixer_base.BaseFix):
    BM_compatible = Kweli
    PATTERN = """
              import_kutoka< 'kutoka' 'itertools' 'agiza' agizas=any >
              """ %(locals())

    eleza transform(self, node, results):
        agizas = results['agizas']
        ikiwa agizas.type == syms.import_as_name ama sio agizas.children:
            children = [agizas]
        isipokua:
            children = agizas.children
        kila child kwenye children[::2]:
            ikiwa child.type == token.NAME:
                member = child.value
                name_node = child
            lasivyo child.type == token.STAR:
                # Just leave the agiza kama is.
                rudisha
            isipokua:
                assert child.type == syms.import_as_name
                name_node = child.children[0]
            member_name = name_node.value
            ikiwa member_name kwenye ('imap', 'izip', 'ifilter'):
                child.value = Tupu
                child.remove()
            lasivyo member_name kwenye ('ifilterfalse', 'izip_longest'):
                node.changed()
                name_node.value = ('filterfalse' ikiwa member_name[1] == 'f'
                                   isipokua 'zip_longest')

        # Make sure the agiza statement ni still sane
        children = agizas.children[:] ama [agizas]
        remove_comma = Kweli
        kila child kwenye children:
            ikiwa remove_comma na child.type == token.COMMA:
                child.remove()
            isipokua:
                remove_comma ^= Kweli

        wakati children na children[-1].type == token.COMMA:
            children.pop().remove()

        # If there are no agizas left, just get rid of the entire statement
        ikiwa (sio (agizas.children ama getattr(agizas, 'value', Tupu)) ama
            agizas.parent ni Tupu):
            p = node.prefix
            node = BlankLine()
            node.prefix = p
            rudisha node
