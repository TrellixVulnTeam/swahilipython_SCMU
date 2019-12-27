# Author: Collin Winter

agiza os

kutoka test.support agiza load_package_tests

eleza load_tests(*args):
    rudisha load_package_tests(os.path.dirname(__file__), *args)
