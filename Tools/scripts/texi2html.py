#! /usr/bin/env python3

# Convert GNU texinfo files into HTML, one file per node.
# Based on Texinfo 2.14.
# Usage: texi2html [-d] [-d] [-c] inputfile outputdirectory
# The input file must be a complete texinfo file, e.g. emacs.texi.
# This creates many files (one per info node) kwenye the output directory,
# overwriting existing files of the same name.  All files created have
# ".html" kama their extension.


# XXX To do:
# - handle @comment*** correctly
# - handle @xref {some words} correctly
# - handle @ftable correctly (items aren't indexed?)
# - handle @itemx properly
# - handle @exdent properly
# - add links directly to the proper line kutoka indices
# - check against the definitive list of @-cmds; we still miss (among others):
# - @defindex (hard)
# - @c(omment) kwenye the middle of a line (rarely used)
# - @this* (sio really needed, only used kwenye headers anyway)
# - @today{} (ever used outside title page?)

# More consistent handling of chapters/sections/etc.
# Lots of documentation
# Many more options:
#       -top    designate top node
#       -links  customize which types of links are included
#       -split  split at chapters ama sections instead of nodes
#       -name   Allow different types of filename handling. Non unix systems
#               will have problems ukijumuisha long node names
#       ...
# Support the most recent texinfo version na take a good look at HTML 3.0
# More debugging output (customizable) na more flexible error handling
# How about icons ?

# rpyron 2002-05-07
# Robert Pyron <rpyron@alum.mit.edu>
# 1. BUGFIX: In function makefile(), strip blanks kutoka the nodename.
#    This ni necessary to match the behavior of parser.makeref() na
#    parser.do_node().
# 2. BUGFIX fixed KeyError kwenye end_ifset (well, I may have just made
#    it go away, rather than fix it)
# 3. BUGFIX allow @menu na menu items inside @ifset ama @ifclear
# 4. Support added for:
#       @uref        URL reference
#       @image       image file reference (see note below)
#       @multitable  output an HTML table
#       @vtable
# 5. Partial support kila accents, to match MAKEINFO output
# 6. I added a new command-line option, '-H basename', to specify
#    HTML Help output. This will cause three files to be created
#    kwenye the current directory:
#       `basename`.hhp  HTML Help Workshop project file
#       `basename`.hhc  Contents file kila the project
#       `basename`.hhk  Index file kila the project
#    When fed into HTML Help Workshop, the resulting file will be
#    named `basename`.chm.
# 7. A new class, HTMLHelp, to accomplish item 6.
# 8. Various calls to HTMLHelp functions.
# A NOTE ON IMAGES: Just kama 'outputdirectory' must exist before
# running this program, all referenced images must already exist
# kwenye outputdirectory.

agiza os
agiza sys
agiza string
agiza re

MAGIC = '\\input texinfo'

cmprog = re.compile('^@([a-z]+)([ \t]|$)')        # Command (line-oriented)
blprog = re.compile('^[ \t]*$')                   # Blank line
kwprog = re.compile('@[a-z]+')                    # Keyword (embedded, usually
                                                  # ukijumuisha {} args)
spprog = re.compile('[\n@{}&<>]')                 # Special characters in
                                                  # running text
                                                  #
                                                  # menu item (Yuck!)
miprog = re.compile(r'^\* ([^:]*):(:|[ \t]*([^\t,\n.]+)([^ \t\n]*))[ \t\n]*')
#                    0    1     1 2        3          34         42        0
#                          -----            ----------  ---------
#                                  -|-----------------------------
#                     -----------------------------------------------------




kundi HTMLNode:
    """Some of the parser's functionality ni separated into this class.

    A Node accumulates its contents, takes care of links to other Nodes
    na saves itself when it ni finished na all links are resolved.
    """

    DOCTYPE = '<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN">'

    type = 0
    cont = ''
    epilogue = '</BODY></HTML>\n'

    eleza __init__(self, dir, name, topname, title, next, prev, up):
        self.dirname = dir
        self.name = name
        ikiwa topname:
            self.topname = topname
        isipokua:
            self.topname = name
        self.title = title
        self.next = next
        self.prev = prev
        self.up = up
        self.lines = []

    eleza write(self, *lines):
        kila line kwenye lines:
            self.lines.append(line)

    eleza flush(self):
        ukijumuisha open(self.dirname + '/' + makefile(self.name), 'w') kama fp:
            fp.write(self.prologue)
            fp.write(self.text)
            fp.write(self.epilogue)

    eleza link(self, label, nodename, rel=Tupu, rev=Tupu):
        ikiwa nodename:
            ikiwa nodename.lower() == '(dir)':
                addr = '../dir.html'
                title = ''
            isipokua:
                addr = makefile(nodename)
                title = ' TITLE="%s"' % nodename
            self.write(label, ': <A HREF="', addr, '"', \
                       rel na (' REL=' + rel) ama "", \
                       rev na (' REV=' + rev) ama "", \
                       title, '>', nodename, '</A>  \n')

    eleza finalize(self):
        length = len(self.lines)
        self.text = ''.join(self.lines)
        self.lines = []
        self.open_links()
        self.output_links()
        self.close_links()
        links = ''.join(self.lines)
        self.lines = []
        self.prologue = (
            self.DOCTYPE +
            '\n<HTML><HEAD>\n'
            '  <!-- Converted ukijumuisha texi2html na Python -->\n'
            '  <TITLE>' + self.title + '</TITLE>\n'
            '  <LINK REL=Next HREF="'
                + makefile(self.next) + '" TITLE="' + self.next + '">\n'
            '  <LINK REL=Previous HREF="'
                + makefile(self.prev) + '" TITLE="' + self.prev  + '">\n'
            '  <LINK REL=Up HREF="'
                + makefile(self.up) + '" TITLE="' + self.up  + '">\n'
            '</HEAD><BODY>\n' +
            links)
        ikiwa length > 20:
            self.epilogue = '<P>\n%s</BODY></HTML>\n' % links

    eleza open_links(self):
        self.write('<HR>\n')

    eleza close_links(self):
        self.write('<HR>\n')

    eleza output_links(self):
        ikiwa self.cont != self.next:
            self.link('  Cont', self.cont)
        self.link('  Next', self.next, rel='Next')
        self.link('  Prev', self.prev, rel='Previous')
        self.link('  Up', self.up, rel='Up')
        ikiwa self.name != self.topname:
            self.link('  Top', self.topname)


kundi HTML3Node(HTMLNode):

    DOCTYPE = '<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML Level 3//EN//3.0">'

    eleza open_links(self):
        self.write('<DIV CLASS=Navigation>\n <HR>\n')

    eleza close_links(self):
        self.write(' <HR>\n</DIV>\n')


