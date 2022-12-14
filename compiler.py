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
        # noinspection PyTypeChecker
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


_program_recursion_depth: int = 0


@_dataclass(frozen=True)
class Program:
    from typing import Optional as _Optional

    instructions: list[Instruction]

    @staticmethod
    def compile(*program: str,
                sugars: _Optional[list["SyntacticSugar"]] = None,
                verbose: bool = False) -> "Program":
        import re

        if sugars is None:
            sugars = []

        @_dataclass
        class SugarJob:
            sugar: SyntacticSugar
            sugar_invocation: str
            index_to_inject: int

        used_variables: set[Variable] = set()
        used_labels: set[Label] = set()
        sugar_jobs: list[SugarJob] = []
        instructions: list[Instruction] = []

        def update_used_labels_and_variables_by_instruction(*instructions_: Instruction) -> None:
            for instruction in instructions_:
                used_variables.add(instruction.sentence.command.variable)

                if instruction.label is not None:
                    used_labels.add(instruction.label)

                if type(instruction.sentence.command) is JumpCommand:
                    used_labels.add(instruction.sentence.command.label)

        global _program_recursion_depth
        _program_recursion_depth += 1

        try:
            for line in program:
                try:
                    instructions.append(Instruction.compile(line))
                    update_used_labels_and_variables_by_instruction(instructions[-1])
                except CompilationFailure as compilation_failure:
                    any_sugar_valid: bool = False
                    for sugar in sugars:
                        if sugar.validate(line):
                            for parameter in sugar.parameters(line):
                                if type(parameter) is Label:
                                    used_labels.add(parameter)
                                elif type(parameter) is Variable:
                                    used_variables.add(parameter)
                            if label_match := re.fullmatch(r"\s*\[\s*(?P<sugar_label>[A-E]([1-9][0-9]*)?)\s*].*", line):
                                used_labels.add(new_label := Label.compile(label_match.group("sugar_label")))
                                instructions.append(Instruction(new_label,
                                                                Sentence(VariableCommand(Variable("Y"),
                                                                                         VariableCommandType.NoOp))))
                            any_sugar_valid = True
                            sugar_jobs.append(SugarJob(sugar, line, len(instructions)))
                            break
                    if not any_sugar_valid:
                        raise compilation_failure

            for sugar_job_index, sugar_job in enumerate(sugar_jobs):
                if verbose:
                    print("| " * (_program_recursion_depth - 1) + f"Compiling '{sugar_job.sugar_invocation}' "
                                                                  f"('{sugar_job.sugar.title}')")
                instructions_to_inject: list[Instruction] = sugar_job.sugar.compile(sugar_job.sugar_invocation,
                                                                                    used_labels,
                                                                                    used_variables,
                                                                                    verbose)
                update_used_labels_and_variables_by_instruction(*instructions_to_inject)
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
        finally:
            _program_recursion_depth -= 1

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
        prime_list: list[int] = primerange(max(factorization) + 1)
        return Program(
            [
                Instruction.decode(factorization.get(p, 0))
                for p in prime_list
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


@_dataclass(frozen=True)
class Const:
    value: int


class SyntacticSugar:
    from typing import (
        Optional as _Optional,
        Union as _Union
    )

    def __init__(self,
                 usage: str,
                 *implementation: str,
                 sugars: _Optional[list["SyntacticSugar"]] = None):
        import re
        from typing import Type, Union

        if sugars is None:
            sugars = []

        supported_types_patterns: dict[Union[Type[Label], Type[Variable], Type[Const]], str] = {
            Label: r"[A-E]([1-9][0-9]*)?",
            Variable: r"[XYZ]([1-9][0-9]*)?",
            Const: r"(([1-9][0-9]*)|0)"
        }

        self.__title: str = usage

        usage = re.sub(r"(?P<special_char>[*+\-|^\\&~#])",
                       r"\\\g<special_char>",
                       usage.strip())
        self.__invocation_arguments: dict[str, Union[Type[Const], Type[Variable], Type[Label]]] = {}
        for match in re.finditer(r"{\s*(?P<type>(" +
                                 r"|".join(actual_type.__name__
                                           for actual_type in supported_types_patterns) +
                                 r"))\s+" +
                                 r"(?P<variable_name>[A-Z]([A-Z]|\d)*)\s*}",
                                 usage,
                                 flags=re.IGNORECASE):
            variable_name: str = match.group("variable_name").upper()
            variable_type: Union[Type[Const], Type[Label], Type[Variable]] = {
                supported_type.__name__.lower(): supported_type
                for supported_type in supported_types_patterns
            }[match.group("type").lower()]

            if variable_name in self.__invocation_arguments:
                if self.__invocation_arguments[variable_name] != variable_type:
                    raise CompilationFailure(f"Sugar back-reference does not maintain the same type "
                                             f"({self.__invocation_arguments[variable_name]} != {variable_type})")
            else:
                self.__invocation_arguments[variable_name] = variable_type

        for invocation_argument, supported_type in self.__invocation_arguments.items():
            usage = re.sub(r"{\s*" + supported_type.__name__ + r"\s+" +
                           invocation_argument + r"\s*}",
                           r"(?P<" + invocation_argument + r">" +
                           supported_types_patterns[supported_type] + r")",
                           usage,
                           count=1,
                           flags=re.IGNORECASE)
        usage = re.sub(r"{\s*(Const|" + Label.__name__ + r"|" + Variable.__name__ + r")\s+" +
                       r"(?P<argument_name>[A-Z]([A-Z]|\d)*)\s*}",
                       r"(?P=\g<argument_name>)",
                       usage,
                       flags=re.IGNORECASE)

        usage = (
            r"\s*(\[[A-E]([1-9][0-9]*)?\])?\s*" +
            re.sub(r"\s+", r"\\s*", usage) +
            r"\s*"
        )

        self.__invocation_regex: re.Pattern[str] = re.compile(usage,
                                                              flags=re.IGNORECASE)

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
                     other_variables: set[Variable]):
            self.__unused_variable_index: int = max((variable.index
                                                     for variable in other_variables),
                                                    default=0) + 1

        def generate(self,
                     starting_index: int = 0) -> Variable:
            variable: Variable = Variable("Z", starting_index + self.__unused_variable_index)
            self.__unused_variable_index += 1
            return variable

    class _LabelGenerator:
        def __init__(self,
                     other_labels: set[Label]):
            self.__unused_label_index: int = max((label.index for label in other_labels),
                                                 default=0) + 1

        def generate(self,
                     starting_index: int = 0) -> Label:
            label: Label = Label("A", starting_index + self.__unused_label_index)
            self.__unused_label_index += 1
            return label

    def validate(self,
                 invocation: str) -> bool:
        import re

        return bool(re.fullmatch(self.__invocation_regex,
                                 invocation))

    @property
    def title(self) -> str:
        return self.__title

    def __str__(self) -> str:
        return self.__title

    def compile(self,
                invocation: str,
                other_labels: _Optional[set[Label]] = None,
                other_variables: _Optional[set[Variable]] = None,
                verbose: bool = False) -> list[Instruction]:
        import re
        from typing import Union

        other_labels = set() if other_labels is None else other_labels.copy()
        other_variables = set() if other_variables is None else other_variables.copy()

        if invocation_match := re.fullmatch(self.__invocation_regex, invocation):
            variable_generator: SyntacticSugar._VariableGenerator = SyntacticSugar._VariableGenerator(other_variables)
            label_generator: SyntacticSugar._LabelGenerator = SyntacticSugar._LabelGenerator(other_labels)
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
                    if repeat_counters[-1] <= 0:
                        repeat_counters.pop()
                        repeat_start_indices.pop()
                        line_index += 1
                    else:
                        line_index = repeat_start_indices[-1]
                elif len(repeat_counters) == 0 or repeat_counters[-1] > 0:
                    line: str = self.__implementation[line_index]
                    for invocation_argument_name, invocation_argument_type in self.__invocation_arguments.items():
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
                else:
                    line_index += 1

            sugar_program: Program = Program.compile(*sugar_program_instructions,
                                                     sugars=self.__sugars,
                                                     verbose=verbose)

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

            return [
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

    def parameters(self,
                   invocation: str) -> list[_Union[Label, Variable]]:
        import re

        if invocation_match := re.fullmatch(self.__invocation_regex, invocation):
            return [
                invocation_argument_type.compile(invocation_match.group(invocation_argument_name))
                for invocation_argument_name, invocation_argument_type in self.__invocation_arguments.items()
                if invocation_argument_type in {Label, Variable}
            ]
        raise CompilationFailure(f"Failed to determine sugar parameters of: '{invocation}'")


def compile_slang(slang_file_path: str,
                  verbose: bool = False) -> Program:
    import re

    with open(slang_file_path, "r") as file_to_compile:
        file_to_compile_content: list[str] = file_to_compile.readlines()

    current_section_lines: list[str] = []
    current_section_title: str = ""
    sugars: list[SyntacticSugar] = []
    is_main: bool = False
    is_before_first_sugar: bool = True

    for line_index, line in enumerate(file_to_compile_content):
        if re.fullmatch(r"\s*(#(\s|.)*)?\s*", line):
            pass
        elif title_match := re.fullmatch(r"\s*>\s*(?P<title>.*)\s*", line):
            if is_main:
                raise CompilationFailure(f"Encountered sugar title after MAIN: '{line}'")

            if is_before_first_sugar:
                is_before_first_sugar = False
            else:
                sugars.append(SyntacticSugar(current_section_title,
                                             *current_section_lines,
                                             sugars=sugars.copy()))
            is_main = bool(re.fullmatch(r"\s*MAIN\s*",
                                        current_section_title := title_match.group("title").split("#")[0].strip(),
                                        re.IGNORECASE))
            current_section_lines = []
        elif line_match := re.fullmatch(r"\s*(?P<line>.*)\s*", line):
            current_section_lines.append(line_match.group("line").split("#")[0].strip())
        else:
            raise CompilationFailure(f"Failed to compile line {line_index}: '{line}'")

    if not is_main:
        raise CompilationFailure("Nonexistent 'MAIN' section!")

    return Program.compile(*current_section_lines,
                           sugars=sugars,
                           verbose=verbose)


def main() -> None:
    from argparse import ArgumentParser, Namespace
    from time import time

    argument_parser: ArgumentParser = ArgumentParser(description="S Compiler")
    input_source_group = argument_parser.add_mutually_exclusive_group(required=True)
    input_source_group.add_argument("-f",
                                    "--file",
                                    type=str,
                                    default=None,
                                    help="File to compile")
    input_source_group.add_argument("-d",
                                    "--decode",
                                    type=int,
                                    default=None,
                                    help="The program encoding")
    compiler_output = argument_parser.add_mutually_exclusive_group(required=True)
    compiler_output.add_argument("-o",
                                 "--output",
                                 type=str,
                                 help="Output binary file",
                                 default=None)
    compiler_output.add_argument("-e",
                                 "--encode",
                                 action="store_true",
                                 help="If present, print out the encoding of the program.\n"
                                      "NOTE: DO NOT use this flag for large binaries as it can "
                                      "result in IMPOSSIBLY SLOW calculations")
    compiler_output.add_argument("-p",
                                 "--print",
                                 action="store_true",
                                 help="If present, simply print out the compiled output")
    argument_parser.add_argument("-v",
                                 "--verbose",
                                 action="store_true",
                                 help="If present, print additional verbose compilation info")
    arguments: Namespace = argument_parser.parse_args()

    start_time: float = time()
    compiled_program: Program = (
        compile_slang(arguments.filename, arguments.verbose)
        if arguments.decode is None
        else Program.decode(arguments.decode)
    )
    time_taken_to_compile: float = time() - start_time

    if arguments.verbose and arguments.filename is not None:
        print()
    print(f"Finished compiling program (took {time_taken_to_compile:0.2f} seconds).")

    if arguments.output or arguments.print:
        program: str = str(compiled_program)
        if arguments.output:
            with open(arguments.output, "w") as output_file:
                output_file.write(program)

            print(f"Saved to binary: \"{arguments.output}\"")
        else:
            print(f"\n"
                  f"The Program:\n"
                  f"{program}")
    elif arguments.encode:
        print(f"It encodes to the value of {compiled_program.encode()}.")


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
    "compile_slang",
    "main"
)
