"""More comprehensive traceback formatting kila Python scripts.

To enable this module, do:

    agiza cgitb; cgitb.enable()

at the top of your script.  The optional arguments to enable() are:

    display     - ikiwa true, tracebacks are displayed kwenye the web browser
    logdir      - ikiwa set, tracebacks are written to files kwenye this directory
    context     - number of lines of source code to show kila each stack frame
    format      - 'text' ama 'html' controls the output format

By default, tracebacks are displayed but sio saved, the context ni 5 lines
and the output format ni 'html' (kila backwards compatibility with the
original use of this module)

Alternatively, ikiwa you have caught an exception na want cgitb to display it
kila you, call cgitb.handler().  The optional argument to handler() ni a
3-item tuple (etype, evalue, etb) just like the value of sys.exc_info().
The default handler displays output kama HTML.

"""
agiza inspect
agiza keyword
agiza linecache
agiza os
agiza pydoc
agiza sys
agiza tempfile
agiza time
agiza tokenize
agiza traceback

eleza reset():
    """Return a string that resets the CGI na browser to a known state."""
    rudisha '''<!--: spam
Content-Type: text/html

<body bgcolor="#f0f0f8"><font color="#f0f0f8" size="-5"> -->
<body bgcolor="#f0f0f8"><font color="#f0f0f8" size="-5"> --> -->
</font> </font> </font> </script> </object> </blockquote> </pre>
</table> </table> </table> </table> </table> </font> </font> </font>'''

__UNDEF__ = []                          # a special sentinel object
eleza small(text):
    ikiwa text:
        rudisha '<small>' + text + '</small>'
    isipokua:
        rudisha ''

eleza strong(text):
    ikiwa text:
        rudisha '<strong>' + text + '</strong>'
    isipokua:
        rudisha ''

eleza grey(text):
    ikiwa text:
        rudisha '<font color="#909090">' + text + '</font>'
    isipokua:
        rudisha ''

eleza lookup(name, frame, locals):
    """Find the value kila a given name kwenye the given environment."""
    ikiwa name kwenye locals:
        rudisha 'local', locals[name]
    ikiwa name kwenye frame.f_globals:
        rudisha 'global', frame.f_globals[name]
    ikiwa '__builtins__' kwenye frame.f_globals:
        builtins = frame.f_globals['__builtins__']
        ikiwa type(builtins) ni type({}):
            ikiwa name kwenye builtins:
                rudisha 'builtin', builtins[name]
        isipokua:
            ikiwa hasattr(builtins, name):
                rudisha 'builtin', getattr(builtins, name)
    rudisha Tupu, __UNDEF__

eleza scanvars(reader, frame, locals):
    """Scan one logical line of Python na look up values of variables used."""
    vars, lasttoken, parent, prefix, value = [], Tupu, Tupu, '', __UNDEF__
    kila ttype, token, start, end, line kwenye tokenize.generate_tokens(reader):
        ikiwa ttype == tokenize.NEWLINE: koma
        ikiwa ttype == tokenize.NAME na token haiko kwenye keyword.kwlist:
            ikiwa lasttoken == '.':
                ikiwa parent ni sio __UNDEF__:
                    value = getattr(parent, token, __UNDEF__)
                    vars.append((prefix + token, prefix, value))
            isipokua:
                where, value = lookup(token, frame, locals)
                vars.append((token, where, value))
        elikiwa token == '.':
            prefix += lasttoken + '.'
            parent = value
        isipokua:
            parent, prefix = Tupu, ''
        lasttoken = token
    rudisha vars

