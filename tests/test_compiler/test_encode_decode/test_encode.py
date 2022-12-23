import pytest

from s_interpreter.compiler import *


@pytest.mark.parametrize(("pair", "encoding"),
                         [
                             ((0, 0), 0),
                             ((1, 0), 1),
                             ((0, 1), 2),
                             ((1, 1), 5),
                             ((3, 2), 39),
                             ((2, 3), 27),
                         ])
def test_encode_pair(pair: tuple[int, int],
                     encoding: int) -> None:
    assert encode_pair(pair) == encoding


@pytest.mark.parametrize(("list_", "encoding"),
                         [
                             ([], 1),
                             ([0], 1),
                             ([0] * 5, 1),
                             ([1], 2),
                             ([0, 1], 3),
                             ([0, 0, 1], 5),
                             ([1, 1], 6),
                             ([0, 1, 1], 15),
                             ([0, 1, 2], 75),
                         ])
def test_encode_list(list_: list[int],
                     encoding: int) -> None:
    assert encode_list(list_) == encoding


@pytest.mark.parametrize(("variable", "encoding"),
                         [
                             (Variable("Y", 1), 1),
                             (Variable("X", 1), 2),
                             (Variable("Z", 1), 3),
                             (Variable("X", 2), 4),
                             (Variable("Z", 2), 5),
                             (Variable("X", 20), 40),
                         ])
def test_encode_variable(variable: Variable,
                         encoding: int) -> None:
    assert variable.encode() == encoding


@pytest.mark.parametrize(("label", "encoding"),
                         [
                             (Label("A", 1), 1),
                             (Label("B", 1), 2),
                             (Label("C", 1), 3),
                             (Label("D", 1), 4),
                             (Label("E", 1), 5),
                             (Label("A", 2), 6),
                             (Label("B", 2), 7),
                             (Label("C", 2), 8),
                             (Label("D", 2), 9),
                             (Label("E", 2), 10),
                             (Label("E", 10), 50),
                         ])
def test_encode_label(label: Label,
                      encoding: int) -> None:
    assert label.encode() == encoding


@pytest.mark.parametrize(("variable_command_type", "encoding"),
                         [
                             (VariableCommandType.NoOp, 0),
                             (VariableCommandType.Increment, 1),
                             (VariableCommandType.Decrement, 2)
                         ])
def test_encode_variable_command_type(variable_command_type: VariableCommandType,
                                      encoding: int) -> None:
    assert variable_command_type.encode() == encoding


@pytest.mark.parametrize(("sentence", "encoding"),
                         [
                             (
                                 Sentence(VariableCommand(Variable("Y", 1),
                                                          VariableCommandType.NoOp)),
                                 0
                             ),
                             (
                                 Sentence(VariableCommand(Variable("Y", 1),
                                                          VariableCommandType.Increment)),
                                 1
                             ),
                             (
                                 Sentence(VariableCommand(Variable("Y", 1),
                                                          VariableCommandType.Decrement)),
                                 3
                             ),
                             (
                                 Sentence(VariableCommand(Variable("X", 1),
                                                          VariableCommandType.Decrement)),
                                 11
                             ),
                             (
                                 Sentence(JumpCommand(Variable("Y", 1),
                                                      Label("A", 1))),
                                 7
                             ),
                             (
                                 Sentence(JumpCommand(Variable("X", 1),
                                                      Label("B", 1))),
                                 47
                             )
                         ])
def test_encode_sentence(sentence: Sentence,
                         encoding: int) -> None:
    assert sentence.encode() == encoding


@pytest.mark.parametrize(("sentence", "encoding"),
                         [
                             (
                                 Sentence(VariableCommand(Variable("Y", 1),
                                                          VariableCommandType.NoOp)),
                                 (0, 0)
                             ),
                             (
                                 Sentence(VariableCommand(Variable("Y", 1),
                                                          VariableCommandType.Increment)),
                                 (1, 0)
                             ),
                             (
                                 Sentence(VariableCommand(Variable("Y", 1),
                                                          VariableCommandType.Decrement)),
                                 (2, 0)
                             ),
                             (
                                 Sentence(VariableCommand(Variable("X", 1),
                                                          VariableCommandType.Decrement)),
                                 (2, 1)
                             ),
                             (
                                 Sentence(JumpCommand(Variable("Y", 1),
                                                      Label("A", 1))),
                                 (3, 0)
                             ),
                             (
                                 Sentence(JumpCommand(Variable("X", 1),
                                                      Label("B", 1))),
                                 (4, 1)
                             )
                         ])
def test_encode_sentence_repr(sentence: Sentence,
                              encoding: tuple[int, int]) -> None:
    assert sentence.encode_repr() == encoding


@pytest.mark.parametrize(("instruction", "encoding"),
                         [
                             (
                                 Instruction(None,
                                             Sentence(JumpCommand(Variable("Y", 1),
                                                                  Label("A", 1)))),
                                 14
                             ),
                             (
                                 Instruction(Label("A", 1),
                                             Sentence(JumpCommand(Variable("Y", 1),
                                                                  Label("A", 1)))),
                                 29
                             )
                         ])
def test_encode_instruction(instruction: Instruction,
                            encoding: int) -> None:
    assert instruction.encode() == encoding


@pytest.mark.parametrize(("instruction", "encoding"),
                         [
                             (
                                 Instruction(None,
                                             Sentence(JumpCommand(Variable("Y", 1),
                                                                  Label("A", 1)))),
                                 (0, (3, 0))
                             ),
                             (
                                 Instruction(Label("A", 1),
                                             Sentence(JumpCommand(Variable("Y", 1),
                                                                  Label("A", 1)))),
                                 (1, (3, 0))
                             )
                         ])
def test_encode_instruction_repr(instruction: Instruction,
                                 encoding: tuple[int, tuple[int, int]]) -> None:
    assert instruction.encode_repr() == encoding


@pytest.mark.parametrize(("program", "encoding"),
                         [
                             (
                                 Program([
                                     Instruction(None,
                                                 Sentence(JumpCommand(Variable("Y", 1),
                                                                      Label("A", 1))))
                                 ]),
                                 16383
                             ),
                             (
                                 Program([
                                     Instruction(None,
                                                 Sentence(JumpCommand(Variable("Y", 1),
                                                                      Label("A", 1)))),
                                     Instruction(Label("A", 1),
                                                 Sentence(JumpCommand(Variable("Y", 1),
                                                                      Label("A", 1))))
                                 ]),
                                 1124440102746243071
                             )
                         ])
def test_encode_program(program: Program,
                        encoding: int) -> None:
    assert program.encode() == encoding


@pytest.mark.parametrize(("program", "encoding"),
                         [
                             (
                                 Program([
                                     Instruction(None,
                                                 Sentence(JumpCommand(Variable("Y", 1),
                                                                      Label("A", 1))))
                                 ]),
                                 [(0, (3, 0))]
                             ),
                             (
                                 Program([
                                     Instruction(None,
                                                 Sentence(JumpCommand(Variable("Y", 1),
                                                                      Label("A", 1)))),
                                     Instruction(Label("A", 1),
                                                 Sentence(JumpCommand(Variable("Y", 1),
                                                                      Label("A", 1))))
                                 ]),
                                 [(0, (3, 0)), (1, (3, 0))]
                             )
                         ])
def test_encode_program_repr(program: Program,
                             encoding: list[tuple[int, tuple[int, int]]]) -> None:
    assert program.encode_repr() == encoding
