# Examples from https://sudoku.com/

# Description: Test cases for sudoku.py

from sudoku import solve

def normalise(s: str) -> str:
    return s.strip().replace(" ", "")

def test_example() -> None:
    EXAMPLE = """
    ___83_6__
    1____5___
    5_3__2497
    __9__83__
    3___1_7_6
    _126_____
    9___2_87_
    ___749__2
    62_3__954
    """

    EXAMPLE_EXPECTED = """
    294837615
    176495238
    583162497
    769258341
    358914726
    412673589
    941526873
    835749162
    627381954
    """

    assert solve(normalise(EXAMPLE)) == normalise(EXAMPLE_EXPECTED)

def test_extreme() -> None:
    EXTREME = """
    _5_____2_
    __64__13_
    4___9____
    ___1____2
    __8_____9
    _3__7_81_
    __39__64_
    ________8
    _7___5___
    """

    EXTREME_EXPECTED="""
    357618924
    896452137
    421793586
    745189362
    218536479
    639274815
    583927641
    962341758
    174865293
    """

    assert solve(normalise(EXTREME)) == normalise(EXTREME_EXPECTED)


def test_hard():
    HARD = """
    8__2____5
    3___8__2_
    2_6743___
    _______7_
    59_3_41__
    __41___3_
    _2___89__
    68____25_
    __5____87
    """

    HARD_EXPECTED = """
    871296345
    349581726
    256743891
    132865479
    598374162
    764129538
    427658913
    683917254
    915432687
    """

    assert solve(normalise(HARD)) == normalise(HARD_EXPECTED)

