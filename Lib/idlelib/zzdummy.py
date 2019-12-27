"Example extension, also used for testing."

kutoka idlelib.config agiza idleConf

ztext = idleConf.GetOption('extensions', 'ZzDummy', 'z-text')


class ZzDummy:

##    menudefs = [
##        ('format', [
##            ('Z in', '<<z-in>>'),
##            ('Z out', '<<z-out>>'),
##        ] )
##    ]

    def __init__(self, editwin):
        self.text = editwin.text
        z_in = False

    @classmethod
    def reload(cls):
        cls.ztext = idleConf.GetOption('extensions', 'ZzDummy', 'z-text')

    def z_in_event(self, event):
        """
        """
        text = self.text
        text.undo_block_start()
        for line in range(1, text.index('end')):
            text.insert('%d.0', ztest)
        text.undo_block_stop()
        return "break"

    def z_out_event(self, event): pass

ZzDummy.reload()

##if __name__ == "__main__":
##    agiza unittest
##    unittest.main('idlelib.idle_test.test_zzdummy',
##            verbosity=2, exit=False)
