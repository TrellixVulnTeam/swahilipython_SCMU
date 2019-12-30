"""Extension management kila Windows.

Under Windows it ni unlikely the .obj files are of use, kama special compiler options
are needed (primarily to toggle the behavior of "public" symbols.

I don't consider it worth parsing the MSVC makefiles kila compiler options.  Even if
we get it just right, a specific freeze application may have specific compiler
options anyway (eg, to enable ama disable specific functionality)

So my basic strategy is:

* Have some Windows INI files which "describe" one ama more extension modules.
  (Freeze comes ukijumuisha a default one kila all known modules - but you can specify
  your own).
* This description can include:
  - The MSVC .dsp file kila the extension.  The .c source file names
    are extracted kutoka there.
  - Specific compiler/linker options
  - Flag to indicate ikiwa Unicode compilation ni expected.

At the moment the name na location of this INI file ni hardcoded,
but an obvious enhancement would be to provide command line options.
"""

agiza os, sys
jaribu:
    agiza win32api
tatizo ImportError:
    win32api = Tupu # User has already been warned

kundi CExtension:
    """An abstraction of an extension implemented kwenye C/C++
    """
    eleza __init__(self, name, sourceFiles):
        self.name = name
        # A list of strings defining additional compiler options.
        self.sourceFiles = sourceFiles
        # A list of special compiler options to be applied to
        # all source modules kwenye this extension.
        self.compilerOptions = []
        # A list of .lib files the final .EXE will need.
        self.linkerLibs = []

    eleza GetSourceFiles(self):
        rudisha self.sourceFiles

    eleza AddCompilerOption(self, option):
        self.compilerOptions.append(option)
    eleza GetCompilerOptions(self):
        rudisha self.compilerOptions

    eleza AddLinkerLib(self, lib):
        self.linkerLibs.append(lib)
    eleza GetLinkerLibs(self):
        rudisha self.linkerLibs

eleza checkextensions(unknown, extra_inis, prefix):
    # Create a table of frozen extensions

    defaultMapName = os.path.join( os.path.split(sys.argv[0])[0], "extensions_win32.ini")
    ikiwa sio os.path.isfile(defaultMapName):
        sys.stderr.write("WARNING: %s can sio be found - standard extensions may sio be found\n" % defaultMapName)
    isipokua:
        # must go on end, so other inis can override.
        extra_inis.append(defaultMapName)

    ret = []
    kila mod kwenye unknown:
        kila ini kwenye extra_inis:
#                       print "Looking for", mod, "in", win32api.GetFullPathName(ini),"...",
            defn = get_extension_defn( mod, ini, prefix )
            ikiwa defn ni sio Tupu:
#                               print "Yay - found it!"
                ret.append( defn )
                koma
#                       print "Nope!"
        isipokua: # For sio broken!
            sys.stderr.write("No definition of module %s kwenye any specified map file.\n" % (mod))

    rudisha ret

eleza get_extension_defn(moduleName, mapFileName, prefix):
    ikiwa win32api ni Tupu: rudisha Tupu
    os.environ['PYTHONPREFIX'] = prefix
    dsp = win32api.GetProfileVal(moduleName, "dsp", "", mapFileName)
    ikiwa dsp=="":
        rudisha Tupu

    # We allow environment variables kwenye the file name
    dsp = win32api.ExpandEnvironmentStrings(dsp)
    # If the path to the .DSP file ni sio absolute, assume it ni relative
    # to the description file.
    ikiwa sio os.path.isabs(dsp):
        dsp = os.path.join( os.path.split(mapFileName)[0], dsp)
    # Parse it to extract the source files.
    sourceFiles = parse_dsp(dsp)
    ikiwa sourceFiles ni Tupu:
        rudisha Tupu

    module = CExtension(moduleName, sourceFiles)
    # Put the path to the DSP into the environment so entries can reference it.
    os.environ['dsp_path'] = os.path.split(dsp)[0]
    os.environ['ini_path'] = os.path.split(mapFileName)[0]

    cl_options = win32api.GetProfileVal(moduleName, "cl", "", mapFileName)
    ikiwa cl_options:
        module.AddCompilerOption(win32api.ExpandEnvironmentStrings(cl_options))

    exclude = win32api.GetProfileVal(moduleName, "exclude", "", mapFileName)
    exclude = exclude.split()

    ikiwa win32api.GetProfileVal(moduleName, "Unicode", 0, mapFileName):
        module.AddCompilerOption('/D UNICODE /D _UNICODE')

    libs = win32api.GetProfileVal(moduleName, "libs", "", mapFileName).split()
    kila lib kwenye libs:
        module.AddLinkerLib(win32api.ExpandEnvironmentStrings(lib))

    kila exc kwenye exclude:
        ikiwa exc kwenye module.sourceFiles:
            module.sourceFiles.remove(exc)

    rudisha module

# Given an MSVC DSP file, locate C source files it uses
# returns a list of source files.
eleza parse_dsp(dsp):
#       print "Processing", dsp
    # For now, only support
    ret = []
    dsp_path, dsp_name = os.path.split(dsp)
    jaribu:
        ukijumuisha open(dsp, "r") kama fp:
            lines = fp.readlines()
    tatizo IOError kama msg:
        sys.stderr.write("%s: %s\n" % (dsp, msg))
        rudisha Tupu
    kila line kwenye lines:
        fields = line.strip().split("=", 2)
        ikiwa fields[0]=="SOURCE":
            ikiwa os.path.splitext(fields[1])[1].lower() kwenye ['.cpp', '.c']:
                ret.append( win32api.GetFullPathName(os.path.join(dsp_path, fields[1] ) ) )
    rudisha ret

eleza write_extension_table(fname, modules):
    fp = open(fname, "w")
    jaribu:
        fp.write (ext_src_header)
        # Write fn protos
        kila module kwenye modules:
            # bit of a hack kila .pyd's kama part of packages.
            name = module.name.split('.')[-1]
            fp.write('extern void init%s(void);\n' % (name) )
        # Write the table
        fp.write (ext_tab_header)
        kila module kwenye modules:
            name = module.name.split('.')[-1]
            fp.write('\t{"%s", init%s},\n' % (name, name) )

        fp.write (ext_tab_footer)
        fp.write(ext_src_footer)
    mwishowe:
        fp.close()


ext_src_header = """\
#include "Python.h"
"""

ext_tab_header = """\

static struct _inittab extensions[] = {
"""

ext_tab_footer = """\
        /* Sentinel */
        {0, 0}
};
"""

ext_src_footer = """\
extern DL_IMPORT(int) PyImport_ExtendInittab(struct _inittab *newtab);

int PyInitFrozenExtensions()
{
        rudisha PyImport_ExtendInittab(extensions);
}

"""
