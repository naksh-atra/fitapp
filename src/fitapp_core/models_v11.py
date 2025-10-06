# # src/fitapp_core/models_v11.py
# from pydantic import BaseModel, Field, conint, confloat
# from typing import Literal, Optional, List
# from uuid import uuid4
# from datetime import datetime, timezone

# BlockType = Literal["main", "accessory", "prehab", "cardio_notes"]

# class InputsV11(BaseModel):
#     age: conint(ge=16, le=80)
#     sex: Literal["male", "female"]
#     height_cm: conint(ge=120, le=220)
#     weight_kg: confloat(ge=35, le=200)
#     pal_code: Literal["sedentary", "active", "vigorous"]
#     goal: Literal["strength", "hypertrophy", "fat_loss", "endurance"]
#     equipment: Optional[List[str]] = None
#     notes: Optional[str] = None

# class PlanRowV11(BaseModel):
#     week_label: str                 # e.g., "Week 1"
#     day: conint(ge=1)
#     day_name: str                   # e.g., "Mon", "Tue"
#     block_type: BlockType           # "main", "accessory", "prehab", "cardio_notes"
#     movement: str                   # e.g., "Squat", "Zone 2 Cardio"
#     main_focus: Optional[str] = None  # e.g., "Squat Singles", "Bench Volume"
#     intensity_cue: Optional[str] = None  # e.g., "%1RM, RPE, Zone"
#     sets: Optional[conint(ge=1)] = None
#     reps: Optional[conint(ge=1)] = None
#     duration: Optional[str] = None      # e.g., "25 min"
#     tempo_or_rest: Optional[str] = None
#     notes: Optional[str] = None

# class PlanV11(BaseModel):
#     schema_version: Literal["1.1"] = "1.1"
#     plan_id: str = Field(default_factory=lambda: uuid4().hex)
#     generated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
#     goal: str
#     week_count: conint(ge=1, le=6) = 4
#     rows: List[PlanRowV11] = []




# src/fitapp_core/models_v11.py
from __future__ import annotations

from pydantic import BaseModel, Field, conint, confloat
from typing import Literal, Optional, List, Dict, Any
from uuid import uuid4
from datetime import datetime, timezone

# Allow extras so we can stash 'extra' or 'weeks' during migration
class _Base(BaseModel):
    model_config = {"extra": "allow"}

BlockType = Literal["main", "accessory", "prehab", "cardio_notes"]

class InputsV11(_Base):
    age: conint(ge=16, le=80)
    sex: Literal["male", "female"]
    height_cm: conint(ge=120, le=220)
    weight_kg: confloat(ge=35, le=200)
    pal_code: Literal["sedentary", "active", "vigorous"]
    goal: Literal["strength", "hypertrophy", "fat_loss", "endurance"]
    equipment: Optional[List[str]] = None
    notes: Optional[str] = None
    # Optional enrichers for retrieval/query shaping
    experience: Optional[str] = None
    days_per_week: Optional[int] = None
    domain_filters: Optional[List[str]] = None

# Compact nested items (used for prompt I/O, then flattened)
class SectionItemV11(_Base):
    movement: str
    main_focus: Optional[str] = None
    intensity_cue: Optional[str] = None
    sets: Optional[int] = None
    reps: Optional[int] = None
    duration: Optional[str] = None
    tempo_or_rest: Optional[str] = None
    notes: Optional[str] = None

class DayV11(_Base):
    day: conint(ge=1) | str
    day_name: Optional[str] = None
    main: Optional[List[SectionItemV11]] = None
    accessory: Optional[List[SectionItemV11]] = None
    prehab: Optional[List[SectionItemV11]] = None
    cardio_notes: Optional[List[SectionItemV11]] = None

class WeekV11(_Base):
    week_label: str
    days: List[DayV11]

# Flattened row (back-compat for UI/exporters)
class PlanRowV11(_Base):
    week_label: str
    day: conint(ge=1)
    day_name: str
    block_type: BlockType
    movement: str
    main_focus: Optional[str] = None
    intensity_cue: Optional[str] = None
    sets: Optional[int] = None
    reps: Optional[int] = None
    duration: Optional[str] = None
    tempo_or_rest: Optional[str] = None
    notes: Optional[str] = None

class PlanV11(_Base):
    schema_version: Literal["1.1"] = "1.1"
    plan_id: str = Field(default_factory=lambda: uuid4().hex)
    generated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    goal: str
    rows: List[PlanRowV11] = []
    week_count: int = 4
