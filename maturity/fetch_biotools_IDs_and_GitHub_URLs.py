#!/usr/bin/env python3
import sys
import json
import io
import gzip
import csv
import re
import urllib.request

BIOTOOLS_API_URL = "https://bio.tools/api/tool/"
OUTPUT_JSON = "backup.json"
OUTPUT_CSV = "biotools_github_map.csv"


def main():
    json_fname = OUTPUT_JSON if (len(sys.argv) < 2) else sys.argv[1]

    reader = BiotoolsReader()
    it = reader.iterator  # BiotoolsIterator yielding one tool (bytes) at a time

    # --- write JSON backup (streamed array) and CSV mapping in one pass ---
    with open(json_fname, "wb") as jf, open(
        OUTPUT_CSV, "w", newline="", encoding="utf-8"
    ) as cf:
        writer = csv.DictWriter(cf, fieldnames=["biotoolsID", "github_urls"])
        writer.writeheader()

        jf.write(b"[")
        first = True

        for tool_bytes in it:
            # write JSON (comma between items)
            if not first:
                jf.write(b",")
            jf.write(tool_bytes)
            first = False

            # parse and write CSV row
            try:
                tool = json.loads(tool_bytes.decode("utf-8"))
            except Exception:
                continue

            biotools_id = str(tool.get("biotoolsID", "")).strip()
            urls = extract_github_urls(tool)

            writer.writerow(
                {
                    "biotoolsID": biotools_id,
                    "github_urls": ";".join(urls) if urls else "",
                }
            )

        jf.write(b"]")

    print(f"Wrote JSON to {json_fname}")
    print(f"Wrote CSV  to {OUTPUT_CSV}")


# -----------------------------
# Streaming reader (unchanged)
# -----------------------------
class BiotoolsReader(io.RawIOBase):
    def __init__(self):
        self.isclosed = None
        self.leftover = [ord("[")]
        self.iterator = BiotoolsIterator()

    def readinto(self, buffer: bytearray):
        size = (
            len(self.leftover)
            if (self.isclosed or len(self.leftover) > 0)
            else len(buffer)
        )
        while len(self.leftover) < size:
            tool = next(self.iterator, None)
            if tool is None:
                self.leftover.append(ord("]"))
                self.isclosed = True
                break
            if self.isclosed is not None:
                self.leftover.append(ord(","))
            else:
                self.isclosed = False
            self.leftover.extend(tool)
        if len(self.leftover) == 0:
            return 0
        output, self.leftover = self.leftover[:size], self.leftover[size:]
        buffer[: len(output)] = output
        return len(output)

    def readable(self):
        return True


class BiotoolsIterator:
    def __init__(self):
        self.iterator = None
        self.next_page = ""

    def __iter__(self):
        return self

    def __next__(self):
        while True:
            if self.iterator is None:
                page = self.get_page()
                biotools = page.get("list")
                self.iterator = iter(biotools)
                self.next_page = page.get("next")
            try:
                biotool = next(self.iterator)
                return json.dumps(biotool).encode("utf-8")
            except StopIteration:
                if self.next_page is None:
                    raise StopIteration
                self.iterator = None

    def get_page(self):
        req = urllib.request.Request(BIOTOOLS_API_URL + self.next_page)
        req.add_header("Accept", "application/json")
        req.add_header("Accept-Encoding", "gzip")
        res = urllib.request.urlopen(req)
        if res.getcode() < 300:
            data = res.read()
            return json.loads(data)
        print("error reading data", req)


# -----------------------------
# GitHub URL extraction helpers
# -----------------------------
_GH_HOST = "github.com"


def extract_github_urls(tool: dict) -> list[str]:
    urls: list[str] = []

    # repository / repositories
    for key in ("repository", "repositories"):
        if key in tool:
            urls.extend(_extract_urls_from_field(tool[key]))

    # link[].url
    if isinstance(tool.get("link"), list):
        for link in tool["link"]:
            if isinstance(link, dict):
                u = link.get("url")
                if isinstance(u, str) and _GH_HOST in u.lower():
                    urls.append(u)

    # homepage
    hp = tool.get("homepage")
    if isinstance(hp, str) and _GH_HOST in hp.lower():
        urls.append(hp)

    # other possible locations
    for key in ("download", "sourceCode", "source", "codeRepository"):
        if key in tool:
            urls.extend(_extract_urls_from_field(tool[key]))

    # fallback: scan all strings
    if not urls:
        for s in _iter_strings(tool):
            if isinstance(s, str) and _GH_HOST in s.lower():
                urls.append(s)

    # deduplicate, preserve order
    seen = set()
    uniq = []
    for u in urls:
        u = u.strip()
        if u and u not in seen:
            seen.add(u)
            uniq.append(u)
    return uniq


def _extract_urls_from_field(field) -> list[str]:
    out = []
    if isinstance(field, str):
        if _GH_HOST in field.lower():
            out.append(field)
    elif isinstance(field, list):
        for item in field:
            if isinstance(item, str):
                if _GH_HOST in item.lower():
                    out.append(item)
            elif isinstance(item, dict):
                for k in ("url", "href", "link"):
                    v = item.get(k)
                    if isinstance(v, str) and _GH_HOST in v.lower():
                        out.append(v)
    elif isinstance(field, dict):
        for k in ("url", "href", "link"):
            v = field.get(k)
            if isinstance(v, str) and _GH_HOST in v.lower():
                out.append(v)
    return out


def _iter_strings(obj):
    if isinstance(obj, str):
        yield obj
    elif isinstance(obj, dict):
        for v in obj.values():
            yield from _iter_strings(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from _iter_strings(v)


if __name__ == "__main__":
    main()
