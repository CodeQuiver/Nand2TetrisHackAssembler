# Project 6: Assembler
Low-level programs written in symbolic machine language are called assembly programs.
Programmers rarely write programs directly in machine language. Rather, programmers who
develop high-performance programs (e.g. system software, mission-critical apps, and software for
embedded systems) often inspect the assembly code generated by compilers. They do so in order
to understand how their high-level code is actually deployed on the target hardware platform, and
how that code can be optimized for gaining better performance. One of the key tools in this
process is the program that translates code written in a symbolic machine language into code
written in binary machine language. This program is called an assembler.

## Objective
Develop an assembler that translates programs written in the Hack assembly language into Hack
binary code. This version of the assembler assumes that the source assembly code is valid. Error
checking, reporting and handling can be added to later versions of the assembler, but are not part
of this project. If you have no programming experience, you can develop a manual assembly
process, as described at the end of this document.

## Contract
When supplied to your assembler as a command-line argument, a Prog.asm file containing a valid
Hack assembly language program should be translated correctly into Hack binary code, and stored
in a file named Prog.hack, located in the same folder as the source file (if a file by this name exists,
it should be overridden). The output produced by your assembler must be identical to the output
produced by the supplied assembler, as described below.

- As I wrote it, this will work with any input file name, but still always output to Prog.hack as specified
    - future improvement: change it to be the same filename as the input, with only suffix changed from ".asm" to ".hack"

## Test programs
Once again, the goal of the assembler is translating Prog.asm files into executable Prog.hack files.
We provide four such test programs (same as those described in Project 4):
- Add.asm: Adds the constants 2 and 3, and puts the result in R0. `nand2tetris\nand2tetris\projects\6\add`
- Max.asm: Computes max(R0, R1) and puts the result in R2.
- Rect.asm: Draws a rectangle at the top left corner of the screen. The rectangle is 16 pixels wide,
and R0 pixels high.
- Pong.asm: A classical single-player arcade game, described in detail in Project 4 (see the executing
machine language programs section). This large assembly file will give your assembler a good
stress-test.