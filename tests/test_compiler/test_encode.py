import pytest

from s_interpreter.compiler import *


@pytest.mark.parametrize("pair",
                         [
                             (-1, 0),
                             (0, -1),
                             (-1, -1),
                             (-10, -10)
                         ])
def test_pair_error(pair: tuple[int, int]) -> None:
    with pytest.raises(ValueError):
        EncodedPair(*pair)


@pytest.mark.parametrize("list_",
                         [
                             [-1],
                             [-10],
                             [-1, 0],
                             [0, -1],
                             [-1, -1],
                             [-10, -10]
                         ])
def test_list_error(list_: list[int]) -> None:
    with pytest.raises(ValueError):
        EncodedList(list_)


@pytest.mark.parametrize(("pair", "encoding"),
                         [
                             (EncodedPair(0, 0), 0),
                             (EncodedPair(1, 0), 1),
                             (EncodedPair(0, 1), 2),
                             (EncodedPair(1, 1), 5),
                             (EncodedPair(3, 2), 39),
                             (EncodedPair(2, 3), 27),
                         ])
def test_encode_pair(pair: EncodedPair,
                     encoding: int) -> None:
    assert pair.encode() == encoding
    assert EncodedPair.decode(encoding) == pair


@pytest.mark.parametrize("encoding",
                         [
                             -1,
                             -2,
                             -3
                         ])
def test_decode_pair_error(encoding: int) -> None:
    with pytest.raises(ValueError):
        EncodedPair.decode(encoding)


@pytest.mark.parametrize(("list_", "encoding"),
                         [
                             (EncodedList([]), 1),
                             (EncodedList([1]), 2),
                             (EncodedList([0, 1]), 3),
                             (EncodedList([0, 0, 1]), 5),
                             (EncodedList([1, 1]), 6),
                             (EncodedList([0, 1, 1]), 15),
                             (EncodedList([0, 1, 2]), 75),
                         ])
def test_encode_list(list_: EncodedList,
                     encoding: int) -> None:
    assert list_.encode() == encoding
    assert EncodedList.decode(encoding) == list_


@pytest.mark.parametrize("encoding",
                         [
                             0,
                             -1,
                             -2,
                             -3
                         ])
def test_decode_list_error(encoding: int) -> None:
    with pytest.raises(ValueError):
        EncodedList.decode(encoding)


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
    assert Variable.decode(encoding) == variable


@pytest.mark.parametrize("encoding",
                         [
                             0,
                             -1,
                             -2,
                             -3
                         ])
def test_decode_variable_error(encoding: int) -> None:
    with pytest.raises(ValueError):
        Variable.decode(encoding)


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
    assert Label.decode(encoding) == label


@pytest.mark.parametrize("encoding",
                         [
                             0,
                             -1,
                             -2,
                             -3
                         ])
def test_decode_label_error(encoding: int) -> None:
    with pytest.raises(ValueError):
        Label.decode(encoding)


@pytest.mark.parametrize(("variable_command_type", "encoding"),
                         [
                             (VariableCommandType.NoOp, 0),
                             (VariableCommandType.Increment, 1),
                             (VariableCommandType.Decrement, 2)
                         ])
def test_encode_variable_command_type(variable_command_type: VariableCommandType,
                                      encoding: int) -> None:
    assert variable_command_type.encode() == encoding
    assert VariableCommandType.decode(encoding) == variable_command_type


@pytest.mark.parametrize("encoding",
                         [
                             4,
                             3,
                             -1,
                             -2,
                             -3
                         ])
def test_decode_variable_command_type_error(encoding: int) -> None:
    with pytest.raises(ValueError):
        VariableCommandType.decode(encoding)


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
    assert Sentence.decode(encoding) == sentence


@pytest.mark.parametrize("encoding",
                         [
                             -1,
                             -2,
                             -3
                         ])
def test_decode_sentence_error(encoding: int) -> None:
    with pytest.raises(ValueError):
        Sentence.decode(encoding)


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
    assert Sentence.decode_repr(encoding) == sentence


@pytest.mark.parametrize("encoding",
                         [
                             (0, -1),
                             (1, -1),
                             (-1, 0),
                             (-1, 1),
                             (-1, -1),
                         ])
def test_decode_repr_sentence_error(encoding: tuple[int, int]) -> None:
    with pytest.raises(ValueError):
        Sentence.decode_repr(encoding)


