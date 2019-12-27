# Copyright 2006 Google, Inc. All Rights Reserved.
# Licensed to PSF under a Contributor Agreement.

"""
Python parse tree definitions.

This is a very concrete parse tree; we need to keep every token and
even the comments and whitespace between tokens.

There's also a pattern matching implementation here.
"""

__author__ = "Guido van Rossum <guido@python.org>"

agiza sys
kutoka io agiza StringIO

HUGE = 0x7FFFFFFF  # maximum repeat count, default max

_type_reprs = {}
eleza type_repr(type_num):
    global _type_reprs
    ikiwa not _type_reprs:
        kutoka .pygram agiza python_symbols
        # printing tokens is possible but not as useful
        # kutoka .pgen2 agiza token // token.__dict__.items():
        for name, val in python_symbols.__dict__.items():
            ikiwa type(val) == int: _type_reprs[val] = name
    rudisha _type_reprs.setdefault(type_num, type_num)

kundi Base(object):

    """
    Abstract base kundi for Node and Leaf.

    This provides some default functionality and boilerplate using the
    template pattern.

    A node may be a subnode of at most one parent.
    """

    # Default values for instance variables
    type = None    # int: token number (< 256) or symbol number (>= 256)
    parent = None  # Parent node pointer, or None
    children = ()  # Tuple of subnodes
    was_changed = False
    was_checked = False

    eleza __new__(cls, *args, **kwds):
        """Constructor that prevents Base kutoka being instantiated."""
        assert cls is not Base, "Cannot instantiate Base"
        rudisha object.__new__(cls)

    eleza __eq__(self, other):
        """
        Compare two nodes for equality.

        This calls the method _eq().
        """
        ikiwa self.__class__ is not other.__class__:
            rudisha NotImplemented
        rudisha self._eq(other)

    __hash__ = None # For Py3 compatibility.

    eleza _eq(self, other):
        """
        Compare two nodes for equality.

        This is called by __eq__ and __ne__.  It is only called ikiwa the two nodes
        have the same type.  This must be implemented by the concrete subclass.
        Nodes should be considered equal ikiwa they have the same structure,
        ignoring the prefix string and other context information.
        """
        raise NotImplementedError

    eleza clone(self):
        """
        Return a cloned (deep) copy of self.

        This must be implemented by the concrete subclass.
        """
        raise NotImplementedError

    eleza post_order(self):
        """
        Return a post-order iterator for the tree.

        This must be implemented by the concrete subclass.
        """
        raise NotImplementedError

    eleza pre_order(self):
        """
        Return a pre-order iterator for the tree.

        This must be implemented by the concrete subclass.
        """
        raise NotImplementedError

    eleza replace(self, new):
        """Replace this node with a new one in the parent."""
        assert self.parent is not None, str(self)
        assert new is not None
        ikiwa not isinstance(new, list):
            new = [new]
        l_children = []
        found = False
        for ch in self.parent.children:
            ikiwa ch is self:
                assert not found, (self.parent.children, self, new)
                ikiwa new is not None:
                    l_children.extend(new)
                found = True
            else:
                l_children.append(ch)
        assert found, (self.children, self, new)
        self.parent.changed()
        self.parent.children = l_children
        for x in new:
            x.parent = self.parent
        self.parent = None

    eleza get_lineno(self):
        """Return the line number which generated the invocant node."""
        node = self
        while not isinstance(node, Leaf):
            ikiwa not node.children:
                return
            node = node.children[0]
        rudisha node.lineno

    eleza changed(self):
        ikiwa self.parent:
            self.parent.changed()
        self.was_changed = True

    eleza remove(self):
        """
        Remove the node kutoka the tree. Returns the position of the node in its
        parent's children before it was removed.
        """
        ikiwa self.parent:
            for i, node in enumerate(self.parent.children):
                ikiwa node is self:
                    self.parent.changed()
                    del self.parent.children[i]
                    self.parent = None
                    rudisha i

    @property
    eleza next_sibling(self):
        """
        The node immediately following the invocant in their parent's children
        list. If the invocant does not have a next sibling, it is None
        """
        ikiwa self.parent is None:
            rudisha None

        # Can't use index(); we need to test by identity
        for i, child in enumerate(self.parent.children):
            ikiwa child is self:
                try:
                    rudisha self.parent.children[i+1]
                except IndexError:
                    rudisha None

    @property
    eleza prev_sibling(self):
        """
        The node immediately preceding the invocant in their parent's children
        list. If the invocant does not have a previous sibling, it is None.
        """
        ikiwa self.parent is None:
            rudisha None

        # Can't use index(); we need to test by identity
        for i, child in enumerate(self.parent.children):
            ikiwa child is self:
                ikiwa i == 0:
                    rudisha None
                rudisha self.parent.children[i-1]

    eleza leaves(self):
        for child in self.children:
            yield kutoka child.leaves()

    eleza depth(self):
        ikiwa self.parent is None:
            rudisha 0
        rudisha 1 + self.parent.depth()

    eleza get_suffix(self):
        """
        Return the string immediately following the invocant node. This is
        effectively equivalent to node.next_sibling.prefix
        """
        next_sib = self.next_sibling
        ikiwa next_sib is None:
            rudisha ""
        rudisha next_sib.prefix

    ikiwa sys.version_info < (3, 0):
        eleza __str__(self):
            rudisha str(self).encode("ascii")

