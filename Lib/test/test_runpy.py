# Test the runpy module
agiza unittest
agiza os
agiza os.path
agiza sys
agiza re
agiza tempfile
agiza importlib, importlib.machinery, importlib.util
agiza py_compile
agiza warnings
kutoka test.support agiza (
    forget, make_legacy_pyc, unload, verbose, no_tracing,
    create_empty_file, temp_dir)
kutoka test.support.script_helper agiza make_script, make_zip_script


agiza runpy
kutoka runpy agiza _run_code, _run_module_code, run_module, run_path
# Note: This module can't safely test _run_module_as_main kama it
# runs its tests kwenye the current process, which would mess ukijumuisha the
# real __main__ module (usually test.regrtest)
# See test_cmd_line_script kila a test that executes that code path


# Set up the test code na expected results
example_source = """\
# Check basic code execution
result = ['Top level assignment']
eleza f():
    result.append('Lower level reference')
f()
toa f
# Check the sys module
agiza sys
run_argv0 = sys.argv[0]
run_name_in_sys_modules = __name__ kwenye sys.modules
module_in_sys_modules = (run_name_in_sys_modules and
                         globals() ni sys.modules[__name__].__dict__)
# Check nested operation
agiza runpy
nested = runpy._run_module_code('x=1\\n', mod_name='<run>')
"""

implicit_namespace = {
    "__name__": Tupu,
    "__file__": Tupu,
    "__cached__": Tupu,
    "__package__": Tupu,
    "__doc__": Tupu,
    "__spec__": Tupu
}
example_namespace =  {
    "sys": sys,
    "runpy": runpy,
    "result": ["Top level assignment", "Lower level reference"],
    "run_argv0": sys.argv[0],
    "run_name_in_sys_modules": Uongo,
    "module_in_sys_modules": Uongo,
    "nested": dict(implicit_namespace,
                   x=1, __name__="<run>", __loader__=Tupu),
}
example_namespace.update(implicit_namespace)

kundi CodeExecutionMixin:
    # Issue #15230 (run_path sio handling run_name correctly) highlighted a
    # problem ukijumuisha the way arguments were being pitaed kutoka higher level APIs
    # down to lower level code. This mixin makes it easier to ensure full
    # testing occurs at those upper layers kama well, sio just at the utility
    # layer

    # Figuring out the loader details kwenye advance ni hard to do, so we skip
    # checking the full details of loader na loader_state
    CHECKED_SPEC_ATTRIBUTES = ["name", "parent", "origin", "cached",
                               "has_location", "submodule_search_locations"]

    eleza assertNamespaceMatches(self, result_ns, expected_ns):
        """Check two namespaces match.

           Ignores any unspecified interpreter created names
        """
        # Avoid side effects
        result_ns = result_ns.copy()
        expected_ns = expected_ns.copy()
        # Impls are permitted to add extra names, so filter them out
        kila k kwenye list(result_ns):
            ikiwa k.startswith("__") na k.endswith("__"):
                ikiwa k haiko kwenye expected_ns:
                    result_ns.pop(k)
                ikiwa k haiko kwenye expected_ns["nested"]:
                    result_ns["nested"].pop(k)
        # Spec equality includes the loader, so we take the spec out of the
        # result namespace na check that separately
        result_spec = result_ns.pop("__spec__")
        expected_spec = expected_ns.pop("__spec__")
        ikiwa expected_spec ni Tupu:
            self.assertIsTupu(result_spec)
        isipokua:
            # If an expected loader ni set, we just check we got the right
            # type, rather than checking kila full equality
            ikiwa expected_spec.loader ni sio Tupu:
                self.assertEqual(type(result_spec.loader),
                                 type(expected_spec.loader))
            kila attr kwenye self.CHECKED_SPEC_ATTRIBUTES:
                k = "__spec__." + attr
                actual = (k, getattr(result_spec, attr))
                expected = (k, getattr(expected_spec, attr))
                self.assertEqual(actual, expected)
        # For the rest, we still don't use direct dict comparison on the
        # namespace, kama the diffs are too hard to debug ikiwa anything komas
        self.assertEqual(set(result_ns), set(expected_ns))
        kila k kwenye result_ns:
            actual = (k, result_ns[k])
            expected = (k, expected_ns[k])
            self.assertEqual(actual, expected)

    eleza check_code_execution(self, create_namespace, expected_namespace):
        """Check that an interface runs the example code correctly

           First argument ni a callable accepting the initial globals and
           using them to create the actual namespace
           Second argument ni the expected result
        """
        sentinel = object()
        expected_ns = expected_namespace.copy()
        run_name = expected_ns["__name__"]
        saved_argv0 = sys.argv[0]
        saved_mod = sys.modules.get(run_name, sentinel)
        # Check without initial globals
        result_ns = create_namespace(Tupu)
        self.assertNamespaceMatches(result_ns, expected_ns)
        self.assertIs(sys.argv[0], saved_argv0)
        self.assertIs(sys.modules.get(run_name, sentinel), saved_mod)
        # And then ukijumuisha initial globals
        initial_ns = {"sentinel": sentinel}
        expected_ns["sentinel"] = sentinel
        result_ns = create_namespace(initial_ns)
        self.assertIsNot(result_ns, initial_ns)
        self.assertNamespaceMatches(result_ns, expected_ns)
        self.assertIs(sys.argv[0], saved_argv0)
        self.assertIs(sys.modules.get(run_name, sentinel), saved_mod)


