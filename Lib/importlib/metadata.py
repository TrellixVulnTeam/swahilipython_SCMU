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
    """The package was sio found."""


kundi EntryPoint(collections.namedtuple('EntryPointBase', 'name value group')):
    """An entry point as defined by Python packaging conventions.

    See `the packaging docs on entry points
    <https://packaging.python.org/specifications/entry-points/>`_
    kila more information.
    """

    pattern = re.compile(
        r'(?P<module>[\w.]+)\s*'
        r'(:\s*(?P<attr>[\w.]+))?\s*'
        r'(?P<extras>\[.*\])?\s*$'
        )
    """
    A regular expression describing the syntax kila an entry point,
    which might look like:

        - module
        - package.module
        - package.module:attribute
        - package.module:object.attribute
        - package.module:attr [extra1, extra2]

    Other combinations are possible as well.

    The expression ni lenient about whitespace around the ':',
    following the attr, na following any extras.
    """

    eleza load(self):
        """Load the entry point kutoka its definition. If only a module
        ni indicated by the value, rudisha that module. Otherwise,
        rudisha the named object.
        """
        match = self.pattern.match(self.value)
        module = import_module(match.group('module'))
        attrs = filter(Tupu, (match.group('attr') ama '').split('.'))
        rudisha functools.reduce(getattr, attrs, module)

    @property
    eleza extras(self):
        match = self.pattern.match(self.value)
        rudisha list(re.finditer(r'\w+', match.group('extras') ama ''))

    @classmethod
    eleza _from_config(cls, config):
        rudisha [
            cls(name, value, group)
            kila group kwenye config.sections()
            kila name, value kwenye config.items(group)
            ]

    @classmethod
    eleza _from_text(cls, text):
        config = ConfigParser(delimiters='=')
        # case sensitive: https://stackoverflow.com/q/1611799/812183
        config.optionxform = str
        jaribu:
            config.read_string(text)
        except AttributeError:  # pragma: nocover
            # Python 2 has no read_string
            config.readfp(io.StringIO(text))
        rudisha EntryPoint._from_config(config)

    eleza __iter__(self):
        """
        Supply iter so one may construct dicts of EntryPoints easily.
        """
        rudisha iter((self.name, self))


