import typing
import s_compiler


class InterpreterError(RuntimeError):
    pass


class Interpreter:
    def __init__(self,
                 program: s_compiler.Program):
        self.program: s_compiler.Program = program
        self.instruction_index = 0
        self.label_map: dict[s_compiler.Label, int] = {}
        for instruction_index, instruction in enumerate(self.program.instructions):
            if instruction.label is not None and instruction.label not in self.label_map:
                self.label_map[instruction.label] = instruction_index

        self.variables: dict[s_compiler.Variable: int] = {}
        for instruction in self.program.instructions:
            if (
                type(instruction.sentence.command) is s_compiler.JumpCommand and
                instruction.sentence.command.label not in self.label_map
            ):
                self.label_map[instruction.sentence.command.label] = len(self.program.instructions)
            self.variables[instruction.sentence.command.variable] = 0
        self.clear_variables()

    def step(self) -> typing.Optional[int]:
        if self.instruction_index < len(self.program.instructions):
            current_instruction: s_compiler.Instruction = self.program.instructions[self.instruction_index]

            if type(current_instruction.sentence.command) is s_compiler.JumpCommand:
                self.instruction_index = (
                    self.label_map[current_instruction.sentence.command.label]
                    if self.variables[current_instruction.sentence.command.variable] != 0
                    else
                    self.instruction_index + 1
                )
            else:
                self.instruction_index += 1

                if current_instruction.sentence.command.command_type == s_compiler.VariableCommandType.Increment:
                    self.variables[current_instruction.sentence.command.variable] += 1
                elif (current_instruction.sentence.command.command_type == s_compiler.VariableCommandType.Decrement and
                      self.variables[current_instruction.sentence.command.variable] > 0):
                    self.variables[current_instruction.sentence.command.variable] -= 1

        if self.instruction_index == len(self.program.instructions):
            return self.variables[s_compiler.Variable("Y", 1)]

    def set_input_variables(self,
                            *x: int) -> None:
        if any(value < 0 for value in x):
            raise InterpreterError("Given negative input values! Only non-negatives in S!")
        self.variables.update({
            variable: value
            for index, value in enumerate(x)
            if (variable := s_compiler.Variable("X", index + 1)) in self.variables
        })

    def clear_variables(self) -> None:
        for key in self.variables:
            self.variables[key] = 0

    def run(self,
            *x: int) -> int:
        self.instruction_index = 0
        self.clear_variables()
        self.set_input_variables(*x)

        while (result := self.step()) is None:
            pass

        return result
