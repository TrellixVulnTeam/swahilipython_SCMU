# -*- Mode: Python; tab-width: 4 -*-
#       Id: asynchat.py,v 2.26 2000/09/07 22:29:26 rushing Exp
#       Author: Sam Rushing <rushing@nightmare.com>

# ======================================================================
# Copyright 1996 by Sam Rushing
#
#                         All Rights Reserved
#
# Permission to use, copy, modify, na distribute this software na
# its documentation kila any purpose na without fee ni hereby
# granted, provided that the above copyright notice appear kwenye all
# copies na that both that copyright notice na this permission
# notice appear kwenye supporting documentation, na that the name of Sam
# Rushing sio be used kwenye advertising ama publicity pertaining to
# distribution of the software without specific, written prior
# permission.
#
# SAM RUSHING DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE,
# INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS, IN
# NO EVENT SHALL SAM RUSHING BE LIABLE FOR ANY SPECIAL, INDIRECT OR
# CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS
# OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT,
# NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN
# CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
# ======================================================================

r"""A kundi supporting chat-style (command/response) protocols.

This kundi adds support kila 'chat' style protocols - where one side
sends a 'command', na the other sends a response (examples would be
the common internet protocols - smtp, nntp, ftp, etc..).

The handle_read() method looks at the input stream kila the current
'terminator' (usually '\r\n' kila single-line responses, '\r\n.\r\n'
kila multi-line output), calling self.found_terminator() on its
receipt.

kila example:
Say you build an async nntp client using this class.  At the start
of the connection, you'll have self.terminator set to '\r\n', in
order to process the single-line greeting.  Just before issuing a
'LIST' command you'll set it to '\r\n.\r\n'.  The output of the LIST
command will be accumulated (using your own 'collect_incoming_data'
method) up to the terminator, na then control will be returned to
you - by calling your self.found_terminator() method.
"""
agiza asyncore
kutoka collections agiza deque


