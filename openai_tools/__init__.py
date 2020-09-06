from typing import Optional, Dict
import requests
from . import schemas


class Client:

    def __init__(self, api_key: str, default_engine: Optional[str]=None):

        self.api_key: str = api_key
        self.api_base: str = 'https://api.openai.com/v1/'
        self.default_engine = default_engine

    def request(self, method: str, endpoint: str, json: Optional[dict]=None) -> requests.Response:
        """
        Make a request to the openai api, automatically adding the auth header and prefixing the base api path.

        Args:
            method: Http method like GET or POST.
            endpoint: The endpoint to make the request to with like 'engines/davinci/search'. Do not start with a slash.
            json: A dict of the JSON to be sent to the API.

        Returns:
            The API response.
        """
        return requests.request(method, self.api_base + endpoint, headers={
            'Authorization': 'Bearer ' + self.api_key
        }, json=json)

    def engines(self):
        """
        Lists the currently available engines, and provides basic information about each option such as the owner
        and availability.
        """
        resp = self.request('GET', 'engines')
        resp.raise_for_status()
        return resp.json()

    def completions(self, engine: Optional[str] = None, **kwargs) -> Dict:
        """
        Create a completion. This is the main endpoint of the API. Returns new text as well as, if requested,
        the probabilities over each alternative token at each position.

        Args:
            engine: The openai engine to use (i.e. 'davinci'). Falls back to the client's default_engine.

        Keyword Args:
            **prompt (str): One or more prompts to generate from.
            **max_tokens (int): How many tokens to complete to. Can return fewer if a stop sequence is hit.
            **temperature (float): How 'creative' should the model be? 0 being conservative and 1 being creative.
            **top_p (int): An alternative to sampling with temperature, called nucleus sampling, where the model
                considers the results of the tokens with top_p probability mass. So 0.1 means only the tokens comprising
                the top 10% probability mass are considered. We generally recommend using this or temperature but not both.
            **n (int): How many choices to create for each prompt.
            **stream (bool): Whether to stream back partial progress. If set, tokens will be sent as data-only
                server-sent events as they become available, with the stream terminated by a data: [DONE] message.
            **logprobs (int): Include the log probabilities on the logprobs most likely tokens. So for example, if
                logprobs is 10, the API will return a list of the 10 most likely tokens. If logprobs is supplied, the
                API will always return the logprob of the sampled token, so there may be up to logprobs+1 elements
                in the response.
            ** stop (List(str)): One or more sequences where the API will stop generating further tokens.
                The returned text will not contain the stop sequence.
            """
        engine = engine if engine else self.default_engine
        assert engine, "Either engine or default_engine must be provided."

        json = schemas.completion.load(kwargs)
        resp = self.request('POST', f'engines/{engine}/completions', json)
        resp.raise_for_status()
        return schemas.completion_response.load(resp.json())

    def search(self, engine: Optional[str] = None, **kwargs) -> Dict:
        """
        Perform a semantic search over a list of documents.

        Args:
            engine: The openai engine to use (i.e. 'davinci'). Falls back to the client's default_engine.

        Keyword Args:
            **documents (List(str)): Documents to search over, provided as a list of strings.
            **query (str): Documents to search over, provided as a list of strings.
        """
        engine = engine if engine else self.default_engine
        assert engine, "Either engine or default_engine must be provided."

        resp = self.request('POST', f'engines/{engine}/search', schemas.search.load(kwargs))
        resp.raise_for_status()
        return schemas.search_response.load(resp.json())
