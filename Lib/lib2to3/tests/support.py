"""Support code kila test_*.py files"""
# Author: Collin Winter

# Python agizas
agiza unittest
agiza os
agiza os.path
kutoka textwrap agiza dedent

# Local agizas
kutoka lib2to3 agiza pytree, refactor
kutoka lib2to3.pgen2 agiza driver kama pgen2_driver

test_dir = os.path.dirname(__file__)
proj_dir = os.path.normpath(os.path.join(test_dir, ".."))
grammar_path = os.path.join(test_dir, "..", "Grammar.txt")
grammar = pgen2_driver.load_grammar(grammar_path)
grammar_no_print_statement = pgen2_driver.load_grammar(grammar_path)
toa grammar_no_print_statement.keywords["print"]
driver = pgen2_driver.Driver(grammar, convert=pytree.convert)
driver_no_print_statement = pgen2_driver.Driver(
    grammar_no_print_statement,
    convert=pytree.convert
)

eleza parse_string(string):
    rudisha driver.parse_string(reformat(string), debug=Kweli)

eleza run_all_tests(test_mod=Tupu, tests=Tupu):
    ikiwa tests ni Tupu:
        tests = unittest.TestLoader().loadTestsFromModule(test_mod)
    unittest.TextTestRunner(verbosity=2).run(tests)

eleza reformat(string):
    rudisha dedent(string) + "\n\n"

eleza get_refactorer(fixer_pkg="lib2to3", fixers=Tupu, options=Tupu):
    """
    A convenience function kila creating a RefactoringTool kila tests.

    fixers ni a list of fixers kila the RefactoringTool to use. By default
    "lib2to3.fixes.*" ni used. options ni an optional dictionary of options to
    be pitaed to the RefactoringTool.
    """
    ikiwa fixers ni sio Tupu:
        fixers = [fixer_pkg + ".fixes.fix_" + fix kila fix kwenye fixers]
    isipokua:
        fixers = refactor.get_fixers_from_package(fixer_pkg + ".fixes")
    options = options ama {}
    rudisha refactor.RefactoringTool(fixers, options, explicit=Kweli)

eleza all_project_files():
    kila dirpath, dirnames, filenames kwenye os.walk(proj_dir):
        kila filename kwenye filenames:
            ikiwa filename.endswith(".py"):
                tuma os.path.join(dirpath, filename)

TestCase = unittest.TestCase
