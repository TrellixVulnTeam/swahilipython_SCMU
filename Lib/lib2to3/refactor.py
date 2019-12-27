# Copyright 2006 Google, Inc. All Rights Reserved.
# Licensed to PSF under a Contributor Agreement.

"""Refactoring framework.

Used as a main program, this can refactor any number of files and/or
recursively descend down directories.  Imported as a module, this
provides infrastructure to write your own refactoring tool.
"""

__author__ = "Guido van Rossum <guido@python.org>"


# Python agizas
agiza io
agiza os
agiza pkgutil
agiza sys
agiza logging
agiza operator
agiza collections
kutoka itertools agiza chain

# Local agizas
kutoka .pgen2 agiza driver, tokenize, token
kutoka .fixer_util agiza find_root
kutoka . agiza pytree, pygram
kutoka . agiza btm_matcher as bm


eleza get_all_fix_names(fixer_pkg, remove_prefix=True):
    """Return a sorted list of all available fix names in the given package."""
    pkg = __import__(fixer_pkg, [], [], ["*"])
    fix_names = []
    for finder, name, ispkg in pkgutil.iter_modules(pkg.__path__):
        ikiwa name.startswith("fix_"):
            ikiwa remove_prefix:
                name = name[4:]
            fix_names.append(name)
    rudisha fix_names


kundi _EveryNode(Exception):
    pass


eleza _get_head_types(pat):
    """ Accepts a pytree Pattern Node and returns a set
        of the pattern types which will match first. """

    ikiwa isinstance(pat, (pytree.NodePattern, pytree.LeafPattern)):
        # NodePatters must either have no type and no content
        #   or a type and content -- so they don't get any farther
        # Always rudisha leafs
        ikiwa pat.type is None:
            raise _EveryNode
        rudisha {pat.type}

    ikiwa isinstance(pat, pytree.NegatedPattern):
        ikiwa pat.content:
            rudisha _get_head_types(pat.content)
        raise _EveryNode # Negated Patterns don't have a type

    ikiwa isinstance(pat, pytree.WildcardPattern):
        # Recurse on each node in content
        r = set()
        for p in pat.content:
            for x in p:
                r.update(_get_head_types(x))
        rudisha r

    raise Exception("Oh no! I don't understand pattern %s" %(pat))


eleza _get_headnode_dict(fixer_list):
    """ Accepts a list of fixers and returns a dictionary
        of head node type --> fixer list.  """
    head_nodes = collections.defaultdict(list)
    every = []
    for fixer in fixer_list:
        ikiwa fixer.pattern:
            try:
                heads = _get_head_types(fixer.pattern)
            except _EveryNode:
                every.append(fixer)
            else:
                for node_type in heads:
                    head_nodes[node_type].append(fixer)
        else:
            ikiwa fixer._accept_type is not None:
                head_nodes[fixer._accept_type].append(fixer)
            else:
                every.append(fixer)
    for node_type in chain(pygram.python_grammar.symbol2number.values(),
                           pygram.python_grammar.tokens):
        head_nodes[node_type].extend(every)
    rudisha dict(head_nodes)


eleza get_fixers_kutoka_package(pkg_name):
    """
    Return the fully qualified names for fixers in the package pkg_name.
    """
    rudisha [pkg_name + "." + fix_name
            for fix_name in get_all_fix_names(pkg_name, False)]

eleza _identity(obj):
    rudisha obj


eleza _detect_future_features(source):
    have_docstring = False
    gen = tokenize.generate_tokens(io.StringIO(source).readline)
    eleza advance():
        tok = next(gen)
        rudisha tok[0], tok[1]
    ignore = frozenset({token.NEWLINE, tokenize.NL, token.COMMENT})
    features = set()
    try:
        while True:
            tp, value = advance()
            ikiwa tp in ignore:
                continue
            elikiwa tp == token.STRING:
                ikiwa have_docstring:
                    break
                have_docstring = True
            elikiwa tp == token.NAME and value == "kutoka":
                tp, value = advance()
                ikiwa tp != token.NAME or value != "__future__":
                    break
                tp, value = advance()
                ikiwa tp != token.NAME or value != "agiza":
                    break
                tp, value = advance()
                ikiwa tp == token.OP and value == "(":
                    tp, value = advance()
                while tp == token.NAME:
                    features.add(value)
                    tp, value = advance()
                    ikiwa tp != token.OP or value != ",":
                        break
                    tp, value = advance()
            else:
                break
    except StopIteration:
        pass
    rudisha frozenset(features)


