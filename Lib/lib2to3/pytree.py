# Copyright 2006 Google, Inc. All Rights Reserved.
# Licensed to PSF under a Contributor Agreement.

"""
Python parse tree definitions.

This ni a very concrete parse tree; we need to keep every token na
even the comments na whitespace between tokens.

There's also a pattern matching implementation here.
"""

__author__ = "Guido van Rossum <guido@python.org>"

agiza sys
kutoka io agiza StringIO

HUGE = 0x7FFFFFFF  # maximum repeat count, default max

_type_reprs = {}
eleza type_repr(type_num):
    global _type_reprs
    ikiwa sio _type_reprs:
        kutoka .pygram agiza python_symbols
        # printing tokens ni possible but sio kama useful
        # kutoka .pgen2 agiza token // token.__dict__.items():
        kila name, val kwenye python_symbols.__dict__.items():
            ikiwa type(val) == int: _type_reprs[val] = name
    rudisha _type_reprs.setdefault(type_num, type_num)

kundi Base(object):

    """
    Abstract base kundi kila Node na Leaf.

    This provides some default functionality na boilerplate using the
    template pattern.

    A node may be a subnode of at most one parent.
    """

    # Default values kila instance variables
    type = Tupu    # int: token number (< 256) ama symbol number (>= 256)
    parent = Tupu  # Parent node pointer, ama Tupu
    children = ()  # Tuple of subnodes
    was_changed = Uongo
    was_checked = Uongo

    eleza __new__(cls, *args, **kwds):
        """Constructor that prevents Base kutoka being instantiated."""
        assert cls ni sio Base, "Cannot instantiate Base"
        rudisha object.__new__(cls)

    eleza __eq__(self, other):
        """
        Compare two nodes kila equality.

        This calls the method _eq().
        """
        ikiwa self.__class__ ni sio other.__class__:
            rudisha NotImplemented
        rudisha self._eq(other)

    __hash__ = Tupu # For Py3 compatibility.

    eleza _eq(self, other):
        """
        Compare two nodes kila equality.

        This ni called by __eq__ na __ne__.  It ni only called ikiwa the two nodes
        have the same type.  This must be implemented by the concrete subclass.
        Nodes should be considered equal ikiwa they have the same structure,
        ignoring the prefix string na other context information.
        """
        ashiria NotImplementedError

    eleza clone(self):
        """
        Return a cloned (deep) copy of self.

        This must be implemented by the concrete subclass.
        """
        ashiria NotImplementedError

    eleza post_order(self):
        """
        Return a post-order iterator kila the tree.

        This must be implemented by the concrete subclass.
        """
        ashiria NotImplementedError

    eleza pre_order(self):
        """
        Return a pre-order iterator kila the tree.

        This must be implemented by the concrete subclass.
        """
        ashiria NotImplementedError

    eleza replace(self, new):
        """Replace this node ukijumuisha a new one kwenye the parent."""
        assert self.parent ni sio Tupu, str(self)
        assert new ni sio Tupu
        ikiwa sio isinstance(new, list):
            new = [new]
        l_children = []
        found = Uongo
        kila ch kwenye self.parent.children:
            ikiwa ch ni self:
                assert sio found, (self.parent.children, self, new)
                ikiwa new ni sio Tupu:
                    l_children.extend(new)
                found = Kweli
            isipokua:
                l_children.append(ch)
        assert found, (self.children, self, new)
        self.parent.changed()
        self.parent.children = l_children
        kila x kwenye new:
            x.parent = self.parent
        self.parent = Tupu

    eleza get_lineno(self):
        """Return the line number which generated the invocant node."""
        node = self
        wakati sio isinstance(node, Leaf):
            ikiwa sio node.children:
                return
            node = node.children[0]
        rudisha node.lineno

    eleza changed(self):
        ikiwa self.parent:
            self.parent.changed()
        self.was_changed = Kweli

    eleza remove(self):
        """
        Remove the node kutoka the tree. Returns the position of the node kwenye its
        parent's children before it was removed.
        """
        ikiwa self.parent:
            kila i, node kwenye enumerate(self.parent.children):
                ikiwa node ni self:
                    self.parent.changed()
                    toa self.parent.children[i]
                    self.parent = Tupu
                    rudisha i

    @property
    eleza next_sibling(self):
        """
        The node immediately following the invocant kwenye their parent's children
        list. If the invocant does sio have a next sibling, it ni Tupu
        """
        ikiwa self.parent ni Tupu:
            rudisha Tupu

        # Can't use index(); we need to test by identity
        kila i, child kwenye enumerate(self.parent.children):
            ikiwa child ni self:
                jaribu:
                    rudisha self.parent.children[i+1]
                tatizo IndexError:
                    rudisha Tupu

    @property
    eleza prev_sibling(self):
        """
        The node immediately preceding the invocant kwenye their parent's children
        list. If the invocant does sio have a previous sibling, it ni Tupu.
        """
        ikiwa self.parent ni Tupu:
            rudisha Tupu

        # Can't use index(); we need to test by identity
        kila i, child kwenye enumerate(self.parent.children):
            ikiwa child ni self:
                ikiwa i == 0:
                    rudisha Tupu
                rudisha self.parent.children[i-1]

    eleza leaves(self):
        kila child kwenye self.children:
            tuma kutoka child.leaves()

    eleza depth(self):
        ikiwa self.parent ni Tupu:
            rudisha 0
        rudisha 1 + self.parent.depth()

    eleza get_suffix(self):
        """
        Return the string immediately following the invocant node. This is
        effectively equivalent to node.next_sibling.prefix
        """
        next_sib = self.next_sibling
        ikiwa next_sib ni Tupu:
            rudisha ""
        rudisha next_sib.prefix

    ikiwa sys.version_info < (3, 0):
        eleza __str__(self):
            rudisha str(self).encode("ascii")