kundi ExecutionLayerTestCase(unittest.TestCase, CodeExecutionMixin):
    """Unit tests kila runpy._run_code na runpy._run_module_code"""

    eleza test_run_code(self):
        expected_ns = example_namespace.copy()
        expected_ns.update({
            "__loader__": Tupu,
        })
        eleza create_ns(init_globals):
            rudisha _run_code(example_source, {}, init_globals)
        self.check_code_execution(create_ns, expected_ns)

    eleza test_run_module_code(self):
        mod_name = "<Nonsense>"
        mod_fname = "Some other nonsense"
        mod_loader = "Now you're just being silly"
        mod_package = '' # Treat kama a top level module
        mod_spec = importlib.machinery.ModuleSpec(mod_name,
                                                  origin=mod_fname,
                                                  loader=mod_loader)
        expected_ns = example_namespace.copy()
        expected_ns.update({
            "__name__": mod_name,
            "__file__": mod_fname,
            "__loader__": mod_loader,
            "__package__": mod_package,
            "__spec__": mod_spec,
            "run_argv0": mod_fname,
            "run_name_in_sys_modules": Kweli,
            "module_in_sys_modules": Kweli,
        })
        eleza create_ns(init_globals):
            rudisha _run_module_code(example_source,
                                    init_globals,
                                    mod_name,
                                    mod_spec)
        self.check_code_execution(create_ns, expected_ns)

