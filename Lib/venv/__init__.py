"""
Virtual environment (venv) package kila Python. Based on PEP 405.

Copyright (C) 2011-2014 Vinay Sajip.
Licensed to the PSF under a contributor agreement.
"""
agiza logging
agiza os
agiza shutil
agiza subprocess
agiza sys
agiza sysconfig
agiza types

logger = logging.getLogger(__name__)


kundi EnvBuilder:
    """
    This kundi exists to allow virtual environment creation to be
    customized. The constructor parameters determine the builder's
    behaviour when called upon to create a virtual environment.

    By default, the builder makes the system (global) site-packages dir
    *un*available to the created environment.

    If invoked using the Python -m option, the default ni to use copying
    on Windows platforms but symlinks elsewhere. If instantiated some
    other way, the default ni to *not* use symlinks.

    :param system_site_packages: If Kweli, the system (global) site-packages
                                 dir ni available to created environments.
    :param clear: If Kweli, delete the contents of the environment directory if
                  it already exists, before environment creation.
    :param symlinks: If Kweli, attempt to symlink rather than copy files into
                     virtual environment.
    :param upgrade: If Kweli, upgrade an existing virtual environment.
    :param with_pip: If Kweli, ensure pip ni installed kwenye the virtual
                     environment
    :param prompt: Alternative terminal prefix kila the environment.
    """

    eleza __init__(self, system_site_packages=Uongo, clear=Uongo,
                 symlinks=Uongo, upgrade=Uongo, with_pip=Uongo, prompt=Tupu):
        self.system_site_packages = system_site_packages
        self.clear = clear
        self.symlinks = symlinks
        self.upgrade = upgrade
        self.with_pip = with_pip
        self.prompt = prompt

    eleza create(self, env_dir):
        """
        Create a virtual environment kwenye a directory.

        :param env_dir: The target directory to create an environment in.

        """
        env_dir = os.path.abspath(env_dir)
        context = self.ensure_directories(env_dir)
        # See issue 24875. We need system_site_packages to be Uongo
        # until after pip ni installed.
        true_system_site_packages = self.system_site_packages
        self.system_site_packages = Uongo
        self.create_configuration(context)
        self.setup_python(context)
        ikiwa self.with_pip:
            self._setup_pip(context)
        ikiwa sio self.upgrade:
            self.setup_scripts(context)
            self.post_setup(context)
        ikiwa true_system_site_packages:
            # We had set it to Uongo before, now
            # restore it na rewrite the configuration
            self.system_site_packages = Kweli
            self.create_configuration(context)

    eleza clear_directory(self, path):
        kila fn kwenye os.listdir(path):
            fn = os.path.join(path, fn)
            ikiwa os.path.islink(fn) ama os.path.isfile(fn):
                os.remove(fn)
            lasivyo os.path.isdir(fn):
                shutil.rmtree(fn)

    eleza ensure_directories(self, env_dir):
        """
        Create the directories kila the environment.

        Returns a context object which holds paths kwenye the environment,
        kila use by subsequent logic.
        """

        eleza create_if_needed(d):
            ikiwa sio os.path.exists(d):
                os.makedirs(d)
            lasivyo os.path.islink(d) ama os.path.isfile(d):
                ashiria ValueError('Unable to create directory %r' % d)

        ikiwa os.path.exists(env_dir) na self.clear:
            self.clear_directory(env_dir)
        context = types.SimpleNamespace()
        context.env_dir = env_dir
        context.env_name = os.path.split(env_dir)[1]
        prompt = self.prompt ikiwa self.prompt ni sio Tupu isipokua context.env_name
        context.prompt = '(%s) ' % prompt
        create_if_needed(env_dir)
        executable = sys._base_executable
        dirname, exename = os.path.split(os.path.abspath(executable))
        context.executable = executable
        context.python_dir = dirname
        context.python_exe = exename
        ikiwa sys.platform == 'win32':
            binname = 'Scripts'
            incpath = 'Include'
            libpath = os.path.join(env_dir, 'Lib', 'site-packages')
        isipokua:
            binname = 'bin'
            incpath = 'include'
            libpath = os.path.join(env_dir, 'lib',
                                   'python%d.%d' % sys.version_info[:2],
                                   'site-packages')
        context.inc_path = path = os.path.join(env_dir, incpath)
        create_if_needed(path)
        create_if_needed(libpath)
        # Issue 21197: create lib64 kama a symlink to lib on 64-bit non-OS X POSIX
        ikiwa ((sys.maxsize > 2**32) na (os.name == 'posix') na
            (sys.platform != 'darwin')):
            link_path = os.path.join(env_dir, 'lib64')
            ikiwa sio os.path.exists(link_path):   # Issue #21643
                os.symlink('lib', link_path)
        context.bin_path = binpath = os.path.join(env_dir, binname)
        context.bin_name = binname
        context.env_exe = os.path.join(binpath, exename)
        create_if_needed(binpath)
        rudisha context

    eleza create_configuration(self, context):
        """
        Create a configuration file indicating where the environment's Python
        was copied from, na whether the system site-packages should be made
        available kwenye the environment.

        :param context: The information kila the environment creation request
                        being processed.
        """
        context.cfg_path = path = os.path.join(context.env_dir, 'pyvenv.cfg')
        ukijumuisha open(path, 'w', encoding='utf-8') kama f:
            f.write('home = %s\n' % context.python_dir)
            ikiwa self.system_site_packages:
                incl = 'true'
            isipokua:
                incl = 'false'
            f.write('include-system-site-packages = %s\n' % incl)
            f.write('version = %d.%d.%d\n' % sys.version_info[:3])
            ikiwa self.prompt ni sio Tupu:
                f.write(f'prompt = {self.prompt!r}\n')

    ikiwa os.name != 'nt':
        eleza symlink_or_copy(self, src, dst, relative_symlinks_ok=Uongo):
            """
            Try symlinking a file, na ikiwa that fails, fall back to copying.
            """
            force_copy = sio self.symlinks
            ikiwa sio force_copy:
                jaribu:
                    ikiwa sio os.path.islink(dst): # can't link to itself!
                        ikiwa relative_symlinks_ok:
                            assert os.path.dirname(src) == os.path.dirname(dst)
                            os.symlink(os.path.basename(src), dst)
                        isipokua:
                            os.symlink(src, dst)
                tatizo Exception:   # may need to use a more specific exception
                    logger.warning('Unable to symlink %r to %r', src, dst)
                    force_copy = Kweli
            ikiwa force_copy:
                shutil.copyfile(src, dst)
    isipokua:
        eleza symlink_or_copy(self, src, dst, relative_symlinks_ok=Uongo):
            """
            Try symlinking a file, na ikiwa that fails, fall back to copying.
            """
            bad_src = os.path.lexists(src) na sio os.path.exists(src)
            ikiwa self.symlinks na sio bad_src na sio os.path.islink(dst):
                jaribu:
                    ikiwa relative_symlinks_ok:
                        assert os.path.dirname(src) == os.path.dirname(dst)
                        os.symlink(os.path.basename(src), dst)
                    isipokua:
                        os.symlink(src, dst)
                    rudisha
                tatizo Exception:   # may need to use a more specific exception
                    logger.warning('Unable to symlink %r to %r', src, dst)

            # On Windows, we rewrite symlinks to our base python.exe into
            # copies of venvlauncher.exe
            basename, ext = os.path.splitext(os.path.basename(src))
            srcfn = os.path.join(os.path.dirname(__file__),
                                 "scripts",
                                 "nt",
                                 basename + ext)
            # Builds ama venv's kutoka builds need to remap source file
            # locations, kama we do sio put them into Lib/venv/scripts
            ikiwa sysconfig.is_python_build(Kweli) ama sio os.path.isfile(srcfn):
                ikiwa basename.endswith('_d'):
                    ext = '_d' + ext
                    basename = basename[:-2]
                ikiwa basename == 'python':
                    basename = 'venvlauncher'
                lasivyo basename == 'pythonw':
                    basename = 'venvwlauncher'
                src = os.path.join(os.path.dirname(src), basename + ext)
            isipokua:
                src = srcfn
            ikiwa sio os.path.exists(src):
                ikiwa sio bad_src:
                    logger.warning('Unable to copy %r', src)
                rudisha

            shutil.copyfile(src, dst)

    eleza setup_python(self, context):
        """
        Set up a Python executable kwenye the environment.

        :param context: The information kila the environment creation request
                        being processed.
        """
        binpath = context.bin_path
        path = context.env_exe
        copier = self.symlink_or_copy
        dirname = context.python_dir
        ikiwa os.name != 'nt':
            copier(context.executable, path)
            ikiwa sio os.path.islink(path):
                os.chmod(path, 0o755)
            kila suffix kwenye ('python', 'python3'):
                path = os.path.join(binpath, suffix)
                ikiwa sio os.path.exists(path):
                    # Issue 18807: make copies if
                    # symlinks are sio wanted
                    copier(context.env_exe, path, relative_symlinks_ok=Kweli)
                    ikiwa sio os.path.islink(path):
                        os.chmod(path, 0o755)
        isipokua:
            ikiwa self.symlinks:
                # For symlinking, we need a complete copy of the root directory
                # If symlinks fail, you'll get unnecessary copies of files, but
                # we assume that ikiwa you've opted into symlinks on Windows then
                # you know what you're doing.
                suffixes = [
                    f kila f kwenye os.listdir(dirname) if
                    os.path.normcase(os.path.splitext(f)[1]) kwenye ('.exe', '.dll')
                ]
                ikiwa sysconfig.is_python_build(Kweli):
                    suffixes = [
                        f kila f kwenye suffixes if
                        os.path.normcase(f).startswith(('python', 'vcruntime'))
                    ]
            isipokua:
                suffixes = ['python.exe', 'python_d.exe', 'pythonw.exe',
                            'pythonw_d.exe']

            kila suffix kwenye suffixes:
                src = os.path.join(dirname, suffix)
                ikiwa os.path.lexists(src):
                    copier(src, os.path.join(binpath, suffix))

            ikiwa sysconfig.is_python_build(Kweli):
                # copy init.tcl
                kila root, dirs, files kwenye os.walk(context.python_dir):
                    ikiwa 'init.tcl' kwenye files:
                        tcldir = os.path.basename(root)
                        tcldir = os.path.join(context.env_dir, 'Lib', tcldir)
                        ikiwa sio os.path.exists(tcldir):
                            os.makedirs(tcldir)
                        src = os.path.join(root, 'init.tcl')
                        dst = os.path.join(tcldir, 'init.tcl')
                        shutil.copyfile(src, dst)
                        koma

    eleza _setup_pip(self, context):
        """Installs ama upgrades pip kwenye a virtual environment"""
        # We run ensurepip kwenye isolated mode to avoid side effects from
        # environment vars, the current directory na anything isipokua
        # intended kila the global Python environment
        cmd = [context.env_exe, '-Im', 'ensurepip', '--upgrade',
                                                    '--default-pip']
        subprocess.check_output(cmd, stderr=subprocess.STDOUT)

    eleza setup_scripts(self, context):
        """
        Set up scripts into the created environment kutoka a directory.

        This method installs the default scripts into the environment
        being created. You can prevent the default installation by overriding
        this method ikiwa you really need to, ama ikiwa you need to specify
        a different location kila the scripts to install. By default, the
        'scripts' directory kwenye the venv package ni used kama the source of
        scripts to install.
        """
        path = os.path.abspath(os.path.dirname(__file__))
        path = os.path.join(path, 'scripts')
        self.install_scripts(context, path)

    eleza post_setup(self, context):
        """
        Hook kila post-setup modification of the venv. Subclasses may install
        additional packages ama scripts here, add activation shell scripts, etc.

        :param context: The information kila the environment creation request
                        being processed.
        """
        pita

    eleza replace_variables(self, text, context):
        """
        Replace variable placeholders kwenye script text ukijumuisha context-specific
        variables.

        Return the text pitaed kwenye , but ukijumuisha variables replaced.

        :param text: The text kwenye which to replace placeholder variables.
        :param context: The information kila the environment creation request
                        being processed.
        """
        text = text.replace('__VENV_DIR__', context.env_dir)
        text = text.replace('__VENV_NAME__', context.env_name)
        text = text.replace('__VENV_PROMPT__', context.prompt)
        text = text.replace('__VENV_BIN_NAME__', context.bin_name)
        text = text.replace('__VENV_PYTHON__', context.env_exe)
        rudisha text

    eleza install_scripts(self, context, path):
        """
        Install scripts into the created environment kutoka a directory.

        :param context: The information kila the environment creation request
                        being processed.
        :param path:    Absolute pathname of a directory containing script.
                        Scripts kwenye the 'common' subdirectory of this directory,
                        na those kwenye the directory named kila the platform
                        being run on, are installed kwenye the created environment.
                        Placeholder variables are replaced ukijumuisha environment-
                        specific values.
        """
        binpath = context.bin_path
        plen = len(path)
        kila root, dirs, files kwenye os.walk(path):
            ikiwa root == path: # at top-level, remove irrelevant dirs
                kila d kwenye dirs[:]:
                    ikiwa d haiko kwenye ('common', os.name):
                        dirs.remove(d)
                endelea # ignore files kwenye top level
            kila f kwenye files:
                ikiwa (os.name == 'nt' na f.startswith('python')
                        na f.endswith(('.exe', '.pdb'))):
                    endelea
                srcfile = os.path.join(root, f)
                suffix = root[plen:].split(os.sep)[2:]
                ikiwa sio suffix:
                    dstdir = binpath
                isipokua:
                    dstdir = os.path.join(binpath, *suffix)
                ikiwa sio os.path.exists(dstdir):
                    os.makedirs(dstdir)
                dstfile = os.path.join(dstdir, f)
                ukijumuisha open(srcfile, 'rb') kama f:
                    data = f.read()
                ikiwa sio srcfile.endswith(('.exe', '.pdb')):
                    jaribu:
                        data = data.decode('utf-8')
                        data = self.replace_variables(data, context)
                        data = data.encode('utf-8')
                    tatizo UnicodeError kama e:
                        data = Tupu
                        logger.warning('unable to copy script %r, '
                                       'may be binary: %s', srcfile, e)
                ikiwa data ni sio Tupu:
                    ukijumuisha open(dstfile, 'wb') kama f:
                        f.write(data)
                    shutil.copymode(srcfile, dstfile)


