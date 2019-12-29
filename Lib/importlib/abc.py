"""Abstract base classes related to agiza."""
kutoka . agiza _bootstrap
kutoka . agiza _bootstrap_external
kutoka . agiza machinery
jaribu:
    agiza _frozen_importlib
tatizo ImportError kama exc:
    ikiwa exc.name != '_frozen_importlib':
        ashiria
    _frozen_importlib = Tupu
jaribu:
    agiza _frozen_importlib_external
tatizo ImportError kama exc:
    _frozen_importlib_external = _bootstrap_external
agiza abc
agiza warnings


eleza _register(abstract_cls, *classes):
    kila cls kwenye classes:
        abstract_cls.register(cls)
        ikiwa _frozen_importlib ni sio Tupu:
            jaribu:
                frozen_cls = getattr(_frozen_importlib, cls.__name__)
            tatizo AttributeError:
                frozen_cls = getattr(_frozen_importlib_external, cls.__name__)
            abstract_cls.register(frozen_cls)


kundi Finder(metaclass=abc.ABCMeta):

    """Legacy abstract base kundi kila agiza finders.

    It may be subclassed kila compatibility with legacy third party
    reimplementations of the agiza system.  Otherwise, finder
    implementations should derive kutoka the more specific MetaPathFinder
    ama PathEntryFinder ABCs.

    Deprecated since Python 3.3
    """

    @abc.abstractmethod
    eleza find_module(self, fullname, path=Tupu):
        """An abstract method that should find a module.
        The fullname ni a str na the optional path ni a str ama Tupu.
        Returns a Loader object ama Tupu.
        """


kundi MetaPathFinder(Finder):

    """Abstract base kundi kila agiza finders on sys.meta_path."""

    # We don't define find_spec() here since that would koma
    # hasattr checks we do to support backward compatibility.

    eleza find_module(self, fullname, path):
        """Return a loader kila the module.

        If no module ni found, rudisha Tupu.  The fullname ni a str and
        the path ni a list of strings ama Tupu.

        This method ni deprecated since Python 3.4 kwenye favor of
        finder.find_spec(). If find_spec() exists then backwards-compatible
        functionality ni provided kila this method.

        """
        warnings.warn("MetaPathFinder.find_module() ni deprecated since Python "
                      "3.4 kwenye favor of MetaPathFinder.find_spec() "
                      "(available since 3.4)",
                      DeprecationWarning,
                      stacklevel=2)
        ikiwa sio hasattr(self, 'find_spec'):
            rudisha Tupu
        found = self.find_spec(fullname, path)
        rudisha found.loader ikiwa found ni sio Tupu else Tupu

    eleza invalidate_caches(self):
        """An optional method kila clearing the finder's cache, ikiwa any.
        This method ni used by importlib.invalidate_caches().
        """

_register(MetaPathFinder, machinery.BuiltinImporter, machinery.FrozenImporter,
          machinery.PathFinder, machinery.WindowsRegistryFinder)


kundi PathEntryFinder(Finder):

    """Abstract base kundi kila path entry finders used by PathFinder."""

    # We don't define find_spec() here since that would koma
    # hasattr checks we do to support backward compatibility.

    eleza find_loader(self, fullname):
        """Return (loader, namespace portion) kila the path entry.

        The fullname ni a str.  The namespace portion ni a sequence of
        path entries contributing to part of a namespace package. The
        sequence may be empty.  If loader ni sio Tupu, the portion will
        be ignored.

        The portion will be discarded ikiwa another path entry finder
        locates the module kama a normal module ama package.

        This method ni deprecated since Python 3.4 kwenye favor of
        finder.find_spec(). If find_spec() ni provided than backwards-compatible
        functionality ni provided.
        """
        warnings.warn("PathEntryFinder.find_loader() ni deprecated since Python "
                      "3.4 kwenye favor of PathEntryFinder.find_spec() "
                      "(available since 3.4)",
                      DeprecationWarning,
                      stacklevel=2)
        ikiwa sio hasattr(self, 'find_spec'):
            rudisha Tupu, []
        found = self.find_spec(fullname)
        ikiwa found ni sio Tupu:
            ikiwa sio found.submodule_search_locations:
                portions = []
            isipokua:
                portions = found.submodule_search_locations
            rudisha found.loader, portions
        isipokua:
            rudisha Tupu, []

    find_module = _bootstrap_external._find_module_shim

    eleza invalidate_caches(self):
        """An optional method kila clearing the finder's cache, ikiwa any.
        This method ni used by PathFinder.invalidate_caches().
        """

