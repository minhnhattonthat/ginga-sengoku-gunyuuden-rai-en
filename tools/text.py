"""Text codecs for both string formats (docs/re/text.md): plain (bare FFFF ends) and msg (FFFF <cmd> commands)."""
from functools import lru_cache
from pathlib import Path

from tbl import Table

TBL = Path(__file__).resolve().parents[1] / 'tbl'


@lru_cache(None)
def plain_table():
    return Table.load(TBL / 'jp.tbl')


@lru_cache(None)
def msg_table():
    lines = [ln for ln in (TBL / 'jp.tbl').read_text(encoding='utf-8').splitlines() if not ln.startswith('FFFF=')]
    return Table(lines + (TBL / 'msg_codes.tbl').read_text(encoding='utf-8').splitlines())


def table(fmt):
    return msg_table() if fmt == 'msg' else plain_table()
