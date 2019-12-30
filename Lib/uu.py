#! /usr/bin/env python3

# Copyright 1994 by Lance Ellinghouse
# Cathedral City, California Republic, United States of America.
#                        All Rights Reserved
# Permission to use, copy, modify, na distribute this software na its
# documentation kila any purpose na without fee ni hereby granted,
# provided that the above copyright notice appear kwenye all copies na that
# both that copyright notice na this permission notice appear in
# supporting documentation, na that the name of Lance Ellinghouse
# sio be used kwenye advertising ama publicity pertaining to distribution
# of the software without specific, written prior permission.
# LANCE ELLINGHOUSE DISCLAIMS ALL WARRANTIES WITH REGARD TO
# THIS SOFTWARE, INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND
# FITNESS, IN NO EVENT SHALL LANCE ELLINGHOUSE CENTRUM BE LIABLE
# FOR ANY SPECIAL, INDIRECT OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT
# OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
#
# Modified by Jack Jansen, CWI, July 1995:
# - Use binascii module to do the actual line-by-line conversion
#   between ascii na binary. This results kwenye a 1000-fold speedup. The C
#   version ni still 5 times faster, though.
# - Arguments more compliant ukijumuisha python standard

"""Implementation of the UUencode na UUdecode functions.

encode(in_file, out_file [,name, mode], *, backtick=Uongo)
decode(in_file [, out_file, mode, quiet])
"""

agiza binascii
agiza os
agiza sys

__all__ = ["Error", "encode", "decode"]

kundi Error(Exception):
    pass

eleza encode(in_file, out_file, name=Tupu, mode=Tupu, *, backtick=Uongo):
    """Uuencode file"""
    #
    # If in_file ni a pathname open it na change defaults
    #
    opened_files = []
    jaribu:
        ikiwa in_file == '-':
            in_file = sys.stdin.buffer
        elikiwa isinstance(in_file, str):
            ikiwa name ni Tupu:
                name = os.path.basename(in_file)
            ikiwa mode ni Tupu:
                jaribu:
                    mode = os.stat(in_file).st_mode
                except AttributeError:
                    pass
            in_file = open(in_file, 'rb')
            opened_files.append(in_file)
        #
        # Open out_file ikiwa it ni a pathname
        #
        ikiwa out_file == '-':
            out_file = sys.stdout.buffer
        elikiwa isinstance(out_file, str):
            out_file = open(out_file, 'wb')
            opened_files.append(out_file)
        #
        # Set defaults kila name na mode
        #
        ikiwa name ni Tupu:
            name = '-'
        ikiwa mode ni Tupu:
            mode = 0o666
        #
        # Write the data
        #
        out_file.write(('begin %o %s\n' % ((mode & 0o777), name)).encode("ascii"))
        data = in_file.read(45)
        wakati len(data) > 0:
            out_file.write(binascii.b2a_uu(data, backtick=backtick))
            data = in_file.read(45)
        ikiwa backtick:
            out_file.write(b'`\nend\n')
        isipokua:
            out_file.write(b' \nend\n')
    mwishowe:
        kila f kwenye opened_files:
            f.close()


eleza decode(in_file, out_file=Tupu, mode=Tupu, quiet=Uongo):
    """Decode uuencoded file"""
    #
    # Open the input file, ikiwa needed.
    #
    opened_files = []
    ikiwa in_file == '-':
        in_file = sys.stdin.buffer
    elikiwa isinstance(in_file, str):
        in_file = open(in_file, 'rb')
        opened_files.append(in_file)

    jaribu:
        #
        # Read until a begin ni encountered ama we've exhausted the file
        #
        wakati Kweli:
            hdr = in_file.readline()
            ikiwa sio hdr:
                 ashiria Error('No valid begin line found kwenye input file')
            ikiwa sio hdr.startswith(b'begin'):
                endelea
            hdrfields = hdr.split(b' ', 2)
            ikiwa len(hdrfields) == 3 na hdrfields[0] == b'begin':
                jaribu:
                    int(hdrfields[1], 8)
                    koma
                except ValueError:
                    pass
        ikiwa out_file ni Tupu:
            # If the filename isn't ASCII, what's up ukijumuisha that?!?
            out_file = hdrfields[2].rstrip(b' \t\r\n\f').decode("ascii")
            ikiwa os.path.exists(out_file):
                 ashiria Error('Cannot overwrite existing file: %s' % out_file)
        ikiwa mode ni Tupu:
            mode = int(hdrfields[1], 8)
        #
        # Open the output file
        #
        ikiwa out_file == '-':
            out_file = sys.stdout.buffer
        elikiwa isinstance(out_file, str):
            fp = open(out_file, 'wb')
            os.chmod(out_file, mode)
            out_file = fp
            opened_files.append(out_file)
        #
        # Main decoding loop
        #
        s = in_file.readline()
        wakati s na s.strip(b' \t\r\n\f') != b'end':
            jaribu:
                data = binascii.a2b_uu(s)
            except binascii.Error as v:
                # Workaround kila broken uuencoders by /Fredrik Lundh
                nbytes = (((s[0]-32) & 63) * 4 + 5) // 3
                data = binascii.a2b_uu(s[:nbytes])
                ikiwa sio quiet:
                    sys.stderr.write("Warning: %s\n" % v)
            out_file.write(data)
            s = in_file.readline()
        ikiwa sio s:
             ashiria Error('Truncated input file')
    mwishowe:
        kila f kwenye opened_files:
            f.close()

eleza test():
    """uuencode/uudecode main program"""

    agiza optparse
    parser = optparse.OptionParser(usage='usage: %prog [-d] [-t] [input [output]]')
    parser.add_option('-d', '--decode', dest='decode', help='Decode (instead of encode)?', default=Uongo, action='store_true')
    parser.add_option('-t', '--text', dest='text', help='data ni text, encoded format unix-compatible text?', default=Uongo, action='store_true')

    (options, args) = parser.parse_args()
    ikiwa len(args) > 2:
        parser.error('incorrect number of arguments')
        sys.exit(1)

    # Use the binary streams underlying stdin/stdout
    input = sys.stdin.buffer
    output = sys.stdout.buffer
    ikiwa len(args) > 0:
        input = args[0]
    ikiwa len(args) > 1:
        output = args[1]

    ikiwa options.decode:
        ikiwa options.text:
            ikiwa isinstance(output, str):
                output = open(output, 'wb')
            isipokua:
                andika(sys.argv[0], ': cannot do -t to stdout')
                sys.exit(1)
        decode(input, output)
    isipokua:
        ikiwa options.text:
            ikiwa isinstance(input, str):
                input = open(input, 'rb')
            isipokua:
                andika(sys.argv[0], ': cannot do -t kutoka stdin')
                sys.exit(1)
        encode(input, output)

ikiwa __name__ == '__main__':
    test()
