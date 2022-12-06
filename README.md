# S Compiler & Interpreter

## Table of Contents
- [The S Language](#The-S-Language)
  - [The Model](#The-Model)
    - [Variables](#Variables)
    - [Labels](#Labels)
    - [Instructions](#Instructions)
    - [The Program](#The-Program)
    - [Example](#Example)
    - [Syntactic Sugars](#Syntactic-Sugars)
  - [Encoding](#Encoding)
    - [PairWise](#PairWise)
    - [ListWise](#ListWise)
    - [Instruction Encoding](#Instruction-Encoding)
    - [Program Encoding](#Program-Encoding)
  - [Conventions](#Conventions)
- [The S Compiler](#The-S-Compiler)
  - [Compiler Usage](#Compiler-Usage)
  - [Slang Files](#Slang-Files)
    - [MAIN](#MAIN)
    - [Sugar Sections](#Sugar-Sections)
      - [Sugar Types](#Sugar-Types)
      - [REPEAT Statement](#REPEAT-Statement)
      - [The REPEAT Tradeoff](#The-REPEAT-Tradeoff)
  - [The Algorithm](#The-Algorithm)
      - [Sugar Parsing](#Sugar-Parsing)
      - [Compiling the Code](#Compiling-the-Code)
      - [Sugar Expansion](#Sugar-Expansion)
- [The S Interpreter](#The-S-Interpreter)
  - [Interpreter Usage](#Interpreter-Usage)
## The S Language

---
`The S Language` is a [model of computation](https://en.wikipedia.org/wiki/Model_of_computation) 
that is taught in course _Theory of Computation_ at _The Academic College of Tel Aviv, Israel_.
### The Model
#### Variables
The main thing to note about the `S Language`, is that it only supports non-negative integers.

The language supports three different variable types:
- **Input Variables**: `X1`/`X`, `X2`, `X3`...
- **Temporary/Work Variables**: `Z1`/`Z`, `Z2`, `Z3`...
- **One Output Variable**: `Y1`/`Y`
#### Labels
You can mark instructions in the `S Language` with labels.

The label names could only be of the following:

`A1`/`A`, `B1`/`B`, `C1`/`C`, `D1`/`D`, `E1`/`E`,
`A2`, `B2`, ..., `E2`, `A3`, `B3`, ...
#### Instructions
`The S Language` only supports 4 different instructions:

Given any variable `V` and label `L`:
- `V <- V` - A blank instruction (do nothing)
- `V <- V + 1` - Increment `V` by 1
- `V <- V - 1` - If `V` is `0`, do nothing. Otherwise decrement `V` by 1
- `IF V != 0 GOTO L` - If `V` isn't `0`, jump to the first occurrence of label `L` (if nonexistent the program exits), 
  otherwise continue from the next instruction.
#### The Program
A program written in the `S Language` is composed of a series of instructions, with or without labels.

At the start of the program, all variables are initialized to `0`.

Only the input variables (`X1`, `X2`, ...) are initialized with the user input. 
All input variables that weren't given before running the program are also initialized to `0`.

A given program may behave in one of two ways:
- Run infinitely, in which case it returns nothing
- Finish running, in which case ONLY the value of variable `Y` is returned

The program runs the instructions sequentially one after the other (unless a jump is performed), 
and may exit by two ways:
- If it reaches the end of the program
- If it performs a jump to a nonexistent _label_.
#### Example
Lets write a program that always returns the value of its first input (`X1`).

Our first approach would be to write something like this:
```
[A] X <- X - 1
    Y <- Y + 1
    IF X != 0 GOTO A
```
This program does the trick for all inputs except for `X = 0`.

Let's fix the edge case:
```
    IF X != 0 GOTO A
    Z <- Z + 1
    IF Z != 0 GOTO E
[A] X <- X - 1
    Y <- Y + 1
    IF X != 0 GOTO A
```
Notice that in order to jump unconditionally to non-existent label `E` (and therefore exit), 
we had to increment a temporary variable to make sure it's not `0`.
#### Syntactic Sugars
Due to the simplicity of the `S Language`, we might want to define conventions 
for patterns that often appear in our code.

Take for example the unconditional jump pattern to some label `L`:
```
Z <- Z + 1
IF Z != 0 GOTO L
```
We can agree that whenever someone writes `GOTO L` in their program, it would mean that they wrote the above pattern.

Of course the `Z` variable would have to be unique and unused anywhere in the program, and not hard-coded `Z`.
We wouldn't want our sugars to change the rest of the program's functionality.

This **DOES NOT MEAN that** `GOTO L` is now a supported instruction in the `S Language`. 
It's just a convention between us programmers. 

To compile a program that uses syntactic sugars, 
we'd still need to expand them to their underlying instructions.

The syntactic sugars will allow us to write higher level code while still respecting the language's restrictions.
### Encoding
Since our language only supports integers, 
we might want to encode structured data into integers so that we can process it.
#### PairWise
If we wish to encode the pair _<a, b>_ where `a`, `b` are non-negative integers, we follow the formula:

$$\left< a, b \right> = 2^a(2b + 1) - 1$$
#### ListWise
If we wish to encode the list _[e<sub>1</sub>, e<sub>2</sub>, ..., e<sub>n</sub>]_, 
where all elements are non-negative integers, we follow the formula:

$$[e_1, e_2, ..., e_n] = \sum_{i=1}^n p_i^{e_i}$$

Where _p<sub>i</sub>_ is the prime at position _i_ (e.g p<sub>1</sub>=2, p<sub>3</sub>=5)

* Notice that adding _0_ to the end of the list does not change its encoding.
Therefore, if we wish to know the length of the list, we assume it won't end with _0_ elements.
#### Instruction Encoding
<ins>Encoding Variables</ins>: If we wish to encode a given variable, 
we just look at its index in the following sequence:

`Y`, `X1`, `Z1`, `X2`, `Z2`, `X3`, `Z3`, ...

* For example, `#Y` = 1, `#Z2` = 5 etc.

<ins>Encoding Labels</ins>: If we wish to encode a given label, we just look at its index in the following sequence:

`A1`, `B1`, `C1`, `D1`, `E1`, `A2`, `B2`, ...

* For example, `A1` = 1, `#C1` = 3 etc.

<ins>Encoding Instructions:</ins> If we wish to encode a given instruction (with or without label), 
it is encoded as _<a, <b, c>_, where:

- <ins>**_a_**</ins>:
  - _0_ if the instruction has no label 
  - Otherwise the encoding of the label
- <ins>**_b_**</ins>: 
  - _0_ if `V <- V`
  - _1_ if `V <- V + 1`
  - _2_ if `V <- V - 1`
  - (_2_ + `#L`) if `IF V != 0 GOTO L` 
- <ins>**_c_**</ins>: `#V` - _1_ where `V` is the variable in the instruction
#### Program Encoding
If we wish to encode the program:
```
I1
I2
.
.
.
In
```

We just follow the formula:

\#[\#_I<sub>1</sub>_, \#_I<sub>2</sub>_, ..., \#_I<sub>n</sub>_] - _1_

* Notice that the encoding for `Y <- Y` is 0.
  This means that adding such instruction without a label to the end of a program **will not** change its encoding.
  This is problematic, so as a convention, no program will end with `Y <- Y` without a label.
### Conventions
- If the index of a variable/label is 1, we can omit it.
- No program will end with a non-labeled `Y <- Y` instruction.
- Although it's not mandatory, label `E` (`E1`) is never used as a label of an instruction,
  so that we can always jump to it if we wish to exit the program.
## The S Compiler

--- 
`The S Compiler` is the central module of this repository.

In short, it allows us to easily compile `slang` files to binaries that the `S Interpreter` can run.

### Compiler Usage
To compile a given `slang` file to a binary file, run the following command:

```
python compiler.py <slang-file-path> -o <binary-file-path>
```
### Slang Files
In order to compile `S Language` code, 
we write it in `.slang` files as a convention.

Notice that the compiler is inherently case and whitespace insensitive.
The compiler only considers the line continuations between instructions,
and between separate words/variables in the same instruction.

`.slang` files are structured into sections, as follows:
#### MAIN
The `MAIN` section will contain the actual program you wish to compile.

Take the following example:

```
> MAIN
        IF X != 0 GOTO A
        Z <- Z + 1
        IF Z != 0 GOTO E
    [A] X <- X - 1
        Y <- Y + 1
        IF X != 0 GOTO A
```
* This program returns the value of `X1` for any input.
* Again, note that the indentation is only for ease of reading, and the compiler completely ignores it.
#### Sugar Sections
The previous example uses the pattern of the `GOTO L` syntactic sugar.

What if we wanted to use this pattern multiple times?
We can define and use a syntactic sugar like so:
```
> GOTO {Label L}
        Z <- Z + 1
        IF Z != 0 GOTO {L}

> MAIN
        IF X != 0 GOTO A
        GOTO E
    [A] X <- X - 1
        Y <- Y + 1
        IF X != 0 GOTO A
```
* Notice that in the definition of the sugar, we specified the type of `L`.
This sugar will only be used if we pass it with a valid label.
* The compiler makes sure that in the compiled output, 
  variable `Z` that was used inside the `GOTO` implementation DOES NOT collide with variable `Z` 
  if it were used outside the sugar. We are safe to use any temporary variables inside sugar implementations.
* A given sugar may only use other sugars that are defined before it in the file.
* Sugar definitions are allowed to overlap in terms of their usage patterns. 
  The sugar that will eventually be used in the compiled output is the first in the file that matches the string.
##### Sugar Types
When defining sugars, we need to specify the type of their arguments.

The supported sugar argument types are:
* `Label` - To only match labels
* `Variable` - To only match variables
* `Const` - To only match const numbers (e.g _0, 1, 2, 3,_ ...)


_Note that you can overload sugar definitions only differing by the sugar arguments' types!_

While it seems pretty clear as to how `Label`/`Variable` are used, how would one use `Const` in valid S Language?

Well, there is only one way to use a `Const`, and that is with the `REPEAT` statement.
##### REPEAT Statement
Say for example we wanted to implement the sugar for `V += 5`.

Well, we'll just write it like so:

```
> {Variable V} += 5
      {V} <- {V} + 1
      {V} <- {V} + 1
      {V} <- {V} + 1
      {V} <- {V} + 1
      {V} <- {V} + 1
```
But what if we wanted to implement the sugar ` V += k` for ANY const number `k`?

* (Notice the difference here between a const number `k` and a variable `V`.
While on a variable we can perform our regular `S` instructions, 
a const is a value that's known **IN COMPILE-TIME** and is not stored anywhere)
  
In that case, we'd have to use the `REPEAT` statement:

```
> {Variable V} += {Const K}
      {REPEAT K}
      {V} <- {V} + 1
      {END REPEAT}
```
You might be thinking: "This is cheating! REPEAT is not a sugar nor is it a supported instruction!".

Well, as explained before, syntactic sugars are only A CONVENTION 
that we can all agree on when writing `S Language` code.

The `REPEAT` keyword is a convention for consts, that the lines shall be repeated as the size of the const.

If you still think it's cheating, you're welcome to implement `V += k` as many times as you want for different `k`'s.
##### The REPEAT Tradeoff
Currently, the only supported functionality of `Const` types is the `REPEAT` statement.
The initial plan was to implement another functionality called `{REPEAT I TO K}`.

Similarly to `REPEAT`, it would repeat the block `K` times, but it would also allow us to use another
compile-time variable `I`, that would represent the current block repetition index.
This way, we can repeat the block while still changing the behavior of how it generates based 
on the value of const variable `I`.
We could even perform a nested `{REPEAT I}` based on const value `I`.

But we can go even further:
Given a const `K`, we can write a `Python` function that generates different instructions based on `K`'s value! 
After all, sugars are a convention and therefore if we all agree that a given sugar is compiled by the output
of a `Python` function, there should be no problem!

But if we do that, we might aswell write our code in `Python` or some other high level language instead of `S`.

So that is why consts only support the `REPEAT` keyword.
Any more keyword that we add will remove us of the challenge of writing in `S`, and defeat the purpose altogether.

You can still do meta-programming in `S` if you want though. Just not with consts 
(as `S` does not natively support them).
### The Algorithm
#### Sugar Parsing
Firstly, the compiler parses the different sugar sections and generates regex patterns 
that would detect potential usages for each sugar.
It also validates the sugar's most basic syntax, 
like making sure that for each `REPEAT` keyword comes an `END REPEAT` eventually.

#### Compiling The Code
The compiler starts with the `MAIN` section.

It goes over each instruction in the section:
- If it's a supported `S` instruction, just compile it as usual
- Otherwise, go over all known sugars in order, and find the first matching sugar.
  - If there is none, the program does not compile.
  - Otherwise, the compiler saves the sugar and its matching occurrence for later compilation.

The compiler then goes over all sugars that were saved for later compilation and
expands each sugar in-place (using the previously compiled instructions to avoid name collision).

#### Sugar Expansion
The sugar expansion algorithm is probably where most of the brains of the compiler lies.

It's a bit too intricate to be discussed here, 
so it is recommended you read the algorithm in file [compiler.py](compiler.py), under the `SyntacticSugar.compile` function.

## The S Interpreter
While the `S Compiler` does all the work of compiling `.slang` files to binaries,
the interpreter's purpose is only to run those compiled binaries.

### Interpreter Usage
To run the interpreter on a given binary file, run the following command:
```
python interpreter.py <x1-input> <x2-input> ... <xn-input> -b <binary-file-path>
```
The interpreter will print out the result of the binary on the given input.
