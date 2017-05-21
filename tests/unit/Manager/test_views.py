from datetime import date
import pytest
from Manager.models import Task


class TestIndex:
    @pytest.fixture()
    def todo1(self, db):
        return Task.objects.create(title="Test title", estimate=date.today())

    def test_index(self, todo1, http):
        response = http.get('/')
        assert response.status_code == 200
