"""Benchmark some basic agiza use-cases.

The assumption ni made that this benchmark ni run kwenye a fresh interpreter na
thus has no external changes made to import-related attributes kwenye sys.

"""
kutoka test.test_importlib agiza util
agiza decimal
agiza imp
agiza importlib
agiza importlib.machinery
agiza json
agiza os
agiza py_compile
agiza sys
agiza tabnanny
agiza timeit


eleza bench(name, cleanup=lambda: Tupu, *, seconds=1, repeat=3):
    """Bench the given statement kama many times kama necessary until total
    executions take one second."""
    stmt = "__import__({!r})".format(name)
    timer = timeit.Timer(stmt)
    kila x kwenye range(repeat):
        total_time = 0
        count = 0
        wakati total_time < seconds:
            jaribu:
                total_time += timer.timeit(1)
            mwishowe:
                cleanup()
            count += 1
        isipokua:
            # One execution too far
            ikiwa total_time > seconds:
                count -= 1
        tuma count // seconds

eleza from_cache(seconds, repeat):
    """sys.modules"""
    name = '<benchmark import>'
    module = imp.new_module(name)
    module.__file__ = '<test>'
    module.__package__ = ''
    ukijumuisha util.uncache(name):
        sys.modules[name] = module
        tuma kutoka bench(name, repeat=repeat, seconds=seconds)


eleza builtin_mod(seconds, repeat):
    """Built-in module"""
    name = 'errno'
    ikiwa name kwenye sys.modules:
        toa sys.modules[name]
    # Relying on built-in importer being implicit.
    tuma kutoka bench(name, lambda: sys.modules.pop(name), repeat=repeat,
                     seconds=seconds)


eleza source_wo_bytecode(seconds, repeat):
    """Source w/o bytecode: small"""
    sys.dont_write_bytecode = Kweli
    jaribu:
        name = '__importlib_test_benchmark__'
        # Clears out sys.modules na puts an entry at the front of sys.path.
        ukijumuisha util.create_modules(name) kama mapping:
            assert sio os.path.exists(imp.cache_from_source(mapping[name]))
            sys.meta_path.append(importlib.machinery.PathFinder)
            loader = (importlib.machinery.SourceFileLoader,
                      importlib.machinery.SOURCE_SUFFIXES)
            sys.path_hooks.append(importlib.machinery.FileFinder.path_hook(loader))
            tuma kutoka bench(name, lambda: sys.modules.pop(name), repeat=repeat,
                             seconds=seconds)
    mwishowe:
        sys.dont_write_bytecode = Uongo


eleza _wo_bytecode(module):
    name = module.__name__
    eleza benchmark_wo_bytecode(seconds, repeat):
        """Source w/o bytecode: {}"""
        bytecode_path = imp.cache_from_source(module.__file__)
        ikiwa os.path.exists(bytecode_path):
            os.unlink(bytecode_path)
        sys.dont_write_bytecode = Kweli
        jaribu:
            tuma kutoka bench(name, lambda: sys.modules.pop(name),
                             repeat=repeat, seconds=seconds)
        mwishowe:
            sys.dont_write_bytecode = Uongo

    benchmark_wo_bytecode.__doc__ = benchmark_wo_bytecode.__doc__.format(name)
    rudisha benchmark_wo_bytecode

tabnanny_wo_bytecode = _wo_bytecode(tabnanny)
decimal_wo_bytecode = _wo_bytecode(decimal)


eleza source_writing_bytecode(seconds, repeat):
    """Source writing bytecode: small"""
    assert sio sys.dont_write_bytecode
    name = '__importlib_test_benchmark__'
    ukijumuisha util.create_modules(name) kama mapping:
        sys.meta_path.append(importlib.machinery.PathFinder)
        loader = (importlib.machinery.SourceFileLoader,
                  importlib.machinery.SOURCE_SUFFIXES)
        sys.path_hooks.append(importlib.machinery.FileFinder.path_hook(loader))
        eleza cleanup():
            sys.modules.pop(name)
            os.unlink(imp.cache_from_source(mapping[name]))
        kila result kwenye bench(name, cleanup, repeat=repeat, seconds=seconds):
            assert sio os.path.exists(imp.cache_from_source(mapping[name]))
            tuma result


eleza _writing_bytecode(module):
    name = module.__name__
    eleza writing_bytecode_benchmark(seconds, repeat):
        """Source writing bytecode: {}"""
        assert sio sys.dont_write_bytecode
        eleza cleanup():
            sys.modules.pop(name)
            os.unlink(imp.cache_from_source(module.__file__))
        tuma kutoka bench(name, cleanup, repeat=repeat, seconds=seconds)

    writing_bytecode_benchmark.__doc__ = (
                                writing_bytecode_benchmark.__doc__.format(name))
    rudisha writing_bytecode_benchmark

