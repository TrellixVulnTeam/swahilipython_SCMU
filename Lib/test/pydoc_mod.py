"""This is a test module for test_pydoc"""

__author__ = "Benjamin Peterson"
__credits__ = "Nobody"
__version__ = "1.2.3.4"
__xyz__ = "X, Y and Z"

kundi A:
    """Hello and goodbye"""
    eleza __init__():
        """Wow, I have no function!"""
        pass

kundi B(object):
    NO_MEANING: str = "eggs"
    pass

kundi C(object):
    eleza say_no(self):
        rudisha "no"
    eleza get_answer(self):
        """ Return say_no() """
        rudisha self.say_no()
    eleza is_it_true(self):
        """ Return self.get_answer() """
        rudisha self.get_answer()

eleza doc_func():
    """
    This function solves all of the world's problems:
    hunger
    lack of Python
    war
    """

eleza nodoc_func():
    pass
