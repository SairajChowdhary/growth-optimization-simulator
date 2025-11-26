
from models.forecast_and_ab_test import compare_models
def test_compare_models_structure():
    res = compare_models()
    assert 'gbr_mae' in res
