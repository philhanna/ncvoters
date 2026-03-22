"""Fetches and parses the NC Board of Elections voter file layout."""

import re
import tempfile
from enum import Enum, auto
from pathlib import Path

import requests

from ncvoters.domain.models import Column, Layout
from ncvoters.ports.outbound import LayoutFetcherPort

# Undocumented reason codes appended verbatim from the Go version
_EXTRA_REASON_CODES = """\
/* ****************************************************************************
Reason codes
reason_cd  voter_status_reason_desc
*******************************************************************************
A1         UNVERIFIED
A2         CONFIRMATION PENDING
AA         ARMED FORCES
AL         LEGACY DATA
AN         UNVERIFIED NEW
AP         VERIFICATION PENDING
AV         VERIFIED
DI         UNAVAILABLE ESSENTIAL INFORMATION
DN         CONFIRMATION NOT RETURNED
DU         VERIFICATION RETURNED UNDELIVERABLE
IA         ADMINISTRATIVE
IL         LEGACY - CONVERSION
IN         CONFIRMATION NOT RETURNED
IU         CONFIRMATION RETURNED UNDELIVERABLE
R2         DUPLICATE
RA         ADMINISTRATIVE
RC         REMOVED DUE TO SUSTAINED CHALLENGE
RD         DECEASED
RF         FELONY CONVICTION
RH         MOVED WITHIN STATE
RL         MOVED FROM COUNTY
RM         REMOVED AFTER 2 FED GENERAL ELECTIONS IN INACTIVE STATUS
RP         REMOVED UNDER OLD PURGE LAW
RQ         REQUEST FROM VOTER
RR         FELONY SENTENCE COMPLETED
RS         MOVED FROM STATE
RT         TEMPORARY REGISTRANT
SM         MILITARY
SO         OVERSEAS CITIZEN
**************************************************************************** */
"""


class _State(Enum):
    INIT = auto()
    LOOKING_FOR_COLUMNS_START = auto()
    READING_COLUMNS = auto()
    LOOKING_FOR_CODE_BLOCK = auto()
    LOOKING_FOR_CODE_BLOCK_NAME = auto()
    LOOKING_FOR_CODE_BLOCK_START = auto()
    READING_CODE_BLOCK = auto()


class NcboeLayoutFetcher(LayoutFetcherPort):
    """Downloads the layout file from the NC BOE site and parses it."""

    def fetch(self, url: str) -> Layout:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        tmp = Path(tempfile.gettempdir()) / "voter_layout.txt"
        tmp.write_text(resp.text + "\n" + _EXTRA_REASON_CODES, encoding="utf-8")
        return _parse_layout_file(tmp)


# ---------------------------------------------------------------------------
# Parsing helpers (pure functions — no I/O after the file is written)
# ---------------------------------------------------------------------------

_WS = re.compile(r"\s+")
_COUNTY_RE = re.compile(r"(\S+)\s+(\d+)")


def _parse_layout_file(path: Path) -> Layout:
    layout = Layout()
    code_blocks: dict[str, list[str]] = {}
    state = _State.INIT
    cb_name = ""
    cb: list[str] = []

    for line in path.read_text(encoding="utf-8").splitlines():
        state, cb_name, cb = _handle_line(layout, line, state, code_blocks, cb_name, cb)

    _add_code_blocks(layout, code_blocks)
    return layout


def _handle_line(
    layout: Layout,
    line: str,
    state: _State,
    code_blocks: dict[str, list[str]],
    cb_name: str,
    cb: list[str],
) -> tuple[_State, str, list[str]]:
    if state is _State.INIT:
        if line.startswith("-- File layout"):
            state = _State.LOOKING_FOR_COLUMNS_START

    elif state is _State.LOOKING_FOR_COLUMNS_START:
        if line.startswith("-------"):
            state = _State.READING_COLUMNS

    elif state is _State.READING_COLUMNS:
        if line.startswith("-------"):
            state = _State.LOOKING_FOR_CODE_BLOCK
        else:
            layout.all_columns.append(_parse_column(line))

    elif state is _State.LOOKING_FOR_CODE_BLOCK:
        if line.startswith("/* ****"):
            state = _State.LOOKING_FOR_CODE_BLOCK_NAME

    elif state is _State.LOOKING_FOR_CODE_BLOCK_NAME:
        cb_name = line
        cb = []
        state = _State.LOOKING_FOR_CODE_BLOCK_START

    elif state is _State.LOOKING_FOR_CODE_BLOCK_START:
        if line.startswith("*******"):
            state = _State.READING_CODE_BLOCK

    elif state is _State.READING_CODE_BLOCK:
        if line.startswith("*******"):
            code_blocks[cb_name] = cb
            state = _State.LOOKING_FOR_CODE_BLOCK
        else:
            cb.append(line)

    return state, cb_name, cb


def _parse_column(line: str) -> Column:
    tokens = _WS.split(line.strip(), maxsplit=2)
    return Column(
        name=tokens[0] if len(tokens) > 0 else "",
        data_type=tokens[1] if len(tokens) > 1 else "",
        description=tokens[2] if len(tokens) > 2 else "",
    )


def _add_code_blocks(layout: Layout, code_blocks: dict[str, list[str]]) -> None:
    for name, lines in code_blocks.items():
        if name == "Status codes":
            for line in lines:
                parts = _WS.split(line, maxsplit=1)
                if len(parts) == 2:
                    layout.status_codes[parts[0]] = parts[1]

        elif name == "Race codes":
            for line in lines:
                parts = _WS.split(line, maxsplit=1)
                if len(parts) == 2:
                    layout.race_codes[parts[0]] = parts[1]

        elif name == "Ethnic codes":
            for line in lines:
                parts = _WS.split(line, maxsplit=1)
                if len(parts) == 2:
                    layout.ethnic_codes[parts[0]] = parts[1]

        elif name == "County identification number codes":
            for line in lines:
                m = _COUNTY_RE.match(line)
                if m:
                    layout.county_codes[int(m.group(2))] = m.group(1)

        elif name == "Reason codes":
            for line in lines:
                parts = _WS.split(line, maxsplit=1)
                if len(parts) == 2:
                    layout.reason_codes[parts[0]] = parts[1]
