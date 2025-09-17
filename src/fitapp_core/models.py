#v1


from pydantic import BaseModel, Field, conint, confloat
from typing import Literal, Optional, List
from uuid import uuid4
from datetime import datetime, timezone

SchemaVersion = Literal["1"]

# Map UI PAL codes to numeric multipliers (tune values as needed per FAO/WHO/UNU bands)
PAL_MAP: dict[str, float] = {
    "sedentary": 1.55,   # midpoint representative
    "active": 1.85,
    "vigorous": 2.20,
}

class Inputs(BaseModel):
    age: conint(ge=16, le=80)
    sex: Literal["male", "female"]
    height_cm: conint(ge=120, le=220)
    weight_kg: confloat(ge=35, le=200)
    pal_code: Literal["sedentary", "active", "vigorous"]
    goal: Literal["hypertrophy", "strength", "fat_loss", "endurance"]
    notes: Optional[str] = None

class PlanRow(BaseModel):
    day: conint(ge=1)
    movement: str
    sets: conint(ge=1)
    reps: conint(ge=1)
    tempo_or_rest: Optional[str] = None
    load_prescription: Optional[str] = None
    notes: Optional[str] = None

class Plan(BaseModel):
    schema_version: SchemaVersion = "1"
    plan_id: str = Field(default_factory=lambda: uuid4().hex)
    generated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    goal: str
    pal_value: float
    bmr: int
    tdee: int
    rows: List[PlanRow] = []