kundi TexinfoParser:

    COPYRIGHT_SYMBOL = "&copy;"
    FN_ID_PATTERN = "(%(id)s)"
    FN_SOURCE_PATTERN = '<A NAME=footnoteref%(id)s' \
                        ' HREF="#footnotetext%(id)s">' \
                        + FN_ID_PATTERN + '</A>'
    FN_TARGET_PATTERN = '<A NAME=footnotetext%(id)s' \
                        ' HREF="#footnoteref%(id)s">' \
                        + FN_ID_PATTERN + '</A>\n%(text)s<P>\n'
    FN_HEADER = '\n<P>\n<HR NOSHADE SIZE=1 WIDTH=200>\n' \
                '<STRONG><EM>Footnotes</EM></STRONG>\n<P>'


    Node = HTMLNode

    # Initialize an instance
    eleza __init__(self):
        self.unknown = {}       # statistics about unknown @-commands
        self.filenames = {}     # Check kila identical filenames
        self.debugging = 0      # larger values produce more output
        self.print_headers = 0  # always print headers?
        self.nodefp = Tupu      # open file we're writing to
        self.nodelineno = 0     # Linenumber relative to node
        self.links = Tupu       # Links kutoka current node
        self.savetext = Tupu    # If sio Tupu, save text head instead
        self.savestack = []     # If sio Tupu, save text head instead
        self.htmlhelp = Tupu    # html help data
        self.dirname = 'tmp'    # directory where files are created
        self.includedir = '.'   # directory to search @include files
        self.nodename = ''      # name of current node
        self.topname = ''       # name of top node (first node seen)
        self.title = ''         # title of this whole Texinfo tree
        self.resetindex()       # Reset all indices
        self.contents = []      # Reset table of contents
        self.numbering = []     # Reset section numbering counters
        self.nofill = 0         # Normal operation: fill paragraphs
        self.values={'html': 1} # Names that should be parsed kwenye ifset
        self.stackinfo={}       # Keep track of state kwenye the stack
        # XXX The following should be reset per node?!
        self.footnotes = []     # Reset list of footnotes
        self.itemarg = Tupu     # Reset command used by @item
        self.itemnumber = Tupu  # Reset number kila @item kwenye @enumerate
        self.itemindex = Tupu   # Reset item index name
        self.node = Tupu
        self.nodestack = []
        self.cont = 0
        self.includedepth = 0

    # Set htmlhelp helper class
    eleza sethtmlhelp(self, htmlhelp):
        self.htmlhelp = htmlhelp

    # Set (output) directory name
    eleza setdirname(self, dirname):
        self.dirname = dirname

    # Set include directory name
    eleza setincludedir(self, includedir):
        self.includedir = includedir

    # Parse the contents of an entire file
    eleza parse(self, fp):
        line = fp.readline()
        lineno = 1
        wakati line na (line[0] == '%' ama blprog.match(line)):
            line = fp.readline()
            lineno = lineno + 1
        ikiwa line[:len(MAGIC)] != MAGIC:
            ashiria SyntaxError('file does sio begin ukijumuisha %r' % (MAGIC,))
        self.parserest(fp, lineno)

    # Parse the contents of a file, sio expecting a MAGIC header
    eleza parserest(self, fp, initial_lineno):
        lineno = initial_lineno
        self.done = 0
        self.skip = 0
        self.stack = []
        accu = []
        wakati sio self.done:
            line = fp.readline()
            self.nodelineno = self.nodelineno + 1
            ikiwa sio line:
                ikiwa accu:
                    ikiwa sio self.skip: self.process(accu)
                    accu = []
                ikiwa initial_lineno > 0:
                    andika('*** EOF before @bye')
                koma
            lineno = lineno + 1
            mo = cmprog.match(line)
            ikiwa mo:
                a, b = mo.span(1)
                cmd = line[a:b]
                ikiwa cmd kwenye ('noindent', 'refill'):
                    accu.append(line)
                isipokua:
                    ikiwa accu:
                        ikiwa sio self.skip:
                            self.process(accu)
                        accu = []
                    self.command(line, mo)
            lasivyo blprog.match(line) na \
                 'format' haiko kwenye self.stack na \
                 'example' haiko kwenye self.stack:
                ikiwa accu:
                    ikiwa sio self.skip:
                        self.process(accu)
                        ikiwa self.nofill:
                            self.write('\n')
                        isipokua:
                            self.write('<P>\n')
                        accu = []
            isipokua:
                # Append the line including trailing \n!
                accu.append(line)
        #
        ikiwa self.skip:
            andika('*** Still skipping at the end')
        ikiwa self.stack:
            andika('*** Stack sio empty at the end')
            andika('***', self.stack)
        ikiwa self.includedepth == 0:
            wakati self.nodestack:
                self.nodestack[-1].finalize()
                self.nodestack[-1].flush()
                toa self.nodestack[-1]

    # Start saving text kwenye a buffer instead of writing it to a file
    eleza startsaving(self):
        ikiwa self.savetext ni sio Tupu:
            self.savestack.append(self.savetext)
            # print '*** Recursively saving text, expect trouble'
        self.savetext = ''

    # Return the text saved so far na start writing to file again
    eleza collectsavings(self):
        savetext = self.savetext
        ikiwa len(self.savestack) > 0:
            self.savetext = self.savestack[-1]
            toa self.savestack[-1]
        isipokua:
            self.savetext = Tupu
        rudisha savetext ama ''

    # Write text to file, ama save it kwenye a buffer, ama ignore it
    eleza write(self, *args):
        jaribu:
            text = ''.join(args)
        tatizo:
            andika(args)
            ashiria TypeError
        ikiwa self.savetext ni sio Tupu:
            self.savetext = self.savetext + text
        lasivyo self.nodefp:
            self.nodefp.write(text)
        lasivyo self.node:
            self.node.write(text)

    # Complete the current node -- write footnotes na close file
    eleza endnode(self):
        ikiwa self.savetext ni sio Tupu:
            andika('*** Still saving text at end of node')
            dummy = self.collectsavings()
        ikiwa self.footnotes:
            self.writefootnotes()
        ikiwa self.nodefp:
            ikiwa self.nodelineno > 20:
                self.write('<HR>\n')
                [name, next, prev, up] = self.nodelinks[:4]
                self.link('Next', next)
                self.link('Prev', prev)
                self.link('Up', up)
                ikiwa self.nodename != self.topname:
                    self.link('Top', self.topname)
                self.write('<HR>\n')
            self.write('</BODY>\n')
            self.nodefp.close()
            self.nodefp = Tupu
        lasivyo self.node:
            ikiwa sio self.cont na \
               (sio self.node.type ama \
                (self.node.next na self.node.prev na self.node.up)):
                self.node.finalize()
                self.node.flush()
            isipokua:
                self.nodestack.append(self.node)
            self.node = Tupu
        self.nodename = ''

    # Process a list of lines, expanding embedded @-commands
    # This mostly distinguishes between menus na normal text
    eleza process(self, accu):
        ikiwa self.debugging > 1:
            andika('!'*self.debugging, 'process:', self.skip, self.stack, end=' ')
            ikiwa accu: andika(accu[0][:30], end=' ')
            ikiwa accu[0][30:] ama accu[1:]: andika('...', end=' ')
            andika()
        ikiwa self.inmenu():
            # XXX should be done differently
            kila line kwenye accu:
                mo = miprog.match(line)
                ikiwa sio mo:
                    line = line.strip() + '\n'
                    self.expand(line)
                    endelea
                bgn, end = mo.span(0)
                a, b = mo.span(1)
                c, d = mo.span(2)
                e, f = mo.span(3)
                g, h = mo.span(4)
                label = line[a:b]
                nodename = line[c:d]
                ikiwa nodename[0] == ':': nodename = label
                isipokua: nodename = line[e:f]
                punct = line[g:h]
                self.write('  <LI><A HREF="',
                           makefile(nodename),
                           '">', nodename,
                           '</A>', punct, '\n')
                self.htmlhelp.menuitem(nodename)
                self.expand(line[end:])
        isipokua:
            text = ''.join(accu)
            self.expand(text)

    # find 'menu' (we might be inside 'ifset' ama 'ifclear')
    eleza inmenu(self):
        #ikiwa 'menu' kwenye self.stack:
        #    print 'inmenu   :', self.skip, self.stack, self.stackinfo
        stack = self.stack
        wakati stack na stack[-1] kwenye ('ifset','ifclear'):
            jaribu:
                ikiwa self.stackinfo[len(stack)]:
                    rudisha 0
            tatizo KeyError:
                pita
            stack = stack[:-1]
        rudisha (stack na stack[-1] == 'menu')

    # Write a string, expanding embedded @-commands
    eleza expand(self, text):
        stack = []
        i = 0
        n = len(text)
        wakati i < n:
            start = i
            mo = spprog.search(text, i)
            ikiwa mo:
                i = mo.start()
            isipokua:
                self.write(text[start:])
                koma
            self.write(text[start:i])
            c = text[i]
            i = i+1
            ikiwa c == '\n':
                self.write('\n')
                endelea
            ikiwa c == '<':
                self.write('&lt;')
                endelea
            ikiwa c == '>':
                self.write('&gt;')
                endelea
            ikiwa c == '&':
                self.write('&amp;')
                endelea
            ikiwa c == '{':
                stack.append('')
                endelea
            ikiwa c == '}':
                ikiwa sio stack:
                    andika('*** Unmatched }')
                    self.write('}')
                    endelea
                cmd = stack[-1]
                toa stack[-1]
                jaribu:
                    method = getattr(self, 'close_' + cmd)
                tatizo AttributeError:
                    self.unknown_close(cmd)
                    endelea
                method()
                endelea
            ikiwa c != '@':
                # Cannot happen unless spprog ni changed
                ashiria RuntimeError('unexpected funny %r' % c)
            start = i
            wakati i < n na text[i] kwenye string.ascii_letters: i = i+1
            ikiwa i == start:
                # @ plus non-letter: literal next character
                i = i+1
                c = text[start:i]
                ikiwa c == ':':
                    # `@:' means no extra space after
                    # preceding `.', `?', `!' ama `:'
                    pita
                isipokua:
                    # `@.' means a sentence-ending period;
                    # `@@', `@{', `@}' quote `@', `{', `}'
                    self.write(c)
                endelea
            cmd = text[start:i]
            ikiwa i < n na text[i] == '{':
                i = i+1
                stack.append(cmd)
                jaribu:
                    method = getattr(self, 'open_' + cmd)
                tatizo AttributeError:
                    self.unknown_open(cmd)
                    endelea
                method()
                endelea
            jaribu:
                method = getattr(self, 'handle_' + cmd)
            tatizo AttributeError:
                self.unknown_handle(cmd)
                endelea
            method()
        ikiwa stack:
            andika('*** Stack sio empty at para:', stack)

    # --- Handle unknown embedded @-commands ---

    eleza unknown_open(self, cmd):
        andika('*** No open func kila @' + cmd + '{...}')
        cmd = cmd + '{'
        self.write('@', cmd)
        ikiwa cmd haiko kwenye self.unknown:
            self.unknown[cmd] = 1
        isipokua:
            self.unknown[cmd] = self.unknown[cmd] + 1

    eleza unknown_close(self, cmd):
        andika('*** No close func kila @' + cmd + '{...}')
        cmd = '}' + cmd
        self.write('}')
        ikiwa cmd haiko kwenye self.unknown:
            self.unknown[cmd] = 1
        isipokua:
            self.unknown[cmd] = self.unknown[cmd] + 1

    eleza unknown_handle(self, cmd):
        andika('*** No handler kila @' + cmd)
        self.write('@', cmd)
        ikiwa cmd haiko kwenye self.unknown:
            self.unknown[cmd] = 1
        isipokua:
            self.unknown[cmd] = self.unknown[cmd] + 1

    # XXX The following sections should be ordered kama the texinfo docs

    # --- Embedded @-commands without {} argument list --

    eleza handle_noindent(self): pita

    eleza handle_refill(self): pita

    # --- Include file handling ---

    eleza do_include(self, args):
        file = args
        file = os.path.join(self.includedir, file)
        jaribu:
            fp = open(file, 'r')
        tatizo IOError kama msg:
            andika('*** Can\'t open include file', repr(file))
            rudisha
        ukijumuisha fp:
            andika('!'*self.debugging, '--> file', repr(file))
            save_done = self.done
            save_skip = self.skip
            save_stack = self.stack
            self.includedepth = self.includedepth + 1
            self.parserest(fp, 0)
            self.includedepth = self.includedepth - 1
        self.done = save_done
        self.skip = save_skip
        self.stack = save_stack
        andika('!'*self.debugging, '<-- file', repr(file))

    # --- Special Insertions ---

    eleza open_dmn(self): pita
    eleza close_dmn(self): pita

    eleza open_dots(self): self.write('...')
    eleza close_dots(self): pita

    eleza open_bullet(self): pita
    eleza close_bullet(self): pita

    eleza open_TeX(self): self.write('TeX')
    eleza close_TeX(self): pita

    eleza handle_copyright(self): self.write(self.COPYRIGHT_SYMBOL)
    eleza open_copyright(self): self.write(self.COPYRIGHT_SYMBOL)
    eleza close_copyright(self): pita

    eleza open_minus(self): self.write('-')
    eleza close_minus(self): pita

    # --- Accents ---

    # rpyron 2002-05-07
    # I would like to do at least kama well kama makeinfo when
    # it ni producing HTML output:
    #
    #   input               output
    #     @"o                 @"o                umlaut accent
    #     @'o                 'o                 acute accent
    #     @,{c}               @,{c}              cedilla accent
    #     @=o                 @=o                macron/overbar accent
    #     @^o                 @^o                circumflex accent
    #     @`o                 `o                 grave accent
    #     @~o                 @~o                tilde accent
    #     @dotaccent{o}       @dotaccent{o}      overdot accent
    #     @H{o}               @H{o}              long Hungarian umlaut
    #     @ringaccent{o}      @ringaccent{o}     ring accent
    #     @tieaccent{oo}      @tieaccent{oo}     tie-after accent
    #     @u{o}               @u{o}              breve accent
    #     @ubaraccent{o}      @ubaraccent{o}     underbar accent
    #     @udotaccent{o}      @udotaccent{o}     underdot accent
    #     @v{o}               @v{o}              hacek ama check accent
    #     @exclamdown{}       &#161;             upside-down !
    #     @questiondown{}     &#191;             upside-down ?
    #     @aa{},@AA{}         &#229;,&#197;      a,A ukijumuisha circle
    #     @ae{},@AE{}         &#230;,&#198;      ae,AE ligatures
    #     @dotless{i}         @dotless{i}        dotless i
    #     @dotless{j}         @dotless{j}        dotless j
    #     @l{},@L{}           l/,L/              suppressed-L,l
    #     @o{},@O{}           &#248;,&#216;      O,o ukijumuisha slash
    #     @oe{},@OE{}         oe,OE              oe,OE ligatures
    #     @ss{}               &#223;             es-zet ama sharp S
    #
    # The following character codes na approximations have been
    # copied kutoka makeinfo's HTML output.

    eleza open_exclamdown(self): self.write('&#161;')   # upside-down !
    eleza close_exclamdown(self): pita
    eleza open_questiondown(self): self.write('&#191;') # upside-down ?
    eleza close_questiondown(self): pita
    eleza open_aa(self): self.write('&#229;') # a ukijumuisha circle
    eleza close_aa(self): pita
    eleza open_AA(self): self.write('&#197;') # A ukijumuisha circle
    eleza close_AA(self): pita
    eleza open_ae(self): self.write('&#230;') # ae ligatures
    eleza close_ae(self): pita
    eleza open_AE(self): self.write('&#198;') # AE ligatures
    eleza close_AE(self): pita
    eleza open_o(self): self.write('&#248;')  # o ukijumuisha slash
    eleza close_o(self): pita
    eleza open_O(self): self.write('&#216;')  # O ukijumuisha slash
    eleza close_O(self): pita
    eleza open_ss(self): self.write('&#223;') # es-zet ama sharp S
    eleza close_ss(self): pita
    eleza open_oe(self): self.write('oe')     # oe ligatures
    eleza close_oe(self): pita
    eleza open_OE(self): self.write('OE')     # OE ligatures
    eleza close_OE(self): pita
    eleza open_l(self): self.write('l/')      # suppressed-l
    eleza close_l(self): pita
    eleza open_L(self): self.write('L/')      # suppressed-L
    eleza close_L(self): pita

    # --- Special Glyphs kila Examples ---

    eleza open_result(self): self.write('=&gt;')
    eleza close_result(self): pita

    eleza open_expansion(self): self.write('==&gt;')
    eleza close_expansion(self): pita

    eleza open_andika(self): self.write('-|')
    eleza close_andika(self): pita

    eleza open_error(self): self.write('error--&gt;')
    eleza close_error(self): pita

    eleza open_equiv(self): self.write('==')
    eleza close_equiv(self): pita

    eleza open_point(self): self.write('-!-')
    eleza close_point(self): pita

    # --- Cross References ---

    eleza open_pxref(self):
        self.write('see ')
        self.startsaving()
    eleza close_pxref(self):
        self.makeref()

    eleza open_xref(self):
        self.write('See ')
        self.startsaving()
    eleza close_xref(self):
        self.makeref()

    eleza open_ref(self):
        self.startsaving()
    eleza close_ref(self):
        self.makeref()

    eleza open_inforef(self):
        self.write('See info file ')
        self.startsaving()
    eleza close_inforef(self):
        text = self.collectsavings()
        args = [s.strip() kila s kwenye text.split(',')]
        wakati len(args) < 3: args.append('')
        node = args[0]
        file = args[2]
        self.write('`', file, '\', node `', node, '\'')

    eleza makeref(self):
        text = self.collectsavings()
        args = [s.strip() kila s kwenye text.split(',')]
        wakati len(args) < 5: args.append('')
        nodename = label = args[0]
        ikiwa args[2]: label = args[2]
        file = args[3]
        title = args[4]
        href = makefile(nodename)
        ikiwa file:
            href = '../' + file + '/' + href
        self.write('<A HREF="', href, '">', label, '</A>')

    # rpyron 2002-05-07  uref support
    eleza open_uref(self):
        self.startsaving()
    eleza close_uref(self):
        text = self.collectsavings()
        args = [s.strip() kila s kwenye text.split(',')]
        wakati len(args) < 2: args.append('')
        href = args[0]
        label = args[1]
        ikiwa sio label: label = href
        self.write('<A HREF="', href, '">', label, '</A>')

    # rpyron 2002-05-07  image support
    # GNU makeinfo producing HTML output tries `filename.png'; if
    # that does sio exist, it tries `filename.jpg'. If that does
    # sio exist either, it complains. GNU makeinfo does sio handle
    # GIF files; however, I include GIF support here because
    # MySQL documentation uses GIF files.

    eleza open_image(self):
        self.startsaving()
    eleza close_image(self):
        self.makeimage()
    eleza makeimage(self):
        text = self.collectsavings()
        args = [s.strip() kila s kwenye text.split(',')]
        wakati len(args) < 5: args.append('')
        filename = args[0]
        width    = args[1]
        height   = args[2]
        alt      = args[3]
        ext      = args[4]

        # The HTML output will have a reference to the image
        # that ni relative to the HTML output directory,
        # which ni what 'filename' gives us. However, we need
        # to find it relative to our own current directory,
        # so we construct 'imagename'.
        imagelocation = self.dirname + '/' + filename

        ikiwa   os.path.exists(imagelocation+'.png'):
            filename += '.png'
        lasivyo os.path.exists(imagelocation+'.jpg'):
            filename += '.jpg'
        lasivyo os.path.exists(imagelocation+'.gif'):   # MySQL uses GIF files
            filename += '.gif'
        isipokua:
            andika("*** Cannot find image " + imagelocation)
        #TODO: what ni 'ext'?
        self.write('<IMG SRC="', filename, '"',                     \
                    width  na (' WIDTH="'  + width  + '"') ama "",  \
                    height na (' HEIGHT="' + height + '"') ama "",  \
                    alt    na (' ALT="'    + alt    + '"') ama "",  \
                    '/>' )
        self.htmlhelp.addimage(imagelocation)


    # --- Marking Words na Phrases ---

    # --- Other @xxx{...} commands ---

    eleza open_(self): pita # Used by {text enclosed kwenye braces}
    eleza close_(self): pita

    open_asis = open_
    close_asis = close_

    eleza open_cite(self): self.write('<CITE>')
    eleza close_cite(self): self.write('</CITE>')

    eleza open_code(self): self.write('<CODE>')
    eleza close_code(self): self.write('</CODE>')

    eleza open_t(self): self.write('<TT>')
    eleza close_t(self): self.write('</TT>')

    eleza open_dfn(self): self.write('<DFN>')
    eleza close_dfn(self): self.write('</DFN>')

    eleza open_emph(self): self.write('<EM>')
    eleza close_emph(self): self.write('</EM>')

    eleza open_i(self): self.write('<I>')
    eleza close_i(self): self.write('</I>')

    eleza open_footnote(self):
        # ikiwa self.savetext ni sio Tupu:
        #       print '*** Recursive footnote -- expect weirdness'
        id = len(self.footnotes) + 1
        self.write(self.FN_SOURCE_PATTERN % {'id': repr(id)})
        self.startsaving()

    eleza close_footnote(self):
        id = len(self.footnotes) + 1
        self.footnotes.append((id, self.collectsavings()))

    eleza writefootnotes(self):
        self.write(self.FN_HEADER)
        kila id, text kwenye self.footnotes:
            self.write(self.FN_TARGET_PATTERN
                       % {'id': repr(id), 'text': text})
        self.footnotes = []

    eleza open_file(self): self.write('<CODE>')
    eleza close_file(self): self.write('</CODE>')

    eleza open_kbd(self): self.write('<KBD>')
    eleza close_kbd(self): self.write('</KBD>')

    eleza open_key(self): self.write('<KEY>')
    eleza close_key(self): self.write('</KEY>')

    eleza open_r(self): self.write('<R>')
    eleza close_r(self): self.write('</R>')

    eleza open_samp(self): self.write('`<SAMP>')
    eleza close_samp(self): self.write('</SAMP>\'')

    eleza open_sc(self): self.write('<SMALLCAPS>')
    eleza close_sc(self): self.write('</SMALLCAPS>')

    eleza open_strong(self): self.write('<STRONG>')
    eleza close_strong(self): self.write('</STRONG>')

    eleza open_b(self): self.write('<B>')
    eleza close_b(self): self.write('</B>')

    eleza open_var(self): self.write('<VAR>')
    eleza close_var(self): self.write('</VAR>')

    eleza open_w(self): self.write('<NOBREAK>')
    eleza close_w(self): self.write('</NOBREAK>')

    eleza open_url(self): self.startsaving()
    eleza close_url(self):
        text = self.collectsavings()
        self.write('<A HREF="', text, '">', text, '</A>')

    eleza open_email(self): self.startsaving()
    eleza close_email(self):
        text = self.collectsavings()
        self.write('<A HREF="mailto:', text, '">', text, '</A>')

    open_titlefont = open_
    close_titlefont = close_

    eleza open_small(self): pita
    eleza close_small(self): pita

    eleza command(self, line, mo):
        a, b = mo.span(1)
        cmd = line[a:b]
        args = line[b:].strip()
        ikiwa self.debugging > 1:
            andika('!'*self.debugging, 'command:', self.skip, self.stack, \
                  '@' + cmd, args)
        jaribu:
            func = getattr(self, 'do_' + cmd)
        tatizo AttributeError:
            jaribu:
                func = getattr(self, 'bgn_' + cmd)
            tatizo AttributeError:
                # don't complain ikiwa we are skipping anyway
                ikiwa sio self.skip:
                    self.unknown_cmd(cmd, args)
                rudisha
            self.stack.append(cmd)
            func(args)
            rudisha
        ikiwa sio self.skip ama cmd == 'end':
            func(args)

    eleza unknown_cmd(self, cmd, args):
        andika('*** unknown', '@' + cmd, args)
        ikiwa cmd haiko kwenye self.unknown:
            self.unknown[cmd] = 1
        isipokua:
            self.unknown[cmd] = self.unknown[cmd] + 1

    eleza do_end(self, args):
        words = args.split()
        ikiwa sio words:
            andika('*** @end w/o args')
        isipokua:
            cmd = words[0]
            ikiwa sio self.stack ama self.stack[-1] != cmd:
                andika('*** @end', cmd, 'unexpected')
            isipokua:
                toa self.stack[-1]
            jaribu:
                func = getattr(self, 'end_' + cmd)
            tatizo AttributeError:
                self.unknown_end(cmd)
                rudisha
            func()

    eleza unknown_end(self, cmd):
        cmd = 'end ' + cmd
        andika('*** unknown', '@' + cmd)
        ikiwa cmd haiko kwenye self.unknown:
            self.unknown[cmd] = 1
        isipokua:
            self.unknown[cmd] = self.unknown[cmd] + 1

    # --- Comments ---

    eleza do_comment(self, args): pita
    do_c = do_comment

    # --- Conditional processing ---

    eleza bgn_ifinfo(self, args): pita
    eleza end_ifinfo(self): pita

    eleza bgn_iftex(self, args): self.skip = self.skip + 1
    eleza end_iftex(self): self.skip = self.skip - 1

    eleza bgn_ignore(self, args): self.skip = self.skip + 1
    eleza end_ignore(self): self.skip = self.skip - 1

    eleza bgn_tex(self, args): self.skip = self.skip + 1
    eleza end_tex(self): self.skip = self.skip - 1

    eleza do_set(self, args):
        fields = args.split(' ')
        key = fields[0]
        ikiwa len(fields) == 1:
            value = 1
        isipokua:
            value = ' '.join(fields[1:])
        self.values[key] = value

    eleza do_clear(self, args):
        self.values[args] = Tupu

    eleza bgn_ifset(self, args):
        ikiwa args haiko kwenye self.values ama self.values[args] ni Tupu:
            self.skip = self.skip + 1
            self.stackinfo[len(self.stack)] = 1
        isipokua:
            self.stackinfo[len(self.stack)] = 0
    eleza end_ifset(self):
        jaribu:
            ikiwa self.stackinfo[len(self.stack) + 1]:
                self.skip = self.skip - 1
            toa self.stackinfo[len(self.stack) + 1]
        tatizo KeyError:
            andika('*** end_ifset: KeyError :', len(self.stack) + 1)

    eleza bgn_ifclear(self, args):
        ikiwa args kwenye self.values na self.values[args] ni sio Tupu:
            self.skip = self.skip + 1
            self.stackinfo[len(self.stack)] = 1
        isipokua:
            self.stackinfo[len(self.stack)] = 0
    eleza end_ifclear(self):
        jaribu:
            ikiwa self.stackinfo[len(self.stack) + 1]:
                self.skip = self.skip - 1
            toa self.stackinfo[len(self.stack) + 1]
        tatizo KeyError:
            andika('*** end_ifclear: KeyError :', len(self.stack) + 1)

    eleza open_value(self):
        self.startsaving()

    eleza close_value(self):
        key = self.collectsavings()
        ikiwa key kwenye self.values:
            self.write(self.values[key])
        isipokua:
            andika('*** Undefined value: ', key)

    # --- Beginning a file ---

    do_finalout = do_comment
    do_setchapternewpage = do_comment
    do_setfilename = do_comment

    eleza do_settitle(self, args):
        self.startsaving()
        self.expand(args)
        self.title = self.collectsavings()
    eleza do_parskip(self, args): pita

    # --- Ending a file ---

    eleza do_bye(self, args):
        self.endnode()
        self.done = 1

    # --- Title page ---

    eleza bgn_titlepage(self, args): self.skip = self.skip + 1
    eleza end_titlepage(self): self.skip = self.skip - 1
    eleza do_shorttitlepage(self, args): pita

    eleza do_center(self, args):
        # Actually sio used outside title page...
        self.write('<H1>')
        self.expand(args)
        self.write('</H1>\n')
    do_title = do_center
    do_subtitle = do_center
    do_author = do_center

    do_vskip = do_comment
    do_vfill = do_comment
    do_smallbook = do_comment

    do_paragraphindent = do_comment
    do_setchapternewpage = do_comment
    do_headings = do_comment
    do_footnotestyle = do_comment

    do_evenheading = do_comment
    do_evenfooting = do_comment
    do_oddheading = do_comment
    do_oddfooting = do_comment
    do_everyheading = do_comment
    do_everyfooting = do_comment

    # --- Nodes ---

    eleza do_node(self, args):
        self.endnode()
        self.nodelineno = 0
        parts = [s.strip() kila s kwenye args.split(',')]
        wakati len(parts) < 4: parts.append('')
        self.nodelinks = parts
        [name, next, prev, up] = parts[:4]
        file = self.dirname + '/' + makefile(name)
        ikiwa file kwenye self.filenames:
            andika('*** Filename already kwenye use: ', file)
        isipokua:
            ikiwa self.debugging: andika('!'*self.debugging, '--- writing', file)
        self.filenames[file] = 1
        # self.nodefp = open(file, 'w')
        self.nodename = name
        ikiwa self.cont na self.nodestack:
            self.nodestack[-1].cont = self.nodename
        ikiwa sio self.topname: self.topname = name
        title = name
        ikiwa self.title: title = title + ' -- ' + self.title
        self.node = self.Node(self.dirname, self.nodename, self.topname,
                              title, next, prev, up)
        self.htmlhelp.addnode(self.nodename,next,prev,up,file)

    eleza link(self, label, nodename):
        ikiwa nodename:
            ikiwa nodename.lower() == '(dir)':
                addr = '../dir.html'
            isipokua:
                addr = makefile(nodename)
            self.write(label, ': <A HREF="', addr, '" TYPE="',
                       label, '">', nodename, '</A>  \n')

    # --- Sectioning commands ---

    eleza popstack(self, type):
        ikiwa (self.node):
            self.node.type = type
            wakati self.nodestack:
                ikiwa self.nodestack[-1].type > type:
                    self.nodestack[-1].finalize()
                    self.nodestack[-1].flush()
                    toa self.nodestack[-1]
                lasivyo self.nodestack[-1].type == type:
                    ikiwa sio self.nodestack[-1].next:
                        self.nodestack[-1].next = self.node.name
                    ikiwa sio self.node.prev:
                        self.node.prev = self.nodestack[-1].name
                    self.nodestack[-1].finalize()
                    self.nodestack[-1].flush()
                    toa self.nodestack[-1]
                isipokua:
                    ikiwa type > 1 na sio self.node.up:
                        self.node.up = self.nodestack[-1].name
                    koma

    eleza do_chapter(self, args):
        self.heading('H1', args, 0)
        self.popstack(1)

    eleza do_unnumbered(self, args):
        self.heading('H1', args, -1)
        self.popstack(1)
    eleza do_appendix(self, args):
        self.heading('H1', args, -1)
        self.popstack(1)
    eleza do_top(self, args):
        self.heading('H1', args, -1)
    eleza do_chapheading(self, args):
        self.heading('H1', args, -1)
    eleza do_majorheading(self, args):
        self.heading('H1', args, -1)

    eleza do_section(self, args):
        self.heading('H1', args, 1)
        self.popstack(2)

    eleza do_unnumberedsec(self, args):
        self.heading('H1', args, -1)
        self.popstack(2)
    eleza do_appendixsec(self, args):
        self.heading('H1', args, -1)
        self.popstack(2)
    do_appendixsection = do_appendixsec
    eleza do_heading(self, args):
        self.heading('H1', args, -1)

    eleza do_subsection(self, args):
        self.heading('H2', args, 2)
        self.popstack(3)
    eleza do_unnumberedsubsec(self, args):
        self.heading('H2', args, -1)
        self.popstack(3)
    eleza do_appendixsubsec(self, args):
        self.heading('H2', args, -1)
        self.popstack(3)
    eleza do_subheading(self, args):
        self.heading('H2', args, -1)

    eleza do_subsubsection(self, args):
        self.heading('H3', args, 3)
        self.popstack(4)
    eleza do_unnumberedsubsubsec(self, args):
        self.heading('H3', args, -1)
        self.popstack(4)
    eleza do_appendixsubsubsec(self, args):
        self.heading('H3', args, -1)
        self.popstack(4)
    eleza do_subsubheading(self, args):
        self.heading('H3', args, -1)

    eleza heading(self, type, args, level):
        ikiwa level >= 0:
            wakati len(self.numbering) <= level:
                self.numbering.append(0)
            toa self.numbering[level+1:]
            self.numbering[level] = self.numbering[level] + 1
            x = ''
            kila i kwenye self.numbering:
                x = x + repr(i) + '.'
            args = x + ' ' + args
            self.contents.append((level, args, self.nodename))
        self.write('<', type, '>')
        self.expand(args)
        self.write('</', type, '>\n')
        ikiwa self.debugging ama self.print_headers:
            andika('---', args)

    eleza do_contents(self, args):
        # pita
        self.listcontents('Table of Contents', 999)

    eleza do_shortcontents(self, args):
        pita
        # self.listcontents('Short Contents', 0)
    do_summarycontents = do_shortcontents

    eleza listcontents(self, title, maxlevel):
        self.write('<H1>', title, '</H1>\n<UL COMPACT PLAIN>\n')
        prevlevels = [0]
        kila level, title, node kwenye self.contents:
            ikiwa level > maxlevel:
                endelea
            ikiwa level > prevlevels[-1]:
                # can only advance one level at a time
                self.write('  '*prevlevels[-1], '<UL PLAIN>\n')
                prevlevels.append(level)
            lasivyo level < prevlevels[-1]:
                # might drop back multiple levels
                wakati level < prevlevels[-1]:
                    toa prevlevels[-1]
                    self.write('  '*prevlevels[-1],
                               '</UL>\n')
            self.write('  '*level, '<LI> <A HREF="',
                       makefile(node), '">')
            self.expand(title)
            self.write('</A>\n')
        self.write('</UL>\n' * len(prevlevels))

    # --- Page lay-out ---

    # These commands are only meaningful kwenye printed text

    eleza do_page(self, args): pita

    eleza do_need(self, args): pita

    eleza bgn_group(self, args): pita
    eleza end_group(self): pita

    # --- Line lay-out ---

    eleza do_sp(self, args):
        ikiwa self.nofill:
            self.write('\n')
        isipokua:
            self.write('<P>\n')

    eleza do_hline(self, args):
        self.write('<HR>')

    # --- Function na variable definitions ---

    eleza bgn_deffn(self, args):
        self.write('<DL>')
        self.do_deffnx(args)

    eleza end_deffn(self):
        self.write('</DL>\n')

    eleza do_deffnx(self, args):
        self.write('<DT>')
        words = splitwords(args, 2)
        [category, name], rest = words[:2], words[2:]
        self.expand('@b{%s}' % name)
        kila word kwenye rest: self.expand(' ' + makevar(word))
        #self.expand(' -- ' + category)
        self.write('\n<DD>')
        self.index('fn', name)

    eleza bgn_defun(self, args): self.bgn_deffn('Function ' + args)
    end_defun = end_deffn
    eleza do_defunx(self, args): self.do_deffnx('Function ' + args)

    eleza bgn_defmac(self, args): self.bgn_deffn('Macro ' + args)
    end_defmac = end_deffn
    eleza do_defmacx(self, args): self.do_deffnx('Macro ' + args)

    eleza bgn_defspec(self, args): self.bgn_deffn('{Special Form} ' + args)
    end_defspec = end_deffn
    eleza do_defspecx(self, args): self.do_deffnx('{Special Form} ' + args)

    eleza bgn_defvr(self, args):
        self.write('<DL>')
        self.do_defvrx(args)

    end_defvr = end_deffn

    eleza do_defvrx(self, args):
        self.write('<DT>')
        words = splitwords(args, 2)
        [category, name], rest = words[:2], words[2:]
        self.expand('@code{%s}' % name)
        # If there are too many arguments, show them
        kila word kwenye rest: self.expand(' ' + word)
        #self.expand(' -- ' + category)
        self.write('\n<DD>')
        self.index('vr', name)

    eleza bgn_defvar(self, args): self.bgn_defvr('Variable ' + args)
    end_defvar = end_defvr
    eleza do_defvarx(self, args): self.do_defvrx('Variable ' + args)

    eleza bgn_defopt(self, args): self.bgn_defvr('{User Option} ' + args)
    end_defopt = end_defvr
    eleza do_defoptx(self, args): self.do_defvrx('{User Option} ' + args)

    # --- Ditto kila typed languages ---

    eleza bgn_deftypefn(self, args):
        self.write('<DL>')
        self.do_deftypefnx(args)

    end_deftypefn = end_deffn

    eleza do_deftypefnx(self, args):
        self.write('<DT>')
        words = splitwords(args, 3)
        [category, datatype, name], rest = words[:3], words[3:]
        self.expand('@code{%s} @b{%s}' % (datatype, name))
        kila word kwenye rest: self.expand(' ' + makevar(word))
        #self.expand(' -- ' + category)
        self.write('\n<DD>')
        self.index('fn', name)


    eleza bgn_deftypefun(self, args): self.bgn_deftypefn('Function ' + args)
    end_deftypefun = end_deftypefn
    eleza do_deftypefunx(self, args): self.do_deftypefnx('Function ' + args)

    eleza bgn_deftypevr(self, args):
        self.write('<DL>')
        self.do_deftypevrx(args)

    end_deftypevr = end_deftypefn

    eleza do_deftypevrx(self, args):
        self.write('<DT>')
        words = splitwords(args, 3)
        [category, datatype, name], rest = words[:3], words[3:]
        self.expand('@code{%s} @b{%s}' % (datatype, name))
        # If there are too many arguments, show them
        kila word kwenye rest: self.expand(' ' + word)
        #self.expand(' -- ' + category)
        self.write('\n<DD>')
        self.index('fn', name)

    eleza bgn_deftypevar(self, args):
        self.bgn_deftypevr('Variable ' + args)
    end_deftypevar = end_deftypevr
    eleza do_deftypevarx(self, args):
        self.do_deftypevrx('Variable ' + args)

    # --- Ditto kila object-oriented languages ---

    eleza bgn_defcv(self, args):
        self.write('<DL>')
        self.do_defcvx(args)

    end_defcv = end_deftypevr

    eleza do_defcvx(self, args):
        self.write('<DT>')
        words = splitwords(args, 3)
        [category, classname, name], rest = words[:3], words[3:]
        self.expand('@b{%s}' % name)
        # If there are too many arguments, show them
        kila word kwenye rest: self.expand(' ' + word)
        #self.expand(' -- %s of @code{%s}' % (category, classname))
        self.write('\n<DD>')
        self.index('vr', '%s @r{on %s}' % (name, classname))

    eleza bgn_defivar(self, args):
        self.bgn_defcv('{Instance Variable} ' + args)
    end_defivar = end_defcv
    eleza do_defivarx(self, args):
        self.do_defcvx('{Instance Variable} ' + args)

    eleza bgn_defop(self, args):
        self.write('<DL>')
        self.do_defopx(args)

    end_defop = end_defcv

    eleza do_defopx(self, args):
        self.write('<DT>')
        words = splitwords(args, 3)
        [category, classname, name], rest = words[:3], words[3:]
        self.expand('@b{%s}' % name)
        kila word kwenye rest: self.expand(' ' + makevar(word))
        #self.expand(' -- %s of @code{%s}' % (category, classname))
        self.write('\n<DD>')
        self.index('fn', '%s @r{on %s}' % (name, classname))

    eleza bgn_defmethod(self, args):
        self.bgn_defop('Method ' + args)
    end_defmethod = end_defop
    eleza do_defmethodx(self, args):
        self.do_defopx('Method ' + args)

    # --- Ditto kila data types ---

    eleza bgn_deftp(self, args):
        self.write('<DL>')
        self.do_deftpx(args)

    end_deftp = end_defcv

    eleza do_deftpx(self, args):
        self.write('<DT>')
        words = splitwords(args, 2)
        [category, name], rest = words[:2], words[2:]
        self.expand('@b{%s}' % name)
        kila word kwenye rest: self.expand(' ' + word)
        #self.expand(' -- ' + category)
        self.write('\n<DD>')
        self.index('tp', name)

    # --- Making Lists na Tables

    eleza bgn_enumerate(self, args):
        ikiwa sio args:
            self.write('<OL>\n')
            self.stackinfo[len(self.stack)] = '</OL>\n'
        isipokua:
            self.itemnumber = args
            self.write('<UL>\n')
            self.stackinfo[len(self.stack)] = '</UL>\n'
    eleza end_enumerate(self):
        self.itemnumber = Tupu
        self.write(self.stackinfo[len(self.stack) + 1])
        toa self.stackinfo[len(self.stack) + 1]

    eleza bgn_itemize(self, args):
        self.itemarg = args
        self.write('<UL>\n')
    eleza end_itemize(self):
        self.itemarg = Tupu
        self.write('</UL>\n')

    eleza bgn_table(self, args):
        self.itemarg = args
        self.write('<DL>\n')
    eleza end_table(self):
        self.itemarg = Tupu
        self.write('</DL>\n')

    eleza bgn_ftable(self, args):
        self.itemindex = 'fn'
        self.bgn_table(args)
    eleza end_ftable(self):
        self.itemindex = Tupu
        self.end_table()

    eleza bgn_vtable(self, args):
        self.itemindex = 'vr'
        self.bgn_table(args)
    eleza end_vtable(self):
        self.itemindex = Tupu
        self.end_table()

    eleza do_item(self, args):
        ikiwa self.itemindex: self.index(self.itemindex, args)
        ikiwa self.itemarg:
            ikiwa self.itemarg[0] == '@' na self.itemarg[1] na \
                            self.itemarg[1] kwenye string.ascii_letters:
                args = self.itemarg + '{' + args + '}'
            isipokua:
                # some other character, e.g. '-'
                args = self.itemarg + ' ' + args
        ikiwa self.itemnumber ni sio Tupu:
            args = self.itemnumber + '. ' + args
            self.itemnumber = increment(self.itemnumber)
        ikiwa self.stack na self.stack[-1] == 'table':
            self.write('<DT>')
            self.expand(args)
            self.write('\n<DD>')
        lasivyo self.stack na self.stack[-1] == 'multitable':
            self.write('<TR><TD>')
            self.expand(args)
            self.write('</TD>\n</TR>\n')
        isipokua:
            self.write('<LI>')
            self.expand(args)
            self.write('  ')
    do_itemx = do_item # XXX Should suppress leading blank line

    # rpyron 2002-05-07  multitable support
    eleza bgn_multitable(self, args):
        self.itemarg = Tupu     # should be handled by columnfractions
        self.write('<TABLE BORDER="">\n')
    eleza end_multitable(self):
        self.itemarg = Tupu
        self.write('</TABLE>\n<BR>\n')
    eleza handle_columnfractions(self):
        # It would be better to handle this, but kila now it's kwenye the way...
        self.itemarg = Tupu
    eleza handle_tab(self):
        self.write('</TD>\n    <TD>')

    # --- Enumerations, displays, quotations ---
    # XXX Most of these should increase the indentation somehow

    eleza bgn_quotation(self, args): self.write('<BLOCKQUOTE>')
    eleza end_quotation(self): self.write('</BLOCKQUOTE>\n')

    eleza bgn_example(self, args):
        self.nofill = self.nofill + 1
        self.write('<PRE>')
    eleza end_example(self):
        self.write('</PRE>\n')
        self.nofill = self.nofill - 1

    bgn_lisp = bgn_example # Synonym when contents are executable lisp code
    end_lisp = end_example

    bgn_smallexample = bgn_example # XXX Should use smaller font
    end_smallexample = end_example

    bgn_smalllisp = bgn_lisp # Ditto
    end_smalllisp = end_lisp

    bgn_display = bgn_example
    end_display = end_example

    bgn_format = bgn_display
    end_format = end_display

    eleza do_exdent(self, args): self.expand(args + '\n')
    # XXX Should really mess ukijumuisha indentation

    eleza bgn_flushleft(self, args):
        self.nofill = self.nofill + 1
        self.write('<PRE>\n')
    eleza end_flushleft(self):
        self.write('</PRE>\n')
        self.nofill = self.nofill - 1

    eleza bgn_flushright(self, args):
        self.nofill = self.nofill + 1
        self.write('<ADDRESS COMPACT>\n')
    eleza end_flushright(self):
        self.write('</ADDRESS>\n')
        self.nofill = self.nofill - 1

    eleza bgn_menu(self, args):
        self.write('<DIR>\n')
        self.write('  <STRONG><EM>Menu</EM></STRONG><P>\n')
        self.htmlhelp.beginmenu()
    eleza end_menu(self):
        self.write('</DIR>\n')
        self.htmlhelp.endmenu()

    eleza bgn_cartouche(self, args): pita
    eleza end_cartouche(self): pita

    # --- Indices ---

    eleza resetindex(self):
        self.noncodeindices = ['cp']
        self.indextitle = {}
        self.indextitle['cp'] = 'Concept'
        self.indextitle['fn'] = 'Function'
        self.indextitle['ky'] = 'Keyword'
        self.indextitle['pg'] = 'Program'
        self.indextitle['tp'] = 'Type'
        self.indextitle['vr'] = 'Variable'
        #
        self.whichindex = {}
        kila name kwenye self.indextitle:
            self.whichindex[name] = []

    eleza user_index(self, name, args):
        ikiwa name kwenye self.whichindex:
            self.index(name, args)
        isipokua:
            andika('*** No index named', repr(name))

    eleza do_cindex(self, args): self.index('cp', args)
    eleza do_findex(self, args): self.index('fn', args)
    eleza do_kindex(self, args): self.index('ky', args)
    eleza do_pindex(self, args): self.index('pg', args)
    eleza do_tindex(self, args): self.index('tp', args)
    eleza do_vindex(self, args): self.index('vr', args)

    eleza index(self, name, args):
        self.whichindex[name].append((args, self.nodename))
        self.htmlhelp.index(args, self.nodename)

    eleza do_synindex(self, args):
        words = args.split()
        ikiwa len(words) != 2:
            andika('*** bad @synindex', args)
            rudisha
        [old, new] = words
        ikiwa old haiko kwenye self.whichindex ama \
                  new haiko kwenye self.whichindex:
            andika('*** bad key(s) kwenye @synindex', args)
            rudisha
        ikiwa old != new na \
                  self.whichindex[old] ni sio self.whichindex[new]:
            inew = self.whichindex[new]
            inew[len(inew):] = self.whichindex[old]
            self.whichindex[old] = inew
    do_syncodeindex = do_synindex # XXX Should use code font

    eleza do_printindex(self, args):
        words = args.split()
        kila name kwenye words:
            ikiwa name kwenye self.whichindex:
                self.prindex(name)
            isipokua:
                andika('*** No index named', repr(name))

    eleza prindex(self, name):
        iscodeindex = (name haiko kwenye self.noncodeindices)
        index = self.whichindex[name]
        ikiwa sio index: rudisha
        ikiwa self.debugging:
            andika('!'*self.debugging, '--- Generating', \
                  self.indextitle[name], 'index')
        #  The node already provides a title
        index1 = []
        junkprog = re.compile('^(@[a-z]+)?{')
        kila key, node kwenye index:
            sortkey = key.lower()
            # Remove leading `@cmd{' kutoka sort key
            # -- don't bother about the matching `}'
            oldsortkey = sortkey
            wakati 1:
                mo = junkprog.match(sortkey)
                ikiwa sio mo:
                    koma
                i = mo.end()
                sortkey = sortkey[i:]
            index1.append((sortkey, key, node))
        toa index[:]
        index1.sort()
        self.write('<DL COMPACT>\n')
        prevkey = prevnode = Tupu
        kila sortkey, key, node kwenye index1:
            ikiwa (key, node) == (prevkey, prevnode):
                endelea
            ikiwa self.debugging > 1: andika('!'*self.debugging, key, ':', node)
            self.write('<DT>')
            ikiwa iscodeindex: key = '@code{' + key + '}'
            ikiwa key != prevkey:
                self.expand(key)
            self.write('\n<DD><A HREF="%s">%s</A>\n' % (makefile(node), node))
            prevkey, prevnode = key, node
        self.write('</DL>\n')

    # --- Final error reports ---

    eleza report(self):
        ikiwa self.unknown:
            andika('--- Unrecognized commands ---')
            cmds = sorted(self.unknown.keys())
            kila cmd kwenye cmds:
                andika(cmd.ljust(20), self.unknown[cmd])


