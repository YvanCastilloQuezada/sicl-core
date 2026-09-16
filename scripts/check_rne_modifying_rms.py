#!/usr/bin/env python3
"""Discover and verify official RM pages related to an RNE standard.

The script checks official gob.pe pages supplied by the operator, extracts
resolution metadata and linked PDFs, and reports candidates. It does not
promote a regulation to VIGENTE; a human authority must validate legal effect.
"""
from __future__ import annotations

import argparse
import json
import re
from html.parser import HTMLParser
from urllib.request import Request, urlopen
from urllib.parse import urljoin

USER_AGENT = "SICL-RFC025-RM-Review/1"
OFFICIAL_HOSTS = ("gob.pe", "www.gob.pe")


class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[dict[str, str]] = []
        self._href = ""
        self._text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "a":
            self._href = dict(attrs).get("href") or ""
            self._text = []

    def handle_data(self, data: str) -> None:
        if self._href:
            self._text.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "a" and self._href:
            self.links.append({"href": self._href, "text": " ".join("".join(self._text).split())})
            self._href = ""
            self._text = []


def fetch(url: str) -> tuple[int, str, str]:
    request = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=20) as response:  # nosec B310: operator-supplied official URL
        return response.status, response.headers.get("content-type", ""), response.read().decode("utf-8", errors="replace")


def inspect_resolution(url: str, standard_code: str) -> dict[str, object]:
    status, content_type, body = fetch(url)
    if "gob.pe" not in url or not url.startswith("https://"):
        raise ValueError("only HTTPS gob.pe URLs are accepted")
    text = " ".join(re.sub(r"<[^>]+>", " ", body).split())
    parser = LinkParser()
    parser.feed(body)
    links = []
    for link in parser.links:
        absolute = urljoin(url, link["href"])
        if "gob.pe" in absolute and ("pdf" in absolute.lower() or "document/file" in absolute):
            links.append({"title": link["text"], "url": absolute})
    resolution = re.search(r"Resolución Ministerial N[.°º]*\s*([0-9]+-\d{4}-VIVIENDA)", text, re.I)
    date = re.search(r"(\d{1,2} de [A-Za-záéíóúñ]+ de \d{4})", text, re.I)
    mentions_standard = standard_code.upper() in text.upper()
    modifying = any(word in text.lower() for word in ("modificar", "modificación", "modifica"))
    return {
        "url": url,
        "http_status": status,
        "content_type": content_type,
        "resolution_number": resolution.group(1) if resolution else None,
        "publication_date_text": date.group(1) if date else None,
        "standard_code": standard_code,
        "standard_mentioned": mentions_standard,
        "modification_language_detected": modifying,
        "linked_official_documents": links,
        "promotion": "HUMAN_REVIEW_REQUIRED",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--standard", required=True, help="RNE code, for example E.030")
    parser.add_argument("--url", action="append", required=True, help="Official gob.pe RM page; repeat for each candidate")
    args = parser.parse_args()
    result = {"tool": "check_rne_modifying_rms/1", "standard": args.standard, "candidates": []}
    for url in args.url:
        try:
            result["candidates"].append(inspect_resolution(url, args.standard))
        except Exception as exc:  # report each candidate without hiding the failure
            result["candidates"].append({"url": url, "error": f"{type(exc).__name__}: {exc}"})
    result["decision"] = "NO_AUTOMATIC_VIGENCY_PROMOTION"
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
