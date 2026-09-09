"""DB 자동증가 ID를 62진법 문자열로 인코딩해 단축 코드를 만든다."""

_ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
_BASE = len(_ALPHABET)

START_ID = 10000  # 첫 링크(id=1)가 base62(10000)부터 시작하도록 하는 오프셋


def encode(number: int) -> str:
    if number < 0:
        raise ValueError("number는 0 이상이어야 합니다.")
    if number == 0:
        return _ALPHABET[0]

    digits = []
    while number > 0:
        number, remainder = divmod(number, _BASE)
        digits.append(_ALPHABET[remainder])
    return "".join(reversed(digits))


def decode(code: str) -> int:
    number = 0
    for char in code:
        number = number * _BASE + _ALPHABET.index(char)
    return number


def encode_id(link_id: int) -> str:
    """DB의 id(1부터 시작)를 START_ID(10000)부터 시작하는 base62 코드로 변환."""
    return encode(link_id - 1 + START_ID)


def decode_id(code: str) -> int:
    return decode(code) - START_ID + 1
