# Copyright 2006 Google, Inc. All Rights Reserved.
# Licensed to PSF under a Contributor Agreement.

"""Pattern compiler.

The grammar is taken kutoka PatternGrammar.txt.

The compiler compiles a pattern to a pytree.*Pattern instance.
"""

__author__ = "Guido van Rossum <guido@python.org>"

# Python agizas
agiza io

# Fairly local agizas
kutoka .pgen2 agiza driver, literals, token, tokenize, parse, grammar

# Really local agizas
kutoka . agiza pytree
kutoka . agiza pygram


kundi PatternSyntaxError(Exception):
    pass


eleza tokenize_wrapper(input):
    """Tokenizes a string suppressing significant whitespace."""
    skip = {token.NEWLINE, token.INDENT, token.DEDENT}
    tokens = tokenize.generate_tokens(io.StringIO(input).readline)
    for quintuple in tokens:
        type, value, start, end, line_text = quintuple
        ikiwa type not in skip:
            yield quintuple


kundi PatternCompiler(object):

    eleza __init__(self, grammar_file=None):
        """Initializer.

        Takes an optional alternative filename for the pattern grammar.
        """
        ikiwa grammar_file is None:
            self.grammar = pygram.pattern_grammar
            self.syms = pygram.pattern_symbols
        else:
            self.grammar = driver.load_grammar(grammar_file)
            self.syms = pygram.Symbols(self.grammar)
        self.pygrammar = pygram.python_grammar
        self.pysyms = pygram.python_symbols
        self.driver = driver.Driver(self.grammar, convert=pattern_convert)

    eleza compile_pattern(self, input, debug=False, with_tree=False):
        """Compiles a pattern string to a nested pytree.*Pattern object."""
        tokens = tokenize_wrapper(input)
        try:
            root = self.driver.parse_tokens(tokens, debug=debug)
        except parse.ParseError as e:
            raise PatternSyntaxError(str(e)) kutoka None
        ikiwa with_tree:
            rudisha self.compile_node(root), root
        else:
            rudisha self.compile_node(root)

    eleza compile_node(self, node):
        """Compiles a node, recursively.

        This is one big switch on the node type.
        """
        # XXX Optimize certain Wildcard-containing-Wildcard patterns
        # that can be merged
        ikiwa node.type == self.syms.Matcher:
            node = node.children[0] # Avoid unneeded recursion

        ikiwa node.type == self.syms.Alternatives:
            # Skip the odd children since they are just '|' tokens
            alts = [self.compile_node(ch) for ch in node.children[::2]]
            ikiwa len(alts) == 1:
                rudisha alts[0]
            p = pytree.WildcardPattern([[a] for a in alts], min=1, max=1)
            rudisha p.optimize()

        ikiwa node.type == self.syms.Alternative:
            units = [self.compile_node(ch) for ch in node.children]
            ikiwa len(units) == 1:
                rudisha units[0]
            p = pytree.WildcardPattern([units], min=1, max=1)
            rudisha p.optimize()

        ikiwa node.type == self.syms.NegatedUnit:
            pattern = self.compile_basic(node.children[1:])
            p = pytree.NegatedPattern(pattern)
            rudisha p.optimize()

        assert node.type == self.syms.Unit

        name = None
        nodes = node.children
        ikiwa len(nodes) >= 3 and nodes[1].type == token.EQUAL:
            name = nodes[0].value
            nodes = nodes[2:]
        repeat = None
        ikiwa len(nodes) >= 2 and nodes[-1].type == self.syms.Repeater:
            repeat = nodes[-1]
            nodes = nodes[:-1]

        # Now we've reduced it to: STRING | NAME [Details] | (...) | [...]
        pattern = self.compile_basic(nodes, repeat)

        ikiwa repeat is not None:
            assert repeat.type == self.syms.Repeater
            children = repeat.children
            child = children[0]
            ikiwa child.type == token.STAR:
                min = 0
                max = pytree.HUGE
            elikiwa child.type == token.PLUS:
                min = 1
                max = pytree.HUGE
            elikiwa child.type == token.LBRACE:
                assert children[-1].type == token.RBRACE
                assert  len(children) in (3, 5)
                min = max = self.get_int(children[1])
                ikiwa len(children) == 5:
                    max = self.get_int(children[3])
            else:
                assert False
            ikiwa min != 1 or max != 1:
                pattern = pattern.optimize()
                pattern = pytree.WildcardPattern([[pattern]], min=min, max=max)

        ikiwa name is not None:
            pattern.name = name
        rudisha pattern.optimize()

    eleza compile_basic(self, nodes, repeat=None):
        # Compile STRING | NAME [Details] | (...) | [...]
        assert len(nodes) >= 1
        node = nodes[0]
        ikiwa node.type == token.STRING:
            value = str(literals.evalString(node.value))
            rudisha pytree.LeafPattern(_type_of_literal(value), value)
        elikiwa node.type == token.NAME:
            value = node.value
            ikiwa value.isupper():
                ikiwa value not in TOKEN_MAP:
                    raise PatternSyntaxError("Invalid token: %r" % value)
                ikiwa nodes[1:]:
                    raise PatternSyntaxError("Can't have details for token")
                rudisha pytree.LeafPattern(TOKEN_MAP[value])
            else:
                ikiwa value == "any":
                    type = None
                elikiwa not value.startswith("_"):
                    type = getattr(self.pysyms, value, None)
                    ikiwa type is None:
                        raise PatternSyntaxError("Invalid symbol: %r" % value)
                ikiwa nodes[1:]: # Details present
                    content = [self.compile_node(nodes[1].children[1])]
                else:
                    content = None
                rudisha pytree.NodePattern(type, content)
        elikiwa node.value == "(":
            rudisha self.compile_node(nodes[1])
        elikiwa node.value == "[":
            assert repeat is None
            subpattern = self.compile_node(nodes[1])
            rudisha pytree.WildcardPattern([[subpattern]], min=0, max=1)
        assert False, node

    eleza get_int(self, node):
        assert node.type == token.NUMBER
        rudisha int(node.value)


# Map named tokens to the type value for a LeafPattern
TOKEN_MAP = {"NAME": token.NAME,
             "STRING": token.STRING,
             "NUMBER": token.NUMBER,
             "TOKEN": None}


eleza _type_of_literal(value):
    ikiwa value[0].isalpha():
        rudisha token.NAME
    elikiwa value in grammar.opmap:
        rudisha grammar.opmap[value]
    else:
        rudisha None


eleza pattern_convert(grammar, raw_node_info):
    """Converts raw node information to a Node or Leaf instance."""
    type, value, context, children = raw_node_info
    ikiwa children or type in grammar.number2symbol:
        rudisha pytree.Node(type, children, context=context)
    else:
        rudisha pytree.Leaf(type, value, context=context)


eleza compile_pattern(pattern):
    rudisha PatternCompiler().compile_pattern(pattern)
