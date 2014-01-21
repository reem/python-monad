"""
Infix hack from:
    http://code.activestate.com/recipes/384122/
"""
# pylint: disable=R0903


class Infix(object):
    """
    Infix decorator. For instance:

    >>> @Infix
    >>> def mult(x, y):
    ...    return x * y
    >>> 2 |mult| 4
    8
    >>> 2 <<mult>> 4
    8
    """
    def __init__(self, function):
        self.function = function

    def __ror__(self, other):
        return Infix(lambda x, self=self, other=other: self.function(other, x))

    def __or__(self, other):
        return self.function(other)

    def __rlshift__(self, other):
        return self.__or__(other)

    def __rshift__(self, other):
        return self.__ror__(other)

    def __call__(self, left, right):
        return self.function(left, right)
