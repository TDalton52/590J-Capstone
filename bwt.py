# from https://en.wikipedia.org/wiki/Burrows%E2%80%93Wheeler_transform
# Modified to use : and ; instead of \x02 and \x03

def bwt(s: str) -> str:
    """Apply Burrows–Wheeler transform to input string."""
    assert ":" not in s and ";" not in s, "Input string cannot contain : and ; characters"
    s = ":" + s + ";"  # Add start and end of text marker
    table = sorted(s[i:] + s[:i] for i in range(len(s)))  # Table of rotations of string
    last_column = [row[-1:] for row in table]  # Last characters of each row
    return "".join(last_column)  # Convert list of characters into string

def ibwt(r: str) -> str:
    """Apply inverse Burrows–Wheeler transform."""
    table = [""] * len(r)  # Make empty table
    for i in range(len(r)):
        table = sorted(r[i] + table[i] for i in range(len(r)))  # Add a column of r
    s = [row for row in table if row.endswith(";")][0]  # Find the correct row (ending in ETX)
    return s.rstrip(";").strip(":")  # Get rid of start and end markers
