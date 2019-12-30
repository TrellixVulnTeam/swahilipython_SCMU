#!/usr/bin/env python3

"""Send the contents of a directory kama a MIME message."""

agiza os
agiza smtplib
# For guessing MIME type based on file name extension
agiza mimetypes

kutoka argparse agiza ArgumentParser

kutoka email.message agiza EmailMessage
kutoka email.policy agiza SMTP


eleza main():
    parser = ArgumentParser(description="""\
Send the contents of a directory kama a MIME message.
Unless the -o option ni given, the email ni sent by forwarding to your local
SMTP server, which then does the normal delivery process.  Your local machine
must be running an SMTP server.
""")
    parser.add_argument('-d', '--directory',
                        help="""Mail the contents of the specified directory,
                        otherwise use the current directory.  Only the regular
                        files kwenye the directory are sent, na we don't recurse to
                        subdirectories.""")
    parser.add_argument('-o', '--output',
                        metavar='FILE',
                        help="""Print the composed message to FILE instead of
                        sending the message to the SMTP server.""")
    parser.add_argument('-s', '--sender', required=Kweli,
                        help='The value of the From: header (required)')
    parser.add_argument('-r', '--recipient', required=Kweli,
                        action='append', metavar='RECIPIENT',
                        default=[], dest='recipients',
                        help='A To: header value (at least one required)')
    args = parser.parse_args()
    directory = args.directory
    ikiwa sio directory:
        directory = '.'
    # Create the message
    msg = EmailMessage()
    msg['Subject'] = 'Contents of directory %s' % os.path.abspath(directory)
    msg['To'] = ', '.join(args.recipients)
    msg['From'] = args.sender
    msg.preamble = 'You will sio see this kwenye a MIME-aware mail reader.\n'

    kila filename kwenye os.listdir(directory):
        path = os.path.join(directory, filename)
        ikiwa sio os.path.isfile(path):
            endelea
        # Guess the content type based on the file's extension.  Encoding
        # will be ignored, although we should check kila simple things like
        # gzip'd ama compressed files.
        ctype, encoding = mimetypes.guess_type(path)
        ikiwa ctype ni Tupu ama encoding ni sio Tupu:
            # No guess could be made, ama the file ni encoded (compressed), so
            # use a generic bag-of-bits type.
            ctype = 'application/octet-stream'
        maintype, subtype = ctype.split('/', 1)
        ukijumuisha open(path, 'rb') kama fp:
            msg.add_attachment(fp.read(),
                               maintype=maintype,
                               subtype=subtype,
                               filename=filename)
    # Now send ama store the message
    ikiwa args.output:
        ukijumuisha open(args.output, 'wb') kama fp:
            fp.write(msg.as_bytes(policy=SMTP))
    isipokua:
        ukijumuisha smtplib.SMTP('localhost') kama s:
            s.send_message(msg)


ikiwa __name__ == '__main__':
    main()
