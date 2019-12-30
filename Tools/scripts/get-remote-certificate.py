#!/usr/bin/env python3
#
# fetch the certificate that the server(s) are providing kwenye PEM form
#
# args are HOST:PORT [, HOST:PORT...]
#
# By Bill Janssen.

agiza re
agiza os
agiza sys
agiza tempfile


eleza fetch_server_certificate (host, port):

    eleza subproc(cmd):
        kutoka subprocess agiza Popen, PIPE, STDOUT
        proc = Popen(cmd, stdout=PIPE, stderr=STDOUT, shell=Kweli)
        status = proc.wait()
        output = proc.stdout.read()
        rudisha status, output

    eleza strip_to_x509_cert(certfile_contents, outfile=Tupu):
        m = re.search(br"^([-]+BEGIN CERTIFICATE[-]+[\r]*\n"
                      br".*[\r]*^[-]+END CERTIFICATE[-]+)$",
                      certfile_contents, re.MULTILINE | re.DOTALL)
        ikiwa sio m:
            rudisha Tupu
        isipokua:
            tn = tempfile.mktemp()
            ukijumuisha open(tn, "wb") kama fp:
                fp.write(m.group(1) + b"\n")
            jaribu:
                tn2 = (outfile ama tempfile.mktemp())
                status, output = subproc(r'openssl x509 -in "%s" -out "%s"' %
                                         (tn, tn2))
                ikiwa status != 0:
                    ashiria RuntimeError('OpenSSL x509 failed ukijumuisha status %s na '
                                       'output: %r' % (status, output))
                ukijumuisha open(tn2, 'rb') kama fp:
                    data = fp.read()
                os.unlink(tn2)
                rudisha data
            mwishowe:
                os.unlink(tn)

    ikiwa sys.platform.startswith("win"):
        tfile = tempfile.mktemp()
        ukijumuisha open(tfile, "w") kama fp:
            fp.write("quit\n")
        jaribu:
            status, output = subproc(
                'openssl s_client -connect "%s:%s" -showcerts < "%s"' %
                (host, port, tfile))
        mwishowe:
            os.unlink(tfile)
    isipokua:
        status, output = subproc(
            'openssl s_client -connect "%s:%s" -showcerts < /dev/null' %
            (host, port))
    ikiwa status != 0:
        ashiria RuntimeError('OpenSSL connect failed ukijumuisha status %s na '
                           'output: %r' % (status, output))
    certtext = strip_to_x509_cert(output)
    ikiwa sio certtext:
        ashiria ValueError("Invalid response received kutoka server at %s:%s" %
                         (host, port))
    rudisha certtext


ikiwa __name__ == "__main__":
    ikiwa len(sys.argv) < 2:
        sys.stderr.write(
            "Usage:  %s HOSTNAME:PORTNUMBER [, HOSTNAME:PORTNUMBER...]\n" %
            sys.argv[0])
        sys.exit(1)
    kila arg kwenye sys.argv[1:]:
        host, port = arg.split(":")
        sys.stdout.buffer.write(fetch_server_certificate(host, int(port)))
    sys.exit(0)
