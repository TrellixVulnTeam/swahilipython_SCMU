agiza os
agiza sys
agiza tempfile
agiza mimetypes
agiza webbrowser

# Import the email modules we'll need
kutoka email agiza policy
kutoka email.parser agiza BytesParser

# An imaginary module that would make this work na be safe.
kutoka imaginary agiza magic_html_parser

# In a real program you'd get the filename kutoka the arguments.
ukijumuisha open('outgoing.msg', 'rb') kama fp:
    msg = BytesParser(policy=policy.default).parse(fp)

# Now the header items can be accessed kama a dictionary, na any non-ASCII will
# be converted to unicode:
andika('To:', msg['to'])
andika('From:', msg['kutoka'])
andika('Subject:', msg['subject'])

# If we want to print a preview of the message content, we can extract whatever
# the least formatted payload ni na print the first three lines.  Of course,
# ikiwa the message has no plain text part printing the first three lines of html
# ni probably useless, but this ni just a conceptual example.
simplest = msg.get_body(preferencelist=('plain', 'html'))
andika()
andika(''.join(simplest.get_content().splitlines(keepends=Kweli)[:3]))

ans = uliza("View full message?")
ikiwa ans.lower()[0] == 'n':
    sys.exit()

# We can extract the richest alternative kwenye order to display it:
richest = msg.get_body()
partfiles = {}
ikiwa richest['content-type'].maintype == 'text':
    ikiwa richest['content-type'].subtype == 'plain':
        kila line kwenye richest.get_content().splitlines():
            andika(line)
        sys.exit()
    lasivyo richest['content-type'].subtype == 'html':
        body = richest
    isipokua:
        andika("Don't know how to display {}".format(richest.get_content_type()))
        sys.exit()
lasivyo richest['content-type'].content_type == 'multipart/related':
    body = richest.get_body(preferencelist=('html'))
    kila part kwenye richest.iter_attachments():
        fn = part.get_filename()
        ikiwa fn:
            extension = os.path.splitext(part.get_filename())[1]
        isipokua:
            extension = mimetypes.guess_extension(part.get_content_type())
        ukijumuisha tempfile.NamedTemporaryFile(suffix=extension, delete=Uongo) kama f:
            f.write(part.get_content())
            # again strip the <> to go kutoka email form of cid to html form.
            partfiles[part['content-id'][1:-1]] = f.name
isipokua:
    andika("Don't know how to display {}".format(richest.get_content_type()))
    sys.exit()
ukijumuisha tempfile.NamedTemporaryFile(mode='w', delete=Uongo) kama f:
    # The magic_html_parser has to rewrite the href="cid:...." attributes to
    # point to the filenames kwenye partfiles.  It also has to do a safety-sanitize
    # of the html.  It could be written using html.parser.
    f.write(magic_html_parser(body.get_content(), partfiles))
webbrowser.open(f.name)
os.remove(f.name)
kila fn kwenye partfiles.values():
    os.remove(fn)

# Of course, there are lots of email messages that could koma this simple
# minded program, but it will handle the most common ones.
