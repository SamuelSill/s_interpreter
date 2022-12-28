import pytest

from s_interpreter.compiler import *
from conftest import *


@pytest.mark.parametrize(("usage", "implementation"),
                         [
                             (
                                 "SUGAR {Const K}",
                                 ("{REPEATK}",
                                  "{END REPEAT}")
                             ),
                             (
                                 "SUGAR {Const K}",
                                 ("{REPEAT K}",
                                  "{ENDREPEAT}")
                             ),
                             (
                                 "SUGAR {Const K}",
                                 ("{REPEAT K}",)
                             ),
                             (
                                 "SUGAR {Const K}",
                                 ("{END REPEAT}",)
                             ),
                             (
                                 "SUGAR {Const K}",
                                 ("{REPEAT K}",
                                  "{END REPEAT}",
                                  "{END REPEAT}")
                             ),
                             (
                                 "SUGAR {Const K}",
                                 ("{REPEAT K}",
                                  "{REPEAT K}",
                                  "{END REPEAT}")
                             ),
                             (
                                 "SUGAR {Variable V}",
                                 ("{REPEAT V}",
                                  "{END REPEAT}")
                             ),
                             (
                                 "SUGAR",
                                 ("{REPEAT K}",
                                  "{END REPEAT}")
                             ),
                             (
                                 "SUGAR {Cons K}",
                                 ("{REPEAT K}",
                                  "{END REPEAT}")
                             ),
                             (
                                 "SUGAR {Variabl X}",
                                 ("{X} <- {X} + 1",)
                             ),
                             (
                                 "SUGAR {Lable L}",
                                 ("IF X != 0 GOTO {L}",)
                             ),
                             (
                                 "SUGAR {Label L}}",
                                 ("IF X != 0 GOTO {L}",)
                             ),
                             (
                                 "SUGAR {Label L",
                                 ("IF X != 0 GOTO {L}",)
                             ),
                             (
                                 "SUGAR {Variable V} + {Label V}",
                                 ("IF {V} != 0 GOTO {L}",)
                             )
                         ])
def test_sugar_error(usage: str,
                     implementation: tuple[str, ...]) -> None:
    with pytest.raises(ValueError):
        SyntacticSugar(usage,
                       *implementation)