kundi Node(Base):

    """Concrete implementation kila interior nodes."""

    eleza __init__(self,type, children,
                 context=Tupu,
                 prefix=Tupu,
                 fixers_applied=Tupu):
        """
        Initializer.

        Takes a type constant (a symbol number >= 256), a sequence of
        child nodes, na an optional context keyword argument.

        As a side effect, the parent pointers of the children are updated.
        """
        assert type >= 256, type
        self.type = type
        self.children = list(children)
        kila ch kwenye self.children:
            assert ch.parent ni Tupu, repr(ch)
            ch.parent = self
        ikiwa prefix ni sio Tupu:
            self.prefix = prefix
        ikiwa fixers_applied:
            self.fixers_applied = fixers_applied[:]
        isipokua:
            self.fixers_applied = Tupu

    eleza __repr__(self):
        """Return a canonical string representation."""
        rudisha "%s(%s, %r)" % (self.__class__.__name__,
                               type_repr(self.type),
                               self.children)

    eleza __unicode__(self):
        """
        Return a pretty string representation.

        This reproduces the input source exactly.
        """
        rudisha "".join(map(str, self.children))

    ikiwa sys.version_info > (3, 0):
        __str__ = __unicode__

    eleza _eq(self, other):
        """Compare two nodes kila equality."""
        rudisha (self.type, self.children) == (other.type, other.children)

    eleza clone(self):
        """Return a cloned (deep) copy of self."""
        rudisha Node(self.type, [ch.clone() kila ch kwenye self.children],
                    fixers_applied=self.fixers_applied)

    eleza post_order(self):
        """Return a post-order iterator kila the tree."""
        kila child kwenye self.children:
            tuma kutoka child.post_order()
        tuma self

    eleza pre_order(self):
        """Return a pre-order iterator kila the tree."""
        tuma self
        kila child kwenye self.children:
            tuma kutoka child.pre_order()

    @property
    eleza prefix(self):
        """
        The whitespace na comments preceding this node kwenye the input.
        """
        ikiwa sio self.children:
            rudisha ""
        rudisha self.children[0].prefix

    @prefix.setter
    eleza prefix(self, prefix):
        ikiwa self.children:
            self.children[0].prefix = prefix

    eleza set_child(self, i, child):
        """
        Equivalent to 'node.children[i] = child'. This method also sets the
        child's parent attribute appropriately.
        """
        child.parent = self
        self.children[i].parent = Tupu
        self.children[i] = child
        self.changed()

    eleza insert_child(self, i, child):
        """
        Equivalent to 'node.children.insert(i, child)'. This method also sets
        the child's parent attribute appropriately.
        """
        child.parent = self
        self.children.insert(i, child)
        self.changed()

    eleza append_child(self, child):
        """
        Equivalent to 'node.children.append(child)'. This method also sets the
        child's parent attribute appropriately.
        """
        child.parent = self
        self.children.append(child)
        self.changed()