kundi TexinfoParserHTML3(TexinfoParser):

    COPYRIGHT_SYMBOL = "&copy;"
    FN_ID_PATTERN = "[%(id)s]"
    FN_SOURCE_PATTERN = '<A ID=footnoteref%(id)s ' \
                        'HREF="#footnotetext%(id)s">' + FN_ID_PATTERN + '</A>'
    FN_TARGET_PATTERN = '<FN ID=footnotetext%(id)s>\n' \
                        '<P><A HREF="#footnoteref%(id)s">' + FN_ID_PATTERN \
                        + '</A>\n%(text)s</P></FN>\n'
    FN_HEADER = '<DIV CLASS=footnotes>\n  <HR NOSHADE WIDTH=200>\n' \
                '  <STRONG><EM>Footnotes</EM></STRONG>\n  <P>\n'

    Node = HTML3Node

    eleza bgn_quotation(self, args): self.write('<BQ>')
    eleza end_quotation(self): self.write('</BQ>\n')

    eleza bgn_example(self, args):
        # this use of <CODE> would sio be legal kwenye HTML 2.0,
        # but ni kwenye more recent DTDs.
        self.nofill = self.nofill + 1
        self.write('<PRE CLASS=example><CODE>')
    eleza end_example(self):
        self.write("</CODE></PRE>\n")
        self.nofill = self.nofill - 1

    eleza bgn_flushleft(self, args):
        self.nofill = self.nofill + 1
        self.write('<PRE CLASS=flushleft>\n')

    eleza bgn_flushright(self, args):
        self.nofill = self.nofill + 1
        self.write('<DIV ALIGN=right CLASS=flushright><ADDRESS COMPACT>\n')
    eleza end_flushright(self):
        self.write('</ADDRESS></DIV>\n')
        self.nofill = self.nofill - 1

    eleza bgn_menu(self, args):
        self.write('<UL PLAIN CLASS=menu>\n')
        self.write('  <LH>Menu</LH>\n')
    eleza end_menu(self):
        self.write('</UL>\n')