@pytest.mark.parametrize(("sugar",
                          "invocation",
                          "program"),
                         [
                             (
                                SyntacticSugar("SUGAR"),
                                "SUGAR",
                                Program([])
                             ),
                             (
                                SyntacticSugar("SUGAR",
                                               "X <- X"),
                                "SUGAR",
                                Program([Instruction(Sentence(VariableCommand(Variable("X", 1),
                                                                              VariableCommandType.NoOp)))])
                             ),
                             (
                                SyntacticSugar("SUGAR {Variable V}",
                                               "{V} <- {V}"),
                                "SUGAR X",
                                Program([Instruction(Sentence(VariableCommand(Variable("X", 1),
                                                                              VariableCommandType.NoOp)))])
                             ),
                             (
                                SyntacticSugar("sUgAr {vArIAble V}",
                                               "{V} <- {V}"),
                                "SUGAR X",
                                Program([Instruction(Sentence(VariableCommand(Variable("X", 1),
                                                                              VariableCommandType.NoOp)))])
                             ),
                             (
                                 SyntacticSugar("SUGAR {Variable V1} + {Variable V2}",
                                                "{V1} <- {V1}",
                                                "{V2} <- {V2}"),
                                 "SUGAR Y + X",
                                 Program([Instruction(Sentence(VariableCommand(Variable("Y", 1),
                                                                               VariableCommandType.NoOp))),
                                          Instruction(Sentence(VariableCommand(Variable("X", 1),
                                                                               VariableCommandType.NoOp)))])
                             ),
                             (
                                 SyntacticSugar("SUGAR {Variable V} + {Variable V}",
                                                "{V} <- {V}"),
                                 "SUGAR X + X",
                                 Program([Instruction(Sentence(VariableCommand(Variable("X", 1),
                                                                               VariableCommandType.NoOp)))])
                             ),
                             (
                                 SyntacticSugar("SUGAR {Variable V} + {Label L}",
                                                "{V} <- {V}",
                                                "IF X != 0 GOTO {L}"),
                                 "SUGAR Y + A",
                                 Program([Instruction(Sentence(VariableCommand(Variable("Y", 1),
                                                                               VariableCommandType.NoOp))),
                                          Instruction(Sentence(JumpCommand(Variable("X", 1),
                                                                           Label("A", 1))))])
                             ),
                             (
                                 SyntacticSugar("SUGAR {Variable V} + {Label L}",
                                                "IF {V} != 0 GOTO {L}"),
                                 "SUGAR Y + A",
                                 Program([Instruction(Sentence(JumpCommand(Variable("Y", 1),
                                                                           Label("A", 1))))])
                             ),
                             (
                                 SyntacticSugar("SUGAR {Variable V} + {Label L}",
                                                "[{L}] IF {V} != 0 GOTO {L}"),
                                 "SUGAR Y + A",
                                 Program([Instruction(Sentence(JumpCommand(Variable("Y", 1),
                                                                           Label("A", 1))),
                                                      Label("A", 1))])
                             ),
                             *[
                                 (
                                     SyntacticSugar("SUGAR {Variable V} + {Const K}",
                                                    f"{pre_whitespace}{{{pre_repeat_whitespace}"
                                                    f"REPEAT{post_repeat_whitespace} "
                                                    f"K{post_const_whitespace}}}{post_whitespace}",
                                                    "{V} <- {V}",
                                                    "{END REPEAT}"),
                                     "SUGAR X + 3",
                                     Program([Instruction(Sentence(VariableCommand(Variable("X", 1),
                                                                                   VariableCommandType.NoOp)))] * 3)
                                 )
                                 for pre_whitespace in OPTIONAL_WHITESPACE
                                 for pre_repeat_whitespace in OPTIONAL_WHITESPACE
                                 for post_repeat_whitespace in OPTIONAL_WHITESPACE
                                 for post_const_whitespace in OPTIONAL_WHITESPACE
                                 for post_whitespace in OPTIONAL_WHITESPACE
                             ],
                             *[
                                 (
                                     SyntacticSugar("SUGAR {Variable V} + {Const K}",
                                                    "{REPEAT K}",
                                                    "{V} <- {V}",
                                                    f"{pre_whitespace}{{{pre_end_whitespace}END "
                                                    f"{pre_repeat_whitespace}REPEAT{post_repeat_whitespace}}}"
                                                    f"{post_whitespace}"),
                                     "SUGAR X + 3",
                                     Program([Instruction(Sentence(VariableCommand(Variable("X", 1),
                                                                                   VariableCommandType.NoOp)))] * 3)
                                 )
                                 for pre_whitespace in OPTIONAL_WHITESPACE
                                 for pre_repeat_whitespace in OPTIONAL_WHITESPACE
                                 for post_repeat_whitespace in OPTIONAL_WHITESPACE
                                 for pre_end_whitespace in OPTIONAL_WHITESPACE
                                 for post_whitespace in OPTIONAL_WHITESPACE
                             ],
                             (
                                 SyntacticSugar("SUGAR {Variable V} + {Const K}",
                                                "{REPEAT K}",
                                                "{V} <- {V}",
                                                "{V} <- {V} + 1",
                                                "{END REPEAT}"),
                                 "SUGAR X + 3",
                                 Program([Instruction(Sentence(VariableCommand(Variable("X", 1),
                                                                               VariableCommandType.NoOp))),
                                          Instruction(Sentence(VariableCommand(Variable("X", 1),
                                                                               VariableCommandType.Increment)))] * 3)
                             ),
                             (
                                 SyntacticSugar("SUGAR {Const K1} + {Const K2}",
                                                "{REPEAT K1}",
                                                "X <- X",
                                                "{REPEAT K2}",
                                                "`Y <- Y` + 1",
                                                "{END REPEAT}",
                                                "{END REPEAT}"),
                                 "SUGAR 2 + 3",
                                 Program([Instruction(Sentence(VariableCommand(Variable("X", 1),
                                                                               VariableCommandType.NoOp))),
                                          *([
                                                Instruction(Sentence(VariableCommand(Variable("Y", 1),
                                                                                     VariableCommandType.Increment)))
                                          ] * 3)] * 2)
                             ),
                             *[
                                 (
                                     SyntacticSugar("SUGAR {Variable V} + {Label L}",
                                                    "[{L}] IF {V} != 0 GOTO {L}"),
                                     f"{whitespace1}SUGAR {whitespace2}Y{whitespace3} + {whitespace4}A{whitespace5}",
                                     Program([Instruction(Sentence(JumpCommand(Variable("Y", 1),
                                                                               Label("A", 1))),
                                                          Label("A", 1))])
                                 )
                                 for whitespace1 in OPTIONAL_WHITESPACE
                                 for whitespace2 in OPTIONAL_WHITESPACE
                                 for whitespace3 in OPTIONAL_WHITESPACE
                                 for whitespace4 in OPTIONAL_WHITESPACE
                                 for whitespace5 in OPTIONAL_WHITESPACE
                                 for whitespace6 in OPTIONAL_WHITESPACE
                             ]
                         ])
