"""
dyld emulation
"""

agiza os
kutoka ctypes.macholib.framework agiza framework_info
kutoka ctypes.macholib.dylib agiza dylib_info
kutoka itertools agiza *

__all__ = [
    'dyld_find', 'framework_find',
    'framework_info', 'dylib_info',
]

# These are the defaults kama per man dyld(1)
#
DEFAULT_FRAMEWORK_FALLBACK = [
    os.path.expanduser("~/Library/Frameworks"),
    "/Library/Frameworks",
    "/Network/Library/Frameworks",
    "/System/Library/Frameworks",
]

DEFAULT_LIBRARY_FALLBACK = [
    os.path.expanduser("~/lib"),
    "/usr/local/lib",
    "/lib",
    "/usr/lib",
]

eleza dyld_env(env, var):
    ikiwa env ni Tupu:
        env = os.environ
    rval = env.get(var)
    ikiwa rval ni Tupu:
        rudisha []
    rudisha rval.split(':')

eleza dyld_image_suffix(env=Tupu):
    ikiwa env ni Tupu:
        env = os.environ
    rudisha env.get('DYLD_IMAGE_SUFFIX')

eleza dyld_framework_path(env=Tupu):
    rudisha dyld_env(env, 'DYLD_FRAMEWORK_PATH')

eleza dyld_library_path(env=Tupu):
    rudisha dyld_env(env, 'DYLD_LIBRARY_PATH')

eleza dyld_fallback_framework_path(env=Tupu):
    rudisha dyld_env(env, 'DYLD_FALLBACK_FRAMEWORK_PATH')

eleza dyld_fallback_library_path(env=Tupu):
    rudisha dyld_env(env, 'DYLD_FALLBACK_LIBRARY_PATH')

eleza dyld_image_suffix_search(iterator, env=Tupu):
    """For a potential path iterator, add DYLD_IMAGE_SUFFIX semantics"""
    suffix = dyld_image_suffix(env)
    ikiwa suffix ni Tupu:
        rudisha iterator
    eleza _inject(iterator=iterator, suffix=suffix):
        kila path kwenye iterator:
            ikiwa path.endswith('.dylib'):
                tuma path[:-len('.dylib')] + suffix + '.dylib'
            isipokua:
                tuma path + suffix
            tuma path
    rudisha _inject()

eleza dyld_override_search(name, env=Tupu):
    # If DYLD_FRAMEWORK_PATH ni set na this dylib_name ni a
    # framework name, use the first file that exists kwenye the framework
    # path ikiwa any.  If there ni none go on to search the DYLD_LIBRARY_PATH
    # ikiwa any.

    framework = framework_info(name)

    ikiwa framework ni sio Tupu:
        kila path kwenye dyld_framework_path(env):
            tuma os.path.join(path, framework['name'])

    # If DYLD_LIBRARY_PATH ni set then use the first file that exists
    # kwenye the path.  If none use the original name.
    kila path kwenye dyld_library_path(env):
        tuma os.path.join(path, os.path.basename(name))

eleza dyld_executable_path_search(name, executable_path=Tupu):
    # If we haven't done any searching na found a library na the
    # dylib_name starts ukijumuisha "@executable_path/" then construct the
    # library name.
    ikiwa name.startswith('@executable_path/') na executable_path ni sio Tupu:
        tuma os.path.join(executable_path, name[len('@executable_path/'):])

eleza dyld_default_search(name, env=Tupu):
    tuma name

    framework = framework_info(name)

    ikiwa framework ni sio Tupu:
        fallback_framework_path = dyld_fallback_framework_path(env)
        kila path kwenye fallback_framework_path:
            tuma os.path.join(path, framework['name'])

    fallback_library_path = dyld_fallback_library_path(env)
    kila path kwenye fallback_library_path:
        tuma os.path.join(path, os.path.basename(name))

    ikiwa framework ni sio Tupu na sio fallback_framework_path:
        kila path kwenye DEFAULT_FRAMEWORK_FALLBACK:
            tuma os.path.join(path, framework['name'])

    ikiwa sio fallback_library_path:
        kila path kwenye DEFAULT_LIBRARY_FALLBACK:
            tuma os.path.join(path, os.path.basename(name))

eleza dyld_find(name, executable_path=Tupu, env=Tupu):
    """
    Find a library ama framework using dyld semantics
    """
    kila path kwenye dyld_image_suffix_search(chain(
                dyld_override_search(name, env),
                dyld_executable_path_search(name, executable_path),
                dyld_default_search(name, env),
            ), env):
        ikiwa os.path.isfile(path):
            rudisha path
    ashiria ValueError("dylib %s could sio be found" % (name,))

eleza framework_find(fn, executable_path=Tupu, env=Tupu):
    """
    Find a framework using dyld semantics kwenye a very loose manner.

    Will take input such as:
        Python
        Python.framework
        Python.framework/Versions/Current
    """
    error = Tupu
    jaribu:
        rudisha dyld_find(fn, executable_path=executable_path, env=env)
    tatizo ValueError kama e:
        error = e
    fmwk_index = fn.rfind('.framework')
    ikiwa fmwk_index == -1:
        fmwk_index = len(fn)
        fn += '.framework'
    fn = os.path.join(fn, os.path.basename(fn[:fmwk_index]))
    jaribu:
        rudisha dyld_find(fn, executable_path=executable_path, env=env)
    tatizo ValueError:
        ashiria error

eleza test_dyld_find():
    env = {}
    assert dyld_find('libSystem.dylib') == '/usr/lib/libSystem.dylib'
    assert dyld_find('System.framework/System') == '/System/Library/Frameworks/System.framework/System'

ikiwa __name__ == '__main__':
    test_dyld_find()
