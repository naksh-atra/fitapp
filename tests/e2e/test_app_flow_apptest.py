# # Sketch only; implement after pages exist
# from streamlit.testing.v1 import AppTest

# def test_full_flow(tmp_path):
#     at = AppTest.from_file("apps/web/app.py").run(timeout=30)
#     # Navigate and interact by querying widgets/labels when pages are finalized
#     # Assert no exceptions, table renders, and a download button returns bytes


import pytest

@pytest.mark.xfail(reason="legacy UI flow (v1) deprecated; replaced by v1.1 headless e2e")
def test_app_flow_legacy_placeholder():
    assert True