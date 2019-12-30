# Copyright 2006 Google, Inc. All Rights Reserved.
# Licensed to PSF under a Contributor Agreement.

"""Refactoring framework.

Used as a main program, this can refactor any number of files and/or
recursively descend down directories.  Imported as a module, this
provides infrastructure to write your own refactoring tool.
"""

__author__ = "Guido van Rossum <guido@python.org>"


# Python imports
agiza io
agiza os
agiza pkgutil
agiza sys
agiza logging
agiza operator
agiza collections
kutoka itertools agiza chain

# Local imports
kutoka .pgen2 agiza driver, tokenize, token
kutoka .fixer_util agiza find_root
kutoka . agiza pytree, pygram
kutoka . agiza btm_matcher as bm


eleza get_all_fix_names(fixer_pkg, remove_prefix=Kweli):
    """Return a sorted list of all available fix names kwenye the given package."""
    pkg = __import__(fixer_pkg, [], [], ["*"])
    fix_names = []
    kila finder, name, ispkg kwenye pkgutil.iter_modules(pkg.__path__):
        ikiwa name.startswith("fix_"):
            ikiwa remove_prefix:
                name = name[4:]
            fix_names.append(name)
    rudisha fix_names


kundi _EveryNode(Exception):
    pass


eleza _get_head_types(pat):
    """ Accepts a pytree Pattern Node na returns a set
        of the pattern types which will match first. """

    ikiwa isinstance(pat, (pytree.NodePattern, pytree.LeafPattern)):
        # NodePatters must either have no type na no content
        #   ama a type na content -- so they don't get any farther
        # Always rudisha leafs
        ikiwa pat.type ni Tupu:
             ashiria _EveryNode
        rudisha {pat.type}

    ikiwa isinstance(pat, pytree.NegatedPattern):
        ikiwa pat.content:
            rudisha _get_head_types(pat.content)
         ashiria _EveryNode # Negated Patterns don't have a type

    ikiwa isinstance(pat, pytree.WildcardPattern):
        # Recurse on each node kwenye content
        r = set()
        kila p kwenye pat.content:
            kila x kwenye p:
                r.update(_get_head_types(x))
        rudisha r

     ashiria Exception("Oh no! I don't understand pattern %s" %(pat))


eleza _get_headnode_dict(fixer_list):
    """ Accepts a list of fixers na returns a dictionary
        of head node type --> fixer list.  """
    head_nodes = collections.defaultdict(list)
    every = []
    kila fixer kwenye fixer_list:
        ikiwa fixer.pattern:
            jaribu:
                heads = _get_head_types(fixer.pattern)
            except _EveryNode:
                every.append(fixer)
            isipokua:
                kila node_type kwenye heads:
                    head_nodes[node_type].append(fixer)
        isipokua:
            ikiwa fixer._accept_type ni sio Tupu:
                head_nodes[fixer._accept_type].append(fixer)
            isipokua:
                every.append(fixer)
    kila node_type kwenye chain(pygram.python_grammar.symbol2number.values(),
                           pygram.python_grammar.tokens):
        head_nodes[node_type].extend(every)
    rudisha dict(head_nodes)


eleza get_fixers_from_package(pkg_name):
    """
    Return the fully qualified names kila fixers kwenye the package pkg_name.
    """
    rudisha [pkg_name + "." + fix_name
            kila fix_name kwenye get_all_fix_names(pkg_name, Uongo)]

eleza _identity(obj):
    rudisha obj


eleza _detect_future_features(source):
    have_docstring = Uongo
    gen = tokenize.generate_tokens(io.StringIO(source).readline)
    eleza advance():
        tok = next(gen)
        rudisha tok[0], tok[1]
    ignore = frozenset({token.NEWLINE, tokenize.NL, token.COMMENT})
    features = set()
    jaribu:
        wakati Kweli:
            tp, value = advance()
            ikiwa tp kwenye ignore:
                endelea
            elikiwa tp == token.STRING:
                ikiwa have_docstring:
                    koma
                have_docstring = Kweli
            elikiwa tp == token.NAME na value == "from":
                tp, value = advance()
                ikiwa tp != token.NAME ama value != "__future__":
                    koma
                tp, value = advance()
                ikiwa tp != token.NAME ama value != "import":
                    koma
                tp, value = advance()
                ikiwa tp == token.OP na value == "(":
                    tp, value = advance()
                wakati tp == token.NAME:
                    features.add(value)
                    tp, value = advance()
                    ikiwa tp != token.OP ama value != ",":
                        koma
                    tp, value = advance()
            isipokua:
                koma
    except StopIteration:
        pass
    rudisha frozenset(features)


