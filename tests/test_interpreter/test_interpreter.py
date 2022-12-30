import pytest

from s_interpreter.compiler import *
from s_interpreter.interpreter import Interpreter


@pytest.fixture(scope="module")
def compile_interpreter() -> None:
    main(["-f", "s_interpreter.slang", "-o", "interpreter_program.txt"])


@pytest.fixture(scope="module")
def interpreter_program_lines(compile_interpreter: None) -> list[str]:
    with open("interpreter_program.txt", "r") as interpreter_program_file:
        yield interpreter_program_file.readlines()


@pytest.fixture(scope="module")
def interpreter_program(interpreter_program_lines: list[str]) -> Program:
    yield Program.compile(*interpreter_program_lines)


@pytest.mark.parametrize(("inputs", "expected_output"),
                         [
                             ((0, Program([
                                 Instruction(Sentence(VariableCommand(Variable("Y"),
                                                                      VariableCommandType.Increment)))
                             ]).encode()), 1),
                             ((0, Program([
                                 Instruction(Sentence(VariableCommand(Variable("Y"),
                                                                      VariableCommandType.Increment)))
                             ] * 2).encode()), 2),
                             ((0, Program([
                                 Instruction(Sentence(VariableCommand(Variable("Y"),
                                                                      VariableCommandType.Increment)))
                             ] * 3).encode()), 3),
                         ])
def test_interpreter(interpreter_program: Program,
                     inputs: tuple[int, ...],
                     expected_output: int) -> None:
    assert Interpreter(interpreter_program).run(*inputs) == expected_output
