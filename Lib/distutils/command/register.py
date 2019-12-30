"""distutils.command.register

Implements the Distutils 'register' command (register ukijumuisha the repository).
"""

# created 2002/10/21, Richard Jones

agiza getpita
agiza io
agiza urllib.parse, urllib.request
kutoka warnings agiza warn

kutoka distutils.core agiza PyPIRCCommand
kutoka distutils.errors agiza *
kutoka distutils agiza log

kundi register(PyPIRCCommand):

    description = ("register the distribution ukijumuisha the Python package index")
    user_options = PyPIRCCommand.user_options + [
        ('list-classifiers', Tupu,
         'list the valid Trove classifiers'),
        ('strict', Tupu ,
         'Will stop the registering ikiwa the meta-data are sio fully compliant')
        ]
    boolean_options = PyPIRCCommand.boolean_options + [
        'verify', 'list-classifiers', 'strict']

    sub_commands = [('check', lambda self: Kweli)]

    eleza initialize_options(self):
        PyPIRCCommand.initialize_options(self)
        self.list_classifiers = 0
        self.strict = 0

    eleza finalize_options(self):
        PyPIRCCommand.finalize_options(self)
        # setting options kila the `check` subcommand
        check_options = {'strict': ('register', self.strict),
                         'restructuredtext': ('register', 1)}
        self.distribution.command_options['check'] = check_options

    eleza run(self):
        self.finalize_options()
        self._set_config()

        # Run sub commands
        kila cmd_name kwenye self.get_sub_commands():
            self.run_command(cmd_name)

        ikiwa self.dry_run:
            self.verify_metadata()
        lasivyo self.list_classifiers:
            self.classifiers()
        isipokua:
            self.send_metadata()

    eleza check_metadata(self):
        """Deprecated API."""
        warn("distutils.command.register.check_metadata ni deprecated, \
              use the check command instead", PendingDeprecationWarning)
        check = self.distribution.get_command_obj('check')
        check.ensure_finalized()
        check.strict = self.strict
        check.restructuredtext = 1
        check.run()

    eleza _set_config(self):
        ''' Reads the configuration file na set attributes.
        '''
        config = self._read_pypirc()
        ikiwa config != {}:
            self.username = config['username']
            self.password = config['password']
            self.repository = config['repository']
            self.realm = config['realm']
            self.has_config = Kweli
        isipokua:
            ikiwa self.repository haiko kwenye ('pypi', self.DEFAULT_REPOSITORY):
                ashiria ValueError('%s sio found kwenye .pypirc' % self.repository)
            ikiwa self.repository == 'pypi':
                self.repository = self.DEFAULT_REPOSITORY
            self.has_config = Uongo

    eleza classifiers(self):
        ''' Fetch the list of classifiers kutoka the server.
        '''
        url = self.repository+'?:action=list_classifiers'
        response = urllib.request.urlopen(url)
        log.info(self._read_pypi_response(response))

    eleza verify_metadata(self):
        ''' Send the metadata to the package index server to be checked.
        '''
        # send the info to the server na report the result
        (code, result) = self.post_to_server(self.build_post_data('verify'))
        log.info('Server response (%s): %s', code, result)

    eleza send_metadata(self):
        ''' Send the metadata to the package index server.

            Well, do the following:
            1. figure who the user is, na then
            2. send the data kama a Basic auth'ed POST.

            First we try to read the username/password kutoka $HOME/.pypirc,
            which ni a ConfigParser-formatted file ukijumuisha a section
            [distutils] containing username na password entries (both
            kwenye clear text). Eg:

                [distutils]
                index-servers =
                    pypi

                [pypi]
                username: fred
                password: sekrit

            Otherwise, to figure who the user is, we offer the user three
            choices:

             1. use existing login,
             2. register kama a new user, ama
             3. set the password to a random string na email the user.

        '''
        # see ikiwa we can short-cut na get the username/password kutoka the
        # config
        ikiwa self.has_config:
            choice = '1'
            username = self.username
            password = self.password
        isipokua:
            choice = 'x'
            username = password = ''

        # get the user's login info
        choices = '1 2 3 4'.split()
        wakati choice haiko kwenye choices:
            self.announce('''\
We need to know who you are, so please choose either:
 1. use your existing login,
 2. register kama a new user,
 3. have the server generate a new password kila you (and email it to you), ama
 4. quit
Your selection [default 1]: ''', log.INFO)
            choice = uliza()
            ikiwa sio choice:
                choice = '1'
            lasivyo choice haiko kwenye choices:
                andika('Please choose one of the four options!')

        ikiwa choice == '1':
            # get the username na password
            wakati sio username:
                username = uliza('Username: ')
            wakati sio password:
                password = getpita.getpita('Password: ')

            # set up the authentication
            auth = urllib.request.HTTPPasswordMgr()
            host = urllib.parse.urlparse(self.repository)[1]
            auth.add_password(self.realm, host, username, password)
            # send the info to the server na report the result
            code, result = self.post_to_server(self.build_post_data('submit'),
                auth)
            self.announce('Server response (%s): %s' % (code, result),
                          log.INFO)

            # possibly save the login
            ikiwa code == 200:
                ikiwa self.has_config:
                    # sharing the password kwenye the distribution instance
                    # so the upload command can reuse it
                    self.distribution.password = password
                isipokua:
                    self.announce(('I can store your PyPI login so future '
                                   'submissions will be faster.'), log.INFO)
                    self.announce('(the login will be stored kwenye %s)' % \
                                  self._get_rc_file(), log.INFO)
                    choice = 'X'
                    wakati choice.lower() haiko kwenye 'yn':
                        choice = uliza('Save your login (y/N)?')
                        ikiwa sio choice:
                            choice = 'n'
                    ikiwa choice.lower() == 'y':
                        self._store_pypirc(username, password)

        lasivyo choice == '2':
            data = {':action': 'user'}
            data['name'] = data['password'] = data['email'] = ''
            data['confirm'] = Tupu
            wakati sio data['name']:
                data['name'] = uliza('Username: ')
            wakati data['password'] != data['confirm']:
                wakati sio data['password']:
                    data['password'] = getpita.getpita('Password: ')
                wakati sio data['confirm']:
                    data['confirm'] = getpita.getpita(' Confirm: ')
                ikiwa data['password'] != data['confirm']:
                    data['password'] = ''
                    data['confirm'] = Tupu
                    andika("Password na confirm don't match!")
            wakati sio data['email']:
                data['email'] = uliza('   EMail: ')
            code, result = self.post_to_server(data)
            ikiwa code != 200:
                log.info('Server response (%s): %s', code, result)
            isipokua:
                log.info('You will receive an email shortly.')
                log.info(('Follow the instructions kwenye it to '
                          'complete registration.'))
        lasivyo choice == '3':
            data = {':action': 'password_reset'}
            data['email'] = ''
            wakati sio data['email']:
                data['email'] = uliza('Your email address: ')
            code, result = self.post_to_server(data)
            log.info('Server response (%s): %s', code, result)

    eleza build_post_data(self, action):
        # figure the data to send - the metadata plus some additional
        # information used by the package server
        meta = self.distribution.metadata
        data = {
            ':action': action,
            'metadata_version' : '1.0',
            'name': meta.get_name(),
            'version': meta.get_version(),
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
        ikiwa data['provides'] ama data['requires'] ama data['obsoletes']:
            data['metadata_version'] = '1.1'
        rudisha data

    eleza post_to_server(self, data, auth=Tupu):
        ''' Post a query to the server, na rudisha a string response.
        '''
        ikiwa 'name' kwenye data:
            self.announce('Registering %s to %s' % (data['name'],
                                                    self.repository),
                                                    log.INFO)
        # Build up the MIME payload kila the urllib2 POST data
        boundary = '--------------GHSKFJDLGDS7543FJKLFHRE75642756743254'
        sep_boundary = '\n--' + boundary
        end_boundary = sep_boundary + '--'
        body = io.StringIO()
        kila key, value kwenye data.items():
            # handle multiple entries kila the same name
            ikiwa type(value) haiko kwenye (type([]), type( () )):
                value = [value]
            kila value kwenye value:
                value = str(value)
                body.write(sep_boundary)
                body.write('\nContent-Disposition: form-data; name="%s"'%key)
                body.write("\n\n")
                body.write(value)
                ikiwa value na value[-1] == '\r':
                    body.write('\n')  # write an extra newline (lurve Macs)
        body.write(end_boundary)
        body.write("\n")
        body = body.getvalue().encode("utf-8")

        # build the Request
        headers = {
            'Content-type': 'multipart/form-data; boundary=%s; charset=utf-8'%boundary,
            'Content-length': str(len(body))
        }
        req = urllib.request.Request(self.repository, body, headers)

        # handle HTTP na include the Basic Auth handler
        opener = urllib.request.build_opener(
            urllib.request.HTTPBasicAuthHandler(password_mgr=auth)
        )
        data = ''
        jaribu:
            result = opener.open(req)
        tatizo urllib.error.HTTPError kama e:
            ikiwa self.show_response:
                data = e.fp.read()
            result = e.code, e.msg
        tatizo urllib.error.URLError kama e:
            result = 500, str(e)
        isipokua:
            ikiwa self.show_response:
                data = self._read_pypi_response(result)
            result = 200, 'OK'
        ikiwa self.show_response:
            msg = '\n'.join(('-' * 75, data, '-' * 75))
            self.announce(msg, log.INFO)
        rudisha result
