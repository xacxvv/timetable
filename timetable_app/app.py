from __future__ import annotations

from pathlib import Path
from typing import Dict, List

from flask import Flask, abort, render_template, request

from parsers import ParsedTimetable, parse_timetable

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
EVENTS_DIR = BASE_DIR / "static" / "events"

app = Flask(__name__)


# Parse timetable data once at startup
teachers_data: ParsedTimetable = parse_timetable(DATA_DIR / "Teachers.html")
classes_data: ParsedTimetable = parse_timetable(DATA_DIR / "Classes.html")

teacher_names: List[str] = sorted(row.name for row in teachers_data.rows)
class_names: List[str] = sorted(row.name for row in classes_data.rows)

teacher_index: Dict[str, str] = teachers_data.html_index
class_index: Dict[str, str] = classes_data.html_index

teacher_structured: Dict[str, Dict[str, Dict[str, str]]] = teachers_data.structured_index
class_structured: Dict[str, Dict[str, Dict[str, str]]] = classes_data.structured_index

teacher_week_order: List[str] = teachers_data.week_order
teacher_day_order: Dict[str, List[str]] = teachers_data.day_order
teacher_period_labels: List[str] = teachers_data.period_labels

class_week_order: List[str] = classes_data.week_order
class_day_order: Dict[str, List[str]] = classes_data.day_order
class_period_labels: List[str] = classes_data.period_labels


def load_events(directory: Path) -> List[Dict[str, str]]:
    events: List[Dict[str, str]] = []
    if not directory.exists():
        return events

    for file_path in sorted(directory.iterdir()):
        if not file_path.is_file():
            continue

        extension = file_path.suffix.lower()
        if extension not in {".mp4", ".jpeg", ".jpg"}:
            continue

        event_type = "video" if extension == ".mp4" else "image"
        events.append(
            {
                "type": event_type,
                "url": f"/static/events/{file_path.name}",
            }
        )
    return events


events = load_events(EVENTS_DIR)


@app.route("/")
def index():
    return render_template(
        "index.html",
        teacher_names=teacher_names,
        class_names=class_names,
        title="Хичээлийн хуваарь",
    )


@app.route("/teacher")
def teacher_view():
    name = request.args.get("name")
    if not name or name not in teacher_index:
        abort(404)

    structured = teacher_structured.get(name, {})
    return render_template(
        "timetable.html",
        mode="teacher",
        name=name,
        structured=structured,
        week_order=teacher_week_order,
        day_order=teacher_day_order,
        period_labels=teacher_period_labels,
        title=f"{name} багшийн хуваарь",
    )


@app.route("/class")
def class_view():
    name = request.args.get("name")
    if not name or name not in class_index:
        abort(404)

    structured = class_structured.get(name, {})
    return render_template(
        "timetable.html",
        mode="class",
        name=name,
        structured=structured,
        week_order=class_week_order,
        day_order=class_day_order,
        period_labels=class_period_labels,
        title=f"{name} ангийн хуваарь",
    )


@app.route("/display")
def display():
    return render_template(
        "display.html",
        events=events,
        title="ДХИС - Долоо хоногийн арга хэмжээ",
    )


@app.errorhandler(404)
def not_found(error):  # type: ignore[override]
    return render_template("error.html", title="Алдаа", message="Хүссэн мэдээлэл олдсонгүй."), 404


if __name__ == "__main__":
    app.run(debug=True)