kundi FixerError(Exception):
    """A fixer could not be loaded."""


kundi RefactoringTool(object):

    _default_options = {"print_function" : False,
                        "write_unchanged_files" : False}

    CLASS_PREFIX = "Fix" # The prefix for fixer classes
    FILE_PREFIX = "fix_" # The prefix for modules with a fixer within

    eleza __init__(self, fixer_names, options=None, explicit=None):
        """Initializer.

        Args:
            fixer_names: a list of fixers to agiza
            options: a dict with configuration.
            explicit: a list of fixers to run even ikiwa they are explicit.
        """
        self.fixers = fixer_names
        self.explicit = explicit or []
        self.options = self._default_options.copy()
        ikiwa options is not None:
            self.options.update(options)
        ikiwa self.options["print_function"]:
            self.grammar = pygram.python_grammar_no_print_statement
        else:
            self.grammar = pygram.python_grammar
        # When this is True, the refactor*() methods will call write_file() for
        # files processed even ikiwa they were not changed during refactoring. If
        # and only ikiwa the refactor method's write parameter was True.
        self.write_unchanged_files = self.options.get("write_unchanged_files")
        self.errors = []
        self.logger = logging.getLogger("RefactoringTool")
        self.fixer_log = []
        self.wrote = False
        self.driver = driver.Driver(self.grammar,
                                    convert=pytree.convert,
                                    logger=self.logger)
        self.pre_order, self.post_order = self.get_fixers()


        self.files = []  # List of files that were or should be modified

        self.BM = bm.BottomMatcher()
        self.bmi_pre_order = [] # Bottom Matcher incompatible fixers
        self.bmi_post_order = []

        for fixer in chain(self.post_order, self.pre_order):
            ikiwa fixer.BM_compatible:
                self.BM.add_fixer(fixer)
                # remove fixers that will be handled by the bottom-up
                # matcher
            elikiwa fixer in self.pre_order:
                self.bmi_pre_order.append(fixer)
            elikiwa fixer in self.post_order:
                self.bmi_post_order.append(fixer)

        self.bmi_pre_order_heads = _get_headnode_dict(self.bmi_pre_order)
        self.bmi_post_order_heads = _get_headnode_dict(self.bmi_post_order)



    eleza get_fixers(self):
        """Inspects the options to load the requested patterns and handlers.

        Returns:
          (pre_order, post_order), where pre_order is the list of fixers that
          want a pre-order AST traversal, and post_order is the list that want
          post-order traversal.
        """
        pre_order_fixers = []
        post_order_fixers = []
        for fix_mod_path in self.fixers:
            mod = __import__(fix_mod_path, {}, {}, ["*"])
            fix_name = fix_mod_path.rsplit(".", 1)[-1]
            ikiwa fix_name.startswith(self.FILE_PREFIX):
                fix_name = fix_name[len(self.FILE_PREFIX):]
            parts = fix_name.split("_")
            class_name = self.CLASS_PREFIX + "".join([p.title() for p in parts])
            try:
                fix_kundi = getattr(mod, class_name)
            except AttributeError:
                raise FixerError("Can't find %s.%s" % (fix_name, class_name)) kutoka None
            fixer = fix_class(self.options, self.fixer_log)
            ikiwa fixer.explicit and self.explicit is not True and \
                    fix_mod_path not in self.explicit:
                self.log_message("Skipping optional fixer: %s", fix_name)
                continue

            self.log_debug("Adding transformation: %s", fix_name)
            ikiwa fixer.order == "pre":
                pre_order_fixers.append(fixer)
            elikiwa fixer.order == "post":
                post_order_fixers.append(fixer)
            else:
                raise FixerError("Illegal fixer order: %r" % fixer.order)

        key_func = operator.attrgetter("run_order")
        pre_order_fixers.sort(key=key_func)
        post_order_fixers.sort(key=key_func)
        rudisha (pre_order_fixers, post_order_fixers)

    eleza log_error(self, msg, *args, **kwds):
        """Called when an error occurs."""
        raise

    eleza log_message(self, msg, *args):
        """Hook to log a message."""
        ikiwa args:
            msg = msg % args
        self.logger.info(msg)

    eleza log_debug(self, msg, *args):
        ikiwa args:
            msg = msg % args
        self.logger.debug(msg)

    eleza print_output(self, old_text, new_text, filename, equal):
        """Called with the old version, new version, and filename of a
        refactored file."""
        pass

    eleza refactor(self, items, write=False, doctests_only=False):
        """Refactor a list of files and directories."""

        for dir_or_file in items:
            ikiwa os.path.isdir(dir_or_file):
                self.refactor_dir(dir_or_file, write, doctests_only)
            else:
                self.refactor_file(dir_or_file, write, doctests_only)

    eleza refactor_dir(self, dir_name, write=False, doctests_only=False):
        """Descends down a directory and refactor every Python file found.

        Python files are assumed to have a .py extension.

        Files and subdirectories starting with '.' are skipped.
        """
        py_ext = os.extsep + "py"
        for dirpath, dirnames, filenames in os.walk(dir_name):
            self.log_debug("Descending into %s", dirpath)
            dirnames.sort()
            filenames.sort()
            for name in filenames:
                ikiwa (not name.startswith(".") and
                    os.path.splitext(name)[1] == py_ext):
                    fullname = os.path.join(dirpath, name)
                    self.refactor_file(fullname, write, doctests_only)
            # Modify dirnames in-place to remove subdirs with leading dots
            dirnames[:] = [dn for dn in dirnames ikiwa not dn.startswith(".")]

    eleza _read_python_source(self, filename):
        """
        Do our best to decode a Python source file correctly.
        """
        try:
            f = open(filename, "rb")
        except OSError as err:
            self.log_error("Can't open %s: %s", filename, err)
            rudisha None, None
        try:
            encoding = tokenize.detect_encoding(f.readline)[0]
        finally:
            f.close()
        with io.open(filename, "r", encoding=encoding, newline='') as f:
            rudisha f.read(), encoding

    eleza refactor_file(self, filename, write=False, doctests_only=False):
        """Refactors a file."""
        input, encoding = self._read_python_source(filename)
        ikiwa input is None:
            # Reading the file failed.
            return
        input += "\n" # Silence certain parse errors
        ikiwa doctests_only:
            self.log_debug("Refactoring doctests in %s", filename)
            output = self.refactor_docstring(input, filename)
            ikiwa self.write_unchanged_files or output != input:
                self.processed_file(output, filename, input, write, encoding)
            else:
                self.log_debug("No doctest changes in %s", filename)
        else:
            tree = self.refactor_string(input, filename)
            ikiwa self.write_unchanged_files or (tree and tree.was_changed):
                # The [:-1] is to take off the \n we added earlier
                self.processed_file(str(tree)[:-1], filename,
                                    write=write, encoding=encoding)
            else:
                self.log_debug("No changes in %s", filename)

    eleza refactor_string(self, data, name):
        """Refactor a given input string.

        Args:
            data: a string holding the code to be refactored.
            name: a human-readable name for use in error/log messages.

        Returns:
            An AST corresponding to the refactored input stream; None if
            there were errors during the parse.
        """
        features = _detect_future_features(data)
        ikiwa "print_function" in features:
            self.driver.grammar = pygram.python_grammar_no_print_statement
        try:
            tree = self.driver.parse_string(data)
        except Exception as err:
            self.log_error("Can't parse %s: %s: %s",
                           name, err.__class__.__name__, err)
            return
        finally:
            self.driver.grammar = self.grammar
        tree.future_features = features
        self.log_debug("Refactoring %s", name)
        self.refactor_tree(tree, name)
        rudisha tree

    eleza refactor_stdin(self, doctests_only=False):
        input = sys.stdin.read()
        ikiwa doctests_only:
            self.log_debug("Refactoring doctests in stdin")
            output = self.refactor_docstring(input, "<stdin>")
            ikiwa self.write_unchanged_files or output != input:
                self.processed_file(output, "<stdin>", input)
            else:
                self.log_debug("No doctest changes in stdin")
        else:
            tree = self.refactor_string(input, "<stdin>")
            ikiwa self.write_unchanged_files or (tree and tree.was_changed):
                self.processed_file(str(tree), "<stdin>", input)
            else:
                self.log_debug("No changes in stdin")

    eleza refactor_tree(self, tree, name):
        """Refactors a parse tree (modifying the tree in place).

        For compatible patterns the bottom matcher module is
        used. Otherwise the tree is traversed node-to-node for
        matches.

        Args:
            tree: a pytree.Node instance representing the root of the tree
                  to be refactored.
            name: a human-readable name for this tree.

        Returns:
            True ikiwa the tree was modified, False otherwise.
        """

        for fixer in chain(self.pre_order, self.post_order):
            fixer.start_tree(tree, name)

        #use traditional matching for the incompatible fixers
        self.traverse_by(self.bmi_pre_order_heads, tree.pre_order())
        self.traverse_by(self.bmi_post_order_heads, tree.post_order())

        # obtain a set of candidate nodes
        match_set = self.BM.run(tree.leaves())

        while any(match_set.values()):
            for fixer in self.BM.fixers:
                ikiwa fixer in match_set and match_set[fixer]:
                    #sort by depth; apply fixers kutoka bottom(of the AST) to top
                    match_set[fixer].sort(key=pytree.Base.depth, reverse=True)

                    ikiwa fixer.keep_line_order:
                        #some fixers(eg fix_agizas) must be applied
                        #with the original file's line order
                        match_set[fixer].sort(key=pytree.Base.get_lineno)

                    for node in list(match_set[fixer]):
                        ikiwa node in match_set[fixer]:
                            match_set[fixer].remove(node)

                        try:
                            find_root(node)
                        except ValueError:
                            # this node has been cut off kutoka a
                            # previous transformation ; skip
                            continue

                        ikiwa node.fixers_applied and fixer in node.fixers_applied:
                            # do not apply the same fixer again
                            continue

                        results = fixer.match(node)

                        ikiwa results:
                            new = fixer.transform(node, results)
                            ikiwa new is not None:
                                node.replace(new)
                                #new.fixers_applied.append(fixer)
                                for node in new.post_order():
                                    # do not apply the fixer again to
                                    # this or any subnode
                                    ikiwa not node.fixers_applied:
                                        node.fixers_applied = []
                                    node.fixers_applied.append(fixer)

                                # update the original match set for
                                # the added code
                                new_matches = self.BM.run(new.leaves())
                                for fxr in new_matches:
                                    ikiwa not fxr in match_set:
                                        match_set[fxr]=[]

                                    match_set[fxr].extend(new_matches[fxr])

        for fixer in chain(self.pre_order, self.post_order):
            fixer.finish_tree(tree, name)
        rudisha tree.was_changed

    eleza traverse_by(self, fixers, traversal):
        """Traverse an AST, applying a set of fixers to each node.

        This is a helper method for refactor_tree().

        Args:
            fixers: a list of fixer instances.
            traversal: a generator that yields AST nodes.

        Returns:
            None
        """
        ikiwa not fixers:
            return
        for node in traversal:
            for fixer in fixers[node.type]:
                results = fixer.match(node)
                ikiwa results:
                    new = fixer.transform(node, results)
                    ikiwa new is not None:
                        node.replace(new)
                        node = new

    eleza processed_file(self, new_text, filename, old_text=None, write=False,
                       encoding=None):
        """
        Called when a file has been refactored and there may be changes.
        """
        self.files.append(filename)
        ikiwa old_text is None:
            old_text = self._read_python_source(filename)[0]
            ikiwa old_text is None:
                return
        equal = old_text == new_text
        self.print_output(old_text, new_text, filename, equal)
        ikiwa equal:
            self.log_debug("No changes to %s", filename)
            ikiwa not self.write_unchanged_files:
                return
        ikiwa write:
            self.write_file(new_text, filename, old_text, encoding)
        else:
            self.log_debug("Not writing changes to %s", filename)

    eleza write_file(self, new_text, filename, old_text, encoding=None):
        """Writes a string to a file.

        It first shows a unified diff between the old text and the new text, and
        then rewrites the file; the latter is only done ikiwa the write option is
        set.
        """
        try:
            fp = io.open(filename, "w", encoding=encoding, newline='')
        except OSError as err:
            self.log_error("Can't create %s: %s", filename, err)
            return

        with fp:
            try:
                fp.write(new_text)
            except OSError as err:
                self.log_error("Can't write %s: %s", filename, err)
        self.log_debug("Wrote changes to %s", filename)
        self.wrote = True

    PS1 = ">>> "
    PS2 = "... "

    eleza refactor_docstring(self, input, filename):
        """Refactors a docstring, looking for doctests.

        This returns a modified version of the input string.  It looks
        for doctests, which start with a ">>>" prompt, and may be
        continued with "..." prompts, as long as the "..." is indented
        the same as the ">>>".

        (Unfortunately we can't use the doctest module's parser,
        since, like most parsers, it is not geared towards preserving
        the original source.)
        """
        result = []
        block = None
        block_lineno = None
        indent = None
        lineno = 0
        for line in input.splitlines(keepends=True):
            lineno += 1
            ikiwa line.lstrip().startswith(self.PS1):
                ikiwa block is not None:
                    result.extend(self.refactor_doctest(block, block_lineno,
                                                        indent, filename))
                block_lineno = lineno
                block = [line]
                i = line.find(self.PS1)
                indent = line[:i]
            elikiwa (indent is not None and
                  (line.startswith(indent + self.PS2) or
                   line == indent + self.PS2.rstrip() + "\n")):
                block.append(line)
            else:
                ikiwa block is not None:
                    result.extend(self.refactor_doctest(block, block_lineno,
                                                        indent, filename))
                block = None
                indent = None
                result.append(line)
        ikiwa block is not None:
            result.extend(self.refactor_doctest(block, block_lineno,
                                                indent, filename))
        rudisha "".join(result)

    eleza refactor_doctest(self, block, lineno, indent, filename):
        """Refactors one doctest.

        A doctest is given as a block of lines, the first of which starts
        with ">>>" (possibly indented), while the remaining lines start
        with "..." (identically indented).

        """
        try:
            tree = self.parse_block(block, lineno, indent)
        except Exception as err:
            ikiwa self.logger.isEnabledFor(logging.DEBUG):
                for line in block:
                    self.log_debug("Source: %s", line.rstrip("\n"))
            self.log_error("Can't parse docstring in %s line %s: %s: %s",
                           filename, lineno, err.__class__.__name__, err)
            rudisha block
        ikiwa self.refactor_tree(tree, filename):
            new = str(tree).splitlines(keepends=True)
            # Undo the adjustment of the line numbers in wrap_toks() below.
            clipped, new = new[:lineno-1], new[lineno-1:]
            assert clipped == ["\n"] * (lineno-1), clipped
            ikiwa not new[-1].endswith("\n"):
                new[-1] += "\n"
            block = [indent + self.PS1 + new.pop(0)]
            ikiwa new:
                block += [indent + self.PS2 + line for line in new]
        rudisha block

    eleza summarize(self):
        ikiwa self.wrote:
            were = "were"
        else:
            were = "need to be"
        ikiwa not self.files:
            self.log_message("No files %s modified.", were)
        else:
            self.log_message("Files that %s modified:", were)
            for file in self.files:
                self.log_message(file)
        ikiwa self.fixer_log:
            self.log_message("Warnings/messages while refactoring:")
            for message in self.fixer_log:
                self.log_message(message)
        ikiwa self.errors:
            ikiwa len(self.errors) == 1:
                self.log_message("There was 1 error:")
            else:
                self.log_message("There were %d errors:", len(self.errors))
            for msg, args, kwds in self.errors:
                self.log_message(msg, *args, **kwds)

    eleza parse_block(self, block, lineno, indent):
        """Parses a block into a tree.

        This is necessary to get correct line number / offset information
        in the parser diagnostics and embedded into the parse tree.
        """
        tree = self.driver.parse_tokens(self.wrap_toks(block, lineno, indent))
        tree.future_features = frozenset()
        rudisha tree

    eleza wrap_toks(self, block, lineno, indent):
        """Wraps a tokenize stream to systematically modify start/end."""
        tokens = tokenize.generate_tokens(self.gen_lines(block, indent).__next__)
        for type, value, (line0, col0), (line1, col1), line_text in tokens:
            line0 += lineno - 1
            line1 += lineno - 1
            # Don't bother updating the columns; this is too complicated
            # since line_text would also have to be updated and it would
            # still break for tokens spanning lines.  Let the user guess
            # that the column numbers for doctests are relative to the
            # end of the prompt string (PS1 or PS2).
            yield type, value, (line0, col0), (line1, col1), line_text


    eleza gen_lines(self, block, indent):
        """Generates lines as expected by tokenize kutoka a list of lines.

        This strips the first len(indent + self.PS1) characters off each line.
        """
        prefix1 = indent + self.PS1
        prefix2 = indent + self.PS2
        prefix = prefix1
        for line in block:
            ikiwa line.startswith(prefix):
                yield line[len(prefix):]
            elikiwa line == prefix.rstrip() + "\n":
                yield "\n"
            else:
                raise AssertionError("line=%r, prefix=%r" % (line, prefix))
            prefix = prefix2
        while True:
            yield ""