kundi Node(Base):

    """Concrete implementation for interior nodes."""

    eleza __init__(self,type, children,
                 context=None,
                 prefix=None,
                 fixers_applied=None):
        """
        Initializer.

        Takes a type constant (a symbol number >= 256), a sequence of
        child nodes, and an optional context keyword argument.

        As a side effect, the parent pointers of the children are updated.
        """
        assert type >= 256, type
        self.type = type
        self.children = list(children)
        for ch in self.children:
            assert ch.parent is None, repr(ch)
            ch.parent = self
        ikiwa prefix is not None:
            self.prefix = prefix
        ikiwa fixers_applied:
            self.fixers_applied = fixers_applied[:]
        else:
            self.fixers_applied = None

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
        """Compare two nodes for equality."""
        rudisha (self.type, self.children) == (other.type, other.children)

    eleza clone(self):
        """Return a cloned (deep) copy of self."""
        rudisha Node(self.type, [ch.clone() for ch in self.children],
                    fixers_applied=self.fixers_applied)

    eleza post_order(self):
        """Return a post-order iterator for the tree."""
        for child in self.children:
            yield kutoka child.post_order()
        yield self

    eleza pre_order(self):
        """Return a pre-order iterator for the tree."""
        yield self
        for child in self.children:
            yield kutoka child.pre_order()

    @property
    eleza prefix(self):
        """
        The whitespace and comments preceding this node in the input.
        """
        ikiwa not self.children:
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
        self.children[i].parent = None
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

    """Concrete implementation for leaf nodes."""

    # Default values for instance variables
    _prefix = ""  # Whitespace and comments preceding this token in the input
    lineno = 0    # Line where this token starts in the input
    column = 0    # Column where this token tarts in the input

    eleza __init__(self, type, value,
                 context=None,
                 prefix=None,
                 fixers_applied=[]):
        """
        Initializer.

        Takes a type constant (a token number < 256), a string value, and an
        optional context keyword argument.
        """
        assert 0 <= type < 256, type
        ikiwa context is not None:
            self._prefix, (self.lineno, self.column) = context
        self.type = type
        self.value = value
        ikiwa prefix is not None:
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
        """Compare two nodes for equality."""
        rudisha (self.type, self.value) == (other.type, other.value)

    eleza clone(self):
        """Return a cloned (deep) copy of self."""
        rudisha Leaf(self.type, self.value,
                    (self.prefix, (self.lineno, self.column)),
                    fixers_applied=self.fixers_applied)

    eleza leaves(self):
        yield self

    eleza post_order(self):
        """Return a post-order iterator for the tree."""
        yield self

    eleza pre_order(self):
        """Return a pre-order iterator for the tree."""
        yield self

    @property
    eleza prefix(self):
        """
        The whitespace and comments preceding this token in the input.
        """
        rudisha self._prefix

    @prefix.setter
    eleza prefix(self, prefix):
        self.changed()
        self._prefix = prefix

eleza convert(gr, raw_node):
    """
    Convert raw node information to a Node or Leaf instance.

    This is passed to the parser driver which calls it whenever a reduction of a
    grammar rule produces a new complete node, so that the tree is build
    strictly bottom-up.
    """
    type, value, context, children = raw_node
    ikiwa children or type in gr.number2symbol:
        # If there's exactly one child, rudisha that child instead of
        # creating a new node.
        ikiwa len(children) == 1:
            rudisha children[0]
        rudisha Node(type, children, context=context)
    else:
        rudisha Leaf(type, value, context=context)


