import pytest

from s_interpreter.compiler import *
from conftest import *


@pytest.mark.parametrize(("instruction_string", "compiled_instruction"),
                         [
                             *[
                                 (f"[{label_name}{label_index}] "
                                  f"X <- X{operation}",
                                  Instruction(Sentence(VariableCommand(Variable("X", 1), command_type)),
                                              Label(label_name, 1 if label_index == "" else label_index)))
                                 for operation, command_type in (("", VariableCommandType.NoOp),
                                                                 (" + 1", VariableCommandType.Increment),
                                                                 (" - 1", VariableCommandType.Decrement))
                                 for label_name in LABEL_NAMES
                                 for label_index in ("", 1, 2, 3)
                             ],
                             *[
                                 (f"X <- X{operation}",
                                  Instruction(Sentence(
                                                  VariableCommand(Variable("X", 1),
                                                                  command_type))
                                              ))
                                 for operation, command_type in (("", VariableCommandType.NoOp),
                                                                 (" + 1", VariableCommandType.Increment),
                                                                 (" - 1", VariableCommandType.Decrement))
                             ],
                             *[
                                 (f"[{label_name}{label_index}] IF X != 0 GOTO A",
                                  Instruction(Sentence(JumpCommand(Variable("X", 1),
                                                                   Label("A", 1))),
                                              Label(label_name, 1 if label_index == "" else label_index)))
                                 for label_name in LABEL_NAMES
                                 for label_index in ("", 1, 2, 3)
                             ],
                             (f"IF X != 0 GOTO A",
                              Instruction(Sentence(
                                              JumpCommand(Variable("X", 1),
                                                          Label("A", 1))))),
                             *[
                                 (f"{pre_whitespace}[{pre_label}A{post_label}]{post_brackets}"
                                  f"IF X != 0 GOTO A{post_whitespace}",
                                  Instruction(Sentence(JumpCommand(Variable("X", 1),
                                                                   Label("A", 1))),
                                              Label("A", 1)))
                                 for pre_whitespace in OPTIONAL_WHITESPACE
                                 for post_whitespace in OPTIONAL_WHITESPACE
                                 for pre_label in OPTIONAL_WHITESPACE
                                 for post_label in OPTIONAL_WHITESPACE
                                 for post_brackets in OPTIONAL_WHITESPACE
                             ]
                         ])
def test_instruction_compile(instruction_string: str,
                             compiled_instruction: Instruction) -> None:
    assert Instruction.compile(instruction_string) == compiled_instruction


@pytest.mark.parametrize("instruction_string",
                         [
                             "[A X <- X",
                             "A X <- X",
                             "A] X <- X",
                             "[Y] X <- X",
                             "[] X <- X"
                         ])
def test_instruction_compilation_error(instruction_string: str) -> None:
    with pytest.raises(CompilationError):
        Instruction.compile(instruction_string)
