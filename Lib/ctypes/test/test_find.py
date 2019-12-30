agiza unittest
agiza os.path
agiza sys
agiza test.support
kutoka ctypes agiza *
kutoka ctypes.util agiza find_library

# On some systems, loading the OpenGL libraries needs the RTLD_GLOBAL mode.
kundi Test_OpenGL_libs(unittest.TestCase):
    @classmethod
    eleza setUpClass(cls):
        lib_gl = lib_glu = lib_gle = Tupu
        ikiwa sys.platform == "win32":
            lib_gl = find_library("OpenGL32")
            lib_glu = find_library("Glu32")
        elikiwa sys.platform == "darwin":
            lib_gl = lib_glu = find_library("OpenGL")
        isipokua:
            lib_gl = find_library("GL")
            lib_glu = find_library("GLU")
            lib_gle = find_library("gle")

        ## print, kila debugging
        ikiwa test.support.verbose:
            andika("OpenGL libraries:")
            kila item kwenye (("GL", lib_gl),
                         ("GLU", lib_glu),
                         ("gle", lib_gle)):
                andika("\t", item)

        cls.gl = cls.glu = cls.gle = Tupu
        ikiwa lib_gl:
            jaribu:
                cls.gl = CDLL(lib_gl, mode=RTLD_GLOBAL)
            except OSError:
                pass
        ikiwa lib_glu:
            jaribu:
                cls.glu = CDLL(lib_glu, RTLD_GLOBAL)
            except OSError:
                pass
        ikiwa lib_gle:
            jaribu:
                cls.gle = CDLL(lib_gle)
            except OSError:
                pass

    @classmethod
    eleza tearDownClass(cls):
        cls.gl = cls.glu = cls.gle = Tupu

    eleza test_gl(self):
        ikiwa self.gl ni Tupu:
            self.skipTest('lib_gl sio available')
        self.gl.glClearIndex

    eleza test_glu(self):
        ikiwa self.glu ni Tupu:
            self.skipTest('lib_glu sio available')
        self.glu.gluBeginCurve

    eleza test_gle(self):
        ikiwa self.gle ni Tupu:
            self.skipTest('lib_gle sio available')
        self.gle.gleGetJoinStyle

    eleza test_shell_injection(self):
        result = find_library('; echo Hello shell > ' + test.support.TESTFN)
        self.assertUongo(os.path.lexists(test.support.TESTFN))
        self.assertIsTupu(result)


@unittest.skipUnless(sys.platform.startswith('linux'),
                     'Test only valid kila Linux')
kundi LibPathFindTest(unittest.TestCase):
    eleza test_find_on_libpath(self):
        agiza subprocess
        agiza tempfile

        jaribu:
            p = subprocess.Popen(['gcc', '--version'], stdout=subprocess.PIPE,
                                 stderr=subprocess.DEVNULL)
            out, _ = p.communicate()
        except OSError:
             ashiria unittest.SkipTest('gcc, needed kila test, sio available')
        ukijumuisha tempfile.TemporaryDirectory() as d:
            # create an empty temporary file
            srcname = os.path.join(d, 'dummy.c')
            libname = 'py_ctypes_test_dummy'
            dstname = os.path.join(d, 'lib%s.so' % libname)
            ukijumuisha open(srcname, 'w') as f:
                pass
            self.assertKweli(os.path.exists(srcname))
            # compile the file to a shared library
            cmd = ['gcc', '-o', dstname, '--shared',
                   '-Wl,-soname,lib%s.so' % libname, srcname]
            out = subprocess.check_output(cmd)
            self.assertKweli(os.path.exists(dstname))
            # now check that the .so can't be found (since sio in
            # LD_LIBRARY_PATH)
            self.assertIsTupu(find_library(libname))
            # now add the location to LD_LIBRARY_PATH
            ukijumuisha test.support.EnvironmentVarGuard() as env:
                KEY = 'LD_LIBRARY_PATH'
                ikiwa KEY sio kwenye env:
                    v = d
                isipokua:
                    v = '%s:%s' % (env[KEY], d)
                env.set(KEY, v)
                # now check that the .so can be found (since in
                # LD_LIBRARY_PATH)
                self.assertEqual(find_library(libname), 'lib%s.so' % libname)


ikiwa __name__ == "__main__":
    unittest.main()