kundi async_chat(asyncore.dispatcher):
    """This ni an abstract class.  You must derive kutoka this class, na add
    the two methods collect_incoming_data() na found_terminator()"""

    # these are overridable defaults

    ac_in_buffer_size = 65536
    ac_out_buffer_size = 65536

    # we don't want to enable the use of encoding by default, because that ni a
    # sign of an application bug that we don't want to pita silently

    use_encoding = 0
    encoding = 'latin-1'

    eleza __init__(self, sock=Tupu, map=Tupu):
        # kila string terminator matching
        self.ac_in_buffer = b''

        # we use a list here rather than io.BytesIO kila a few reasons...
        # toa lst[:] ni faster than bio.truncate(0)
        # lst = [] ni faster than bio.truncate(0)
        self.incoming = []

        # we toss the use of the "simple producer" na replace it with
        # a pure deque, which the original fifo was a wrapping of
        self.producer_fifo = deque()
        asyncore.dispatcher.__init__(self, sock, map)

    eleza collect_incoming_data(self, data):
        ashiria NotImplementedError("must be implemented kwenye subclass")

    eleza _collect_incoming_data(self, data):
        self.incoming.append(data)

    eleza _get_data(self):
        d = b''.join(self.incoming)
        toa self.incoming[:]
        rudisha d

    eleza found_terminator(self):
        ashiria NotImplementedError("must be implemented kwenye subclass")

    eleza set_terminator(self, term):
        """Set the input delimiter.

        Can be a fixed string of any length, an integer, ama Tupu.
        """
        ikiwa isinstance(term, str) na self.use_encoding:
            term = bytes(term, self.encoding)
        lasivyo isinstance(term, int) na term < 0:
            ashiria ValueError('the number of received bytes must be positive')
        self.terminator = term

    eleza get_terminator(self):
        rudisha self.terminator

    # grab some more data kutoka the socket,
    # throw it to the collector method,
    # check kila the terminator,
    # ikiwa found, transition to the next state.

    eleza handle_read(self):

        jaribu:
            data = self.recv(self.ac_in_buffer_size)
        tatizo BlockingIOError:
            rudisha
        tatizo OSError kama why:
            self.handle_error()
            rudisha

        ikiwa isinstance(data, str) na self.use_encoding:
            data = bytes(str, self.encoding)
        self.ac_in_buffer = self.ac_in_buffer + data

        # Continue to search kila self.terminator kwenye self.ac_in_buffer,
        # wakati calling self.collect_incoming_data.  The wakati loop
        # ni necessary because we might read several data+terminator
        # combos ukijumuisha a single recv(4096).

        wakati self.ac_in_buffer:
            lb = len(self.ac_in_buffer)
            terminator = self.get_terminator()
            ikiwa sio terminator:
                # no terminator, collect it all
                self.collect_incoming_data(self.ac_in_buffer)
                self.ac_in_buffer = b''
            lasivyo isinstance(terminator, int):
                # numeric terminator
                n = terminator
                ikiwa lb < n:
                    self.collect_incoming_data(self.ac_in_buffer)
                    self.ac_in_buffer = b''
                    self.terminator = self.terminator - lb
                isipokua:
                    self.collect_incoming_data(self.ac_in_buffer[:n])
                    self.ac_in_buffer = self.ac_in_buffer[n:]
                    self.terminator = 0
                    self.found_terminator()
            isipokua:
                # 3 cases:
                # 1) end of buffer matches terminator exactly:
                #    collect data, transition
                # 2) end of buffer matches some prefix:
                #    collect data to the prefix
                # 3) end of buffer does sio match any prefix:
                #    collect data
                terminator_len = len(terminator)
                index = self.ac_in_buffer.find(terminator)
                ikiwa index != -1:
                    # we found the terminator
                    ikiwa index > 0:
                        # don't bother reporting the empty string
                        # (source of subtle bugs)
                        self.collect_incoming_data(self.ac_in_buffer[:index])
                    self.ac_in_buffer = self.ac_in_buffer[index+terminator_len:]
                    # This does the Right Thing ikiwa the terminator
                    # ni changed here.
                    self.found_terminator()
                isipokua:
                    # check kila a prefix of the terminator
                    index = find_prefix_at_end(self.ac_in_buffer, terminator)
                    ikiwa index:
                        ikiwa index != lb:
                            # we found a prefix, collect up to the prefix
                            self.collect_incoming_data(self.ac_in_buffer[:-index])
                            self.ac_in_buffer = self.ac_in_buffer[-index:]
                        koma
                    isipokua:
                        # no prefix, collect it all
                        self.collect_incoming_data(self.ac_in_buffer)
                        self.ac_in_buffer = b''

    eleza handle_write(self):
        self.initiate_send()

    eleza handle_close(self):
        self.close()

    eleza push(self, data):
        ikiwa sio isinstance(data, (bytes, bytearray, memoryview)):
            ashiria TypeError('data argument must be byte-ish (%r)',
                            type(data))
        sabs = self.ac_out_buffer_size
        ikiwa len(data) > sabs:
            kila i kwenye range(0, len(data), sabs):
                self.producer_fifo.append(data[i:i+sabs])
        isipokua:
            self.producer_fifo.append(data)
        self.initiate_send()

    eleza push_with_producer(self, producer):
        self.producer_fifo.append(producer)
        self.initiate_send()

    eleza readable(self):
        "predicate kila inclusion kwenye the readable kila select()"
        # cannot use the old predicate, it violates the claim of the
        # set_terminator method.

        # rudisha (len(self.ac_in_buffer) <= self.ac_in_buffer_size)
        rudisha 1

    eleza writable(self):
        "predicate kila inclusion kwenye the writable kila select()"
        rudisha self.producer_fifo ama (sio self.connected)

    eleza close_when_done(self):
        "automatically close this channel once the outgoing queue ni empty"
        self.producer_fifo.append(Tupu)

    eleza initiate_send(self):
        wakati self.producer_fifo na self.connected:
            first = self.producer_fifo[0]
            # handle empty string/buffer ama Tupu entry
            ikiwa sio first:
                toa self.producer_fifo[0]
                ikiwa first ni Tupu:
                    self.handle_close()
                    rudisha

            # handle classic producer behavior
            obs = self.ac_out_buffer_size
            jaribu:
                data = first[:obs]
            tatizo TypeError:
                data = first.more()
                ikiwa data:
                    self.producer_fifo.appendleft(data)
                isipokua:
                    toa self.producer_fifo[0]
                endelea

            ikiwa isinstance(data, str) na self.use_encoding:
                data = bytes(data, self.encoding)

            # send the data
            jaribu:
                num_sent = self.send(data)
            tatizo OSError:
                self.handle_error()
                rudisha

            ikiwa num_sent:
                ikiwa num_sent < len(data) ama obs < len(first):
                    self.producer_fifo[0] = first[num_sent:]
                isipokua:
                    toa self.producer_fifo[0]
            # we tried to send some actual data
            rudisha

    eleza discard_buffers(self):
        # Emergencies only!
        self.ac_in_buffer = b''
        toa self.incoming[:]
        self.producer_fifo.clear()


kundi simple_producer:

    eleza __init__(self, data, buffer_size=512):
        self.data = data
        self.buffer_size = buffer_size

    eleza more(self):
        ikiwa len(self.data) > self.buffer_size:
            result = self.data[:self.buffer_size]
            self.data = self.data[self.buffer_size:]
            rudisha result
        isipokua:
            result = self.data
            self.data = b''
            rudisha result


# Given 'haystack', see ikiwa any prefix of 'needle' ni at its end.  This
# assumes an exact match has already been checked.  Return the number of
# characters matched.
# kila example:
# f_p_a_e("qwerty\r", "\r\n") => 1
# f_p_a_e("qwertydkjf", "\r\n") => 0
# f_p_a_e("qwerty\r\n", "\r\n") => <undefined>

# this could maybe be made faster ukijumuisha a computed regex?
# [answer: no; circa Python-2.0, Jan 2001]
# new python:   28961/s
# old python:   18307/s
# re:        12820/s
# regex:     14035/s

eleza find_prefix_at_end(haystack, needle):
    l = len(needle) - 1
    wakati l na sio haystack.endswith(needle[:l]):
        l -= 1
    rudisha l
