import pytest
import db
import datetime
import random


@pytest.fixture
def client():
    client = db.Client(db_name=f'pytest-{datetime.datetime.utcnow().isoformat().replace(":", "_")}-{random.randint(100000, 999999)}')
    return client


class TestRequests:

    def test_add_base_request(self, client):
        settings = {'prompt': 'test'}
        uid = client.request_add(settings)
        assert uid
        req = client.request_load(uid)

        assert req
        assert req['settings']['prompt'] == "test"

    def test_add_diff_request(self, client):
        settings1 = {'prompt': 'test'}
        uid1 = client.request_add(settings1)

        settings2 = {'prompt': "test1\ntest2"}
        uid2 = client.request_add(settings2, parent_uid=uid1)

        settings3 = {'prompt': "test1\ntest2\ntest3"}
        uid3 = client.request_add(settings3, parent_uid=uid2)

        req = client.request_load(uid3)

        assert req
        assert req['settings'] == settings3
