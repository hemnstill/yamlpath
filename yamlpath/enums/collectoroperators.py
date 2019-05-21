"""
Implements the CollectorOperators enumeration.

Copyright 2019 William W. Kimball, Jr. MBA MSIS
"""
from enum import Enum, auto
from typing import List


class CollectorOperators(Enum):
    """
    Supported Collector operators.  These identify how one Collector's results
    are to be combined with its predecessor Collector, if there is one.
    Operations include:

    `NONE`
        The Collector's results are not combined with its predecessor.
        Instead, the Collector creates a new result derived from its position
        with the data.

    `ADDITION`
        The Collector's results are concatenated with its immediate predecessor
        Collector's results.  No effort is made to limit the resluting data to
        unique values.

    `SUBTRACTION`
        The Collector's results are removed from its immediate predecessor
        Collector's results.  Only exact matches are removed.
    """
    ADDITION = auto()
    NONE = auto()
    SUBTRACTION = auto()

    @staticmethod
    def get_names() -> List[str]:
        """
        Returns all entry names for this enumeration.

        Parameters:  N/A

        Returns:  (List[str]) Upper-case names from this enumeration

        Raises:  N/A
        """
        return [entry.name.upper() for entry in CollectorOperators]

    @staticmethod
    def to_operator(name: "CollectorOperators") -> str:
        """
        Converts a value of this enumeration into a human-friendly operator.

        Parameters:
            1. name (CollectorOperators) The enumeration value to convert

        Returns: (str) The operator

        Raises:
            - `NameError` when name is unknown to this method.
        """
        operator: str = ''
        if name is CollectorOperators.NONE:
            operator = ''
        elif name is CollectorOperators.ADDITION:
            operator = '+'
        elif name is CollectorOperators.SUBTRACTION:
            operator = '-'
        else:
            raise NameError(
                "CollectorOperators has no such item:  {}"
                .format(name))

        return operator

    @staticmethod
    def from_operator(operator: str) -> "CollectorOperators":
        """Converts a string value to a value of this enumeration, if valid.

        Parameters:
            1. operator (str) The name to convert

        Returns:  (CollectorOperators) the converted enumeration value

        Raises:
            - `NameError` when name doesn't match any enumeration values.
        """
        if isinstance(operator, CollectorOperators):
            return operator

        check: str = str(operator).upper()

        if check == '+':
            check = "ADDITION"
        elif check == '-':
            check = "SUBTRACTION"

        if check in CollectorOperators.get_names():
            return CollectorOperators[check]
        raise NameError(
            "CollectorOperators has no such item, {}.".format(check))