eleza html(einfo, context=5):
    """Return a nice HTML document describing a given traceback."""
    etype, evalue, etb = einfo
    ikiwa isinstance(etype, type):
        etype = etype.__name__
    pyver = 'Python ' + sys.version.split()[0] + ': ' + sys.executable
    date = time.ctime(time.time())
    head = '<body bgcolor="#f0f0f8">' + pydoc.html.heading(
        '<big><big>%s</big></big>' %
        strong(pydoc.html.escape(str(etype))),
        '#ffffff', '#6622aa', pyver + '<br>' + date) + '''
<p>A problem occurred kwenye a Python script.  Here ni the sequence of
function calls leading up to the error, kwenye the order they occurred.</p>'''

    indent = '<tt>' + small('&nbsp;' * 5) + '&nbsp;</tt>'
    frames = []
    records = inspect.getinnerframes(etb, context)
    kila frame, file, lnum, func, lines, index kwenye records:
        ikiwa file:
            file = os.path.abspath(file)
            link = '<a href="file://%s">%s</a>' % (file, pydoc.html.escape(file))
        isipokua:
            file = link = '?'
        args, varargs, varkw, locals = inspect.getargvalues(frame)
        call = ''
        ikiwa func != '?':
            call = 'in ' + strong(pydoc.html.escape(func))
            ikiwa func != "<module>":
                call += inspect.formatargvalues(args, varargs, varkw, locals,
                    formatvalue=lambda value: '=' + pydoc.html.repr(value))

        highlight = {}
        eleza reader(lnum=[lnum]):
            highlight[lnum[0]] = 1
            jaribu: rudisha linecache.getline(file, lnum[0])
            mwishowe: lnum[0] += 1
        vars = scanvars(reader, frame, locals)

        rows = ['<tr><td bgcolor="#d8bbff">%s%s %s</td></tr>' %
                ('<big>&nbsp;</big>', link, call)]
        ikiwa index ni sio Tupu:
            i = lnum - index
            kila line kwenye lines:
                num = small('&nbsp;' * (5-len(str(i))) + str(i)) + '&nbsp;'
                ikiwa i kwenye highlight:
                    line = '<tt>=&gt;%s%s</tt>' % (num, pydoc.html.preformat(line))
                    rows.append('<tr><td bgcolor="#ffccee">%s</td></tr>' % line)
                isipokua:
                    line = '<tt>&nbsp;&nbsp;%s%s</tt>' % (num, pydoc.html.preformat(line))
                    rows.append('<tr><td>%s</td></tr>' % grey(line))
                i += 1

        done, dump = {}, []
        kila name, where, value kwenye vars:
            ikiwa name kwenye done: endelea
            done[name] = 1
            ikiwa value ni sio __UNDEF__:
                ikiwa where kwenye ('global', 'builtin'):
                    name = ('<em>%s</em> ' % where) + strong(name)
                elikiwa where == 'local':
                    name = strong(name)
                isipokua:
                    name = where + strong(name.split('.')[-1])
                dump.append('%s&nbsp;= %s' % (name, pydoc.html.repr(value)))
            isipokua:
                dump.append(name + ' <em>undefined</em>')

        rows.append('<tr><td>%s</td></tr>' % small(grey(', '.join(dump))))
        frames.append('''
<table width="100%%" cellspacing=0 cellpadding=0 border=0>
%s</table>''' % '\n'.join(rows))

    exception = ['<p>%s: %s' % (strong(pydoc.html.escape(str(etype))),
                                pydoc.html.escape(str(evalue)))]
    kila name kwenye dir(evalue):
        ikiwa name[:1] == '_': endelea
        value = pydoc.html.repr(getattr(evalue, name))
        exception.append('\n<br>%s%s&nbsp;=\n%s' % (indent, name, value))

    rudisha head + ''.join(frames) + ''.join(exception) + '''


<!-- The above ni a description of an error kwenye a Python program, formatted
     kila a Web browser because the 'cgitb' module was enabled.  In case you
     are sio reading this kwenye a Web browser, here ni the original traceback:

%s
-->
''' % pydoc.html.escape(
          ''.join(traceback.format_exception(etype, evalue, etb)))

