import pytest

from s_interpreter.compiler import *
from conftest import *


@pytest.mark.parametrize(("name", "index"),
                         [
                             *[
                                 (letter, index)
                                 for letter in VARIABLE_NAMES
                                 for index in (0, -1, -2)
                             ],
                             *[
                                 ("Y", index)
                                 for index in (2, 3, 4)
                             ],
                             *[
                                 (letter, index)
                                 for letter in LABEL_NAMES
                                 for index in (1, 2, 3)
                             ],
                             *[
                                 (letter * 2, index)
                                 for letter in VARIABLE_NAMES
                                 for index in (1, 2, 3)
                             ]
                         ])
def test_variable_error(name: str,
                        index: int) -> None:
    with pytest.raises(ValueError):
        Variable(name, index)


@pytest.mark.parametrize(("variable_string", "compiled_variable"),
                         [
                             *[
                                 (f"{string_function(letter)}{index}",
                                  Variable(variable_function(letter), 1 if index == "" else index))
                                 for letter in VARIABLE_NAMES
                                 for index in (50, 2, 1, "")
                                 for string_function in (str.upper, str)
                                 for variable_function in (str.upper, str)
                                 if letter != "Y" or index == 1
                             ],
                             *[
                                 (f"{pre_whitespace}X{post_whitespace}", Variable("X", 1))
                                 for pre_whitespace in OPTIONAL_WHITESPACE
                                 for post_whitespace in OPTIONAL_WHITESPACE
                             ]
                         ])
def test_variable_compile(variable_string: str,
                          compiled_variable: Variable) -> None:
    assert Variable.compile(variable_string) == compiled_variable


@pytest.mark.parametrize("variable_string",
                         [
                             *[
                                 f"{letter}{index}"
                                 for letter in VARIABLE_NAMES
                                 for index in (0, -1, -2)
                             ],
                             *[
                                 f"{letter * 2}{index}"
                                 for letter in VARIABLE_NAMES
                                 for index in (1, 2, 3)
                             ],
                             *[
                                 f"{letter}{index}"
                                 for letter in LABEL_NAMES
                                 for index in (1, 2, 3)
                             ],
                             "Y2",
                             "Y3",
                         ])
def test_variable_compilation_error(variable_string: str) -> None:
    with pytest.raises(CompilationError):
        Variable.compile(variable_string)


def test_variable_hash() -> None:
    # noinspection PyArgumentList
    assert len({
        *[
            Variable(letter_func(letter), index)
            for letter_func in (str.upper, str.lower)
            for letter in VARIABLE_NAMES
            for index in (1, 2, 3)
            if letter.upper() != "Y" or index == 1
        ]
    }) == 7
