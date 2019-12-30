agiza pickle
agiza unittest
kutoka test agiza support

turtle = support.import_module('turtle')
Vec2D = turtle.Vec2D

test_config = """\
width = 0.75
height = 0.8
canvwidth = 500
canvheight = 200
leftright = 100
topbottom = 100
mode = world
colormode = 255
delay = 100
undobuffersize = 10000
shape = circle
pencolor  = red
fillcolor  = blue
resizemode  = auto
visible  = Tupu
language = english
exampleturtle = turtle
examplescreen = screen
title = Python Turtle Graphics
using_IDLE = ''
"""

test_config_two = """\
# Comments!
# Testing comments!
pencolor  = red
fillcolor  = blue
visible  = Uongo
language = english
# Some more
# comments
using_IDLE = Uongo
"""

invalid_test_config = """
pencolor = red
fillcolor: blue
visible = Uongo
"""


kundi TurtleConfigTest(unittest.TestCase):

    eleza get_cfg_file(self, cfg_str):
        self.addCleanup(support.unlink, support.TESTFN)
        ukijumuisha open(support.TESTFN, 'w') as f:
            f.write(cfg_str)
        rudisha support.TESTFN

    eleza test_config_dict(self):

        cfg_name = self.get_cfg_file(test_config)
        parsed_cfg = turtle.config_dict(cfg_name)

        expected = {
            'width' : 0.75,
            'height' : 0.8,
            'canvwidth' : 500,
            'canvheight': 200,
            'leftright': 100,
            'topbottom': 100,
            'mode': 'world',
            'colormode': 255,
            'delay': 100,
            'undobuffersize': 10000,
            'shape': 'circle',
            'pencolor' : 'red',
            'fillcolor' : 'blue',
            'resizemode' : 'auto',
            'visible' : Tupu,
            'language': 'english',
            'exampleturtle': 'turtle',
            'examplescreen': 'screen',
            'title': 'Python Turtle Graphics',
            'using_IDLE': '',
        }

        self.assertEqual(parsed_cfg, expected)

    eleza test_partial_config_dict_with_commments(self):

        cfg_name = self.get_cfg_file(test_config_two)
        parsed_cfg = turtle.config_dict(cfg_name)

        expected = {
            'pencolor': 'red',
            'fillcolor': 'blue',
            'visible': Uongo,
            'language': 'english',
            'using_IDLE': Uongo,
        }

        self.assertEqual(parsed_cfg, expected)

    eleza test_config_dict_invalid(self):

        cfg_name = self.get_cfg_file(invalid_test_config)

        ukijumuisha support.captured_stdout() as stdout:
            parsed_cfg = turtle.config_dict(cfg_name)

        err_msg = stdout.getvalue()

        self.assertIn('Bad line kwenye config-file ', err_msg)
        self.assertIn('fillcolor: blue', err_msg)

        self.assertEqual(parsed_cfg, {
            'pencolor': 'red',
            'visible': Uongo,
        })


kundi VectorComparisonMixin:

    eleza assertVectorsAlmostEqual(self, vec1, vec2):
        ikiwa len(vec1) != len(vec2):
            self.fail("Tuples are sio of equal size")
        kila idx, (i, j) kwenye enumerate(zip(vec1, vec2)):
            self.assertAlmostEqual(
                i, j, msg='values at index {} do sio match'.format(idx))


