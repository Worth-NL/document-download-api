"""NotifyNL: keep detecting 2-column CSVs as text/csv on libmagic 5.46 (Debian trixie).

libmagic's CSV check (file/file src/is_csv.c) changed in rev 1.15 (2024-05-18, file 5.46): `csv_parse` went from
`tf != 0 ... nl > 2` to `tf > 1 ... nl >= 2`, so every line now needs at least 2 commas. A 2-column CSV is reported as
text/plain, where bookworm's file 5.44 reported text/csv. Without a filename, that would store and serve such a CSV as
a .txt "tekstbestand". `looks_like_csv_libmagic_5_44` ports the 5.44 check, so uploads keep the type they had before
the move to trixie. It only turns text/plain into text/csv, both allowed types, so the allowlist doesn't change.
"""

import re

from app.utils import get_mime_type

# libmagic decides on the first CSV_LINES lines
CSV_LINES = 10

_QUOTE_COMMA_OR_NEWLINE = re.compile(rb'[",\n]')


def _skip_quoted(data: bytes, pos: int) -> int:
    """Port of libmagic's `eatquote`: the position after the quote that closes the field opened before `pos`."""
    while (pos := data.find(b'"', pos)) != -1:
        pos += 1
        if data[pos : pos + 1] != b'"':
            return pos
        # "" is an escaped quote inside the field
        pos += 1
    return len(data)


def looks_like_csv_libmagic_5_44(data: bytes) -> bool:
    """Port of libmagic 5.44's `csv_parse`.

    Every line has the same number of commas, at least 1, outside quoted fields, over at least 3 lines. Only the
    first CSV_LINES lines count, and a last line without a newline doesn't.
    """
    commas = 0  # `nf`: commas on the current line
    commas_per_line = 0  # `tf`: commas on the first line
    lines = 0  # `nl`
    pos = 0
    while match := _QUOTE_COMMA_OR_NEWLINE.search(data, pos):
        char = match.group()
        pos = match.end()
        if char == b'"':
            pos = _skip_quoted(data, pos)
        elif char == b",":
            commas += 1
        else:
            lines += 1
            if lines == CSV_LINES:
                return commas_per_line != 0 and commas_per_line == commas
            if commas_per_line == 0:
                if commas == 0:
                    return False
                commas_per_line = commas
            elif commas_per_line != commas:
                return False
            commas = 0
    return commas_per_line != 0 and lines > 2


def get_mime_type_nl(document_stream):
    mime_type = get_mime_type(document_stream)

    if mime_type == "text/plain":
        data = document_stream.read()
        document_stream.seek(0)
        if looks_like_csv_libmagic_5_44(data):
            return "text/csv"

    return mime_type
