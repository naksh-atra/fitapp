import pytest
from pydantic import ValidationError
from fitapp_core.models import Inputs

def test_inputs_valid():
    Inputs(age=25, sex="male", height_cm=175, weight_kg=70.0, pal_code="active", goal="hypertrophy")

def test_inputs_invalid_range():
    with pytest.raises(ValidationError):
        Inputs(age=10, sex="male", height_cm=175, weight_kg=70.0, pal_code="active", goal="hypertrophy")
