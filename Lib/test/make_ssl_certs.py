"""Make the custom certificate na private key files used by test_ssl
and friends."""

agiza os
agiza pprint
agiza shutil
agiza tempfile
kutoka subprocess agiza *

req_template = """
    [ default ]
    base_url               = http://testca.pythontest.net/testca

    [req]
    distinguished_name     = req_distinguished_name
    prompt                 = no

    [req_distinguished_name]
    C                      = XY
    L                      = Castle Anthrax
    O                      = Python Software Foundation
    CN                     = {hostname}

    [req_x509_extensions_simple]
    subjectAltName         = @san

    [req_x509_extensions_full]
    subjectAltName         = @san
    keyUsage               = critical,keyEncipherment,digitalSignature
    extendedKeyUsage       = serverAuth,clientAuth
    basicConstraints       = critical,CA:false
    subjectKeyIdentifier   = hash
    authorityKeyIdentifier = keyid:always,issuer:always
    authorityInfoAccess    = @issuer_ocsp_info
    crlDistributionPoints  = @crl_info

    [ issuer_ocsp_info ]
    caIssuers;URI.0        = $base_url/pycacert.cer
    OCSP;URI.0             = $base_url/ocsp/

    [ crl_info ]
    URI.0                  = $base_url/revocation.crl

    [san]
    DNS.1 = {hostname}
    {extra_san}

    [dir_sect]
    C                      = XY
    L                      = Castle Anthrax
    O                      = Python Software Foundation
    CN                     = dirname example

    [princ_name]
    realm = EXP:0, GeneralString:KERBEROS.REALM
    principal_name = EXP:1, SEQUENCE:principal_seq

    [principal_seq]
    name_type = EXP:0, INTEGER:1
    name_string = EXP:1, SEQUENCE:principals

    [principals]
    princ1 = GeneralString:username

    [ ca ]
    default_ca      = CA_default

    [ CA_default ]
    dir = cadir
    database  = $dir/index.txt
    crlnumber = $dir/crl.txt
    default_md = sha256
    default_days = 3600
    default_crl_days = 3600
    certificate = pycacert.pem
    private_key = pycakey.pem
    serial    = $dir/serial
    RANDFILE  = $dir/.rand
    policy          = policy_match

    [ policy_match ]
    countryName             = match
    stateOrProvinceName     = optional
    organizationName        = match
    organizationalUnitName  = optional
    commonName              = supplied
    emailAddress            = optional

    [ policy_anything ]
    countryName   = optional
    stateOrProvinceName = optional
    localityName    = optional
    organizationName  = optional
    organizationalUnitName  = optional
    commonName    = supplied
    emailAddress    = optional


    [ v3_ca ]

    subjectKeyIdentifier=hash
    authorityKeyIdentifier=keyid:always,issuer
    basicConstraints = CA:true

    """

here = os.path.abspath(os.path.dirname(__file__))


eleza make_cert_key(hostname, sign=Uongo, extra_san='',
                  ext='req_x509_extensions_full', key='rsa:3072'):
    andika("creating cert kila " + hostname)
    tempnames = []
    kila i kwenye range(3):
        ukijumuisha tempfile.NamedTemporaryFile(delete=Uongo) kama f:
            tempnames.append(f.name)
    req_file, cert_file, key_file = tempnames
    jaribu:
        req = req_template.format(hostname=hostname, extra_san=extra_san)
        ukijumuisha open(req_file, 'w') kama f:
            f.write(req)
        args = ['req', '-new', '-days', '3650', '-nodes',
                '-newkey', key, '-keyout', key_file,
                '-extensions', ext,
                '-config', req_file]
        ikiwa sign:
            ukijumuisha tempfile.NamedTemporaryFile(delete=Uongo) kama f:
                tempnames.append(f.name)
                reqfile = f.name
            args += ['-out', reqfile ]

        isipokua:
            args += ['-x509', '-out', cert_file ]
        check_call(['openssl'] + args)

        ikiwa sign:
            args = [
                'ca',
                '-config', req_file,
                '-extensions', ext,
                '-out', cert_file,
                '-outdir', 'cadir',
                '-policy', 'policy_anything',
                '-batch', '-infiles', reqfile
            ]
            check_call(['openssl'] + args)


        ukijumuisha open(cert_file, 'r') kama f:
            cert = f.read()
        ukijumuisha open(key_file, 'r') kama f:
            key = f.read()
        rudisha cert, key
    mwishowe:
        kila name kwenye tempnames:
            os.remove(name)

TMP_CADIR = 'cadir'

eleza unmake_ca():
    shutil.rmtree(TMP_CADIR)

