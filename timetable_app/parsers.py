from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Tuple

from bs4 import BeautifulSoup


def parse_timetable(file_path: Path) -> Tuple[str, List[Dict[str, str]], Dict[str, str]]:
    """Parse an EduPage/ASC timetable export into reusable HTML fragments."""

    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Timetable file not found: {path}")

    with path.open("r", encoding="utf-8") as fh:
        soup = BeautifulSoup(fh, "html.parser")

    table = soup.find("table")
    if table is None:
        raise ValueError(f"No table found in {path}")

    rows = table.find_all("tr")
    if len(rows) < 2:
        raise ValueError(f"Expected at least two header rows in {path}")

    header_html = "".join(str(row) for row in rows[:2])

    data_rows: List[Dict[str, str]] = []
    index: Dict[str, str] = {}

    for row in rows[2:]:
        cells = row.find_all("td")
        if not cells:
            continue
        name = cells[0].get_text(strip=True)
        if not name:
            continue
        row_html = str(row)
        data_rows.append({"name": name, "row_html": row_html})
        index[name] = row_html

    return header_html, data_rows, index