kundi Leaf(Base):

    """Concrete implementation kila leaf nodes."""

    # Default values kila instance variables
    _prefix = ""  # Whitespace na comments preceding this token kwenye the input
    lineno = 0    # Line where this token starts kwenye the input
    column = 0    # Column where this token tarts kwenye the input

    eleza __init__(self, type, value,
                 context=Tupu,
                 prefix=Tupu,
                 fixers_applied=[]):
        """
        Initializer.

        Takes a type constant (a token number < 256), a string value, na an
        optional context keyword argument.
        """
        assert 0 <= type < 256, type
        ikiwa context ni sio Tupu:
            self._prefix, (self.lineno, self.column) = context
        self.type = type
        self.value = value
        ikiwa prefix ni sio Tupu:
            self._prefix = prefix
        self.fixers_applied = fixers_applied[:]

    eleza __repr__(self):
        """Return a canonical string representation."""
        rudisha "%s(%r, %r)" % (self.__class__.__name__,
                               self.type,
                               self.value)

    eleza __unicode__(self):
        """
        Return a pretty string representation.

        This reproduces the input source exactly.
        """
        rudisha self.prefix + str(self.value)

    ikiwa sys.version_info > (3, 0):
        __str__ = __unicode__

    eleza _eq(self, other):
        """Compare two nodes kila equality."""
        rudisha (self.type, self.value) == (other.type, other.value)

    eleza clone(self):
        """Return a cloned (deep) copy of self."""
        rudisha Leaf(self.type, self.value,
                    (self.prefix, (self.lineno, self.column)),
                    fixers_applied=self.fixers_applied)

    eleza leaves(self):
        tuma self

    eleza post_order(self):
        """Return a post-order iterator kila the tree."""
        tuma self

    eleza pre_order(self):
        """Return a pre-order iterator kila the tree."""
        tuma self

    @property
    eleza prefix(self):
        """
        The whitespace na comments preceding this token kwenye the input.
        """
        rudisha self._prefix

    @prefix.setter
    eleza prefix(self, prefix):
        self.changed()
        self._prefix = prefix

eleza convert(gr, raw_node):
    """
    Convert raw node information to a Node ama Leaf instance.

    This ni pitaed to the parser driver which calls it whenever a reduction of a
    grammar rule produces a new complete node, so that the tree ni build
    strictly bottom-up.
    """
    type, value, context, children = raw_node
    ikiwa children ama type kwenye gr.number2symbol:
        # If there's exactly one child, rudisha that child instead of
        # creating a new node.
        ikiwa len(children) == 1:
            rudisha children[0]
        rudisha Node(type, children, context=context)
    isipokua:
        rudisha Leaf(type, value, context=context)


kundi BasePattern(object):

    """
    A pattern ni a tree matching pattern.

    It looks kila a specific node type (token ama symbol), na
    optionally kila a specific content.

    This ni an abstract base class.  There are three concrete
    subclasses:

    - LeafPattern matches a single leaf node;
    - NodePattern matches a single node (usually non-leaf);
    - WildcardPattern matches a sequence of nodes of variable length.
    """

    # Defaults kila instance variables
    type = Tupu     # Node type (token ikiwa < 256, symbol ikiwa >= 256)
    content = Tupu  # Optional content matching pattern
    name = Tupu     # Optional name used to store match kwenye results dict

    eleza __new__(cls, *args, **kwds):
        """Constructor that prevents BasePattern kutoka being instantiated."""
        assert cls ni sio BasePattern, "Cannot instantiate BasePattern"
        rudisha object.__new__(cls)

    eleza __repr__(self):
        args = [type_repr(self.type), self.content, self.name]
        wakati args na args[-1] ni Tupu:
            toa args[-1]
        rudisha "%s(%s)" % (self.__class__.__name__, ", ".join(map(repr, args)))

    eleza optimize(self):
        """
        A subkundi can define this kama a hook kila optimizations.

        Returns either self ama another node ukijumuisha the same effect.
        """
        rudisha self

    eleza match(self, node, results=Tupu):
        """
        Does this pattern exactly match a node?

        Returns Kweli ikiwa it matches, Uongo ikiwa not.

        If results ni sio Tupu, it must be a dict which will be
        updated ukijumuisha the nodes matching named subpatterns.

        Default implementation kila non-wildcard patterns.
        """
        ikiwa self.type ni sio Tupu na node.type != self.type:
            rudisha Uongo
        ikiwa self.content ni sio Tupu:
            r = Tupu
            ikiwa results ni sio Tupu:
                r = {}
            ikiwa sio self._submatch(node, r):
                rudisha Uongo
            ikiwa r:
                results.update(r)
        ikiwa results ni sio Tupu na self.name:
            results[self.name] = node
        rudisha Kweli

    eleza match_seq(self, nodes, results=Tupu):
        """
        Does this pattern exactly match a sequence of nodes?

        Default implementation kila non-wildcard patterns.
        """
        ikiwa len(nodes) != 1:
            rudisha Uongo
        rudisha self.match(nodes[0], results)

    eleza generate_matches(self, nodes):
        """
        Generator tumaing all matches kila this pattern.

        Default implementation kila non-wildcard patterns.
        """
        r = {}
        ikiwa nodes na self.match(nodes[0], r):
            tuma 1, r


