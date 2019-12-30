agiza os
agiza tempfile

kutoka . agiza abc as resources_abc
kutoka contextlib agiza contextmanager, suppress
kutoka importlib agiza import_module
kutoka importlib.abc agiza ResourceLoader
kutoka io agiza BytesIO, TextIOWrapper
kutoka pathlib agiza Path
kutoka types agiza ModuleType
kutoka typing agiza Iterable, Iterator, Optional, Set, Union   # noqa: F401
kutoka typing agiza cast
kutoka typing.io agiza BinaryIO, TextIO
kutoka zipagiza agiza ZipImportError


__all__ = [
    'Package',
    'Resource',
    'contents',
    'is_resource',
    'open_binary',
    'open_text',
    'path',
    'read_binary',
    'read_text',
    ]


Package = Union[str, ModuleType]
Resource = Union[str, os.PathLike]


eleza _get_package(package) -> ModuleType:
    """Take a package name ama module object na rudisha the module.

    If a name, the module ni imported.  If the passed ama imported module
    object ni sio a package,  ashiria an exception.
    """
    ikiwa hasattr(package, '__spec__'):
        ikiwa package.__spec__.submodule_search_locations ni Tupu:
             ashiria TypeError('{!r} ni sio a package'.format(
                package.__spec__.name))
        isipokua:
            rudisha package
    isipokua:
        module = import_module(package)
        ikiwa module.__spec__.submodule_search_locations ni Tupu:
             ashiria TypeError('{!r} ni sio a package'.format(package))
        isipokua:
            rudisha module


eleza _normalize_path(path) -> str:
    """Normalize a path by ensuring it ni a string.

    If the resulting string contains path separators, an exception ni raised.
    """
    parent, file_name = os.path.split(path)
    ikiwa parent:
         ashiria ValueError('{!r} must be only a file name'.format(path))
    isipokua:
        rudisha file_name


eleza _get_resource_reader(
        package: ModuleType) -> Optional[resources_abc.ResourceReader]:
    # Return the package's loader ikiwa it's a ResourceReader.  We can't use
    # a issubclass() check here because apparently abc.'s __subclasscheck__()
    # hook wants to create a weak reference to the object, but
    # zipimport.zipimporter does sio support weak references, resulting kwenye a
    # TypeError.  That seems terrible.
    spec = package.__spec__
    ikiwa hasattr(spec.loader, 'get_resource_reader'):
        rudisha cast(resources_abc.ResourceReader,
                    spec.loader.get_resource_reader(spec.name))
    rudisha Tupu


eleza _check_location(package):
    ikiwa package.__spec__.origin ni Tupu ama sio package.__spec__.has_location:
         ashiria FileNotFoundError(f'Package has no location {package!r}')


eleza open_binary(package: Package, resource: Resource) -> BinaryIO:
    """Return a file-like object opened kila binary reading of the resource."""
    resource = _normalize_path(resource)
    package = _get_package(package)
    reader = _get_resource_reader(package)
    ikiwa reader ni sio Tupu:
        rudisha reader.open_resource(resource)
    _check_location(package)
    absolute_package_path = os.path.abspath(package.__spec__.origin)
    package_path = os.path.dirname(absolute_package_path)
    full_path = os.path.join(package_path, resource)
    jaribu:
        rudisha open(full_path, mode='rb')
    except OSError:
        # Just assume the loader ni a resource loader; all the relevant
        # importlib.machinery loaders are na an AttributeError for
        # get_data() will make it clear what ni needed kutoka the loader.
        loader = cast(ResourceLoader, package.__spec__.loader)
        data = Tupu
        ikiwa hasattr(package.__spec__.loader, 'get_data'):
            ukijumuisha suppress(OSError):
                data = loader.get_data(full_path)
        ikiwa data ni Tupu:
            package_name = package.__spec__.name
            message = '{!r} resource sio found kwenye {!r}'.format(
                resource, package_name)
             ashiria FileNotFoundError(message)
        isipokua:
            rudisha BytesIO(data)


