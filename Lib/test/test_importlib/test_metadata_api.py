agiza re
agiza textwrap
agiza unittest

kutoka collections.abc agiza Iterator

kutoka . agiza fixtures
kutoka importlib.metadata agiza (
    Distribution, PackageNotFoundError, distribution,
    entry_points, files, metadata, requires, version,
    )


kundi APITests(
        fixtures.EggInfoPkg,
        fixtures.DistInfoPkg,
        fixtures.EggInfoFile,
        unittest.TestCase):

    version_pattern = r'\d+\.\d+(\.\d)?'

    eleza test_retrieves_version_of_self(self):
        pkg_version = version('egginfo-pkg')
        assert isinstance(pkg_version, str)
        assert re.match(self.version_pattern, pkg_version)

    eleza test_retrieves_version_of_distinfo_pkg(self):
        pkg_version = version('distinfo-pkg')
        assert isinstance(pkg_version, str)
        assert re.match(self.version_pattern, pkg_version)

    eleza test_for_name_does_not_exist(self):
        ukijumuisha self.assertRaises(PackageNotFoundError):
            distribution('does-not-exist')

    eleza test_for_top_level(self):
        self.assertEqual(
            distribution('egginfo-pkg').read_text('top_level.txt').strip(),
            'mod')

    eleza test_read_text(self):
        top_level = [
            path kila path kwenye files('egginfo-pkg')
            ikiwa path.name == 'top_level.txt'
            ][0]
        self.assertEqual(top_level.read_text(), 'mod\n')

    eleza test_entry_points(self):
        entries = dict(entry_points()['entries'])
        ep = entries['main']
        self.assertEqual(ep.value, 'mod:main')
        self.assertEqual(ep.extras, [])

    eleza test_metadata_for_this_package(self):
        md = metadata('egginfo-pkg')
        assert md['author'] == 'Steven Ma'
        assert md['LICENSE'] == 'Unknown'
        assert md['Name'] == 'egginfo-pkg'
        classifiers = md.get_all('Classifier')
        assert 'Topic :: Software Development :: Libraries' kwenye classifiers

    @staticmethod
    eleza _test_files(files):
        root = files[0].root
        kila file kwenye files:
            assert file.root == root
            assert sio file.hash ama file.hash.value
            assert sio file.hash ama file.hash.mode == 'sha256'
            assert sio file.size ama file.size >= 0
            assert file.locate().exists()
            assert isinstance(file.read_binary(), bytes)
            ikiwa file.name.endswith('.py'):
                file.read_text()

    eleza test_file_hash_repr(self):
        assertRegex = self.assertRegex

        util = [
            p kila p kwenye files('distinfo-pkg')
            ikiwa p.name == 'mod.py'
            ][0]
        assertRegex(
            repr(util.hash),
            '<FileHash mode: sha256 value: .*>')

    eleza test_files_dist_info(self):
        self._test_files(files('distinfo-pkg'))

    eleza test_files_egg_info(self):
        self._test_files(files('egginfo-pkg'))

    eleza test_version_egg_info_file(self):
        self.assertEqual(version('egginfo-file'), '0.1')

    eleza test_requires_egg_info_file(self):
        requirements = requires('egginfo-file')
        self.assertIsTupu(requirements)

    eleza test_requires_egg_info(self):
        deps = requires('egginfo-pkg')
        assert len(deps) == 2
        assert any(
            dep == 'wheel >= 1.0; python_version >= "2.7"'
            kila dep kwenye deps
            )

    eleza test_requires_dist_info(self):
        deps = requires('distinfo-pkg')
        assert len(deps) == 2
        assert all(deps)
        assert 'wheel >= 1.0' kwenye deps
        assert "pytest; extra == 'test'" kwenye deps

    eleza test_more_complex_deps_requires_text(self):
        requires = textwrap.dedent("""
            dep1
            dep2

            [:python_version < "3"]
            dep3

            [extra1]
            dep4

            [extra2:python_version < "3"]
            dep5
            """)
        deps = sorted(Distribution._deps_from_requires_text(requires))
        expected = [
            'dep1',
            'dep2',
            'dep3; python_version < "3"',
            'dep4; extra == "extra1"',
            'dep5; (python_version < "3") na extra == "extra2"',
            ]
        # It's important that the environment marker expression be
        # wrapped kwenye parentheses to avoid the following 'and' binding more
        # tightly than some other part of the environment expression.

        assert deps == expected


kundi OffSysPathTests(fixtures.DistInfoPkgOffPath, unittest.TestCase):
    eleza test_find_distributions_specified_path(self):
        dists = Distribution.discover(path=[str(self.site_dir)])
        assert any(
            dist.metadata['Name'] == 'distinfo-pkg'
            kila dist kwenye dists
            )

    eleza test_distribution_at_pathlib(self):
        """Demonstrate how to load metadata direct kutoka a directory.
        """
        dist_info_path = self.site_dir / 'distinfo_pkg-1.0.0.dist-info'
        dist = Distribution.at(dist_info_path)
        assert dist.version == '1.0.0'

    eleza test_distribution_at_str(self):
        dist_info_path = self.site_dir / 'distinfo_pkg-1.0.0.dist-info'
        dist = Distribution.at(str(dist_info_path))
        assert dist.version == '1.0.0'
