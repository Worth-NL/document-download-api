from io import BytesIO
from pathlib import Path

import pytest

from app.utils import get_mime_type
from app.utils.mime_types_nl import get_mime_type_nl, looks_like_csv_libmagic_5_44

sample_files_path = Path(__file__).parent.parent / "sample_files"

TWO_COLUMN_CSV = b"colour,number\ngreen,three\nblue,four\nred,seven\n"


@pytest.mark.parametrize(
    ["filename", "expected_mime_type"],
    [
        # supported by doc dl
        ("test.pdf", "application/pdf"),
        ("test.csv", "text/plain"),
        ("test_longer.csv", "text/csv"),
        ("test.doc", "application/msword"),
        ("test.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"),
        ("test.odt", "application/vnd.oasis.opendocument.text"),
        ("test.rtf", "text/rtf"),
        ("test.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"),
        ("test.jpeg", "image/jpeg"),
        ("test.png", "image/png"),
        # not supported by doc dl
        ("test.pptx", "application/vnd.openxmlformats-officedocument.presentationml.presentation"),
        # libmagic 5.46 (Debian trixie) no longer reports a plain zip as application/zip
        ("test.zip", "application/octet-stream"),
        ("corrupted.zip", "application/octet-stream"),
    ],
)
def test_get_mime_type_nl(filename, expected_mime_type):
    with open(sample_files_path / filename, "rb") as file:
        assert get_mime_type_nl(file) == expected_mime_type


@pytest.mark.parametrize("path", sorted(sample_files_path.iterdir()), ids=lambda path: path.name)
def test_get_mime_type_nl_only_turns_plain_text_into_csv(path):
    with open(path, "rb") as file:
        upstream_mime_type = get_mime_type(file)
        nl_mime_type = get_mime_type_nl(file)

    assert nl_mime_type == upstream_mime_type or (upstream_mime_type, nl_mime_type) == ("text/plain", "text/csv")


def test_get_mime_type_nl_detects_two_column_csv_reported_as_plain_text(mocker):
    mocker.patch("app.utils.magic.from_buffer", return_value="text/plain")

    assert get_mime_type_nl(BytesIO(TWO_COLUMN_CSV)) == "text/csv"


def test_get_mime_type_nl_keeps_plain_text_that_is_not_csv(mocker):
    mocker.patch("app.utils.magic.from_buffer", return_value="text/plain")

    assert get_mime_type_nl(BytesIO(b"just some text\nover a few\nlines\n")) == "text/plain"


@pytest.mark.parametrize("libmagic_return_value", ["text/csv", "application/pdf", "application/json"])
def test_get_mime_type_nl_passes_other_mime_types_through(libmagic_return_value, mocker):
    mocker.patch("app.utils.magic.from_buffer", return_value=libmagic_return_value)

    assert get_mime_type_nl(BytesIO(TWO_COLUMN_CSV)) == libmagic_return_value


def test_get_mime_type_nl_leaves_stream_at_start():
    stream = BytesIO(TWO_COLUMN_CSV)

    get_mime_type_nl(stream)

    assert stream.read() == TWO_COLUMN_CSV


def _lines(*lines):
    return b"".join(line + b"\n" for line in lines)


@pytest.mark.parametrize(
    ["data", "expected"],
    [
        (_lines(b"a,b", b"c,d", b"e,f"), True),
        (_lines(b"a,b,c", b"d,e,f", b"g,h,i"), True),
        (_lines(b"a,b", b"c,d"), False),
        (b"a,b\nc,d\ne,f", False),
        (_lines(b"a,b", b"c", b"d,e"), False),
        (_lines(b"no commas", b"on any", b"line"), False),
        (_lines(b'"x,y",b', b"c,d", b"e,f"), True),
        (_lines(b'"say ""hi"", ok",b', b"c,d", b"e,f"), True),
        (_lines(b'"multi\nline",b', b"c,d", b"e,f"), True),
        (b"a,b\r\nc,d\r\ne,f\r\n", True),
        (_lines(*[b"a,b"] * 9, b"a,b,c"), False),
        (_lines(*[b"a,b"] * 10, b"a,b,c"), True),
        (_lines(*[b"a,b"] * 12), True),
        (b"", False),
    ],
    ids=[
        "two-columns-three-lines",
        "three-columns-three-lines",
        "two-lines",
        "last-line-without-newline-not-counted",
        "comma-count-mismatch",
        "no-commas",
        "quoted-comma",
        "escaped-quotes",
        "quoted-newline",
        "crlf",
        "mismatch-on-tenth-line",
        "mismatch-after-tenth-line",
        "more-than-ten-lines",
        "empty",
    ],
)
def test_looks_like_csv_libmagic_5_44(data, expected):
    assert looks_like_csv_libmagic_5_44(data) is expected