kundi BasePattern(object):

    """
    A pattern is a tree matching pattern.

    It looks for a specific node type (token or symbol), and
    optionally for a specific content.

    This is an abstract base class.  There are three concrete
    subclasses:

    - LeafPattern matches a single leaf node;
    - NodePattern matches a single node (usually non-leaf);
    - WildcardPattern matches a sequence of nodes of variable length.
    """

    # Defaults for instance variables
    type = None     # Node type (token ikiwa < 256, symbol ikiwa >= 256)
    content = None  # Optional content matching pattern
    name = None     # Optional name used to store match in results dict

    eleza __new__(cls, *args, **kwds):
        """Constructor that prevents BasePattern kutoka being instantiated."""
        assert cls is not BasePattern, "Cannot instantiate BasePattern"
        rudisha object.__new__(cls)

    eleza __repr__(self):
        args = [type_repr(self.type), self.content, self.name]
        while args and args[-1] is None:
            del args[-1]
        rudisha "%s(%s)" % (self.__class__.__name__, ", ".join(map(repr, args)))

    eleza optimize(self):
        """
        A subkundi can define this as a hook for optimizations.

        Returns either self or another node with the same effect.
        """
        rudisha self

    eleza match(self, node, results=None):
        """
        Does this pattern exactly match a node?

        Returns True ikiwa it matches, False ikiwa not.

        If results is not None, it must be a dict which will be
        updated with the nodes matching named subpatterns.

        Default implementation for non-wildcard patterns.
        """
        ikiwa self.type is not None and node.type != self.type:
            rudisha False
        ikiwa self.content is not None:
            r = None
            ikiwa results is not None:
                r = {}
            ikiwa not self._submatch(node, r):
                rudisha False
            ikiwa r:
                results.update(r)
        ikiwa results is not None and self.name:
            results[self.name] = node
        rudisha True

    eleza match_seq(self, nodes, results=None):
        """
        Does this pattern exactly match a sequence of nodes?

        Default implementation for non-wildcard patterns.
        """
        ikiwa len(nodes) != 1:
            rudisha False
        rudisha self.match(nodes[0], results)

    eleza generate_matches(self, nodes):
        """
        Generator yielding all matches for this pattern.

        Default implementation for non-wildcard patterns.
        """
        r = {}
        ikiwa nodes and self.match(nodes[0], r):
            yield 1, r


kundi LeafPattern(BasePattern):

    eleza __init__(self, type=None, content=None, name=None):
        """
        Initializer.  Takes optional type, content, and name.

        The type, ikiwa given must be a token type (< 256).  If not given,
        this matches any *leaf* node; the content may still be required.

        The content, ikiwa given, must be a string.

        If a name is given, the matching node is stored in the results
        dict under that key.
        """
        ikiwa type is not None:
            assert 0 <= type < 256, type
        ikiwa content is not None:
            assert isinstance(content, str), repr(content)
        self.type = type
        self.content = content
        self.name = name

    eleza match(self, node, results=None):
        """Override match() to insist on a leaf node."""
        ikiwa not isinstance(node, Leaf):
            rudisha False
        rudisha BasePattern.match(self, node, results)

    eleza _submatch(self, node, results=None):
        """
        Match the pattern's content to the node's children.

        This assumes the node type matches and self.content is not None.

        Returns True ikiwa it matches, False ikiwa not.

        If results is not None, it must be a dict which will be
        updated with the nodes matching named subpatterns.

        When returning False, the results dict may still be updated.
        """
        rudisha self.content == node.value