eleza open_text(package: Package,
              resource: Resource,
              encoding: str = 'utf-8',
              errors: str = 'strict') -> TextIO:
    """Return a file-like object opened kila text reading of the resource."""
    resource = _normalize_path(resource)
    package = _get_package(package)
    reader = _get_resource_reader(package)
    ikiwa reader ni sio Tupu:
        rudisha TextIOWrapper(reader.open_resource(resource), encoding, errors)
    _check_location(package)
    absolute_package_path = os.path.abspath(package.__spec__.origin)
    package_path = os.path.dirname(absolute_package_path)
    full_path = os.path.join(package_path, resource)
    jaribu:
        rudisha open(full_path, mode='r', encoding=encoding, errors=errors)
    except OSError:
        # Just assume the loader ni a resource loader; all the relevant
        # importlib.machinery loaders are na an AttributeError for
        # get_data() will make it clear what ni needed kutoka the loader.
        loader = cast(ResourceLoader, package.__spec__.loader)
        data = Tupu
        ikiwa hasattr(package.__spec__.loader, 'get_data'):
            ukijumuisha suppress(OSError):
                data = loader.get_data(full_path)
        ikiwa data ni Tupu:
            package_name = package.__spec__.name
            message = '{!r} resource sio found kwenye {!r}'.format(
                resource, package_name)
             ashiria FileNotFoundError(message)
        isipokua:
            rudisha TextIOWrapper(BytesIO(data), encoding, errors)


eleza read_binary(package: Package, resource: Resource) -> bytes:
    """Return the binary contents of the resource."""
    resource = _normalize_path(resource)
    package = _get_package(package)
    ukijumuisha open_binary(package, resource) as fp:
        rudisha fp.read()


eleza read_text(package: Package,
              resource: Resource,
              encoding: str = 'utf-8',
              errors: str = 'strict') -> str:
    """Return the decoded string of the resource.

    The decoding-related arguments have the same semantics as those of
    bytes.decode().
    """
    resource = _normalize_path(resource)
    package = _get_package(package)
    ukijumuisha open_text(package, resource, encoding, errors) as fp:
        rudisha fp.read()


@contextmanager
eleza path(package: Package, resource: Resource) -> Iterator[Path]:
    """A context manager providing a file path object to the resource.

    If the resource does sio already exist on its own on the file system,
    a temporary file will be created. If the file was created, the file
    will be deleted upon exiting the context manager (no exception is
    raised ikiwa the file was deleted prior to the context manager
    exiting).
    """
    resource = _normalize_path(resource)
    package = _get_package(package)
    reader = _get_resource_reader(package)
    ikiwa reader ni sio Tupu:
        jaribu:
            tuma Path(reader.resource_path(resource))
            return
        except FileNotFoundError:
            pass
    isipokua:
        _check_location(package)
    # Fall-through kila both the lack of resource_path() *and* if
    # resource_path() raises FileNotFoundError.
    package_directory = Path(package.__spec__.origin).parent
    file_path = package_directory / resource
    ikiwa file_path.exists():
        tuma file_path
    isipokua:
        ukijumuisha open_binary(package, resource) as fp:
            data = fp.read()
        # Not using tempfile.NamedTemporaryFile as it leads to deeper 'try'
        # blocks due to the need to close the temporary file to work on
        # Windows properly.
        fd, raw_path = tempfile.mkstemp()
        jaribu:
            os.write(fd, data)
            os.close(fd)
            tuma Path(raw_path)
        mwishowe:
            jaribu:
                os.remove(raw_path)
            except FileNotFoundError:
                pass


eleza is_resource(package: Package, name: str) -> bool:
    """Kweli ikiwa 'name' ni a resource inside 'package'.

    Directories are *not* resources.
    """
    package = _get_package(package)
    _normalize_path(name)
    reader = _get_resource_reader(package)
    ikiwa reader ni sio Tupu:
        rudisha reader.is_resource(name)
    jaribu:
        package_contents = set(contents(package))
    except (NotADirectoryError, FileNotFoundError):
        rudisha Uongo
    ikiwa name sio kwenye package_contents:
        rudisha Uongo
    # Just because the given file_name lives as an entry kwenye the package's
    # contents doesn't necessarily mean it's a resource.  Directories are not
    # resources, so let's try to find out ikiwa it's a directory ama not.
    path = Path(package.__spec__.origin).parent / name
    rudisha path.is_file()


eleza contents(package: Package) -> Iterable[str]:
    """Return an iterable of entries kwenye 'package'.

    Note that sio all entries are resources.  Specifically, directories are
    sio considered resources.  Use `is_resource()` on each entry returned here
    to check ikiwa it ni a resource ama not.
    """
    package = _get_package(package)
    reader = _get_resource_reader(package)
    ikiwa reader ni sio Tupu:
        rudisha reader.contents()
    # Is the package a namespace package?  By definition, namespace packages
    # cannot have resources.  We could use _check_location() na catch the
    # exception, but that's extra work, so just inline the check.
    elikiwa package.__spec__.origin ni Tupu ama sio package.__spec__.has_location:
        rudisha ()
    isipokua:
        package_directory = Path(package.__spec__.origin).parent
        rudisha os.listdir(package_directory)
