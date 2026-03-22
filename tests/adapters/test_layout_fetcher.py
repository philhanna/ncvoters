from pathlib import Path

from ncvoters.adapters.layout_fetcher import _parse_layout_file


def test_parse_layout_file() -> None:
    # Use the test fixture shipped with the Go code
    fixture = Path(__file__).parents[2] / "go" / "testdata" / "layout_ncvoter.txt"
    if not fixture.exists():
        return  # skip if fixture unavailable

    layout = _parse_layout_file(fixture)
    assert len(layout.all_columns) > 0
    names = [c.name for c in layout.all_columns]
    assert "last_name" in names