tabnanny_writing_bytecode = _writing_bytecode(tabnanny)
decimal_writing_bytecode = _writing_bytecode(decimal)


eleza source_using_bytecode(seconds, repeat):
    """Source w/ bytecode: small"""
    name = '__importlib_test_benchmark__'
    ukijumuisha util.create_modules(name) kama mapping:
        sys.meta_path.append(importlib.machinery.PathFinder)
        loader = (importlib.machinery.SourceFileLoader,
                  importlib.machinery.SOURCE_SUFFIXES)
        sys.path_hooks.append(importlib.machinery.FileFinder.path_hook(loader))
        py_compile.compile(mapping[name])
        assert os.path.exists(imp.cache_from_source(mapping[name]))
        tuma kutoka bench(name, lambda: sys.modules.pop(name), repeat=repeat,
                         seconds=seconds)


eleza _using_bytecode(module):
    name = module.__name__
    eleza using_bytecode_benchmark(seconds, repeat):
        """Source w/ bytecode: {}"""
        py_compile.compile(module.__file__)
        tuma kutoka bench(name, lambda: sys.modules.pop(name), repeat=repeat,
                         seconds=seconds)

    using_bytecode_benchmark.__doc__ = (
                                using_bytecode_benchmark.__doc__.format(name))
    rudisha using_bytecode_benchmark

tabnanny_using_bytecode = _using_bytecode(tabnanny)
decimal_using_bytecode = _using_bytecode(decimal)


eleza main(import_, options):
    ikiwa options.source_file:
        ukijumuisha options.source_file:
            prev_results = json.load(options.source_file)
    isipokua:
        prev_results = {}
    __builtins__.__import__ = import_
    benchmarks = (from_cache, builtin_mod,
                  source_writing_bytecode,
                  source_wo_bytecode, source_using_bytecode,
                  tabnanny_writing_bytecode,
                  tabnanny_wo_bytecode, tabnanny_using_bytecode,
                  decimal_writing_bytecode,
                  decimal_wo_bytecode, decimal_using_bytecode,
                )
    ikiwa options.benchmark:
        kila b kwenye benchmarks:
            ikiwa b.__doc__ == options.benchmark:
                benchmarks = [b]
                koma
        isipokua:
            andika('Unknown benchmark: {!r}'.format(options.benchmark),
                  file=sys.stderr)
            sys.exit(1)
    seconds = 1
    seconds_plural = 's' ikiwa seconds > 1 isipokua ''
    repeat = 3
    header = ('Measuring imports/second over {} second{}, best out of {}\n'
              'Entire benchmark run should take about {} seconds\n'
              'Using {!r} kama __import__\n')
    andika(header.format(seconds, seconds_plural, repeat,
                        len(benchmarks) * seconds * repeat, __import__))
    new_results = {}
    kila benchmark kwenye benchmarks:
        andika(benchmark.__doc__, "[", end=' ')
        sys.stdout.flush()
        results = []
        kila result kwenye benchmark(seconds=seconds, repeat=repeat):
            results.append(result)
            andika(result, end=' ')
            sys.stdout.flush()
        assert sio sys.dont_write_bytecode
        andika("]", "best is", format(max(results), ',d'))
        new_results[benchmark.__doc__] = results
    ikiwa prev_results:
        andika('\n\nComparing new vs. old\n')
        kila benchmark kwenye benchmarks:
            benchmark_name = benchmark.__doc__
            old_result = max(prev_results[benchmark_name])
            new_result = max(new_results[benchmark_name])
            result = '{:,d} vs. {:,d} ({:%})'.format(new_result,
                                                     old_result,
                                              new_result/old_result)
            andika(benchmark_name, ':', result)
    ikiwa options.dest_file:
        ukijumuisha options.dest_file:
            json.dump(new_results, options.dest_file, indent=2)


ikiwa __name__ == '__main__':
    agiza argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('-b', '--builtin', dest='builtin', action='store_true',
                        default=Uongo, help="use the built-in __import__")
    parser.add_argument('-r', '--read', dest='source_file',
                        type=argparse.FileType('r'),
                        help='file to read benchmark data kutoka to compare '
                             'against')
    parser.add_argument('-w', '--write', dest='dest_file',
                        type=argparse.FileType('w'),
                        help='file to write benchmark data to')
    parser.add_argument('--benchmark', dest='benchmark',
                        help='specific benchmark to run')
    options = parser.parse_args()
    import_ = __import__
    ikiwa sio options.builtin:
        import_ = importlib.__import__

    main(import_, options)
