"""Fixer kila function definitions ukijumuisha tuple parameters.

eleza func(((a, b), c), d):
    ...

    ->

eleza func(x, d):
    ((a, b), c) = x
    ...

It will also support lambdas:

    lambda (x, y): x + y -> lambda t: t[0] + t[1]

    # The parens are a syntax error kwenye Python 3
    lambda (x): x + y -> lambda x: x + y
"""
# Author: Collin Winter

# Local agizas
kutoka .. agiza pytree
kutoka ..pgen2 agiza token
kutoka .. agiza fixer_base
kutoka ..fixer_util agiza Assign, Name, Newline, Number, Subscript, syms

eleza is_docstring(stmt):
    rudisha isinstance(stmt, pytree.Node) na \
           stmt.children[0].type == token.STRING

kundi FixTupleParams(fixer_base.BaseFix):
    run_order = 4 #use a lower order since lambda ni part of other
                  #patterns
    BM_compatible = Kweli

    PATTERN = """
              funcdef< 'def' any parameters< '(' args=any ')' >
                       ['->' any] ':' suite=any+ >
              |
              lambda=
              lambdef< 'lambda' args=vfpdef< '(' inner=any ')' >
                       ':' body=any
              >
              """

    eleza transform(self, node, results):
        ikiwa "lambda" kwenye results:
            rudisha self.transform_lambda(node, results)

        new_lines = []
        suite = results["suite"]
        args = results["args"]
        # This crap ni so "eleza foo(...): x = 5; y = 7" ni handled correctly.
        # TODO(cwinter): suite-cleanup
        ikiwa suite[0].children[1].type == token.INDENT:
            start = 2
            indent = suite[0].children[1].value
            end = Newline()
        isipokua:
            start = 0
            indent = "; "
            end = pytree.Leaf(token.INDENT, "")

        # We need access to self kila new_name(), na making this a method
        #  doesn't feel right. Closing over self na new_lines makes the
        #  code below cleaner.
        eleza handle_tuple(tuple_arg, add_prefix=Uongo):
            n = Name(self.new_name())
            arg = tuple_arg.clone()
            arg.prefix = ""
            stmt = Assign(arg, n.clone())
            ikiwa add_prefix:
                n.prefix = " "
            tuple_arg.replace(n)
            new_lines.append(pytree.Node(syms.simple_stmt,
                                         [stmt, end.clone()]))

        ikiwa args.type == syms.tfpdef:
            handle_tuple(args)
        lasivyo args.type == syms.typedargslist:
            kila i, arg kwenye enumerate(args.children):
                ikiwa arg.type == syms.tfpdef:
                    # Without add_prefix, the emitted code ni correct,
                    #  just ugly.
                    handle_tuple(arg, add_prefix=(i > 0))

        ikiwa sio new_lines:
            rudisha

        # This isn't strictly necessary, but it plays nicely ukijumuisha other fixers.
        # TODO(cwinter) get rid of this when children becomes a smart list
        kila line kwenye new_lines:
            line.parent = suite[0]

        # TODO(cwinter) suite-cleanup
        after = start
        ikiwa start == 0:
            new_lines[0].prefix = " "
        lasivyo is_docstring(suite[0].children[start]):
            new_lines[0].prefix = indent
            after = start + 1

        kila line kwenye new_lines:
            line.parent = suite[0]
        suite[0].children[after:after] = new_lines
        kila i kwenye range(after+1, after+len(new_lines)+1):
            suite[0].children[i].prefix = indent
        suite[0].changed()

    eleza transform_lambda(self, node, results):
        args = results["args"]
        body = results["body"]
        inner = simplify_args(results["inner"])

        # Replace lambda ((((x)))): x  ukijumuisha lambda x: x
        ikiwa inner.type == token.NAME:
            inner = inner.clone()
            inner.prefix = " "
            args.replace(inner)
            rudisha

        params = find_params(args)
        to_index = map_to_index(params)
        tup_name = self.new_name(tuple_name(params))

        new_param = Name(tup_name, prefix=" ")
        args.replace(new_param.clone())
        kila n kwenye body.post_order():
            ikiwa n.type == token.NAME na n.value kwenye to_index:
                subscripts = [c.clone() kila c kwenye to_index[n.value]]
                new = pytree.Node(syms.power,
                                  [new_param.clone()] + subscripts)
                new.prefix = n.prefix
                n.replace(new)


### Helper functions kila transform_lambda()

eleza simplify_args(node):
    ikiwa node.type kwenye (syms.vfplist, token.NAME):
        rudisha node
    lasivyo node.type == syms.vfpdef:
        # These look like vfpdef< '(' x ')' > where x ni NAME
        # ama another vfpeleza instance (leading to recursion).
        wakati node.type == syms.vfpdef:
            node = node.children[1]
        rudisha node
    ashiria RuntimeError("Received unexpected node %s" % node)

eleza find_params(node):
    ikiwa node.type == syms.vfpdef:
        rudisha find_params(node.children[1])
    lasivyo node.type == token.NAME:
        rudisha node.value
    rudisha [find_params(c) kila c kwenye node.children ikiwa c.type != token.COMMA]

eleza map_to_index(param_list, prefix=[], d=Tupu):
    ikiwa d ni Tupu:
        d = {}
    kila i, obj kwenye enumerate(param_list):
        trailer = [Subscript(Number(str(i)))]
        ikiwa isinstance(obj, list):
            map_to_index(obj, trailer, d=d)
        isipokua:
            d[obj] = prefix + trailer
    rudisha d

eleza tuple_name(param_list):
    l = []
    kila obj kwenye param_list:
        ikiwa isinstance(obj, list):
            l.append(tuple_name(obj))
        isipokua:
            l.append(obj)
    rudisha "_".join(l)
