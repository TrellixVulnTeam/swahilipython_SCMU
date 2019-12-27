agiza io
agiza os
agiza re
agiza abc
agiza csv
agiza sys
agiza email
agiza pathlib
agiza zipfile
agiza operator
agiza functools
agiza itertools
agiza collections

kutoka configparser agiza ConfigParser
kutoka contextlib agiza suppress
kutoka importlib agiza import_module
kutoka importlib.abc agiza MetaPathFinder
kutoka itertools agiza starmap


__all__ = [
    'Distribution',
    'DistributionFinder',
    'PackageNotFoundError',
    'distribution',
    'distributions',
    'entry_points',
    'files',
    'metadata',
    'requires',
    'version',
    ]


kundi PackageNotFoundError(ModuleNotFoundError):
    """The package was not found."""


kundi EntryPoint(collections.namedtuple('EntryPointBase', 'name value group')):
    """An entry point as defined by Python packaging conventions.

    See `the packaging docs on entry points
    <https://packaging.python.org/specifications/entry-points/>`_
    for more information.
    """

    pattern = re.compile(
        r'(?P<module>[\w.]+)\s*'
        r'(:\s*(?P<attr>[\w.]+))?\s*'
        r'(?P<extras>\[.*\])?\s*$'
        )
    """
    A regular expression describing the syntax for an entry point,
    which might look like:

        - module
        - package.module
        - package.module:attribute
        - package.module:object.attribute
        - package.module:attr [extra1, extra2]

    Other combinations are possible as well.

    The expression is lenient about whitespace around the ':',
    following the attr, and following any extras.
    """

    eleza load(self):
        """Load the entry point kutoka its definition. If only a module
        is indicated by the value, rudisha that module. Otherwise,
        rudisha the named object.
        """
        match = self.pattern.match(self.value)
        module = import_module(match.group('module'))
        attrs = filter(None, (match.group('attr') or '').split('.'))
        rudisha functools.reduce(getattr, attrs, module)

    @property
    eleza extras(self):
        match = self.pattern.match(self.value)
        rudisha list(re.finditer(r'\w+', match.group('extras') or ''))

    @classmethod
    eleza _kutoka_config(cls, config):
        rudisha [
            cls(name, value, group)
            for group in config.sections()
            for name, value in config.items(group)
            ]

    @classmethod
    eleza _kutoka_text(cls, text):
        config = ConfigParser(delimiters='=')
        # case sensitive: https://stackoverflow.com/q/1611799/812183
        config.optionxform = str
        try:
            config.read_string(text)
        except AttributeError:  # pragma: nocover
            # Python 2 has no read_string
            config.readfp(io.StringIO(text))
        rudisha EntryPoint._kutoka_config(config)

    eleza __iter__(self):
        """
        Supply iter so one may construct dicts of EntryPoints easily.
        """
        rudisha iter((self.name, self))


kundi PackagePath(pathlib.PurePosixPath):
    """A reference to a path in a package"""

    eleza read_text(self, encoding='utf-8'):
        with self.locate().open(encoding=encoding) as stream:
            rudisha stream.read()

    eleza read_binary(self):
        with self.locate().open('rb') as stream:
            rudisha stream.read()

    eleza locate(self):
        """Return a path-like object for this path"""
        rudisha self.dist.locate_file(self)


kundi FileHash:
    eleza __init__(self, spec):
        self.mode, _, self.value = spec.partition('=')

    eleza __repr__(self):
        rudisha '<FileHash mode: {} value: {}>'.format(self.mode, self.value)