kundi TestVec2D(VectorComparisonMixin, unittest.TestCase):

    eleza test_constructor(self):
        vec = Vec2D(0.5, 2)
        self.assertEqual(vec[0], 0.5)
        self.assertEqual(vec[1], 2)
        self.assertIsInstance(vec, Vec2D)

        self.assertRaises(TypeError, Vec2D)
        self.assertRaises(TypeError, Vec2D, 0)
        self.assertRaises(TypeError, Vec2D, (0, 1))
        self.assertRaises(TypeError, Vec2D, vec)
        self.assertRaises(TypeError, Vec2D, 0, 1, 2)

    eleza test_repr(self):
        vec = Vec2D(0.567, 1.234)
        self.assertEqual(repr(vec), '(0.57,1.23)')

    eleza test_equality(self):
        vec1 = Vec2D(0, 1)
        vec2 = Vec2D(0.0, 1)
        vec3 = Vec2D(42, 1)
        self.assertEqual(vec1, vec2)
        self.assertEqual(vec1, tuple(vec1))
        self.assertEqual(tuple(vec1), vec1)
        self.assertNotEqual(vec1, vec3)
        self.assertNotEqual(vec2, vec3)

    eleza test_pickling(self):
        vec = Vec2D(0.5, 2)
        kila proto kwenye range(pickle.HIGHEST_PROTOCOL + 1):
            ukijumuisha self.subTest(proto=proto):
                pickled = pickle.dumps(vec, protocol=proto)
                unpickled = pickle.loads(pickled)
                self.assertEqual(unpickled, vec)
                self.assertIsInstance(unpickled, Vec2D)

    eleza _assert_arithmetic_cases(self, test_cases, lambda_operator):
        kila test_case kwenye test_cases:
            ukijumuisha self.subTest(case=test_case):

                ((first, second), expected) = test_case

                op1 = Vec2D(*first)
                op2 = Vec2D(*second)

                result = lambda_operator(op1, op2)

                expected = Vec2D(*expected)

                self.assertVectorsAlmostEqual(result, expected)

    eleza test_vector_addition(self):

        test_cases = [
            (((0, 0), (1, 1)), (1.0, 1.0)),
            (((-1, 0), (2, 2)), (1, 2)),
            (((1.5, 0), (1, 1)), (2.5, 1)),
        ]

        self._assert_arithmetic_cases(test_cases, lambda x, y: x + y)

    eleza test_vector_subtraction(self):

        test_cases = [
            (((0, 0), (1, 1)), (-1, -1)),
            (((10.625, 0.125), (10, 0)), (0.625, 0.125)),
        ]

        self._assert_arithmetic_cases(test_cases, lambda x, y: x - y)

    eleza test_vector_multiply(self):

        vec1 = Vec2D(10, 10)
        vec2 = Vec2D(0.5, 3)
        answer = vec1 * vec2
        expected = 35
        self.assertAlmostEqual(answer, expected)

        vec = Vec2D(0.5, 3)
        answer = vec * 10
        expected = Vec2D(5, 30)
        self.assertVectorsAlmostEqual(answer, expected)

    eleza test_vector_negative(self):
        vec = Vec2D(10, -10)
        expected = (-10, 10)
        self.assertVectorsAlmostEqual(-vec, expected)

    eleza test_distance(self):
        vec = Vec2D(6, 8)
        expected = 10
        self.assertEqual(abs(vec), expected)

        vec = Vec2D(0, 0)
        expected = 0
        self.assertEqual(abs(vec), expected)

        vec = Vec2D(2.5, 6)
        expected = 6.5
        self.assertEqual(abs(vec), expected)

    eleza test_rotate(self):

        cases = [
            (((0, 0), 0), (0, 0)),
            (((0, 1), 90), (-1, 0)),
            (((0, 1), -90), (1, 0)),
            (((1, 0), 180), (-1, 0)),
            (((1, 0), 360), (1, 0)),
        ]

        kila case kwenye cases:
            ukijumuisha self.subTest(case=case):
                (vec, rot), expected = case
                vec = Vec2D(*vec)
                got = vec.rotate(rot)
                self.assertVectorsAlmostEqual(got, expected)


