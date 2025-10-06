import json
import pytest

from fitapp_core.exporters.json_csv import to_csv_str_v11, to_json_bytes
from fitapp_core.exporters.pdf import build_pdf_v11


def sample_plan():
    # Minimal, valid v1.1 plan dict covering all exporters
    return {
        "schema_version": "1.1",
        "plan_id": "abc123",
        "generated_at": "2025-09-17T00:00:00Z",
        "goal": "hypertrophy",
        "week_count": 4,
        "rows": [
            {
                "week_label": "Week 1",
                "day": 1,
                "day_name": "Mon",
                "block_type": "main",
                "movement": "Squat",
                "main_focus": "Strength",
                "intensity_cue": "RPE 7",
                "sets": 3,
                "reps": 8,
                "duration": None,
                "tempo_or_rest": "2-0-2",
                "notes": "",
            },
            {
                "week_label": "Week 1",
                "day": 1,
                "day_name": "Mon",
                "block_type": "accessory",
                "movement": "Leg Extension",
                "sets": 3,
                "reps": 12,
                "duration": None,
                "tempo_or_rest": "",
                "notes": "",
            },
        ],
    }


def test_json_export_includes_schema_and_id():
    data = to_json_bytes(sample_plan())
    obj = json.loads(data.decode("utf-8"))
    # Strict v1.1 expectation for new exporter
    assert obj["schema_version"] == "1.1"
    assert obj["plan_id"] == "abc123"
    # Sanity: rows present
    assert isinstance(obj["rows"], list) and len(obj["rows"]) >= 1


def test_csv_export_header_and_row_count(tmp_path):
    plan = sample_plan()
    csv_text = to_csv_str_v11(plan["rows"])
    # Write/read to simulate real IO and catch encoding issues
    fp = tmp_path / "plan.csv"
    fp.write_text(csv_text, encoding="utf-8")
    text = fp.read_text(encoding="utf-8")

    # Header must match v1.1 exporter contract; extras are ignored by DictWriter. [Python csv docs]
    expected_cols = [
        "week_label",
        "day",
        "day_name",
        "block_type",
        "movement",
        "main_focus",
        "intensity_cue",
        "sets",
        "reps",
        "duration",
        "tempo_or_rest",
        "notes",
    ]
    header = text.splitlines()[0].strip()
    for col in expected_cols:
        assert col in header

    # Row count equals number of input rows
    data_lines = [ln for ln in text.splitlines()[1:] if ln.strip()]
    assert len(data_lines) == len(plan["rows"])


def test_pdf_export_bytes_and_write(tmp_path):
    plan = sample_plan()
    buf = build_pdf_v11(plan)
    # Return buffer must be bytes-like for Streamlit download and file IO
    assert isinstance(buf, (bytes, bytearray))
    # Write to disk to ensure no encoding or buffer issues
    out = tmp_path / "plan.pdf"
    out.write_bytes(buf)
    assert out.exists() and out.stat().st_size > 0
