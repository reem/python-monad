"""
Jonathan Reem
January 2014

Basic implementation of the IO monad - PURE until run with execute_IO!
Allows for writing to stdout and reading from stdin.

Does not allow:
    Reading or changing mutable variables
    Opening files
    Running threads
    etc.

It could be extended to allow those actions,
just add their types, constructors, and a bind case for them.
"""
# pylint: disable=C0103

import monad
import func


@monad.monadize
class IO(monad.Monad):
    "IO structured as a Monad. Evaluated using execute_IO()"
    FinalT = 0
    OutputT = 1
    InputT = 2

    def __init__(self, IOtype, **IOkwargs):
        "Should not be called directly."
        if IOtype == IO.FinalT:
            self.IOtype = IOtype
            self.value = IOkwargs["value"]
        elif IOtype == IO.OutputT:
            self.IOtype = IOtype
            self.output = IOkwargs["output"]
            self.followup = IOkwargs["followup"]
        elif IOtype == IO.InputT:
            self.IOtype = IOtype
            self.action = IOkwargs["action"]

    @classmethod
    def Final(cls, value):
        "Constructor for the IO Final type."
        return cls(IO.FinalT, value=value)

    @classmethod
    def Output(cls, output, followup):
        "Constructor the IO Output type."
        return cls(IO.OutputT, output=output, followup=followup)

    @classmethod
    def Input(cls, action):
        "Constructor for the IO Input type."
        return cls(IO.InputT, action=action)

    def bind(self, bindee):
        if self.IOtype == IO.FinalT:
            return bindee(self.value)

        elif self.IOtype == IO.OutputT:
            return IO.Output(self.output, (self.followup >= bindee))

        elif self.IOtype == IO.InputT:
            return IO.Input(lambda s: self.action(s) >= bindee)

    @classmethod
    def return_m(cls, value):
        return cls.Final(value)

    def __str__(self):
        if self.IOtype == IO.FinalT:
            return "IO.Final({})".format(self.value)
        elif self.IOtype == IO.OutputT:
            return "IO.Output({}, {})".format(self.output,
                                              self.followup)
        elif self.IOtype == IO.InputT:
            return "IO.Input({})".format(self.action.__name__)

    def __repr__(self):
        return self.__str__()


def get_line():
    "IO construct for getting a line from the user and returning it."
    return IO.Input(IO.Final)


def put_line(string):
    "IO construct for printing a line and returning Unit()"
    return IO.Output(string, IO.Final(func.Unit()))


def execute_IO(IO_action, return_unit=False):
    """
    Takes an IO instance and actually runs it.
    Sort of analogous to unsafePerformIO, except not unsafe.
    """
    if IO_action.IOtype == IO.FinalT:
        if return_unit:
            return IO_action.value
        else:
            if IO_action.value == func.Unit():
                return None
            else:
                return IO_action.value

    elif IO_action.IOtype == IO.OutputT:
        print IO_action.output
        return execute_IO(IO_action.followup)

    elif IO_action.IOtype == IO.InputT:
        return execute_IO(IO_action.action(raw_input("")))

    raise ValueError("Malformed IO action.")