@pytest.mark.parametrize(("instruction", "encoding"),
                         [
                             (
                                 Instruction(Sentence(JumpCommand(Variable("Y", 1),
                                                                  Label("A", 1)))),
                                 14
                             ),
                             (
                                 Instruction(Sentence(JumpCommand(Variable("Y", 1),
                                                                  Label("A", 1))),
                                             Label("A", 1)),
                                 29
                             )
                         ])
def test_encode_instruction(instruction: Instruction,
                            encoding: int) -> None:
    assert instruction.encode() == encoding
    assert Instruction.decode(encoding) == instruction


@pytest.mark.parametrize("encoding",
                         [
                             -1,
                             -2,
                             -3
                         ])
def test_decode_sentence_error(encoding: int) -> None:
    with pytest.raises(ValueError):
        Instruction.decode(encoding)


@pytest.mark.parametrize(("instruction", "encoding"),
                         [
                             (
                                 Instruction(Sentence(JumpCommand(Variable("Y", 1),
                                                                  Label("A", 1)))),
                                 (0, (3, 0))
                             ),
                             (
                                 Instruction(Sentence(JumpCommand(Variable("Y", 1),
                                                                  Label("A", 1))),
                                             Label("A", 1)),
                                 (1, (3, 0))
                             )
                         ])
def test_encode_instruction_repr(instruction: Instruction,
                                 encoding: tuple[int, tuple[int, int]]) -> None:
    assert instruction.encode_repr() == encoding
    assert Instruction.decode_repr(encoding) == instruction


@pytest.mark.parametrize("encoding",
                         [
                             (1, (1, -1)),
                             (1, (0, -1)),
                             (0, (1, -1)),
                             (0, (0, -1)),

                             (1, (-1, 1)),
                             (1, (-1, 0)),
                             (0, (-1, 1)),
                             (0, (-1, 0)),

                             (-1, (1, 1)),
                             (-1, (1, 0)),
                             (-1, (0, 1)),
                             (-1, (0, 0)),

                             (1, (-1, -1)),
                             (0, (-1, -1)),

                             (-1, (1, -1)),
                             (-1, (0, -1)),

                             (-1, (-1, 1)),
                             (-1, (-1, 0)),

                             (-1, (-1, -1)),
                         ])
def test_decode_repr_sentence_error(encoding: tuple[int, tuple[int, int]]) -> None:
    with pytest.raises(ValueError):
        Instruction.decode_repr(encoding)


@pytest.mark.parametrize(("program", "encoding"),
                         [
                             (
                                 Program([
                                     Instruction(Sentence(JumpCommand(Variable("Y", 1),
                                                                      Label("A", 1))))
                                 ]),
                                 16383
                             ),
                             (
                                 Program([
                                     Instruction(Sentence(JumpCommand(Variable("Y", 1),
                                                                      Label("A", 1)))),
                                     Instruction(Sentence(JumpCommand(Variable("Y", 1),
                                                                      Label("A", 1))),
                                                 Label("A", 1))
                                 ]),
                                 1124440102746243071
                             )
                         ])
def test_encode_program(program: Program,
                        encoding: int) -> None:
    assert program.encode() == encoding
    assert Program.decode(encoding) == program


@pytest.mark.parametrize("encoding",
                         [
                             -1,
                             -2,
                             -3
                         ])
def test_decode_program_error(encoding: int) -> None:
    with pytest.raises(ValueError):
        Program.decode(encoding)


@pytest.mark.parametrize(("program", "encoding"),
                         [
                             (
                                 Program([
                                     Instruction(Sentence(JumpCommand(Variable("Y", 1),
                                                                      Label("A", 1))))
                                 ]),
                                 [(0, (3, 0))]
                             ),
                             (
                                 Program([
                                     Instruction(Sentence(JumpCommand(Variable("Y", 1),
                                                                      Label("A", 1)))),
                                     Instruction(Sentence(JumpCommand(Variable("Y", 1),
                                                                      Label("A", 1))),
                                                 Label("A", 1))
                                 ]),
                                 [(0, (3, 0)), (1, (3, 0))]
                             )
                         ])
def test_encode_program_repr(program: Program,
                             encoding: list[tuple[int, tuple[int, int]]]) -> None:
    assert program.encode_repr() == encoding
    assert Program.decode_repr(encoding) == program


@pytest.mark.parametrize("encoding",
                         [
                             [(0, (3, 0)), (-1, (3, 0))],
                             [(0, (3, -1))]
                         ])
def test_decode_repr_program_error(encoding: list[tuple[int, tuple[int, int]]]) -> None:
    with pytest.raises(ValueError):
        Program.decode_repr(encoding)
