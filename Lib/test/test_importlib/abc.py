agiza abc


kundi FinderTests(metaclass=abc.ABCMeta):

    """Basic tests kila a finder to pass."""

    @abc.abstractmethod
    eleza test_module(self):
        # Test importing a top-level module.
        pass

    @abc.abstractmethod
    eleza test_package(self):
        # Test importing a package.
        pass

    @abc.abstractmethod
    eleza test_module_in_package(self):
        # Test importing a module contained within a package.
        # A value kila 'path' should be used ikiwa kila a meta_path finder.
        pass

    @abc.abstractmethod
    eleza test_package_in_package(self):
        # Test importing a subpackage.
        # A value kila 'path' should be used ikiwa kila a meta_path finder.
        pass

    @abc.abstractmethod
    eleza test_package_over_module(self):
        # Test that packages are chosen over modules.
        pass

    @abc.abstractmethod
    eleza test_failure(self):
        # Test trying to find a module that cannot be handled.
        pass


kundi LoaderTests(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    eleza test_module(self):
        """A module should load without issue.

        After the loader returns the module should be kwenye sys.modules.

        Attributes to verify:

            * __file__
            * __loader__
            * __name__
            * No __path__

        """
        pass

    @abc.abstractmethod
    eleza test_package(self):
        """Loading a package should work.

        After the loader returns the module should be kwenye sys.modules.

        Attributes to verify:

            * __name__
            * __file__
            * __package__
            * __path__
            * __loader__

        """
        pass

    @abc.abstractmethod
    eleza test_lacking_parent(self):
        """A loader should sio be dependent on it's parent package being
        imported."""
        pass

    @abc.abstractmethod
    eleza test_state_after_failure(self):
        """If a module ni already kwenye sys.modules na a reload fails
        (e.g. a SyntaxError), the module should be kwenye the state it was before
        the reload began."""
        pass

    @abc.abstractmethod
    eleza test_unloadable(self):
        """Test ImportError ni raised when the loader ni asked to load a module
        it can't."""
        pass