kundi MultiprocessingUnsupported(Exception):
    pass


kundi MultiprocessRefactoringTool(RefactoringTool):

    eleza __init__(self, *args, **kwargs):
        super(MultiprocessRefactoringTool, self).__init__(*args, **kwargs)
        self.queue = None
        self.output_lock = None

    eleza refactor(self, items, write=False, doctests_only=False,
                 num_processes=1):
        ikiwa num_processes == 1:
            rudisha super(MultiprocessRefactoringTool, self).refactor(
                items, write, doctests_only)
        try:
            agiza multiprocessing
        except ImportError:
            raise MultiprocessingUnsupported
        ikiwa self.queue is not None:
            raise RuntimeError("already doing multiple processes")
        self.queue = multiprocessing.JoinableQueue()
        self.output_lock = multiprocessing.Lock()
        processes = [multiprocessing.Process(target=self._child)
                     for i in range(num_processes)]
        try:
            for p in processes:
                p.start()
            super(MultiprocessRefactoringTool, self).refactor(items, write,
                                                              doctests_only)
        finally:
            self.queue.join()
            for i in range(num_processes):
                self.queue.put(None)
            for p in processes:
                ikiwa p.is_alive():
                    p.join()
            self.queue = None

    eleza _child(self):
        task = self.queue.get()
        while task is not None:
            args, kwargs = task
            try:
                super(MultiprocessRefactoringTool, self).refactor_file(
                    *args, **kwargs)
            finally:
                self.queue.task_done()
            task = self.queue.get()

    eleza refactor_file(self, *args, **kwargs):
        ikiwa self.queue is not None:
            self.queue.put((args, kwargs))
        else:
            rudisha super(MultiprocessRefactoringTool, self).refactor_file(
                *args, **kwargs)
