# src/fitapp_core/models_v11.py
from pydantic import BaseModel, Field, conint, confloat
from typing import Literal, Optional, List
from uuid import uuid4
from datetime import datetime, timezone

BlockType = Literal["main", "accessory", "prehab", "cardio_notes"]

class InputsV11(BaseModel):
    age: conint(ge=16, le=80)
    sex: Literal["male", "female"]
    height_cm: conint(ge=120, le=220)
    weight_kg: confloat(ge=35, le=200)
    pal_code: Literal["sedentary", "active", "vigorous"]
    goal: Literal["strength", "hypertrophy", "fat_loss", "endurance"]
    equipment: Optional[List[str]] = None
    notes: Optional[str] = None

class PlanRowV11(BaseModel):
    week_label: str                 # e.g., "Week 1"
    day: conint(ge=1)
    day_name: str                   # e.g., "Mon", "Tue"
    block_type: BlockType           # "main", "accessory", "prehab", "cardio_notes"
    movement: str                   # e.g., "Squat", "Zone 2 Cardio"
    main_focus: Optional[str] = None  # e.g., "Squat Singles", "Bench Volume"
    intensity_cue: Optional[str] = None  # e.g., "%1RM, RPE, Zone"
    sets: Optional[conint(ge=1)] = None
    reps: Optional[conint(ge=1)] = None
    duration: Optional[str] = None      # e.g., "25 min"
    tempo_or_rest: Optional[str] = None
    notes: Optional[str] = None

class PlanV11(BaseModel):
    schema_version: Literal["1.1"] = "1.1"
    plan_id: str = Field(default_factory=lambda: uuid4().hex)
    generated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    goal: str
    week_count: conint(ge=1, le=6) = 4
    rows: List[PlanRowV11] = []
