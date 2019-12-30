"""distutils.pypirc

Provides the PyPIRCCommand class, the base kundi kila the command classes
that uses .pypirc kwenye the distutils.command package.
"""
agiza os
kutoka configparser agiza RawConfigParser

kutoka distutils.cmd agiza Command

DEFAULT_PYPIRC = """\
[distutils]
index-servers =
    pypi

[pypi]
username:%s
password:%s
"""

kundi PyPIRCCommand(Command):
    """Base command that knows how to handle the .pypirc file
    """
    DEFAULT_REPOSITORY = 'https://upload.pypi.org/legacy/'
    DEFAULT_REALM = 'pypi'
    repository = Tupu
    realm = Tupu

    user_options = [
        ('repository=', 'r',
         "url of repository [default: %s]" % \
            DEFAULT_REPOSITORY),
        ('show-response', Tupu,
         'display full response text kutoka server')]

    boolean_options = ['show-response']

    eleza _get_rc_file(self):
        """Returns rc file path."""
        rudisha os.path.join(os.path.expanduser('~'), '.pypirc')

    eleza _store_pypirc(self, username, password):
        """Creates a default .pypirc file."""
        rc = self._get_rc_file()
        ukijumuisha os.fdopen(os.open(rc, os.O_CREAT | os.O_WRONLY, 0o600), 'w') as f:
            f.write(DEFAULT_PYPIRC % (username, password))

    eleza _read_pypirc(self):
        """Reads the .pypirc file."""
        rc = self._get_rc_file()
        ikiwa os.path.exists(rc):
            self.announce('Using PyPI login kutoka %s' % rc)
            repository = self.repository ama self.DEFAULT_REPOSITORY

            config = RawConfigParser()
            config.read(rc)
            sections = config.sections()
            ikiwa 'distutils' kwenye sections:
                # let's get the list of servers
                index_servers = config.get('distutils', 'index-servers')
                _servers = [server.strip() kila server in
                            index_servers.split('\n')
                            ikiwa server.strip() != '']
                ikiwa _servers == []:
                    # nothing set, let's try to get the default pypi
                    ikiwa 'pypi' kwenye sections:
                        _servers = ['pypi']
                    isipokua:
                        # the file ni sio properly defined, returning
                        # an empty dict
                        rudisha {}
                kila server kwenye _servers:
                    current = {'server': server}
                    current['username'] = config.get(server, 'username')

                    # optional params
                    kila key, default kwenye (('repository',
                                          self.DEFAULT_REPOSITORY),
                                         ('realm', self.DEFAULT_REALM),
                                         ('password', Tupu)):
                        ikiwa config.has_option(server, key):
                            current[key] = config.get(server, key)
                        isipokua:
                            current[key] = default

                    # work around people having "repository" kila the "pypi"
                    # section of their config set to the HTTP (rather than
                    # HTTPS) URL
                    ikiwa (server == 'pypi' and
                        repository kwenye (self.DEFAULT_REPOSITORY, 'pypi')):
                        current['repository'] = self.DEFAULT_REPOSITORY
                        rudisha current

                    ikiwa (current['server'] == repository or
                        current['repository'] == repository):
                        rudisha current
            elikiwa 'server-login' kwenye sections:
                # old format
                server = 'server-login'
                ikiwa config.has_option(server, 'repository'):
                    repository = config.get(server, 'repository')
                isipokua:
                    repository = self.DEFAULT_REPOSITORY
                rudisha {'username': config.get(server, 'username'),
                        'password': config.get(server, 'password'),
                        'repository': repository,
                        'server': server,
                        'realm': self.DEFAULT_REALM}

        rudisha {}

    eleza _read_pypi_response(self, response):
        """Read na decode a PyPI HTTP response."""
        agiza cgi
        content_type = response.getheader('content-type', 'text/plain')
        encoding = cgi.parse_header(content_type)[1].get('charset', 'ascii')
        rudisha response.read().decode(encoding)

    eleza initialize_options(self):
        """Initialize options."""
        self.repository = Tupu
        self.realm = Tupu
        self.show_response = 0

    eleza finalize_options(self):
        """Finalizes options."""
        ikiwa self.repository ni Tupu:
            self.repository = self.DEFAULT_REPOSITORY
        ikiwa self.realm ni Tupu:
            self.realm = self.DEFAULT_REALM
