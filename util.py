#!/usr/bin/env python3

from argparse import ArgumentTypeError

class IntRange:
    def __init__(self, min=None, max=None):
        self.__min = min
        self.__max = max

    def __call__(self, arg):
        try:
            value = int(arg)
        except ValueError:
            raise self.exception()

        if ((self.__min is not None) and (value < self.__min)) or ((self.__max is not None) and (value > self.__max)):
            raise self.exception()

        return value

    def exception(self):
        if (self.__min is not None) and (self.__max is not None):
            return ArgumentTypeError(f"Must be an integer in the range [{self.__min, self.__max}]")
        elif self.__min is not None:
            return ArgumentTypeError(f"Must be an integer >= {self.__min}")
        elif self.__max is not None:
            return ArgumentTypeError(f"Must be an integer <= {self.__max}")
        else:
            return ArgumentTypeError("Must be an integer")

