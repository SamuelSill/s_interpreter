import dataclasses
import enum
import re
import typing
from sympy.ntheory import factorint, primerange, prime


class CompilationFailure(RuntimeError):
    pass


def encode_pair(pair: tuple[int, int]) -> int:
    return (2 ** pair[0]) * (2 * pair[1] + 1) - 1


def encode_list(number_list: list[int]) -> int:
    primes: list[int] = primerange(prime(len(number_list)) + 1)
    mul: int = 1
    for p, exponent in zip(primes, number_list):
        mul *= p ** exponent
    return mul


@dataclasses.dataclass(frozen=True)
class Variable:
    name: str
    index: int = 1

    @staticmethod
    def compile(variable_string: str) -> "Variable":
        if (variable_match := re.fullmatch(
                r"\s*(?P<variable_name>[XYZxyz])(?P<index>([1-9][0-9]*)?)\s*",
                variable_string
        )):
            if (
                variable_match.group("variable_name") == "Y" and
                len(variable_match.group("index")) > 0
            ):
                raise CompilationFailure(f"Failed to compile variable: \"{variable_string}\"")
            return Variable(
                variable_match.group("variable_name").upper(),
                int(variable_match.group("index"))
                if len(variable_match.group("index")) > 0
                else
                1
            )

    def encode(self) -> int:
        return (
            1
            if self.name == "Y"
            else
            (self.index * 2 + (0 if self.name == "X" else 1))
        )

    @staticmethod
    def decode(encoded_variable: int) -> "Variable":
        return (
            Variable("Y", 1)
            if encoded_variable == 0
            else
            Variable(
                "X"
                if encoded_variable % 2 != 0
                else
                "Y",
                ((encoded_variable - 1) // 2) + 1
            )
        )


@dataclasses.dataclass(frozen=True)
class Label:
    name: str
    index: int

    @staticmethod
    def compile(label_string: str) -> "Label":
        if (label_match := re.fullmatch(
                r"\s*(?P<label>[A-Ea-e])(?P<index>([1-9][0-9]*)?)\s*",
                label_string
        )):
            return Label(label_match.group("label").upper(),
                         int(label_match.group("index"))
                         if len(label_match.group("index")) > 0
                         else
                         1)
        else:
            raise CompilationFailure(f"Failed to compile label: \"{label_string}\"")

    def encode(self) -> int:
        return (self.index - 1) * (ord("E") - ord("A")) + (ord(self.name) - ord("A") + 1)

    @staticmethod
    def decode(encoded_label: int) -> "Label":
        return Label(
            "ABCDE"[(encoded_label - 1) % len("ABCDE")],
            ((encoded_label - 1) // 5) + 1
        )


@dataclasses.dataclass(frozen=True)
class JumpCommand:
    variable: Variable
    label: Label


class VariableCommandType(enum.IntEnum):
    NoOp = 0
    Increment = 1
    Decrement = 2

    @staticmethod
    def compile(command_type: str) -> "VariableCommandType":
        if (command_type_match := re.fullmatch(
                r"(?P<operation>[+-])\s*1",
                command_type
        )):
            return (
                VariableCommandType.Increment
                if command_type_match.group("operation") == '+'
                else
                VariableCommandType.Decrement
            )
        if re.fullmatch(r"\s*", command_type):
            return VariableCommandType.NoOp

    def encode(self) -> int:
        return int(self.value)


@dataclasses.dataclass(frozen=True)
class VariableCommand:
    variable: Variable
    command_type: VariableCommandType


@dataclasses.dataclass(frozen=True)
class Sentence:
    command: typing.Union[JumpCommand, VariableCommand]

    @staticmethod
    def compile(sentence: str) -> "Sentence":
        if (jump_match := re.fullmatch(
                r"\s*[Ii][Ff]\s+(?P<variable>[XYZxyz]([1-9][0-9]*)?)\s*!\s*=\s*0\s+"
                r"[Gg][Oo][Tt][Oo]\s+(?P<label>[A-Ea-e]([1-9][0-9]*)?)\s*",
                sentence
        )):
            return Sentence(JumpCommand(Variable.compile(jump_match.group("variable")),
                                        Label.compile(jump_match.group("label"))))
        if (variable_match := re.fullmatch(
                r"\s*(?P<variable1>[XYZxyz]([1-9][0-9]*)?)\s*<\s*-"
                r"\s*(?P<variable2>[XYZxyz]([1-9][0-9]*)?)\s*(?P<operation>([+-]\s*1)?)",
                sentence
        )):
            if variable_match.group("variable1") != variable_match.group("variable2"):
                raise CompilationFailure(f"Failed to compile sentence (used two different variables in sentence): "
                                         f"\"{sentence}\"")
            return Sentence(VariableCommand(Variable.compile(variable_match.group("variable1")),
                                            VariableCommandType.compile(variable_match.group("operation"))))
        else:
            raise CompilationFailure(f"Failed to compile sentence: \"{sentence}\"")

    def encode_repr(self) -> tuple[int, int]:
        return (
            self.command.command_type.encode()
            if type(self.command) is VariableCommand
            else
            self.command.label.encode() + 2,
            self.command.variable.encode() - 1
        )

    def encode(self) -> int:
        return encode_pair(self.encode_repr())

    @staticmethod
    def decode(encoded_sentence: int) -> "Sentence":
        encoded_sentence += 1
        factorization: dict[int, int] = factorint(encoded_sentence)

        return Sentence(
            JumpCommand(
                Variable.decode(((encoded_sentence // (2 ** factorization.get(2, 0))) - 1) // 2),
                Label.decode(factorization[2] - 2)
            )
            if factorization.get(2, 0) > 2
            else
            VariableCommand(
                Variable.decode(((encoded_sentence // (2 ** factorization.get(2, 0))) - 1) // 2),
                VariableCommandType(factorization.get(2, 0))
            )
        )


@dataclasses.dataclass(frozen=True)
class Instruction:
    label: typing.Optional[Label]
    sentence: Sentence

    @staticmethod
    def compile(line: str) -> "Instruction":
        instruction_match: typing.Optional[re.Match] = re.fullmatch(
            r"\s*(\[\s*(?P<label>[A-Ea-e]([1-9][0-9]*)?)\s*])?\s*(?P<sentence>.*)\s*",
            line
        )

        if not instruction_match:
            raise CompilationFailure(f"Failed to compile instruction: \"{line}\"")
        return Instruction(Label.compile(instruction_match.group("label"))
                           if instruction_match.group("label")
                           else
                           None,
                           Sentence.compile(instruction_match.group("sentence")))

    def encode_repr(self) -> tuple[int, tuple[int, int]]:
        return (
            0
            if self.label is None
            else
            self.label.encode(),
            self.sentence.encode_repr()
        )

    def encode(self) -> int:
        encoding: tuple[int, tuple[int, int]] = self.encode_repr()
        return encode_pair((encoding[0], encode_pair(encoding[1])))

    @staticmethod
    def decode(encoded_instruction: int) -> "Instruction":
        encoded_instruction += 1
        factorization: dict[int, int] = factorint(encoded_instruction)
        return Instruction(
            Label.decode(factorization[2])
            if 2 in factorization
            else
            None,
            Sentence.decode(((encoded_instruction // (2 ** factorization.get(2, 0))) - 1) // 2)
        )


@dataclasses.dataclass(frozen=True)
class Program:
    instructions: list[Instruction]

    @staticmethod
    def compile(*s_program: str) -> "Program":
        s_program_lines = s_program if len(s_program) > 1 else s_program[0].splitlines()
        instructions: list[Instruction] = [
            Instruction.compile(line)
            for line in s_program_lines
        ]

        if (instructions[-1].label is None and
                type(instructions[-1].sentence.command) is VariableCommand and
                instructions[-1].sentence.command.variable.name == "Y" and
                instructions[-1].sentence.command.command_type == VariableCommandType.NoOp):
            raise CompilationFailure("Convention of Y<-Y is not respected!")
        return Program(instructions)

    def encode_repr(self) -> list[tuple[int, tuple[int, int]]]:
        return [
            instruction.encode_repr()
            for instruction in self.instructions
        ]

    def encode(self) -> int:
        return encode_list([instruction.encode() for instruction in self.instructions]) - 1

    @staticmethod
    def decode(encoded_program: int) -> "Program":
        factorization: dict[int, int] = factorint(encoded_program + 1)
        return Program(
            [
                Instruction.decode(factorization.get(p, 0))
                for p in primerange(max(factorization) + 1)
            ]
        )

    def __add__(self,
                other: "Program") -> "Program":
        return Program(self.instructions + other.instructions)
