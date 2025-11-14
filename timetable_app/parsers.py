from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

from bs4 import BeautifulSoup


@dataclass
class TimetableRow:
    name: str
    row_html: str
    structured: Dict[str, Dict[str, Dict[str, str]]]


@dataclass
class ParsedTimetable:
    header_html: str
    rows: List[TimetableRow]
    html_index: Dict[str, str]
    structured_index: Dict[str, Dict[str, Dict[str, str]]]
    week_order: List[str]
    day_order: Dict[str, List[str]]
    period_labels: List[str]


def parse_timetable(file_path: Path) -> ParsedTimetable:
    """Parse an EduPage/ASC timetable export into reusable HTML fragments and a structured grid."""

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

    # Prepare metadata describing the table layout (weeks, days, periods)
    week_header_cells = rows[0].find_all(["th", "td"])
    time_header_cells = rows[1].find_all(["th", "td"])

    if len(week_header_cells) < 2 or len(time_header_cells) < 2:
        raise ValueError(f"Unexpected timetable header structure in {path}")

    layout_sequence: List[Tuple[str, str, int]] = []
    for cell in week_header_cells[1:]:
        label = cell.get_text(strip=True)
        colspan = int(cell.get("colspan", 1))
        normalized_label = label.replace("–", "-")
        if "-" in normalized_label:
            week_label, day_label = [part.strip() for part in normalized_label.split("-", 1)]
        else:
            week_label, day_label = label.strip(), ""
        layout_sequence.append((week_label, day_label, colspan))

    total_columns = sum(colspan for _, _, colspan in layout_sequence)
    time_cells = time_header_cells[1:]
    if total_columns != len(time_cells):
        raise ValueError(
            f"Column count mismatch in {path}: expected {total_columns}, got {len(time_cells)}"
        )

    column_meta: List[Tuple[str, str, str]] = []
    week_order: List[str] = []
    day_order: Dict[str, List[str]] = {}
    period_labels: List[str] = []

    offset = 0
    for week_label, day_label, colspan in layout_sequence:
        if week_label not in week_order:
            week_order.append(week_label)
            day_order[week_label] = []
        if day_label and day_label not in day_order[week_label]:
            day_order[week_label].append(day_label)

        day_period_labels: List[str] = []
        for _ in range(colspan):
            period_label = time_cells[offset].get_text(strip=True)
            day_period_labels.append(period_label)
            column_meta.append((week_label, day_label, period_label))
            offset += 1

        if not period_labels:
            period_labels = day_period_labels

    rows_data: List[TimetableRow] = []
    html_index: Dict[str, str] = {}
    structured_index: Dict[str, Dict[str, Dict[str, str]]] = {}

    for row in rows[2:]:
        cells = row.find_all("td")
        if not cells:
            continue
        name = cells[0].get_text(strip=True)
        if not name:
            continue

        row_html = str(row)
        structured: Dict[str, Dict[str, Dict[str, str]]] = {}

        col_index = 0
        for cell in cells[1:]:
            colspan = int(cell.get("colspan", 1))
            content_html = cell.decode_contents().strip()
            for _ in range(colspan):
                if col_index >= len(column_meta):
                    break
                week_label, day_label, period_label = column_meta[col_index]
                structured.setdefault(week_label, {}).setdefault(day_label, {})[period_label] = content_html
                col_index += 1
        # Fill any remaining columns with empty strings to keep structure aligned
        while col_index < len(column_meta):
            week_label, day_label, period_label = column_meta[col_index]
            structured.setdefault(week_label, {}).setdefault(day_label, {}).setdefault(period_label, "")
            col_index += 1

        rows_data.append(TimetableRow(name=name, row_html=row_html, structured=structured))
        html_index[name] = row_html
        structured_index[name] = structured

    return ParsedTimetable(
        header_html=header_html,
        rows=rows_data,
        html_index=html_index,
        structured_index=structured_index,
        week_order=week_order,
        day_order=day_order,
        period_labels=period_labels,
    )