_register(PathEntryFinder, machinery.FileFinder)


kundi Loader(metaclass=abc.ABCMeta):

    """Abstract base kundi kila agiza loaders."""

    eleza create_module(self, spec):
        """Return a module to initialize na into which to load.

        This method should ashiria ImportError ikiwa anything prevents it
        kutoka creating a new module.  It may rudisha Tupu to indicate
        that the spec should create the new module.
        """
        # By default, defer to default semantics kila the new module.
        rudisha Tupu

    # We don't define exec_module() here since that would koma
    # hasattr checks we do to support backward compatibility.

    eleza load_module(self, fullname):
        """Return the loaded module.

        The module must be added to sys.modules na have agiza-related
        attributes set properly.  The fullname ni a str.

        ImportError ni ashiriad on failure.

        This method ni deprecated kwenye favor of loader.exec_module(). If
        exec_module() exists then it ni used to provide a backwards-compatible
        functionality kila this method.

        """
        ikiwa sio hasattr(self, 'exec_module'):
            ashiria ImportError
        rudisha _bootstrap._load_module_shim(self, fullname)

    eleza module_repr(self, module):
        """Return a module's repr.

        Used by the module type when the method does sio ashiria
        NotImplementedError.

        This method ni deprecated.

        """
        # The exception will cause ModuleType.__repr__ to ignore this method.
        ashiria NotImplementedError


kundi ResourceLoader(Loader):

    """Abstract base kundi kila loaders which can rudisha data kutoka their
    back-end storage.

    This ABC represents one of the optional protocols specified by PEP 302.

    """

    @abc.abstractmethod
    eleza get_data(self, path):
        """Abstract method which when implemented should rudisha the bytes for
        the specified path.  The path must be a str."""
        ashiria OSError


kundi InspectLoader(Loader):

    """Abstract base kundi kila loaders which support inspection about the
    modules they can load.

    This ABC represents one of the optional protocols specified by PEP 302.

    """

    eleza is_package(self, fullname):
        """Optional method which when implemented should rudisha whether the
        module ni a package.  The fullname ni a str.  Returns a bool.

        Raises ImportError ikiwa the module cannot be found.
        """
        ashiria ImportError

    eleza get_code(self, fullname):
        """Method which rudishas the code object kila the module.

        The fullname ni a str.  Returns a types.CodeType ikiwa possible, else
        rudishas Tupu ikiwa a code object does sio make sense
        (e.g. built-in module). Raises ImportError ikiwa the module cannot be
        found.
        """
        source = self.get_source(fullname)
        ikiwa source ni Tupu:
            rudisha Tupu
        rudisha self.source_to_code(source)

    @abc.abstractmethod
    eleza get_source(self, fullname):
        """Abstract method which should rudisha the source code kila the
        module.  The fullname ni a str.  Returns a str.

        Raises ImportError ikiwa the module cannot be found.
        """
        ashiria ImportError

    @staticmethod
    eleza source_to_code(data, path='<string>'):
        """Compile 'data' into a code object.

        The 'data' argument can be anything that compile() can handle. The'path'
        argument should be where the data was retrieved (when applicable)."""
        rudisha compile(data, path, 'exec', dont_inherit=Kweli)

    exec_module = _bootstrap_external._LoaderBasics.exec_module
    load_module = _bootstrap_external._LoaderBasics.load_module

_register(InspectLoader, machinery.BuiltinImporter, machinery.FrozenImporter)


