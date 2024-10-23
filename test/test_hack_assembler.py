import hack_assembler
import IPython  # use pytest -v -s to eanble IPython embed debugging within a test

# command-line tests to copy-paste:
# python hack_assembler/hack_assembler.py "hack_assembler/translation_target/Add.asm"


class TestAInstruction:

    def test_decimal_1(self):
        assert hack_assembler.a_instruction("@1") == "0" * 15 + "1"

    def test_decimal_2(self):
        assert hack_assembler.a_instruction("@2") == "0" * 14 + "10"

    def test_keyboard(self):
        """should return 0 + the address for KBD which is 24576 or 110 0000 0000 0000"""
        assert hack_assembler.a_instruction("@KBD") == "0110000000000000"


class TestCInstruction:
    # Encodings:
    # 1 1 1 a c1 c2 c3 c4 c5 c6 d1 d2 d3 j1 j2 j3
    def test_d_plus_a(self):
        """
        "D=D+A": "1110000010010000",
        """
        assert hack_assembler.c_instruction("D=D+A") == "1110000010010000"

    def test_m_eq_neg_1(self):
        """
        "M=-1: should encode to "1110111010001000"
        """
        assert hack_assembler.c_instruction("M=-1") == "1110111010001000"

    def test_md_eq_m_plus_1(self):
        """
        "MD=M+1" should encode to "1111110111011000"
        """
        assert hack_assembler.c_instruction("MD=M+1") == "1111110111011000"

    def test_no_dest_comp_d_and_jump_jgt(self):
        """
        "D;JGT" should encode to "1110001100000001"
        """
        assert hack_assembler.c_instruction("D;JGT") == "1110001100000001"

    def test_no_dest_comp_zero_and_jmp(self):
        """
        "0;JMP" should encode to "1110101010000111"
        """
        assert hack_assembler.c_instruction("0;JMP") == "1110101010000111"


class TestHackAssemblerNoSymbols:
    # To run just this class- syntax
    #  pytest hack_assembler/test/test_hack_assembler.py::TestHackAssembler
    def test_add(self):
        result_add = hack_assembler.main("hack_assembler/translation_target/Add.asm")
        assert isinstance(result_add, list)
        assert len(result_add) == 6
        # result as code: ["@2", "D=A", "@3", "D=D+A", "@0", "M=D"]

        expected_result = [
            "0000000000000010",
            "1110110000010000",
            "0000000000000011",
            "1110000010010000",
            "0000000000000000",
            "1110001100001000",
        ]

        for i, expected in enumerate(expected_result):
            assert (
                expected == result_add[i]
            ), f"line {i} expected {expected} but got actual {result_add[i]}"

    def test_maxl(self):
        # ['@0', 'D=M', '@1', 'D=D-M', '@10', 'D;JGT', '@1', 'D=M', '@12', '0;JMP', '@0', 'D=M', '@2', 'M=D', '@14', '0;JMP']
        # Encodings:
        # 1 1 1 a c1 c2 c3 c4 c5 c6 d1 d2 d3 j1 j2 j3
        # IPython.embed()
        # import ipdb

        # ipdb.set_trace()

        result_max = hack_assembler.main("hack_assembler/translation_target/MaxL.asm")
        assert isinstance(result_max, list)

        assert len(result_max) == 16

        assert result_max[0] == "0" * 16  # '@0'  # first line "@0" should be all zeroes
        assert result_max[1] == "1111110000010000"  # 'D=M'
        assert result_max[2] == "0" * 15 + "1"
        assert result_max[3] == "1111010011010000"  # 'D=D-M'
        assert result_max[4] == "0" * 12 + "1010"  # '@10'
        assert result_max[5] == "1110001100000001"  # 'D;JGT' comp;jump
        assert result_max[6] == "0" * 15 + "1"  # @1
        assert result_max[7] == "1111110000010000"  # dest=010  #comp = 1110000 # 'D=M'
        assert result_max[8] == "0" * 12 + "1100"  # '@12'
        assert result_max[9] == "1110101010000111"  # '0;JMP'
        assert result_max[10] == "0" * 16  # '@0'
        assert result_max[11] == "1111110000010000"  # 'D=M'
        assert result_max[12] == "0" * 14 + "10"  # '@2'
        assert result_max[13] == "1110001100001000"  # dest=001  # comp=0001100  # 'M=D'
        assert result_max[14] == "0" * 12 + "1110"  # '@14'
        assert result_max[15] == "1110101010000111"  # '0;JMP'

        expected_output = [
            "0000000000000000",
            "1111110000010000",
            "0000000000000001",
            "1111010011010000",
            "0000000000001010",
            "1110001100000001",
            "0000000000000001",
            "1111110000010000",
            "0000000000001100",
            "1110101010000111",
            "0000000000000000",
            "1111110000010000",
            "0000000000000010",
            "1110001100001000",
            "0000000000001110",
            "1110101010000111",
        ]

        for i, expected in enumerate(expected_output):
            assert (
                expected == result_max[i]
            ), f"line {i} expected {expected} but got actual {result_max[i]}"

    def test_output_written_in_file_add(self):
        result_add = hack_assembler.main("hack_assembler/translation_target/Add.asm")
        assert isinstance(result_add, list)
        assert len(result_add) == 6
        # result as code: ["@2", "D=A", "@3", "D=D+A", "@0", "M=D"]
        assert result_add == [
            "0000000000000010",
            "1110110000010000",
            "0000000000000011",
            "1110000010010000",
            "0000000000000000",
            "1110001100001000",
        ]

        with open("hack_assembler/translation_target/Prog.hack", "r") as output_file:
            for i, line in enumerate(output_file):
                assert (
                    line.removesuffix("\n") == result_add[i]
                ), f"line {i} expected {result_add[i]} but got actual {line.removesuffix("\n")}"

    def test_rectl(self):
        hack_assembler.main("hack_assembler/translation_target/RectL.asm")

        output_file = open("hack_assembler/translation_target/Prog.hack", "r")
        output_lines = output_file.readlines()
        output_file.close()

        with open(
            "hack_assembler/translation_target/Rect_test_expected.hack", "r"
        ) as expected_output_file:
            expected_output_lines = expected_output_file.readlines()
            assert len(output_lines) == len(expected_output_lines)

            for i, actual_line in enumerate(output_lines):
                actual = actual_line.removesuffix("\n")
                expected = expected_output_lines[i].removesuffix("\n")
                assert (
                    actual == expected
                ), f"line {i} expected {expected} but got actual {actual}"

    def test_pongl(self):
        hack_assembler.main("hack_assembler/translation_target/PongL.asm")

        output_file = open("hack_assembler/translation_target/Prog.hack", "r")
        output_lines = output_file.readlines()
        output_file.close()

        with open(
            "hack_assembler/translation_target/Pong_test_expected.hack", "r"
        ) as expected_output_file:
            expected_output_lines = expected_output_file.readlines()
            assert len(output_lines) == len(expected_output_lines)

            for i, actual_line in enumerate(output_lines):
                actual = actual_line.removesuffix("\n")
                expected = expected_output_lines[i].removesuffix("\n")
                assert (
                    actual == expected
                ), f"line {i} expected {expected} but got actual {actual}"


