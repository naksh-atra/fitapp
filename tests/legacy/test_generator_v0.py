# Unit tests to lock behavior early and keep core logic stable as features grow, following standard Python project practices.

import pytest

@pytest.mark.xfail(reason="v0 deprecated")