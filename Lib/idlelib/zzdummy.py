"Example extension, also used kila testing."

kutoka idlelib.config agiza idleConf

ztext = idleConf.GetOption('extensions', 'ZzDummy', 'z-text')


kundi ZzDummy:

##    menudefs = [
##        ('format', [
##            ('Z in', '<<z-in>>'),
##            ('Z out', '<<z-out>>'),
##        ] )
##    ]

    eleza __init__(self, editwin):
        self.text = editwin.text
        z_in = Uongo

    @classmethod
    eleza reload(cls):
        cls.ztext = idleConf.GetOption('extensions', 'ZzDummy', 'z-text')

    eleza z_in_event(self, event):
        """
        """
        text = self.text
        text.undo_block_start()
        kila line kwenye range(1, text.index('end')):
            text.insert('%d.0', ztest)
        text.undo_block_stop()
        rudisha "koma"

    eleza z_out_event(self, event): pass

ZzDummy.reload()

##ikiwa __name__ == "__main__":
##    agiza unittest
##    unittest.main('idlelib.idle_test.test_zzdummy',
##            verbosity=2, exit=Uongo)
