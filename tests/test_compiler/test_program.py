import pytest

from s_interpreter.compiler import *


def test_program_error() -> None:
    with pytest.raises(ValueError):
        Program([
            Instruction(None,
                        Sentence(VariableCommand(Variable("Y", 1),
                                                 VariableCommandType.NoOp)))
        ])


@pytest.mark.parametrize(("program_tuple", "compiled_program"),
                         [
                             (tuple(), Program([])),
                             (("IF X != 0 GOTO A",),
                              Program(
                                 [
                                     Instruction(
                                         None,
                                         Sentence(
                                             JumpCommand(Variable("X", 1), Label("A", 1))
                                         ))
                                 ]
                             )),
                             (("IF X != 0 GOTO A",
                               "[A] Y <- Y"),
                              Program(
                                 [
                                     Instruction(
                                         None,
                                         Sentence(
                                             JumpCommand(Variable("X", 1), Label("A", 1))
                                         )),
                                     Instruction(
                                         Label("A", 1),
                                         Sentence(VariableCommand(Variable("Y", 1), VariableCommandType.NoOp))
                                     )
                                 ]
                              ))
                         ])
def test_program_compile(program_tuple: tuple[str, ...],
                         compiled_program: Program) -> None:
    assert Program.compile(*program_tuple) == compiled_program


@pytest.mark.parametrize("program_tuple",
                         [
                             ("X <- X",
                              "Y <- X"),
                             ("Y <- X",
                              "X <- X"),
                             ("Y <-",
                              "Y"),
                             ("IF X != 0 GOTO A",
                              "Y <- Y"),
                             ("Y <- Y",
                              "",
                              "X <- X")
                         ])
def test_program_compilation_error(program_tuple: tuple[str, ...]) -> None:
    with pytest.raises(CompilationError):
        Program.compile(*program_tuple)