kundi PackagePath(pathlib.PurePosixPath):
    """A reference to a path kwenye a package"""

    eleza read_text(self, encoding='utf-8'):
        ukijumuisha self.locate().open(encoding=encoding) as stream:
            rudisha stream.read()

    eleza read_binary(self):
        ukijumuisha self.locate().open('rb') as stream:
            rudisha stream.read()

    eleza locate(self):
        """Return a path-like object kila this path"""
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

        :param filename: The name of the file kwenye the distribution info.
        :return: The text ikiwa found, otherwise Tupu.
        """

    @abc.abstractmethod
    eleza locate_file(self, path):
        """
        Given a path to a file kwenye this distribution, rudisha a path
        to it.
        """

    @classmethod
    eleza from_name(cls, name):
        """Return the Distribution kila the given package name.

        :param name: The name of the distribution package to search for.
        :return: The Distribution instance (or subkundi thereof) kila the named
            package, ikiwa found.
        :raises PackageNotFoundError: When the named package's distribution
            metadata cannot be found.
        """
        kila resolver kwenye cls._discover_resolvers():
            dists = resolver(DistributionFinder.Context(name=name))
            dist = next(dists, Tupu)
            ikiwa dist ni sio Tupu:
                rudisha dist
        isipokua:
             ashiria PackageNotFoundError(name)

    @classmethod
    eleza discover(cls, **kwargs):
        """Return an iterable of Distribution objects kila all packages.

        Pass a ``context`` ama pass keyword arguments kila constructing
        a context.

        :context: A ``DistributionFinder.Context`` object.
        :return: Iterable of Distribution objects kila all packages.
        """
        context = kwargs.pop('context', Tupu)
        ikiwa context na kwargs:
             ashiria ValueError("cannot accept context na kwargs")
        context = context ama DistributionFinder.Context(**kwargs)
        rudisha itertools.chain.from_iterable(
            resolver(context)
            kila resolver kwenye cls._discover_resolvers()
            )

    @staticmethod
    eleza at(path):
        """Return a Distribution kila the indicated metadata path

        :param path: a string ama path-like object
        :return: a concrete Distribution instance kila the path
        """
        rudisha PathDistribution(pathlib.Path(path))

    @staticmethod
    eleza _discover_resolvers():
        """Search the meta_path kila resolvers."""
        declared = (
            getattr(finder, 'find_distributions', Tupu)
            kila finder kwenye sys.meta_path
            )
        rudisha filter(Tupu, declared)

    @property
    eleza metadata(self):
        """Return the parsed metadata kila this Distribution.

        The returned object will have keys that name the various bits of
        metadata.  See PEP 566 kila details.
        """
        text = (
            self.read_text('METADATA')
            ama self.read_text('PKG-INFO')
            # This last clause ni here to support old egg-info files.  Its
            # effect ni to just end up using the PathDistribution's self._path
            # (which points to the egg-info file) attribute unchanged.
            ama self.read_text('')
            )
        rudisha email.message_from_string(text)

    @property
    eleza version(self):
        """Return the 'Version' metadata kila the distribution package."""
        rudisha self.metadata['Version']

    @property
    eleza entry_points(self):
        rudisha EntryPoint._from_text(self.read_text('entry_points.txt'))

    @property
    eleza files(self):
        """Files kwenye this distribution.

        :return: List of PackagePath kila this distribution ama Tupu

        Result ni `Tupu` ikiwa the metadata file that enumerates files
        (i.e. RECORD kila dist-info ama SOURCES.txt kila egg-info) is
        missing.
        Result may be empty ikiwa the metadata exists but ni empty.
        """
        file_lines = self._read_files_distinfo() ama self._read_files_egginfo()

        eleza make_file(name, hash=Tupu, size_str=Tupu):
            result = PackagePath(name)
            result.hash = FileHash(hash) ikiwa hash isipokua Tupu
            result.size = int(size_str) ikiwa size_str isipokua Tupu
            result.dist = self
            rudisha result

        rudisha file_lines na list(starmap(make_file, csv.reader(file_lines)))

    eleza _read_files_distinfo(self):
        """
        Read the lines of RECORD
        """
        text = self.read_text('RECORD')
        rudisha text na text.splitlines()

    eleza _read_files_egginfo(self):
        """
        SOURCES.txt might contain literal commas, so wrap each line
        kwenye quotes.
        """
        text = self.read_text('SOURCES.txt')
        rudisha text na map('"{}"'.format, text.splitlines())

    @property
    eleza requires(self):
        """Generated requirements specified kila this Distribution"""
        reqs = self._read_dist_info_reqs() ama self._read_egg_info_reqs()
        rudisha reqs na list(reqs)

    eleza _read_dist_info_reqs(self):
        rudisha self.metadata.get_all('Requires-Dist')

    eleza _read_egg_info_reqs(self):
        source = self.read_text('requires.txt')
        rudisha source na self._deps_from_requires_text(source)

    @classmethod
    eleza _deps_from_requires_text(cls, source):
        section_pairs = cls._read_sections(source.splitlines())
        sections = {
            section: list(map(operator.itemgetter('line'), results))
            kila section, results in
            itertools.groupby(section_pairs, operator.itemgetter('section'))
            }
        rudisha cls._convert_egg_info_reqs_to_simple_reqs(sections)

    @staticmethod
    eleza _read_sections(lines):
        section = Tupu
        kila line kwenye filter(Tupu, lines):
            section_match = re.match(r'\[(.*)\]$', line)
            ikiwa section_match:
                section = section_match.group(1)
                endelea
            tuma locals()

    @staticmethod
    eleza _convert_egg_info_reqs_to_simple_reqs(sections):
        """
        Historically, setuptools would solicit na store 'extra'
        requirements, including those ukijumuisha environment markers,
        kwenye separate sections. More modern tools expect each
        dependency to be defined separately, ukijumuisha any relevant
        extras na environment markers attached directly to that
        requirement. This method converts the former to the
        latter. See _test_deps_from_requires_text kila an example.
        """
        eleza make_condition(name):
            rudisha name na 'extra == "{name}"'.format(name=name)

        eleza parse_condition(section):
            section = section ama ''
            extra, sep, markers = section.partition(':')
            ikiwa extra na markers:
                markers = '({markers})'.format(markers=markers)
            conditions = list(filter(Tupu, [markers, make_condition(extra)]))
            rudisha '; ' + ' na '.join(conditions) ikiwa conditions isipokua ''

        kila section, deps kwenye sections.items():
            kila dep kwenye deps:
                tuma dep + parse_condition(section)


kundi DistributionFinder(MetaPathFinder):
    """
    A MetaPathFinder capable of discovering installed distributions.
    """

    kundi Context:

        name = Tupu
        """
        Specific name kila which a distribution finder should match.
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
            rudisha '.*' ikiwa self.name ni Tupu isipokua re.escape(self.name)

    @abc.abstractmethod
    eleza find_distributions(self, context=Context()):
        """
        Find distributions.

        Return an iterable of all Distribution instances capable of
        loading the metadata kila packages matching the ``context``,
        a DistributionFinder.Context instance.
        """


