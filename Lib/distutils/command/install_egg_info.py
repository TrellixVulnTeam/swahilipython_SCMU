"""distutils.command.install_egg_info

Implements the Distutils 'install_egg_info' command, kila installing
a package's PKG-INFO metadata."""


kutoka distutils.cmd agiza Command
kutoka distutils agiza log, dir_util
agiza os, sys, re

kundi install_egg_info(Command):
    """Install an .egg-info file kila the package"""

    description = "Install package's PKG-INFO metadata kama an .egg-info file"
    user_options = [
        ('install-dir=', 'd', "directory to install to"),
    ]

    eleza initialize_options(self):
        self.install_dir = Tupu

    eleza finalize_options(self):
        self.set_undefined_options('install_lib',('install_dir','install_dir'))
        basename = "%s-%s-py%d.%d.egg-info" % (
            to_filename(safe_name(self.distribution.get_name())),
            to_filename(safe_version(self.distribution.get_version())),
            *sys.version_info[:2]
        )
        self.target = os.path.join(self.install_dir, basename)
        self.outputs = [self.target]

    eleza run(self):
        target = self.target
        ikiwa os.path.isdir(target) na sio os.path.islink(target):
            dir_util.remove_tree(target, dry_run=self.dry_run)
        lasivyo os.path.exists(target):
            self.execute(os.unlink,(self.target,),"Removing "+target)
        lasivyo sio os.path.isdir(self.install_dir):
            self.execute(os.makedirs, (self.install_dir,),
                         "Creating "+self.install_dir)
        log.info("Writing %s", target)
        ikiwa sio self.dry_run:
            ukijumuisha open(target, 'w', encoding='UTF-8') kama f:
                self.distribution.metadata.write_pkg_file(f)

    eleza get_outputs(self):
        rudisha self.outputs


# The following routines are taken kutoka setuptools' pkg_resources module na
# can be replaced by importing them kutoka pkg_resources once it ni included
# kwenye the stdlib.

eleza safe_name(name):
    """Convert an arbitrary string to a standard distribution name

    Any runs of non-alphanumeric/. characters are replaced ukijumuisha a single '-'.
    """
    rudisha re.sub('[^A-Za-z0-9.]+', '-', name)


eleza safe_version(version):
    """Convert an arbitrary string to a standard version string

    Spaces become dots, na all other non-alphanumeric characters become
    dashes, ukijumuisha runs of multiple dashes condensed to a single dash.
    """
    version = version.replace(' ','.')
    rudisha re.sub('[^A-Za-z0-9.]+', '-', version)


eleza to_filename(name):
    """Convert a project ama version name to its filename-escaped form

    Any '-' characters are currently replaced ukijumuisha '_'.
    """
    rudisha name.replace('-','_')