# rpyron 2002-05-07
kundi HTMLHelp:
    """
    This kundi encapsulates support kila HTML Help. Node names,
    file names, menu items, index items, na image file names are
    accumulated until a call to finalize(). At that time, three
    output files are created kwenye the current directory:

        `helpbase`.hhp  ni a HTML Help Workshop project file.
                        It contains various information, some of
                        which I do sio understand; I just copied
                        the default project info kutoka a fresh
                        installation.
        `helpbase`.hhc  ni the Contents file kila the project.
        `helpbase`.hhk  ni the Index file kila the project.

    When these files are used kama input to HTML Help Workshop,
    the resulting file will be named:

        `helpbase`.chm

    If none of the defaults kwenye `helpbase`.hhp are changed,
    the .CHM file will have Contents, Index, Search, na
    Favorites tabs.
    """

    codeprog = re.compile('@code{(.*?)}')

    eleza __init__(self,helpbase,dirname):
        self.helpbase    = helpbase
        self.dirname     = dirname
        self.projectfile = Tupu
        self.contentfile = Tupu
        self.indexfile   = Tupu
        self.nodelist    = []
        self.nodenames   = {}         # nodename : index
        self.nodeindex   = {}
        self.filenames   = {}         # filename : filename
        self.indexlist   = []         # (args,nodename) == (key,location)
        self.current     = ''
        self.menudict    = {}
        self.dumped      = {}


    eleza addnode(self,name,next,prev,up,filename):
        node = (name,next,prev,up,filename)
        # add this file to dict
        # retrieve list ukijumuisha self.filenames.values()
        self.filenames[filename] = filename
        # add this node to nodelist
        self.nodeindex[name] = len(self.nodelist)
        self.nodelist.append(node)
        # set 'current' kila menu items
        self.current = name
        self.menudict[self.current] = []

    eleza menuitem(self,nodename):
        menu = self.menudict[self.current]
        menu.append(nodename)


    eleza addimage(self,imagename):
        self.filenames[imagename] = imagename

    eleza index(self, args, nodename):
        self.indexlist.append((args,nodename))

    eleza beginmenu(self):
        pita

    eleza endmenu(self):
        pita

    eleza finalize(self):
        ikiwa sio self.helpbase:
            rudisha

        # generate interesting filenames
        resultfile   = self.helpbase + '.chm'
        projectfile  = self.helpbase + '.hhp'
        contentfile  = self.helpbase + '.hhc'
        indexfile    = self.helpbase + '.hhk'

        # generate a reasonable title
        title        = self.helpbase

        # get the default topic file
        (topname,topnext,topprev,topup,topfile) = self.nodelist[0]
        defaulttopic = topfile

        # PROJECT FILE
        jaribu:
            ukijumuisha open(projectfile, 'w') kama fp:
                andika('[OPTIONS]', file=fp)
                andika('Auto Index=Yes', file=fp)
                andika('Binary TOC=No', file=fp)
                andika('Binary Index=Yes', file=fp)
                andika('Compatibility=1.1', file=fp)
                andika('Compiled file=' + resultfile + '', file=fp)
                andika('Contents file=' + contentfile + '', file=fp)
                andika('Default topic=' + defaulttopic + '', file=fp)
                andika('Error log file=ErrorLog.log', file=fp)
                andika('Index file=' + indexfile + '', file=fp)
                andika('Title=' + title + '', file=fp)
                andika('Display compile progress=Yes', file=fp)
                andika('Full-text search=Yes', file=fp)
                andika('Default window=main', file=fp)
                andika('', file=fp)
                andika('[WINDOWS]', file=fp)
                andika('main=,"' + contentfile + '","' + indexfile
                            + '","","",,,,,0x23520,222,0x1046,[10,10,780,560],'
                            '0xB0000,,,,,,0', file=fp)
                andika('', file=fp)
                andika('[FILES]', file=fp)
                andika('', file=fp)
                self.dumpfiles(fp)
        tatizo IOError kama msg:
            andika(projectfile, ':', msg)
            sys.exit(1)

        # CONTENT FILE
        jaribu:
            ukijumuisha open(contentfile, 'w') kama fp:
                andika('<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML//EN">', file=fp)
                andika('<!-- This file defines the table of contents -->', file=fp)
                andika('<HTML>', file=fp)
                andika('<HEAD>', file=fp)
                andika('<meta name="GENERATOR" '
                            'content="Microsoft&reg; HTML Help Workshop 4.1">', file=fp)
                andika('<!-- Sitemap 1.0 -->', file=fp)
                andika('</HEAD>', file=fp)
                andika('<BODY>', file=fp)
                andika('   <OBJECT type="text/site properties">', file=fp)
                andika('     <param name="Window Styles" value="0x800025">', file=fp)
                andika('     <param name="comment" value="title:">', file=fp)
                andika('     <param name="comment" value="base:">', file=fp)
                andika('   </OBJECT>', file=fp)
                self.dumpnodes(fp)
                andika('</BODY>', file=fp)
                andika('</HTML>', file=fp)
        tatizo IOError kama msg:
            andika(contentfile, ':', msg)
            sys.exit(1)

        # INDEX FILE
        jaribu:
            ukijumuisha open(indexfile, 'w') kama fp:
                andika('<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML//EN">', file=fp)
                andika('<!-- This file defines the index -->', file=fp)
                andika('<HTML>', file=fp)
                andika('<HEAD>', file=fp)
                andika('<meta name="GENERATOR" '
                            'content="Microsoft&reg; HTML Help Workshop 4.1">', file=fp)
                andika('<!-- Sitemap 1.0 -->', file=fp)
                andika('</HEAD>', file=fp)
                andika('<BODY>', file=fp)
                andika('<OBJECT type="text/site properties">', file=fp)
                andika('</OBJECT>', file=fp)
                self.dumpindex(fp)
                andika('</BODY>', file=fp)
                andika('</HTML>', file=fp)
        tatizo IOError kama msg:
            andika(indexfile  , ':', msg)
            sys.exit(1)

    eleza dumpfiles(self, outfile=sys.stdout):
        filelist = sorted(self.filenames.values())
        kila filename kwenye filelist:
            andika(filename, file=outfile)

    eleza dumpnodes(self, outfile=sys.stdout):
        self.dumped = {}
        ikiwa self.nodelist:
            nodename, dummy, dummy, dummy, dummy = self.nodelist[0]
            self.topnode = nodename

        andika('<UL>', file=outfile)
        kila node kwenye self.nodelist:
            self.dumpnode(node,0,outfile)
        andika('</UL>', file=outfile)

    eleza dumpnode(self, node, indent=0, outfile=sys.stdout):
        ikiwa node:
            # Retrieve info kila this node
            (nodename,next,prev,up,filename) = node
            self.current = nodename

            # Have we been dumped already?
            ikiwa nodename kwenye self.dumped:
                rudisha
            self.dumped[nodename] = 1

            # Print info kila this node
            andika(' '*indent, end=' ', file=outfile)
            andika('<LI><OBJECT type="text/sitemap">', end=' ', file=outfile)
            andika('<param name="Name" value="' + nodename +'">', end=' ', file=outfile)
            andika('<param name="Local" value="'+ filename +'">', end=' ', file=outfile)
            andika('</OBJECT>', file=outfile)

            # Does this node have menu items?
            jaribu:
                menu = self.menudict[nodename]
                self.dumpmenu(menu,indent+2,outfile)
            tatizo KeyError:
                pita

    eleza dumpmenu(self, menu, indent=0, outfile=sys.stdout):
        ikiwa menu:
            currentnode = self.current
            ikiwa currentnode != self.topnode:    # XXX this ni a hack
                andika(' '*indent + '<UL>', file=outfile)
                indent += 2
            kila item kwenye menu:
                menunode = self.getnode(item)
                self.dumpnode(menunode,indent,outfile)
            ikiwa currentnode != self.topnode:    # XXX this ni a hack
                andika(' '*indent + '</UL>', file=outfile)
                indent -= 2

    eleza getnode(self, nodename):
        jaribu:
            index = self.nodeindex[nodename]
            rudisha self.nodelist[index]
        tatizo KeyError:
            rudisha Tupu
        tatizo IndexError:
            rudisha Tupu

    # (args,nodename) == (key,location)
    eleza dumpindex(self, outfile=sys.stdout):
        andika('<UL>', file=outfile)
        kila (key,location) kwenye self.indexlist:
            key = self.codeexpand(key)
            location = makefile(location)
            location = self.dirname + '/' + location
            andika('<LI><OBJECT type="text/sitemap">', end=' ', file=outfile)
            andika('<param name="Name" value="' + key + '">', end=' ', file=outfile)
            andika('<param name="Local" value="' + location + '">', end=' ', file=outfile)
            andika('</OBJECT>', file=outfile)
        andika('</UL>', file=outfile)

    eleza codeexpand(self, line):
        co = self.codeprog.match(line)
        ikiwa sio co:
            rudisha line
        bgn, end = co.span(0)
        a, b = co.span(1)
        line = line[:bgn] + line[a:b] + line[end:]
        rudisha line


