import unittest
from unittest import mock
import openai_tools as gpt3
import requests


class TestClient(unittest.TestCase):

    def test_init(self):
        client = gpt3.Client('test_key')
        self.assertEqual(client.default_engine, None)
        self.assertEqual(client.api_key, 'test_key')

    def test_default_engine(self):
        client = gpt3.Client('test_key', 'test_engine')
        self.assertEqual(client.default_engine, 'test_engine')
        self.assertEqual(client.api_key, 'test_key')

    def test_engine_request(self):
        client = gpt3.Client('test_key', 'test_engine')
        resp = requests.Response()
        resp.status_code = 200
        resp._content = b"""{
          "id": "davinci",
          "object": "engine",
          "owner": "openai",
          "ready": true
        }"""

        with mock.patch('requests.request', autospec=True, return_value=resp) as mock_request:
            result = client.engines()

            mock_request.assert_called_once_with('GET', 'https://api.openai.com/v1/engines',
                                             headers={'Authorization': 'Bearer test_key'}, json=None)

    def test_completions_request(self):
        client = gpt3.Client('test_key', 'test_engine')
        resp = requests.Response()
        resp.status_code = 200
        resp._content = b"""{
          "id": "cmpl-uqkvlQyYK7bGYrRHQ0eXlWi7",
          "object": "text_completion",
          "created": 1589478378,
          "model": "davinci:2020-05-03",
          "choices": [
            {
              "text": " there was a girl who",
              "index": 0,
              "logprobs": null,
              "finish_reason": "length"
            }
          ]
        }"""

        with mock.patch('requests.request', autospec=True, return_value=resp) as mock_get:
            result = client.completions(prompt="Once upon a time")

            mock_get.assert_called_once_with('POST', 'https://api.openai.com/v1/engines/test_engine/completions',
                                             headers={'Authorization': 'Bearer test_key'}, json={'prompt': 'Once upon a time'})

            self.assertEqual(type(result), dict)
            self.assertEqual(result, resp.json())

    def test_search_request(self):
        client = gpt3.Client('test_key', 'test_engine')
        resp = requests.Response()
        resp.status_code = 200
        resp._content = b""" {
          "data": [
            {
              "document": 0,
              "object": "search_result",
              "score": 215.412
            },
            {
              "document": 1,
              "object": "search_result",
              "score": 55.226
            },
            {
              "document": 2,
              "object": "search_result",
              "score": 40.316
            }
          ],
          "object": "list"
        }"""

        with mock.patch('requests.request', autospec=True, return_value=resp) as mock_get:
            result = client.search(documents=['one', 'two', 'three'], query="first")

            mock_get.assert_called_once_with('POST', 'https://api.openai.com/v1/engines/test_engine/search',
                                             headers={'Authorization': 'Bearer test_key'},
                                             json={'documents': ['one', 'two', 'three'], 'query': "first"})

            self.assertEqual(type(result), dict)
            self.assertEqual(result, resp.json())
