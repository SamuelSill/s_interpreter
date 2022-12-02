from dataclasses import dataclass as _dataclass
import enum as _enum


class CompilationFailure(RuntimeError):
    pass


def encode_pair(pair: tuple[int, int]) -> int:
    return (2 ** pair[0]) * (2 * pair[1] + 1) - 1


def encode_list(number_list: list[int]) -> int:
    from sympy.ntheory import primerange, prime
    primes: list[int] = primerange(prime(len(number_list)) + 1)
    mul: int = 1
    for p, exponent in zip(primes, number_list):
        mul *= p ** exponent
    return mul


@_dataclass(frozen=True)
class Variable:
    name: str
    index: int = 1

    @staticmethod
    def compile(variable_string: str) -> "Variable":
        import re

        if (variable_match := re.fullmatch(
            r"\s*(?P<variable_name>[XYZ])(?P<index>([1-9][0-9]*)?)\s*",
            variable_string,
            flags=re.IGNORECASE
        )):
            variable: Variable = Variable(
                variable_match.group("variable_name").upper(),
                int(variable_match.group("index"))
                if len(variable_match.group("index")) > 0
                else
                1
            )
            if variable.name == "Y" and variable.index > 1:
                raise CompilationFailure(f"Failed to compile variable: \"{variable_string}\"")
            return variable

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

    def __str__(self) -> str:
        return f"{self.name}" + ("" if self.index == 1 else str(self.index))