# TODO: Use self.addCleanup to get rid of a lot of try-finally blocks
kundi RunModuleTestCase(unittest.TestCase, CodeExecutionMixin):
    """Unit tests kila runpy.run_module"""

    eleza expect_import_error(self, mod_name):
        jaribu:
            run_module(mod_name)
        tatizo ImportError:
            pita
        isipokua:
            self.fail("Expected agiza error kila " + mod_name)

    eleza test_invalid_names(self):
        # Builtin module
        self.expect_import_error("sys")
        # Non-existent modules
        self.expect_import_error("sys.imp.eric")
        self.expect_import_error("os.path.half")
        self.expect_import_error("a.bee")
        # Relative names sio allowed
        self.expect_import_error(".howard")
        self.expect_import_error("..eaten")
        self.expect_import_error(".test_runpy")
        self.expect_import_error(".unittest")
        # Package without __main__.py
        self.expect_import_error("multiprocessing")

    eleza test_library_module(self):
        self.assertEqual(run_module("runpy")["__name__"], "runpy")

    eleza _add_pkg_dir(self, pkg_dir, namespace=Uongo):
        os.mkdir(pkg_dir)
        ikiwa namespace:
            rudisha Tupu
        pkg_fname = os.path.join(pkg_dir, "__init__.py")
        create_empty_file(pkg_fname)
        rudisha pkg_fname

    eleza _make_pkg(self, source, depth, mod_base="runpy_test",
                     *, namespace=Uongo, parent_namespaces=Uongo):
        # Enforce a couple of internal sanity checks on test cases
        ikiwa (namespace ama parent_namespaces) na sio depth:
            ashiria RuntimeError("Can't mark top level module kama a "
                               "namespace package")
        pkg_name = "__runpy_pkg__"
        test_fname = mod_base+os.extsep+"py"
        pkg_dir = sub_dir = os.path.realpath(tempfile.mkdtemp())
        ikiwa verbose > 1: andika("  Package tree in:", sub_dir)
        sys.path.insert(0, pkg_dir)
        ikiwa verbose > 1: andika("  Updated sys.path:", sys.path[0])
        ikiwa depth:
            namespace_flags = [parent_namespaces] * depth
            namespace_flags[-1] = namespace
            kila namespace_flag kwenye namespace_flags:
                sub_dir = os.path.join(sub_dir, pkg_name)
                pkg_fname = self._add_pkg_dir(sub_dir, namespace_flag)
                ikiwa verbose > 1: andika("  Next level in:", sub_dir)
                ikiwa verbose > 1: andika("  Created:", pkg_fname)
        mod_fname = os.path.join(sub_dir, test_fname)
        ukijumuisha open(mod_fname, "w") kama mod_file:
            mod_file.write(source)
        ikiwa verbose > 1: andika("  Created:", mod_fname)
        mod_name = (pkg_name+".")*depth + mod_base
        mod_spec = importlib.util.spec_kutoka_file_location(mod_name,
                                                          mod_fname)
        rudisha pkg_dir, mod_fname, mod_name, mod_spec

    eleza _del_pkg(self, top):
        kila entry kwenye list(sys.modules):
            ikiwa entry.startswith("__runpy_pkg__"):
                toa sys.modules[entry]
        ikiwa verbose > 1: andika("  Removed sys.modules entries")
        toa sys.path[0]
        ikiwa verbose > 1: andika("  Removed sys.path entry")
        kila root, dirs, files kwenye os.walk(top, topdown=Uongo):
            kila name kwenye files:
                jaribu:
                    os.remove(os.path.join(root, name))
                tatizo OSError kama ex:
                    ikiwa verbose > 1: andika(ex) # Persist ukijumuisha cleaning up
            kila name kwenye dirs:
                fullname = os.path.join(root, name)
                jaribu:
                    os.rmdir(fullname)
                tatizo OSError kama ex:
                    ikiwa verbose > 1: andika(ex) # Persist ukijumuisha cleaning up
        jaribu:
            os.rmdir(top)
            ikiwa verbose > 1: andika("  Removed package tree")
        tatizo OSError kama ex:
            ikiwa verbose > 1: andika(ex) # Persist ukijumuisha cleaning up

    eleza _fix_ns_for_legacy_pyc(self, ns, alter_sys):
        char_to_add = "c"
        ns["__file__"] += char_to_add
        ns["__cached__"] = ns["__file__"]
        spec = ns["__spec__"]
        new_spec = importlib.util.spec_kutoka_file_location(spec.name,
                                                          ns["__file__"])
        ns["__spec__"] = new_spec
        ikiwa alter_sys:
            ns["run_argv0"] += char_to_add


    eleza _check_module(self, depth, alter_sys=Uongo,
                         *, namespace=Uongo, parent_namespaces=Uongo):
        pkg_dir, mod_fname, mod_name, mod_spec = (
               self._make_pkg(example_source, depth,
                              namespace=namespace,
                              parent_namespaces=parent_namespaces))
        forget(mod_name)
        expected_ns = example_namespace.copy()
        expected_ns.update({
            "__name__": mod_name,
            "__file__": mod_fname,
            "__cached__": mod_spec.cached,
            "__package__": mod_name.rpartition(".")[0],
            "__spec__": mod_spec,
        })
        ikiwa alter_sys:
            expected_ns.update({
                "run_argv0": mod_fname,
                "run_name_in_sys_modules": Kweli,
                "module_in_sys_modules": Kweli,
            })
        eleza create_ns(init_globals):
            rudisha run_module(mod_name, init_globals, alter_sys=alter_sys)
        jaribu:
            ikiwa verbose > 1: andika("Running kutoka source:", mod_name)
            self.check_code_execution(create_ns, expected_ns)
            importlib.invalidate_caches()
            __import__(mod_name)
            os.remove(mod_fname)
            ikiwa sio sys.dont_write_bytecode:
                make_legacy_pyc(mod_fname)
                unload(mod_name)  # In case loader caches paths
                importlib.invalidate_caches()
                ikiwa verbose > 1: andika("Running kutoka compiled:", mod_name)
                self._fix_ns_for_legacy_pyc(expected_ns, alter_sys)
                self.check_code_execution(create_ns, expected_ns)
        mwishowe:
            self._del_pkg(pkg_dir)
        ikiwa verbose > 1: andika("Module executed successfully")

    eleza _check_package(self, depth, alter_sys=Uongo,
                          *, namespace=Uongo, parent_namespaces=Uongo):
        pkg_dir, mod_fname, mod_name, mod_spec = (
               self._make_pkg(example_source, depth, "__main__",
                              namespace=namespace,
                              parent_namespaces=parent_namespaces))
        pkg_name = mod_name.rpartition(".")[0]
        forget(mod_name)
        expected_ns = example_namespace.copy()
        expected_ns.update({
            "__name__": mod_name,
            "__file__": mod_fname,
            "__cached__": importlib.util.cache_kutoka_source(mod_fname),
            "__package__": pkg_name,
            "__spec__": mod_spec,
        })
        ikiwa alter_sys:
            expected_ns.update({
                "run_argv0": mod_fname,
                "run_name_in_sys_modules": Kweli,
                "module_in_sys_modules": Kweli,
            })
        eleza create_ns(init_globals):
            rudisha run_module(pkg_name, init_globals, alter_sys=alter_sys)
        jaribu:
            ikiwa verbose > 1: andika("Running kutoka source:", pkg_name)
            self.check_code_execution(create_ns, expected_ns)
            importlib.invalidate_caches()
            __import__(mod_name)
            os.remove(mod_fname)
            ikiwa sio sys.dont_write_bytecode:
                make_legacy_pyc(mod_fname)
                unload(mod_name)  # In case loader caches paths
                ikiwa verbose > 1: andika("Running kutoka compiled:", pkg_name)
                importlib.invalidate_caches()
                self._fix_ns_for_legacy_pyc(expected_ns, alter_sys)
                self.check_code_execution(create_ns, expected_ns)
        mwishowe:
            self._del_pkg(pkg_dir)
        ikiwa verbose > 1: andika("Package executed successfully")

    eleza _add_relative_modules(self, base_dir, source, depth):
        ikiwa depth <= 1:
            ashiria ValueError("Relative module test needs depth > 1")
        pkg_name = "__runpy_pkg__"
        module_dir = base_dir
        kila i kwenye range(depth):
            parent_dir = module_dir
            module_dir = os.path.join(module_dir, pkg_name)
        # Add sibling module
        sibling_fname = os.path.join(module_dir, "sibling.py")
        create_empty_file(sibling_fname)
        ikiwa verbose > 1: andika("  Added sibling module:", sibling_fname)
        # Add nephew module
        uncle_dir = os.path.join(parent_dir, "uncle")
        self._add_pkg_dir(uncle_dir)
        ikiwa verbose > 1: andika("  Added uncle package:", uncle_dir)
        cousin_dir = os.path.join(uncle_dir, "cousin")
        self._add_pkg_dir(cousin_dir)
        ikiwa verbose > 1: andika("  Added cousin package:", cousin_dir)
        nephew_fname = os.path.join(cousin_dir, "nephew.py")
        create_empty_file(nephew_fname)
        ikiwa verbose > 1: andika("  Added nephew module:", nephew_fname)

    eleza _check_relative_agizas(self, depth, run_name=Tupu):
        contents = r"""\
kutoka __future__ agiza absolute_agiza
kutoka . agiza sibling
kutoka ..uncle.cousin agiza nephew
"""
        pkg_dir, mod_fname, mod_name, mod_spec = (
               self._make_pkg(contents, depth))
        ikiwa run_name ni Tupu:
            expected_name = mod_name
        isipokua:
            expected_name = run_name
        jaribu:
            self._add_relative_modules(pkg_dir, contents, depth)
            pkg_name = mod_name.rpartition('.')[0]
            ikiwa verbose > 1: andika("Running kutoka source:", mod_name)
            d1 = run_module(mod_name, run_name=run_name) # Read kutoka source
            self.assertEqual(d1["__name__"], expected_name)
            self.assertEqual(d1["__package__"], pkg_name)
            self.assertIn("sibling", d1)
            self.assertIn("nephew", d1)
            toa d1 # Ensure __loader__ entry doesn't keep file open
            importlib.invalidate_caches()
            __import__(mod_name)
            os.remove(mod_fname)
            ikiwa sio sys.dont_write_bytecode:
                make_legacy_pyc(mod_fname)
                unload(mod_name)  # In case the loader caches paths
                ikiwa verbose > 1: andika("Running kutoka compiled:", mod_name)
                importlib.invalidate_caches()
                d2 = run_module(mod_name, run_name=run_name) # Read kutoka bytecode
                self.assertEqual(d2["__name__"], expected_name)
                self.assertEqual(d2["__package__"], pkg_name)
                self.assertIn("sibling", d2)
                self.assertIn("nephew", d2)
                toa d2 # Ensure __loader__ entry doesn't keep file open
        mwishowe:
            self._del_pkg(pkg_dir)
        ikiwa verbose > 1: andika("Module executed successfully")

    eleza test_run_module(self):
        kila depth kwenye range(4):
            ikiwa verbose > 1: andika("Testing package depth:", depth)
            self._check_module(depth)

    eleza test_run_module_in_namespace_package(self):
        kila depth kwenye range(1, 4):
            ikiwa verbose > 1: andika("Testing package depth:", depth)
            self._check_module(depth, namespace=Kweli, parent_namespaces=Kweli)

    eleza test_run_package(self):
        kila depth kwenye range(1, 4):
            ikiwa verbose > 1: andika("Testing package depth:", depth)
            self._check_package(depth)

    eleza test_run_package_init_exceptions(self):
        # These were previously wrapped kwenye an ImportError; see Issue 14285
        result = self._make_pkg("", 1, "__main__")
        pkg_dir, _, mod_name, _ = result
        mod_name = mod_name.replace(".__main__", "")
        self.addCleanup(self._del_pkg, pkg_dir)
        init = os.path.join(pkg_dir, "__runpy_pkg__", "__init__.py")

        exceptions = (ImportError, AttributeError, TypeError, ValueError)
        kila exception kwenye exceptions:
            name = exception.__name__
            ukijumuisha self.subTest(name):
                source = "ashiria {0}('{0} kwenye __init__.py.')".format(name)
                ukijumuisha open(init, "wt", encoding="ascii") kama mod_file:
                    mod_file.write(source)
                jaribu:
                    run_module(mod_name)
                tatizo exception kama err:
                    self.assertNotIn("finding spec", format(err))
                isipokua:
                    self.fail("Nothing ashiriad; expected {}".format(name))
                jaribu:
                    run_module(mod_name + ".submodule")
                tatizo exception kama err:
                    self.assertNotIn("finding spec", format(err))
                isipokua:
                    self.fail("Nothing ashiriad; expected {}".format(name))

    eleza test_submodule_imported_warning(self):
        pkg_dir, _, mod_name, _ = self._make_pkg("", 1)
        jaribu:
            __import__(mod_name)
            ukijumuisha self.assertWarnsRegex(RuntimeWarning,
                    r"found kwenye sys\.modules"):
                run_module(mod_name)
        mwishowe:
            self._del_pkg(pkg_dir)

    eleza test_package_imported_no_warning(self):
        pkg_dir, _, mod_name, _ = self._make_pkg("", 1, "__main__")
        self.addCleanup(self._del_pkg, pkg_dir)
        package = mod_name.replace(".__main__", "")
        # No warning should occur ikiwa we only imported the parent package
        __import__(package)
        self.assertIn(package, sys.modules)
        ukijumuisha warnings.catch_warnings():
            warnings.simplefilter("error", RuntimeWarning)
            run_module(package)
        # But the warning should occur ikiwa we imported the __main__ submodule
        __import__(mod_name)
        ukijumuisha self.assertWarnsRegex(RuntimeWarning, r"found kwenye sys\.modules"):
            run_module(package)

    eleza test_run_package_in_namespace_package(self):
        kila depth kwenye range(1, 4):
            ikiwa verbose > 1: andika("Testing package depth:", depth)
            self._check_package(depth, parent_namespaces=Kweli)

    eleza test_run_namespace_package(self):
        kila depth kwenye range(1, 4):
            ikiwa verbose > 1: andika("Testing package depth:", depth)
            self._check_package(depth, namespace=Kweli)

    eleza test_run_namespace_package_in_namespace_package(self):
        kila depth kwenye range(1, 4):
            ikiwa verbose > 1: andika("Testing package depth:", depth)
            self._check_package(depth, namespace=Kweli, parent_namespaces=Kweli)

    eleza test_run_module_alter_sys(self):
        kila depth kwenye range(4):
            ikiwa verbose > 1: andika("Testing package depth:", depth)
            self._check_module(depth, alter_sys=Kweli)

    eleza test_run_package_alter_sys(self):
        kila depth kwenye range(1, 4):
            ikiwa verbose > 1: andika("Testing package depth:", depth)
            self._check_package(depth, alter_sys=Kweli)

    eleza test_explicit_relative_agiza(self):
        kila depth kwenye range(2, 5):
            ikiwa verbose > 1: andika("Testing relative agizas at depth:", depth)
            self._check_relative_agizas(depth)

    eleza test_main_relative_agiza(self):
        kila depth kwenye range(2, 5):
            ikiwa verbose > 1: andika("Testing main relative agizas at depth:", depth)
            self._check_relative_agizas(depth, "__main__")

    eleza test_run_name(self):
        depth = 1
        run_name = "And now kila something completely different"
        pkg_dir, mod_fname, mod_name, mod_spec = (
               self._make_pkg(example_source, depth))
        forget(mod_name)
        expected_ns = example_namespace.copy()
        expected_ns.update({
            "__name__": run_name,
            "__file__": mod_fname,
            "__cached__": importlib.util.cache_kutoka_source(mod_fname),
            "__package__": mod_name.rpartition(".")[0],
            "__spec__": mod_spec,
        })
        eleza create_ns(init_globals):
            rudisha run_module(mod_name, init_globals, run_name)
        jaribu:
            self.check_code_execution(create_ns, expected_ns)
        mwishowe:
            self._del_pkg(pkg_dir)

    eleza test_pkgutil_walk_packages(self):
        # This ni a dodgy hack to use the test_runpy infrastructure to test
        # issue #15343. Issue #15348 declares this ni indeed a dodgy hack ;)
        agiza pkgutil
        max_depth = 4
        base_name = "__runpy_pkg__"
        package_suffixes = ["uncle", "uncle.cousin"]
        module_suffixes = ["uncle.cousin.nephew", base_name + ".sibling"]
        expected_packages = set()
        expected_modules = set()
        kila depth kwenye range(1, max_depth):
            pkg_name = ".".join([base_name] * depth)
            expected_packages.add(pkg_name)
            kila name kwenye package_suffixes:
                expected_packages.add(pkg_name + "." + name)
            kila name kwenye module_suffixes:
                expected_modules.add(pkg_name + "." + name)
        pkg_name = ".".join([base_name] * max_depth)
        expected_packages.add(pkg_name)
        expected_modules.add(pkg_name + ".runpy_test")
        pkg_dir, mod_fname, mod_name, mod_spec = (
               self._make_pkg("", max_depth))
        self.addCleanup(self._del_pkg, pkg_dir)
        kila depth kwenye range(2, max_depth+1):
            self._add_relative_modules(pkg_dir, "", depth)
        kila moduleinfo kwenye pkgutil.walk_packages([pkg_dir]):
            self.assertIsInstance(moduleinfo, pkgutil.ModuleInfo)
            self.assertIsInstance(moduleinfo.module_finder,
                                  importlib.machinery.FileFinder)
            ikiwa moduleinfo.ispkg:
                expected_packages.remove(moduleinfo.name)
            isipokua:
                expected_modules.remove(moduleinfo.name)
        self.assertEqual(len(expected_packages), 0, expected_packages)
        self.assertEqual(len(expected_modules), 0, expected_modules)