# Put @var{} around alphabetic substrings
eleza makevar(str):
    rudisha '@var{'+str+'}'


# Split a string kwenye "words" according to findwordend
eleza splitwords(str, minlength):
    words = []
    i = 0
    n = len(str)
    wakati i < n:
        wakati i < n na str[i] kwenye ' \t\n': i = i+1
        ikiwa i >= n: koma
        start = i
        i = findwordend(str, i, n)
        words.append(str[start:i])
    wakati len(words) < minlength: words.append('')
    rudisha words


# Find the end of a "word", matching braces na interpreting @@ @{ @}
fwprog = re.compile('[@{} ]')
eleza findwordend(str, i, n):
    level = 0
    wakati i < n:
        mo = fwprog.search(str, i)
        ikiwa sio mo:
            koma
        i = mo.start()
        c = str[i]; i = i+1
        ikiwa c == '@': i = i+1 # Next character ni sio special
        lasivyo c == '{': level = level+1
        lasivyo c == '}': level = level-1
        lasivyo c == ' ' na level <= 0: rudisha i-1
    rudisha n


# Convert a node name into a file name
eleza makefile(nodename):
    nodename = nodename.strip()
    rudisha fixfunnychars(nodename) + '.html'


# Characters that are perfectly safe kwenye filenames na hyperlinks
goodchars = string.ascii_letters + string.digits + '!@-=+.'