kundi FixerError(Exception):
    """A fixer could sio be loaded."""


kundi RefactoringTool(object):

    _default_options = {"print_function" : Uongo,
                        "write_unchanged_files" : Uongo}

    CLASS_PREFIX = "Fix" # The prefix kila fixer classes
    FILE_PREFIX = "fix_" # The prefix kila modules ukijumuisha a fixer within

    eleza __init__(self, fixer_names, options=Tupu, explicit=Tupu):
        """Initializer.

        Args:
            fixer_names: a list of fixers to import
            options: a dict ukijumuisha configuration.
            explicit: a list of fixers to run even ikiwa they are explicit.
        """
        self.fixers = fixer_names
        self.explicit = explicit ama []
        self.options = self._default_options.copy()
        ikiwa options ni sio Tupu:
            self.options.update(options)
        ikiwa self.options["print_function"]:
            self.grammar = pygram.python_grammar_no_print_statement
        isipokua:
            self.grammar = pygram.python_grammar
        # When this ni Kweli, the refactor*() methods will call write_file() for
        # files processed even ikiwa they were sio changed during refactoring. If
        # na only ikiwa the refactor method's write parameter was Kweli.
        self.write_unchanged_files = self.options.get("write_unchanged_files")
        self.errors = []
        self.logger = logging.getLogger("RefactoringTool")
        self.fixer_log = []
        self.wrote = Uongo
        self.driver = driver.Driver(self.grammar,
                                    convert=pytree.convert,
                                    logger=self.logger)
        self.pre_order, self.post_order = self.get_fixers()


        self.files = []  # List of files that were ama should be modified

        self.BM = bm.BottomMatcher()
        self.bmi_pre_order = [] # Bottom Matcher incompatible fixers
        self.bmi_post_order = []

        kila fixer kwenye chain(self.post_order, self.pre_order):
            ikiwa fixer.BM_compatible:
                self.BM.add_fixer(fixer)
                # remove fixers that will be handled by the bottom-up
                # matcher
            elikiwa fixer kwenye self.pre_order:
                self.bmi_pre_order.append(fixer)
            elikiwa fixer kwenye self.post_order:
                self.bmi_post_order.append(fixer)

        self.bmi_pre_order_heads = _get_headnode_dict(self.bmi_pre_order)
        self.bmi_post_order_heads = _get_headnode_dict(self.bmi_post_order)



    eleza get_fixers(self):
        """Inspects the options to load the requested patterns na handlers.

        Returns:
          (pre_order, post_order), where pre_order ni the list of fixers that
          want a pre-order AST traversal, na post_order ni the list that want
          post-order traversal.
        """
        pre_order_fixers = []
        post_order_fixers = []
        kila fix_mod_path kwenye self.fixers:
            mod = __import__(fix_mod_path, {}, {}, ["*"])
            fix_name = fix_mod_path.rsplit(".", 1)[-1]
            ikiwa fix_name.startswith(self.FILE_PREFIX):
                fix_name = fix_name[len(self.FILE_PREFIX):]
            parts = fix_name.split("_")
            class_name = self.CLASS_PREFIX + "".join([p.title() kila p kwenye parts])
            jaribu:
                fix_kundi = getattr(mod, class_name)
            except AttributeError:
                 ashiria FixerError("Can't find %s.%s" % (fix_name, class_name)) kutoka Tupu
            fixer = fix_class(self.options, self.fixer_log)
            ikiwa fixer.explicit na self.explicit ni sio Kweli na \
                    fix_mod_path sio kwenye self.explicit:
                self.log_message("Skipping optional fixer: %s", fix_name)
                endelea

            self.log_debug("Adding transformation: %s", fix_name)
            ikiwa fixer.order == "pre":
                pre_order_fixers.append(fixer)
            elikiwa fixer.order == "post":
                post_order_fixers.append(fixer)
            isipokua:
                 ashiria FixerError("Illegal fixer order: %r" % fixer.order)

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
        """Called ukijumuisha the old version, new version, na filename of a
        refactored file."""
        pass

    eleza refactor(self, items, write=Uongo, doctests_only=Uongo):
        """Refactor a list of files na directories."""

        kila dir_or_file kwenye items:
            ikiwa os.path.isdir(dir_or_file):
                self.refactor_dir(dir_or_file, write, doctests_only)
            isipokua:
                self.refactor_file(dir_or_file, write, doctests_only)

    eleza refactor_dir(self, dir_name, write=Uongo, doctests_only=Uongo):
        """Descends down a directory na refactor every Python file found.

        Python files are assumed to have a .py extension.

        Files na subdirectories starting ukijumuisha '.' are skipped.
        """
        py_ext = os.extsep + "py"
        kila dirpath, dirnames, filenames kwenye os.walk(dir_name):
            self.log_debug("Descending into %s", dirpath)
            dirnames.sort()
            filenames.sort()
            kila name kwenye filenames:
                ikiwa (not name.startswith(".") and
                    os.path.splitext(name)[1] == py_ext):
                    fullname = os.path.join(dirpath, name)
                    self.refactor_file(fullname, write, doctests_only)
            # Modify dirnames in-place to remove subdirs ukijumuisha leading dots
            dirnames[:] = [dn kila dn kwenye dirnames ikiwa sio dn.startswith(".")]

    eleza _read_python_source(self, filename):
        """
        Do our best to decode a Python source file correctly.
        """
        jaribu:
            f = open(filename, "rb")
        except OSError as err:
            self.log_error("Can't open %s: %s", filename, err)
            rudisha Tupu, Tupu
        jaribu:
            encoding = tokenize.detect_encoding(f.readline)[0]
        mwishowe:
            f.close()
        ukijumuisha io.open(filename, "r", encoding=encoding, newline='') as f:
            rudisha f.read(), encoding

    eleza refactor_file(self, filename, write=Uongo, doctests_only=Uongo):
        """Refactors a file."""
        input, encoding = self._read_python_source(filename)
        ikiwa input ni Tupu:
            # Reading the file failed.
            return
        input += "\n" # Silence certain parse errors
        ikiwa doctests_only:
            self.log_debug("Refactoring doctests kwenye %s", filename)
            output = self.refactor_docstring(input, filename)
            ikiwa self.write_unchanged_files ama output != input:
                self.processed_file(output, filename, input, write, encoding)
            isipokua:
                self.log_debug("No doctest changes kwenye %s", filename)
        isipokua:
            tree = self.refactor_string(input, filename)
            ikiwa self.write_unchanged_files ama (tree na tree.was_changed):
                # The [:-1] ni to take off the \n we added earlier
                self.processed_file(str(tree)[:-1], filename,
                                    write=write, encoding=encoding)
            isipokua:
                self.log_debug("No changes kwenye %s", filename)

    eleza refactor_string(self, data, name):
        """Refactor a given input string.

        Args:
            data: a string holding the code to be refactored.
            name: a human-readable name kila use kwenye error/log messages.

        Returns:
            An AST corresponding to the refactored input stream; Tupu if
            there were errors during the parse.
        """
        features = _detect_future_features(data)
        ikiwa "print_function" kwenye features:
            self.driver.grammar = pygram.python_grammar_no_print_statement
        jaribu:
            tree = self.driver.parse_string(data)
        except Exception as err:
            self.log_error("Can't parse %s: %s: %s",
                           name, err.__class__.__name__, err)
            return
        mwishowe:
            self.driver.grammar = self.grammar
        tree.future_features = features
        self.log_debug("Refactoring %s", name)
        self.refactor_tree(tree, name)
        rudisha tree

    eleza refactor_stdin(self, doctests_only=Uongo):
        input = sys.stdin.read()
        ikiwa doctests_only:
            self.log_debug("Refactoring doctests kwenye stdin")
            output = self.refactor_docstring(input, "<stdin>")
            ikiwa self.write_unchanged_files ama output != input:
                self.processed_file(output, "<stdin>", input)
            isipokua:
                self.log_debug("No doctest changes kwenye stdin")
        isipokua:
            tree = self.refactor_string(input, "<stdin>")
            ikiwa self.write_unchanged_files ama (tree na tree.was_changed):
                self.processed_file(str(tree), "<stdin>", input)
            isipokua:
                self.log_debug("No changes kwenye stdin")

    eleza refactor_tree(self, tree, name):
        """Refactors a parse tree (modifying the tree kwenye place).

        For compatible patterns the bottom matcher module is
        used. Otherwise the tree ni traversed node-to-node for
        matches.

        Args:
            tree: a pytree.Node instance representing the root of the tree
                  to be refactored.
            name: a human-readable name kila this tree.

        Returns:
            Kweli ikiwa the tree was modified, Uongo otherwise.
        """

        kila fixer kwenye chain(self.pre_order, self.post_order):
            fixer.start_tree(tree, name)

        #use traditional matching kila the incompatible fixers
        self.traverse_by(self.bmi_pre_order_heads, tree.pre_order())
        self.traverse_by(self.bmi_post_order_heads, tree.post_order())

        # obtain a set of candidate nodes
        match_set = self.BM.run(tree.leaves())

        wakati any(match_set.values()):
            kila fixer kwenye self.BM.fixers:
                ikiwa fixer kwenye match_set na match_set[fixer]:
                    #sort by depth; apply fixers kutoka bottom(of the AST) to top
                    match_set[fixer].sort(key=pytree.Base.depth, reverse=Kweli)

                    ikiwa fixer.keep_line_order:
                        #some fixers(eg fix_imports) must be applied
                        #ukijumuisha the original file's line order
                        match_set[fixer].sort(key=pytree.Base.get_lineno)

                    kila node kwenye list(match_set[fixer]):
                        ikiwa node kwenye match_set[fixer]:
                            match_set[fixer].remove(node)

                        jaribu:
                            find_root(node)
                        except ValueError:
                            # this node has been cut off kutoka a
                            # previous transformation ; skip
                            endelea

                        ikiwa node.fixers_applied na fixer kwenye node.fixers_applied:
                            # do sio apply the same fixer again
                            endelea

                        results = fixer.match(node)

                        ikiwa results:
                            new = fixer.transform(node, results)
                            ikiwa new ni sio Tupu:
                                node.replace(new)
                                #new.fixers_applied.append(fixer)
                                kila node kwenye new.post_order():
                                    # do sio apply the fixer again to
                                    # this ama any subnode
                                    ikiwa sio node.fixers_applied:
                                        node.fixers_applied = []
                                    node.fixers_applied.append(fixer)

                                # update the original match set for
                                # the added code
                                new_matches = self.BM.run(new.leaves())
                                kila fxr kwenye new_matches:
                                    ikiwa sio fxr kwenye match_set:
                                        match_set[fxr]=[]

                                    match_set[fxr].extend(new_matches[fxr])

        kila fixer kwenye chain(self.pre_order, self.post_order):
            fixer.finish_tree(tree, name)
        rudisha tree.was_changed

    eleza traverse_by(self, fixers, traversal):
        """Traverse an AST, applying a set of fixers to each node.

        This ni a helper method kila refactor_tree().

        Args:
            fixers: a list of fixer instances.
            traversal: a generator that yields AST nodes.

        Returns:
            Tupu
        """
        ikiwa sio fixers:
            return
        kila node kwenye traversal:
            kila fixer kwenye fixers[node.type]:
                results = fixer.match(node)
                ikiwa results:
                    new = fixer.transform(node, results)
                    ikiwa new ni sio Tupu:
                        node.replace(new)
                        node = new

    eleza processed_file(self, new_text, filename, old_text=Tupu, write=Uongo,
                       encoding=Tupu):
        """
        Called when a file has been refactored na there may be changes.
        """
        self.files.append(filename)
        ikiwa old_text ni Tupu:
            old_text = self._read_python_source(filename)[0]
            ikiwa old_text ni Tupu:
                return
        equal = old_text == new_text
        self.print_output(old_text, new_text, filename, equal)
        ikiwa equal:
            self.log_debug("No changes to %s", filename)
            ikiwa sio self.write_unchanged_files:
                return
        ikiwa write:
            self.write_file(new_text, filename, old_text, encoding)
        isipokua:
            self.log_debug("Not writing changes to %s", filename)

    eleza write_file(self, new_text, filename, old_text, encoding=Tupu):
        """Writes a string to a file.

        It first shows a unified diff between the old text na the new text, and
        then rewrites the file; the latter ni only done ikiwa the write option is
        set.
        """
        jaribu:
            fp = io.open(filename, "w", encoding=encoding, newline='')
        except OSError as err:
            self.log_error("Can't create %s: %s", filename, err)
            return

        ukijumuisha fp:
            jaribu:
                fp.write(new_text)
            except OSError as err:
                self.log_error("Can't write %s: %s", filename, err)
        self.log_debug("Wrote changes to %s", filename)
        self.wrote = Kweli

    PS1 = ">>> "
    PS2 = "... "

    eleza refactor_docstring(self, input, filename):
        """Refactors a docstring, looking kila doctests.

        This returns a modified version of the input string.  It looks
        kila doctests, which start ukijumuisha a ">>>" prompt, na may be
        endelead ukijumuisha "..." prompts, as long as the "..." ni indented
        the same as the ">>>".

        (Unfortunately we can't use the doctest module's parser,
        since, like most parsers, it ni sio geared towards preserving
        the original source.)
        """
        result = []
        block = Tupu
        block_lineno = Tupu
        indent = Tupu
        lineno = 0
        kila line kwenye input.splitlines(keepends=Kweli):
            lineno += 1
            ikiwa line.lstrip().startswith(self.PS1):
                ikiwa block ni sio Tupu:
                    result.extend(self.refactor_doctest(block, block_lineno,
                                                        indent, filename))
                block_lineno = lineno
                block = [line]
                i = line.find(self.PS1)
                indent = line[:i]
            elikiwa (indent ni sio Tupu and
                  (line.startswith(indent + self.PS2) or
                   line == indent + self.PS2.rstrip() + "\n")):
                block.append(line)
            isipokua:
                ikiwa block ni sio Tupu:
                    result.extend(self.refactor_doctest(block, block_lineno,
                                                        indent, filename))
                block = Tupu
                indent = Tupu
                result.append(line)
        ikiwa block ni sio Tupu:
            result.extend(self.refactor_doctest(block, block_lineno,
                                                indent, filename))
        rudisha "".join(result)

    eleza refactor_doctest(self, block, lineno, indent, filename):
        """Refactors one doctest.

        A doctest ni given as a block of lines, the first of which starts
        ukijumuisha ">>>" (possibly indented), wakati the remaining lines start
        ukijumuisha "..." (identically indented).

        """
        jaribu:
            tree = self.parse_block(block, lineno, indent)
        except Exception as err:
            ikiwa self.logger.isEnabledFor(logging.DEBUG):
                kila line kwenye block:
                    self.log_debug("Source: %s", line.rstrip("\n"))
            self.log_error("Can't parse docstring kwenye %s line %s: %s: %s",
                           filename, lineno, err.__class__.__name__, err)
            rudisha block
        ikiwa self.refactor_tree(tree, filename):
            new = str(tree).splitlines(keepends=Kweli)
            # Undo the adjustment of the line numbers kwenye wrap_toks() below.
            clipped, new = new[:lineno-1], new[lineno-1:]
            assert clipped == ["\n"] * (lineno-1), clipped
            ikiwa sio new[-1].endswith("\n"):
                new[-1] += "\n"
            block = [indent + self.PS1 + new.pop(0)]
            ikiwa new:
                block += [indent + self.PS2 + line kila line kwenye new]
        rudisha block

    eleza summarize(self):
        ikiwa self.wrote:
            were = "were"
        isipokua:
            were = "need to be"
        ikiwa sio self.files:
            self.log_message("No files %s modified.", were)
        isipokua:
            self.log_message("Files that %s modified:", were)
            kila file kwenye self.files:
                self.log_message(file)
        ikiwa self.fixer_log:
            self.log_message("Warnings/messages wakati refactoring:")
            kila message kwenye self.fixer_log:
                self.log_message(message)
        ikiwa self.errors:
            ikiwa len(self.errors) == 1:
                self.log_message("There was 1 error:")
            isipokua:
                self.log_message("There were %d errors:", len(self.errors))
            kila msg, args, kwds kwenye self.errors:
                self.log_message(msg, *args, **kwds)

    eleza parse_block(self, block, lineno, indent):
        """Parses a block into a tree.

        This ni necessary to get correct line number / offset information
        kwenye the parser diagnostics na embedded into the parse tree.
        """
        tree = self.driver.parse_tokens(self.wrap_toks(block, lineno, indent))
        tree.future_features = frozenset()
        rudisha tree

    eleza wrap_toks(self, block, lineno, indent):
        """Wraps a tokenize stream to systematically modify start/end."""
        tokens = tokenize.generate_tokens(self.gen_lines(block, indent).__next__)
        kila type, value, (line0, col0), (line1, col1), line_text kwenye tokens:
            line0 += lineno - 1
            line1 += lineno - 1
            # Don't bother updating the columns; this ni too complicated
            # since line_text would also have to be updated na it would
            # still koma kila tokens spanning lines.  Let the user guess
            # that the column numbers kila doctests are relative to the
            # end of the prompt string (PS1 ama PS2).
            tuma type, value, (line0, col0), (line1, col1), line_text


    eleza gen_lines(self, block, indent):
        """Generates lines as expected by tokenize kutoka a list of lines.

        This strips the first len(indent + self.PS1) characters off each line.
        """
        prefix1 = indent + self.PS1
        prefix2 = indent + self.PS2
        prefix = prefix1
        kila line kwenye block:
            ikiwa line.startswith(prefix):
                tuma line[len(prefix):]
            elikiwa line == prefix.rstrip() + "\n":
                tuma "\n"
            isipokua:
                 ashiria AssertionError("line=%r, prefix=%r" % (line, prefix))
            prefix = prefix2
        wakati Kweli:
            tuma ""