@_dataclass(frozen=True)
class Label:
    name: str
    index: int = 1

    @staticmethod
    def compile(label_string: str) -> "Label":
        import re

        if (label_match := re.fullmatch(
            r"\s*(?P<label>[A-E])(?P<index>([1-9][0-9]*)?)\s*",
            label_string,
            flags=re.IGNORECASE
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

    def __str__(self) -> str:
        return f"{self.name}" + ("" if self.index == 1 else str(self.index))


@_dataclass(frozen=True)
class JumpCommand:
    variable: Variable
    label: Label

    def __str__(self) -> str:
        return f"IF {str(self.variable)} != 0 GOTO {str(self.label)}"


class VariableCommandType(_enum.IntEnum):
    NoOp = 0
    Increment = 1
    Decrement = 2

    @staticmethod
    def compile(command_type: str) -> "VariableCommandType":
        import re

        if command_type_match := re.fullmatch(r"(?P<operation>[+-])\s*1", command_type):
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

    def __str__(self) -> str:
        return (
            ""
            if self.value == VariableCommandType.NoOp
            else
            " + 1"
            if self.value == VariableCommandType.Increment
            else
            " - 1"
        )


@_dataclass(frozen=True)
class VariableCommand:
    variable: Variable
    command_type: VariableCommandType

    def __str__(self) -> str:
        return (
            f"{str(self.variable)} <- {str(self.variable)}{str(self.command_type)}"
        )


@_dataclass(frozen=True)
class Sentence:
    from typing import Union as _Union
    command: _Union[JumpCommand, VariableCommand]

    @staticmethod
    def compile(sentence: str) -> "Sentence":
        import re

        if (jump_match := re.fullmatch(
            r"\s*IF\s+(?P<variable>[XYZ]([1-9][0-9]*)?)\s*!\s*=\s*0\s+"
            r"GOTO\s+(?P<label>[A-E]([1-9][0-9]*)?)\s*",
            sentence,
            flags=re.IGNORECASE
        )):
            return Sentence(JumpCommand(Variable.compile(jump_match.group("variable")),
                                        Label.compile(jump_match.group("label"))))
        if (variable_match := re.fullmatch(
            r"\s*(?P<variable1>[XYZ]([1-9][0-9]*)?)\s*<\s*-"
            r"\s*(?P<variable2>[XYZ]([1-9][0-9]*)?)\s*(?P<operation>([+-]\s*1)?)",
            sentence,
            flags=re.IGNORECASE
        )):
            variable: Variable = Variable.compile(variable_match.group("variable1"))
            if variable != Variable.compile(variable_match.group("variable2")):
                raise CompilationFailure(f"Failed to compile sentence (used two different variables in sentence): "
                                         f"\"{sentence}\"")
            return Sentence(VariableCommand(variable,
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
        from sympy.ntheory import factorint
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

    def __str__(self) -> str:
        return str(self.command)


@_dataclass(frozen=True)
class Instruction:
    from typing import Optional as _Optional

    label: _Optional[Label]
    sentence: Sentence

    @staticmethod
    def compile(line: str) -> "Instruction":
        import re
        from typing import Optional

        instruction_match: Optional[re.Match] = re.fullmatch(
            r"\s*(\[\s*(?P<label>[A-E]([1-9][0-9]*)?)\s*])?\s*(?P<sentence>.*)\s*",
            line,
            flags=re.IGNORECASE
        )

        if not instruction_match:
            raise CompilationFailure(f"Failed to compile instruction: \"{line}\"")
        return Instruction(Label.compile(label)
                           if (label := instruction_match.group("label"))
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
        from sympy.ntheory import factorint

        encoded_instruction += 1
        factorization: dict[int, int] = factorint(encoded_instruction)
        return Instruction(
            Label.decode(factorization[2])
            if 2 in factorization
            else
            None,
            Sentence.decode(((encoded_instruction // (2 ** factorization.get(2, 0))) - 1) // 2)
        )

    def __str__(self) -> str:
        return (f"[{str(self.label)}] " if self.label is not None else "") + str(self.sentence)


@_dataclass(frozen=True)
class Program:
    from typing import Optional as _Optional

    instructions: list[Instruction]

    @staticmethod
    def compile(*program: str,
                sugars: _Optional[list["SyntacticSugar"]] = None) -> "Program":
        if sugars is None:
            sugars = []

        @_dataclass
        class SugarJob:
            sugar: SyntacticSugar
            sugar_invocation: str
            index_to_inject: int

        sugar_jobs: list[SugarJob] = []
        instructions: list[Instruction] = []
        for line in program:
            try:
                instructions.append(Instruction.compile(line))
            except CompilationFailure as compilation_failure:
                any_sugar_valid: bool = False
                for sugar in sugars:
                    if sugar.validate(line):
                        any_sugar_valid = True
                        sugar_jobs.append(SugarJob(sugar, line, len(instructions)))
                        break
                if not any_sugar_valid:
                    raise compilation_failure

        for sugar_job_index, sugar_job in enumerate(sugar_jobs):
            instructions_to_inject: list[Instruction] = sugar_job.sugar.compile(sugar_job.sugar_invocation,
                                                                                instructions)
            for instruction_index, instruction_to_inject in enumerate(instructions_to_inject):
                instructions.insert(sugar_job.index_to_inject + instruction_index,
                                    instruction_to_inject)
            sugar_job_index += 1
            while sugar_job_index < len(sugar_jobs):
                sugar_jobs[sugar_job_index].index_to_inject += len(instructions_to_inject)
                sugar_job_index += 1

        if (len(instructions) > 0 and
                instructions[-1].label is None and
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
        from sympy.ntheory import factorint, primerange

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

    def __str__(self) -> str:
        import re

        max_sentence_indentation: int = max(
            (
                len(re.match(r"(\[.*])?\s*", str(instruction)).group())
                for instruction in self.instructions
            ),
            default=0
        )

        return "\n".join(
            (start := re.match(r"(\[.*])?\s*", str(instruction)).group()) +
            (max_sentence_indentation - len(start)) * " " +
            str(instruction.sentence)
            for instruction in self.instructions
        )


class SyntacticSugar:
    from typing import Optional as _Optional

    def __init__(self,
                 usage: str,
                 *implementation: str,
                 sugars: _Optional[list["SyntacticSugar"]] = None):
        import re
        from typing import Union, Type

        if sugars is None:
            sugars = []
            r"()[]{}?*+-|^$\\.&~# \t\n\r\v\f"
        usage = re.sub(r"(?P<special_char>[*+\-|^\\&~#])",
                       r"\\\g<special_char>",
                       usage.strip())
        self.__invocation_arguments: list[tuple[Union[Type[Label], Type[Variable]], str]] = [
            (
                {
                    Label.__name__.lower(): Label,
                    Variable.__name__.lower(): Variable,
                    "Const".lower(): int
                }[match.group("type").lower()],
                match.group("variable_name").upper()
            )
            for match in re.finditer(r"{\s*(?P<type>(Const|" + Label.__name__ + r"|" + Variable.__name__ + r"))\s+" +
                                     r"(?P<variable_name>[A-Z]([A-Z]|\d)*)\s*}",
                                     usage,
                                     flags=re.IGNORECASE)
        ]
        self.__invocation_regex: str = re.sub(r"{\s*(" + Label.__name__ + r"|" + Variable.__name__ + r")\s+" +
                                              r"(?P<argument_name>[A-Z]([A-Z]|\d)*)\s*}",
                                              r"(?P<\g<argument_name>>[A-Z]([A-Z]|\\d)*)",
                                              usage,
                                              flags=re.IGNORECASE)
        self.__invocation_regex: str = re.sub(r"{\s*Const\s+(?P<argument_name>[A-Z]([A-Z]|\d)*)\s*}",
                                              r"(?P<\g<argument_name>>\\d+)",
                                              self.__invocation_regex,
                                              flags=re.IGNORECASE)
        self.__invocation_regex = (
            r"\s*(\[(?P<__sugar_label>[A-E]([1-9][0-9]*)?)\])?\s*" +
            re.sub(r"\s+",
                   r"\\s*",
                   self.__invocation_regex) +
            r"\s*"
        )

        self.__implementation: tuple[str] = implementation
        repeat_counter: int = 0
        for line in self.__implementation:
            if re.fullmatch(r"\s*{\s*REPEAT\s+.+\s*}\s*",
                            line,
                            flags=re.IGNORECASE):
                repeat_counter += 1
            elif re.fullmatch(r"\s*{\s*END\s+REPEAT\s*}\s*",
                              line,
                              flags=re.IGNORECASE):
                if repeat_counter == 0:
                    raise CompilationFailure("No 'REPEAT' for matching 'END REPEAT'!")
                repeat_counter -= 1
        if repeat_counter > 0:
            raise CompilationFailure("No 'END REPEAT' for matching 'REPEAT'!")
        self.__sugars: list[SyntacticSugar] = sugars

    class _VariableGenerator:
        def __init__(self,
                     other_instructions: list[Instruction]):
            self.unused_variable_index: int = max(
                (
                    instruction.sentence.command.variable.index
                    for instruction in other_instructions
                ),
                default=0
            ) + 1

        def generate(self,
                     starting_index: int = 0) -> Variable:
            variable: Variable = Variable("Z", starting_index + self.unused_variable_index)
            self.unused_variable_index += 1
            return variable

    class _LabelGenerator:
        def __init__(self,
                     other_instructions: list[Instruction]):
            self.unused_label_index: int = max(
                max(
                    (
                        instruction.sentence.command.label.index
                        for instruction in other_instructions
                        if type(instruction.sentence.command) is JumpCommand
                    ),
                    default=0
                ),
                max(
                    (
                        instruction.label.index
                        for instruction in other_instructions
                        if instruction.label is not None
                    ),
                    default=0
                )
            ) + 1

        def generate(self,
                     starting_index: int = 0) -> Label:
            label: Label = Label("A", starting_index + self.unused_label_index)
            self.unused_label_index += 1
            return label

    def validate(self,
                 invocation: str) -> bool:
        import re

        return bool(re.fullmatch(self.__invocation_regex,
                                 invocation,
                                 flags=re.IGNORECASE))

    def compile(self,
                invocation: str,
                other_instructions: _Optional[list[Instruction]] = None) -> list[Instruction]:
        import re
        from typing import Union

        if other_instructions is None:
            other_instructions = []

        if invocation_match := re.fullmatch(self.__invocation_regex,
                                            invocation,
                                            flags=re.IGNORECASE):
            if invocation_match.group("__sugar_label") is not None:
                other_instructions += [
                    Instruction(Label.compile(invocation_match.group("__sugar_label")),
                                Sentence(VariableCommand(Variable("Y"), VariableCommandType.NoOp)))
                ]
            variable_generator: SyntacticSugar._VariableGenerator = SyntacticSugar._VariableGenerator(
                other_instructions
            )
            label_generator: SyntacticSugar._LabelGenerator = SyntacticSugar._LabelGenerator(other_instructions)
            fixes_to_perform: dict[Union[Label, Variable], Union[Label, Variable]] = {}

            parameter_replacements: dict[str, str] = {}
            sugar_program_instructions: list[str] = []
            max_sugar_internals: int = 1000000000000000
            # Code smell due to the way the algorithm works with the sugar arguments (replacing them at the start
            # and fixing them later alongside the other variables)
            repeat_counters: list[int] = []
            repeat_start_indices: list[int] = []
            line_index: int = 0
            while line_index < len(self.__implementation):
                if repeat_match := re.fullmatch(r"\s*{\s*REPEAT\s+(?P<const_name>[A-Z]([A-Z]|\d)*)\s*}\s*",
                                                self.__implementation[line_index],
                                                flags=re.IGNORECASE):
                    line_index += 1
                    repeat_counters.append(int(invocation_match.group(repeat_match.group("const_name"))))
                    repeat_start_indices.append(line_index)
                elif re.fullmatch(r"\s*{\s*END\s+REPEAT\s*}\s*",
                                  self.__implementation[line_index],
                                  flags=re.IGNORECASE):
                    repeat_counters[-1] -= 1
                    if repeat_counters[-1] == 0:
                        repeat_counters.pop()
                        repeat_start_indices.pop()
                        line_index += 1
                    else:
                        line_index = repeat_start_indices[-1]
                else:
                    line: str = self.__implementation[line_index]
                    for invocation_argument_type, invocation_argument_name in self.__invocation_arguments:
                        invocation_parameter: str = invocation_match.group(invocation_argument_name)

                        if invocation_argument_type is Label or invocation_argument_type is Variable:
                            if invocation_parameter not in parameter_replacements:
                                if invocation_argument_type is Label:
                                    generated_label: Label = label_generator.generate(max_sugar_internals)
                                    parameter_replacements[invocation_parameter]: str = str(generated_label)
                                    fixes_to_perform[generated_label] = Label.compile(invocation_parameter)
                                else:
                                    generated_variable: Variable = variable_generator.generate(max_sugar_internals)
                                    parameter_replacements[invocation_parameter]: str = str(generated_variable)
                                    fixes_to_perform[generated_variable] = Variable.compile(invocation_parameter)

                        line = re.sub(r"{\s*" + invocation_argument_name + r"\s*}",
                                      parameter_replacements.get(invocation_parameter, invocation_parameter),
                                      line,
                                      flags=re.IGNORECASE)
                    sugar_program_instructions.append(line)
                    line_index += 1

            sugar_program: Program = Program.compile(*sugar_program_instructions,
                                                     sugars=self.__sugars)

            for instruction in sugar_program.instructions:
                if (
                    instruction.label is not None and
                    instruction.label not in fixes_to_perform
                ):
                    fixes_to_perform[instruction.label] = label_generator.generate()
                if (
                    type(instruction.sentence.command) is JumpCommand and
                    instruction.sentence.command.label not in fixes_to_perform
                ):
                    fixes_to_perform[instruction.sentence.command.label] = label_generator.generate()
                if (
                    instruction.sentence.command.variable.name not in {"X", "Y"} and
                    instruction.sentence.command.variable not in fixes_to_perform
                ):
                    fixes_to_perform[instruction.sentence.command.variable] = variable_generator.generate()

            return (
                []
                if (sugar_label := invocation_match.group("__sugar_label")) is None
                else
                [Instruction(
                    Label.compile(sugar_label),
                    Sentence(VariableCommand(
                        Variable("Y"),
                        VariableCommandType.NoOp
                    ))
                )]
            ) + [
                Instruction(
                    fixes_to_perform.get(instruction.label, instruction.label),
                    Sentence(
                        JumpCommand(fixes_to_perform.get(instruction.sentence.command.variable,
                                                         instruction.sentence.command.variable),
                                    fixes_to_perform.get(instruction.sentence.command.label,
                                                         instruction.sentence.command.label))
                        if type(instruction.sentence.command) is JumpCommand
                        else
                        VariableCommand(fixes_to_perform.get(instruction.sentence.command.variable,
                                                             instruction.sentence.command.variable),
                                        instruction.sentence.command.command_type)
                    )
                )
                for instruction in sugar_program.instructions
            ]
        raise CompilationFailure(f"Failed using sugar to compile line: '{invocation}'")


def main() -> None:
    from argparse import ArgumentParser, Namespace
    import re

    argument_parser: ArgumentParser = ArgumentParser(description="S Compiler")
    argument_parser.add_argument("filename",
                                 type=str,
                                 help="File to compile")
    argument_parser.add_argument("-o",
                                 "--output",
                                 type=str,
                                 help="Output program file")
    arguments: Namespace = argument_parser.parse_args()

    with open(arguments.filename, "r") as file_to_compile:
        file_to_compile_content: list[str] = file_to_compile.readlines()

    current_section_lines: list[str] = []
    current_section_title: str = ""
    sugars: list[SyntacticSugar] = []
    is_main: bool = False

    for line_index, line in enumerate(file_to_compile_content):
        if re.fullmatch(r"\s*", line):
            pass
        elif title_match := re.fullmatch(r"\s*>\s*(?P<title>.*)\s*", line):
            if is_main:
                raise CompilationFailure(f"Encountered sugar title after MAIN: '{line}'")

            sugars.append(SyntacticSugar(current_section_title,
                                         *current_section_lines,
                                         sugars=sugars.copy()))
            is_main = bool(re.fullmatch(r"MAIN",
                                        current_section_title := title_match.group("title"),
                                        re.IGNORECASE))
            current_section_lines = []
        elif line_match := re.fullmatch(r"\s*(?P<line>.*)\s*", line):
            current_section_lines.append(line_match.group("line"))
        else:
            raise CompilationFailure(f"Failed to compile line {line_index}: '{line}'")

    program: str = str(Program.compile(*current_section_lines, sugars=sugars))

    with open(arguments.output, "w") as output_file:
        output_file.write(program)


if __name__ == '__main__':
    main()


__all__ = (
    "CompilationFailure",
    "encode_pair",
    "encode_list",
    "Variable",
    "Label",
    "JumpCommand",
    "VariableCommandType",
    "VariableCommand",
    "Sentence",
    "Instruction",
    "Program",
    "SyntacticSugar",
    "main"
)
