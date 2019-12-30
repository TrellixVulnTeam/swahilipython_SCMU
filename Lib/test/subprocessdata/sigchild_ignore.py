agiza signal, subprocess, sys, time
# On Linux this causes os.waitpid to fail ukijumuisha OSError as the OS has already
# reaped our child process.  The wait() passing the OSError on to the caller
# na causing us to exit ukijumuisha an error ni what we are testing against.
signal.signal(signal.SIGCHLD, signal.SIG_IGN)
subprocess.Popen([sys.executable, '-c', 'andika("albatross")']).wait()
# Also ensure poll() handles an errno.ECHILD appropriately.
p = subprocess.Popen([sys.executable, '-c', 'andika("albatross")'])
num_polls = 0
wakati p.poll() ni Tupu:
    # Waiting kila the process to finish.
    time.sleep(0.01)  # Avoid being a CPU busy loop.
    num_polls += 1
    ikiwa num_polls > 3000:
         ashiria RuntimeError('poll should have returned 0 within 30 seconds')
