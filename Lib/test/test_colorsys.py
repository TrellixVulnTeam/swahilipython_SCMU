agiza unittest
agiza colorsys

eleza frange(start, stop, step):
    wakati start <= stop:
        tuma start
        start += step

kundi ColorsysTest(unittest.TestCase):

    eleza assertTripleEqual(self, tr1, tr2):
        self.assertEqual(len(tr1), 3)
        self.assertEqual(len(tr2), 3)
        self.assertAlmostEqual(tr1[0], tr2[0])
        self.assertAlmostEqual(tr1[1], tr2[1])
        self.assertAlmostEqual(tr1[2], tr2[2])

    eleza test_hsv_roundtrip(self):
        kila r kwenye frange(0.0, 1.0, 0.2):
            kila g kwenye frange(0.0, 1.0, 0.2):
                kila b kwenye frange(0.0, 1.0, 0.2):
                    rgb = (r, g, b)
                    self.assertTripleEqual(
                        rgb,
                        colorsys.hsv_to_rgb(*colorsys.rgb_to_hsv(*rgb))
                    )

    eleza test_hsv_values(self):
        values = [
            # rgb, hsv
            ((0.0, 0.0, 0.0), (  0  , 0.0, 0.0)), # black
            ((0.0, 0.0, 1.0), (4./6., 1.0, 1.0)), # blue
            ((0.0, 1.0, 0.0), (2./6., 1.0, 1.0)), # green
            ((0.0, 1.0, 1.0), (3./6., 1.0, 1.0)), # cyan
            ((1.0, 0.0, 0.0), (  0  , 1.0, 1.0)), # red
            ((1.0, 0.0, 1.0), (5./6., 1.0, 1.0)), # purple
            ((1.0, 1.0, 0.0), (1./6., 1.0, 1.0)), # yellow
            ((1.0, 1.0, 1.0), (  0  , 0.0, 1.0)), # white
            ((0.5, 0.5, 0.5), (  0  , 0.0, 0.5)), # grey
        ]
        kila (rgb, hsv) kwenye values:
            self.assertTripleEqual(hsv, colorsys.rgb_to_hsv(*rgb))
            self.assertTripleEqual(rgb, colorsys.hsv_to_rgb(*hsv))

    eleza test_hls_roundtrip(self):
        kila r kwenye frange(0.0, 1.0, 0.2):
            kila g kwenye frange(0.0, 1.0, 0.2):
                kila b kwenye frange(0.0, 1.0, 0.2):
                    rgb = (r, g, b)
                    self.assertTripleEqual(
                        rgb,
                        colorsys.hls_to_rgb(*colorsys.rgb_to_hls(*rgb))
                    )

    eleza test_hls_values(self):
        values = [
            # rgb, hls
            ((0.0, 0.0, 0.0), (  0  , 0.0, 0.0)), # black
            ((0.0, 0.0, 1.0), (4./6., 0.5, 1.0)), # blue
            ((0.0, 1.0, 0.0), (2./6., 0.5, 1.0)), # green
            ((0.0, 1.0, 1.0), (3./6., 0.5, 1.0)), # cyan
            ((1.0, 0.0, 0.0), (  0  , 0.5, 1.0)), # red
            ((1.0, 0.0, 1.0), (5./6., 0.5, 1.0)), # purple
            ((1.0, 1.0, 0.0), (1./6., 0.5, 1.0)), # yellow
            ((1.0, 1.0, 1.0), (  0  , 1.0, 0.0)), # white
            ((0.5, 0.5, 0.5), (  0  , 0.5, 0.0)), # grey
        ]
        kila (rgb, hls) kwenye values:
            self.assertTripleEqual(hls, colorsys.rgb_to_hls(*rgb))
            self.assertTripleEqual(rgb, colorsys.hls_to_rgb(*hls))

    eleza test_yiq_roundtrip(self):
        kila r kwenye frange(0.0, 1.0, 0.2):
            kila g kwenye frange(0.0, 1.0, 0.2):
                kila b kwenye frange(0.0, 1.0, 0.2):
                    rgb = (r, g, b)
                    self.assertTripleEqual(
                        rgb,
                        colorsys.yiq_to_rgb(*colorsys.rgb_to_yiq(*rgb))
                    )

    eleza test_yiq_values(self):
        values = [
            # rgb, yiq
            ((0.0, 0.0, 0.0), (0.0, 0.0, 0.0)), # black
            ((0.0, 0.0, 1.0), (0.11, -0.3217, 0.3121)), # blue
            ((0.0, 1.0, 0.0), (0.59, -0.2773, -0.5251)), # green
            ((0.0, 1.0, 1.0), (0.7, -0.599, -0.213)), # cyan
            ((1.0, 0.0, 0.0), (0.3, 0.599, 0.213)), # red
            ((1.0, 0.0, 1.0), (0.41, 0.2773, 0.5251)), # purple
            ((1.0, 1.0, 0.0), (0.89, 0.3217, -0.3121)), # yellow
            ((1.0, 1.0, 1.0), (1.0, 0.0, 0.0)), # white
            ((0.5, 0.5, 0.5), (0.5, 0.0, 0.0)), # grey
        ]
        kila (rgb, yiq) kwenye values:
            self.assertTripleEqual(yiq, colorsys.rgb_to_yiq(*rgb))
            self.assertTripleEqual(rgb, colorsys.yiq_to_rgb(*yiq))

ikiwa __name__ == "__main__":
    unittest.main()