class TestHackAssemblerWithSymbols:
    def test_max(self):

        result_max = hack_assembler.main("hack_assembler/translation_target/Max.asm")
        assert isinstance(result_max, list)

        assert len(result_max) == 16

        expected_output = [
            "0000000000000000",
            "1111110000010000",
            "0000000000000001",
            "1111010011010000",
            "0000000000001010",
            "1110001100000001",
            "0000000000000001",
            "1111110000010000",
            "0000000000001100",
            "1110101010000111",
            "0000000000000000",
            "1111110000010000",
            "0000000000000010",
            "1110001100001000",
            "0000000000001110",
            "1110101010000111",
        ]

        for i, expected in enumerate(expected_output):
            assert (
                expected == result_max[i]
            ), f"line {i} expected {expected} but got actual {result_max[i]}"

    def test_rect(self):
        hack_assembler.main("hack_assembler/translation_target/Rect.asm")

        output_file = open("hack_assembler/translation_target/Prog.hack", "r")
        output_lines = output_file.readlines()
        output_file.close()

        with open(
            "hack_assembler/translation_target/Rect_test_expected.hack", "r"
        ) as expected_output_file:
            expected_output_lines = expected_output_file.readlines()
            assert len(output_lines) == len(expected_output_lines)

            for i, actual_line in enumerate(output_lines):
                actual = actual_line.removesuffix("\n")
                expected = expected_output_lines[i].removesuffix("\n")
                assert (
                    actual == expected
                ), f"line {i} expected {expected} but got actual {actual}"

    def test_pong(self):
        hack_assembler.main("hack_assembler/translation_target/Pong.asm")

        output_file = open("hack_assembler/translation_target/Prog.hack", "r")
        output_lines = output_file.readlines()
        output_file.close()

        with open(
            "hack_assembler/translation_target/Pong_test_expected.hack", "r"
        ) as expected_output_file:
            expected_output_lines = expected_output_file.readlines()
            assert len(output_lines) == len(expected_output_lines)

            for i, actual_line in enumerate(output_lines):
                actual = actual_line.removesuffix("\n")
                expected = expected_output_lines[i].removesuffix("\n")
                assert (
                    actual == expected
                ), f"line {i} expected {expected} but got actual {actual}"