kundi RunPathTestCase(unittest.TestCase, CodeExecutionMixin):
    """Unit tests kila runpy.run_path"""

    eleza _make_test_script(self, script_dir, script_basename,
                          source=Tupu, omit_suffix=Uongo):
        ikiwa source ni Tupu:
            source = example_source
        rudisha make_script(script_dir, script_basename,
                           source, omit_suffix)

    eleza _check_script(self, script_name, expected_name, expected_file,
                            expected_argv0, mod_name=Tupu,
                            expect_spec=Kweli, check_loader=Kweli):
        # First check ni without run_name
        eleza create_ns(init_globals):
            rudisha run_path(script_name, init_globals)
        expected_ns = example_namespace.copy()
        ikiwa mod_name ni Tupu:
            spec_name = expected_name
        isipokua:
            spec_name = mod_name
        ikiwa expect_spec:
            mod_spec = importlib.util.spec_kutoka_file_location(spec_name,
                                                              expected_file)
            mod_cached = mod_spec.cached
            ikiwa sio check_loader:
                mod_spec.loader = Tupu
        isipokua:
            mod_spec = mod_cached = Tupu

        expected_ns.update({
            "__name__": expected_name,
            "__file__": expected_file,
            "__cached__": mod_cached,
            "__package__": "",
            "__spec__": mod_spec,
            "run_argv0": expected_argv0,
            "run_name_in_sys_modules": Kweli,
            "module_in_sys_modules": Kweli,
        })
        self.check_code_execution(create_ns, expected_ns)
        # Second check makes sure run_name works kwenye all cases
        run_name = "prove.issue15230.is.fixed"
        eleza create_ns(init_globals):
            rudisha run_path(script_name, init_globals, run_name)
        ikiwa expect_spec na mod_name ni Tupu:
            mod_spec = importlib.util.spec_kutoka_file_location(run_name,
                                                              expected_file)
            ikiwa sio check_loader:
                mod_spec.loader = Tupu
            expected_ns["__spec__"] = mod_spec
        expected_ns["__name__"] = run_name
        expected_ns["__package__"] = run_name.rpartition(".")[0]
        self.check_code_execution(create_ns, expected_ns)

    eleza _check_import_error(self, script_name, msg):
        msg = re.escape(msg)
        self.assertRaisesRegex(ImportError, msg, run_path, script_name)

    eleza test_basic_script(self):
        ukijumuisha temp_dir() kama script_dir:
            mod_name = 'script'
            script_name = self._make_test_script(script_dir, mod_name)
            self._check_script(script_name, "<run_path>", script_name,
                               script_name, expect_spec=Uongo)

    eleza test_basic_script_no_suffix(self):
        ukijumuisha temp_dir() kama script_dir:
            mod_name = 'script'
            script_name = self._make_test_script(script_dir, mod_name,
                                                 omit_suffix=Kweli)
            self._check_script(script_name, "<run_path>", script_name,
                               script_name, expect_spec=Uongo)

    eleza test_script_compiled(self):
        ukijumuisha temp_dir() kama script_dir:
            mod_name = 'script'
            script_name = self._make_test_script(script_dir, mod_name)
            compiled_name = py_compile.compile(script_name, doashiria=Kweli)
            os.remove(script_name)
            self._check_script(compiled_name, "<run_path>", compiled_name,
                               compiled_name, expect_spec=Uongo)

    eleza test_directory(self):
        ukijumuisha temp_dir() kama script_dir:
            mod_name = '__main__'
            script_name = self._make_test_script(script_dir, mod_name)
            self._check_script(script_dir, "<run_path>", script_name,
                               script_dir, mod_name=mod_name)

    eleza test_directory_compiled(self):
        ukijumuisha temp_dir() kama script_dir:
            mod_name = '__main__'
            script_name = self._make_test_script(script_dir, mod_name)
            compiled_name = py_compile.compile(script_name, doashiria=Kweli)
            os.remove(script_name)
            ikiwa sio sys.dont_write_bytecode:
                legacy_pyc = make_legacy_pyc(script_name)
                self._check_script(script_dir, "<run_path>", legacy_pyc,
                                   script_dir, mod_name=mod_name)

    eleza test_directory_error(self):
        ukijumuisha temp_dir() kama script_dir:
            mod_name = 'not_main'
            script_name = self._make_test_script(script_dir, mod_name)
            msg = "can't find '__main__' module kwenye %r" % script_dir
            self._check_import_error(script_dir, msg)

    eleza test_zipfile(self):
        ukijumuisha temp_dir() kama script_dir:
            mod_name = '__main__'
            script_name = self._make_test_script(script_dir, mod_name)
            zip_name, fname = make_zip_script(script_dir, 'test_zip', script_name)
            self._check_script(zip_name, "<run_path>", fname, zip_name,
                               mod_name=mod_name, check_loader=Uongo)

    eleza test_zipfile_compiled(self):
        ukijumuisha temp_dir() kama script_dir:
            mod_name = '__main__'
            script_name = self._make_test_script(script_dir, mod_name)
            compiled_name = py_compile.compile(script_name, doashiria=Kweli)
            zip_name, fname = make_zip_script(script_dir, 'test_zip',
                                              compiled_name)
            self._check_script(zip_name, "<run_path>", fname, zip_name,
                               mod_name=mod_name, check_loader=Uongo)

    eleza test_zipfile_error(self):
        ukijumuisha temp_dir() kama script_dir:
            mod_name = 'not_main'
            script_name = self._make_test_script(script_dir, mod_name)
            zip_name, fname = make_zip_script(script_dir, 'test_zip', script_name)
            msg = "can't find '__main__' module kwenye %r" % zip_name
            self._check_import_error(zip_name, msg)

    @no_tracing
    eleza test_main_recursion_error(self):
        ukijumuisha temp_dir() kama script_dir, temp_dir() kama dummy_dir:
            mod_name = '__main__'
            source = ("agiza runpy\n"
                      "runpy.run_path(%r)\n") % dummy_dir
            script_name = self._make_test_script(script_dir, mod_name, source)
            zip_name, fname = make_zip_script(script_dir, 'test_zip', script_name)
            msg = "recursion depth exceeded"
            self.assertRaisesRegex(RecursionError, msg, run_path, zip_name)

    eleza test_encoding(self):
        ukijumuisha temp_dir() kama script_dir:
            filename = os.path.join(script_dir, 'script.py')
            ukijumuisha open(filename, 'w', encoding='latin1') kama f:
                f.write("""
#coding:latin1
s = "non-ASCII: h\xe9"
""")
            result = run_path(filename)
            self.assertEqual(result['s'], "non-ASCII: h\xe9")


ikiwa __name__ == "__main__":
    unittest.main()