kundi Distribution:
    """A Python distribution package."""

    @abc.abstractmethod
    eleza read_text(self, filename):
        """Attempt to load metadata file given by the name.

        :param filename: The name of the file in the distribution info.
        :return: The text ikiwa found, otherwise None.
        """

    @abc.abstractmethod
    eleza locate_file(self, path):
        """
        Given a path to a file in this distribution, rudisha a path
        to it.
        """

    @classmethod
    eleza kutoka_name(cls, name):
        """Return the Distribution for the given package name.

        :param name: The name of the distribution package to search for.
        :return: The Distribution instance (or subkundi thereof) for the named
            package, ikiwa found.
        :raises PackageNotFoundError: When the named package's distribution
            metadata cannot be found.
        """
        for resolver in cls._discover_resolvers():
            dists = resolver(DistributionFinder.Context(name=name))
            dist = next(dists, None)
            ikiwa dist is not None:
                rudisha dist
        else:
            raise PackageNotFoundError(name)

    @classmethod
    eleza discover(cls, **kwargs):
        """Return an iterable of Distribution objects for all packages.

        Pass a ``context`` or pass keyword arguments for constructing
        a context.

        :context: A ``DistributionFinder.Context`` object.
        :return: Iterable of Distribution objects for all packages.
        """
        context = kwargs.pop('context', None)
        ikiwa context and kwargs:
            raise ValueError("cannot accept context and kwargs")
        context = context or DistributionFinder.Context(**kwargs)
        rudisha itertools.chain.kutoka_iterable(
            resolver(context)
            for resolver in cls._discover_resolvers()
            )

    @staticmethod
    eleza at(path):
        """Return a Distribution for the indicated metadata path

        :param path: a string or path-like object
        :return: a concrete Distribution instance for the path
        """
        rudisha PathDistribution(pathlib.Path(path))

    @staticmethod
    eleza _discover_resolvers():
        """Search the meta_path for resolvers."""
        declared = (
            getattr(finder, 'find_distributions', None)
            for finder in sys.meta_path
            )
        rudisha filter(None, declared)

    @property
    eleza metadata(self):
        """Return the parsed metadata for this Distribution.

        The returned object will have keys that name the various bits of
        metadata.  See PEP 566 for details.
        """
        text = (
            self.read_text('METADATA')
            or self.read_text('PKG-INFO')
            # This last clause is here to support old egg-info files.  Its
            # effect is to just end up using the PathDistribution's self._path
            # (which points to the egg-info file) attribute unchanged.
            or self.read_text('')
            )
        rudisha email.message_kutoka_string(text)

    @property
    eleza version(self):
        """Return the 'Version' metadata for the distribution package."""
        rudisha self.metadata['Version']

    @property
    eleza entry_points(self):
        rudisha EntryPoint._kutoka_text(self.read_text('entry_points.txt'))

    @property
    eleza files(self):
        """Files in this distribution.

        :return: List of PackagePath for this distribution or None

        Result is `None` ikiwa the metadata file that enumerates files
        (i.e. RECORD for dist-info or SOURCES.txt for egg-info) is
        missing.
        Result may be empty ikiwa the metadata exists but is empty.
        """
        file_lines = self._read_files_distinfo() or self._read_files_egginfo()

        eleza make_file(name, hash=None, size_str=None):
            result = PackagePath(name)
            result.hash = FileHash(hash) ikiwa hash else None
            result.size = int(size_str) ikiwa size_str else None
            result.dist = self
            rudisha result

        rudisha file_lines and list(starmap(make_file, csv.reader(file_lines)))

    eleza _read_files_distinfo(self):
        """
        Read the lines of RECORD
        """
        text = self.read_text('RECORD')
        rudisha text and text.splitlines()

    eleza _read_files_egginfo(self):
        """
        SOURCES.txt might contain literal commas, so wrap each line
        in quotes.
        """
        text = self.read_text('SOURCES.txt')
        rudisha text and map('"{}"'.format, text.splitlines())

    @property
    eleza requires(self):
        """Generated requirements specified for this Distribution"""
        reqs = self._read_dist_info_reqs() or self._read_egg_info_reqs()
        rudisha reqs and list(reqs)

    eleza _read_dist_info_reqs(self):
        rudisha self.metadata.get_all('Requires-Dist')

    eleza _read_egg_info_reqs(self):
        source = self.read_text('requires.txt')
        rudisha source and self._deps_kutoka_requires_text(source)

    @classmethod
    eleza _deps_kutoka_requires_text(cls, source):
        section_pairs = cls._read_sections(source.splitlines())
        sections = {
            section: list(map(operator.itemgetter('line'), results))
            for section, results in
            itertools.groupby(section_pairs, operator.itemgetter('section'))
            }
        rudisha cls._convert_egg_info_reqs_to_simple_reqs(sections)

    @staticmethod
    eleza _read_sections(lines):
        section = None
        for line in filter(None, lines):
            section_match = re.match(r'\[(.*)\]$', line)
            ikiwa section_match:
                section = section_match.group(1)
                continue
            yield locals()

    @staticmethod
    eleza _convert_egg_info_reqs_to_simple_reqs(sections):
        """
        Historically, setuptools would solicit and store 'extra'
        requirements, including those with environment markers,
        in separate sections. More modern tools expect each
        dependency to be defined separately, with any relevant
        extras and environment markers attached directly to that
        requirement. This method converts the former to the
        latter. See _test_deps_kutoka_requires_text for an example.
        """
        eleza make_condition(name):
            rudisha name and 'extra == "{name}"'.format(name=name)

        eleza parse_condition(section):
            section = section or ''
            extra, sep, markers = section.partition(':')
            ikiwa extra and markers:
                markers = '({markers})'.format(markers=markers)
            conditions = list(filter(None, [markers, make_condition(extra)]))
            rudisha '; ' + ' and '.join(conditions) ikiwa conditions else ''

        for section, deps in sections.items():
            for dep in deps:
                yield dep + parse_condition(section)


