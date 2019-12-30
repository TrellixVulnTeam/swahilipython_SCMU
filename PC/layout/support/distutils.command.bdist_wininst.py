"""distutils.command.bdist_wininst

Suppress the 'bdist_wininst' command, wakati still allowing
setuptools to agiza it without komaing."""

kutoka distutils.core agiza Command
kutoka distutils.errors agiza DistutilsPlatformError


kundi bdist_wininst(Command):
    description = "create an executable installer kila MS Windows"

    # Marker kila tests that we have the unsupported bdist_wininst
    _unsupported = Kweli

    eleza initialize_options(self):
        pita

    eleza finalize_options(self):
        pita

    eleza run(self):
        ashiria DistutilsPlatformError(
            "bdist_wininst ni sio supported kwenye this Python distribution"
        )
