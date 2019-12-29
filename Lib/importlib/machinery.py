"""The machinery of importlib: finders, loaders, hooks, etc."""

agiza _imp

kutoka ._bootstrap agiza ModuleSpec
kutoka ._bootstrap agiza BuiltinImporter
kutoka ._bootstrap agiza FrozenImporter
kutoka ._bootstrap_external agiza (SOURCE_SUFFIXES, DEBUG_BYTECODE_SUFFIXES,
                     OPTIMIZED_BYTECODE_SUFFIXES, BYTECODE_SUFFIXES,
                     EXTENSION_SUFFIXES)
kutoka ._bootstrap_external agiza WindowsRegistryFinder
kutoka ._bootstrap_external agiza PathFinder
kutoka ._bootstrap_external agiza FileFinder
kutoka ._bootstrap_external agiza SourceFileLoader
kutoka ._bootstrap_external agiza SourcelessFileLoader
kutoka ._bootstrap_external agiza ExtensionFileLoader


eleza all_suffixes():
    """Returns a list of all recognized module suffixes kila this process"""
    rudisha SOURCE_SUFFIXES + BYTECODE_SUFFIXES + EXTENSION_SUFFIXES
