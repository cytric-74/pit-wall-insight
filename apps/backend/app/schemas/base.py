"""Shared Pydantic base for every response DTO (docs/08_API_SPECIFICATION.md: "Return camelCase responses").

Every schema in `app/schemas/` that reaches an HTTP response should subclass
`CamelModel` rather than `BaseModel` directly, so field names stay
snake_case in Python (readable, matches the Gold column names they're
sourced from) while serializing as camelCase over the wire. `populate_by_name`
keeps constructing instances with snake_case keyword arguments working
(the only way services actually build these objects) alongside the alias.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class CamelModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)
