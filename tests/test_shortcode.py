import pytest

from shorten_link import shortcode


@pytest.mark.parametrize(
    "number,expected",
    [
        (0, "0"),
        (1, "1"),
        (9, "9"),
        (10, "a"),
        (35, "z"),
        (36, "A"),
        (61, "Z"),
        (62, "10"),
        (123, "1Z"),
    ],
)
def test_encode(number, expected):
    assert shortcode.encode(number) == expected


@pytest.mark.parametrize("number", [0, 1, 61, 62, 123, 987654321])
def test_roundtrip(number):
    assert shortcode.decode(shortcode.encode(number)) == number


def test_encode_id_starts_at_10000():
    assert shortcode.decode(shortcode.encode_id(1)) == 10000
    assert shortcode.decode(shortcode.encode_id(2)) == 10001


@pytest.mark.parametrize("link_id", [1, 2, 3, 61, 62, 100000])
def test_encode_id_roundtrip(link_id):
    assert shortcode.decode_id(shortcode.encode_id(link_id)) == link_id
