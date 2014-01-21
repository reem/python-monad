"""
Jonathan Reem
January 2014

Implementation of the Either type and monad from Haskell.
Equivalent to Data.Either, docstrings mostly from the same.
"""
# pylint: disable=C0103

import monad


@monad.monadize
class Either(monad.Monad):
    """Either a b from the Haskell Prelude.

    From Data.Either:

    The 'Either' type represents values with two possibilities: a value of
    type 'Either' a b is either 'Left' a or 'Right' b.

    The 'Either' type is sometimes used to represent a value which is
    either correct or an error; by convention, the 'Left' constructor is
    used to hold an error value and the 'Right' constructor is used to
    hold a correct value (mnemonic: "right" also means "correct").
    """
    LeftT = 0
    RightT = 1

    def __init__(self, EitherT, value):
        "Should not be called directly."
        self.EitherT = EitherT
        self.value = value

    @classmethod
    def Left(cls, value):
        "Constructor for Left values."
        return cls(Either.LeftT, value)

    @classmethod
    def Right(cls, value):
        "Constructor Right values."
        return cls(Either.RightT, value)

    def bind(self, bindee):
        if self.EitherT == Either.LeftT:
            return self

        elif self.EitherT == Either.RightT:
            return bindee(self.value)

    @classmethod
    def return_m(cls, value):
        return cls.Right(value)

    def __str__(self):
        return "{}({})".format("Right" if self.EitherT == Either.RightT
                               else "Left", self.value)

    def __repr__(self):
        return str(self)


def either(left_callback, right_callback, either_value):
    """
    Case analysis for Either.

    If the value is left, apply the left_callback.
    If the value is right, apply the right_callback.
    """
    if either_value.EitherT == Either.RightT:
        return right_callback(either_value.value)
    elif either_value.EitherT == Either.LeftT:
        return left_callback(either_value.value)


def lefts(either_list):
    "Extracts all the left values from a list of Eithers."
    return [left.value
            for left in either_list
            if left.EitherT == Either.LeftT]


def rights(either_list):
    "Extracts all the right values from a list of Eithers."
    return [right.value
            for right in either_list
            if right.EitherT == Either.RightT]


def partition_eithers(either_list):
    "Partitions the values into two lists, the lefts and the rights."
    return (lefts(either_list), rights(either_list))
