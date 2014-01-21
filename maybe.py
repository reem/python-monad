"""
Jonathan Reem

Implementation of Data.Maybe from Haskell.
"""
# pylint: disable=C0103

from monad import Monad, MonadPlus, monadize


@monadize
class Maybe(Monad, MonadPlus):
    "Implements the Maybe monad from Haskell."
    NothingType = 'Nothing'
    JustType = 'Just'

    def __init__(self, maybe_type, value=None):
        "WARNING: Should not be called directly."
        self._maybe_type = maybe_type
        if maybe_type == Maybe.JustType:
            self._value = value

    @classmethod
    def Just(cls, value):
        "Constructor for Just x values."
        return cls(Maybe.JustType, value)

    @classmethod
    def Nothing(cls):
        "Constructor for Nothing values."
        return cls(Maybe.NothingType)

    # Maybe as a Monad
    def bind(self, bindee):
        if self.kind == Maybe.JustType:
            return bindee(self.value)
        elif self.kind == Maybe.NothingType:
            return Maybe.Nothing()

    def return_m(self, val):
        return Maybe.Just(val)

    # Maybe as a MonadPlus
    @property
    def mzero(self):
        return Maybe.Nothing()

    def mplus(self, other):
        if self.is_nothing:
            return other
        else:
            return self

    @property
    def kind(self):
        "Gets the kind of Maybe, Just or Nothing."
        return self._maybe_type

    @property
    def is_nothing(self):
        "Returns true if this is a Nothing"
        return self.kind == Maybe.NothingType

    @property
    def is_just(self):
        "Returns true if this is a Just"
        return self.kind == Maybe.JustType

    @property
    def value(self):
        "Gets the value if this is a Just, else throws an error."
        if self.is_just:
            return self._value
        elif self.is_nothing:
            raise ValueError("Tried to get value of a Nothing.")

    def __str__(self):
        if self.is_nothing:
            return "Nothing()"
        elif self.is_just:
            return "Just({})".format(self.value)

    def __repr__(self):
        return str(self)


def maybe(default, func, maybe_val):
    """Takes a default value, a function, and a Maybe value.
    If it's Nothing, return the default,
    else, return the function applied to the value."""
    if maybe_val.is_nothing:
        return default
    elif maybe_val.is_just:
        return func(maybe_val.value)


def from_just(maybe_val):
    "Will throw a ValueError if maybe_val is a Nothing."
    return maybe_val.value


def from_maybe(default, maybe_val):
    """Takes a maybe_value and a default,
    if the maybe_value is nothing returns the default,
    else returns the value."""
    try:
        return maybe_val.value
    except ValueError:
        return default