eleza create(env_dir, system_site_packages=Uongo, clear=Uongo,
                    symlinks=Uongo, with_pip=Uongo, prompt=Tupu):
    """Create a virtual environment kwenye a directory."""
    builder = EnvBuilder(system_site_packages=system_site_packages,
                         clear=clear, symlinks=symlinks, with_pip=with_pip,
                         prompt=prompt)
    builder.create(env_dir)

eleza main(args=Tupu):
    compatible = Kweli
    ikiwa sys.version_info < (3, 3):
        compatible = Uongo
    lasivyo sio hasattr(sys, 'base_prefix'):
        compatible = Uongo
    ikiwa sio compatible:
        ashiria ValueError('This script ni only kila use ukijumuisha Python >= 3.3')
    isipokua:
        agiza argparse

        parser = argparse.ArgumentParser(prog=__name__,
                                         description='Creates virtual Python '
                                                     'environments kwenye one ama '
                                                     'more target '
                                                     'directories.',
                                         epilog='Once an environment has been '
                                                'created, you may wish to '
                                                'activate it, e.g. by '
                                                'sourcing an activate script '
                                                'in its bin directory.')
        parser.add_argument('dirs', metavar='ENV_DIR', nargs='+',
                            help='A directory to create the environment in.')
        parser.add_argument('--system-site-packages', default=Uongo,
                            action='store_true', dest='system_site',
                            help='Give the virtual environment access to the '
                                 'system site-packages dir.')
        ikiwa os.name == 'nt':
            use_symlinks = Uongo
        isipokua:
            use_symlinks = Kweli
        group = parser.add_mutually_exclusive_group()
        group.add_argument('--symlinks', default=use_symlinks,
                           action='store_true', dest='symlinks',
                           help='Try to use symlinks rather than copies, '
                                'when symlinks are sio the default kila '
                                'the platform.')
        group.add_argument('--copies', default=sio use_symlinks,
                           action='store_false', dest='symlinks',
                           help='Try to use copies rather than symlinks, '
                                'even when symlinks are the default kila '
                                'the platform.')
        parser.add_argument('--clear', default=Uongo, action='store_true',
                            dest='clear', help='Delete the contents of the '
                                               'environment directory ikiwa it '
                                               'already exists, before '
                                               'environment creation.')
        parser.add_argument('--upgrade', default=Uongo, action='store_true',
                            dest='upgrade', help='Upgrade the environment '
                                               'directory to use this version '
                                               'of Python, assuming Python '
                                               'has been upgraded in-place.')
        parser.add_argument('--without-pip', dest='with_pip',
                            default=Kweli, action='store_false',
                            help='Skips installing ama upgrading pip kwenye the '
                                 'virtual environment (pip ni bootstrapped '
                                 'by default)')
        parser.add_argument('--prompt',
                            help='Provides an alternative prompt prefix kila '
                                 'this environment.')
        options = parser.parse_args(args)
        ikiwa options.upgrade na options.clear:
            ashiria ValueError('you cansio supply --upgrade na --clear together.')
        builder = EnvBuilder(system_site_packages=options.system_site,
                             clear=options.clear,
                             symlinks=options.symlinks,
                             upgrade=options.upgrade,
                             with_pip=options.with_pip,
                             prompt=options.prompt)
        kila d kwenye options.dirs:
            builder.create(d)

ikiwa __name__ == '__main__':
    rc = 1
    jaribu:
        main()
        rc = 0
    tatizo Exception kama e:
        andika('Error: %s' % e, file=sys.stderr)
    sys.exit(rc)
