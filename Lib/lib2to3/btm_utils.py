"Utility functions used by the btm_matcher module"

kutoka . agiza pytree
kutoka .pgen2 agiza grammar, token
kutoka .pygram agiza pattern_symbols, python_symbols

syms = pattern_symbols
pysyms = python_symbols
tokens = grammar.opmap
token_labels = token

TYPE_ANY = -1
TYPE_ALTERNATIVES = -2
TYPE_GROUP = -3

kundi MinNode(object):
    """This kundi serves as an intermediate representation of the
    pattern tree during the conversion to sets of leaf-to-root
    subpatterns"""

    eleza __init__(self, type=Tupu, name=Tupu):
        self.type = type
        self.name = name
        self.children = []
        self.leaf = Uongo
        self.parent = Tupu
        self.alternatives = []
        self.group = []

    eleza __repr__(self):
        rudisha str(self.type) + ' ' + str(self.name)

    eleza leaf_to_root(self):
        """Internal method. Returns a characteristic path of the
        pattern tree. This method must be run kila all leaves until the
        linear subpatterns are merged into a single"""
        node = self
        subp = []
        wakati node:
            ikiwa node.type == TYPE_ALTERNATIVES:
                node.alternatives.append(subp)
                ikiwa len(node.alternatives) == len(node.children):
                    #last alternative
                    subp = [tuple(node.alternatives)]
                    node.alternatives = []
                    node = node.parent
                    endelea
                isipokua:
                    node = node.parent
                    subp = Tupu
                    koma

            ikiwa node.type == TYPE_GROUP:
                node.group.append(subp)
                #probably should check the number of leaves
                ikiwa len(node.group) == len(node.children):
                    subp = get_characteristic_subpattern(node.group)
                    node.group = []
                    node = node.parent
                    endelea
                isipokua:
                    node = node.parent
                    subp = Tupu
                    koma

            ikiwa node.type == token_labels.NAME na node.name:
                #in case of type=name, use the name instead
                subp.append(node.name)
            isipokua:
                subp.append(node.type)

            node = node.parent
        rudisha subp

    eleza get_linear_subpattern(self):
        """Drives the leaf_to_root method. The reason that
        leaf_to_root must be run multiple times ni because we need to
        reject 'group' matches; kila example the alternative form
        (a | b c) creates a group [b c] that needs to be matched. Since
        matching multiple linear patterns overcomes the automaton's
        capabilities, leaf_to_root merges each group into a single
        choice based on 'characteristic'ity,

        i.e. (a|b c) -> (a|b) ikiwa b more characteristic than c

        Returns: The most 'characteristic'(as defined by
          get_characteristic_subpattern) path kila the compiled pattern
          tree.
        """

        kila l kwenye self.leaves():
            subp = l.leaf_to_root()
            ikiwa subp:
                rudisha subp

    eleza leaves(self):
        "Generator that returns the leaves of the tree"
        kila child kwenye self.children:
            tuma kutoka child.leaves()
        ikiwa sio self.children:
            tuma self

