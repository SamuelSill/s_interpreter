import pytest

from s_interpreter.compiler import *
from conftest import *


@pytest.mark.parametrize(("sentence_string", "variable_command"),
                         [
                             *[
                                 (f"{variable_name}{index}<-{variable_name}{index}",
                                  VariableCommand(Variable(variable_name, index),
                                                  VariableCommandType.NoOp))
                                 for variable_name in VARIABLE_NAMES
                                 for index in (1, 2, 3)
                                 if variable_name != "Y" or index == 1
                             ],
                             *[
                                 (f"{pre_whitespace}X"
                                  f"{pre_arrow_whitespace}<-"
                                  f"{post_arrow_whitespace}X"
                                  f"{post_whitespace}",
                                  VariableCommand(Variable("X", 1), VariableCommandType.NoOp))
                                 for pre_whitespace in OPTIONAL_WHITESPACE
                                 for post_whitespace in OPTIONAL_WHITESPACE
                                 for pre_arrow_whitespace in OPTIONAL_WHITESPACE
                                 for post_arrow_whitespace in OPTIONAL_WHITESPACE
                             ],
                             *[
                                 (f"{variable_name}{index}<-{variable_name}{index}{operation}1",
                                  VariableCommand(Variable(variable_name, index),
                                                  command_type))
                                 for variable_name in VARIABLE_NAMES
                                 for index in (1, 2, 3)
                                 for operation, command_type in (("+", VariableCommandType.Increment),
                                                                 ("-", VariableCommandType.Decrement))
                                 if variable_name != "Y" or index == 1
                             ],
                             *[
                                 (f"{pre_whitespace}X"
                                  f"{pre_arrow_whitespace}<-"
                                  f"{post_arrow_whitespace}X"
                                  f"{pre_inc_whitespace}+"
                                  f"{post_inc_whitespace}1"
                                  f"{post_whitespace}",
                                  VariableCommand(Variable("X", 1), VariableCommandType.Increment))
                                 for pre_whitespace in OPTIONAL_WHITESPACE
                                 for post_whitespace in OPTIONAL_WHITESPACE
                                 for pre_arrow_whitespace in OPTIONAL_WHITESPACE
                                 for post_arrow_whitespace in OPTIONAL_WHITESPACE
                                 for pre_inc_whitespace in OPTIONAL_WHITESPACE
                                 for post_inc_whitespace in OPTIONAL_WHITESPACE
                             ]
                         ])
def test_variable_command_compile(sentence_string: str,
                                  variable_command: VariableCommand) -> None:
    assert Sentence.compile(sentence_string) == Sentence(variable_command)


@pytest.mark.parametrize(("sentence_string", "jump_command"),
                         [
                             *[
                                 (f"IF {variable_name}{variable_index}!=0 GOTO {label_name}{label_index}",
                                  JumpCommand(Variable(variable_name, variable_index),
                                              Label(label_name, label_index)))
                                 for variable_name in VARIABLE_NAMES
                                 for variable_index in (1, 2, 3)
                                 for label_name in LABEL_NAMES
                                 for label_index in (1, 2, 3)
                                 if variable_name != "Y" or variable_index == 1
                             ],
                             *[
                                 (f"{pre_whitespace}IF "
                                  f"{pre_variable}X{post_variable}"
                                  f"!{in_not_equals}="
                                  f"{pre_zero}0{post_zero} GOTO "
                                  f"{pre_label}A{post_whitespace}",
                                  JumpCommand(Variable("X", 1), Label("A", 1)))
                                 for pre_whitespace in OPTIONAL_WHITESPACE
                                 for post_whitespace in OPTIONAL_WHITESPACE
                                 for pre_variable in OPTIONAL_WHITESPACE
                                 for post_variable in OPTIONAL_WHITESPACE
                                 for in_not_equals in OPTIONAL_WHITESPACE
                                 for pre_zero in OPTIONAL_WHITESPACE
                                 for post_zero in OPTIONAL_WHITESPACE
                                 for pre_label in OPTIONAL_WHITESPACE
                             ],
                             ("iF X!=0 goTO A", JumpCommand(Variable("X", 1), Label("A", 1)))
                         ])
def test_jump_command_compile(sentence_string: str,
                              jump_command: JumpCommand):
    assert Sentence.compile(sentence_string) == Sentence(jump_command)


@pytest.mark.parametrize("sentence_string",
                         [
                             *[
                                 f"{first_variable}{first_variable_index}<-"
                                 f"{second_variable}{second_variable_index}{operation}"
                                 for first_variable in VARIABLE_NAMES
                                 for first_variable_index in (1, 2, 3)
                                 for second_variable in VARIABLE_NAMES
                                 for second_variable_index in (1, 2, 3)
                                 for operation in ("", "+1", "-1")
                                 if f"{first_variable}{first_variable_index}" !=
                                    f"{second_variable}{second_variable_index}"
                             ],
                             "IF X=0 GOTO A",
                             "IF X!=0GOTO A",
                             "IF X!=0 GOTOA",
                             "IFX!=0 GOTO A",
                         ])
def test_sentence_compilation_error(sentence_string: str) -> None:
    with pytest.raises(CompilationError):
        Sentence.compile(sentence_string)
