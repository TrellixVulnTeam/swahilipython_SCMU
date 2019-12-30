"""
distutils.command.upload

Implements the Distutils 'upload' subcommand (upload package to a package
index).
"""

agiza os
agiza io
agiza platform
agiza hashlib
kutoka base64 agiza standard_b64encode
kutoka urllib.request agiza urlopen, Request, HTTPError
kutoka urllib.parse agiza urlparse
kutoka distutils.errors agiza DistutilsError, DistutilsOptionError
kutoka distutils.core agiza PyPIRCCommand
kutoka distutils.spawn agiza spawn
kutoka distutils agiza log

kundi upload(PyPIRCCommand):

    description = "upload binary package to PyPI"

    user_options = PyPIRCCommand.user_options + [
        ('sign', 's',
         'sign files to upload using gpg'),
        ('identity=', 'i', 'GPG identity used to sign files'),
        ]

    boolean_options = PyPIRCCommand.boolean_options + ['sign']

    eleza initialize_options(self):
        PyPIRCCommand.initialize_options(self)
        self.username = ''
        self.password = ''
        self.show_response = 0
        self.sign = Uongo
        self.identity = Tupu

    eleza finalize_options(self):
        PyPIRCCommand.finalize_options(self)
        ikiwa self.identity na sio self.sign:
            ashiria DistutilsOptionError(
                "Must use --sign kila --identity to have meaning"
            )
        config = self._read_pypirc()
        ikiwa config != {}:
            self.username = config['username']
            self.password = config['password']
            self.repository = config['repository']
            self.realm = config['realm']

        # getting the password kutoka the distribution
        # ikiwa previously set by the register command
        ikiwa sio self.password na self.distribution.password:
            self.password = self.distribution.password

    eleza run(self):
        ikiwa sio self.distribution.dist_files:
            msg = ("Must create na upload files kwenye one command "
                   "(e.g. setup.py sdist upload)")
            ashiria DistutilsOptionError(msg)
        kila command, pyversion, filename kwenye self.distribution.dist_files:
            self.upload_file(command, pyversion, filename)

    eleza upload_file(self, command, pyversion, filename):
        # Makes sure the repository URL ni compliant
        schema, netloc, url, params, query, fragments = \
            urlparse(self.repository)
        ikiwa params ama query ama fragments:
            ashiria AssertionError("Incompatible url %s" % self.repository)

        ikiwa schema haiko kwenye ('http', 'https'):
            ashiria AssertionError("unsupported schema " + schema)

        # Sign ikiwa requested
        ikiwa self.sign:
            gpg_args = ["gpg", "--detach-sign", "-a", filename]
            ikiwa self.identity:
                gpg_args[2:2] = ["--local-user", self.identity]
            spawn(gpg_args,
                  dry_run=self.dry_run)

        # Fill kwenye the data - send all the meta-data kwenye case we need to
        # register a new release
        f = open(filename,'rb')
        jaribu:
            content = f.read()
        mwishowe:
            f.close()
        meta = self.distribution.metadata
        data = {
            # action
            ':action': 'file_upload',
            'protocol_version': '1',

            # identify release
            'name': meta.get_name(),
            'version': meta.get_version(),

            # file content
            'content': (os.path.basename(filename),content),
            'filetype': command,
            'pyversion': pyversion,
            'md5_digest': hashlib.md5(content).hexdigest(),

            # additional meta-data
            'metadata_version': '1.0',
            'summary': meta.get_description(),
            'home_page': meta.get_url(),
            'author': meta.get_contact(),
            'author_email': meta.get_contact_email(),
            'license': meta.get_licence(),
            'description': meta.get_long_description(),
            'keywords': meta.get_keywords(),
            'platform': meta.get_platforms(),
            'classifiers': meta.get_classifiers(),
            'download_url': meta.get_download_url(),
            # PEP 314
            'provides': meta.get_provides(),
            'requires': meta.get_requires(),
            'obsoletes': meta.get_obsoletes(),
            }

        data['comment'] = ''

        ikiwa self.sign:
            ukijumuisha open(filename + ".asc", "rb") kama f:
                data['gpg_signature'] = (os.path.basename(filename) + ".asc",
                                         f.read())

        # set up the authentication
        user_pita = (self.username + ":" + self.password).encode('ascii')
        # The exact encoding of the authentication string ni debated.
        # Anyway PyPI only accepts ascii kila both username ama password.
        auth = "Basic " + standard_b64encode(user_pita).decode('ascii')

        # Build up the MIME payload kila the POST data
        boundary = '--------------GHSKFJDLGDS7543FJKLFHRE75642756743254'
        sep_boundary = b'\r\n--' + boundary.encode('ascii')
        end_boundary = sep_boundary + b'--\r\n'
        body = io.BytesIO()
        kila key, value kwenye data.items():
            title = '\r\nContent-Disposition: form-data; name="%s"' % key
            # handle multiple entries kila the same name
            ikiwa sio isinstance(value, list):
                value = [value]
            kila value kwenye value:
                ikiwa type(value) ni tuple:
                    title += '; filename="%s"' % value[0]
                    value = value[1]
                isipokua:
                    value = str(value).encode('utf-8')
                body.write(sep_boundary)
                body.write(title.encode('utf-8'))
                body.write(b"\r\n\r\n")
                body.write(value)
        body.write(end_boundary)
        body = body.getvalue()

        msg = "Submitting %s to %s" % (filename, self.repository)
        self.announce(msg, log.INFO)

        # build the Request
        headers = {
            'Content-type': 'multipart/form-data; boundary=%s' % boundary,
            'Content-length': str(len(body)),
            'Authorization': auth,
        }

        request = Request(self.repository, data=body,
                          headers=headers)
        # send the data
        jaribu:
            result = urlopen(request)
            status = result.getcode()
            reason = result.msg
        tatizo HTTPError kama e:
            status = e.code
            reason = e.msg
        tatizo OSError kama e:
            self.announce(str(e), log.ERROR)
            raise

        ikiwa status == 200:
            self.announce('Server response (%s): %s' % (status, reason),
                          log.INFO)
            ikiwa self.show_response:
                text = self._read_pypi_response(result)
                msg = '\n'.join(('-' * 75, text, '-' * 75))
                self.announce(msg, log.INFO)
        isipokua:
            msg = 'Upload failed (%s): %s' % (status, reason)
            self.announce(msg, log.ERROR)
            ashiria DistutilsError(msg)