kundi NodePattern(BasePattern):

    wildcards = False

    eleza __init__(self, type=None, content=None, name=None):
        """
        Initializer.  Takes optional type, content, and name.

        The type, ikiwa given, must be a symbol type (>= 256).  If the
        type is None this matches *any* single node (leaf or not),
        except ikiwa content is not None, in which it only matches
        non-leaf nodes that also match the content pattern.

        The content, ikiwa not None, must be a sequence of Patterns that
        must match the node's children exactly.  If the content is
        given, the type must not be None.

        If a name is given, the matching node is stored in the results
        dict under that key.
        """
        ikiwa type is not None:
            assert type >= 256, type
        ikiwa content is not None:
            assert not isinstance(content, str), repr(content)
            content = list(content)
            for i, item in enumerate(content):
                assert isinstance(item, BasePattern), (i, item)
                ikiwa isinstance(item, WildcardPattern):
                    self.wildcards = True
        self.type = type
        self.content = content
        self.name = name

    eleza _submatch(self, node, results=None):
        """
        Match the pattern's content to the node's children.

        This assumes the node type matches and self.content is not None.

        Returns True ikiwa it matches, False ikiwa not.

        If results is not None, it must be a dict which will be
        updated with the nodes matching named subpatterns.

        When returning False, the results dict may still be updated.
        """
        ikiwa self.wildcards:
            for c, r in generate_matches(self.content, node.children):
                ikiwa c == len(node.children):
                    ikiwa results is not None:
                        results.update(r)
                    rudisha True
            rudisha False
        ikiwa len(self.content) != len(node.children):
            rudisha False
        for subpattern, child in zip(self.content, node.children):
            ikiwa not subpattern.match(child, results):
                rudisha False
        rudisha True


kundi WildcardPattern(BasePattern):

    """
    A wildcard pattern can match zero or more nodes.

    This has all the flexibility needed to implement patterns like:

    .*      .+      .?      .{m,n}
    (a b c | d e | f)
    (...)*  (...)+  (...)?  (...){m,n}

    except it always uses non-greedy matching.
    """

    eleza __init__(self, content=None, min=0, max=HUGE, name=None):
        """
        Initializer.

        Args:
            content: optional sequence of subsequences of patterns;
                     ikiwa absent, matches one node;
                     ikiwa present, each subsequence is an alternative [*]
            min: optional minimum number of times to match, default 0
            max: optional maximum number of times to match, default HUGE
            name: optional name assigned to this match

        [*] Thus, ikiwa content is [[a, b, c], [d, e], [f, g, h]] this is
            equivalent to (a b c | d e | f g h); ikiwa content is None,
            this is equivalent to '.' in regular expression terms.
            The min and max parameters work as follows:
                min=0, max=maxint: .*
                min=1, max=maxint: .+
                min=0, max=1: .?
                min=1, max=1: .
            If content is not None, replace the dot with the parenthesized
            list of alternatives, e.g. (a b c | d e | f g h)*
        """
        assert 0 <= min <= max <= HUGE, (min, max)
        ikiwa content is not None:
            content = tuple(map(tuple, content))  # Protect against alterations
            # Check sanity of alternatives
            assert len(content), repr(content)  # Can't have zero alternatives
            for alt in content:
                assert len(alt), repr(alt) # Can have empty alternatives
        self.content = content
        self.min = min
        self.max = max
        self.name = name

    eleza optimize(self):
        """Optimize certain stacked wildcard patterns."""
        subpattern = None
        ikiwa (self.content is not None and
            len(self.content) == 1 and len(self.content[0]) == 1):
            subpattern = self.content[0][0]
        ikiwa self.min == 1 and self.max == 1:
            ikiwa self.content is None:
                rudisha NodePattern(name=self.name)
            ikiwa subpattern is not None and  self.name == subpattern.name:
                rudisha subpattern.optimize()
        ikiwa (self.min <= 1 and isinstance(subpattern, WildcardPattern) and
            subpattern.min <= 1 and self.name == subpattern.name):
            rudisha WildcardPattern(subpattern.content,
                                   self.min*subpattern.min,
                                   self.max*subpattern.max,
                                   subpattern.name)
        rudisha self

    eleza match(self, node, results=None):
        """Does this pattern exactly match a node?"""
        rudisha self.match_seq([node], results)

    eleza match_seq(self, nodes, results=None):
        """Does this pattern exactly match a sequence of nodes?"""
        for c, r in self.generate_matches(nodes):
            ikiwa c == len(nodes):
                ikiwa results is not None:
                    results.update(r)
                    ikiwa self.name:
                        results[self.name] = list(nodes)
                rudisha True
        rudisha False

    eleza generate_matches(self, nodes):
        """
        Generator yielding matches for a sequence of nodes.

        Args:
            nodes: sequence of nodes

        Yields:
            (count, results) tuples where:
            count: the match comprises nodes[:count];
            results: dict containing named submatches.
        """
        ikiwa self.content is None:
            # Shortcut for special case (see __init__.__doc__)
            for count in range(self.min, 1 + min(len(nodes), self.max)):
                r = {}
                ikiwa self.name:
                    r[self.name] = nodes[:count]
                yield count, r
        elikiwa self.name == "bare_name":
            yield self._bare_name_matches(nodes)
        else:
            # The reason for this is that hitting the recursion limit usually
            # results in some ugly messages about how RuntimeErrors are being
            # ignored. We only have to do this on CPython, though, because other
            # implementations don't have this nasty bug in the first place.
            ikiwa hasattr(sys, "getrefcount"):
                save_stderr = sys.stderr
                sys.stderr = StringIO()
            try:
                for count, r in self._recursive_matches(nodes, 0):
                    ikiwa self.name:
                        r[self.name] = nodes[:count]
                    yield count, r
            except RuntimeError:
                # We fall back to the iterative pattern matching scheme ikiwa the recursive
                # scheme hits the recursion limit.
                for count, r in self._iterative_matches(nodes):
                    ikiwa self.name:
                        r[self.name] = nodes[:count]
                    yield count, r
            finally:
                ikiwa hasattr(sys, "getrefcount"):
                    sys.stderr = save_stderr

    eleza _iterative_matches(self, nodes):
        """Helper to iteratively yield the matches."""
        nodelen = len(nodes)
        ikiwa 0 >= self.min:
            yield 0, {}

        results = []
        # generate matches that use just one alt kutoka self.content
        for alt in self.content:
            for c, r in generate_matches(alt, nodes):
                yield c, r
                results.append((c, r))

        # for each match, iterate down the nodes
        while results:
            new_results = []
            for c0, r0 in results:
                # stop ikiwa the entire set of nodes has been matched
                ikiwa c0 < nodelen and c0 <= self.max:
                    for alt in self.content:
                        for c1, r1 in generate_matches(alt, nodes[c0:]):
                            ikiwa c1 > 0:
                                r = {}
                                r.update(r0)
                                r.update(r1)
                                yield c0 + c1, r
                                new_results.append((c0 + c1, r))
            results = new_results

    eleza _bare_name_matches(self, nodes):
        """Special optimized matcher for bare_name."""
        count = 0
        r = {}
        done = False
        max = len(nodes)
        while not done and count < max:
            done = True
            for leaf in self.content:
                ikiwa leaf[0].match(nodes[count], r):
                    count += 1
                    done = False
                    break
        r[self.name] = nodes[:count]
        rudisha count, r

    eleza _recursive_matches(self, nodes, count):
        """Helper to recursively yield the matches."""
        assert self.content is not None
        ikiwa count >= self.min:
            yield 0, {}
        ikiwa count < self.max:
            for alt in self.content:
                for c0, r0 in generate_matches(alt, nodes):
                    for c1, r1 in self._recursive_matches(nodes[c0:], count+1):
                        r = {}
                        r.update(r0)
                        r.update(r1)
                        yield c0 + c1, r


