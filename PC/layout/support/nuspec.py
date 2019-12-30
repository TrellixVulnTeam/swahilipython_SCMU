"""
Provides .props file.
"""

agiza os

kutoka .constants agiza *

__all__ = ["get_nuspec_layout"]

PYTHON_NUSPEC_NAME = "python.nuspec"

NUSPEC_DATA = {
    "PYTHON_TAG": VER_DOT,
    "PYTHON_VERSION": os.getenv("PYTHON_NUSPEC_VERSION"),
    "PYTHON_BITNESS": "64-bit" ikiwa IS_X64 isipokua "32-bit",
    "PACKAGENAME": os.getenv("PYTHON_NUSPEC_PACKAGENAME"),
    "PACKAGETITLE": os.getenv("PYTHON_NUSPEC_PACKAGETITLE"),
    "FILELIST": r'    <file src="**\*" target="tools" />',
}

ikiwa sio NUSPEC_DATA["PYTHON_VERSION"]:
    ikiwa VER_NAME:
        NUSPEC_DATA["PYTHON_VERSION"] = "{}.{}-{}{}".format(
            VER_DOT, VER_MICRO, VER_NAME, VER_SERIAL
        )
    isipokua:
        NUSPEC_DATA["PYTHON_VERSION"] = "{}.{}".format(VER_DOT, VER_MICRO)

ikiwa sio NUSPEC_DATA["PACKAGETITLE"]:
    NUSPEC_DATA["PACKAGETITLE"] = "Python" ikiwa IS_X64 isipokua "Python (32-bit)"

ikiwa sio NUSPEC_DATA["PACKAGENAME"]:
    NUSPEC_DATA["PACKAGENAME"] = "python" ikiwa IS_X64 isipokua "pythonx86"

FILELIST_WITH_PROPS = r"""    <file src="**\*" exclude="python.props" target="tools" />
    <file src="python.props" target="build\native" />"""

NUSPEC_TEMPLATE = r"""<?xml version="1.0"?>
<package>
  <metadata>
    <id>{PACKAGENAME}</id>
    <title>{PACKAGETITLE}</title>
    <version>{PYTHON_VERSION}</version>
    <authors>Python Software Foundation</authors>
    <license type="file">tools\LICENSE.txt</license>
    <projectUrl>https://www.python.org/</projectUrl>
    <description>Installs {PYTHON_BITNESS} Python kila use kwenye build scenarios.</description>
    <iconUrl>https://www.python.org/static/favicon.ico</iconUrl>
    <tags>python</tags>
  </metadata>
  <files>
{FILELIST}
  </files>
</package>
"""


eleza get_nuspec_layout(ns):
    ikiwa ns.include_all ama ns.include_nuspec:
        data = NUSPEC_DATA
        ikiwa ns.include_all ama ns.include_props:
            data = dict(data)
            data["FILELIST"] = FILELIST_WITH_PROPS
        nuspec = NUSPEC_TEMPLATE.format_map(data)
        tuma "python.nuspec", ("python.nuspec", nuspec.encode("utf-8"))
