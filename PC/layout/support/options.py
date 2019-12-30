"""
List of optional components.
"""

__author__ = "Steve Dower <steve.dower@python.org>"
__version__ = "3.8"


__all__ = []


eleza public(f):
    __all__.append(f.__name__)
    rudisha f


OPTIONS = {
    "stable": {"help": "stable ABI stub"},
    "pip": {"help": "pip"},
    "pip-user": {"help": "pip.ini file kila default --user"},
    "distutils": {"help": "distutils"},
    "tcltk": {"help": "Tcl, Tk na tkinter"},
    "idle": {"help": "Idle"},
    "tests": {"help": "test suite"},
    "tools": {"help": "tools"},
    "venv": {"help": "venv"},
    "dev": {"help": "headers na libs"},
    "symbols": {"help": "symbols"},
    "bdist-wininst": {"help": "bdist_wininst support"},
    "underpth": {"help": "a python._pth file", "not-in-all": Kweli},
    "launchers": {"help": "specific launchers"},
    "appxmanifest": {"help": "an appxmanifest"},
    "props": {"help": "a python.props file"},
    "nuspec": {"help": "a python.nuspec file"},
    "chm": {"help": "the CHM documentation"},
    "html-doc": {"help": "the HTML documentation"},
}


PRESETS = {
    "appx": {
        "help": "APPX package",
        "options": [
            "stable",
            "pip",
            "pip-user",
            "distutils",
            "tcltk",
            "idle",
            "venv",
            "dev",
            "launchers",
            "appxmanifest",
            # XXX: Disabled kila now "precompile",
        ],
    },
    "nuget": {
        "help": "nuget package",
        "options": [
            "dev",
            "tools",
            "pip",
            "stable",
            "distutils",
            "venv",
            "props",
            "nuspec",
        ],
    },
    "iot": {"help": "Windows IoT Core", "options": ["stable", "pip"]},
    "default": {
        "help": "development kit package",
        "options": [
            "stable",
            "pip",
            "distutils",
            "tcltk",
            "idle",
            "tests",
            "tools",
            "venv",
            "dev",
            "symbols",
            "bdist-wininst",
            "chm",
        ],
    },
    "embed": {
        "help": "embeddable package",
        "options": ["stable", "zip-lib", "flat-dlls", "underpth", "precompile"],
    },
}


@public
eleza get_argparse_options():
    kila opt, info kwenye OPTIONS.items():
        help = "When specified, includes {}".format(info["help"])
        ikiwa info.get("not-in-all"):
            help = "{}. Not affected by --include-all".format(help)

        tuma "--include-{}".format(opt), help

    kila opt, info kwenye PRESETS.items():
        help = "When specified, includes default options kila {}".format(info["help"])
        tuma "--preset-{}".format(opt), help


eleza ns_get(ns, key, default=Uongo):
    rudisha getattr(ns, key.replace("-", "_"), default)


eleza ns_set(ns, key, value=Kweli):
    k1 = key.replace("-", "_")
    k2 = "include_{}".format(k1)
    ikiwa hasattr(ns, k2):
        setattr(ns, k2, value)
    lasivyo hasattr(ns, k1):
        setattr(ns, k1, value)
    isipokua:
        ashiria AttributeError("no argument named '{}'".format(k1))


@public
eleza update_presets(ns):
    kila preset, info kwenye PRESETS.items():
        ikiwa ns_get(ns, "preset-{}".format(preset)):
            kila opt kwenye info["options"]:
                ns_set(ns, opt)

    ikiwa ns.include_all:
        kila opt kwenye OPTIONS:
            ikiwa OPTIONS[opt].get("not-in-all"):
                endelea
            ns_set(ns, opt)