kundi NegatedPattern(BasePattern):

    eleza __init__(self, content=None):
        """
        Initializer.

        The argument is either a pattern or None.  If it is None, this
        only matches an empty sequence (effectively '$' in regex
        lingo).  If it is not None, this matches whenever the argument
        pattern doesn't have any matches.
        """
        ikiwa content is not None:
            assert isinstance(content, BasePattern), repr(content)
        self.content = content

    eleza match(self, node):
        # We never match a node in its entirety
        rudisha False

    eleza match_seq(self, nodes):
        # We only match an empty sequence of nodes in its entirety
        rudisha len(nodes) == 0

    eleza generate_matches(self, nodes):
        ikiwa self.content is None:
            # Return a match ikiwa there is an empty sequence
            ikiwa len(nodes) == 0:
                yield 0, {}
        else:
            # Return a match ikiwa the argument pattern has no matches
            for c, r in self.content.generate_matches(nodes):
                return
            yield 0, {}


eleza generate_matches(patterns, nodes):
    """
    Generator yielding matches for a sequence of patterns and nodes.

    Args:
        patterns: a sequence of patterns
        nodes: a sequence of nodes

    Yields:
        (count, results) tuples where:
        count: the entire sequence of patterns matches nodes[:count];
        results: dict containing named submatches.
        """
    ikiwa not patterns:
        yield 0, {}
    else:
        p, rest = patterns[0], patterns[1:]
        for c0, r0 in p.generate_matches(nodes):
            ikiwa not rest:
                yield c0, r0
            else:
                for c1, r1 in generate_matches(rest, nodes[c0:]):
                    r = {}
                    r.update(r0)
                    r.update(r1)
                    yield c0 + c1, r
