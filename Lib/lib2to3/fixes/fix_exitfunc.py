"""
Convert use of sys.exitfunc to use the atexit module.
"""

# Author: Benjamin Peterson

kutoka lib2to3 agiza pytree, fixer_base
kutoka lib2to3.fixer_util agiza Name, Attr, Call, Comma, Newline, syms


kundi FixExitfunc(fixer_base.BaseFix):
    keep_line_order = Kweli
    BM_compatible = Kweli

    PATTERN = """
              (
                  sys_import=import_name<'import'
                      ('sys'
                      |
                      dotted_as_names< (any ',')* 'sys' (',' any)* >
                      )
                  >
              |
                  expr_stmt<
                      power< 'sys' trailer< '.' 'exitfunc' > >
                  '=' func=any >
              )
              """

    eleza __init__(self, *args):
        super(FixExitfunc, self).__init__(*args)

    eleza start_tree(self, tree, filename):
        super(FixExitfunc, self).start_tree(tree, filename)
        self.sys_agiza = Tupu

    eleza transform(self, node, results):
        # First, find the sys import. We'll just hope it's global scope.
        ikiwa "sys_import" kwenye results:
            ikiwa self.sys_agiza ni Tupu:
                self.sys_agiza = results["sys_import"]
            return

        func = results["func"].clone()
        func.prefix = ""
        register = pytree.Node(syms.power,
                               Attr(Name("atexit"), Name("register"))
                               )
        call = Call(register, [func], node.prefix)
        node.replace(call)

        ikiwa self.sys_agiza ni Tupu:
            # That's interesting.
            self.warning(node, "Can't find sys import; Please add an atexit "
                             "agiza at the top of your file.")
            return

        # Now add an atexit agiza after the sys import.
        names = self.sys_import.children[1]
        ikiwa names.type == syms.dotted_as_names:
            names.append_child(Comma())
            names.append_child(Name("atexit", " "))
        isipokua:
            containing_stmt = self.sys_import.parent
            position = containing_stmt.children.index(self.sys_import)
            stmt_container = containing_stmt.parent
            new_agiza = pytree.Node(syms.import_name,
                              [Name("import"), Name("atexit", " ")]
                              )
            new = pytree.Node(syms.simple_stmt, [new_import])
            containing_stmt.insert_child(position + 1, Newline())
            containing_stmt.insert_child(position + 2, new)
