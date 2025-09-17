from fitapp_core.energy import bmr_mifflin_st_jeor, tdee_from_bmr

def test_bmr_rounding_male():
    assert bmr_mifflin_st_jeor("male", 70.0, 175, 25) == int(round(10*70+6.25*175-5*25+5))

def test_bmr_rounding_female():
    assert bmr_mifflin_st_jeor("female", 60.0, 165, 30) == int(round(10*60+6.25*165-5*30-161))

def test_tdee():
    assert tdee_from_bmr(1700, 1.85) == int(round(1700*1.85))
