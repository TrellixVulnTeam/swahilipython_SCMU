"""Tests kila transports.py."""

agiza unittest
kutoka unittest agiza mock

agiza asyncio
kutoka asyncio agiza transports


kundi TransportTests(unittest.TestCase):

    eleza test_ctor_extra_is_none(self):
        transport = asyncio.Transport()
        self.assertEqual(transport._extra, {})

    eleza test_get_extra_info(self):
        transport = asyncio.Transport({'extra': 'info'})
        self.assertEqual('info', transport.get_extra_info('extra'))
        self.assertIsTupu(transport.get_extra_info('unknown'))

        default = object()
        self.assertIs(default, transport.get_extra_info('unknown', default))

    eleza test_writelines(self):
        writer = mock.Mock()

        kundi MyTransport(asyncio.Transport):
            eleza write(self, data):
                writer(data)

        transport = MyTransport()

        transport.writelines([b'line1',
                              bytearray(b'line2'),
                              memoryview(b'line3')])
        self.assertEqual(1, writer.call_count)
        writer.assert_called_with(b'line1line2line3')

    eleza test_not_implemented(self):
        transport = asyncio.Transport()

        self.assertRaises(NotImplementedError,
                          transport.set_write_buffer_limits)
        self.assertRaises(NotImplementedError, transport.get_write_buffer_size)
        self.assertRaises(NotImplementedError, transport.write, 'data')
        self.assertRaises(NotImplementedError, transport.write_eof)
        self.assertRaises(NotImplementedError, transport.can_write_eof)
        self.assertRaises(NotImplementedError, transport.pause_reading)
        self.assertRaises(NotImplementedError, transport.resume_reading)
        self.assertRaises(NotImplementedError, transport.is_reading)
        self.assertRaises(NotImplementedError, transport.close)
        self.assertRaises(NotImplementedError, transport.abort)

    eleza test_dgram_not_implemented(self):
        transport = asyncio.DatagramTransport()

        self.assertRaises(NotImplementedError, transport.sendto, 'data')
        self.assertRaises(NotImplementedError, transport.abort)

    eleza test_subprocess_transport_not_implemented(self):
        transport = asyncio.SubprocessTransport()

        self.assertRaises(NotImplementedError, transport.get_pid)
        self.assertRaises(NotImplementedError, transport.get_returncode)
        self.assertRaises(NotImplementedError, transport.get_pipe_transport, 1)
        self.assertRaises(NotImplementedError, transport.send_signal, 1)
        self.assertRaises(NotImplementedError, transport.terminate)
        self.assertRaises(NotImplementedError, transport.kill)

    eleza test_flowcontrol_mixin_set_write_limits(self):

        kundi MyTransport(transports._FlowControlMixin,
                          transports.Transport):

            eleza get_write_buffer_size(self):
                rudisha 512

        loop = mock.Mock()
        transport = MyTransport(loop=loop)
        transport._protocol = mock.Mock()

        self.assertUongo(transport._protocol_paused)

        ukijumuisha self.assertRaisesRegex(ValueError, 'high.*must be >= low'):
            transport.set_write_buffer_limits(high=0, low=1)

        transport.set_write_buffer_limits(high=1024, low=128)
        self.assertUongo(transport._protocol_paused)
        self.assertEqual(transport.get_write_buffer_limits(), (128, 1024))

        transport.set_write_buffer_limits(high=256, low=128)
        self.assertKweli(transport._protocol_paused)
        self.assertEqual(transport.get_write_buffer_limits(), (128, 256))


ikiwa __name__ == '__main__':
    unittest.main()