kundi MultiprocessingUnsupported(Exception):
    pass


kundi MultiprocessRefactoringTool(RefactoringTool):

    eleza __init__(self, *args, **kwargs):
        super(MultiprocessRefactoringTool, self).__init__(*args, **kwargs)
        self.queue = Tupu
        self.output_lock = Tupu

    eleza refactor(self, items, write=Uongo, doctests_only=Uongo,
                 num_processes=1):
        ikiwa num_processes == 1:
            rudisha super(MultiprocessRefactoringTool, self).refactor(
                items, write, doctests_only)
        jaribu:
            agiza multiprocessing
        except ImportError:
             ashiria MultiprocessingUnsupported
        ikiwa self.queue ni sio Tupu:
             ashiria RuntimeError("already doing multiple processes")
        self.queue = multiprocessing.JoinableQueue()
        self.output_lock = multiprocessing.Lock()
        processes = [multiprocessing.Process(target=self._child)
                     kila i kwenye range(num_processes)]
        jaribu:
            kila p kwenye processes:
                p.start()
            super(MultiprocessRefactoringTool, self).refactor(items, write,
                                                              doctests_only)
        mwishowe:
            self.queue.join()
            kila i kwenye range(num_processes):
                self.queue.put(Tupu)
            kila p kwenye processes:
                ikiwa p.is_alive():
                    p.join()
            self.queue = Tupu

    eleza _child(self):
        task = self.queue.get()
        wakati task ni sio Tupu:
            args, kwargs = task
            jaribu:
                super(MultiprocessRefactoringTool, self).refactor_file(
                    *args, **kwargs)
            mwishowe:
                self.queue.task_done()
            task = self.queue.get()

    eleza refactor_file(self, *args, **kwargs):
        ikiwa self.queue ni sio Tupu:
            self.queue.put((args, kwargs))
        isipokua:
            rudisha super(MultiprocessRefactoringTool, self).refactor_file(
                *args, **kwargs)
