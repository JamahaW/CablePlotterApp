from __future__ import annotations


class Regex:
    IDENTIFIER = r"^[a-zA-Z_][a-zA-Z\d_]*$"
    CHAR = r"^'.'$"
    INTEGER = r"^0$|^([+-]?[1-9][\d_]*)$"
    EXPONENT = r"^[-+]?\d+[.]\d+([eE][-+]?\d+)?$"
    HEX_VALUE = r"^0[xX][_\da-fA-F]+$"
    OCT_VALUE = r"^[+-]?0[_0-7]+$"
    BIN_VALUE = r"^0[bB][_01]+$"

    NAME = r"[_a-zA-Z\d]+"
