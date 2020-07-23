from typing import Optional
import requests
from . import schemas


class Client:

    def __init__(self, api_key: str, default_engine: Optional[str]=None):

        self.api_key: str = api_key
        self.api_base: str = 'https://api.openai.com/v1/'
        self.default_engine = default_engine

    def request(self, method, endpoint, json: Optional[dict]=None) -> requests.Response:
        return requests.request(method, self.api_base + endpoint, headers={
            'Authorization': 'Bearer ' + self.api_key
        }, json=json)

    def engines(self):
        resp = self.request('GET', 'engines')
        resp.raise_for_status()
        return resp.json()

    def completions(self, engine: Optional[str] = None, **kwargs):
        engine = engine if engine else self.default_engine
        assert engine, "Either engine or default_engine must be provided."

        resp = self.request('POST', f'engines/{engine}/completions', schemas.completion.load(kwargs))
        resp.raise_for_status()
        return schemas.completion_response.load(resp.json())

    def search(self, engine: Optional[str] = None, **kwargs):
        engine = engine if engine else self.default_engine
        assert engine, "Either engine or default_engine must be provided."

        resp = self.request('POST', f'engines/{engine}/search', schemas.search.load(kwargs))
        resp.raise_for_status()
        return schemas.search_response.load(resp.json())
