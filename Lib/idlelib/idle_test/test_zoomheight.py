"Test zoomheight, coverage 66%."
# Some code is system dependent.

kutoka idlelib agiza zoomheight
agiza unittest
kutoka test.support agiza requires
kutoka tkinter agiza Tk
kutoka idlelib.editor agiza EditorWindow


kundi Test(unittest.TestCase):

    @classmethod
    eleza setUpClass(cls):
        requires('gui')
        cls.root = Tk()
        cls.root.withdraw()
        cls.editwin = EditorWindow(root=cls.root)

    @classmethod
    eleza tearDownClass(cls):
        cls.editwin._close()
        cls.root.update_idletasks()
        for id in cls.root.tk.call('after', 'info'):
            cls.root.after_cancel(id)  # Need for EditorWindow.
        cls.root.destroy()
        del cls.root

    eleza test_init(self):
        zoom = zoomheight.ZoomHeight(self.editwin)
        self.assertIs(zoom.editwin, self.editwin)

    eleza test_zoom_height_event(self):
        zoom = zoomheight.ZoomHeight(self.editwin)
        zoom.zoom_height_event()


ikiwa __name__ == '__main__':
    unittest.main(verbosity=2)