kundi LeafPattern(BasePattern):

    eleza __init__(self, type=Tupu, content=Tupu, name=Tupu):
        """
        Initializer.  Takes optional type, content, na name.

        The type, ikiwa given must be a token type (< 256).  If sio given,
        this matches any *leaf* node; the content may still be required.

        The content, ikiwa given, must be a string.

        If a name ni given, the matching node ni stored kwenye the results
        dict under that key.
        """
        ikiwa type ni sio Tupu:
            assert 0 <= type < 256, type
        ikiwa content ni sio Tupu:
            assert isinstance(content, str), repr(content)
        self.type = type
        self.content = content
        self.name = name

    eleza match(self, node, results=Tupu):
        """Override match() to insist on a leaf node."""
        ikiwa sio isinstance(node, Leaf):
            rudisha Uongo
        rudisha BasePattern.match(self, node, results)

    eleza _submatch(self, node, results=Tupu):
        """
        Match the pattern's content to the node's children.

        This assumes the node type matches na self.content ni sio Tupu.

        Returns Kweli ikiwa it matches, Uongo ikiwa not.

        If results ni sio Tupu, it must be a dict which will be
        updated ukijumuisha the nodes matching named subpatterns.

        When returning Uongo, the results dict may still be updated.
        """
        rudisha self.content == node.value


kundi NodePattern(BasePattern):

    wildcards = Uongo

    eleza __init__(self, type=Tupu, content=Tupu, name=Tupu):
        """
        Initializer.  Takes optional type, content, na name.

        The type, ikiwa given, must be a symbol type (>= 256).  If the
        type ni Tupu this matches *any* single node (leaf ama not),
        tatizo ikiwa content ni sio Tupu, kwenye which it only matches
        non-leaf nodes that also match the content pattern.

        The content, ikiwa sio Tupu, must be a sequence of Patterns that
        must match the node's children exactly.  If the content is
        given, the type must sio be Tupu.

        If a name ni given, the matching node ni stored kwenye the results
        dict under that key.
        """
        ikiwa type ni sio Tupu:
            assert type >= 256, type
        ikiwa content ni sio Tupu:
            assert sio isinstance(content, str), repr(content)
            content = list(content)
            kila i, item kwenye enumerate(content):
                assert isinstance(item, BasePattern), (i, item)
                ikiwa isinstance(item, WildcardPattern):
                    self.wildcards = Kweli
        self.type = type
        self.content = content
        self.name = name

    eleza _submatch(self, node, results=Tupu):
        """
        Match the pattern's content to the node's children.

        This assumes the node type matches na self.content ni sio Tupu.

        Returns Kweli ikiwa it matches, Uongo ikiwa not.

        If results ni sio Tupu, it must be a dict which will be
        updated ukijumuisha the nodes matching named subpatterns.

        When returning Uongo, the results dict may still be updated.
        """
        ikiwa self.wildcards:
            kila c, r kwenye generate_matches(self.content, node.children):
                ikiwa c == len(node.children):
                    ikiwa results ni sio Tupu:
                        results.update(r)
                    rudisha Kweli
            rudisha Uongo
        ikiwa len(self.content) != len(node.children):
            rudisha Uongo
        kila subpattern, child kwenye zip(self.content, node.children):
            ikiwa sio subpattern.match(child, results):
                rudisha Uongo
        rudisha Kweli


