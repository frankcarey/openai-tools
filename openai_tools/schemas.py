from marshmallow import Schema, fields


class CompletionRequestSchema(Schema):
    prompt = fields.String()
    max_tokens = fields.Integer()
    temperature = fields.Float()
    top_p = fields.Float()
    n = fields.Integer(default=1)
    stream = fields.Boolean(default=False)
    logprobs = fields.Integer()
    stop = fields.List(fields.String)


class ChoiceLogProbsSchema(Schema):
    tokens = fields.List(fields.String, allow_none=False)
    token_logprobs = fields.List(fields.Float(), allow_none=False)
    top_logprobs = fields.List(fields.Integer(), allow_none=True)
    text_offset = fields.List(fields.Integer(), allow_none=False)


class CompletionChoicesSchema(Schema):
    text = fields.String(required=True)
    index = fields.Integer(required=True)
    logprobs = fields.Nested(ChoiceLogProbsSchema(), required=True)
    finish_reason = fields.String(required=True)


class CompletionResponseSchema(Schema):
    id = fields.String(required=True)
    object = fields.String(required=True)
    created = fields.Integer(required=True)
    model = fields.String(required=True)
    choices = fields.List(fields.Nested(CompletionChoicesSchema()))
    stream = fields.Boolean(default=False)
    stop = fields.List(fields.String)


class SearchRequestSchema(Schema):
    documents = fields.List(fields.String(), required=True)
    query = fields.String(required=True)


class SearchResultSchema(Schema):
    document = fields.Integer()
    object = fields.String()
    score = fields.Float()


class SearchResponseSchema(Schema):
    data = fields.List(fields.Nested(SearchResultSchema()), required=True)
    object = fields.String(required=True)


completion = CompletionRequestSchema()
completion_response = CompletionResponseSchema()

search = SearchRequestSchema()
search_response = SearchResponseSchema()