kundi DistributionFinder(MetaPathFinder):
    """
    A MetaPathFinder capable of discovering installed distributions.
    """

    kundi Context:

        name = None
        """
        Specific name for which a distribution finder should match.
        """

        eleza __init__(self, **kwargs):
            vars(self).update(kwargs)

        @property
        eleza path(self):
            """
            The path that a distribution finder should search.
            """
            rudisha vars(self).get('path', sys.path)

        @property
        eleza pattern(self):
            rudisha '.*' ikiwa self.name is None else re.escape(self.name)

    @abc.abstractmethod
    eleza find_distributions(self, context=Context()):
        """
        Find distributions.

        Return an iterable of all Distribution instances capable of
        loading the metadata for packages matching the ``context``,
        a DistributionFinder.Context instance.
        """


kundi MetadataPathFinder(DistributionFinder):
    @classmethod
    eleza find_distributions(cls, context=DistributionFinder.Context()):
        """
        Find distributions.

        Return an iterable of all Distribution instances capable of
        loading the metadata for packages matching ``context.name``
        (or all names ikiwa ``None`` indicated) along the paths in the list
        of directories ``context.path``.
        """
        found = cls._search_paths(context.pattern, context.path)
        rudisha map(PathDistribution, found)

    @classmethod
    eleza _search_paths(cls, pattern, paths):
        """Find metadata directories in paths heuristically."""
        rudisha itertools.chain.kutoka_iterable(
            cls._search_path(path, pattern)
            for path in map(cls._switch_path, paths)
            )

    @staticmethod
    eleza _switch_path(path):
        PYPY_OPEN_BUG = False
        ikiwa not PYPY_OPEN_BUG or os.path.isfile(path):  # pragma: no branch
            with suppress(Exception):
                rudisha zipfile.Path(path)
        rudisha pathlib.Path(path)

    @classmethod
    eleza _matches_info(cls, normalized, item):
        template = r'{pattern}(-.*)?\.(dist|egg)-info'
        manifest = template.format(pattern=normalized)
        rudisha re.match(manifest, item.name, flags=re.IGNORECASE)

    @classmethod
    eleza _matches_legacy(cls, normalized, item):
        template = r'{pattern}-.*\.egg[\\/]EGG-INFO'
        manifest = template.format(pattern=normalized)
        rudisha re.search(manifest, str(item), flags=re.IGNORECASE)

    @classmethod
    eleza _search_path(cls, root, pattern):
        ikiwa not root.is_dir():
            rudisha ()
        normalized = pattern.replace('-', '_')
        rudisha (item for item in root.iterdir()
                ikiwa cls._matches_info(normalized, item)
                or cls._matches_legacy(normalized, item))


kundi PathDistribution(Distribution):
    eleza __init__(self, path):
        """Construct a distribution kutoka a path to the metadata directory.

        :param path: A pathlib.Path or similar object supporting
                     .joinpath(), __div__, .parent, and .read_text().
        """
        self._path = path

    eleza read_text(self, filename):
        with suppress(FileNotFoundError, IsADirectoryError, KeyError,
                      NotADirectoryError, PermissionError):
            rudisha self._path.joinpath(filename).read_text(encoding='utf-8')
    read_text.__doc__ = Distribution.read_text.__doc__

    eleza locate_file(self, path):
        rudisha self._path.parent / path


eleza distribution(distribution_name):
    """Get the ``Distribution`` instance for the named package.

    :param distribution_name: The name of the distribution package as a string.
    :return: A ``Distribution`` instance (or subkundi thereof).
    """
    rudisha Distribution.kutoka_name(distribution_name)


eleza distributions(**kwargs):
    """Get all ``Distribution`` instances in the current environment.

    :return: An iterable of ``Distribution`` instances.
    """
    rudisha Distribution.discover(**kwargs)


eleza metadata(distribution_name):
    """Get the metadata for the named package.

    :param distribution_name: The name of the distribution package to query.
    :return: An email.Message containing the parsed metadata.
    """
    rudisha Distribution.kutoka_name(distribution_name).metadata


eleza version(distribution_name):
    """Get the version string for the named package.

    :param distribution_name: The name of the distribution package to query.
    :return: The version string for the package as defined in the package's
        "Version" metadata key.
    """
    rudisha distribution(distribution_name).version


eleza entry_points():
    """Return EntryPoint objects for all installed packages.

    :return: EntryPoint objects for all installed packages.
    """
    eps = itertools.chain.kutoka_iterable(
        dist.entry_points for dist in distributions())
    by_group = operator.attrgetter('group')
    ordered = sorted(eps, key=by_group)
    grouped = itertools.groupby(ordered, by_group)
    rudisha {
        group: tuple(eps)
        for group, eps in grouped
        }


eleza files(distribution_name):
    """Return a list of files for the named package.

    :param distribution_name: The name of the distribution package to query.
    :return: List of files composing the distribution.
    """
    rudisha distribution(distribution_name).files


eleza requires(distribution_name):
    """
    Return a list of requirements for the named package.

    :return: An iterator of requirements, suitable for
    packaging.requirement.Requirement.
    """
    rudisha distribution(distribution_name).requires