kundi WildcardPattern(BasePattern):

    """
    A wildcard pattern can match zero ama more nodes.

    This has all the flexibility needed to implement patterns like:

    .*      .+      .?      .{m,n}
    (a b c | d e | f)
    (...)*  (...)+  (...)?  (...){m,n}

    tatizo it always uses non-greedy matching.
    """

    eleza __init__(self, content=Tupu, min=0, max=HUGE, name=Tupu):
        """
        Initializer.

        Args:
            content: optional sequence of subsequences of patterns;
                     ikiwa absent, matches one node;
                     ikiwa present, each subsequence ni an alternative [*]
            min: optional minimum number of times to match, default 0
            max: optional maximum number of times to match, default HUGE
            name: optional name assigned to this match

        [*] Thus, ikiwa content ni [[a, b, c], [d, e], [f, g, h]] this is
            equivalent to (a b c | d e | f g h); ikiwa content ni Tupu,
            this ni equivalent to '.' kwenye regular expression terms.
            The min na max parameters work kama follows:
                min=0, max=maxint: .*
                min=1, max=maxint: .+
                min=0, max=1: .?
                min=1, max=1: .
            If content ni sio Tupu, replace the dot ukijumuisha the parenthesized
            list of alternatives, e.g. (a b c | d e | f g h)*
        """
        assert 0 <= min <= max <= HUGE, (min, max)
        ikiwa content ni sio Tupu:
            content = tuple(map(tuple, content))  # Protect against alterations
            # Check sanity of alternatives
            assert len(content), repr(content)  # Can't have zero alternatives
            kila alt kwenye content:
                assert len(alt), repr(alt) # Can have empty alternatives
        self.content = content
        self.min = min
        self.max = max
        self.name = name

    eleza optimize(self):
        """Optimize certain stacked wildcard patterns."""
        subpattern = Tupu
        ikiwa (self.content ni sio Tupu na
            len(self.content) == 1 na len(self.content[0]) == 1):
            subpattern = self.content[0][0]
        ikiwa self.min == 1 na self.max == 1:
            ikiwa self.content ni Tupu:
                rudisha NodePattern(name=self.name)
            ikiwa subpattern ni sio Tupu na  self.name == subpattern.name:
                rudisha subpattern.optimize()
        ikiwa (self.min <= 1 na isinstance(subpattern, WildcardPattern) na
            subpattern.min <= 1 na self.name == subpattern.name):
            rudisha WildcardPattern(subpattern.content,
                                   self.min*subpattern.min,
                                   self.max*subpattern.max,
                                   subpattern.name)
        rudisha self

    eleza match(self, node, results=Tupu):
        """Does this pattern exactly match a node?"""
        rudisha self.match_seq([node], results)

    eleza match_seq(self, nodes, results=Tupu):
        """Does this pattern exactly match a sequence of nodes?"""
        kila c, r kwenye self.generate_matches(nodes):
            ikiwa c == len(nodes):
                ikiwa results ni sio Tupu:
                    results.update(r)
                    ikiwa self.name:
                        results[self.name] = list(nodes)
                rudisha Kweli
        rudisha Uongo

    eleza generate_matches(self, nodes):
        """
        Generator tumaing matches kila a sequence of nodes.

        Args:
            nodes: sequence of nodes

        Yields:
            (count, results) tuples where:
            count: the match comprises nodes[:count];
            results: dict containing named submatches.
        """
        ikiwa self.content ni Tupu:
            # Shortcut kila special case (see __init__.__doc__)
            kila count kwenye range(self.min, 1 + min(len(nodes), self.max)):
                r = {}
                ikiwa self.name:
                    r[self.name] = nodes[:count]
                tuma count, r
        lasivyo self.name == "bare_name":
            tuma self._bare_name_matches(nodes)
        isipokua:
            # The reason kila this ni that hitting the recursion limit usually
            # results kwenye some ugly messages about how RuntimeErrors are being
            # ignored. We only have to do this on CPython, though, because other
            # implementations don't have this nasty bug kwenye the first place.
            ikiwa hasattr(sys, "getrefcount"):
                save_stderr = sys.stderr
                sys.stderr = StringIO()
            jaribu:
                kila count, r kwenye self._recursive_matches(nodes, 0):
                    ikiwa self.name:
                        r[self.name] = nodes[:count]
                    tuma count, r
            tatizo RuntimeError:
                # We fall back to the iterative pattern matching scheme ikiwa the recursive
                # scheme hits the recursion limit.
                kila count, r kwenye self._iterative_matches(nodes):
                    ikiwa self.name:
                        r[self.name] = nodes[:count]
                    tuma count, r
            mwishowe:
                ikiwa hasattr(sys, "getrefcount"):
                    sys.stderr = save_stderr

    eleza _iterative_matches(self, nodes):
        """Helper to iteratively tuma the matches."""
        nodelen = len(nodes)
        ikiwa 0 >= self.min:
            tuma 0, {}

        results = []
        # generate matches that use just one alt kutoka self.content
        kila alt kwenye self.content:
            kila c, r kwenye generate_matches(alt, nodes):
                tuma c, r
                results.append((c, r))

        # kila each match, iterate down the nodes
        wakati results:
            new_results = []
            kila c0, r0 kwenye results:
                # stop ikiwa the entire set of nodes has been matched
                ikiwa c0 < nodelen na c0 <= self.max:
                    kila alt kwenye self.content:
                        kila c1, r1 kwenye generate_matches(alt, nodes[c0:]):
                            ikiwa c1 > 0:
                                r = {}
                                r.update(r0)
                                r.update(r1)
                                tuma c0 + c1, r
                                new_results.append((c0 + c1, r))
            results = new_results

    eleza _bare_name_matches(self, nodes):
        """Special optimized matcher kila bare_name."""
        count = 0
        r = {}
        done = Uongo
        max = len(nodes)
        wakati sio done na count < max:
            done = Kweli
            kila leaf kwenye self.content:
                ikiwa leaf[0].match(nodes[count], r):
                    count += 1
                    done = Uongo
                    koma
        r[self.name] = nodes[:count]
        rudisha count, r

    eleza _recursive_matches(self, nodes, count):
        """Helper to recursively tuma the matches."""
        assert self.content ni sio Tupu
        ikiwa count >= self.min:
            tuma 0, {}
        ikiwa count < self.max:
            kila alt kwenye self.content:
                kila c0, r0 kwenye generate_matches(alt, nodes):
                    kila c1, r1 kwenye self._recursive_matches(nodes[c0:], count+1):
                        r = {}
                        r.update(r0)
                        r.update(r1)
                        tuma c0 + c1, r


