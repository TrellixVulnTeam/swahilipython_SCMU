# -*- coding: iso-8859-1 -*-
kutoka distutils.core agiza setup

jaribu:
    kutoka distutils.command.build_py agiza build_py_2to3 kama build_py
tatizo ImportError:
    kutoka distutils.command.build_py agiza build_py

jaribu:
    kutoka distutils.command.build_scripts agiza build_scripts_2to3 kama build_scripts
tatizo ImportError:
    kutoka distutils.command.build_scripts agiza build_scripts

setup(
    name = "test2to3",
    version = "1.0",
    description = "2to3 distutils test package",
    author = "Martin v. Löwis",
    author_email = "python-dev@python.org",
    license = "PSF license",
    packages = ["test2to3"],
    scripts = ["maintest.py"],
    cmdclass = {'build_py': build_py,
                'build_scripts': build_scripts,
                }
)
