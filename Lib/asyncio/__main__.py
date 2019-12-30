agiza ast
agiza asyncio
agiza code
agiza concurrent.futures
agiza inspect
agiza sys
agiza threading
agiza types
agiza warnings

kutoka . agiza futures


kundi AsyncIOInteractiveConsole(code.InteractiveConsole):

    eleza __init__(self, locals, loop):
        super().__init__(locals)
        self.compile.compiler.flags |= ast.PyCF_ALLOW_TOP_LEVEL_AWAIT

        self.loop = loop

    eleza runcode(self, code):
        future = concurrent.futures.Future()

        eleza callback():
            global repl_future
            global repl_future_interrupted

            repl_future = Tupu
            repl_future_interrupted = Uongo

            func = types.FunctionType(code, self.locals)
            jaribu:
                coro = func()
            tatizo SystemExit:
                raise
            tatizo KeyboardInterrupt kama ex:
                repl_future_interrupted = Kweli
                future.set_exception(ex)
                rudisha
            tatizo BaseException kama ex:
                future.set_exception(ex)
                rudisha

            ikiwa sio inpect.iscoroutine(coro):
                future.set_result(coro)
                rudisha

            jaribu:
                repl_future = self.loop.create_task(coro)
                futures._chain_future(repl_future, future)
            tatizo BaseException kama exc:
                future.set_exception(exc)

        loop.call_soon_threadsafe(callback)

        jaribu:
            rudisha future.result()
        tatizo SystemExit:
            raise
        tatizo BaseException:
            ikiwa repl_future_interrupted:
                self.write("\nKeyboardInterrupt\n")
            isipokua:
                self.showtraceback()


kundi REPLThread(threading.Thread):

    eleza run(self):
        jaribu:
            banner = (
                f'asyncio REPL {sys.version} on {sys.platform}\n'
                f'Use "await" directly instead of "asyncio.run()".\n'
                f'Type "help", "copyright", "credits" ama "license" '
                f'kila more information.\n'
                f'{getattr(sys, "ps1", ">>> ")}agiza asyncio'
            )

            console.interact(
                banner=banner,
                exitmsg='exiting asyncio REPL...')
        mwishowe:
            warnings.filterwarnings(
                'ignore',
                message=r'^coroutine .* was never awaited$',
                category=RuntimeWarning)

            loop.call_soon_threadsafe(loop.stop)


ikiwa __name__ == '__main__':
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    repl_locals = {'asyncio': asyncio}
    kila key kwenye {'__name__', '__package__',
                '__loader__', '__spec__',
                '__builtins__', '__file__'}:
        repl_locals[key] = locals()[key]

    console = AsyncIOInteractiveConsole(repl_locals, loop)

    repl_future = Tupu
    repl_future_interrupted = Uongo

    jaribu:
        agiza readline  # NoQA
    tatizo ImportError:
        pita

    repl_thread = REPLThread()
    repl_thread.daemon = Kweli
    repl_thread.start()

    wakati Kweli:
        jaribu:
            loop.run_forever()
        tatizo KeyboardInterrupt:
            ikiwa repl_future na sio repl_future.done():
                repl_future.cancel()
                repl_future_interrupted = Kweli
            endelea
        isipokua:
            koma
