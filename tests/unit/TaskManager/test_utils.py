import pytest
from TaskManager.utils import div


class TestDiv:
    @pytest.fixture()
    def gen_5(self):
        print("Entering gen_5")
        return 5

    @pytest.fixture()
    def gen_2(self):
        return 2

    @pytest.fixture()
    def gen_1(self):
        return 1

    @pytest.fixture()
    def gen_0(self):
        return 0

    def test_utils(self, gen_5, gen_0):
        result = div(gen_5, gen_0)
        assert result is None

    def test_success(self, gen_5, gen_2):
        result = div(5, 2)
        assert result == 2.5