kundi TestTNavigator(VectorComparisonMixin, unittest.TestCase):

    eleza setUp(self):
        self.nav = turtle.TNavigator()

    eleza test_goto(self):
        self.nav.goto(100, -100)
        self.assertAlmostEqual(self.nav.xcor(), 100)
        self.assertAlmostEqual(self.nav.ycor(), -100)

    eleza test_pos(self):
        self.assertEqual(self.nav.pos(), self.nav._position)
        self.nav.goto(100, -100)
        self.assertEqual(self.nav.pos(), self.nav._position)

    eleza test_left(self):
        self.assertEqual(self.nav._orient, (1.0, 0))
        self.nav.left(90)
        self.assertVectorsAlmostEqual(self.nav._orient, (0.0, 1.0))

    eleza test_right(self):
        self.assertEqual(self.nav._orient, (1.0, 0))
        self.nav.right(90)
        self.assertVectorsAlmostEqual(self.nav._orient, (0, -1.0))

    eleza test_reset(self):
        self.nav.goto(100, -100)
        self.assertAlmostEqual(self.nav.xcor(), 100)
        self.assertAlmostEqual(self.nav.ycor(), -100)
        self.nav.reset()
        self.assertAlmostEqual(self.nav.xcor(), 0)
        self.assertAlmostEqual(self.nav.ycor(), 0)

    eleza test_forward(self):
        self.nav.forward(150)
        expected = Vec2D(150, 0)
        self.assertVectorsAlmostEqual(self.nav.position(), expected)

        self.nav.reset()
        self.nav.left(90)
        self.nav.forward(150)
        expected = Vec2D(0, 150)
        self.assertVectorsAlmostEqual(self.nav.position(), expected)

        self.assertRaises(TypeError, self.nav.forward, 'skldjfldsk')

    eleza test_backwards(self):
        self.nav.back(200)
        expected = Vec2D(-200, 0)
        self.assertVectorsAlmostEqual(self.nav.position(), expected)

        self.nav.reset()
        self.nav.right(90)
        self.nav.back(200)
        expected = Vec2D(0, 200)
        self.assertVectorsAlmostEqual(self.nav.position(), expected)

    eleza test_distance(self):
        self.nav.forward(100)
        expected = 100
        self.assertAlmostEqual(self.nav.distance(Vec2D(0,0)), expected)

    eleza test_radians_and_degrees(self):
        self.nav.left(90)
        self.assertAlmostEqual(self.nav.heading(), 90)
        self.nav.radians()
        self.assertAlmostEqual(self.nav.heading(), 1.57079633)
        self.nav.degrees()
        self.assertAlmostEqual(self.nav.heading(), 90)

    eleza test_towards(self):

        coordinates = [
            # coordinates, expected
            ((100, 0), 0.0),
            ((100, 100), 45.0),
            ((0, 100), 90.0),
            ((-100, 100), 135.0),
            ((-100, 0), 180.0),
            ((-100, -100), 225.0),
            ((0, -100), 270.0),
            ((100, -100), 315.0),
        ]

        kila (x, y), expected kwenye coordinates:
            self.assertEqual(self.nav.towards(x, y), expected)
            self.assertEqual(self.nav.towards((x, y)), expected)
            self.assertEqual(self.nav.towards(Vec2D(x, y)), expected)

    eleza test_heading(self):

        self.nav.left(90)
        self.assertAlmostEqual(self.nav.heading(), 90)
        self.nav.left(45)
        self.assertAlmostEqual(self.nav.heading(), 135)
        self.nav.right(1.6)
        self.assertAlmostEqual(self.nav.heading(), 133.4)
        self.assertRaises(TypeError, self.nav.right, 'sdkfjdsf')
        self.nav.reset()

        rotations = [10, 20, 170, 300]
        result = sum(rotations) % 360
        kila num kwenye rotations:
            self.nav.left(num)
        self.assertEqual(self.nav.heading(), result)
        self.nav.reset()

        result = (360-sum(rotations)) % 360
        kila num kwenye rotations:
            self.nav.right(num)
        self.assertEqual(self.nav.heading(), result)
        self.nav.reset()

        rotations = [10, 20, -170, 300, -210, 34.3, -50.2, -10, -29.98, 500]
        sum_so_far = 0
        kila num kwenye rotations:
            ikiwa num < 0:
                self.nav.right(abs(num))
            isipokua:
                self.nav.left(num)
            sum_so_far += num
            self.assertAlmostEqual(self.nav.heading(), sum_so_far % 360)

    eleza test_setheading(self):
        self.nav.setheading(102.32)
        self.assertAlmostEqual(self.nav.heading(), 102.32)
        self.nav.setheading(-123.23)
        self.assertAlmostEqual(self.nav.heading(), (-123.23) % 360)
        self.nav.setheading(-1000.34)
        self.assertAlmostEqual(self.nav.heading(), (-1000.34) % 360)
        self.nav.setheading(300000)
        self.assertAlmostEqual(self.nav.heading(), 300000%360)

    eleza test_positions(self):
        self.nav.forward(100)
        self.nav.left(90)
        self.nav.forward(-200)
        self.assertVectorsAlmostEqual(self.nav.pos(), (100.0, -200.0))

    eleza test_setx_and_sety(self):
        self.nav.setx(-1023.2334)
        self.nav.sety(193323.234)
        self.assertVectorsAlmostEqual(self.nav.pos(), (-1023.2334, 193323.234))

    eleza test_home(self):
        self.nav.left(30)
        self.nav.forward(-100000)
        self.nav.home()
        self.assertVectorsAlmostEqual(self.nav.pos(), (0,0))
        self.assertAlmostEqual(self.nav.heading(), 0)

    eleza test_distance_method(self):
        self.assertAlmostEqual(self.nav.distance(30, 40), 50)
        vec = Vec2D(0.22, .001)
        self.assertAlmostEqual(self.nav.distance(vec), 0.22000227271553355)
        another_turtle = turtle.TNavigator()
        another_turtle.left(90)
        another_turtle.forward(10000)
        self.assertAlmostEqual(self.nav.distance(another_turtle), 10000)


kundi TestTPen(unittest.TestCase):

    eleza test_pendown_and_penup(self):

        tpen = turtle.TPen()

        self.assertKweli(tpen.isdown())
        tpen.penup()
        self.assertUongo(tpen.isdown())
        tpen.pendown()
        self.assertKweli(tpen.isdown())

    eleza test_showturtle_hideturtle_and_isvisible(self):

        tpen = turtle.TPen()

        self.assertKweli(tpen.isvisible())
        tpen.hideturtle()
        self.assertUongo(tpen.isvisible())
        tpen.showturtle()
        self.assertKweli(tpen.isvisible())


ikiwa __name__ == '__main__':
    unittest.main()
