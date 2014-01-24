"""
Jonathan Reem

Implementation of Monads from Haskell in Python as a "copy" of
Control.Monad from the GHC libraries.

docstrings of functions heavily influenced by Control.Monad
"""

# pylint: disable=C0322, C0103, R0921, R0922, W0141, W0142
import func
import infix


def monadize(monad):
    "Decorator for creating a monad."
    monad.then = lambda s, se: s >= (lambda a: se)
    monad.__ge__ = monad.bind                 # >= is Haskell's >>=
    monad.__lshift__ = func.flip(monad.bind)  # << is Haskell's =<<
    monad.__rshift__ = monad.then             # >> is Haskell's >>
    return monad


@monadize
class Monad(object):

    """
    Monad operators should have the following types:
        bind      :: Monad(a) -> (a -> Monad(b)) -> Monad(b)
        then      :: Monad(a) -> Monad(b)        -> Monad(b)
        return_m  :: a        -> Monad(a)

    Monad laws:
        return_m(a) >= f == f(a)                        --  Left Identity
        m >= return_m    == m                           --  Right Identity
        (m >= f) >= g    == m >= (lambda x: f(x) >= g)  --  Associativity

        For further info on Monad Laws, see:
            http://www.haskell.org/haskellwiki/Monad_law

    Using the |mcompl| and |mcompr| operators, we can write the
    Monad Laws in a way that might be a bit clearer:
        return_m |mcompr| g       == g
        f |mcompr| return_m       == f
        (f |mcompr| g) |mcompr| h == f |mcompr| (g |mcompr| h)

    If these laws are satisfied, then the Monad forms a mathematical category
    from Category theory, which makes lots of things convenient.
    """

    def bind(self, bindee):
        "Equivalent to Haskell's >>="
        raise NotImplementedError(
            "Your Monad must define its own bind.")

    @classmethod
    def return_m(cls, value):
        "Equivalent to Haskell's return"
        raise NotImplementedError(
            "Your monad must implement return_m.")


class MonadPlus(object):  # Monad

    """
    MonadPlus laws:
        mzero >= f == mzero
        v >> mzero == mzero
    """
    @classmethod
    def mzero(cls):
        "The mzero value."
        raise NotImplementedError("mzero must be defined.")

    def mplus(self, other):
        """An associative combined operation."""
        raise NotImplementedError


def sequence(monad_t, monad_list):
    """Evaluates each action in sequence from left to right and
    collects the results."""
    def helper(monad, acc):
        "Helper for sequence."
        return monad >= (lambda x:
              (acc >= (lambda xs:
              (monad_t.return_m(xs + [x])))))

    return func.foldr(helper, monad_t.return_m([]), list(reversed(monad_list)))


def sequence_(monad_t, monad_list):
    """Evaluates each action in sequence from
    left to right and dumps the results."""
    return func.foldr(monad_t.then, monad_t.return_m(func.Unit()), monad_list)


def map_m(monad_t, transform, from_list):
    """Creates a list of monad_ts, then evaluates
    them and keeps the results."""
    return sequence(monad_t, [transform(a) for a in from_list])


def map_m_(monad_t, transform, from_list):
    """Creates a list of monad_ts, then evaluates
    them and dumps the results."""
    return sequence_(monad_t, [transform(a) for a in from_list])


def guard(monad_t, predicate):
    "return_m(Unit()) if the predicate is true, else mzero"
    if predicate:
        return monad_t.return_m(func.Unit())
    else:
        return monad_t.mzero()


def msum(monad_t, monad_list):
    "Generalized concatenation."
    return func.foldr(monad_t.mplus(), monad_t.mzero(), monad_list)


def filter_m(monad_t, predicate, filter_list):
    """Generalize the list filter for other monads."""
    if filter_list == []:
        return monad_t.return_m([])
    else:
        first, rest_orig = filter_list[0], filter_list[1:]
        return predicate(first) >= (lambda flg:
               filter_m(monad_t, predicate, rest_orig) >= (lambda rest:
               monad_t.return_m(rest + first if flg else rest)))


def for_m(monad_t, from_list, transform):
    "Flipped map_m"
    return map_m(monad_t, transform, from_list)


def for_m_(monad_t, from_list, transform):
    "Flipped map_m_"
    return map_m_(monad_t, transform, from_list)


@infix.Infix
def mcompl(a_to_monad_b, b_to_monad_c):
    """Left-to-right Kleisli composition."""
    return lambda a: (a_to_monad_b(a) >= b_to_monad_c)

mcompr = infix.Infix(func.flip(mcompl))
mcompr.__doc__ = "Flipped Kleisli composition."


def forever(monad_action):
    "Repeats a monad action infinitely."
    return monad_action >> forever(monad_action)


def join(monad_of_monads):
    "Removes a level of monadic structure."
    return monad_of_monads >= (lambda x: x)


def map_and_unzip_m(monad_t, map_function, from_list):
    """
    Maps a pair-generating function over the from_list, then unzips the result
    and returns a pair of lists.
    """
    return sequence(monad_t, map(map_function, from_list)) >= \
        (lambda r: monad_t.return_m(func.unzip(r)))


def zip_with_m(monad_t, zip_function, left, right):
    "Generalizes zip_with over non-list monads."
    return sequence(monad_t, func.zip_with(zip_function, left, right))


def zip_with_m_(monad_t, zip_function, left, right):
    "Same as zip_with_m, but ignores the result."
    return sequence_(monad_t, func.zip_with(zip_function, left, right))


def fold_m(monad_t, folder, acc, from_list, first=True):
    """Like foldl but the result is encapsulated in a monad.

    Equivalent to:
        folder acc1 from_list1 >=
        lambda acc2: folder acc2 from_list2 >=
        ...
        return folder accm from_listm
    """
    if first:
        from_list = list(reversed(from_list))
    if from_list == []:
        return monad_t.return_m(acc)
    else:
        return folder(acc, from_list.pop()) >= \
            (lambda fld: fold_m(monad_t, folder, fld, from_list, False))


def fold_m_(monad_t, folder, acc, from_list):
    "fold_m but the result is thrown away."
    return fold_m(monad_t, folder, acc, from_list) >> \
        monad_t.return_m(func.Unit())


def replicate_m(monad_t, replications, monad_item):
    "Generalized replicate for monads. Preforms the action n times."
    return sequence(monad_t, func.replicate(monad_item, replications))


def replicate_m_(monad_t, replications, monad_item):
    "Like replicateM, but discards the result."
    return sequence_(monad_t, func.replicate(monad_item, replications))


def when(monad_t, predicate, action):
    "Conditional execution of monads."
    return action if predicate else monad_t.return_m(func.Unit())


def unless(monad_t, predicate, action):
    "The opposite of when."
    return when(monad_t, not predicate, action)

# The liftM functions, as well as ap, are cumbersome and mostly unneeded in
# python. However, using python tuples and * magic, which breaks Haskell's
# type system, you can actually define a lift_m_n function like so:


def lift_m_n(monad_t, function, *monad_list):
    """
    By using a variadic function, we have successfully
    created a lift_m_n function. This would not be allowed in Haskell's
    type system, which is why it does not exist there.
    """
    return function(*sequence(monad_t, monad_list))


def mfilter(monad_t, predicate, monad_action):
    "MonadPlus equivalent of filter for lists."
    return monad_action >= (lambda a:
           monad_t.return_m(a) if predicate else monad_t.mzero())
