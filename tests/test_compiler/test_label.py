import pytest

from s_interpreter.compiler import *


@pytest.mark.parametrize(("name", "index"),
                         [
                             *[
                                 (letter, index)
                                 for letter in ("A", "B", "C", "D", "E")
                                 for index in (0, -1, -2)
                             ],
                             *[
                                 (letter, index)
                                 for letter in ("X", "Y", "Z")
                                 for index in (1, 2, 3)
                             ],
                             *[
                                 (letter * 2, index)
                                 for letter in ("A", "B", "C", "D", "E")
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
                                 (f"{pre_whitespace}{string_function(letter)}{index}{post_whitespace}",
                                  Label(variable_function(letter), 1 if index == "" else int(index)))
                                 for string_function in (str.upper, str)
                                 for variable_function in (str.upper, str)
                                 for letter in ("A", "B", "C", "D", "E")
                                 for index in ("50", "2", "1", "")
                                 for pre_whitespace in ("", "\t", " ", "\n")
                                 for post_whitespace in ("", "\t", " ", "\n")
                             ]
                         ])
def test_variable_compile(label_string: str,
                          compiled_label: Label) -> None:
    assert Label.compile(label_string) == compiled_label


@pytest.mark.parametrize("label_string",
                         [
                             *[
                                 f"{letter}{index}"
                                 for letter in ("A", "B", "C", "D", "E")
                                 for index in (0, -1, -2)
                             ],
                             *[
                                 f"{letter * 2}{index}"
                                 for letter in ("A", "B", "C", "D", "E")
                                 for index in (1, 2, 3)
                             ],
                             *[
                                 f"{letter}{index}"
                                 for letter in ("X", "Y", "Z")
                                 for index in (1, 2, 3)
                             ]
                         ])
def test_variable_compilation_error(label_string: str) -> None:
    with pytest.raises(CompilationError):
        Label.compile(label_string)


def test_variable_hash() -> None:
    # noinspection PyArgumentList
    assert len({
                Label(letter_func(letter), index)
                for letter_func in (str.upper, str.lower)
                for letter in ("A", "B", "C", "D", "E")
                for index in (1, 2, 3)}) == 15