eleza reduce_tree(node, parent=Tupu):
    """
    Internal function. Reduces a compiled pattern tree to an
    intermediate representation suitable kila feeding the
    automaton. This also trims off any optional pattern elements(like
    [a], a*).
    """

    new_node = Tupu
    #switch on the node type
    ikiwa node.type == syms.Matcher:
        #skip
        node = node.children[0]

    ikiwa node.type == syms.Alternatives  :
        #2 cases
        ikiwa len(node.children) <= 2:
            #just a single 'Alternative', skip this node
            new_node = reduce_tree(node.children[0], parent)
        isipokua:
            #real alternatives
            new_node = MinNode(type=TYPE_ALTERNATIVES)
            #skip odd children('|' tokens)
            kila child kwenye node.children:
                ikiwa node.children.index(child)%2:
                    endelea
                reduced = reduce_tree(child, new_node)
                ikiwa reduced ni sio Tupu:
                    new_node.children.append(reduced)
    elikiwa node.type == syms.Alternative:
        ikiwa len(node.children) > 1:

            new_node = MinNode(type=TYPE_GROUP)
            kila child kwenye node.children:
                reduced = reduce_tree(child, new_node)
                ikiwa reduced:
                    new_node.children.append(reduced)
            ikiwa sio new_node.children:
                # delete the group ikiwa all of the children were reduced to Tupu
                new_node = Tupu

        isipokua:
            new_node = reduce_tree(node.children[0], parent)

    elikiwa node.type == syms.Unit:
        ikiwa (isinstance(node.children[0], pytree.Leaf) and
            node.children[0].value == '('):
            #skip parentheses
            rudisha reduce_tree(node.children[1], parent)
        ikiwa ((isinstance(node.children[0], pytree.Leaf) and
               node.children[0].value == '[')
               or
               (len(node.children)>1 and
               hasattr(node.children[1], "value") and
               node.children[1].value == '[')):
            #skip whole unit ikiwa its optional
            rudisha Tupu

        leaf = Kweli
        details_node = Tupu
        alternatives_node = Tupu
        has_repeater = Uongo
        repeater_node = Tupu
        has_variable_name = Uongo

        kila child kwenye node.children:
            ikiwa child.type == syms.Details:
                leaf = Uongo
                details_node = child
            elikiwa child.type == syms.Repeater:
                has_repeater = Kweli
                repeater_node = child
            elikiwa child.type == syms.Alternatives:
                alternatives_node = child
            ikiwa hasattr(child, 'value') na child.value == '=': # variable name
                has_variable_name = Kweli

        #skip variable name
        ikiwa has_variable_name:
            #skip variable name, '='
            name_leaf = node.children[2]
            ikiwa hasattr(name_leaf, 'value') na name_leaf.value == '(':
                # skip parenthesis
                name_leaf = node.children[3]
        isipokua:
            name_leaf = node.children[0]

        #set node type
        ikiwa name_leaf.type == token_labels.NAME:
            #(python) non-name ama wildcard
            ikiwa name_leaf.value == 'any':
                new_node = MinNode(type=TYPE_ANY)
            isipokua:
                ikiwa hasattr(token_labels, name_leaf.value):
                    new_node = MinNode(type=getattr(token_labels, name_leaf.value))
                isipokua:
                    new_node = MinNode(type=getattr(pysyms, name_leaf.value))

        elikiwa name_leaf.type == token_labels.STRING:
            #(python) name ama character; remove the apostrophes from
            #the string value
            name = name_leaf.value.strip("'")
            ikiwa name kwenye tokens:
                new_node = MinNode(type=tokens[name])
            isipokua:
                new_node = MinNode(type=token_labels.NAME, name=name)
        elikiwa name_leaf.type == syms.Alternatives:
            new_node = reduce_tree(alternatives_node, parent)

        #handle repeaters
        ikiwa has_repeater:
            ikiwa repeater_node.children[0].value == '*':
                #reduce to Tupu
                new_node = Tupu
            elikiwa repeater_node.children[0].value == '+':
                #reduce to a single occurrence i.e. do nothing
                pass
            isipokua:
                #TODO: handle {min, max} repeaters
                 ashiria NotImplementedError
                pass

        #add children
        ikiwa details_node na new_node ni sio Tupu:
            kila child kwenye details_node.children[1:-1]:
                #skip '<', '>' markers
                reduced = reduce_tree(child, new_node)
                ikiwa reduced ni sio Tupu:
                    new_node.children.append(reduced)
    ikiwa new_node:
        new_node.parent = parent
    rudisha new_node


eleza get_characteristic_subpattern(subpatterns):
    """Picks the most characteristic kutoka a list of linear patterns
    Current order used is:
    names > common_names > common_chars
    """
    ikiwa sio isinstance(subpatterns, list):
        rudisha subpatterns
    ikiwa len(subpatterns)==1:
        rudisha subpatterns[0]

    # first pick out the ones containing variable names
    subpatterns_with_names = []
    subpatterns_with_common_names = []
    common_names = ['in', 'for', 'if' , 'not', 'Tupu']
    subpatterns_with_common_chars = []
    common_chars = "[]().,:"
    kila subpattern kwenye subpatterns:
        ikiwa any(rec_test(subpattern, lambda x: type(x) ni str)):
            ikiwa any(rec_test(subpattern,
                            lambda x: isinstance(x, str) na x kwenye common_chars)):
                subpatterns_with_common_chars.append(subpattern)
            elikiwa any(rec_test(subpattern,
                              lambda x: isinstance(x, str) na x kwenye common_names)):
                subpatterns_with_common_names.append(subpattern)

            isipokua:
                subpatterns_with_names.append(subpattern)

    ikiwa subpatterns_with_names:
        subpatterns = subpatterns_with_names
    elikiwa subpatterns_with_common_names:
        subpatterns = subpatterns_with_common_names
    elikiwa subpatterns_with_common_chars:
        subpatterns = subpatterns_with_common_chars
    # of the remaining subpatterns pick out the longest one
    rudisha max(subpatterns, key=len)

eleza rec_test(sequence, test_func):
    """Tests test_func on all items of sequence na items of included
    sub-iterables"""
    kila x kwenye sequence:
        ikiwa isinstance(x, (list, tuple)):
            tuma kutoka rec_test(x, test_func)
        isipokua:
            tuma test_func(x)
