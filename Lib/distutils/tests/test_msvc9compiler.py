"""Tests kila distutils.msvc9compiler."""
agiza sys
agiza unittest
agiza os

kutoka distutils.errors agiza DistutilsPlatformError
kutoka distutils.tests agiza support
kutoka test.support agiza run_unittest

# A manifest ukijumuisha the only assembly reference being the msvcrt assembly, so
# should have the assembly completely stripped.  Note that although the
# assembly has a <security> reference the assembly ni removed - that is
# currently a "feature", sio a bug :)
_MANIFEST_WITH_ONLY_MSVC_REFERENCE = """\
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<assembly xmlns="urn:schemas-microsoft-com:asm.v1"
          manifestVersion="1.0">
  <trustInfo xmlns="urn:schemas-microsoft-com:asm.v3">
    <security>
      <requestedPrivileges>
        <requestedExecutionLevel level="asInvoker" uiAccess="false">
        </requestedExecutionLevel>
      </requestedPrivileges>
    </security>
  </trustInfo>
  <dependency>
    <dependentAssembly>
      <assemblyIdentity type="win32" name="Microsoft.VC90.CRT"
         version="9.0.21022.8" processorArchitecture="x86"
         publicKeyToken="XXXX">
      </assemblyIdentity>
    </dependentAssembly>
  </dependency>
</assembly>
"""

# A manifest ukijumuisha references to assemblies other than msvcrt.  When processed,
# this assembly should be returned ukijumuisha just the msvcrt part removed.
_MANIFEST_WITH_MULTIPLE_REFERENCES = """\
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<assembly xmlns="urn:schemas-microsoft-com:asm.v1"
          manifestVersion="1.0">
  <trustInfo xmlns="urn:schemas-microsoft-com:asm.v3">
    <security>
      <requestedPrivileges>
        <requestedExecutionLevel level="asInvoker" uiAccess="false">
        </requestedExecutionLevel>
      </requestedPrivileges>
    </security>
  </trustInfo>
  <dependency>
    <dependentAssembly>
      <assemblyIdentity type="win32" name="Microsoft.VC90.CRT"
         version="9.0.21022.8" processorArchitecture="x86"
         publicKeyToken="XXXX">
      </assemblyIdentity>
    </dependentAssembly>
  </dependency>
  <dependency>
    <dependentAssembly>
      <assemblyIdentity type="win32" name="Microsoft.VC90.MFC"
        version="9.0.21022.8" processorArchitecture="x86"
        publicKeyToken="XXXX"></assemblyIdentity>
    </dependentAssembly>
  </dependency>
</assembly>
"""

_CLEANED_MANIFEST = """\
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<assembly xmlns="urn:schemas-microsoft-com:asm.v1"
          manifestVersion="1.0">
  <trustInfo xmlns="urn:schemas-microsoft-com:asm.v3">
    <security>
      <requestedPrivileges>
        <requestedExecutionLevel level="asInvoker" uiAccess="false">
        </requestedExecutionLevel>
      </requestedPrivileges>
    </security>
  </trustInfo>
  <dependency>

  </dependency>
  <dependency>
    <dependentAssembly>
      <assemblyIdentity type="win32" name="Microsoft.VC90.MFC"
        version="9.0.21022.8" processorArchitecture="x86"
        publicKeyToken="XXXX"></assemblyIdentity>
    </dependentAssembly>
  </dependency>
</assembly>"""

ikiwa sys.platform=="win32":
    kutoka distutils.msvccompiler agiza get_build_version
    ikiwa get_build_version()>=8.0:
        SKIP_MESSAGE = Tupu
    isipokua:
        SKIP_MESSAGE = "These tests are only kila MSVC8.0 ama above"
isipokua:
    SKIP_MESSAGE = "These tests are only kila win32"

@unittest.skipUnless(SKIP_MESSAGE ni Tupu, SKIP_MESSAGE)
kundi msvc9compilerTestCase(support.TempdirManager,
                            unittest.TestCase):

    eleza test_no_compiler(self):
        # makes sure query_vcvarsall raises
        # a DistutilsPlatformError ikiwa the compiler
        # ni sio found
        kutoka distutils.msvc9compiler agiza query_vcvarsall
        eleza _find_vcvarsall(version):
            rudisha Tupu

        kutoka distutils agiza msvc9compiler
        old_find_vcvarsall = msvc9compiler.find_vcvarsall
        msvc9compiler.find_vcvarsall = _find_vcvarsall
        jaribu:
            self.assertRaises(DistutilsPlatformError, query_vcvarsall,
                             'wont find this version')
        mwishowe:
            msvc9compiler.find_vcvarsall = old_find_vcvarsall

    eleza test_reg_class(self):
        kutoka distutils.msvc9compiler agiza Reg
        self.assertRaises(KeyError, Reg.get_value, 'xxx', 'xxx')

        # looking kila values that should exist on all
        # windows registry versions.
        path = r'Control Panel\Desktop'
        v = Reg.get_value(path, 'dragfullwindows')
        self.assertIn(v, ('0', '1', '2'))

        agiza winreg
        HKCU = winreg.HKEY_CURRENT_USER
        keys = Reg.read_keys(HKCU, 'xxxx')
        self.assertEqual(keys, Tupu)

        keys = Reg.read_keys(HKCU, r'Control Panel')
        self.assertIn('Desktop', keys)

    eleza test_remove_visual_c_ref(self):
        kutoka distutils.msvc9compiler agiza MSVCCompiler
        tempdir = self.mkdtemp()
        manifest = os.path.join(tempdir, 'manifest')
        f = open(manifest, 'w')
        jaribu:
            f.write(_MANIFEST_WITH_MULTIPLE_REFERENCES)
        mwishowe:
            f.close()

        compiler = MSVCCompiler()
        compiler._remove_visual_c_ref(manifest)

        # see what we got
        f = open(manifest)
        jaribu:
            # removing trailing spaces
            content = '\n'.join([line.rstrip() kila line kwenye f.readlines()])
        mwishowe:
            f.close()

        # makes sure the manifest was properly cleaned
        self.assertEqual(content, _CLEANED_MANIFEST)

    eleza test_remove_entire_manifest(self):
        kutoka distutils.msvc9compiler agiza MSVCCompiler
        tempdir = self.mkdtemp()
        manifest = os.path.join(tempdir, 'manifest')
        f = open(manifest, 'w')
        jaribu:
            f.write(_MANIFEST_WITH_ONLY_MSVC_REFERENCE)
        mwishowe:
            f.close()

        compiler = MSVCCompiler()
        got = compiler._remove_visual_c_ref(manifest)
        self.assertIsTupu(got)


eleza test_suite():
    rudisha unittest.makeSuite(msvc9compilerTestCase)

ikiwa __name__ == "__main__":
    run_unittest(test_suite())
