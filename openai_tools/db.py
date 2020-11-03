import uuid
import datetime
from copy import deepcopy
from functools import partial

from diff_match_patch import diff_match_patch
from tinymongo import tinymongo as tm
import tinydb


# Override the class to avoid a recursion issue with recent tinydb
# See https://github.com/schapman1974/tinymongo/issues/58
class TinyMongoClient(tm.TinyMongoClient):
    @property
    def _storage(self):
        return tinydb.storages.JSONStorage


class Client:
    def __init__(self, storage_folder=u"tinydb", db_name='chatbot_db'):
        # you can include a folder name or absolute path
        # as a parameter if not it will default to "tinydb"
        self.connection = TinyMongoClient(storage_folder)

        # either creates a new database file or accesses an existing one named `my_tiny_database`
        self.db = getattr(self.connection, db_name)

        # Use google's diff tool, but it looks like you have to use a Diff_Timeout to get to work well?
        # See https://github.com/google/diff-match-patch/issues/100
        self._difftool = diff_match_patch()
        self._difftool.Diff_Timeout = 0.01

    def response_add(self, request_id, text):
        assert request_id is not None
        self.db.response.insert_one({
            'id': str(uuid.uuid4()),
            'request_id': request_id,
            'text': text,
            'timestamp': datetime.datetime.utcnow().timestamp()
        })

    def request_add(self, settings: dict, parent_uid: str = None):

        # pull out prompt as we don't want to save it along with settings, but we don't want to modify the version
        # we were given, so make a deep copy of it.
        prompt = settings['prompt']
        settings_clone = deepcopy(settings)
        del(settings_clone['prompt'])

        if parent_uid is None:

            # Otherwise create a new one.
            _id = str(uuid.uuid4())
            self.db.requests.insert_one({
                'id': _id,
                'prompt_base': prompt,
                'settings': settings_clone,
                'timestamp': datetime.datetime.utcnow().timestamp()
            })
            return _id

        # Since parent was provided, try to find that one.
        parent_request = self.request_load(parent_uid)
        assert parent_request

        # find the diff.
        patches = self._difftool.patch_make(parent_request['settings']['prompt'], prompt)
        diff = self._difftool.patch_toText(patches)

        # Otherwise create a new one.
        _id = str(uuid.uuid4())
        self.db.requests.insert_one({
            'id': _id,
            'prompt_diff': diff,
            'parent_id': parent_uid,
            'settings': settings_clone,
            'timestamp': datetime.datetime.utcnow().timestamp()
        })
        return _id

    def request_load(self, uid):
        req = self.db.requests.find_one({'id': uid})
        assert req

        # Create a stack of patches to apply (top first)
        diffs = []
        prompt = req.get('prompt_base')

        while prompt is None:
            diffs.append(req['prompt_diff'])
            req = self.db.requests.find_one({'id': req['parent_id']})
            prompt = req.get('prompt_base')

        # Apply the diffs in order of the most recent one added first.
        for diff in diffs[::-1]:
            patches = self._difftool.patch_fromText(diff)
            prompt, _ = self._difftool.patch_apply(patches, prompt)

        req['settings']['prompt'] = prompt
        return req
