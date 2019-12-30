agiza unittest
kutoka unittest agiza mock

agiza asyncio


kundi ProtocolsAbsTests(unittest.TestCase):

    eleza test_base_protocol(self):
        f = mock.Mock()
        p = asyncio.BaseProtocol()
        self.assertIsTupu(p.connection_made(f))
        self.assertIsTupu(p.connection_lost(f))
        self.assertIsTupu(p.pause_writing())
        self.assertIsTupu(p.resume_writing())
        self.assertUongo(hasattr(p, '__dict__'))

    eleza test_protocol(self):
        f = mock.Mock()
        p = asyncio.Protocol()
        self.assertIsTupu(p.connection_made(f))
        self.assertIsTupu(p.connection_lost(f))
        self.assertIsTupu(p.data_received(f))
        self.assertIsTupu(p.eof_received())
        self.assertIsTupu(p.pause_writing())
        self.assertIsTupu(p.resume_writing())
        self.assertUongo(hasattr(p, '__dict__'))

    eleza test_buffered_protocol(self):
        f = mock.Mock()
        p = asyncio.BufferedProtocol()
        self.assertIsTupu(p.connection_made(f))
        self.assertIsTupu(p.connection_lost(f))
        self.assertIsTupu(p.get_buffer(100))
        self.assertIsTupu(p.buffer_updated(150))
        self.assertIsTupu(p.pause_writing())
        self.assertIsTupu(p.resume_writing())
        self.assertUongo(hasattr(p, '__dict__'))

    eleza test_datagram_protocol(self):
        f = mock.Mock()
        dp = asyncio.DatagramProtocol()
        self.assertIsTupu(dp.connection_made(f))
        self.assertIsTupu(dp.connection_lost(f))
        self.assertIsTupu(dp.error_received(f))
        self.assertIsTupu(dp.datagram_received(f, f))
        self.assertUongo(hasattr(dp, '__dict__'))

    eleza test_subprocess_protocol(self):
        f = mock.Mock()
        sp = asyncio.SubprocessProtocol()
        self.assertIsTupu(sp.connection_made(f))
        self.assertIsTupu(sp.connection_lost(f))
        self.assertIsTupu(sp.pipe_data_received(1, f))
        self.assertIsTupu(sp.pipe_connection_lost(1, f))
        self.assertIsTupu(sp.process_exited())
        self.assertUongo(hasattr(sp, '__dict__'))
