#!/usr/bin/env python3

"""Unpack a MIME message into a directory of files."""

agiza os
agiza email
agiza mimetypes

kutoka email.policy agiza default

kutoka argparse agiza ArgumentParser


eleza main():
    parser = ArgumentParser(description="""\
Unpack a MIME message into a directory of files.
""")
    parser.add_argument('-d', '--directory', required=Kweli,
                        help="""Unpack the MIME message into the named
                        directory, which will be created ikiwa it doesn't already
                        exist.""")
    parser.add_argument('msgfile')
    args = parser.parse_args()

    ukijumuisha open(args.msgfile, 'rb') kama fp:
        msg = email.message_kutoka_binary_file(fp, policy=default)

    jaribu:
        os.mkdir(args.directory)
    tatizo FileExistsError:
        pita

    counter = 1
    kila part kwenye msg.walk():
        # multipart/* are just containers
        ikiwa part.get_content_maintype() == 'multipart':
            endelea
        # Applications should really sanitize the given filename so that an
        # email message can't be used to overwrite agizaant files
        filename = part.get_filename()
        ikiwa sio filename:
            ext = mimetypes.guess_extension(part.get_content_type())
            ikiwa sio ext:
                # Use a generic bag-of-bits extension
                ext = '.bin'
            filename = 'part-%03d%s' % (counter, ext)
        counter += 1
        ukijumuisha open(os.path.join(args.directory, filename), 'wb') kama fp:
            fp.write(part.get_payload(decode=Kweli))


ikiwa __name__ == '__main__':
    main()
