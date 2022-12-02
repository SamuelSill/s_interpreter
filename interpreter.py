import compiler as _compiler


class InterpreterError(RuntimeError):
    pass


class Interpreter:
    from typing import Optional as _Optional

    def __init__(self,
                 program: _compiler.Program):
        self.__program: _compiler.Program = program
        self.__instruction_index = 0
        self.__label_map: dict[_compiler.Label, int] = {}
        for instruction_index, instruction in enumerate(self.__program.instructions):
            if instruction.label is not None and instruction.label not in self.__label_map:
                self.__label_map[instruction.label] = instruction_index

        self.__variables: dict[_compiler.Variable: int] = {_compiler.Variable("Y", 1): 0}
        for instruction in self.__program.instructions:
            if (
                type(instruction.sentence.command) is _compiler.JumpCommand and
                instruction.sentence.command.label not in self.__label_map
            ):
                self.__label_map[instruction.sentence.command.label] = len(self.__program.instructions)
            self.__variables[instruction.sentence.command.variable] = 0

    @property
    def program(self) -> _compiler.Program:
        return self.__program

    @property
    def variables(self) -> dict[str, int]:
        return {str(key): value for key, value in self.__variables.items()}

    def step(self) -> _Optional[int]:
        if self.__instruction_index < len(self.__program.instructions):
            current_instruction: _compiler.Instruction = self.__program.instructions[self.__instruction_index]

            if type(current_instruction.sentence.command) is _compiler.JumpCommand:
                self.__instruction_index = (
                    self.__label_map[current_instruction.sentence.command.label]
                    if self.__variables[current_instruction.sentence.command.variable] != 0
                    else
                    self.__instruction_index + 1
                )
            else:
                self.__instruction_index += 1

                if current_instruction.sentence.command.command_type == _compiler.VariableCommandType.Increment:
                    self.__variables[current_instruction.sentence.command.variable] += 1
                elif (current_instruction.sentence.command.command_type == _compiler.VariableCommandType.Decrement and
                      self.__variables[current_instruction.sentence.command.variable] > 0):
                    self.__variables[current_instruction.sentence.command.variable] -= 1

        if self.__instruction_index == len(self.__program.instructions):
            return self.__variables[_compiler.Variable("Y", 1)]

    def reset(self,
              *x: int) -> None:
        if any(value < 0 for value in x):
            raise InterpreterError("Given negative input values! Only non-negatives in S!")

        for key in self.__variables:
            self.__variables[key] = 0
        self.__variables.update({
            variable: value
            for index, value in enumerate(x)
            if (variable := _compiler.Variable("X", index + 1)) in self.__variables
        })

        self.__variables[_compiler.Variable("Y", 1)] = 0
        self.__instruction_index = 0

    def run(self,
            *x: int) -> int:
        self.reset(*x)
        while (result := self.step()) is None:
            pass

        return result


def main() -> None:
    from argparse import ArgumentParser, Namespace

    argument_parser: ArgumentParser = ArgumentParser(description="S Compiler")
    argument_parser.add_argument("-b",
                                 "--binary",
                                 type=str,
                                 help="Binary file to run")
    argument_parser.add_argument("x",
                                 type=int,
                                 nargs="+",
                                 help="The program's input")
    arguments: Namespace = argument_parser.parse_args()

    with open(arguments.binary, "r") as binary_file:
        binary_file_content: list[str] = binary_file.readlines()
    print(Interpreter(_compiler.Program.compile(*binary_file_content)).run(*arguments.x))


if __name__ == '__main__':
    main()


__all__ = (
    "InterpreterError",
    "Interpreter",
    "main"
)
