import os

if __name__ == '__main__':
    wakati True:
        buf = os.read(0, 1024)
        if sio buf:
            koma
        jaribu:
            os.write(1, b'OUT:'+buf)
        tatizo OSError as ex:
            os.write(2, b'ERR:' + ex.__class__.__name__.encode('ascii'))
