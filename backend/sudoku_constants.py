from typing import Any
VALUES_9 = list(range(1, 10))
VALUES_12 = list(range(1, 13))
VALUES_16 = list(range(1, 17))
SYMBOLS = {10: 'A', 11: 'B', 12: 'C', 13: 'D', 14: 'E', 15: 'F', 16: 'G'}
LETTER_TO_INT = {v: k for k, v in SYMBOLS.items()}
ALGORITHM_KEYS = ('backtracking', 'brute_force', 'mrv')

def normalize(value: Any) -> str:
    if value in (None, '', 0, '0'):
        return ''
    if isinstance(value, str):
        return value.upper()
    if isinstance(value, int) and value in SYMBOLS:
        return SYMBOLS[value]
    return str(value)

def get_blocks(size: int) -> tuple[int, int]:
    if size == 12:
        return (3, 4)
    if size == 16:
        return (4, 4)
    return (3, 3)

def get_values(size: int) -> list[int]:
    if size == 12:
        return VALUES_12
    if size == 16:
        return VALUES_16
    return VALUES_9