kundi ExecutionLoader(InspectLoader):

    """Abstract base kundi kila loaders that wish to support the execution of
    modules kama scripts.

    This ABC represents one of the optional protocols specified kwenye PEP 302.

    """

    @abc.abstractmethod
    eleza get_filename(self, fullname):
        """Abstract method which should rudisha the value that __file__ ni to be
        set to.

        Raises ImportError ikiwa the module cannot be found.
        """
        ashiria ImportError

    eleza get_code(self, fullname):
        """Method to rudisha the code object kila fullname.

        Should rudisha Tupu ikiwa sio applicable (e.g. built-in module).
        Raise ImportError ikiwa the module cannot be found.
        """
        source = self.get_source(fullname)
        ikiwa source ni Tupu:
            rudisha Tupu
        jaribu:
            path = self.get_filename(fullname)
        tatizo ImportError:
            rudisha self.source_to_code(source)
        isipokua:
            rudisha self.source_to_code(source, path)

_register(ExecutionLoader, machinery.ExtensionFileLoader)


kundi FileLoader(_bootstrap_external.FileLoader, ResourceLoader, ExecutionLoader):

    """Abstract base kundi partially implementing the ResourceLoader and
    ExecutionLoader ABCs."""

_register(FileLoader, machinery.SourceFileLoader,
            machinery.SourcelessFileLoader)


kundi SourceLoader(_bootstrap_external.SourceLoader, ResourceLoader, ExecutionLoader):

    """Abstract base kundi kila loading source code (and optionally any
    corresponding bytecode).

    To support loading kutoka source code, the abstractmethods inherited kutoka
    ResourceLoader na ExecutionLoader need to be implemented. To also support
    loading kutoka bytecode, the optional methods specified directly by this ABC
    ni required.

    Inherited abstractmethods sio implemented kwenye this ABC:

        * ResourceLoader.get_data
        * ExecutionLoader.get_filename

    """

    eleza path_mtime(self, path):
        """Return the (int) modification time kila the path (str)."""
        ikiwa self.path_stats.__func__ ni SourceLoader.path_stats:
            ashiria OSError
        rudisha int(self.path_stats(path)['mtime'])

    eleza path_stats(self, path):
        """Return a metadata dict kila the source pointed to by the path (str).
        Possible keys:
        - 'mtime' (mandatory) ni the numeric timestamp of last source
          code modification;
        - 'size' (optional) ni the size kwenye bytes of the source code.
        """
        ikiwa self.path_mtime.__func__ ni SourceLoader.path_mtime:
            ashiria OSError
        rudisha {'mtime': self.path_mtime(path)}

    eleza set_data(self, path, data):
        """Write the bytes to the path (ikiwa possible).

        Accepts a str path na data kama bytes.

        Any needed intermediary directories are to be created. If kila some
        reason the file cannot be written because of permissions, fail
        silently.
        """

_register(SourceLoader, machinery.SourceFileLoader)


kundi ResourceReader(metaclass=abc.ABCMeta):

    """Abstract base kundi to provide resource-reading support.

    Loaders that support resource reading are expected to implement
    the ``get_resource_reader(fullname)`` method na have it either rudisha Tupu
    ama an object compatible with this ABC.
    """

    @abc.abstractmethod
    eleza open_resource(self, resource):
        """Return an opened, file-like object kila binary reading.

        The 'resource' argument ni expected to represent only a file name
        na thus sio contain any subdirectory components.

        If the resource cannot be found, FileNotFoundError ni ashiriad.
        """
        ashiria FileNotFoundError

    @abc.abstractmethod
    eleza resource_path(self, resource):
        """Return the file system path to the specified resource.

        The 'resource' argument ni expected to represent only a file name
        na thus sio contain any subdirectory components.

        If the resource does sio exist on the file system, ashiria
        FileNotFoundError.
        """
        ashiria FileNotFoundError

    @abc.abstractmethod
    eleza is_resource(self, name):
        """Return Kweli ikiwa the named 'name' ni consider a resource."""
        ashiria FileNotFoundError

    @abc.abstractmethod
    eleza contents(self):
        """Return an iterable of strings over the contents of the package."""
        rudisha []


_register(ResourceReader, machinery.SourceFileLoader)
