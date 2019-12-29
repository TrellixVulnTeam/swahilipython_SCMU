"""Fixer that addes parentheses where they are required

This converts ``[x kila x kwenye 1, 2]`` to ``[x kila x kwenye (1, 2)]``."""

# By Taek Joo Kim na Benjamin Peterson

# Local agizas
kutoka .. agiza fixer_base
kutoka ..fixer_util agiza LParen, RParen

# XXX This doesn't support nested kila loops like [x kila x kwenye 1, 2 kila x kwenye 1, 2]
kundi FixParen(fixer_base.BaseFix):
    BM_compatible = Kweli

    PATTERN = """
        atom< ('[' | '(')
            (listmaker< any
                comp_for<
                    'for' NAME 'in'
                    target=testlist_safe< any (',' any)+ [',']
                     >
                    [any]
                >
            >
            |
            testlist_gexp< any
                comp_for<
                    'for' NAME 'in'
                    target=testlist_safe< any (',' any)+ [',']
                     >
                    [any]
                >
            >)
        (']' | ')') >
    """

    eleza transform(self, node, results):
        target = results["target"]

        lparen = LParen()
        lparen.prefix = target.prefix
        target.prefix = "" # Make it hug the parentheses
        target.insert_child(0, lparen)
        target.append_child(RParen())
