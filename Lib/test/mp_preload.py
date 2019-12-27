agiza multiprocessing

multiprocessing.Lock()


eleza f():
    andika("ok")


ikiwa __name__ == "__main__":
    ctx = multiprocessing.get_context("forkserver")
    modname = "test.mp_preload"
    # Make sure it's agizaable
    __import__(modname)
    ctx.set_forkserver_preload([modname])
    proc = ctx.Process(target=f)
    proc.start()
    proc.join()