kundi MetadataPathFinder(DistributionFinder):
    @classmethod
    eleza find_distributions(cls, context=DistributionFinder.Context()):
        """
        Find distributions.

        Return an iterable of all Distribution instances capable of
        loading the metadata kila packages matching ``context.name``
        (or all names ikiwa ``Tupu`` indicated) along the paths kwenye the list
        of directories ``context.path``.
        """
        found = cls._search_paths(context.pattern, context.path)
        rudisha map(PathDistribution, found)

    @classmethod
    eleza _search_paths(cls, pattern, paths):
        """Find metadata directories kwenye paths heuristically."""
        rudisha itertools.chain.from_iterable(
            cls._search_path(path, pattern)
            kila path kwenye map(cls._switch_path, paths)
            )

    @staticmethod
    eleza _switch_path(path):
        PYPY_OPEN_BUG = Uongo
        ikiwa sio PYPY_OPEN_BUG ama os.path.isfile(path):  # pragma: no branch
            ukijumuisha suppress(Exception):
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
        ikiwa sio root.is_dir():
            rudisha ()
        normalized = pattern.replace('-', '_')
        rudisha (item kila item kwenye root.iterdir()
                ikiwa cls._matches_info(normalized, item)
                ama cls._matches_legacy(normalized, item))


kundi PathDistribution(Distribution):
    eleza __init__(self, path):
        """Construct a distribution kutoka a path to the metadata directory.

        :param path: A pathlib.Path ama similar object supporting
                     .joinpath(), __div__, .parent, na .read_text().
        """
        self._path = path

    eleza read_text(self, filename):
        ukijumuisha suppress(FileNotFoundError, IsADirectoryError, KeyError,
                      NotADirectoryError, PermissionError):
            rudisha self._path.joinpath(filename).read_text(encoding='utf-8')
    read_text.__doc__ = Distribution.read_text.__doc__

    eleza locate_file(self, path):
        rudisha self._path.parent / path


eleza distribution(distribution_name):
    """Get the ``Distribution`` instance kila the named package.

    :param distribution_name: The name of the distribution package as a string.
    :return: A ``Distribution`` instance (or subkundi thereof).
    """
    rudisha Distribution.from_name(distribution_name)


eleza distributions(**kwargs):
    """Get all ``Distribution`` instances kwenye the current environment.

    :return: An iterable of ``Distribution`` instances.
    """
    rudisha Distribution.discover(**kwargs)


eleza metadata(distribution_name):
    """Get the metadata kila the named package.

    :param distribution_name: The name of the distribution package to query.
    :return: An email.Message containing the parsed metadata.
    """
    rudisha Distribution.from_name(distribution_name).metadata


eleza version(distribution_name):
    """Get the version string kila the named package.

    :param distribution_name: The name of the distribution package to query.
    :return: The version string kila the package as defined kwenye the package's
        "Version" metadata key.
    """
    rudisha distribution(distribution_name).version


eleza entry_points():
    """Return EntryPoint objects kila all installed packages.

    :return: EntryPoint objects kila all installed packages.
    """
    eps = itertools.chain.from_iterable(
        dist.entry_points kila dist kwenye distributions())
    by_group = operator.attrgetter('group')
    ordered = sorted(eps, key=by_group)
    grouped = itertools.groupby(ordered, by_group)
    rudisha {
        group: tuple(eps)
        kila group, eps kwenye grouped
        }


eleza files(distribution_name):
    """Return a list of files kila the named package.

    :param distribution_name: The name of the distribution package to query.
    :return: List of files composing the distribution.
    """
    rudisha distribution(distribution_name).files


eleza requires(distribution_name):
    """
    Return a list of requirements kila the named package.

    :return: An iterator of requirements, suitable for
    packaging.requirement.Requirement.
    """
    rudisha distribution(distribution_name).requires