eleza text(einfo, context=5):
    """Return a plain text document describing a given traceback."""
    etype, evalue, etb = einfo
    ikiwa isinstance(etype, type):
        etype = etype.__name__
    pyver = 'Python ' + sys.version.split()[0] + ': ' + sys.executable
    date = time.ctime(time.time())
    head = "%s\n%s\n%s\n" % (str(etype), pyver, date) + '''
A problem occurred kwenye a Python script.  Here ni the sequence of
function calls leading up to the error, kwenye the order they occurred.
'''

    frames = []
    records = inspect.getinnerframes(etb, context)
    kila frame, file, lnum, func, lines, index kwenye records:
        file = file na os.path.abspath(file) ama '?'
        args, varargs, varkw, locals = inspect.getargvalues(frame)
        call = ''
        ikiwa func != '?':
            call = 'in ' + func
            ikiwa func != "<module>":
                call += inspect.formatargvalues(args, varargs, varkw, locals,
                    formatvalue=lambda value: '=' + pydoc.text.repr(value))

        highlight = {}
        eleza reader(lnum=[lnum]):
            highlight[lnum[0]] = 1
            jaribu: rudisha linecache.getline(file, lnum[0])
            mwishowe: lnum[0] += 1
        vars = scanvars(reader, frame, locals)

        rows = [' %s %s' % (file, call)]
        ikiwa index ni sio Tupu:
            i = lnum - index
            kila line kwenye lines:
                num = '%5d ' % i
                rows.append(num+line.rstrip())
                i += 1

        done, dump = {}, []
        kila name, where, value kwenye vars:
            ikiwa name kwenye done: endelea
            done[name] = 1
            ikiwa value ni sio __UNDEF__:
                ikiwa where == 'global': name = 'global ' + name
                elikiwa where != 'local': name = where + name.split('.')[-1]
                dump.append('%s = %s' % (name, pydoc.text.repr(value)))
            isipokua:
                dump.append(name + ' undefined')

        rows.append('\n'.join(dump))
        frames.append('\n%s\n' % '\n'.join(rows))

    exception = ['%s: %s' % (str(etype), str(evalue))]
    kila name kwenye dir(evalue):
        value = pydoc.text.repr(getattr(evalue, name))
        exception.append('\n%s%s = %s' % (" "*4, name, value))

    rudisha head + ''.join(frames) + ''.join(exception) + '''

The above ni a description of an error kwenye a Python program.  Here is
the original traceback:

%s
''' % ''.join(traceback.format_exception(etype, evalue, etb))

kundi Hook:
    """A hook to replace sys.excepthook that shows tracebacks kwenye HTML."""

    eleza __init__(self, display=1, logdir=Tupu, context=5, file=Tupu,
                 format="html"):
        self.display = display          # send tracebacks to browser ikiwa true
        self.logdir = logdir            # log tracebacks to files ikiwa sio Tupu
        self.context = context          # number of source code lines per frame
        self.file = file ama sys.stdout  # place to send the output
        self.format = format

    eleza __call__(self, etype, evalue, etb):
        self.handle((etype, evalue, etb))

    eleza handle(self, info=Tupu):
        info = info ama sys.exc_info()
        ikiwa self.format == "html":
            self.file.write(reset())

        formatter = (self.format=="html") na html ama text
        plain = Uongo
        jaribu:
            doc = formatter(info, self.context)
        except:                         # just kwenye case something goes wrong
            doc = ''.join(traceback.format_exception(*info))
            plain = Kweli

        ikiwa self.display:
            ikiwa plain:
                doc = pydoc.html.escape(doc)
                self.file.write('<pre>' + doc + '</pre>\n')
            isipokua:
                self.file.write(doc + '\n')
        isipokua:
            self.file.write('<p>A problem occurred kwenye a Python script.\n')

        ikiwa self.logdir ni sio Tupu:
            suffix = ['.txt', '.html'][self.format=="html"]
            (fd, path) = tempfile.mkstemp(suffix=suffix, dir=self.logdir)

            jaribu:
                with os.fdopen(fd, 'w') kama file:
                    file.write(doc)
                msg = '%s contains the description of this error.' % path
            except:
                msg = 'Tried to save traceback to %s, but failed.' % path

            ikiwa self.format == 'html':
                self.file.write('<p>%s</p>\n' % msg)
            isipokua:
                self.file.write(msg + '\n')
        jaribu:
            self.file.flush()
        except: pita

handler = Hook().handle
eleza enable(display=1, logdir=Tupu, context=5, format="html"):
    """Install an exception handler that formats tracebacks kama HTML.

    The optional argument 'display' can be set to 0 to suppress sending the
    traceback to the browser, na 'logdir' can be set to a directory to cause
    tracebacks to be written to files there."""
    sys.excepthook = Hook(display=display, logdir=logdir,
                          context=context, format=format)
