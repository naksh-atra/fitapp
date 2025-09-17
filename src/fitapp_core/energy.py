# v1
# Mifflin–St Jeor BMR and TDEE

from typing import Literal

def bmr_mifflin_st_jeor(sex: Literal["male","female"], weight_kg: float, height_cm: int, age: int) -> int:
    # BMR_male = 10w + 6.25h - 5a + 5;  BMR_female = 10w + 6.25h - 5a - 161
    base = 10 * weight_kg + 6.25 * height_cm - 5 * age
    return int(round(base + (5 if sex == "male" else -161)))

def tdee_from_bmr(bmr: int, pal_value: float) -> int:
    return int(round(bmr * pal_value))