# Replace characters that aren't perfectly safe by dashes
# Underscores are bad since Cern HTTPD treats them kama delimiters for
# encoding times, so you get mismatches ikiwa you compress your files:
# a.html.gz will map to a_b.html.gz
eleza fixfunnychars(addr):
    i = 0
    wakati i < len(addr):
        c = addr[i]
        ikiwa c haiko kwenye goodchars:
            c = '-'
            addr = addr[:i] + c + addr[i+1:]
        i = i + len(c)
    rudisha addr


# Increment a string used kama an enumeration
eleza increment(s):
    ikiwa sio s:
        rudisha '1'
    kila sequence kwenye string.digits, string.ascii_lowercase, string.ascii_uppercase:
        lastc = s[-1]
        ikiwa lastc kwenye sequence:
            i = sequence.index(lastc) + 1
            ikiwa i >= len(sequence):
                ikiwa len(s) == 1:
                    s = sequence[0]*2
                    ikiwa s == '00':
                        s = '10'
                isipokua:
                    s = increment(s[:-1]) + sequence[0]
            isipokua:
                s = s[:-1] + sequence[i]
            rudisha s
    rudisha s # Don't increment


eleza test():
    agiza sys
    debugging = 0
    print_headers = 0
    cont = 0
    html3 = 0
    htmlhelp = ''

    wakati sys.argv[1] == ['-d']:
        debugging = debugging + 1
        toa sys.argv[1]
    ikiwa sys.argv[1] == '-p':
        print_headers = 1
        toa sys.argv[1]
    ikiwa sys.argv[1] == '-c':
        cont = 1
        toa sys.argv[1]
    ikiwa sys.argv[1] == '-3':
        html3 = 1
        toa sys.argv[1]
    ikiwa sys.argv[1] == '-H':
        helpbase = sys.argv[2]
        toa sys.argv[1:3]
    ikiwa len(sys.argv) != 3:
        andika('usage: texi2hh [-d [-d]] [-p] [-c] [-3] [-H htmlhelp]', \
              'inputfile outputdirectory')
        sys.exit(2)

    ikiwa html3:
        parser = TexinfoParserHTML3()
    isipokua:
        parser = TexinfoParser()
    parser.cont = cont
    parser.debugging = debugging
    parser.print_headers = print_headers

    file = sys.argv[1]
    dirname  = sys.argv[2]
    parser.setdirname(dirname)
    parser.setincludedir(os.path.dirname(file))

    htmlhelp = HTMLHelp(helpbase, dirname)
    parser.sethtmlhelp(htmlhelp)

    jaribu:
        fp = open(file, 'r')
    tatizo IOError kama msg:
        andika(file, ':', msg)
        sys.exit(1)

    ukijumuisha fp:
        parser.parse(fp)
    parser.report()

    htmlhelp.finalize()


ikiwa __name__ == "__main__":
    test()
