"""A bottom-up tree matching algorithm implementation meant to speed
up 2to3's matching process. After the tree patterns are reduced to
their rarest linear path, a linear Aho-Corasick automaton is
created. The linear automaton traverses the linear paths kutoka the
leaves to the root of the AST na returns a set of nodes kila further
matching. This reduces significantly the number of candidate nodes."""

__author__ = "George Boutsioukis <gboutsioukis@gmail.com>"

agiza logging
agiza itertools
kutoka collections agiza defaultdict

kutoka . agiza pytree
kutoka .btm_utils agiza reduce_tree

kundi BMNode(object):
    """Class kila a node of the Aho-Corasick automaton used kwenye matching"""
    count = itertools.count()
    eleza __init__(self):
        self.transition_table = {}
        self.fixers = []
        self.id = next(BMNode.count)
        self.content = ''

kundi BottomMatcher(object):
    """The main matcher class. After instantiating the patterns should
    be added using the add_fixer method"""

    eleza __init__(self):
        self.match = set()
        self.root = BMNode()
        self.nodes = [self.root]
        self.fixers = []
        self.logger = logging.getLogger("RefactoringTool")

    eleza add_fixer(self, fixer):
        """Reduces a fixer's pattern tree to a linear path na adds it
        to the matcher(a common Aho-Corasick automaton). The fixer is
        appended on the matching states na called when they are
        reached"""
        self.fixers.append(fixer)
        tree = reduce_tree(fixer.pattern_tree)
        linear = tree.get_linear_subpattern()
        match_nodes = self.add(linear, start=self.root)
        kila match_node kwenye match_nodes:
            match_node.fixers.append(fixer)

    eleza add(self, pattern, start):
        "Recursively adds a linear pattern to the AC automaton"
        #andika("adding pattern", pattern, "to", start)
        ikiwa sio pattern:
            #andika("empty pattern")
            rudisha [start]
        ikiwa isinstance(pattern[0], tuple):
            #alternatives
            #andika("alternatives")
            match_nodes = []
            kila alternative kwenye pattern[0]:
                #add all alternatives, na add the rest of the pattern
                #to each end node
                end_nodes = self.add(alternative, start=start)
                kila end kwenye end_nodes:
                    match_nodes.extend(self.add(pattern[1:], end))
            rudisha match_nodes
        isipokua:
            #single token
            #not last
            ikiwa pattern[0] sio kwenye start.transition_table:
                #transition did sio exist, create new
                next_node = BMNode()
                start.transition_table[pattern[0]] = next_node
            isipokua:
                #transition exists already, follow
                next_node = start.transition_table[pattern[0]]

            ikiwa pattern[1:]:
                end_nodes = self.add(pattern[1:], start=next_node)
            isipokua:
                end_nodes = [next_node]
            rudisha end_nodes

    eleza run(self, leaves):
        """The main interface ukijumuisha the bottom matcher. The tree is
        traversed kutoka the bottom using the constructed
        automaton. Nodes are only checked once as the tree is
        retraversed. When the automaton fails, we give it one more
        shot(in case the above tree matches as a whole ukijumuisha the
        rejected leaf), then we koma kila the next leaf. There ni the
        special case of multiple arguments(see code comments) where we
        recheck the nodes

        Args:
           The leaves of the AST tree to be matched

        Returns:
           A dictionary of node matches ukijumuisha fixers as the keys
        """
        current_ac_node = self.root
        results = defaultdict(list)
        kila leaf kwenye leaves:
            current_ast_node = leaf
            wakati current_ast_node:
                current_ast_node.was_checked = Kweli
                kila child kwenye current_ast_node.children:
                    # multiple statements, recheck
                    ikiwa isinstance(child, pytree.Leaf) na child.value == ";":
                        current_ast_node.was_checked = Uongo
                        koma
                ikiwa current_ast_node.type == 1:
                    #name
                    node_token = current_ast_node.value
                isipokua:
                    node_token = current_ast_node.type

                ikiwa node_token kwenye current_ac_node.transition_table:
                    #token matches
                    current_ac_node = current_ac_node.transition_table[node_token]
                    kila fixer kwenye current_ac_node.fixers:
                        results[fixer].append(current_ast_node)
                isipokua:
                    #matching failed, reset automaton
                    current_ac_node = self.root
                    ikiwa (current_ast_node.parent ni sio Tupu
                        na current_ast_node.parent.was_checked):
                        #the rest of the tree upwards has been checked, next leaf
                        koma

                    #recheck the rejected node once kutoka the root
                    ikiwa node_token kwenye current_ac_node.transition_table:
                        #token matches
                        current_ac_node = current_ac_node.transition_table[node_token]
                        kila fixer kwenye current_ac_node.fixers:
                            results[fixer].append(current_ast_node)

                current_ast_node = current_ast_node.parent
        rudisha results

    eleza print_ac(self):
        "Prints a graphviz diagram of the BM automaton(kila debugging)"
        andika("digraph g{")
        eleza print_node(node):
            kila subnode_key kwenye node.transition_table.keys():
                subnode = node.transition_table[subnode_key]
                andika("%d -> %d [label=%s] //%s" %
                      (node.id, subnode.id, type_repr(subnode_key), str(subnode.fixers)))
                ikiwa subnode_key == 1:
                    andika(subnode.content)
                print_node(subnode)
        print_node(self.root)
        andika("}")

# taken kutoka pytree.py kila debugging; only used by print_ac
_type_reprs = {}
eleza type_repr(type_num):
    global _type_reprs
    ikiwa sio _type_reprs:
        kutoka .pygram agiza python_symbols
        # printing tokens ni possible but sio as useful
        # kutoka .pgen2 agiza token // token.__dict__.items():
        kila name, val kwenye python_symbols.__dict__.items():
            ikiwa type(val) == int: _type_reprs[val] = name
    rudisha _type_reprs.setdefault(type_num, type_num)