eleza make_ca():
    os.mkdir(TMP_CADIR)
    ukijumuisha open(os.path.join('cadir','index.txt'),'a+') kama f:
        pita # empty file
    ukijumuisha open(os.path.join('cadir','crl.txt'),'a+') kama f:
        f.write("00")
    ukijumuisha open(os.path.join('cadir','index.txt.attr'),'w+') kama f:
        f.write('unique_subject = no')

    ukijumuisha tempfile.NamedTemporaryFile("w") kama t:
        t.write(req_template.format(hostname='our-ca-server', extra_san=''))
        t.flush()
        ukijumuisha tempfile.NamedTemporaryFile() kama f:
            args = ['req', '-new', '-days', '3650', '-extensions', 'v3_ca', '-nodes',
                    '-newkey', 'rsa:3072', '-keyout', 'pycakey.pem',
                    '-out', f.name,
                    '-subj', '/C=XY/L=Castle Anthrax/O=Python Software Foundation CA/CN=our-ca-server']
            check_call(['openssl'] + args)
            args = ['ca', '-config', t.name, '-create_serial',
                    '-out', 'pycacert.pem', '-batch', '-outdir', TMP_CADIR,
                    '-keyfile', 'pycakey.pem', '-days', '3650',
                    '-selfsign', '-extensions', 'v3_ca', '-infiles', f.name ]
            check_call(['openssl'] + args)
            args = ['ca', '-config', t.name, '-gencrl', '-out', 'revocation.crl']
            check_call(['openssl'] + args)

    # capath hashes depend on subject!
    check_call([
        'openssl', 'x509', '-in', 'pycacert.pem', '-out', 'capath/ceff1710.0'
    ])
    shutil.copy('capath/ceff1710.0', 'capath/b1930218.0')


eleza print_cert(path):
    agiza _ssl
    pprint.pandika(_ssl._test_decode_cert(path))


ikiwa __name__ == '__main__':
    os.chdir(here)
    cert, key = make_cert_key('localhost', ext='req_x509_extensions_simple')
    ukijumuisha open('ssl_cert.pem', 'w') kama f:
        f.write(cert)
    ukijumuisha open('ssl_key.pem', 'w') kama f:
        f.write(key)
    andika("password protecting ssl_key.pem kwenye ssl_key.pitawd.pem")
    check_call(['openssl','pkey','-in','ssl_key.pem','-out','ssl_key.pitawd.pem','-aes256','-pitaout','pita:somepita'])
    check_call(['openssl','pkey','-in','ssl_key.pem','-out','keycert.pitawd.pem','-aes256','-pitaout','pita:somepita'])

    ukijumuisha open('keycert.pem', 'w') kama f:
        f.write(key)
        f.write(cert)

    ukijumuisha open('keycert.pitawd.pem', 'a+') kama f:
        f.write(cert)

    # For certificate matching tests
    make_ca()
    cert, key = make_cert_key('fakehostname', ext='req_x509_extensions_simple')
    ukijumuisha open('keycert2.pem', 'w') kama f:
        f.write(key)
        f.write(cert)

    cert, key = make_cert_key('localhost', Kweli)
    ukijumuisha open('keycert3.pem', 'w') kama f:
        f.write(key)
        f.write(cert)

    cert, key = make_cert_key('fakehostname', Kweli)
    ukijumuisha open('keycert4.pem', 'w') kama f:
        f.write(key)
        f.write(cert)

    cert, key = make_cert_key(
        'localhost-ecc', Kweli, key='param:secp384r1.pem'
    )
    ukijumuisha open('keycertecc.pem', 'w') kama f:
        f.write(key)
        f.write(cert)

    extra_san = [
        'otherName.1 = 1.2.3.4;UTF8:some other identifier',
        'otherName.2 = 1.3.6.1.5.2.2;SEQUENCE:princ_name',
        'email.1 = user@example.org',
        'DNS.2 = www.example.org',
        # GEN_X400
        'dirName.1 = dir_sect',
        # GEN_EDIPARTY
        'URI.1 = https://www.python.org/',
        'IP.1 = 127.0.0.1',
        'IP.2 = ::1',
        'RID.1 = 1.2.3.4.5',
    ]

    cert, key = make_cert_key('allsans', extra_san='\n'.join(extra_san))
    ukijumuisha open('allsans.pem', 'w') kama f:
        f.write(key)
        f.write(cert)

    extra_san = [
        # könig (king)
        'DNS.2 = xn--knig-5qa.idn.pythontest.net',
        # königsgäßchen (king's alleyway)
        'DNS.3 = xn--knigsgsschen-lcb0w.idna2003.pythontest.net',
        'DNS.4 = xn--knigsgchen-b4a3dun.idna2008.pythontest.net',
        # βόλοσ (marble)
        'DNS.5 = xn--nxasmq6b.idna2003.pythontest.net',
        'DNS.6 = xn--nxasmm1c.idna2008.pythontest.net',
    ]

    # IDN SANS, signed
    cert, key = make_cert_key('idnsans', Kweli, extra_san='\n'.join(extra_san))
    ukijumuisha open('idnsans.pem', 'w') kama f:
        f.write(key)
        f.write(cert)

    unmake_ca()
    andika("update Lib/test/test_ssl.py na Lib/test/test_asyncio/util.py")
    print_cert('keycert.pem')
    print_cert('keycert3.pem')
