"""
Jonathan Reem
January 2014

Functional programming utility functions.
"""
# pylint: disable=C0103, W0142, W0622

from infix import Infix
from collections import namedtuple

Unit = namedtuple("Unit", "")

def curry(func, args):
    "Curries a function."
    return lambda *a: func(args + a)

def const(first, _):
    "const from the functional paradigm"
    return first

def id(x):
    "id from the functional paradigm"
    return x

def flip(func):
    "Flips function arguments."
    return lambda a, b: func(b, a)

def foldl(helper, acc, itr):
    "foldl from Haskell Prelude, but optimized to a loop."
    return reduce(helper, itr, acc)

def foldr(helper, acc, itr):
    "foldr from Haskell Prelude, but optimized to a loop."
    return foldl(lambda x, y: helper(y, x), acc, list(reversed(itr)))

def replicate(item, replications):
    "replicate from the Haskell Prelude"
    return [item for _ in xrange(replications)]

c = Infix(curry)
c.__doc__ = "infix version of curry"

def unzip(pair_list):
    "Undoes zip."
    return zip(*pair_list)

def zip_with(function, lefts, rights):
    "Generalize zip to non-tuple functions."
    return [function(left, right) for left, right in zip(lefts, rights)]
