# Copyright 2006 Google, Inc. All Rights Reserved.
# Licensed to PSF under a Contributor Agreement.

"""Base kundi kila fixers (optional, but recommended)."""

# Python agizas
agiza itertools

# Local agizas
kutoka .patcomp agiza PatternCompiler
kutoka . agiza pygram
kutoka .fixer_util agiza does_tree_agiza

kundi BaseFix(object):

    """Optional base kundi kila fixers.

    The subkundi name must be FixFooBar where FooBar ni the result of
    removing underscores na capitalizing the words of the fix name.
    For example, the kundi name kila a fixer named 'has_key' should be
    FixHasKey.
    """

    PATTERN = Tupu  # Most subclasses should override with a string literal
    pattern = Tupu  # Compiled pattern, set by compile_pattern()
    pattern_tree = Tupu # Tree representation of the pattern
    options = Tupu  # Options object pitaed to initializer
    filename = Tupu # The filename (set by set_filename)
    numbers = itertools.count(1) # For new_name()
    used_names = set() # A set of all used NAMEs
    order = "post" # Does the fixer prefer pre- ama post-order traversal
    explicit = Uongo # Is this ignored by refactor.py -f all?
    run_order = 5   # Fixers will be sorted by run order before execution
                    # Lower numbers will be run first.
    _accept_type = Tupu # [Advanced na sio public] This tells RefactoringTool
                        # which node type to accept when there's sio a pattern.

    keep_line_order = Uongo # For the bottom matcher: match with the
                            # original line order
    BM_compatible = Uongo # Compatibility with the bottom matching
                          # module; every fixer should set this
                          # manually

    # Shortcut kila access to Python grammar symbols
    syms = pygram.python_symbols

    eleza __init__(self, options, log):
        """Initializer.  Subkundi may override.

        Args:
            options: a dict containing the options pitaed to RefactoringTool
            that could be used to customize the fixer through the command line.
            log: a list to append warnings na other messages to.
        """
        self.options = options
        self.log = log
        self.compile_pattern()

    eleza compile_pattern(self):
        """Compiles self.PATTERN into self.pattern.

        Subkundi may override ikiwa it doesn't want to use
        self.{pattern,PATTERN} kwenye .match().
        """
        ikiwa self.PATTERN ni sio Tupu:
            PC = PatternCompiler()
            self.pattern, self.pattern_tree = PC.compile_pattern(self.PATTERN,
                                                                 with_tree=Kweli)

    eleza set_filename(self, filename):
        """Set the filename.

        The main refactoring tool should call this.
        """
        self.filename = filename

    eleza match(self, node):
        """Returns match kila a given parse tree node.

        Should rudisha a true ama false object (not necessarily a bool).
        It may rudisha a non-empty dict of matching sub-nodes as
        rudishaed by a matching pattern.

        Subkundi may override.
        """
        results = {"node": node}
        rudisha self.pattern.match(node, results) na results

    eleza transform(self, node, results):
        """Returns the transformation kila a given parse tree node.

        Args:
          node: the root of the parse tree that matched the fixer.
          results: a dict mapping symbolic names to part of the match.

        Returns:
          Tupu, ama a node that ni a modified copy of the
          argument node.  The node argument may also be modified in-place to
          effect the same change.

        Subkundi *must* override.
        """
        ashiria NotImplementedError()

    eleza new_name(self, template="xxx_todo_changeme"):
        """Return a string suitable kila use kama an identifier

        The new name ni guaranteed sio to conflict with other identifiers.
        """
        name = template
        wakati name kwenye self.used_names:
            name = template + str(next(self.numbers))
        self.used_names.add(name)
        rudisha name

    eleza log_message(self, message):
        ikiwa self.first_log:
            self.first_log = Uongo
            self.log.append("### In file %s ###" % self.filename)
        self.log.append(message)

    eleza cannot_convert(self, node, reason=Tupu):
        """Warn the user that a given chunk of code ni sio valid Python 3,
        but that it cannot be converted automatically.

        First argument ni the top-level node kila the code kwenye question.
        Optional second argument ni why it can't be converted.
        """
        lineno = node.get_lineno()
        for_output = node.clone()
        for_output.prefix = ""
        msg = "Line %d: could sio convert: %s"
        self.log_message(msg % (lineno, for_output))
        ikiwa reason:
            self.log_message(reason)

    eleza warning(self, node, reason):
        """Used kila warning the user about possible uncertainty kwenye the
        translation.

        First argument ni the top-level node kila the code kwenye question.
        Optional second argument ni why it can't be converted.
        """
        lineno = node.get_lineno()
        self.log_message("Line %d: %s" % (lineno, reason))

    eleza start_tree(self, tree, filename):
        """Some fixers need to maintain tree-wide state.
        This method ni called once, at the start of tree fix-up.

        tree - the root node of the tree to be processed.
        filename - the name of the file the tree came kutoka.
        """
        self.used_names = tree.used_names
        self.set_filename(filename)
        self.numbers = itertools.count(1)
        self.first_log = Kweli

    eleza finish_tree(self, tree, filename):
        """Some fixers need to maintain tree-wide state.
        This method ni called once, at the conclusion of tree fix-up.

        tree - the root node of the tree to be processed.
        filename - the name of the file the tree came kutoka.
        """
        pita


kundi ConditionalFix(BaseFix):
    """ Base kundi kila fixers which sio execute ikiwa an agiza ni found. """

    # This ni the name of the agiza which, ikiwa found, will cause the test to be skipped
    skip_on = Tupu

    eleza start_tree(self, *args):
        super(ConditionalFix, self).start_tree(*args)
        self._should_skip = Tupu

    eleza should_skip(self, node):
        ikiwa self._should_skip ni sio Tupu:
            rudisha self._should_skip
        pkg = self.skip_on.split(".")
        name = pkg[-1]
        pkg = ".".join(pkg[:-1])
        self._should_skip = does_tree_agiza(pkg, name, node)
        rudisha self._should_skip
