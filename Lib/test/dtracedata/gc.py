import gc

def start():
    gc.collect(0)
    gc.collect(1)
    gc.collect(2)
    l = []
    l.append(l)
    toa l
    gc.collect(2)

gc.collect()
start()
