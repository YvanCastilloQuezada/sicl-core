"""UCG-NORM-02 — ARKI Spanish semantic text normalization.

This module normalizes semantic TEXT ONLY.
It is not a technical-unit parser or SI canonicalizer.
"""

from __future__ import annotations

import unicodedata


CONTRACT_VERSION = "UCG-NORM-02"


class NormalizationError(ValueError):
    """Raised when semantic text contains invalid input."""


# Deliberately limited to ASCII and Spanish.
# Other scripts are not transliterated or case-folded.
_TRANSLATION = {
    ord("a"): "A", ord("b"): "B", ord("c"): "C", ord("d"): "D",
    ord("e"): "E", ord("f"): "F", ord("g"): "G", ord("h"): "H",
    ord("i"): "I", ord("j"): "J", ord("k"): "K", ord("l"): "L",
    ord("m"): "M", ord("n"): "N", ord("o"): "O", ord("p"): "P",
    ord("q"): "Q", ord("r"): "R", ord("s"): "S", ord("t"): "T",
    ord("u"): "U", ord("v"): "V", ord("w"): "W", ord("x"): "X",
    ord("y"): "Y", ord("z"): "Z",
    ord("á"): "A", ord("Á"): "A",
    ord("é"): "E", ord("É"): "E",
    ord("í"): "I", ord("Í"): "I",
    ord("ó"): "O", ord("Ó"): "O",
    ord("ú"): "U", ord("Ú"): "U",
    ord("ñ"): "Ñ", ord("Ñ"): "Ñ",
    ord("²"): "2", ord("³"): "3",
}


_FORBIDDEN_CATEGORIES = {
    "Cc",  # control
    "Cf",  # format / invisible format controls
    "Cs",  # surrogate
    "Co",  # private use
    "Cn",  # unassigned
    "Zl",  # line separator
    "Zp",  # paragraph separator
    "Me",  # enclosing marks
}


def normalize_semantic_text(value: str) -> str:
    """Normalize semantic text to ARKI's Spanish uppercase convention.

    Rules:
    - Require str input.
    - NFC normalization.
    - Reject forbidden Unicode categories.
    - Convert Unicode Zs spaces to ASCII space.
    - Convert Spanish accented vowels to unaccented uppercase.
    - Preserve Ñ as Ñ.
    - Convert superscript 2 and 3 to plain digits.
    - Convert ASCII lowercase to uppercase.
    - Compact and trim whitespace.
    - Preserve punctuation and unsupported-script characters as-is.
    """
    if not isinstance(value, str):
        raise NormalizationError("SEMANTIC_TEXT_MUST_BE_STRING")

    value = unicodedata.normalize("NFC", value)

    for char in value:
        category = unicodedata.category(char)
        if category in _FORBIDDEN_CATEGORIES:
            raise NormalizationError(
                f"SEMANTIC_UNICODE_CATEGORY_FORBIDDEN:{category}"
            )

    chars = []
    for char in value:
        if unicodedata.category(char) == "Zs":
            chars.append(" ")
        else:
            chars.append(char)

    value = "".join(chars)
    value = value.translate(_TRANSLATION)
    value = " ".join(value.split())
    return value
