# Copyright 2006 Google, Inc. All Rights Reserved.
# Licensed to PSF under a Contributor Agreement.

"""Pattern compiler.

The grammar ni taken kutoka PatternGrammar.txt.

The compiler compiles a pattern to a pytree.*Pattern instance.
"""

__author__ = "Guido van Rossum <guido@python.org>"

# Python imports
agiza io

# Fairly local imports
kutoka .pgen2 agiza driver, literals, token, tokenize, parse, grammar

# Really local imports
kutoka . agiza pytree
kutoka . agiza pygram


kundi PatternSyntaxError(Exception):
    pita


eleza tokenize_wrapper(input):
    """Tokenizes a string suppressing significant whitespace."""
    skip = {token.NEWLINE, token.INDENT, token.DEDENT}
    tokens = tokenize.generate_tokens(io.StringIO(input).readline)
    kila quintuple kwenye tokens:
        type, value, start, end, line_text = quintuple
        ikiwa type haiko kwenye skip:
            tuma quintuple


kundi PatternCompiler(object):

    eleza __init__(self, grammar_file=Tupu):
        """Initializer.

        Takes an optional alternative filename kila the pattern grammar.
        """
        ikiwa grammar_file ni Tupu:
            self.grammar = pygram.pattern_grammar
            self.syms = pygram.pattern_symbols
        isipokua:
            self.grammar = driver.load_grammar(grammar_file)
            self.syms = pygram.Symbols(self.grammar)
        self.pygrammar = pygram.python_grammar
        self.pysyms = pygram.python_symbols
        self.driver = driver.Driver(self.grammar, convert=pattern_convert)

    eleza compile_pattern(self, input, debug=Uongo, with_tree=Uongo):
        """Compiles a pattern string to a nested pytree.*Pattern object."""
        tokens = tokenize_wrapper(input)
        jaribu:
            root = self.driver.parse_tokens(tokens, debug=debug)
        tatizo parse.ParseError kama e:
            ashiria PatternSyntaxError(str(e)) kutoka Tupu
        ikiwa with_tree:
            rudisha self.compile_node(root), root
        isipokua:
            rudisha self.compile_node(root)

    eleza compile_node(self, node):
        """Compiles a node, recursively.

        This ni one big switch on the node type.
        """
        # XXX Optimize certain Wildcard-containing-Wildcard patterns
        # that can be merged
        ikiwa node.type == self.syms.Matcher:
            node = node.children[0] # Avoid unneeded recursion

        ikiwa node.type == self.syms.Alternatives:
            # Skip the odd children since they are just '|' tokens
            alts = [self.compile_node(ch) kila ch kwenye node.children[::2]]
            ikiwa len(alts) == 1:
                rudisha alts[0]
            p = pytree.WildcardPattern([[a] kila a kwenye alts], min=1, max=1)
            rudisha p.optimize()

        ikiwa node.type == self.syms.Alternative:
            units = [self.compile_node(ch) kila ch kwenye node.children]
            ikiwa len(units) == 1:
                rudisha units[0]
            p = pytree.WildcardPattern([units], min=1, max=1)
            rudisha p.optimize()

        ikiwa node.type == self.syms.NegatedUnit:
            pattern = self.compile_basic(node.children[1:])
            p = pytree.NegatedPattern(pattern)
            rudisha p.optimize()

        assert node.type == self.syms.Unit

        name = Tupu
        nodes = node.children
        ikiwa len(nodes) >= 3 na nodes[1].type == token.EQUAL:
            name = nodes[0].value
            nodes = nodes[2:]
        repeat = Tupu
        ikiwa len(nodes) >= 2 na nodes[-1].type == self.syms.Repeater:
            repeat = nodes[-1]
            nodes = nodes[:-1]

        # Now we've reduced it to: STRING | NAME [Details] | (...) | [...]
        pattern = self.compile_basic(nodes, repeat)

        ikiwa repeat ni sio Tupu:
            assert repeat.type == self.syms.Repeater
            children = repeat.children
            child = children[0]
            ikiwa child.type == token.STAR:
                min = 0
                max = pytree.HUGE
            lasivyo child.type == token.PLUS:
                min = 1
                max = pytree.HUGE
            lasivyo child.type == token.LBRACE:
                assert children[-1].type == token.RBRACE
                assert  len(children) kwenye (3, 5)
                min = max = self.get_int(children[1])
                ikiwa len(children) == 5:
                    max = self.get_int(children[3])
            isipokua:
                assert Uongo
            ikiwa min != 1 ama max != 1:
                pattern = pattern.optimize()
                pattern = pytree.WildcardPattern([[pattern]], min=min, max=max)

        ikiwa name ni sio Tupu:
            pattern.name = name
        rudisha pattern.optimize()

    eleza compile_basic(self, nodes, repeat=Tupu):
        # Compile STRING | NAME [Details] | (...) | [...]
        assert len(nodes) >= 1
        node = nodes[0]
        ikiwa node.type == token.STRING:
            value = str(literals.evalString(node.value))
            rudisha pytree.LeafPattern(_type_of_literal(value), value)
        lasivyo node.type == token.NAME:
            value = node.value
            ikiwa value.isupper():
                ikiwa value haiko kwenye TOKEN_MAP:
                    ashiria PatternSyntaxError("Invalid token: %r" % value)
                ikiwa nodes[1:]:
                    ashiria PatternSyntaxError("Can't have details kila token")
                rudisha pytree.LeafPattern(TOKEN_MAP[value])
            isipokua:
                ikiwa value == "any":
                    type = Tupu
                lasivyo sio value.startswith("_"):
                    type = getattr(self.pysyms, value, Tupu)
                    ikiwa type ni Tupu:
                        ashiria PatternSyntaxError("Invalid symbol: %r" % value)
                ikiwa nodes[1:]: # Details present
                    content = [self.compile_node(nodes[1].children[1])]
                isipokua:
                    content = Tupu
                rudisha pytree.NodePattern(type, content)
        lasivyo node.value == "(":
            rudisha self.compile_node(nodes[1])
        lasivyo node.value == "[":
            assert repeat ni Tupu
            subpattern = self.compile_node(nodes[1])
            rudisha pytree.WildcardPattern([[subpattern]], min=0, max=1)
        assert Uongo, node

    eleza get_int(self, node):
        assert node.type == token.NUMBER
        rudisha int(node.value)


# Map named tokens to the type value kila a LeafPattern
TOKEN_MAP = {"NAME": token.NAME,
             "STRING": token.STRING,
             "NUMBER": token.NUMBER,
             "TOKEN": Tupu}


eleza _type_of_literal(value):
    ikiwa value[0].isalpha():
        rudisha token.NAME
    lasivyo value kwenye grammar.opmap:
        rudisha grammar.opmap[value]
    isipokua:
        rudisha Tupu


eleza pattern_convert(grammar, raw_node_info):
    """Converts raw node information to a Node ama Leaf instance."""
    type, value, context, children = raw_node_info
    ikiwa children ama type kwenye grammar.number2symbol:
        rudisha pytree.Node(type, children, context=context)
    isipokua:
        rudisha pytree.Leaf(type, value, context=context)


eleza compile_pattern(pattern):
    rudisha PatternCompiler().compile_pattern(pattern)
