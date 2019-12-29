agiza unittest
kutoka test agiza support
agiza smtplib
agiza socket

ssl = support.import_module("ssl")

support.requires("network")

eleza check_ssl_verifiy(host, port):
    context = ssl.create_default_context()
    with socket.create_connection((host, port)) kama sock:
        jaribu:
            sock = context.wrap_socket(sock, server_hostname=host)
        tatizo Exception:
            rudisha Uongo
        isipokua:
            sock.close()
            rudisha Kweli


kundi SmtpTest(unittest.TestCase):
    testServer = 'smtp.gmail.com'
    remotePort = 587

    eleza test_connect_starttls(self):
        support.get_attribute(smtplib, 'SMTP_SSL')
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        context.check_hostname = Uongo
        context.verify_mode = ssl.CERT_NONE
        with support.transient_internet(self.testServer):
            server = smtplib.SMTP(self.testServer, self.remotePort)
            jaribu:
                server.starttls(context=context)
            tatizo smtplib.SMTPException kama e:
                ikiwa e.args[0] == 'STARTTLS extension sio supported by server.':
                    unittest.skip(e.args[0])
                isipokua:
                    ashiria
            server.ehlo()
            server.quit()


kundi SmtpSSLTest(unittest.TestCase):
    testServer = 'smtp.gmail.com'
    remotePort = 465

    eleza test_connect(self):
        support.get_attribute(smtplib, 'SMTP_SSL')
        with support.transient_internet(self.testServer):
            server = smtplib.SMTP_SSL(self.testServer, self.remotePort)
            server.ehlo()
            server.quit()

    eleza test_connect_default_port(self):
        support.get_attribute(smtplib, 'SMTP_SSL')
        with support.transient_internet(self.testServer):
            server = smtplib.SMTP_SSL(self.testServer)
            server.ehlo()
            server.quit()

    eleza test_connect_using_sslcontext(self):
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        context.check_hostname = Uongo
        context.verify_mode = ssl.CERT_NONE
        support.get_attribute(smtplib, 'SMTP_SSL')
        with support.transient_internet(self.testServer):
            server = smtplib.SMTP_SSL(self.testServer, self.remotePort, context=context)
            server.ehlo()
            server.quit()

    eleza test_connect_using_sslcontext_verified(self):
        with support.transient_internet(self.testServer):
            can_verify = check_ssl_verifiy(self.testServer, self.remotePort)
            ikiwa sio can_verify:
                self.skipTest("SSL certificate can't be verified")

        support.get_attribute(smtplib, 'SMTP_SSL')
        context = ssl.create_default_context()
        with support.transient_internet(self.testServer):
            server = smtplib.SMTP_SSL(self.testServer, self.remotePort, context=context)
            server.ehlo()
            server.quit()


ikiwa __name__ == "__main__":
    unittest.main()
