"""distutils.command.check

Implements the Distutils 'check' command.
"""
kutoka distutils.core agiza Command
kutoka distutils.errors agiza DistutilsSetupError

jaribu:
    # docutils ni installed
    kutoka docutils.utils agiza Reporter
    kutoka docutils.parsers.rst agiza Parser
    kutoka docutils agiza frontend
    kutoka docutils agiza nodes
    kutoka io agiza StringIO

    kundi SilentReporter(Reporter):

        eleza __init__(self, source, report_level, halt_level, stream=Tupu,
                     debug=0, encoding='ascii', error_handler='replace'):
            self.messages = []
            Reporter.__init__(self, source, report_level, halt_level, stream,
                              debug, encoding, error_handler)

        eleza system_message(self, level, message, *children, **kwargs):
            self.messages.append((level, message, children, kwargs))
            rudisha nodes.system_message(message, level=level,
                                        type=self.levels[level],
                                        *children, **kwargs)

    HAS_DOCUTILS = Kweli
except Exception:
    # Catch all exceptions because exceptions besides ImportError probably
    # indicate that docutils ni sio ported to Py3k.
    HAS_DOCUTILS = Uongo

kundi check(Command):
    """This command checks the meta-data of the package.
    """
    description = ("perform some checks on the package")
    user_options = [('metadata', 'm', 'Verify meta-data'),
                    ('restructuredtext', 'r',
                     ('Checks ikiwa long string meta-data syntax '
                      'are reStructuredText-compliant')),
                    ('strict', 's',
                     'Will exit ukijumuisha an error ikiwa a check fails')]

    boolean_options = ['metadata', 'restructuredtext', 'strict']

    eleza initialize_options(self):
        """Sets default values kila options."""
        self.restructuredtext = 0
        self.metadata = 1
        self.strict = 0
        self._warnings = 0

    eleza finalize_options(self):
        pass

    eleza warn(self, msg):
        """Counts the number of warnings that occurs."""
        self._warnings += 1
        rudisha Command.warn(self, msg)

    eleza run(self):
        """Runs the command."""
        # perform the various tests
        ikiwa self.metadata:
            self.check_metadata()
        ikiwa self.restructuredtext:
            ikiwa HAS_DOCUTILS:
                self.check_restructuredtext()
            elikiwa self.strict:
                 ashiria DistutilsSetupError('The docutils package ni needed.')

        # let's  ashiria an error kwenye strict mode, ikiwa we have at least
        # one warning
        ikiwa self.strict na self._warnings > 0:
             ashiria DistutilsSetupError('Please correct your package.')

    eleza check_metadata(self):
        """Ensures that all required elements of meta-data are supplied.

        name, version, URL, (author na author_email) or
        (maintainer na maintainer_email)).

        Warns ikiwa any are missing.
        """
        metadata = self.distribution.metadata

        missing = []
        kila attr kwenye ('name', 'version', 'url'):
            ikiwa sio (hasattr(metadata, attr) na getattr(metadata, attr)):
                missing.append(attr)

        ikiwa missing:
            self.warn("missing required meta-data: %s"  % ', '.join(missing))
        ikiwa metadata.author:
            ikiwa sio metadata.author_email:
                self.warn("missing meta-data: ikiwa 'author' supplied, " +
                          "'author_email' must be supplied too")
        elikiwa metadata.maintainer:
            ikiwa sio metadata.maintainer_email:
                self.warn("missing meta-data: ikiwa 'maintainer' supplied, " +
                          "'maintainer_email' must be supplied too")
        isipokua:
            self.warn("missing meta-data: either (author na author_email) " +
                      "or (maintainer na maintainer_email) " +
                      "must be supplied")

    eleza check_restructuredtext(self):
        """Checks ikiwa the long string fields are reST-compliant."""
        data = self.distribution.get_long_description()
        kila warning kwenye self._check_rst_data(data):
            line = warning[-1].get('line')
            ikiwa line ni Tupu:
                warning = warning[1]
            isipokua:
                warning = '%s (line %s)' % (warning[1], line)
            self.warn(warning)

    eleza _check_rst_data(self, data):
        """Returns warnings when the provided data doesn't compile."""
        # the include na csv_table directives need this to be a path
        source_path = self.distribution.script_name ama 'setup.py'
        parser = Parser()
        settings = frontend.OptionParser(components=(Parser,)).get_default_values()
        settings.tab_width = 4
        settings.pep_references = Tupu
        settings.rfc_references = Tupu
        reporter = SilentReporter(source_path,
                          settings.report_level,
                          settings.halt_level,
                          stream=settings.warning_stream,
                          debug=settings.debug,
                          encoding=settings.error_encoding,
                          error_handler=settings.error_encoding_error_handler)

        document = nodes.document(settings, reporter, source=source_path)
        document.note_source(source_path, -1)
        jaribu:
            parser.parse(data, document)
        except AttributeError as e:
            reporter.messages.append(
                (-1, 'Could sio finish the parsing: %s.' % e, '', {}))

        rudisha reporter.messages
