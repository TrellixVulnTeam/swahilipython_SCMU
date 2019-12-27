"""Support code for test_*.py files"""
# Author: Collin Winter

# Python agizas
agiza unittest
agiza os
agiza os.path
kutoka textwrap agiza dedent

# Local agizas
kutoka lib2to3 agiza pytree, refactor
kutoka lib2to3.pgen2 agiza driver as pgen2_driver

test_dir = os.path.dirname(__file__)
proj_dir = os.path.normpath(os.path.join(test_dir, ".."))
grammar_path = os.path.join(test_dir, "..", "Grammar.txt")
grammar = pgen2_driver.load_grammar(grammar_path)
grammar_no_print_statement = pgen2_driver.load_grammar(grammar_path)
del grammar_no_print_statement.keywords["print"]
driver = pgen2_driver.Driver(grammar, convert=pytree.convert)
driver_no_print_statement = pgen2_driver.Driver(
    grammar_no_print_statement,
    convert=pytree.convert
)

eleza parse_string(string):
    rudisha driver.parse_string(reformat(string), debug=True)

eleza run_all_tests(test_mod=None, tests=None):
    ikiwa tests is None:
        tests = unittest.TestLoader().loadTestsFromModule(test_mod)
    unittest.TextTestRunner(verbosity=2).run(tests)

eleza reformat(string):
    rudisha dedent(string) + "\n\n"

eleza get_refactorer(fixer_pkg="lib2to3", fixers=None, options=None):
    """
    A convenience function for creating a RefactoringTool for tests.

    fixers is a list of fixers for the RefactoringTool to use. By default
    "lib2to3.fixes.*" is used. options is an optional dictionary of options to
    be passed to the RefactoringTool.
    """
    ikiwa fixers is not None:
        fixers = [fixer_pkg + ".fixes.fix_" + fix for fix in fixers]
    else:
        fixers = refactor.get_fixers_kutoka_package(fixer_pkg + ".fixes")
    options = options or {}
    rudisha refactor.RefactoringTool(fixers, options, explicit=True)

eleza all_project_files():
    for dirpath, dirnames, filenames in os.walk(proj_dir):
        for filename in filenames:
            ikiwa filename.endswith(".py"):
                yield os.path.join(dirpath, filename)

TestCase = unittest.TestCase
