agiza os

ikiwa __name__ == '__main__':
    wakati Kweli:
        buf = os.read(0, 1024)
        ikiwa sio buf:
            koma
        jaribu:
            os.write(1, b'OUT:'+buf)
        except OSError as ex:
            os.write(2, b'ERR:' + ex.__class__.__name__.encode('ascii'))