kundi NegatedPattern(BasePattern):

    eleza __init__(self, content=Tupu):
        """
        Initializer.

        The argument ni either a pattern ama Tupu.  If it ni Tupu, this
        only matches an empty sequence (effectively '$' kwenye regex
        lingo).  If it ni sio Tupu, this matches whenever the argument
        pattern doesn't have any matches.
        """
        ikiwa content ni sio Tupu:
            assert isinstance(content, BasePattern), repr(content)
        self.content = content

    eleza match(self, node):
        # We never match a node kwenye its entirety
        rudisha Uongo

    eleza match_seq(self, nodes):
        # We only match an empty sequence of nodes kwenye its entirety
        rudisha len(nodes) == 0

    eleza generate_matches(self, nodes):
        ikiwa self.content ni Tupu:
            # Return a match ikiwa there ni an empty sequence
            ikiwa len(nodes) == 0:
                tuma 0, {}
        isipokua:
            # Return a match ikiwa the argument pattern has no matches
            kila c, r kwenye self.content.generate_matches(nodes):
                return
            tuma 0, {}


eleza generate_matches(patterns, nodes):
    """
    Generator tumaing matches kila a sequence of patterns na nodes.

    Args:
        patterns: a sequence of patterns
        nodes: a sequence of nodes

    Yields:
        (count, results) tuples where:
        count: the entire sequence of patterns matches nodes[:count];
        results: dict containing named submatches.
        """
    ikiwa sio patterns:
        tuma 0, {}
    isipokua:
        p, rest = patterns[0], patterns[1:]
        kila c0, r0 kwenye p.generate_matches(nodes):
            ikiwa sio rest:
                tuma c0, r0
            isipokua:
                kila c1, r1 kwenye generate_matches(rest, nodes[c0:]):
                    r = {}
                    r.update(r0)
                    r.update(r1)
                    tuma c0 + c1, r
