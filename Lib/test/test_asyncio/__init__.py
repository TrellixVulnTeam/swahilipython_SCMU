agiza os
kutoka test.support agiza load_package_tests, import_module

# Skip tests ikiwa we don't have concurrent.futures.
import_module('concurrent.futures')

eleza load_tests(*args):
    rudisha load_package_tests(os.path.dirname(__file__), *args)
