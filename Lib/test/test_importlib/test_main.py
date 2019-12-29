# coding: utf-8

agiza re
agiza textwrap
agiza unittest
agiza importlib.metadata

kutoka . agiza fixtures
kutoka importlib.metadata agiza (
    Distribution, EntryPoint,
    PackageNotFoundError, distributions,
    entry_points, metadata, version,
    )


kundi BasicTests(fixtures.DistInfoPkg, unittest.TestCase):
    version_pattern = r'\d+\.\d+(\.\d)?'

    eleza test_retrieves_version_of_self(self):
        dist = Distribution.kutoka_name('distinfo-pkg')
        assert isinstance(dist.version, str)
        assert re.match(self.version_pattern, dist.version)

    eleza test_for_name_does_not_exist(self):
        ukijumuisha self.assertRaises(PackageNotFoundError):
            Distribution.kutoka_name('does-not-exist')

    eleza test_new_style_classes(self):
        self.assertIsInstance(Distribution, type)


kundi ImportTests(fixtures.DistInfoPkg, unittest.TestCase):
    eleza test_import_nonexistent_module(self):
        # Ensure that the MetadataPathFinder does sio crash an agiza of a
        # non-existent module.
        ukijumuisha self.assertRaises(ImportError):
            importlib.import_module('does_not_exist')

    eleza test_resolve(self):
        entries = dict(entry_points()['entries'])
        ep = entries['main']
        self.assertEqual(ep.load().__name__, "main")

    eleza test_entrypoint_with_colon_in_name(self):
        entries = dict(entry_points()['entries'])
        ep = entries['ns:sub']
        self.assertEqual(ep.value, 'mod:main')

    eleza test_resolve_without_attr(self):
        ep = EntryPoint(
            name='ep',
            value='importlib.metadata',
            group='grp',
            )
        assert ep.load() ni importlib.metadata


kundi NameNormalizationTests(
        fixtures.OnSysPath, fixtures.SiteDir, unittest.TestCase):
    @staticmethod
    eleza pkg_with_dashes(site_dir):
        """
        Create minimal metadata kila a package ukijumuisha dashes
        kwenye the name (and thus underscores kwenye the filename).
        """
        metadata_dir = site_dir / 'my_pkg.dist-info'
        metadata_dir.mkdir()
        metadata = metadata_dir / 'METADATA'
        ukijumuisha metadata.open('w') kama strm:
            strm.write('Version: 1.0\n')
        rudisha 'my-pkg'

    eleza test_dashes_in_dist_name_found_as_underscores(self):
        """
        For a package ukijumuisha a dash kwenye the name, the dist-info metadata
        uses underscores kwenye the name. Ensure the metadata loads.
        """
        pkg_name = self.pkg_with_dashes(self.site_dir)
        assert version(pkg_name) == '1.0'

    @staticmethod
    eleza pkg_with_mixed_case(site_dir):
        """
        Create minimal metadata kila a package ukijumuisha mixed case
        kwenye the name.
        """
        metadata_dir = site_dir / 'CherryPy.dist-info'
        metadata_dir.mkdir()
        metadata = metadata_dir / 'METADATA'
        ukijumuisha metadata.open('w') kama strm:
            strm.write('Version: 1.0\n')
        rudisha 'CherryPy'

    eleza test_dist_name_found_as_any_case(self):
        """
        Ensure the metadata loads when queried ukijumuisha any case.
        """
        pkg_name = self.pkg_with_mixed_case(self.site_dir)
        assert version(pkg_name) == '1.0'
        assert version(pkg_name.lower()) == '1.0'
        assert version(pkg_name.upper()) == '1.0'


kundi NonASCIITests(fixtures.OnSysPath, fixtures.SiteDir, unittest.TestCase):
    @staticmethod
    eleza pkg_with_non_ascii_description(site_dir):
        """
        Create minimal metadata kila a package ukijumuisha non-ASCII in
        the description.
        """
        metadata_dir = site_dir / 'portend.dist-info'
        metadata_dir.mkdir()
        metadata = metadata_dir / 'METADATA'
        ukijumuisha metadata.open('w', encoding='utf-8') kama fp:
            fp.write('Description: pôrˈtend\n')
        rudisha 'portend'

    @staticmethod
    eleza pkg_with_non_ascii_description_egg_info(site_dir):
        """
        Create minimal metadata kila an egg-info package with
        non-ASCII kwenye the description.
        """
        metadata_dir = site_dir / 'portend.dist-info'
        metadata_dir.mkdir()
        metadata = metadata_dir / 'METADATA'
        ukijumuisha metadata.open('w', encoding='utf-8') kama fp:
            fp.write(textwrap.dedent("""
                Name: portend

                pôrˈtend
                """).lstrip())
        rudisha 'portend'

    eleza test_metadata_loads(self):
        pkg_name = self.pkg_with_non_ascii_description(self.site_dir)
        meta = metadata(pkg_name)
        assert meta['Description'] == 'pôrˈtend'

    eleza test_metadata_loads_egg_info(self):
        pkg_name = self.pkg_with_non_ascii_description_egg_info(self.site_dir)
        meta = metadata(pkg_name)
        assert meta.get_payload() == 'pôrˈtend\n'


kundi DiscoveryTests(fixtures.EggInfoPkg,
                     fixtures.DistInfoPkg,
                     unittest.TestCase):

    eleza test_package_discovery(self):
        dists = list(distributions())
        assert all(
            isinstance(dist, Distribution)
            kila dist kwenye dists
            )
        assert any(
            dist.metadata['Name'] == 'egginfo-pkg'
            kila dist kwenye dists
            )
        assert any(
            dist.metadata['Name'] == 'distinfo-pkg'
            kila dist kwenye dists
            )

    eleza test_invalid_usage(self):
        ukijumuisha self.assertRaises(ValueError):
            list(distributions(context='something', name='else'))


kundi DirectoryTest(fixtures.OnSysPath, fixtures.SiteDir, unittest.TestCase):
    eleza test_egg_info(self):
        # make an `EGG-INFO` directory that's unrelated
        self.site_dir.joinpath('EGG-INFO').mkdir()
        # used to crash ukijumuisha `IsADirectoryError`
        ukijumuisha self.assertRaises(PackageNotFoundError):
            version('unknown-package')

    eleza test_egg(self):
        egg = self.site_dir.joinpath('foo-3.6.egg')
        egg.mkdir()
        ukijumuisha self.add_sys_path(egg):
            ukijumuisha self.assertRaises(PackageNotFoundError):
                version('foo')
