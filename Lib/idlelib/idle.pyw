jaribu:
    agiza idlelib.pyshell
tatizo ImportError:
    # IDLE ni sio installed, but maybe pyshell ni on sys.path:
    kutoka . agiza pyshell
    agiza os
    idledir = os.path.dirname(os.path.abspath(pyshell.__file__))
    ikiwa idledir != os.getcwd():
        # We're haiko kwenye the IDLE directory, help the subprocess find run.py
        pypath = os.environ.get('PYTHONPATH', '')
        ikiwa pypath:
            os.environ['PYTHONPATH'] = pypath + ':' + idledir
        isipokua:
            os.environ['PYTHONPATH'] = idledir
    pyshell.main()
isipokua:
    idlelib.pyshell.main()
