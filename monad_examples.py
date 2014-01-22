"""
Jonathan Reem
January 2014

Examples of some of the basic Monads, such as Maybe and Either.

Idea to use sqrt and log functions credit to:
    http://en.wikibooks.org/wiki/Haskell/Understanding_monads/Maybe
"""
# pylint: disable=C0103

import math
import func

# Maybe Monad
import maybe


def safe_sqrt(num):
    """Returns Nothing if the argument is outside the domain of
    the sqrt function. Otherwise returns Just the value."""
    if num < 0:
        return maybe.Maybe.Nothing()
    else:
        return maybe.Maybe.Just(num ** 0.5)


def safe_log(num):
    """Returns Nothing if the argument is outside the domain of
    the log function. Otherwise returns Just the value."""
    if num < 0:
        return maybe.Maybe.Nothing()
    else:
        return maybe.Maybe.Just(math.log(num))


def safe_log_then_sqrt(num):
    """
    Here's where monads come in. Without the very convenient bind operator,
    we would have to manually check the result of safe_log before executing
    safe_sqrt.

    We can't simply compose the functions together by doing:
        return safe_sqrt(safe_log(num))
    because safe_sqrt is expecting a plain number, not a Maybe(number).

    Manually catching that maybe would mean we couldn't just compose our
    previous two functions, instead we would have to do something like:
        sqrt_result = safe_sqrt(num)
        if sqrt_result.is_nothing:
            return maybe.Maybe.Nothing()
        else:
            return safe_log(sqrt_result.value)

    which is manageable (but annoying) for composing two functions, but
    quickly becomes unreasonable if you want to compose four or five.

    By making Maybe a monad, we can use bind to implement worry-free
    function composition over Maybe functions! This way we can effectively
    go back to the very first option, which is what we'd like to do, except
    using bind, which implements the correct composition rules for us, instead
    of plain function composition.

    You could also write: safe_log_then_sqrt = safe_log |mcompl| sqrt
    """
    return safe_log(num) >= safe_sqrt

# Either Monad
import either


def either_sqrt(num):
    """What if we want to send some custom error message back instead of just
    giving back an inscrutable Nothing? We can use the Either Monad!"""
    if num < 0:
        return either.Either.Left(
            "You can't take the square root of a negative number!")
    else:
        return either.Either.Right(num ** 0.5)


def either_log(num):
    """We can throw a different error message for each function, or even each
    failure case of each function."""
    if num < 0:
        return either.Either.Left(
            "You can't take the log of a negative number!")
    else:
        return either.Either.Right(math.log(num))


def either_log_then_sqrt(num):
    """
    Here's the really cool part. By using Either's bind operator, we can
    chain these two functions together and implement a sort of "exception"
    but in a completely pure context. There are no side effects here
    because the only thing we are doing is composing pure functions using
    a pure function!
    """
    return either_log(num) >= either_sqrt

# IO Monad
import IO


def IO_sqrt(num):
    """
    We can even combine the Either and IO monads to allow us to return
    arbitrary IO actions as our error messages instead of just strings.
    Maybe we want to write them to a file or get input from the user as
    part of the process. Whatever it is, by using the IO monad, we can
    do this *purely*, even though we are doing IO!
    """
    if num < 0:
        return either.Either.Left(IO.put_line(
            "You can't take the square root of a negative number!"))
    else:
        return either.Either.Right(num ** 0.5)


def IO_log(num):
    """
    We could even get input from the user as part of the error, for instance:
    """
    if num < 0:
        return either.Either.Left(
            IO.put_line("You can't take the log of a negative number!") >>
            IO.put_line("Do you understand?") >>
            IO.get_line())
    else:
        return either.Either.Right(math.log(num))


def IO_sqrt_log(num):
    """
    Using the same technique as with the previous combiners, we can just bind
    these values together. Once we do this computation we'll have to pattern
    match eventually to decide if we want to execute_IO() or return the final
    value.
    """
    return IO_log(num) >= IO_sqrt

# Putting it all together (and using the IO monad!):

get_number = (IO.put_line("Enter a number:") >>
              IO.IO.Input(lambda s: IO.IO.Final(float(s))))


def handle_maybe(maybe_val):
    "Handles a maybe value."
    if maybe_val.is_just:
        return maybe_val.value
    else:
        return "Nothing"

maybe_main = (get_number >= (lambda n:
              IO.put_line("The square root of {} is:".format(n))     >>
              IO.put_line("{}".format(handle_maybe(safe_sqrt(n))))   >>
              IO.put_line("The ln of {} is:".format(n))              >>
              IO.put_line("{}".format(handle_maybe(safe_log(n))))    >>
              IO.put_line("The sqrt of the log of {} is:".format(n)) >>
              IO.put_line("{}".format(handle_maybe(safe_log_then_sqrt(n))))))


def handle_either(either_val):
    "Handles an either value."
    return either_val.value

either_main = (get_number >= (lambda n:
               IO.put_line("The square root of {} is:".format(n))      >>
               IO.put_line("{}".format(handle_either(either_sqrt(n)))) >>
               IO.put_line("The ln of {} is:".format(n))               >>
               IO.put_line("{}".format(handle_either(either_log(n))))  >>
               IO.put_line("The sqrt of the log of {} is:".format(n))  >>
               IO.put_line("{}".format(handle_either(either_log_then_sqrt(n))))))


def handle_IO(either_IO_val):
    "Handles an either IO value."
    return either.either(func.id,
                         IO.put_line,
                         either_IO_val)

IO_main = (get_number >= (lambda n:
           IO.put_line("The square root of {} is:".format(n))     >>
           handle_IO(IO_sqrt(n))                                  >>
           IO.put_line("The ln of {} is:".format(n))              >>
           handle_IO(IO_log(n))                                   >>
           IO.put_line("The sqrt of the log of {} is:".format(n)) >>
           handle_IO(IO_sqrt_log(n))))


def main():
    "Runs each set of examples."
    # Ideally your main() consists of a single call of IO.execute_IO
    # Since we are really running three programs, we are making three calls
    # to IO.execute_IO. You could just chain them together with >>, though.
    IO.execute_IO(maybe_main)
    IO.execute_IO(either_main)
    IO.execute_IO(IO_main)

if __name__ == '__main__':
    main()
