agiza os
kutoka test.support agiza load_package_tests

def load_tests(*args):
    return load_package_tests(os.path.dirname(__file__), *args)