def test_sugar_unused_vars_and_labels_compile(sugar: SyntacticSugar,
                                              invocation: str,
                                              program: Program) -> None:
    assert sugar.compile(invocation) == program


def test_sugar_used_vars_and_labels_compile() -> None:
    assert SyntacticSugar(
        "SUGAR",
        "Z <- Z"
    ).compile(
        "SUGAR",
        used_variables={Variable("Z")}
    ).instructions[0].sentence.command.variable != Variable("Z")

    assert SyntacticSugar(
        "SUGAR",
        "IF X != 0 GOTO A"
    ).compile(
        "SUGAR",
        used_labels={Label("A")}
    ).instructions[0].sentence.command.label != Label("A")

    assert SyntacticSugar(
        "SUGAR",
        "[A] IF X != 0 GOTO B"
    ).compile(
        "SUGAR",
        used_labels={Label("A")}
    ).instructions[0].label != Label("A")


def test_program_sugar_usage():
    assert Program.compile("SUGAR1",
                           sugars=[
                               SyntacticSugar("SUGAR1",
                                              "SUGAR2",
                                              sugars=[
                                                  SyntacticSugar("SUGAR2",
                                                                 "X <- X")
                                              ])
                           ]) == Program([Instruction(Sentence(VariableCommand(Variable("X"),
                                                                               VariableCommandType.NoOp)))])
    assert Program.compile("Z <- Z",
                           "SUGAR1",
                           sugars=[
                               SyntacticSugar("SUGAR1",
                                              "Z <- Z + 1")
                           ]).instructions[1].sentence.command.variable != Variable("Z")
    assert Program.compile("SUGAR1",
                           "Z <- Z",
                           sugars=[
                               SyntacticSugar("SUGAR1",
                                              "Z <- Z + 1")
                           ]).instructions[0].sentence.command.variable != Variable("Z")
    assert Program.compile("SUGAR1",
                           "IF X != 0 GOTO A",
                           sugars=[
                               SyntacticSugar("SUGAR1",
                                              "IF X != 0 GOTO A")
                           ]).instructions[0].sentence.command.label != Label("A")
    assert Program.compile("SUGAR1",
                           "[A] X <- X",
                           sugars=[
                               SyntacticSugar("SUGAR1",
                                              "IF X != 0 GOTO A")
                           ]).instructions[0].sentence.command.label != Label("A")
    assert Program.compile("SUGAR1",
                           "[A] X <- X",
                           sugars=[
                               SyntacticSugar("SUGAR1",
                                              "[A] X <- X")
                           ]).instructions[0].label != Label("A")


def test_sugar_precedence():
    assert Program.compile("SUGAR1",
                           sugars=[
                               SyntacticSugar("SUGAR1",
                                              "X <- X"),
                               SyntacticSugar("SUGAR1",
                                              "X2 <- X2"),
                           ]) == Program([Instruction(Sentence(VariableCommand(Variable("X"),
                                                                               VariableCommandType.NoOp)))])


def test_sugar_overloading():
    overloads: tuple[str, ...] = (
        "SUGAR A",
        "SUGAR {Label L}",
        "SUGAR X",
        "SUGAR {Variable V}",
        "SUGAR 1",
        "SUGAR {Const K}",
        "SUGAR {Variable V} {Variable V}",
        "SUGAR {Variable V} {Variable U}",
        "SUGAR {Label L} {Label L}",
        "SUGAR {Label L1} {Label L2}",
        "SUGAR {Label L} {Variable V}",
        "SUGAR {Variable V} {Label L}"
    )

    unreachable_overloads: tuple[str, ...] = (
        "SUGAR B",
        "SUGAR Y",
        "SUGAR 2",
        "SUGAR {Label L2}",
        "SUGAR {Variable V2}",
        "SUGAR {Const K2}",
    )

    assert Program.compile("SUGAR A",
                           "SUGAR B",
                           "SUGAR X",
                           "SUGAR Y",
                           "SUGAR 1",
                           "SUGAR 2",
                           "SUGAR X X",
                           "SUGAR X Y",
                           "SUGAR A A",
                           "SUGAR A B",
                           "SUGAR A X",
                           "SUGAR X A",
                           sugars=[
                               SyntacticSugar(title,
                                              f"X{index + 1} <- X{index + 1}")
                               for index, title in enumerate(overloads + unreachable_overloads)
                           ]) == Program([Instruction(Sentence(VariableCommand(Variable("X", index + 1),
                                                                               VariableCommandType.NoOp)))
                                          for index in range(len(overloads))])
