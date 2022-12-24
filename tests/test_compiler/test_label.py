import pytest

from s_interpreter.compiler import *
from conftest import *


@pytest.mark.parametrize(("name", "index"),
                         [
                             *[
                                 (letter, index)
                                 for letter in LABEL_NAMES
                                 for index in (0, -1, -2)
                             ],
                             *[
                                 (letter, index)
                                 for letter in VARIABLE_NAMES
                                 for index in (1, 2, 3)
                             ],
                             *[
                                 (letter * 2, index)
                                 for letter in LABEL_NAMES
                                 for index in (1, 2, 3)
                             ]
                         ])
def test_label_error(name: str,
                     index: int) -> None:
    with pytest.raises(ValueError):
        Label(name, index)


@pytest.mark.parametrize(("label_string", "compiled_label"),
                         [
                             *[
                                 (f"{string_function(letter)}{index}",
                                  Label(variable_function(letter), 1 if index == "" else index))
                                 for string_function in (str.upper, str)
                                 for variable_function in (str.upper, str)
                                 for letter in LABEL_NAMES
                                 for index in (50, 2, 1, "")
                             ],
                             *[
                                 (f"{pre_whitespace}A{post_whitespace}", Label("A", 1))
                                 for pre_whitespace in OPTIONAL_WHITESPACE
                                 for post_whitespace in OPTIONAL_WHITESPACE
                             ]
                         ])
def test_label_compile(label_string: str,
                       compiled_label: Label) -> None:
    assert Label.compile(label_string) == compiled_label


@pytest.mark.parametrize("label_string",
                         [
                             *[
                                 f"{letter}{index}"
                                 for letter in LABEL_NAMES
                                 for index in (0, -1, -2)
                             ],
                             *[
                                 f"{letter * 2}{index}"
                                 for letter in LABEL_NAMES
                                 for index in (1, 2, 3)
                             ],
                             *[
                                 f"{letter}{index}"
                                 for letter in VARIABLE_NAMES
                                 for index in (1, 2, 3)
                             ]
                         ])
def test_label_compilation_error(label_string: str) -> None:
    with pytest.raises(CompilationError):
        Label.compile(label_string)


def test_label_hash() -> None:
    # noinspection PyArgumentList
    assert len({
                Label(letter_func(letter), index)
                for letter_func in (str.upper, str.lower)
                for letter in LABEL_NAMES
                for index in (1, 2, 3)}) == 15
