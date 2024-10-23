"""
Accepts argument of path to Prog.asm, containing a valid Hack Assembly Language program.
Translates from Hack Assembly Language to Hack binary code.
Stores resulting binary in Prog.hack, in the same folder as the source,
overwriting if necessary.
"""

import re
import sys
import os

# Constants- rule dicts representing tables

destination_dict = {
    None: "000",
    "M": "001",
    "D": "010",
    "DM": "011",
    "MD": "011",
    "A": "100",
    "AM": "101",
    "MA": "101",
    "AD": "110",
    "DA": "110",
    "ADM": "111",
    "AMD": "111",
    "MDA": "111",
    "MAD": "111",
    "DAM": "111",
    "DMA": "111",
}

jump_dict = {
    None: "000",
    "JGT": "001",
    "JEQ": "010",
    "JGE": "011",
    "JLT": "100",
    "JNE": "101",
    "JLE": "110",
    "JMP": "111",
}

comp_dict = {
    "0": "0101010",
    "1": "0111111",
    "-1": "0111010",
    "D": "0001100",
    "A": "0110000",
    "!D": "0001101",
    "!A": "0110001",
    "-D": "0001111",
    "-A": "0110011",
    "D+1": "0011111",
    "A+1": "0110111",
    "D-1": "0001110",
    "A-1": "0110010",
    "D+A": "0000010",
    "D-A": "0010011",
    "A-D": "0000111",
    "D&A": "0000000",
    "D|A": "0010101",
    "M": "1110000",
    "!M": "1110001",
    "-M": "1110011",
    "M+1": "1110111",
    "M-1": "1110010",
    "D+M": "1000010",
    "D-M": "1010011",
    "M-D": "1000111",
    "D&M": "1000000",
    "D|M": "1010101",
}

# Symbol Table is below- will be dynamically added to
# during label and variable handling
# see pg. 82 in book for specification
# "symbol":"decimal value",
# Note- first address for Variable symbols will be
# RAM 16
symbol_table_dict = {
    "R0": 0,
    "SP": 0,
    "R1": 1,
    "LCL": 1,
    "R2": 2,
    "ARG": 2,
    "R3": 3,
    "THIS": 3,
    "R4": 4,
    "THAT": 4,
    "R5": 5,
    "R6": 6,
    "R7": 7,
    "R8": 8,
    "R9": 9,
    "R10": 10,
    "R11": 11,
    "R12": 12,
    "R13": 13,
    "R14": 14,
    "R15": 15,
    "SCREEN": 16384,
    "KBD": 24576,
}


def a_instruction(instruction: str):
    """If line is an a-instruction, call this function.

    Args:
        instruction (str): individual instruction to encode

    Returns:
        string: 16-bit machine code representation of instruction
    """
    # 1- Set first bit to 0
    # 2- if command is a decimal value, translate to binary using 15 bits
    # 3- if command is a symbol/variable, just return the 0 and nothing else for now
    command = instruction[1:]

    if not command.isdecimal():
        try:
            command = symbol_table_dict[command]
            # fetch decimal encoding
        except KeyError:
            raise KeyError(
                f"{command} not found in symbol table, a-instruction '{instruction}' can't be translated"
            )

    binary_str = "{0:015b}".format(int(command))
    return f"0{binary_str}"


def destination(dest_command: str):
    try:
        return destination_dict[dest_command]
    except KeyError:
        raise KeyError(f"{dest_command} not found in destination table")


def jump(jump_command: str):
    try:
        return jump_dict[jump_command]
    except KeyError:
        raise KeyError(f"{jump_command} not found in jump dict")


def computation(comp_command: str):
    try:
        return comp_dict[comp_command]
    except KeyError:
        raise KeyError(f"{comp_command} not found in computation dict")


def c_instruction(instruction: str):
    """
    If line is an c-instruction, call this function. Outputs 16-bit machine code representation.
    """
    # separate into "computation", "destination", and "jump" fields
    #
    # syntax:
    # dest = comp ; jump
    #
    # encode each field separately
    # recombine them in order
    # 1 1 1 a c1 c2 c3 c4 c5 c6 d1 d2 d3 j1 j2 j3
    # ("a" is part of computation fields)

    # default values
    dest_code = "000"
    comp_code = "0000000"
    jump_code = "000"

    # case 1: dest = comp ; jump
    if ("=" in instruction) and (";" in instruction):
        instruction_list = re.split("=|;", instruction)

        dest_code = destination(instruction_list[0])
        comp_code = computation(instruction_list[1])
        jump_code = jump(instruction_list[2])

    # case 2: dest = comp
    elif ("=" in instruction) and (";" not in instruction):
        instruction_list = re.split("=", instruction)

        dest_code = destination(instruction_list[0])
        comp_code = computation(instruction_list[1])

    # case 3: comp ; jump
    elif (";" in instruction) and ("=" not in instruction):
        instruction_list = re.split(";", instruction)

        comp_code = computation(instruction_list[0])
        jump_code = jump(instruction_list[1])

    else:
        raise ValueError(
            f"c-instruction '{instruction}' lacks required syntax markers of either '=' or ';', cannot be assembled"
        )

    result = f"111{comp_code}{dest_code}{jump_code}"

    # return final binary as string
    return result


def main(path: str):
    """
        1- read file at given path line-by-line
        2- remove comments and whitespace
        3- assemble into list of commands- input_lines_original
        4- deal with symbols/variable substitution- return input_lines_working
        5- parse result of step 4 - process each command
        6- insert translation of commands into output_binary list
        7- write output_binary list line-by-line to Prog.hack at same path as input file
        8- also return output_binary or a success/failure message to be output to console

    Args:
        path (string): Path to <input>.asm, containing a valid Hack Assembly Language program.
    """
    output_binary = []

    print("PATH: " + path)

    with open(path, mode="r") as file:
        # Syntax Notes:
        # `re.sub(r"\s+", "", line)` is for removing all whitespaces- strip only trims leading and trailing
        clean_lines = [
            re.sub(r"\s+|//.*$", "", line)
            for line in file
            if line and (not line.isspace()) and (not line.startswith("//"))
        ]

        # print("CLEAN LINES: " + str(clean_lines))

        for line in clean_lines:
            if line.startswith("@"):
                output_line = a_instruction(line)
                output_binary.append(output_line)
            elif line.startswith("("):
                # ignore label lines
                continue
            else:
                # must be c-instruction
                output_line = c_instruction(line)
                output_binary.append(output_line)

    # print("output_binary: " + str(output_binary))

    path_parent_directory = os.path.dirname(path)  # get path only- cuts off filename

    with open(f"{path_parent_directory}/Prog.hack", "w") as output_file:
        for line in output_binary:
            output_file.write(line + "\n")

    return output_binary


if __name__ == "__main__":
    result = main(sys.argv[1])

    # print any return values to console
    if result:
        print(result)
